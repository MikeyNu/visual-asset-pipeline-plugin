#!/usr/bin/env python3
"""Optional paid API adapter. Dry-run by default; no embedded credentials."""
from __future__ import annotations
import argparse
import base64
from contextlib import ExitStack
import json
import os
from pathlib import Path
import sys
from typing import Any
from assetctl import AssetError, digest, inspect_bytes, linked, new_file, read_limited, require_alpha


def run(args: argparse.Namespace, client_factory: Any = None) -> dict[str, Any]:
    prompt_bytes = read_limited(args.prompt_file, 256 * 1024)
    prompt = prompt_bytes.decode("utf-8").strip()
    if not prompt:
        raise AssetError("Prompt is empty")
    if not args.model.strip():
        raise AssetError("Choose an explicit, currently available model")
    if args.output.suffix.lower() != ".png":
        raise AssetError("Output must use .png because this adapter requests PNG")
    if args.output.exists() or linked(args.output):
        raise AssetError("Choose a new output path before making a paid request")
    if not args.output.parent.is_dir() or linked(args.output.parent):
        raise AssetError("Output parent must already exist and not be linked")
    receipt_path = args.output.with_suffix(".receipt.json")
    if receipt_path.exists() or linked(receipt_path):
        raise AssetError("Receipt path already exists")
    inputs = args.input or []
    if args.mode == "edit" and not inputs:
        raise AssetError("Editing requires an actual input image")
    if args.mode == "generate" and (inputs or args.mask):
        raise AssetError("Inputs and masks are supported only for edit mode")
    input_records = []
    for path in inputs:
        info = inspect_bytes(read_limited(path), path.name)
        input_records.append({"name": path.name, "sha256": info["sha256"],
                              "width": info["width"], "height": info["height"]})
    if args.mask:
        info = inspect_bytes(read_limited(args.mask), args.mask.name)
        if info["format"] != "PNG" or info["mode"] not in ("RGBA", "LA"):
            raise AssetError("Mask must be a PNG with an alpha channel")
        if [info["width"], info["height"]] != [input_records[0]["width"], input_records[0]["height"]]:
            raise AssetError("Mask must match the first input image dimensions")
    request = {"model": args.model, "prompt": prompt, "size": args.size,
               "quality": args.quality, "background": args.background, "output_format": "png", "n": 1}
    receipt = {"mode": args.mode, "requested_model": args.model,
               "prompt_sha256": digest(prompt_bytes), "prompt_characters": len(prompt),
               "parameters": {k: v for k, v in request.items() if k != "prompt"},
               "input_records": input_records,
               "billing": "Separate API usage; no cost estimate or charge amount inferred."}
    if not args.execute:
        return {"status": "dry-run", "network_request_made": False, **receipt}
    if not args.paid_api_approved:
        raise AssetError("Execution requires --paid-api-approved after actual user authorization")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise AssetError("OPENAI_API_KEY is not set in this execution environment")
    if client_factory is None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AssetError("Install the OpenAI Python SDK in the approved environment") from exc
        client_factory = OpenAI
    # Disable SDK retries: an ambiguous image timeout can already have incurred a charge.
    client = client_factory(api_key=key, base_url="https://api.openai.com/v1", max_retries=0, timeout=180)
    try:
        with ExitStack() as stack:
            if args.mode == "edit":
                request["image"] = [stack.enter_context(path.open("rb")) for path in inputs]
                if args.mask:
                    request["mask"] = stack.enter_context(args.mask.open("rb"))
                result = client.images.edit(**request)
            else:
                result = client.images.generate(**request)
    except Exception as exc:
        # Deliberately avoid logging raw exceptions, URLs, prompts, or credentials.
        raise AssetError(f"Image request failed ({type(exc).__name__}); no automatic retry. Check provider status and billing before retrying.") from None
    finally:
        if hasattr(client, "close"):
            client.close()
    if not getattr(result, "data", None) or not getattr(result.data[0], "b64_json", None):
        raise AssetError("Response has no accessible base64 image; do not invent an output file")
    try:
        data = base64.b64decode(result.data[0].b64_json, validate=True)
    except Exception as exc:
        raise AssetError("Invalid base64 image response") from exc
    info = inspect_bytes(data, args.output.name)
    if info["format"] != "PNG":
        raise AssetError("Provider did not return the requested PNG format")
    alpha_ok = True
    if args.background == "transparent":
        try:
            require_alpha(info)
        except AssetError:
            alpha_ok = False
    new_file(args.output, data)
    receipt.update({"status": "candidate-saved" if alpha_ok else "candidate-saved-alpha-rejected",
                    "network_request_made": True, "request_id": getattr(result, "_request_id", None),
                    "actual_image": info, "artistic_approval": "not_performed"})
    new_file(receipt_path, (json.dumps(receipt, indent=2) + "\n").encode())
    return {**receipt, "output": str(args.output), "receipt": str(receipt_path)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--mode", choices=["generate", "edit"], default="generate")
    p.add_argument("--input", action="append", type=Path)
    p.add_argument("--mask", type=Path)
    p.add_argument("--size", default="auto")
    p.add_argument("--quality", default="auto", help="Use a value supported by the selected model")
    p.add_argument("--background", choices=["auto", "opaque", "transparent"], default="auto")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--paid-api-approved", action="store_true")
    args = p.parse_args()
    try:
        result = run(args)
        print(json.dumps(result, indent=2))
        return 1 if result["status"].endswith("rejected") else 0
    except (AssetError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

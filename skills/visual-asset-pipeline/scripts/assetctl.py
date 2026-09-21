#!/usr/bin/env python3
"""Deterministic asset QA and create-only transfer. Does not generate artwork."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import warnings
from typing import Any

from PIL import Image, ImageCms, ImageOps

VERSION = "1.0.0"
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_PIXELS = 40_000_000
FORMATS = {"PNG": {".png"}, "JPEG": {".jpg", ".jpeg"}, "WEBP": {".webp"}, "AVIF": {".avif"}}
STATES = {"planned", "generated", "prepared", "installed", "integrated", "verified", "blocked"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
RESERVED = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)", re.I)
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class AssetError(ValueError):
    """Invalid input or unsafe operation."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_limited(path: Path, limit: int = MAX_FILE_BYTES) -> bytes:
    if not path.is_file() or path.stat().st_size > limit:
        raise AssetError(f"Not a regular file or exceeds {limit} bytes: {path}")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise AssetError(f"File grew beyond allowed size: {path}")
    return data


def relative_parts(value: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise AssetError(f"Expected a portable relative POSIX path: {value!r}")
    if value.startswith("/") or any(ord(c) < 32 for c in value):
        raise AssetError(f"Unsafe path: {value!r}")
    parts = tuple(value.split("/"))
    if any(p in ("", ".", "..") or p.endswith((".", " ")) or RESERVED.match(p)
           or any(c in p for c in '<>"|?*') for p in parts):
        raise AssetError(f"Unsafe path components: {value!r}")
    if any(p.casefold() == ".git" for p in parts):
        raise AssetError("Writing Git internals is forbidden")
    return parts


def linked(path: Path) -> bool:
    if path.is_symlink():
        return True
    if path.exists():
        stat = path.lstat()
        return bool(getattr(stat, "st_file_attributes", 0) & 0x400)
    return False


def safe_under(root: Path, relative: str) -> Path:
    root = Path(os.path.abspath(root))
    if not root.is_dir() or linked(root):
        raise AssetError(f"Root must be an existing, non-linked directory: {root}")
    parts = relative_parts(relative)
    current = root
    for part in parts:
        current = current / part
        if linked(current):
            raise AssetError(f"Symlink/reparse point refused: {current}")
    try:
        current.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise AssetError("Path escapes root") from exc
    return current


def decode_image(data: bytes) -> Image.Image:
    if not data or len(data) > MAX_FILE_BYTES:
        raise AssetError("Image is empty or exceeds the byte limit")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(data))
            if image.format not in FORMATS:
                raise AssetError(f"Unsupported raster format: {image.format}")
            if image.width * image.height > MAX_PIXELS:
                raise AssetError("Image exceeds pixel limit")
            if getattr(image, "n_frames", 1) != 1:
                raise AssetError("Animated images require a separate animation workflow")
            image.load()
            return image
    except AssetError:
        raise
    except Exception as exc:
        raise AssetError(f"Cannot decode image: {type(exc).__name__}") from exc


def inspect_bytes(data: bytes, name: str = "") -> dict[str, Any]:
    image = decode_image(data)
    fmt = image.format
    native = list(image.size)
    oriented = ImageOps.exif_transpose(image)
    alpha = oriented.convert("RGBA").getchannel("A")
    hist = alpha.histogram()
    pixels = oriented.width * oriented.height
    bbox = alpha.getbbox()
    transparent = hist[0] / pixels
    opaque = hist[255] / pixels
    suffix = Path(name).suffix.lower()
    return {
        "format": fmt, "width": oriented.width, "height": oriented.height,
        "native_encoded_dimensions": native, "bytes": len(data), "sha256": digest(data),
        "mode": image.mode, "frames": 1,
        "suffix_matches": not suffix or suffix in FORMATS[fmt],
        "alpha": {
            "min": alpha.getextrema()[0], "max": alpha.getextrema()[1],
            "transparent_fraction": transparent,
            "partial_fraction": sum(hist[1:255]) / pixels,
            "opaque_fraction": opaque, "visible_bounds": list(bbox) if bbox else None,
            "has_visible_transparency": transparent + sum(hist[1:255]) / pixels > 0 and hist[0] < pixels,
            "touches_canvas_edge": bool(bbox and (bbox[0] == 0 or bbox[1] == 0
                                        or bbox[2] == oriented.width or bbox[3] == oriented.height)),
        },
        "icc_profile_present": bool(image.info.get("icc_profile")),
        "note": "Numeric inspection is not visual approval. Native master bytes are unchanged.",
    }


def require_alpha(info: dict[str, Any]) -> None:
    if not info["alpha"]["has_visible_transparency"]:
        raise AssetError("Required cutout is fully opaque or fully transparent")


def new_file(path: Path, data: bytes) -> str:
    """Atomic create-only file install, with identical-byte idempotence."""
    if linked(path):
        raise AssetError("Refusing linked destination")
    if path.exists():
        if path.is_file() and read_limited(path, MAX_BUNDLE_BYTES) == data:
            return "unchanged"
        raise AssetError(f"Destination conflict, no overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".asset-staging-", dir=path.parent)
    temp = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            if path.is_file() and not linked(path) and read_limited(path, MAX_BUNDLE_BYTES) == data:
                return "unchanged"
            raise AssetError(f"Concurrent destination conflict: {path}")
        except OSError as exc:
            raise AssetError("Atomic create failed; filesystem must support hard links") from exc
        return "created"
    finally:
        temp.unlink(missing_ok=True)


def to_srgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    alpha = image.convert("RGBA").getchannel("A")
    profile = image.info.get("icc_profile")
    rgb = image.convert("RGB")
    if profile:
        try:
            rgb = ImageCms.profileToProfile(
                image.convert("CMYK") if image.mode == "CMYK" else rgb,
                ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception as exc:
            raise AssetError("ICC conversion failed; preserve master and inspect the profile") from exc
    rgb.putalpha(alpha)
    return rgb


def prepare(source: Path, out_dir: Path, name: str, widths: list[int], fmt: str,
            quality: int = 85, alpha_required: bool = False, lossless: bool = False) -> dict[str, Any]:
    if not ID_RE.fullmatch(name):
        raise AssetError("Asset name must be lowercase kebab-case")
    if not widths or any(type(w) is not int or w < 1 or w > 16384 for w in widths):
        raise AssetError("Provide positive widths no greater than 16384")
    if not 1 <= quality <= 100:
        raise AssetError("Quality must be 1-100")
    if fmt not in {"webp", "png", "jpeg"}:
        raise AssetError("Export format must be webp, png, or jpeg")
    raw = read_limited(source)
    original = inspect_bytes(raw, source.name)
    if alpha_required:
        require_alpha(original)
    image = to_srgb(decode_image(raw))
    if fmt == "jpeg" and image.getchannel("A").getextrema()[0] < 255:
        raise AssetError("JPEG would discard alpha; use PNG or WebP")
    if not out_dir.is_dir() or linked(out_dir):
        raise AssetError("Output directory must already exist and not be linked")
    effective = sorted(set(min(w, image.width) for w in widths))
    results = []
    for width in effective:
        height = max(1, round(image.height * width / image.width))
        # Premultiplied-alpha resampling avoids color bleeding from invisible pixels.
        resized = image.convert("RGBa").resize((width, height), Image.Resampling.LANCZOS).convert("RGBA")
        buf = io.BytesIO()
        if fmt == "webp":
            resized.save(buf, format="WEBP", quality=quality, lossless=lossless, method=6)
        elif fmt == "png":
            resized.save(buf, format="PNG", optimize=True)
        else:
            resized.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        data = buf.getvalue()
        ext = "jpg" if fmt == "jpeg" else fmt
        filename = f"{name}-{width}w-{digest(data)[:12]}.{ext}"
        target = safe_under(out_dir, filename)
        info = inspect_bytes(data, filename)
        if alpha_required:
            require_alpha(info)
        info["file"] = filename
        info["write"] = new_file(target, data)
        results.append(info)
    return {"original": original, "outputs": results,
            "requested_widths": widths, "effective_widths": effective,
            "upscaled": False, "transforms": ["EXIF orientation", "sRGB normalization", "downscale", fmt],
            "provenance": "Original untouched. Derivatives may not retain embedded Content Credentials."}


def pack(root: Path, files: list[str], out: Path) -> dict[str, Any]:
    seen: set[str] = set()
    entries = []
    total = 0
    for relative in files:
        path = safe_under(root, relative)
        key = relative.casefold()
        if key in seen:
            raise AssetError("Duplicate or case-colliding file path")
        seen.add(key)
        data = read_limited(path)
        info = inspect_bytes(data, relative)
        if not info["suffix_matches"]:
            raise AssetError("File extension does not match decoded image format")
        total += len(data)
        if total > MAX_FILE_BYTES:
            raise AssetError("Bundle decoded total exceeds 32 MiB")
        encoded = base64.b64encode(data).decode("ascii")
        entries.append({"path": relative, "bytes": len(data), "sha256": digest(data),
                        "base64_chunks": [encoded[i:i+4096] for i in range(0, len(encoded), 4096)]})
    if not entries:
        raise AssetError("No files selected")
    payload = (json.dumps({"version": VERSION, "files": entries}, indent=2) + "\n").encode()
    if len(payload) > MAX_BUNDLE_BYTES:
        raise AssetError("Encoded bundle exceeds limit")
    state = new_file(out, payload)
    return {"bundle": str(out), "sha256": digest(payload), "bytes": len(payload),
            "image_count": len(entries), "decoded_bytes": total, "write": state}


def receive(root: Path, bundle: Path, expected_sha256: str, allow_prefix: str,
            apply: bool = False) -> dict[str, Any]:
    if not SHA_RE.fullmatch(expected_sha256):
        raise AssetError("A valid expected bundle SHA-256 is required")
    prefix = relative_parts(allow_prefix)
    raw = read_limited(bundle, MAX_BUNDLE_BYTES)
    if digest(raw) != expected_sha256:
        raise AssetError("Bundle checksum mismatch")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("version") != VERSION or not isinstance(obj.get("files"), list):
        raise AssetError("Invalid bundle envelope")
    if not 1 <= len(obj["files"]) <= 256:
        raise AssetError("Bundle must contain between 1 and 256 images")
    pending = []
    seen: set[str] = set()
    total = 0
    for item in obj["files"]:
        if not isinstance(item, dict):
            raise AssetError("Invalid bundle item")
        relative = item.get("path")
        parts = relative_parts(relative)
        if len(parts) <= len(prefix) or parts[:len(prefix)] != prefix:
            raise AssetError("Image path is outside allowed asset prefix")
        key = relative.casefold()
        if key in seen:
            raise AssetError("Duplicate or case-colliding destination")
        seen.add(key)
        path = safe_under(root, relative)
        chunks = item.get("base64_chunks")
        if not isinstance(chunks, list) or not chunks or any(not isinstance(x, str) or len(x) > 4096 for x in chunks):
            raise AssetError("Invalid base64 chunks")
        try:
            data = base64.b64decode("".join(chunks), validate=True)
        except Exception as exc:
            raise AssetError("Invalid base64 payload") from exc
        total += len(data)
        if total > MAX_FILE_BYTES:
            raise AssetError("Decoded bundle exceeds limit")
        if type(item.get("bytes")) is not int or len(data) != item["bytes"] or digest(data) != item.get("sha256"):
            raise AssetError("Image length or checksum mismatch")
        info = inspect_bytes(data, relative)
        if not info["suffix_matches"]:
            raise AssetError("Image extension mismatch")
        if path.exists() and (not path.is_file() or read_limited(path) != data):
            raise AssetError(f"Destination conflict, entire batch preflight stopped: {relative}")
        pending.append((relative, path, data))
    results = []
    for relative, path, data in pending:
        # Recheck destination chain immediately before installing.
        safe_under(root, relative)
        state = new_file(path, data) if apply else ("unchanged" if path.exists() else "would-create")
        if apply and digest(read_limited(path)) != digest(data):
            raise AssetError(f"Post-write checksum mismatch: {relative}")
        results.append({"path": relative, "sha256": digest(data), "action": state})
    return {"mode": "apply" if apply else "dry-run", "files": results,
            "note": "Create-only, per-file atomicity. Not a multi-file transaction."}


def validate_plan(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict) or obj.get("schema_version") != VERSION or not isinstance(obj.get("assets"), list):
        raise AssetError("Expected a versioned asset plan with an assets array")
    seen = set()
    for asset in obj["assets"]:
        if not isinstance(asset, dict) or not isinstance(asset.get("id"), str) or not ID_RE.fullmatch(asset["id"]):
            raise AssetError("Invalid asset ID")
        if asset["id"] in seen:
            raise AssetError("Duplicate asset ID")
        seen.add(asset["id"])
        if asset.get("status") not in STATES:
            raise AssetError("Invalid asset state")
        if type(asset.get("alpha_required")) is not bool:
            raise AssetError("alpha_required must be a boolean")
        if not isinstance(asset.get("brief"), dict) or not asset["brief"].get("purpose"):
            raise AssetError("Asset needs a brief with a purpose")
        if not isinstance(asset.get("outputs"), list) or not isinstance(asset.get("consumers"), list):
            raise AssetError("Asset outputs and consumers must be arrays")
    return obj


def scan_tags(root: Path) -> dict[str, Any]:
    suffixes = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
    excluded = {"node_modules", ".git", ".next", "dist", "build", ".venv"}
    files = []
    if root.is_file():
        files = [root]
    elif root.is_dir():
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in excluded and not linked(Path(directory)/d)]
            files.extend(Path(directory)/n for n in names if Path(n).suffix in suffixes)
    else:
        raise AssetError("Source file or directory does not exist")
    assets = []
    for path in sorted(files):
        if linked(path):
            continue
        text = read_limited(path, 2 * 1024 * 1024).decode("utf-8")
        count = 0
        for comment in re.findall(r"<!--[\s\S]*?-->|/\*[\s\S]*?\*/", text):
            for match in re.finditer(r"<visual-asset>\s*([\s\S]*?)\s*</visual-asset>", comment):
                assets.append(json.loads(match.group(1)))
                count += 1
        if text.count("<visual-asset>") != count or text.count("</visual-asset>") != count:
            raise AssetError(f"Malformed tag or tag outside inert comment: {path}")
    return validate_plan({"schema_version": VERSION, "assets": assets})


def verify(root: Path, manifest: Path) -> dict[str, Any]:
    plan = validate_plan(json.loads(read_limited(manifest, 4 * 1024 * 1024)))
    errors = []
    checked = []
    for asset in plan["assets"]:
        aid = asset["id"]
        try:
            if not asset["outputs"] or not asset["consumers"]:
                raise AssetError("No delivered outputs or declared consumers")
            needles = []
            for output in asset["outputs"]:
                relative = output["path"]
                info = inspect_bytes(read_limited(safe_under(root, relative)), relative)
                if not info["suffix_matches"]:
                    raise AssetError("File extension mismatch")
                for field in ("sha256", "width", "height", "bytes", "format"):
                    if output.get(field) != info[field]:
                        raise AssetError(f"Output {field} mismatch: {relative}")
                if asset["alpha_required"]:
                    require_alpha(info)
                needles.extend([relative, Path(relative).name])
                if output.get("public_url"):
                    needles.append(output["public_url"])
            consumer_evidence = []
            for consumer in asset["consumers"]:
                text = read_limited(safe_under(root, consumer["file"]), 4 * 1024 * 1024).decode("utf-8")
                hit = next((needle for needle in needles if needle and needle in text), None)
                if not hit:
                    raise AssetError(f"No static asset reference in declared consumer: {consumer['file']}")
                consumer_evidence.append({"file": consumer["file"], "matched_reference": hit})
            checked.append({"id": aid, "file_checks": "pass", "consumer_evidence": consumer_evidence})
        except (AssetError, KeyError, TypeError, UnicodeError, OSError) as exc:
            errors.append({"id": aid, "error": str(exc)})
    return {"pass": bool(plan["assets"]) and not errors, "checked": checked, "errors": errors,
            "scope": "Decoded files and static reference evidence only. No browser or visual approval."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("image", type=Path)
    p.add_argument("--require-alpha", action="store_true")
    p = sub.add_parser("prepare")
    p.add_argument("image", type=Path)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--widths", default="640,960,1280")
    p.add_argument("--format", choices=["webp", "png", "jpeg"], default="webp")
    p.add_argument("--quality", type=int, default=85)
    p.add_argument("--require-alpha", action="store_true")
    p.add_argument("--lossless", action="store_true")
    p = sub.add_parser("scan-tags")
    p.add_argument("source", type=Path)
    p = sub.add_parser("pack")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--files", nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("receive")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--allow-prefix", required=True)
    p.add_argument("--apply", action="store_true")
    p = sub.add_parser("verify")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            result = inspect_bytes(read_limited(args.image), args.image.name)
            if args.require_alpha:
                require_alpha(result)
        elif args.command == "prepare":
            result = prepare(args.image, args.out_dir, args.name,
                             [int(x) for x in args.widths.split(",")], args.format,
                             args.quality, args.require_alpha, args.lossless)
        elif args.command == "scan-tags":
            result = scan_tags(args.source)
        elif args.command == "pack":
            result = pack(args.root, args.files, args.out)
        elif args.command == "receive":
            result = receive(args.root, args.bundle, args.expected_sha256, args.allow_prefix, args.apply)
        else:
            result = verify(args.root, args.manifest)
        print(json.dumps(result, indent=2))
        return 0 if result.get("pass", True) else 1
    except (AssetError, ValueError, KeyError, OSError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc), "command": args.command}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

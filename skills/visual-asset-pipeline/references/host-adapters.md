# Host and generation adapters

## Capability preflight

Fill these fields from evidence for each run, not from the skill author's environment:

| Field | Evidence to collect |
| --- | --- |
| Project filesystem | Which machine owns the root and which tool can read/write it |
| Native generation | Actual tool name, live schema, permitted inputs, return representation |
| Image editing | Usable input pixels, supported references/masks, target identification |
| File output | Mounted local file, connector file object, byte response, authorized HTTPS URL, or preview only |
| Alpha | Supported request setting plus measured output alpha |
| Continuation | Can more tools run after generation, or must the host end the turn? |
| Delivery | Verified binary path into the intended repository or asset store |
| QA | Decoding tools, image viewing, browser, project test/build commands |
| Authorization | Scope of edits, any permitted commit/push, provider use and budget |

A skill describes behavior. It does not grant access to an image model, a local filesystem, a connector, a remote repository, or a browser. Neither tags nor a skill ZIP create these capabilities.

## Native ChatGPT generation

Prefer the host's built-in image tool for image work when it is available and appropriate. Inspect its current instructions. Some hosts take an explicit prompt parameter; others infer instructions from the conversation and reject or deprecate explicit prompt fields. Some return a displayed image but not a mounted file.

The asset contract belongs in the task context and durable project plan. Tool arguments belong inside the actual tool call, not as a supposed image result in user-facing text. A planning document can describe a prompt, but returning that document is not execution of the image-generation step.

Follow image-specific host rules about clarification, references, people, web images, updates, and end-of-turn behavior. In a host that requires the response to end after generation, stop there. Save the transfer mapping before generating, and resume on the next permitted turn with actual output-file access. Do not claim an unconditional same-turn image-to-repository pipeline on that host.

## Image output bridge

Classify the result before taking the next step:

1. **Accessible mounted file:** stat and decode the exact returned path, hash it, and copy bytes into the workspace.
2. **Connector file reference:** pass the exact reference or mounted file path to the connector's documented file parameter. Do not put base64 or raw contents in a parameter designated as a file reference.
3. **Byte/base64 response:** decode with code, enforce size limits, verify format, and save a real file. Do not manually retype binary data.
4. **Authorized reachable URL:** acquire the bytes using an appropriate authorized tool. Treat signed URLs as temporary secrets. Verify content before use; an HTTP 200 can still contain an HTML error.
5. **Preview or opaque identifier only:** find a documented export or attachment route. If none is available, mark `blocked: output_not_accessible` and request the original/exported image file. Never fabricate an export endpoint or infer a sandbox path.

A locally mounted reference does not automatically become visible to an image tool; a preview visible to the conversation does not automatically become locally mounted.

## Optional programmatic API route

This is a separate, explicitly authorized route, not a workaround for refusals or quota enforcement. An API key and separately billed usage are not implied by a ChatGPT subscription. Select a currently available model and parameters from the provider's current primary documentation. Never hard-code a supposed newest model from this package's date.

`scripts/generate_openai.py` offers a narrowly scoped OpenAI image generation/editing adapter. It defaults to dry-run, takes an explicit model, and needs both `--execute` and `--paid-api-approved` before a network request. It uses `OPENAI_API_KEY` from the execution environment only. Do not print the key or put it in browser code.

The adapter saves returned image bytes and a minimal receipt. It is not an agent, a prompt author, an approval system, or a cost calculator. A CLI flag is an execution guard, not a substitute for the user's authorization. Do not automatically retry paid generation after an ambiguous timeout because the original request may already have consumed usage.

Native generation, API generation, and a provider connector may differ in feature support and output shape. Use only documented capabilities. Do not route private screenshots to an unrelated third party without permission.

## No generation available

Finish the asset map and any safe layout work, reuse approved assets where possible, and report the specific unavailable capability. Do not pretend a blank area, gradient, or hand-coded pseudo-photo satisfies required imagery. Preserve a resumable plan and keep unresolved slots explicit.

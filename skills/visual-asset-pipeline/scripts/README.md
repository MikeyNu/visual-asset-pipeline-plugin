# Executable helpers

Run from an approved environment with Python 3.10+ and Pillow. Paths below are examples,
not pre-existing files. On a remote computer, run the commands there through the actual
terminal tool. Do not expect cloud paths to work on Windows.

## Inspect and prepare

```sh
python scripts/assetctl.py inspect /path/to/master.png --require-alpha
python scripts/assetctl.py prepare /path/to/master.png --out-dir /path/to/repo/public/images/generated --name hero-sculpture --widths 640,960,1280 --format webp --require-alpha
```

Create and inspect the intended output directory first. Preparation does not create a
new project or discover its layout. It writes only newly named, content-hashed files;
identical files are no-ops and conflicting files are refused. Native originals are
unchanged. It does not upscale, crop, remove backgrounds, generate an AVIF encoder,
judge artistic quality, or preserve every metadata block in derivatives. WebP/PNG
exports support alpha; JPEG is refused when it would remove transparency. `--lossless`
affects WebP. Native input decoding supports PNG, JPEG, WebP, and AVIF when the installed
Pillow build provides that decoder. Animation is rejected.

Numeric alpha checks reject all-opaque and all-transparent cutouts but cannot prove
that a semitransparent image depicts the correct subject or lacks a painted checkerboard.
Always inspect contrasting mattes and the real page. The guard limits are 32 MiB per
image, 40 million pixels, and 32 MiB total decoded transfer payload. Use a different
approved transport for larger files rather than removing safeguards casually.

## Extract inert authoring tags

```sh
python scripts/assetctl.py scan-tags /path/to/repo/src
```

The output is a JSON plan, not generated images or automatic code modification. Tags
must contain JSON inside HTML comments or block comments, as in
`templates/asset-tag-example.html`. JSON cannot contain comment-closing sequences that
break its enclosing source comment. Duplicate IDs and malformed tags are rejected.
Treat all extracted data as untrusted and validate it against the project before acting.
The scanner is deliberately narrow, not a full parser for every programming language.

## Verified text-envelope transfer

Run `pack` where the actual files exist:

```sh
python scripts/assetctl.py pack --root /path/to/repo --files public/images/generated/hero-sculpture.png --out /path/to/private/assets-transfer.json
```

Move the exact JSON bytes and receiver helper through an authorized, supported route.
The envelope's SHA-256 is printed by `pack`. Keep that expected hash independent of the
received file. The base64 is programmatically derived from the real image, never guessed.
A text-only Desktop Commander write can carry bounded envelope chunks, but is not a
raw image upload. Respect its live limits, including line chunking. Do not put file
contents into a connector parameter declared as a file reference. Large envelopes
should use Git, a proper file route, or an approved download URL instead of repeated
context-heavy tool calls. Never make private files public solely to move them.

On the actual destination machine, inspect its root and run a dry run first:

```sh
python scripts/assetctl.py receive --root /path/to/repo --bundle /path/to/private/assets-transfer.json --expected-sha256 REPLACE_WITH_PRINTED_HASH --allow-prefix public/images/generated
```

After reviewing the dry run, repeat with `--apply`. The receiver decodes and hashes all
entries, rejects path traversal, linked destinations, unsafe Windows names, mismatched
formats, duplicate/case-colliding paths, and existing-file conflicts. It writes only
under the allowlisted prefix and rechecks installed hashes. Writes are create-only and
atomic per file using filesystem hard links. Filesystems without hard-link support
fail safely; this is not a universal transport or a multi-file transaction. Concurrent
hostile mutation of a user-controlled directory is outside the helper's threat model.
Retries of identical bytes are idempotent. No files are deleted to resolve conflicts.

## Static integration check

Populate real output metadata and consumer files in a copy of the asset plan:

```sh
python scripts/assetctl.py verify --root /path/to/repo --manifest /path/to/private/asset-plan.json
```

`prepare` returns `file`; map it to a root-relative `path` and actual served `public_url`
when updating the manifest. The verifier checks all declared file metadata and whether
consumer source mentions a declared path, URL, or filename. That is static evidence
only: comments can contain such text and dynamically indirect imports may not. It is
not proof of rendering, valid application behavior, or artistic approval. The helper
performs lightweight plan validation; use the full JSON schema during package/CI checks.

## Optional browser audit

Use an approved running preview and installed Playwright/Chromium:

```sh
python scripts/browser_audit.py --base-url http://127.0.0.1:3000 --manifest /path/to/private/asset-plan.json --out-dir /path/to/private/asset-qa-run-01
```

Default widths: 390, 768, 1440. Each consumer needs its actual route, unique CSS selector,
and `kind` (`image`, `background`, or `mask`). Target the actual `img`, not its wrapper.
For CSS imagery on pseudo-elements set `pseudo` to `::before` or `::after`.
Use `viewport_widths` only for intentional, documented viewport-specific consumers.
All output variants must have real `public_url` values. The helper checks resource
paths, including Next's image optimizer indirection, decoding, boxes, error overlays,
console/network failures, and horizontal overflow. It captures full-page screenshots.

Report directories must be new and outside publicly served assets. Screenshots may show
private content. Raw console messages are intentionally omitted. No credentials are
loaded, no buttons are clicked, and no forms are submitted. Authenticated pages require
your established browser-testing workflow; the helper does not bypass login. It tests
one Chromium engine, not every device, browser, accessibility mode, animation, or
interaction. CSS URL extraction is intentionally basic; nested image-set/canvas/WebGL
resources require a project-specific adapter. Network/image decoding is not hash-level
proof of server payload identity. Open the screenshots and perform visual/interaction
QA separately. `--executable` can name an inspected Chromium path.

## Optional separately billed image API

Native host image tools remain the first choice when available. This adapter is only a
fallback that must be explicitly authorized, not a way to use the user's ChatGPT plan
credits. Check the provider's current model and size/quality support before calling it.

```sh
python scripts/generate_openai.py --model CURRENT_APPROVED_IMAGE_MODEL --prompt-file /path/to/private/prompt.txt --output /path/to/private/new-master.png --background transparent
```

This is a dry run by default. It makes no request, creates no file, and does not require
a key. Actual generation additionally requires both `--execute` and
`--paid-api-approved`, plus `OPENAI_API_KEY` in the execution environment. An agent must
not set the approval flag without real user authorization. The adapter requests one PNG,
requires a new output path, and disables automatic SDK retries to avoid ambiguous
repeat charges. It saves actual returned bytes and a receipt without the prompt or key.
The model name is explicit rather than frozen to a potentially retired release.

For edits use `--mode edit --input /path/to/reference.png`, repeating `--input` where
supported. An optional `--mask` must be an alpha-bearing PNG matching the first image.
Mask transparency identifies editable regions in the API; inspect the current model's
behavior and preserve required invariants in the prompt. Never submit a reference that
is absent, unauthorized, or represented only by an opaque chat ID. A failed alpha check
keeps the candidate and reports rejection; it does not silently regenerate or bill again.
Provider response schemas and model capabilities can change, so verify current docs.

## Tests and exit codes

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/browser_smoke.py --out-dir /path/to/new-private-test-report
```

Unit tests create synthetic images in temporary directories and mock the API. The browser
smoke test starts a temporary loopback-only static fixture, tests it, and shuts it down.
It does not inspect the user's platform. Helper exit codes are zero for success, one
for a completed check that failed, and two for invalid inputs or an execution blocker.
A passed browser smoke check is not the same as a successful native image generation.

## Offline browser-side fixture test

```sh
python tests/browser_offline.py --out-dir /path/to/new-private-offline-report --executable /path/to/approved/chromium
```

This alternative tests element decoding and CSS image/mask inspection using synthetic
HTML and in-memory data-URI images, with network requests disabled. It does not test
server routing, production image optimization, lazy-load scrolling, or remote transfer.
Use it as a separate check when navigation is unavailable, not as evidence that the live
route audit passed. Never remove browser administration policies to make a test pass.
The live `browser_smoke.py` also accepts `--executable` for an inspected browser path.

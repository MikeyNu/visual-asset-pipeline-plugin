# Validation report

Version 1.0.0 | 21 September 2026

## Executed and passed

**51 unit/package tests passed.** These cover real PNG/WebP processing of synthetic
fixtures, alpha and empty-image rejection, disguised image formats, corruption, EXIF
orientation, no-upscale derivatives, original preservation, create-only writes,
idempotent transfer, safe paths, checksums, prefix restrictions, case collisions,
batch conflict preflight, inert-tag extraction, static consumer checks, mocked API
behavior, skill metadata, JSON schema, reference existence, and evaluation status.

**15 offline browser-side checks passed**, covering five consumer types at each of
390, 768, and 1440 CSS pixels: image, CSS background, CSS mask, pseudo-element background,
and a second image element. Synthetic data-URI assets decoded in Chromium and returned
expected dimensions. The offline fixture also passed its overflow assertions. Three
screenshots were captured. The 390-pixel screenshot was directly viewed to confirm the
fixture rendered, without claiming an artistic benchmark or real product inspection.

**Three command-line entry points passed their help checks**, and script compilation
completed. The portable plugin manifest uses fields permitted by the current published
schema; the package builder validates those field names and required values. Archive
integrity, member paths, per-file checksums, and extraction are validated when packaging.

## Blocked or not exercised

**Live-route browser audit was attempted but blocked.** The environment's existing
Chromium returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` when navigating to the synthetic
loopback HTTP fixture. An initially missing Playwright-managed executable was resolved
by selecting the inspected installed Chromium, but the navigation policy remained.
No policy was removed. Offline checks are not presented as a successful live-route audit.

No native image generation or editing request was made, no paid API was called, and no
real screenshot-to-asset generation benchmark was run. API tests use explicit mock
responses and a deliberately non-real credential. The Windows Desktop Commander
transfer and GitHub binary-upload routes were documented but not end-to-end exercised
against the user's machine or repository. No user project files were changed.

Twenty agent-evaluation scenarios are defined, not executed as live agent benchmarks.
No cross-model effectiveness, visual-quality percentage, or perfect-reference-parity
claim is made.

## Environment

- Python: 3.13.5
- Pillow: 12.3.0
- Playwright Python: 1.57.0
- OpenAI Python SDK: not installed in the test interpreter; tests inject a mock client
- jsonschema: 4.26.0
- Chromium used for offline fixtures: 144.0.7559.96
- Operating system: Linux. Native Windows behavior remains untested.

## Evidence files

`tests/evidence/unit-tests.txt` contains the executed unit test log.
`tests/evidence/offline-summary.json` contains all fifteen offline check results.
`tests/evidence/offline-390w.png`, `offline-768w.png`, and `offline-1440w.png` are synthetic
fixture screenshots, not generated website artwork.
`tests/evidence/live-browser-attempt.txt` records the live browser blocker.

## Reproduce

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/browser_offline.py --out-dir /path/to/new-offline-report --executable /path/to/approved/chromium
python tests/browser_smoke.py --out-dir /path/to/new-live-report --executable /path/to/approved/chromium
```

The last command must run in an environment where navigating to the temporary loopback
fixture is permitted. Passing the synthetic tests does not remove the need to test real
assets, actual destination files, framework routing, responsive crops, and rendered UI.

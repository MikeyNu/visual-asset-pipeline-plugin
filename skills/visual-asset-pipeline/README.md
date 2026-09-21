# Visual Asset Pipeline

Version 1.0.0 | Reviewed 21 September 2026

A reusable skill for agents that need to make actual visual assets part of a working
website, application, platform, or product. The image is specified for its place in the
interface, generated or recovered, inspected, saved, integrated, and checked in context.

## Start

Read `INSTALL.md`. Attach or install the whole folder, then ask the agent to use
**Visual Asset Pipeline** during frontend work. `CHATGPT_PROJECT_INSTRUCTIONS.md` is a
paste-ready bridge for a ChatGPT project. `SKILL.md` is the primary agent entry point.

## What is included

- A compact primary skill and seven focused reference guides.
- Art direction and robust prompts for cutouts, shared backgrounds, coordinated visual
  families, reference reconstruction, responsive placement, and editable interfaces.
- An optional inert `<visual-asset>` authoring convention, a JSON schema, and a delivery
  manifest with evidence-based states.
- `assetctl.py` for image inspection, alpha checks, immutable responsive derivatives,
  tag extraction, verified text-envelope transfer, and static integration checks.
- `generate_openai.py`, an optional explicit-approval paid API adapter, disabled by
  default and requiring a selected current model.
- `browser_audit.py` for declared images, backgrounds, and masks, with viewport
  screenshots and runtime checks.
- Unit tests, a synthetic browser fixture test, and agent-evaluation scenarios.

The helpers do not pretend to judge composition from a checksum. They prepare and
verify files. The agent must inspect the pixels and the actual rendered page.

## Completion standard

A preview is not a file. A file is not an installed asset. An installed asset is not a
verified interface. Each transition needs its own evidence. The manifest tracks
`planned`, `generated`, `prepared`, `installed`, `integrated`, `verified`, or `blocked`.

## Scope limits

This is a workflow package, not a new image model or a tool-permission bypass. Native
image generation, editing support, output accessibility, post-generation continuation,
remote transfer, and browser capabilities vary by host. Exact screenshot reconstruction
cannot reveal information that was not present in the source. The package cannot
promise perfect generation, automatic global installation, or native access to another
machine's filesystem. Its fallbacks are explicit, safe, and resumable.

No user's repository is modified by creating this package. No paid API request is
needed to use or test its deterministic helpers. The included tests use synthetic
fixtures and mocked API responses, not generated commercial artwork. See
`TEST_REPORT.md` for the exact validation performed and what remains untested.

## File map

```text
SKILL.md                         Agent entry point
agents/openai.yaml               Optional host display/activation metadata
CHATGPT_PROJECT_INSTRUCTIONS.md  Paste-ready project instructions
INSTALL.md                       Attachment, local skill, and plugin packaging
RESEARCH.md                      Primary-source findings and design decisions
references/                      Focused agent guidance
scripts/                         Optional executable helpers
templates/                       Plans, tags, briefs, checkpoints, reports
tests/                           Executable deterministic tests
evals/                           Agent behavior cases and scoring rules
TEST_REPORT.md                   Actual validation evidence
LICENSE                          MIT license for this authored package
```

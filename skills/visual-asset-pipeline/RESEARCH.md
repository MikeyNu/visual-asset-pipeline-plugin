# Research and design decisions

Reviewed: **21 September 2026**. This package distinguishes researched platform
capabilities from original workflow decisions and from capabilities observed in the
current session. Recheck provider documentation and live tool schemas during use.

## Main conclusion

Generating a good-looking image is only one part of the requested workflow. A usable
system must connect visual intent to an actual file, preserve its identity through
transfer, integrate it with the real UI, and inspect the rendered result. The asset
contract, evidence-based states, transfer envelope, and failure handling in this package
are original engineering choices, not undocumented features claimed to exist in ChatGPT.

## Primary source register

### R1. Agent Skills specification
https://agentskills.io/specification

The portable convention uses a directory with a `SKILL.md` entry point and structured
frontmatter; references and scripts can accompany it. This informed the package layout,
compact activation description, and separation of execution instructions from resources.

### R2. OpenAI: Build skills
https://learn.chatgpt.com/docs/build-skills

Documents standalone and plugin-bundled skills, selective loading, explicit activation,
and `.agents/skills` locations for supported local environments. The package includes
optional OpenAI display metadata but does not treat an attached file as proof of global
installation. Existing legacy directories are not silently migrated.

### R3. OpenAI: Image prompting
https://developers.openai.com/api/docs/guides/image-prompting

The current guide favors concrete visual requirements, intended use, composition,
reference handling, and targeted edit instructions. This informed the prompt compiler:
subject, layout role, geometry, material, lighting, constraints, and retained invariants.
The package's four detailed example briefs are newly authored, not copied prompts.

### R4. OpenAI: Image generation API
https://developers.openai.com/api/docs/guides/image-generation

Documents generation/editing, encoded image output, output formats, transparency, and
model limitations. Transparent output needs a supporting format such as PNG or WebP.
Precise layout and consistent details can still require iteration. This informed real
alpha validation, native-original retention, format checks, explicit parameter selection,
and the refusal to guarantee exact screenshot recovery. Current model choices and valid
sizes must be checked at execution time rather than frozen into this package.

### R5. OpenAI: Native image generation
https://learn.chatgpt.com/docs/image-generation

Describes native image generation alongside product/code workflows and distinguishes it
from API usage. The skill defaults to a usable native tool and treats the API as a
separately authorized execution route. A skill cannot grant unavailable tool access.
Host-specific output accessibility and turn boundaries must be discovered in the session.

### R6. W3C WAI: An alt decision tree
https://www.w3.org/WAI/tutorials/images/decision-tree/

Alternative text depends on the image's purpose and context. Decorative images can have
empty alt text; informative or functional images require the appropriate equivalent.
This informed the semantic checks rather than a blanket rule to describe every image.

### R7. MDN: Responsive images
https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images

Separates resolution switching from art direction. `srcset` and `sizes` help select
appropriate resolutions; `picture` supports deliberate alternate compositions. This
informed distinct delivery variants and mobile crop decisions, not just automatic
shrinking of a desktop hero.

### R8. MDN: shape-outside
https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/shape-outside

Explains float-based wrapping with shapes and image alpha. This informed the distinction
between actual text flow and a decorative object positioned near text. The guide includes
float/shape-margin behavior and a narrow-layout fallback rather than assuming an absolute
PNG changes line breaks.

### R9. web.dev: Optimize Largest Contentful Paint
https://web.dev/articles/optimize-lcp

Explains resource discovery and prioritization for the largest visible content. This
informed avoiding lazy loading for an LCP hero and avoiding high priority on every asset.
The package does not claim to measure Core Web Vitals from static code inspection.

### R10. GitHub: Repository contents REST API
https://docs.github.com/en/rest/repos/contents

Documents content encoding and update requirements, including the existing file's SHA.
This informed binary-aware GitHub transfer guidance and distinguishing a Git blob SHA
from this helper's SHA-256 content checksum. The live connector schema remains decisive;
API documentation is not proof that a connector exposes the same operation.

### R11. Next.js: Image component
https://nextjs.org/docs/app/api-reference/components/image

Documents image dimensions, fill/sizing behavior, responsive source selection, and
version-dependent loading/preload guidance. The skill inspects the installed Next.js
version and uses supported properties instead of prescribing a stale universal snippet.
It also preserves native HTML or other frameworks when those are the actual project.

### R12. Playwright: Visual comparisons
https://playwright.dev/docs/test-snapshots

Documents screenshot comparisons and environment-sensitive rendering. This informed the
separation between a regression baseline and an external UI reference. A newly recorded
baseline is not evidence of visual fidelity to a user's screenshot.

### R13. OpenAI: Build plugins
https://learn.chatgpt.com/docs/build-plugins

Documents the portable root `plugin.json` plus skill-directory layout, distinct from
compatibility scaffolds. A skills-only plugin wrapper is provided separately. It is
source packaging for a supported installation process, not an already installed plugin.

### R14. Agent Skills: Best practices and evaluations
https://agentskills.io/skill-creation/best-practices
https://agentskills.io/skill-creation/evaluating-skills

Supports focused entry instructions, progressive reference loading, and testing against
representative tasks. This informed the short core skill and separate positive, negative,
error, and reference-fidelity evaluation scenarios. These scenarios are specified, not
represented as completed multi-model benchmarks.

### R15. Agent Plugins manifest schema
https://agent-plugins.org/schemas/1.0.0/plugin.schema.json

The current portable schema requires `$schema` and `name`, restricts naming, and rejects
unknown top-level fields. The wrapper uses only declared fields and does not invent
runtime permissions, transport tools, or automatic service connections.

## Live tool-contract observations

The connected Desktop Commander tool descriptions were inspected in this session.
`write_file` accepts text, not a raw binary file parameter, and documents bounded line
chunks. Terminal tools can run local decoders. This supports an explicitly checked
text-envelope fallback but does not establish that a file was transferred to the user's
machine. No Desktop Commander filesystem write was performed while creating this skill.

The available plugin-management actions were inspected. No action for registering an
arbitrary new personal skill was exposed. The deliverable is therefore a created package,
project bridge, and plugin source wrapper, not a claim of global activation.

## Original design choices and tradeoffs

**Asset contracts before prompts.** UI geometry, negative space, alpha, responsive needs,
and visual semantics are known before spending a generation. The contract remains useful
when a provider or host changes.

**Native tools first, API opt-in.** An authorized native tool avoids assuming API credentials
or separate billing. An optional explicit-model API adapter provides a controllable
byte-output route where separately approved. No silent service switching is permitted.

**Source first for exact references.** Original asset reuse/extraction is more defensible
for identity than unconstrained regeneration. Synthetic enhancement is labeled as such.
The package tracks observed, inferred, and unknown details instead of promising hidden
information can be exactly recovered.

**Multiple evidence states.** Generation, byte preparation, installation, integration,
and runtime/visual approval are different achievements. Explicit states prevent a
preview, local hash, or build success from being reported as a complete product result.

**No arbitrary SVG ban.** Bad handmade complex illustration is the pain point, not SVG
itself. Vector icons, precise masks, and geometry should remain deterministic. Rich
photography and illustration are assigned to suitable visual tools.

**Bounded verified transfer.** The fallback envelope has explicit paths, hashes, byte
limits, and create-only writes. It minimizes accidental corruption/overwrite, but large
binary transfers belong in a more appropriate supported file route or authorized Git.

**Checks are not artistic judgment.** Programmatic checks catch invalid files, false
transparency, broken consumers, and path errors. Actual image and screenshot inspection
is still necessary for aesthetic quality and reference parity.

**No fictional autonomy.** A host may end the turn after image generation or expose only
a preview. The workflow checkpoints and resumes where permitted; instructions do not
create inaccessible bytes or override host rules.

## Review triggers

Recheck this skill when the host changes image output/continuation behavior, image models
or API schemas change, connector transfer contracts change, a project's stack changes,
or skill/plugin installation rules change. Use actual failing cases to improve it rather
than adding unsupported capability claims.

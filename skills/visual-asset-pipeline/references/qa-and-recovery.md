# QA, evidence, budgets, and recovery

## The verification ladder

1. **Package validity:** Skill metadata, referenced files, scripts, fixtures, and archive integrity are valid. This says nothing about future generated art.
2. **File validity:** Actual bytes decode, format matches the intended file type, dimensions are measured, content hash is recorded, alpha is verified if required.
3. **Destination validity:** The intended machine/repository contains the same bytes at the approved relative path.
4. **Integration validity:** Real consuming code references the delivered asset with correct path/base, semantics, sizing, and responsive behavior.
5. **Runtime validity:** The actual routes load; images, backgrounds, masks, and responsive sources resolve and decode; no relevant console/network errors occur.
6. **Visual validity:** Screenshots and the actual asset were viewed. Composition, cropping, masks, edges, typography relationships, and reference fidelity satisfy the contract.
7. **Interaction validity:** Layers do not obstruct relevant controls, keyboard focus, reading order, or touch targets.

Only level 6 supports an assertion about appearance. Unit tests on synthetic fixtures do not establish artistic quality. A package author must report native generation, remote writes, API calls, and UI tests separately.

## Measurable file checks

Decode the file instead of trusting the extension. Record width, height, format, byte length, hash, animation count, alpha range, transparent/partial/opaque fractions, and nonzero-alpha bounds. An RGBA image can be completely opaque. An all-transparent image is also a failure for a required visible cutout.

Inspect alpha edges on light, dark, and intended brand backgrounds. Numeric alpha checks do not detect a checkerboard painted inside an opaque object, semantically wrong cutouts, or all color fringing. Treat edge-touch statistics as a signal, not an automatic defect.

Do not globally erase white pixels: white highlights, uniforms, glass, and product surfaces may be real. Preserve edge antialiasing and translucent materials. A soft shadow must be intentional and must match the target surface.

## Browser checks

Use the actual project's browser tooling when available. The bundled browser helper is an optional measured check, not an autonomous visual judge. It checks declared routes/consumers, decodes image elements, resolves CSS background or mask resources, tests horizontal overflow, and captures screenshots at specified widths. It emits factual pass/fail data and leaves visual approval to an actual inspection.

Default evaluation widths are 390, 768, and 1440 CSS pixels as a starting sample, not a substitute for project-specific breakpoint coverage. Add the exact reference viewport for screenshot recreation. Test another narrow width when close-fitting text or masks are involved.

Inspect the initial viewport and the relevant section after scrolling. Avoid silently omitting lazy images from QA. Compare important `picture` sources and cropping at each viewport. Ensure reduced-motion behavior where animated graphics are introduced. Test hover/focus states near overlays and relevant route navigation.

Do not create a new screenshot baseline and call it parity with a supplied screenshot. Preserve a separate expected reference and compare the same content state and viewport. Playwright screenshots can vary with rendering environment [R12]; pin the environment when numerical comparisons matter.

## State discipline

Maintain `planned`, `generated`, `prepared`, `installed`, `integrated`, `verified`, or `blocked`. Record why a status changed and the evidence. A preview without retrievable bytes can be `generated`, but not `prepared` or `installed`.

When blocked, save the last successful state, current actual file references, and exact next action. Examples include `input_reference_missing`, `generation_unavailable`, `output_not_accessible`, `transfer_unavailable`, `permission_required`, `quota_exhausted`, `destination_conflict`, `visual_qa_unavailable`, and `subject_fidelity_unresolved`.

## Failure playbook

| Failure | Correct response |
| --- | --- |
| Image tool returns a preview only | Find an authorized export route; otherwise preserve plan and request exported input |
| Tool requires turn to end after generation | Checkpoint before generation, obey the boundary, resume only when permitted |
| Claimed PNG is HTML or corrupt data | Reject it; repair acquisition; do not add it to production |
| Cutout is actually opaque | Re-edit or use appropriate matting; do not just set CSS opacity |
| Correct image does not fit | Inspect layout, dimensions, crop, and anchor before regenerating |
| Thumbnail too small for hero | Find larger original or disclose upscale; do not mislabel native resolution |
| Text overlaps subject on mobile | Change crop, stack layout, or create purposeful mobile art direction |
| Local file differs after transfer | Reject installation and investigate transport; verify before updating code |
| Existing destination differs | Use a new versioned filename; preserve the existing file and unrelated work |
| Required original is missing | Mark inference/unknown; do not promise exact reconstruction |
| API timeout after request | Treat billing as ambiguous; inspect receipts/provider status where available before retrying |
| Browser is unavailable | Finish static/file checks and report that runtime and appearance remain unverified |

## Budget and iteration

An initial default is one candidate plus two targeted revisions per asset. Batch size should follow the user's scope and actual provider limits. Plan page-wide visual needs early, reuse approved families, and avoid serially discovering the same asset requirement.

Estimate cost only when a current provider rate and expected request shape are known. Do not claim a native plan includes a fixed number of generations. Do not use a paid fallback unless approved. Do not evade safety refusals, account restrictions, or rate limits.

## Evidence report

For each asset record role, source method, original reference, actual native dimensions, exported variants, hash, destination, consumers, states, checks performed, screenshot paths, remaining defects, and approval. Record prompt/model details only where actually available. Keep private prompts and references out of the public runtime manifest.

A self-assessed score is a diagnostic, not proof. Separate visual quality from exact-reference fidelity and from deployment correctness. Report limitations without silently calling unfinished work complete.

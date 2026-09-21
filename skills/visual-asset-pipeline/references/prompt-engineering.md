# Prompt compilation and controlled iteration

Research anchors: [R3] current OpenAI image prompting guidance, [R4] image generation API, and [R5] native image workflow documentation in `RESEARCH.md`. The detailed contracts below are this package's engineering design, not guarantees from a provider.

## Prompt compiler

Write only details that constrain the visible result. Use these fields as a drafting aid, not mandatory boilerplate:

1. **Deliverable and role:** An isolated foreground object for a light medical-company capabilities section, not a finished website.
2. **Subject and geometry:** Exact object count, meaningful parts, proportions, pose, silhouette, construction, and view.
3. **Composition:** Subject location, occupied area, camera angle, framing, visible extremities, copy-safe area, and crop tolerance.
4. **Visual language:** Match actual brand/source material: photographic, editorial illustration, physical product rendering, tactile print, and so forth.
5. **Material and light:** Surface type, roughness, translucency, light direction, softness, reflection and shadow treatment.
6. **Output behavior:** Alpha where needed, clean edges, isolated shadow logic, target ratio, seam behavior, or consistent origin for animation frames.
7. **Invariants and exclusions:** Properties that must not change, prohibited extra objects, lettering, watermarks, compositional mistakes, or domain inaccuracies.
8. **Acceptance:** The few visible checks that distinguish a usable result from a beautiful but unusable one.

First state the most important constraint. Keep subject descriptions internally consistent. Do not mix orthographic and strongly perspective instructions, isolated alpha and a fully opaque environmental background, or full-object framing and aggressive limb clipping.

Negative instructions complement a positive specification; they do not replace one. Ask for a purposeful visual rather than merely saying 'no AI slop'. Do not depend on unsupported seed, negative_prompt, sampler, mask, resolution, or fidelity parameters.

## Generation versus editing

For generation, describe the desired picture. For editing, identify the actual input and state a minimal delta while naming invariants. For reconstruction, anchor to measured features in a real supplied source. Repeat critical preserved details during each revision.

Do not treat a screenshot crop coordinate or a file ID as though the image tool has received its pixels. Verify the reference is available to that specific tool. Host restrictions can prohibit editing a web image even when the file could technically be downloaded; use the authorized reference route instead.

## Example A: Biocor foreground cutout

This is an illustrative brief, not an already-generated asset or a default for other brands:

> Create one isolated sculptural DNA-inspired double-helix object as a decorative foreground asset for Biocor Global's spacious light-mode website. It will sit on the right of editable HTML copy, so form a tall, open S-shaped silhouette with a concave left edge that leaves breathing room beside the text. Show two continuous intertwined rails joined by regularly spaced crosspieces; avoid disconnected pieces and impossible fused junctions. Use restrained deep-blue ceramic surfaces inspired by #073F77, with gentle satin reflections and clean white highlights. View from a slightly elevated three-quarter angle, lit by one large soft source above-left. Keep the entire object and all tips inside the frame with modest transparent padding. Use a genuinely transparent background with antialiased edges, no opaque floor, and no baked rectangular shadow. No words, letters, logo, interface, frame, particles, extra objects, or watermark. The result should read clearly at a 480-pixel display width and remain clean against both a white page and a blue section.

Do not describe this decorative object as a scientifically verified molecular model. Keep the brand reference isolated to its intended project.

## Example B: Continuous environment behind multiple sections

> Create a single wide environmental image for a website whose navigation, hero, and introductory section share one continuous background. Compose a monumental, DNA-inspired architectural curve entering from the upper-right and receding diagonally toward the lower-right, with natural atmospheric depth rather than scattered science icons. Keep the left half and upper navigation strip quiet, low-detail, and light enough for dark-blue HTML text. Use pale mineral surfaces, restrained cool-blue accents, physically coherent light from the upper-left, and generous negative space. Preserve continuity through the bottom edge rather than ending with a dark vignette or artificial section divider. No text, panels, buttons, logos, borders, or interface elements. The final crop must keep the main curve visible at desktop width; mobile art direction will be handled separately.

A seamless page composition is achieved by shared layout placement as well as image composition. Repeating this image independently on three section backgrounds can create seams.

## Example C: Screenshot-guided restoration

> Use the attached crop as the visual source of truth for the isolated laboratory microscope only. Preserve its left-facing orientation, three-quarter camera angle, silhouette, objective arrangement, stage position, base proportions, and the direction of the original soft light. Increase clarity of the observed surfaces without redesigning the device. Remove only the surrounding card background and unrelated UI text. Return the complete observed object on true alpha, keeping naturally soft antialiased edges. Do not invent an additional eyepiece, lens, control knob, brand label, or hidden component. Areas obscured in the source must be identified as inferred in the accompanying asset record, not represented as exact restoration.

Use this example only when the input exists and the tool permits the requested edit. Never ask a model to 'recover' unreadable medical labels or hidden device details as facts.

## Example D: Cohesive onboarding illustrations

> Create the second illustration in the attached approved onboarding series. Match its side-lit matte-paper material, muted green and ink palette, shallow three-quarter viewpoint, simple faceted construction, and soft contact shadows. Show three distinct document sheets being placed into one open folder, with no legible text or UI. Keep object scale and ground height consistent with the reference. Center the group in a square canvas, preserving a 12% clear margin for responsive cropping. Change only the subject arrangement; do not switch to glossy plastic, dramatic rim light, gradients, floating confetti, or a different perspective.

## Revisions

Use a defect ledger: observed defect, responsible layer, invariant, targeted change, result. Examples:
- Silhouette blocks text: first inspect placement and crop; edit the silhouette only if layout is already correct.
- White halo on a dark matte: inspect alpha and color contamination; request edge repair or use an appropriate image-matting tool, not destructive global white removal.
- Subject changes across a series: reuse the anchor and explicitly lock materials/camera/identity.
- Wrong machinery anatomy: recover an approved source or correct the specific visible part; do not hide it with blur.

Choose the minimum-change operation. Do not regenerate approved siblings after changing one asset unless their shared style actually became inconsistent.

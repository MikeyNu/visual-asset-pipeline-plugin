# Reference reconstruction and fidelity

Use alongside an installed `reference-ui-reconstruction` skill when available. That skill owns layout and UI parity; this skill owns recoverable visual assets and their integration. Read the actual companion skill rather than assuming its current contents.

## Source hierarchy

Prefer an original asset supplied by the user, an authorized design export, an existing repository asset, then a clean crop when its resolution suffices. Use restoration or reference-conditioned editing next. Free generation is last for exact-match work because it can reinterpret identity and geometry.

Generative enhancement can synthesize plausible detail. It cannot demonstrate what an occluded object actually looked like. 'Higher quality' must preserve important identity rather than license a redesign. Distinguish pixel-preserving recovery from faithful reconstruction and stylistic approximation.

## Forensic inspection

Inspect the full screenshot and targeted zoomed crops. Record screenshot dimensions, viewport if known, visible crop rectangle, source pixel density if known, object bounds, optical center, silhouette, colors, lighting, shadows, and surrounding masks.

Decompose image content from UI styling. A custom organic card may be an ordinary photo clipped by a vector path, not a uniquely generated photo with a white shape baked into it. Recover the photo and recreate the measured mask separately. Distinguish rounded corners, negative cutouts, edge shadows, and actual transparent regions.

Classify evidence:
- **Observed:** visible and measurable in the provided material.
- **Inferred:** plausible from visible evidence but not directly recoverable.
- **Unknown:** obscured, too small, compressed, or missing.

Never copy screenshot text into a photograph just because it overlapped the source object. Keep actual logos as exact approved assets. Do not replace a reference person's identity or a product's physical structure while calling the result restoration.

## Reconstruction procedure

1. Search the authorized assets, repository, and design exports first.
2. Isolate a useful source region without cutting off necessary edges. Do not OCR when vision or source text is sufficient.
3. Decide whether the remaining task is extraction, matting, resizing, restoration, inpainting, outpainting, or generation.
4. Confirm a usable input is present for the image tool and the source use is authorized.
5. Specify exactly what remains fixed and what can improve.
6. Compare at native scale and at the intended display size.
7. Compare inside the original layout, with the correct clipping and surrounding colors.
8. Record deviations and uncertainty. Label synthesized hidden regions honestly.

## Acceptance

Compare silhouette, orientation, relative size, important parts, focal point, color family, lighting, material, crop, and interaction with neighboring UI. A high-resolution reinterpretation with a different silhouette fails an exact-match task.

For deterministic layouts use aligned screenshot overlays and diffs. For generative image content, numerical pixel differences can over-penalize benign texture changes and under-explain meaningful identity changes. Use visual review alongside measurements. Do not advertise 100% parity without defensible evidence and a defined tolerance.

If exactness is essential and the only input is inadequate, preserve the best recovered version, explain precisely what is unknowable, and request the original source asset. Continue other independent implementation work rather than inventing precision.

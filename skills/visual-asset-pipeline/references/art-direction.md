# Art direction and asset planning

## Plan for the interface, not a disconnected picture

An asset succeeds when it helps the section do its job. Start from the surrounding headline, audience, product, layout, existing tokens, and approved reference. Define what the viewer should understand before choosing a rendering style. A compliance dashboard may need no decorative art; a product launch may need a carefully staged hero.

Create an asset map with role, source, display box, focal region, copy-safe region, viewport behaviors, and acceptance checks. Inventory approved logos, product photography, vectors, reference exports, and existing generated masters before spending a generation.

## Select the right medium

| Visual need | Preferred method |
| --- | --- |
| Existing exact logo, packaging, distinctive icon | Reuse approved source, extract permitted source, or deterministic reconstruction with inspection |
| Photography, rich illustration, atmospheric world, isolated rendered object | Generative imagery or image editing with a usable reference |
| Border, rounded or organic panel edge, geometric mask, simple divider | CSS or measured vector geometry; use actual artwork inside it |
| Navigation and action icons | Existing approved icon library or vector asset |
| Live chart, technical values, labels, responsive UI | Real code and data, not an image of controls |
| Existing correct picture at insufficient resolution | Seek higher-resolution original, then controlled restoration, then disclosed synthesis |

Do not interpret the rejection of bad SVG artwork as a ban on real SVG assets or useful geometry. Conversely, a 200-element hand-coded SVG is not an acceptable substitute for a required photograph.

## Composition contract

Use normalized coordinates in the plan: x and y from 0 to 1, measured from the top-left. A copy-safe rectangle `[0.04, 0.15, 0.40, 0.65]` means left, top, width, height. These are design targets, not exact controls a generator is guaranteed to obey. Inspect the result.

Separate:
- Canvas ratio and intended rendered ratio.
- Subject occupied bounds and transparent padding.
- Subject anchor point and acceptable cropping limits.
- Copy-safe area and the object's silhouette.
- Camera direction and the direction the subject visually leads the viewer.

A full-bleed composition can allow edge cropping. A cutout normally needs all extremities intact. Excess transparent padding shrinks a subject at an apparently correct CSS width. Trim only as a deliberate derivative and remeasure the anchor and text-wrapping contour.

## Layer decisions

Choose one of these deliberately: one background scene; independent foreground cutout; separate shadow layer; background plus foreground; texture tile; controlled sprite sheet. Do not flatten layers that need independent responsive positioning or interaction.

For text flowing around an image, distinguish two intentions. A decorative object behind or beside a heading needs ordinary grid/positioning. Paragraph text following an irregular silhouette needs an actual exclusion contour and appropriate layout. Text should not be painted into the generated bitmap.

For semi-transparent glass, a raster texture cannot dynamically refract arbitrary changing page content. Use a CSS rendering effect where live backdrop behavior is required, or render a purpose-specific optical texture with disclosed limitations. Do not promise physical refraction from simple alpha.

## Cohesive families

Create a style anchor first. Record material, lighting direction, camera elevation, palette, edge treatment, shadow logic, detail density, and subject scale. Make siblings inherit those properties but vary the meaningful content. Use the approved anchor as a reference when the tool supports it.

Keep defaults project-dependent. Do not apply universal purple gradients, glass cards, blobs, glowing particles, oversized fake 3D icons, or arbitrary bento layouts. Add them only when the brief and existing design language genuinely require them.

## Responsive decisions

Plan mobile behavior before generation. A wide hero may use a different crop, a separate art-directed mobile image, or a stacked cutout, depending on whether the subject survives narrowing. Avoid shipping the desktop composition in a tiny box simply to claim responsiveness.

Derive delivery width from rendered CSS width and an appropriate target pixel density, bounded by real source resolution and network cost. An initial heuristic is up to 2x the rendered size for important assets, but inspect softness and actual transfer cost. This is a project heuristic, not a universal standard.

## Domain truth

Generated visuals are illustrations unless verified otherwise. Do not imply a fictional factory, employee, clinical result, certification, inventory item, or facility is real. Product anatomy and equipment details that affect factual claims must be checked against approved material. Do not fabricate endorsements, certification marks, or operational evidence.

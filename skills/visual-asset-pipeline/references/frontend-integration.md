# Frontend and product integration

Research anchors: W3C alternative-text guidance [R6], MDN responsive images and shapes [R7-R8], web.dev LCP guidance [R9], Next.js image documentation [R11], and Playwright visual comparison guidance [R12]. Example implementation choices below are project-specific engineering patterns.

## Keep artwork and UI separate

Images carry photography, texture, illustration, and composed artwork. HTML and native components carry headings, body copy, buttons, forms, menus, and data. A generated screenshot may be a reference or a marketing illustration; it must not replace the actual interactive UI.

Store immutable production derivatives in the existing asset convention. Keep a master and private metadata outside the publicly served tree. Map physical file paths to deployed public URLs. An absolute Windows path is not a browser URL. A `/public` filesystem directory usually is not part of the URL in frameworks that serve it as the root.

## Responsive HTML

Use real image dimensions to reserve layout space. Use `srcset`/`sizes` for resolution selection and `picture` for genuinely different art direction or formats. Every width descriptor must describe the actual file. Ensure nested routes and deployment subpaths resolve correctly.

```html
<picture>
  <source media="(max-width: 42rem)" srcset="/images/generated/hero-mobile.webp">
  <img data-asset-id="home-hero" src="/images/generated/hero-desktop.webp"
       width="1536" height="1024" alt=""
       loading="eager" fetchpriority="high"
       class="hero-art">
</picture>
```

These are example paths, not existing generated assets. Replace them with verified outputs. A dominant initial-view image normally should not be lazy-loaded. Avoid giving every image high priority. Less urgent images can use lazy loading. Confirm behavior with the actual page rather than relying on the component name 'hero'.

## React, Vite, Next.js, and other stacks

Honor the installed framework version and existing conventions. Vite asset imports and public assets have different handling, especially with a configured base path. In Next.js use the existing `Image` convention, real dimensions or a correctly sized `fill` parent, and accurate `sizes`. Check current version-specific loading APIs rather than copying an obsolete `priority` prop blindly [R11]. Do not combine mutually discouraged priority/preload options.

Do not add a client-component boundary just to display an image. Avoid adding a new image service or broad remote-domain wildcard for local generated assets. For static export, confirm how the existing image optimizer is configured. Do not globally disable optimization without a demonstrated requirement.

For Astro, Vue/Nuxt, SvelteKit, WordPress, email, native apps, presentations, or 3D products, inspect their real asset ingestion conventions. Reuse the planning, generation, persistence, and QA loop, but do not blindly paste browser-only code into another target. Follow any host-specific artifact skill before creating those file types.

## Text wrapping around alpha

`shape-outside` affects floats; absolute positioning and ordinary grid overlap do not create line exclusion. The shape can use an image's alpha channel, with suitable origin/CORS handling [R8].

```html
<article class="copy-with-cutout">
  <img class="copy-cutout" data-asset-id="capabilities-cutout"
       src="/images/generated/cutout.webp"
       width="1024" height="1536" alt="">
  <h2>A real editable heading</h2>
  <p>Editable paragraph text follows the silhouette where space allows.</p>
</article>
```

```css
.copy-with-cutout { display: flow-root; }
.copy-cutout {
  float: right;
  width: min(42%, 24rem);
  height: auto;
  shape-outside: url('/images/generated/cutout.webp');
  shape-image-threshold: .12;
  shape-margin: 1.25rem;
  margin: 0 0 1rem 1rem;
}
@media (max-width: 42rem) {
  .copy-cutout {
    float: none;
    display: block;
    width: min(100%, 20rem);
    margin: 0 auto 1.5rem;
    shape-outside: none;
  }
}
```

The example threshold and breakpoint must be tuned to the actual image and typography. Soft shadows can accidentally affect exclusion; a separately prepared contour mask may be better. Verify line length and readability, including zoom and localization. Do not force irregular text flow onto a dense dashboard.

## Organic masks and shared backgrounds

Treat a shaped card as two assets of responsibility: content image and deterministic clipping geometry. Use measured SVG clip paths or CSS masks where needed. An approved path is not the bad improvised SVG artwork this workflow avoids. Keep coordinates consistent with the intended aspect ratio and inspect edge behavior at every breakpoint.

For a continuous scene behind a header and two sections, create a shared outer wrapper and one background-positioning context. Do not restart the same image in each section. Separate opaque surfaces should only cover it where the reference actually does so. Inspect mobile height changes and background-size behavior.

For independent foreground overlays, use explicit stacking contexts, predictable container anchoring, and `pointer-events: none` only when the layer is truly decorative. Ensure the decoration cannot block buttons, focus rings, selections, or touch gestures.

## Accessibility and truth

Use `alt=""` for decorative imagery. Describe meaningful visual information in context; describe the action for an image used as a control. Do not repeat surrounding copy unnecessarily. Supply a text equivalent for complex information [R6]. CSS backgrounds must not be the only source of essential content.

Do not encode headings, prices, labels, or certification claims into generated imagery. Keep contrast readable over all responsive crops. Do not identify generated people as actual staff or customers. Do not present fabricated product specifications as real stock.

## Delivery performance

Preserve alpha using a format that supports it. Use efficient delivery derivatives appropriate to the actual image and project constraints; no universal format wins every case. Do not ship a giant master where a smaller derivative meets the requirement. Measure network transfer, decoding, and the page's loading behavior.

The helper defaults to downscaling only. Plan separate mobile art direction where necessary rather than stretching or severely cropping a desktop composition. Retain originals for future exports and provenance. Respect the existing cache policy and content-hashed URL strategy.

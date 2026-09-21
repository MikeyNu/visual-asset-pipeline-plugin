#!/usr/bin/env python3
"""Read-only browser smoke audit of declared visual consumers. Not artistic QA."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urljoin, urlsplit, urlunsplit
from assetctl import AssetError, digest, linked, new_file, read_limited, validate_plan


def error_code(exc: Exception) -> str:
    message = str(exc)
    if 'ERR_BLOCKED_BY_ADMINISTRATOR' in message:
        return 'BROWSER_NAVIGATION_BLOCKED_BY_HOST_POLICY'
    if "Executable doesn't exist" in message:
        return 'BROWSER_EXECUTABLE_UNAVAILABLE'
    if 'Timeout' in type(exc).__name__:
        return 'BROWSER_TIMEOUT'
    return type(exc).__name__


def clean_url(value: str) -> str:
    p = urlsplit(value)
    return urlunsplit((p.scheme, p.netloc.split('@')[-1], p.path, '', ''))


def resource_identity(value: str) -> str:
    """Unwrap Next's image optimizer without accepting an arbitrary basename match."""
    p = urlsplit(value)
    if p.path.endswith('/_next/image'):
        inner = parse_qs(p.query).get('url', [None])[0]
        if inner:
            p = urlsplit(inner)
    return unquote(p.path)


def route_url(base: str, route: str) -> str:
    b = urlsplit(base)
    if b.scheme not in ('http', 'https') or not b.hostname or b.username or b.password or b.query or b.fragment:
        raise AssetError('Base URL must be an explicit HTTP(S) origin/base path without credentials or query')
    r = urlsplit(route)
    if r.scheme or r.netloc or r.query or r.fragment or '\\' in route:
        raise AssetError('Consumer routes must be same-origin paths without a query or fragment')
    result = urljoin(base.rstrip('/') + '/', route)
    if urlsplit(result).netloc != b.netloc:
        raise AssetError('Route escapes the authorized origin')
    return result


ELEMENT_JS = r"""async (el, opts) => {
  const style = getComputedStyle(el, opts.pseudo || null);
  const rect = el.getBoundingClientRect();
  const result = {
    tag: el.tagName, kind: opts.kind,
    box: {x:rect.x,y:rect.y,width:rect.width,height:rect.height},
    displayed: style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0,
    resources: [], alt: el.getAttribute('alt'),
    loading: el.getAttribute('loading'), fetchPriority: el.getAttribute('fetchpriority'),
    objectFit: style.objectFit, objectPosition: style.objectPosition
  };
  if (opts.kind === 'image') {
    if (!(el instanceof HTMLImageElement)) throw new Error('Selector must target the actual img element');
    await Promise.race([el.decode(), new Promise((_, reject) => setTimeout(() => reject(new Error('image decode timeout')), 8000))]);
    result.resources.push({url:el.currentSrc || el.src, loaded:el.complete && el.naturalWidth > 0,
      width:el.naturalWidth,height:el.naturalHeight});
  } else {
    const value = opts.kind === 'mask' ? (style.maskImage || style.webkitMaskImage) : style.backgroundImage;
    const urls = [...value.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)].map(x=>x[1]);
    for (const url of urls) {
      const probe = new Image(); probe.src = url;
      let loaded = true;
      try { await Promise.race([probe.decode(), new Promise((_, reject) => setTimeout(() => reject(new Error('decode timeout')),8000))]); }
      catch { loaded = false; }
      result.resources.push({url,loaded,width:probe.naturalWidth,height:probe.naturalHeight});
    }
  }
  result.inDocument = el.isConnected;
  return result;
}"""


def audit(base_url: str, manifest: Path, out_dir: Path, widths: list[int], executable: str | None = None) -> dict:
    plan = validate_plan(json.loads(read_limited(manifest, 4*1024*1024)))
    if not widths or any(w < 240 or w > 3840 for w in widths):
        raise AssetError('Audit widths must be between 240 and 3840')
    if out_dir.exists():
        raise AssetError('Use a new private report directory; screenshots are never overwritten')
    if not out_dir.parent.is_dir() or linked(out_dir.parent):
        raise AssetError('Report parent must exist and not be linked')
    grouped: dict[str, list] = {}
    for asset in plan['assets']:
        for consumer in asset['consumers']:
            route = consumer.get('route')
            selector = consumer.get('selector')
            kind = consumer.get('kind', 'image')
            if not isinstance(route, str) or not isinstance(selector, str) or not selector:
                raise AssetError('Each audited consumer needs a route and CSS selector')
            if kind not in ('image', 'background', 'mask') or consumer.get('pseudo') not in (None, '::before', '::after'):
                raise AssetError('Unsupported consumer kind or pseudo-element')
            if kind == 'image' and consumer.get('pseudo'):
                raise AssetError('An img consumer cannot target a pseudo-element')
            expected = [resource_identity(x['public_url']) for x in asset['outputs'] if x.get('public_url')]
            if not expected:
                raise AssetError('Audit needs real public_url values for each asset')
            grouped.setdefault(route_url(base_url, route), []).append((asset, consumer, expected))
    if not grouped:
        raise AssetError('No declared browser consumers')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise AssetError('Install Playwright and a browser in the approved environment before auditing') from exc
    out_dir.mkdir()
    records, errors = [], []
    with sync_playwright() as p:
        launch = {'headless': True}
        if executable:
            launch['executable_path'] = executable
        browser = p.chromium.launch(**launch)
        try:
            for width in sorted(set(widths)):
                for url, entries in grouped.items():
                    context = browser.new_context(viewport={'width':width,'height':900}, device_scale_factor=1, reduced_motion='reduce')
                    page = context.new_page()
                    page.set_default_timeout(10000)
                    page_errors: list[str] = []
                    console_errors: list[str] = []
                    failed_requests: list[str] = []
                    # Counts only for console/JS exceptions: raw messages can contain secrets.
                    page.on('pageerror', lambda e: page_errors.append(type(e).__name__))
                    page.on('console', lambda m: console_errors.append(m.type) if m.type == 'error' else None)
                    page.on('requestfailed', lambda r: failed_requests.append(clean_url(r.url)))
                    record = {'url':clean_url(url), 'viewport_width':width, 'consumers':[]}
                    try:
                        response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                        if not response or response.status >= 400:
                            raise AssetError('Page did not return a successful HTTP response')
                        page.evaluate('() => Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve,3000))])')
                        for asset, consumer, expected in entries:
                            allowed_widths = consumer.get('viewport_widths')
                            if allowed_widths and width not in allowed_widths:
                                record['consumers'].append({'id':asset['id'],'status':'not-targeted-at-this-width'})
                                continue
                            entry = {'id':asset['id'],'selector':consumer['selector']}
                            try:
                                loc = page.locator(consumer['selector'])
                                if loc.count() != 1:
                                    raise AssetError('Consumer selector must resolve to exactly one element')
                                loc.scroll_into_view_if_needed()
                                details = loc.evaluate(ELEMENT_JS, {'kind':consumer.get('kind','image'), 'pseudo':consumer.get('pseudo')})
                                identities = [resource_identity(r['url']) for r in details['resources']]
                                matches = any(x in expected for x in identities)
                                okay = details['displayed'] and details['box']['width'] > 0 and details['box']['height'] > 0 and bool(details['resources']) and all(r['loaded'] for r in details['resources']) and matches
                                for resource in details['resources']:
                                    resource['url'] = clean_url(resource['url'])
                                entry.update({'pass':bool(okay), 'expected_resource_used':matches, 'details':details})
                                if not okay:
                                    errors.append({'url':clean_url(url),'width':width,'id':asset['id'],'error':'Asset is missing, hidden, empty, unloaded, or not the declared resource'})
                            except Exception as exc:
                                entry.update({'pass':False, 'error_type':error_code(exc)})
                                errors.append({'url':clean_url(url),'width':width,'id':asset['id'],'error_type':error_code(exc)})
                            record['consumers'].append(entry)
                        page.evaluate('window.scrollTo(0,0)')
                        record['horizontal_overflow'] = page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2')
                        record['framework_error_overlay'] = page.locator('[data-nextjs-dialog],vite-error-overlay,#webpack-dev-server-client-overlay').count() > 0
                        record['has_body_content'] = bool(page.locator('body').inner_text().strip()) or bool(page.locator('img').count())
                        shot = f'page-{digest(url.encode())[:10]}-{width}w.png'
                        page.screenshot(path=str(out_dir/shot), full_page=True, animations='disabled', timeout=20000)
                        record['screenshot'] = shot
                        if record['horizontal_overflow'] or record['framework_error_overlay'] or not record['has_body_content']:
                            errors.append({'url':clean_url(url),'width':width,'error':'Page layout, content, or error-overlay check failed'})
                    except Exception as exc:
                        record['error_type'] = error_code(exc)
                        errors.append({'url':clean_url(url),'width':width,'error_type':error_code(exc)})
                    record.update({'page_error_count':len(page_errors),'console_error_count':len(console_errors),'failed_requests':failed_requests})
                    if page_errors or console_errors or failed_requests:
                        errors.append({'url':clean_url(url),'width':width,'error':'Console, JavaScript, or network failure requires review'})
                    records.append(record)
                    context.close()
        finally:
            browser.close()
    report = {'pass':not errors,'pages':records,'errors':errors,
              'scope':'Declared assets and browser smoke checks only. Human or agent screenshot inspection is still required.',
              'visual_approval':'not_performed','interactions_tested':False}
    new_file(out_dir/'report.json', (json.dumps(report,indent=2)+'\n').encode())
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url', required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--widths', default='390,768,1440')
    p.add_argument('--executable', help='Optional inspected Chromium executable path')
    args = p.parse_args()
    try:
        result = audit(args.base_url,args.manifest,args.out_dir,[int(w) for w in args.widths.split(',')],args.executable)
        print(json.dumps(result,indent=2))
        return 0 if result['pass'] else 1
    except Exception as exc:
        print(json.dumps({'error_type':error_code(exc),'message':'Browser audit could not complete. Check dependencies, approved paths, and inputs locally.'}),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())

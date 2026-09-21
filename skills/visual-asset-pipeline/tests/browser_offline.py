#!/usr/bin/env python3
"""Offline browser-side decoder/selector fixtures. No route or network integration claim."""
from __future__ import annotations
import argparse,base64,io,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assetctl import new_file
from browser_audit import ELEMENT_JS
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--executable');args=p.parse_args()
    if args.out_dir.exists():raise SystemExit('Choose a new output directory')
    args.out_dir.mkdir(parents=True)
    im=Image.new('RGBA',(160,200),(0,0,0,0));ImageDraw.Draw(im).ellipse((30,20,130,180),fill=(30,70,120,255))
    b=io.BytesIO();im.save(b,format='PNG');url='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
    html=f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{{box-sizing:border-box}}body{{margin:0;padding:24px;font:16px Arial}}.row{{display:flex;flex-wrap:wrap;gap:24px}}.box{{width:160px;height:200px}}.background{{background:url("{url}") center/contain no-repeat}}.mask{{background:#194d7f;mask-image:url("{url}");mask-size:contain}}.pseudo{{position:relative}}.pseudo::before{{content:"";position:absolute;inset:0;background:url("{url}") center/contain no-repeat}}img{{max-width:100%;height:auto}}</style></head><body><h1>Offline image-helper fixture</h1><p>Synthetic test only. No generated artwork.</p><div class="row"><img id="image" src="{url}" width="160" height="200" alt=""><div id="background" class="box background"></div><div id="mask" class="box mask"></div><div id="pseudo" class="box pseudo"></div><img id="second" src="{url}" width="160" height="200" alt=""></div></body></html>'''
    records=[]
    with sync_playwright() as p:
        launch={'headless':True}
        if args.executable:launch['executable_path']=args.executable
        browser=p.chromium.launch(**launch)
        try:
            for width in [390,768,1440]:
                page=browser.new_page(viewport={'width':width,'height':1000})
                page.route('**/*',lambda r:r.abort())
                page.set_content(html,wait_until='domcontentloaded')
                for selector,kind,pseudo in [('#image','image',None),('#background','background',None),('#mask','mask',None),('#pseudo','background','::before'),('#second','image',None)]:
                    result=page.locator(selector).evaluate(ELEMENT_JS,{'kind':kind,'pseudo':pseudo})
                    assert result['displayed'] and result['resources'] and all(x['loaded'] for x in result['resources'])
                    assert result['resources'][0]['width']==160 and result['resources'][0]['height']==200
                    records.append({'width':width,'selector':selector,'pass':True})
                assert not page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth+2')
                page.screenshot(path=str(args.out_dir/f'offline-{width}w.png'),full_page=True)
                page.close()
        finally:browser.close()
    report={'pass':True,'checks':records,'scope':'15 offline browser element/decoder checks; set_content with data-URI synthetic fixtures, no network navigation.',
      'live_route_audit':'blocked_by_environment_policy_in_this_session','native_generation_tested':False,'artistic_quality_tested':False}
    new_file(args.out_dir/'summary.json',(json.dumps(report,indent=2)+'\n').encode());print(json.dumps({'pass':True,'checks':len(records),'scope':report['scope']},indent=2))

if __name__=='__main__':main()

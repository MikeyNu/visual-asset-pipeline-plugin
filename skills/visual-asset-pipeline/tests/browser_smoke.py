#!/usr/bin/env python3
"""Synthetic loopback browser test. Not a visual benchmark of generated artwork."""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io,json
from pathlib import Path
import sys,tempfile,threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from PIL import Image,ImageDraw
from assetctl import inspect_bytes,new_file
from browser_audit import audit

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,format,*args):pass

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out-dir',type=Path,required=True);parser.add_argument('--executable');args=parser.parse_args()
    if args.out_dir.exists():raise SystemExit('Choose a new output directory')
    args.out_dir.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);folder=root/'assets';folder.mkdir()
        im=Image.new('RGBA',(160,200),(0,0,0,0));ImageDraw.Draw(im).ellipse((30,20,130,180),fill=(30,70,120,255))
        stream=io.BytesIO();im.save(stream,format='PNG');data=stream.getvalue();(folder/'fixture.png').write_bytes(data)
        im=Image.new('RGB',(16,16),(100,100,100));im.save(folder/'wrong.png')
        (root/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>Asset helper synthetic test</title><style>
        *{box-sizing:border-box}body{margin:0;padding:24px;font:16px Arial,sans-serif;background:#f6f8fa;color:#111}main{max-width:700px;margin:auto}img{max-width:100%;height:auto}.row{display:flex;gap:24px;flex-wrap:wrap}.graphic{width:160px;height:200px;background-image:url('/assets/fixture.png');background-size:contain;background-repeat:no-repeat}.mask{width:160px;height:200px;background:#164c8a;mask-image:url('/assets/fixture.png');mask-size:contain;mask-repeat:no-repeat}.pseudo{position:relative;width:160px;height:200px}.pseudo::before{content:"";position:absolute;inset:0;background:url('/assets/fixture.png') center/contain no-repeat}.spacer{height:950px}</style></head><body><main><h1>Synthetic asset audit fixture</h1><p>This tests file loading and integration checks, not generated artwork.</p><div class="row"><img id="hero" src="/assets/fixture.png" width="160" height="200" alt=""><div id="backdrop" class="graphic" aria-hidden="true"></div><div id="masked" class="mask" aria-hidden="true"></div><div id="pseudo" class="pseudo" aria-hidden="true"></div></div><div class="spacer"></div><h2>Lazy image</h2><img id="lazy" loading="lazy" src="/assets/fixture.png" width="160" height="200" alt=""></main></body></html>''')
        info=inspect_bytes(data);output={k:info[k] for k in ('width','height','bytes','format','sha256')};output.update(path='assets/fixture.png',public_url='/assets/fixture.png')
        consumers=[{'file':'index.html','route':'/','selector':s,'kind':kind} for s,kind in [('#hero','image'),('#backdrop','background'),('#masked','mask'),('#pseudo','background'),('#lazy','image')]];consumers[3]['pseudo']='::before'
        plan={'schema_version':'1.0.0','assets':[{'id':'fixture','status':'integrated','alpha_required':True,'brief':{'purpose':'Synthetic transport/browser QA'},'outputs':[output],'consumers':consumers}]}
        manifest=root/'plan.json';manifest.write_text(json.dumps(plan))
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(root)))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            base=f'http://127.0.0.1:{server.server_address[1]}'
            positive=audit(base,manifest,args.out_dir/'positive',[390,768,1440],args.executable)
            if not positive['pass']:raise AssertionError('Positive browser fixture failed: '+json.dumps(positive['errors']))
            # Detect a real broken image, rather than counting static source references.
            html=(root/'index.html').read_text().replace('id="hero" src="/assets/fixture.png"','id="hero" src="/assets/missing.png"')
            (root/'index.html').write_text(html)
            negative=audit(base,manifest,args.out_dir/'broken-image',[390],args.executable)
            if negative['pass']:raise AssertionError('Broken image was incorrectly accepted')
            # An unrelated valid image must not satisfy the declared resource mapping.
            (root/'index.html').write_text(html.replace('/assets/missing.png','/assets/wrong.png'))
            mismatch=audit(base,manifest,args.out_dir/'wrong-resource',[390],args.executable)
            if mismatch['pass']:raise AssertionError('Wrong image was incorrectly accepted')
            report={'pass':True,'positive_viewports':[390,768,1440],'positive_consumer_checks':15,'broken_image_rejected':True,'wrong_resource_rejected':True,'native_generation_tested':False,'remote_machine_tested':False,'note':'Synthetic fixtures only. Asset generation and artistic/reference parity were not evaluated.'}
            new_file(args.out_dir/'summary.json',(json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report,indent=2))
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)
    return 0
if __name__=='__main__':raise SystemExit(main())

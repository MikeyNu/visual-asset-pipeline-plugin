from __future__ import annotations
import argparse
import base64
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import assetctl as a
import generate_openai as g
import browser_audit as b
from PIL import Image, ImageDraw


def raster(mode='RGBA', color=(255,0,0,0), size=(80,100), cutout=True, fmt='PNG'):
    im=Image.new(mode,size,color)
    if cutout:
        ImageDraw.Draw(im).rectangle((20,20,60,80),fill=(40,100,160,255) if mode=='RGBA' else (40,100,160))
    out=io.BytesIO();im.save(out,format=fmt);return out.getvalue()


def plan(outputs=None, consumers=None):
    return {'schema_version':'1.0.0','assets':[{'id':'hero-object','status':'planned','alpha_required':True,
      'brief':{'purpose':'A test cutout'},'outputs':outputs or [],'consumers':consumers or []}]}


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'original.png';self.source.write_bytes(raster())
        self.out=self.root/'out';self.out.mkdir()
    def tearDown(self):self.temp.cleanup()
    def test_actual_alpha_and_bounds(self):
        x=a.inspect_bytes(self.source.read_bytes(),'a.png');a.require_alpha(x)
        self.assertEqual(x['alpha']['visible_bounds'],[20,20,61,81]);self.assertFalse(x['alpha']['touches_canvas_edge'])
    def test_fake_opaque_checkerboard_rejected(self):
        im=Image.new('RGB',(32,32),'white');d=ImageDraw.Draw(im)
        for y in range(0,32,8):
            for x in range(0,32,8):
                if (x+y)//8%2==0:d.rectangle((x,y,x+7,y+7),fill='gray')
        s=io.BytesIO();im.save(s,format='PNG')
        with self.assertRaises(a.AssetError):a.require_alpha(a.inspect_bytes(s.getvalue()))
    def test_empty_alpha_rejected(self):
        with self.assertRaises(a.AssetError):a.require_alpha(a.inspect_bytes(raster(cutout=False)))
    def test_extension_does_not_define_format(self):
        x=a.inspect_bytes(raster(mode='RGB',color='white',fmt='JPEG'),'not-a-png.png')
        self.assertEqual(x['format'],'JPEG');self.assertFalse(x['suffix_matches'])
    def test_corrupt_data_rejected(self):
        with self.assertRaises(a.AssetError):a.inspect_bytes(b'not image data')
    def test_no_upscaling_and_native_unchanged(self):
        original=self.source.read_bytes();r=a.prepare(self.source,self.out,'hero',[40,80,1000],'webp',alpha_required=True)
        self.assertEqual(r['effective_widths'],[40,80]);self.assertEqual(original,self.source.read_bytes())
        self.assertEqual(len(r['outputs']),2);self.assertFalse(r['upscaled'])
        for o in r['outputs']:self.assertIn(o['sha256'][:12],o['file']);a.require_alpha(o)
    def test_prepare_repeat_idempotent(self):
        a.prepare(self.source,self.out,'hero',[40],'png')
        r=a.prepare(self.source,self.out,'hero',[40],'png')
        self.assertEqual(r['outputs'][0]['write'],'unchanged')
    def test_jpeg_alpha_loss_rejected(self):
        with self.assertRaises(a.AssetError):a.prepare(self.source,self.out,'hero',[40],'jpeg')
    def test_invalid_name_rejected(self):
        with self.assertRaises(a.AssetError):a.prepare(self.source,self.out,'../hero',[40],'png')
    def test_invalid_dimensions_rejected(self):
        with self.assertRaises(a.AssetError):a.prepare(self.source,self.out,'hero',[0],'png')
    def test_exif_orientation_recorded(self):
        im=Image.new('RGB',(40,80),'white');exif=Image.Exif();exif[274]=6
        data=io.BytesIO();im.save(data,format='JPEG',exif=exif)
        x=a.inspect_bytes(data.getvalue());self.assertEqual(x['native_encoded_dimensions'],[40,80]);self.assertEqual((x['width'],x['height']),(80,40))
    def test_create_only_no_overwrite(self):
        target=self.root/'target.txt';a.new_file(target,b'first')
        with self.assertRaises(a.AssetError):a.new_file(target,b'second')
        self.assertEqual(target.read_bytes(),b'first')
    def test_bad_portable_paths(self):
        for value in ('../x','/root/x','C:\\x','a/../b','a//b','CON.png','a/nul.webp','a/.git/x','a/file.','a/file ', 'a\\b','a\x00b'):
            with self.subTest(value=value),self.assertRaises(a.AssetError):a.relative_parts(value)
    @unittest.skipUnless(hasattr(os,'symlink'),'symlinks unavailable')
    def test_symlink_escape_rejected(self):
        (self.root/'linked').symlink_to(self.out,target_is_directory=True)
        with self.assertRaises(a.AssetError):a.safe_under(self.root,'linked/a.png')
    def make_bundle(self):
        src=self.root/'src';src.mkdir();p=src/'public/images/generated';p.mkdir(parents=True)
        (p/'hero.png').write_bytes(self.source.read_bytes())
        bundle=self.root/'bundle.json';report=a.pack(src,['public/images/generated/hero.png'],bundle)
        dest=self.root/'dest';dest.mkdir();return dest,bundle,report
    def test_roundtrip_dryrun_and_apply(self):
        dest,bundle,r=self.make_bundle()
        dry=a.receive(dest,bundle,r['sha256'],'public/images/generated')
        self.assertEqual(dry['mode'],'dry-run');self.assertFalse((dest/'public').exists())
        real=a.receive(dest,bundle,r['sha256'],'public/images/generated',True)
        self.assertEqual(real['files'][0]['action'],'created')
        self.assertEqual((dest/'public/images/generated/hero.png').read_bytes(),self.source.read_bytes())
    def test_transfer_repeat_idempotent(self):
        dest,bundle,r=self.make_bundle();a.receive(dest,bundle,r['sha256'],'public/images/generated',True)
        report=a.receive(dest,bundle,r['sha256'],'public/images/generated',True)
        self.assertEqual(report['files'][0]['action'],'unchanged')
    def test_envelope_hash_required(self):
        dest,bundle,r=self.make_bundle()
        with self.assertRaises(a.AssetError):a.receive(dest,bundle,'0'*64,'public/images/generated',True)
        self.assertEqual(list(dest.iterdir()),[])
    def test_payload_hash_checked_even_with_valid_envelope_hash(self):
        dest,bundle,r=self.make_bundle();obj=json.loads(bundle.read_bytes());obj['files'][0]['sha256']='0'*64
        data=json.dumps(obj).encode();bundle.write_bytes(data)
        with self.assertRaises(a.AssetError):a.receive(dest,bundle,a.digest(data),'public/images/generated',True)
    def test_prefix_violation_rejected(self):
        dest,bundle,r=self.make_bundle()
        with self.assertRaises(a.AssetError):a.receive(dest,bundle,r['sha256'],'src/assets',True)
    def test_destination_conflict_preflight(self):
        dest,bundle,r=self.make_bundle();obj=json.loads(bundle.read_bytes());extra=dict(obj['files'][0]);extra['path']='public/images/generated/second.png';obj['files'].append(extra)
        data=json.dumps(obj).encode();bundle.write_bytes(data)
        folder=dest/'public/images/generated';folder.mkdir(parents=True);(folder/'second.png').write_bytes(b'existing user work')
        with self.assertRaises(a.AssetError):a.receive(dest,bundle,a.digest(data),'public/images/generated',True)
        self.assertFalse((folder/'hero.png').exists());self.assertEqual((folder/'second.png').read_bytes(),b'existing user work')
    def test_case_collision_rejected(self):
        dest,bundle,r=self.make_bundle();obj=json.loads(bundle.read_bytes());extra=dict(obj['files'][0]);extra['path']='public/images/generated/HERO.png';obj['files'].append(extra)
        data=json.dumps(obj).encode();bundle.write_bytes(data)
        with self.assertRaises(a.AssetError):a.receive(dest,bundle,a.digest(data),'public/images/generated',True)
    def test_valid_comment_tag(self):
        p=self.root/'component.tsx';p.write_text('{/* <visual-asset>'+json.dumps(plan()['assets'][0])+'</visual-asset> */}')
        parsed=a.scan_tags(p);self.assertEqual(parsed['assets'][0]['id'],'hero-object')
    def test_raw_tag_rejected(self):
        p=self.root/'index.html';p.write_text('<visual-asset>'+json.dumps(plan()['assets'][0])+'</visual-asset>')
        with self.assertRaises(a.AssetError):a.scan_tags(p)
    def test_duplicate_tag_id_rejected(self):
        p=self.root/'index.html';tag='<!-- <visual-asset>'+json.dumps(plan()['assets'][0])+'</visual-asset> -->';p.write_text(tag*2)
        with self.assertRaises(a.AssetError):a.scan_tags(p)
    def test_code_in_tag_not_executed(self):
        p=self.root/'index.html';p.write_text('<!-- <visual-asset>__import__("os").system("echo nope")</visual-asset> -->')
        with self.assertRaises(ValueError):a.scan_tags(p)
    def test_static_valid_files_and_consumers(self):
        i=a.inspect_bytes(self.source.read_bytes());o={k:i[k] for k in ('sha256','width','height','bytes','format')};o['path']='original.png';o['public_url']='/original.png'
        (self.root/'index.html').write_text('<img src="/original.png" alt="">')
        p=self.root/'plan.json';p.write_text(json.dumps(plan([o],[{'file':'index.html'}])))
        self.assertTrue(a.verify(self.root,p)['pass'])
    def test_static_missing_integration_fails(self):
        i=a.inspect_bytes(self.source.read_bytes());o={k:i[k] for k in ('sha256','width','height','bytes','format')};o['path']='original.png'
        (self.root/'index.html').write_text('<h1>No visual reference</h1>')
        p=self.root/'plan.json';p.write_text(json.dumps(plan([o],[{'file':'index.html'}])))
        self.assertFalse(a.verify(self.root,p)['pass'])
    def test_plan_without_files_not_delivered(self):
        p=self.root/'plan.json';p.write_text(json.dumps(plan()));self.assertFalse(a.verify(self.root,p)['pass'])


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.prompt=self.root/'prompt.txt';self.prompt.write_text('Isolated object, transparent background, no text.')
        self.args=argparse.Namespace(prompt_file=self.prompt,model='test-only-mock-model',output=self.root/'new.png',
         mode='generate',input=None,mask=None,size='auto',quality='auto',background='transparent',execute=False,paid_api_approved=False)
    def tearDown(self):self.temp.cleanup()
    def factory(self,**kwargs):
        self.client_args=kwargs
        def make(**request):
            self.request=request
            return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(self.response).decode())],_request_id='mock-request')
        return SimpleNamespace(images=SimpleNamespace(generate=make,edit=make),close=lambda:None)
    def test_dryrun_no_key_no_request_no_files(self):
        with patch.dict(os.environ,{},clear=True):
            result=g.run(self.args,lambda **kw:self.fail('Network factory called in dry run'))
        self.assertFalse(result['network_request_made']);self.assertFalse(self.args.output.exists())
    def test_execution_requires_explicit_approval(self):
        self.args.execute=True
        with self.assertRaises(a.AssetError):g.run(self.args,self.factory)
    def test_execution_requires_key(self):
        self.args.execute=True;self.args.paid_api_approved=True
        with patch.dict(os.environ,{},clear=True),self.assertRaises(a.AssetError):g.run(self.args,self.factory)
    def test_mocked_png_saved_and_receipt(self):
        self.args.execute=True;self.args.paid_api_approved=True;self.response=raster()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-not-a-real-key'}):result=g.run(self.args,self.factory)
        self.assertEqual(result['status'],'candidate-saved');self.assertEqual(self.args.output.read_bytes(),self.response)
        self.assertEqual(self.client_args['max_retries'],0)
        receipt=self.args.output.with_suffix('.receipt.json').read_text()
        self.assertNotIn('unit-test-not-a-real-key',receipt);self.assertNotIn(self.prompt.read_text(),receipt)
    def test_rejected_alpha_keeps_candidate_without_retry(self):
        self.args.execute=True;self.args.paid_api_approved=True;self.response=raster(color=(255,255,255,255))
        with patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-not-a-real-key'}):result=g.run(self.args,self.factory)
        self.assertEqual(result['status'],'candidate-saved-alpha-rejected');self.assertTrue(self.args.output.exists())
    def test_missing_edit_input_rejected(self):
        self.args.mode='edit'
        with self.assertRaises(a.AssetError):g.run(self.args,self.factory)
    def test_existing_output_prevents_paid_request(self):
        self.args.output.write_bytes(b'previous work')
        with self.assertRaises(a.AssetError):g.run(self.args,lambda **kw:self.fail('Should not call network'))
    def test_mask_size_mismatch(self):
        inp=self.root/'input.png';inp.write_bytes(raster());mask=self.root/'mask.png';mask.write_bytes(raster(size=(100,120)))
        self.args.mode='edit';self.args.input=[inp];self.args.mask=mask
        with self.assertRaises(a.AssetError):g.run(self.args,self.factory)
    def test_provider_error_not_leaked(self):
        self.args.execute=True;self.args.paid_api_approved=True
        def fail(**kw):raise RuntimeError('private key prompt signed URL')
        factory=lambda **kw:SimpleNamespace(images=SimpleNamespace(generate=fail),close=lambda:None)
        with patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-not-a-real-key'}):
            with self.assertRaises(a.AssetError) as result:g.run(self.args,factory)
        self.assertNotIn('private key',str(result.exception));self.assertFalse(self.args.output.exists())
    def test_missing_response_not_fabricated(self):
        self.args.execute=True;self.args.paid_api_approved=True
        factory=lambda **kw:SimpleNamespace(images=SimpleNamespace(generate=lambda **k:SimpleNamespace(data=[])),close=lambda:None)
        with patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-not-a-real-key'}),self.assertRaises(a.AssetError):g.run(self.args,factory)
        self.assertFalse(self.args.output.exists())


class BrowserUtilityTests(unittest.TestCase):
    def test_optimizer_url_unwraps(self):
        self.assertEqual(b.resource_identity('https://example.com/_next/image?url=%2Fimages%2Fhero.webp&w=800&q=85'),'/images/hero.webp')
    def test_query_secrets_removed(self):
        self.assertEqual(b.clean_url('https://example.com/a.png?token=private'), 'https://example.com/a.png')
    def test_same_origin_route(self):
        self.assertEqual(b.route_url('http://127.0.0.1:3000/base/','page'),'http://127.0.0.1:3000/base/page')
    def test_cross_origin_route_rejected(self):
        with self.assertRaises(a.AssetError):b.route_url('http://127.0.0.1:3000','https://other.example/a')
    def test_credential_url_rejected(self):
        with self.assertRaises(a.AssetError):b.route_url('http://user:secret@example.com','/')

if __name__=='__main__':unittest.main()

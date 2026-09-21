from pathlib import Path
import json,re,unittest
import yaml,jsonschema
ROOT=Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        text=(ROOT/'SKILL.md').read_text();header=text.split('---',2)[1];meta=yaml.safe_load(header)
        self.assertEqual(meta['name'],ROOT.name);self.assertLessEqual(len(meta['name']),64)
        self.assertLessEqual(len(meta['description']),1024);self.assertLessEqual(len(meta['compatibility']),500)
        self.assertLess(len(text.splitlines()),500);self.assertIsInstance(meta['metadata']['version'],str)
    def test_frontmatter_resources_exist(self):
        text=(ROOT/'SKILL.md').read_text()
        for value in re.findall(r'`((?:references|templates|scripts)/[^`]+)`',text):
            with self.subTest(resource=value):self.assertTrue((ROOT/value).is_file())
    def test_plan_matches_schema(self):
        schema=json.loads((ROOT/'templates/asset-manifest.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(json.loads((ROOT/'templates/asset-plan.json').read_text()),schema)
    def test_tag_matches_schema(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from assetctl import scan_tags
        schema=json.loads((ROOT/'templates/asset-manifest.schema.json').read_text())
        jsonschema.validate(scan_tags(ROOT/'templates/asset-tag-example.html'),schema)
    def test_no_em_dash(self):
        for f in ROOT.rglob('*'):
            if f.suffix in {'.md','.py','.json','.yaml','.html','.txt'} and f.is_file():
                with self.subTest(file=str(f.relative_to(ROOT))):self.assertNotIn(chr(0x2014),f.read_text())
    def test_agent_metadata(self):
        data=yaml.safe_load((ROOT/'agents/openai.yaml').read_text())
        self.assertTrue(data['policy']['allow_implicit_invocation']);self.assertIn('$visual-asset-pipeline',data['interface']['default_prompt'])
    def test_evaluation_status_truthful(self):
        data=json.loads((ROOT/'evals/scenarios.json').read_text());self.assertEqual(len(data['scenarios']),20)
        self.assertEqual(data['status'],'defined_not_run')
        self.assertEqual(len({x['id'] for x in data['scenarios']}),20)
        for case in data['scenarios']:self.assertEqual(case['execution_status'],'not_run')
    def test_research_ids_defined(self):
        text=(ROOT/'RESEARCH.md').read_text()
        for f in list((ROOT/'references').glob('*.md'))+[ROOT/'INSTALL.md']:
            for number in re.findall(r'\[R(\d+)\]',f.read_text()):
                with self.subTest(source=number):self.assertIn(f'### R{number}.',text)

if __name__=='__main__':unittest.main()

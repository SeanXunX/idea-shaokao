"""Behavior checks for rendering actual artifacts without modifying research evidence."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_review as renderer
from review_fixture import make_workspace, write_index


def payload(root):
    html = (root / 'final/review.html').read_text()
    return json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>', html, re.S).group(1))


class RenderReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'study'
        self.state, self.index = make_workspace(self.root)

    def state_write(self):
        (self.root / 'state.json').write_text(json.dumps(self.state))

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file()}

    def test_actual_run_metadata_sources_and_multiple_rounds_are_rendered(self):
        before = self.snapshot()
        result = renderer.render(self.root)
        data = payload(self.root)
        self.assertEqual(data['project']['recommendation'], 'Proceed')
        self.assertEqual(data['project']['title'], 'Adaptive cache eviction')
        self.assertEqual(data['project']['version'], 'v01')
        self.assertEqual(data['project']['round'], 2)
        self.assertEqual([r['round'] for r in data['reviewers']], [1, 2])
        self.assertIsNone(data['reviewers'][0]['final'])
        self.assertEqual(data['reviewers'][1]['final']['score'], '6/8')
        self.assertEqual(data['issues'][0]['status'], 'Pending experiment')
        self.assertEqual(data['experiments'][0]['status'], 'Planned')
        for source in data['sources'].values():
            raw = (self.root / source['path']).read_bytes()
            self.assertEqual(source['text'].encode(), raw)
            self.assertEqual(source['sha256'], hashlib.sha256(raw).hexdigest())
        after = self.snapshot()
        self.assertTrue(all(after[key] == value for key, value in before.items()))
        self.assertEqual(set(after) - set(before), {'final/review.html', 'final/review-manifest.json'})
        self.assertEqual(json.loads((self.root / 'final/review-manifest.json').read_text())['workspace_id'], result['workspace_id'])

    def test_identity_survives_regeneration_revision_move_and_manifest_recovery(self):
        identity = renderer.render(self.root)['workspace_id']
        self.state['proposal_version'] = 'v02'
        self.state_write()
        self.assertEqual(renderer.render(self.root)['workspace_id'], identity)
        relocated = self.root.parent / 'relocated'
        shutil.move(str(self.root), relocated)
        self.root = relocated
        self.assertEqual(renderer.render(self.root)['workspace_id'], identity)
        (self.root / 'final/review-manifest.json').unlink()
        self.assertEqual(renderer.render(self.root)['workspace_id'], identity)

    def test_check_mode_does_not_write(self):
        before = self.snapshot()
        self.assertTrue(renderer.render(self.root, check=True)['checked_only'])
        self.assertEqual(self.snapshot(), before)

    def test_invalid_input_keeps_previous_report_and_identity_unchanged(self):
        renderer.render(self.root)
        self.index['issues'][0]['discussion'][0]['source'] = 'missing'
        write_index(self.root, self.index)
        before = self.snapshot()
        with self.assertRaises(renderer.ReviewError):
            renderer.render(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_escaping_paths_and_symlinks_are_rejected(self):
        outside = Path(self.temp.name) / 'private.md'
        outside.write_text('Do not embed this outside file.')
        (self.root / 'escape.md').symlink_to(outside)
        for path in ('../private.md', str(outside), 'escape.md', 'C:\\private.md'):
            with self.subTest(path=path):
                self.index['sources']['escape'] = path
                write_index(self.root, self.index)
                before = self.snapshot()
                with self.assertRaises(renderer.ReviewError):
                    renderer.render(self.root)
                self.assertEqual(self.snapshot(), before)

    def test_missing_non_text_oversized_and_display_sources_fail_explicitly(self):
        paths = {'missing': 'missing.md', 'binary': 'binary.bin', 'large': 'large.txt', 'display': 'final/review-data.json', 'normalized-display': 'final/./review-data.json'}
        (self.root / 'binary.bin').write_bytes(b'\xff\xfe')
        (self.root / 'large.txt').write_bytes(b'x' * (renderer.MAX_SOURCE_BYTES + 1))
        for label, path in paths.items():
            with self.subTest(label=label):
                self.index['sources']['invalid'] = path
                write_index(self.root, self.index)
                with self.assertRaises(renderer.ReviewError):
                    renderer.render(self.root)

    def test_single_agent_partial_run_has_no_invented_roles_or_results(self):
        self.state['execution_mode'] = 'single_agent'
        self.state['current_round'] = 0
        self.state['status'] = 'budget_stopped'
        self.state['recommendation'] = 'Undetermined'
        self.state_write()
        self.index['overview'].update(assessor='Author', recommendation='Undetermined', sources=['report'])
        for collection in ('issues', 'claims', 'reviewers', 'timeline', 'experiments'):
            self.index[collection] = []
        write_index(self.root, self.index)
        renderer.render(self.root)
        data = payload(self.root)
        self.assertEqual(data['project']['mode'], 'single_agent')
        self.assertEqual(data['project']['assessor'], 'Author')
        self.assertEqual(data['project']['round'], 0)
        self.assertEqual(data['reviewers'], [])
        self.assertEqual(data['experiments'], [])
        self.assertEqual(data['issues'], [])

    def test_false_chairs_and_conflicting_recommendations_are_rejected(self):
        self.state['execution_mode'] = 'single_agent'
        self.state_write()
        with self.assertRaises(renderer.ReviewError):
            renderer.render(self.root)
        self.state['execution_mode'] = 'independent'
        self.state['recommendation'] = 'Kill'
        self.state_write()
        with self.assertRaises(renderer.ReviewError):
            renderer.render(self.root)

    def test_duplicate_ids_aliases_and_reserved_sources_are_rejected(self):
        bad = json.loads(json.dumps(self.index))
        bad['issues'].append(bad['issues'][0])
        write_index(self.root, bad)
        with self.assertRaises(renderer.ReviewError): renderer.render(self.root)
        bad = json.loads(json.dumps(self.index))
        bad['issues'][1]['aliases'] = ['I-2', 'R01-R2-01']
        write_index(self.root, bad)
        with self.assertRaises(renderer.ReviewError): renderer.render(self.root)
        self.index['sources']['report'] = 'proposal/v01/proposal.md'
        write_index(self.root, self.index)
        with self.assertRaises(renderer.ReviewError): renderer.render(self.root)

    def test_source_script_text_is_embedded_as_json_not_executable_markup(self):
        dangerous = '</script><script>window.injected = true</script>\u2028'
        (self.root / 'proposal/v01/proposal.md').write_text(dangerous)
        self.index['overview']['title'] = '<img src=x onerror="window.injected=true">'
        write_index(self.root, self.index)
        renderer.render(self.root)
        self.assertEqual(payload(self.root)['sources']['proposal']['text'], dangerous)
        self.assertNotIn(dangerous, (self.root / 'final/review.html').read_text())

    def test_malformed_identity_is_not_silently_reset(self):
        renderer.render(self.root)
        manifest = self.root / 'final/review-manifest.json'
        manifest.write_text('{')
        before = self.snapshot()
        with self.assertRaises(renderer.ReviewError): renderer.render(self.root)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()

"""Behavioral tests for the portable workspace helper."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_research.py"


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "research"
        self.workspace = self.root / "retrieval-audit"

    def run_cli(self, *options, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--slug", "retrieval-audit", *options],
            capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
        return result

    def create(self, *options):
        return self.run_cli("--topic", "Audit retrieval under distribution shift", *options)

    def snapshot(self):
        return {
            str(item.relative_to(self.workspace)): (item.read_bytes(), item.stat().st_mtime_ns)
            for item in self.workspace.rglob("*") if item.is_file()
        }

    def write_state(self, state):
        (self.workspace / "state.json").write_text(json.dumps(state), encoding="utf-8")

    def read_state(self):
        return json.loads((self.workspace / "state.json").read_text(encoding="utf-8"))

    def test_initialization_records_configuration_and_empty_evidence_folders(self):
        result = self.create("--venue", "ICML 2027", "--stage", "implementation", "--max-rounds", "2")
        state = json.loads(result.stdout)["state"]
        self.assertEqual(state, self.read_state())
        self.assertEqual(state["venue"], "ICML 2027")
        self.assertEqual(state["review_stage"], "implementation")
        self.assertEqual(state["max_rounds"], 2)
        self.assertEqual(state["current_round"], 0)
        self.assertEqual(state["execution_mode"], "unselected")
        for folder in ("literature", "ideation", "proposal", "reviews", "rebuttals", "experiments", "final"):
            self.assertEqual(list((self.workspace / folder).iterdir()), [])

    def test_defaults_and_all_stages(self):
        self.create()
        state = self.read_state()
        self.assertEqual(state["review_stage"], "proposal")
        self.assertEqual(state["max_rounds"], 4)
        self.assertEqual(state["venue"], "Unspecified")
        self.run_cli("--slug", "paper-run", "--topic", "Paper evidence", "--stage", "paper")

    def test_existing_workspace_is_never_overwritten(self):
        self.create()
        (self.workspace / "proposal" / "v1.md").write_text("Original proposal", encoding="utf-8")
        before = self.snapshot()
        self.run_cli("--topic", "Different idea", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_resume_preserves_every_file_and_reports_checkpoint(self):
        self.create()
        state = self.read_state()
        state.update(current_round=1, execution_mode="independent", next_action="author_rebuttal")
        state["extra_context"] = {"proposal": "proposal/v1.md"}
        self.write_state(state)
        (self.workspace / "proposal" / "v1.md").write_text("Research contents", encoding="utf-8")
        before = self.snapshot()
        result = self.run_cli("--resume")
        self.assertTrue(json.loads(result.stdout)["resumed"])
        self.assertEqual(json.loads(result.stdout)["state"]["next_action"], "author_rebuttal")
        self.assertEqual(self.snapshot(), before)

    def test_resume_supplied_configuration_must_match(self):
        self.create("--stage", "paper", "--max-rounds", "2")
        before = self.snapshot()
        self.run_cli("--resume", "--stage", "paper", "--max-rounds", "2")
        for option in (("--topic", "Different"), ("--venue", "Different"), ("--stage", "proposal"), ("--max-rounds", "3")):
            with self.subTest(option=option):
                self.run_cli("--resume", *option, success=False)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_slugs_do_not_create_paths(self):
        for slug in ("../escape", "/tmp/escape", "a/b", "a\\b", ".", "", "UPPER", "-bad", "bad-", "a--b", "a" * 65):
            with self.subTest(slug=slug):
                self.run_cli("--slug=" + slug, "--topic", "Test", success=False)
        self.assertFalse(self.root.exists())

    def test_invalid_configuration_does_not_create_workspace(self):
        for options in ((), ("--topic", " "), ("--topic", "Test", "--max-rounds", "0"), ("--topic", "Test", "--max-rounds", "5")):
            with self.subTest(options=options):
                self.run_cli(*options, success=False)
        self.assertFalse(self.root.exists())

    def test_resume_missing_workspace_does_not_create_it(self):
        self.run_cli("--resume", success=False)
        self.assertFalse(self.root.exists())

    def test_resume_rejects_malformed_or_unsupported_state_without_writing(self):
        self.create()
        original = self.read_state()
        for data in ("{", "[]", "null", "\xff"):
            with self.subTest(data=data):
                (self.workspace / "state.json").write_bytes(data.encode("latin-1"))
                before = self.snapshot()
                self.run_cli("--resume", success=False)
                self.assertEqual(self.snapshot(), before)
        for field, invalid in (
            ("schema_version", 2), ("schema_version", True), ("slug", "other"),
            ("topic", ""), ("review_stage", "unknown"), ("max_rounds", 5),
            ("current_round", -1), ("current_round", 5), ("current_round", True),
            ("created_at", "yesterday"), ("updated_at", "2026-01-01T00:00:00"),
        ):
            with self.subTest(field=field, invalid=invalid):
                state = dict(original)
                state[field] = invalid
                self.write_state(state)
                before = self.snapshot()
                self.run_cli("--resume", success=False)
                self.assertEqual(self.snapshot(), before)

    def test_resume_requires_workspace_files_and_directories(self):
        self.create()
        (self.workspace / "experiments").rmdir()
        self.run_cli("--resume", success=False)
        (self.workspace / "experiments").mkdir()
        (self.workspace / "issue_tracker.md").unlink()
        self.run_cli("--resume", success=False)

    def test_workspace_symlink_is_never_followed(self):
        self.root.mkdir()
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        self.workspace.symlink_to(outside, target_is_directory=True)
        self.run_cli("--topic", "Test", success=False)
        self.run_cli("--resume", success=False)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

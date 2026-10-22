from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "luma_brief.py"
spec = importlib.util.spec_from_file_location("luma_brief_under_test", SCRIPT)
brief = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = brief
spec.loader.exec_module(brief)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "briefs"
EXPECTED = json.loads((FIXTURES / "EXPECTED.json").read_text(encoding="utf-8"))


def run(workspace, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = brief.brief_main(["--workspace", str(workspace), *args], prog="luma_brief.py")
    return code, out.getvalue(), err.getvalue()


class BriefTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ws = Path(tmp.name) / "workspace"
        shutil.copytree(FIXTURES / "workspace", self.ws)

    def test_fixture_set_passes_and_fails_exactly_per_expected(self):
        code, out, _ = run(self.ws, "check", "--json")
        self.assertEqual(code, 1)
        found = {Path(path).relative_to(self.ws).as_posix(): [p["rule"] for p in problems]
                 for path, problems in json.loads(out).items()}
        self.assertEqual(found, {name: ([rule] if rule else []) for name, rule in EXPECTED.items()})

    def test_valid_briefs_alone_check_clean(self):
        valid = [str(self.ws / name) for name, rule in EXPECTED.items() if not rule]
        self.assertEqual(run(self.ws, "check", *valid)[0], 0)

    def test_index_regeneration_is_byte_identical(self):
        self.assertEqual(run(self.ws, "index")[0], 0)
        index = self.ws / ".agents" / "briefs" / "INDEX.md"
        first = index.read_bytes()
        self.assertEqual(run(self.ws, "index")[0], 0)
        self.assertEqual(index.read_bytes(), first)
        self.assertIn(b"2026-10-22-open-reading", first)

    def test_archive_with_supersedes_flips_the_target(self):
        root = self.ws / ".agents" / "briefs"
        code, _, err = run(self.ws, "archive", "2026-10-22-reading-v2")
        self.assertEqual(code, 0, err)
        self.assertFalse((root / "2026-10-22-reading-v2.md").exists())
        moved = root / "archive" / "2026" / "2026-10-22-reading-v2.md"
        self.assertEqual(brief.load(moved).meta["status"], "done")
        target = brief.load(root / "archive" / "2026" / "2026-10-18-old-reading.md")
        self.assertEqual(target.meta["status"], "superseded")
        self.assertTrue((root / "INDEX.md").is_file())

    def test_new_skeleton_fails_only_on_goal_deliverables_and_success_criteria(self):
        code, out, err = run(self.ws, "new", "fresh-slug", "--sender", "luke", "--date", "2026-10-24")
        self.assertEqual(code, 0, err)
        path = Path(out.strip())
        rules = [p.rule for p in brief.validate(brief.load(path), brief.approval_line(self.ws))]
        self.assertEqual(len(rules), len(set(rules)), rules)
        self.assertEqual({rule.split(".")[0] for rule in rules}, {"goal", "deliverables", "success_criteria"}, rules)

    def test_new_rejects_identity_sender(self):
        code, _, err = run(self.ws, "new", "fresh-slug", "--sender", "agent")
        self.assertEqual(code, 1)
        self.assertIn("error", err)


if __name__ == "__main__":
    unittest.main()

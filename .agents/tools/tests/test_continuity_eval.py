import importlib.util
from pathlib import Path
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("continuity_eval_test", TOOLS / "luma_continuity_eval.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def case_with(path):
    return {"format_version": 1, "model": "test", "repetitions": 1, "timeout_seconds": 10,
            "readme": "Project", "common_prompt": "Review locally",
            "stages": [{"id": "intro", "prompt": "Explain this", "files": {path: "source"}}],
            "probes": [{"id": "apply", "prompt": "Recommend next work"}]}


class ContinuityEvaluationTests(unittest.TestCase):
    def test_case_cannot_replace_seed_or_escape_input_namespace(self):
        for path in ("../outside", "inputs/../../outside", ".agents/AGENTS.md", "inputs/../.agents/AGENTS.md", "inputs/requests/01-intro.txt", "inputs\\outside", "/inputs/source"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                runner.validate_case(case_with(path))
        runner.validate_case(case_with("inputs/excerpt.md"))

    def test_probe_cannot_introduce_extra_evidence_or_duplicate_sources(self):
        case = case_with("inputs/source.md")
        case["probes"][0]["files"] = {"inputs/answer.md": "answer"}
        with self.assertRaises(ValueError):
            runner.validate_case(case)
        case = case_with("inputs/source.md")
        case["stages"].append({"id": "second", "prompt": "Review", "files": {"inputs/source.md": "replacement"}})
        with self.assertRaises(ValueError):
            runner.validate_case(case)

    def test_retained_records_distinguish_authored_understanding_from_supplied_inputs(self):
        original = {"README.md": b"index", ".agents/AGENTS.md": b"core"}
        after = {**original, "inputs/source.md": b"original evidence", "wiki/topic.md": b"synthesis", ".agents/memory/record.md": b"provenance"}
        retained = runner.retained_records(after, original)
        self.assertEqual(set(retained), {"wiki/topic.md", ".agents/memory/record.md"})
        after["README.md"] = b"index with navigation"
        self.assertIn("README.md", runner.retained_records(after, original))

    def test_existing_results_are_preserved_before_any_host_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = root / "evidence.json"
            protected.write_text("original")
            with self.assertRaises(ValueError):
                runner.compare(root / "missing-source", root / "missing-case", root)
            self.assertEqual(protected.read_text(), "original")


if __name__ == "__main__":
    unittest.main()

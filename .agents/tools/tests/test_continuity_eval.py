import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


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

    def test_v2_replacements_preserve_bytes_and_manifest_digests(self):
        import hashlib
        import json
        case = case_with("inputs/source.md")
        case["format_version"] = 2
        case["stages"].append({"id": "update", "prompt": "Inspect revision", "files": {"inputs/source.md": "new"}})
        runner.validate_case(case)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            put = lambda r, fs: [((r / n).parent.mkdir(parents=True, exist_ok=True), (r / n).write_text(t)) for n, t in fs.items()]
            runner.stage_inputs(root, case["stages"][0], 1, put, 2, [])
            manifest = []
            runner.stage_inputs(root, case["stages"][1], 2, put, 2, manifest)
            archived = root / "inputs/history/02-update/source.md"
            self.assertEqual(archived.read_text(), "source")
            entry = json.loads((root / "inputs/history/manifest.json").read_text())[0]
            self.assertEqual(entry["previous_sha256"], hashlib.sha256(b"source").hexdigest())
            self.assertEqual(entry["current_sha256"], hashlib.sha256(b"new").hexdigest())

    def test_v2_probe_replacements_are_independent_and_safe_paths(self):
        case = case_with("inputs/source.md")
        case["format_version"] = 2
        case["probes"][0]["files"] = {"inputs/source.md": "probe"}
        case["probes"].append({"id": "other", "prompt": "Other", "files": {"inputs/source.md": "other"}})
        runner.validate_case(case)
        for path in ("inputs/history/file", "inputs/requests/a", "inputs/a/../b", "inputs/a:b", "inputs/a\\b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                runner.validate_case(case_with(path))
        case["stages"][0]["files"] = ["invalid"]
        with self.assertRaises(ValueError):
            runner.validate_case(case)
        case["stages"][0]["files"] = {"inputs/a": "x"}
        case["probes"][0]["files"] = {"inputs/a/b": "y"}
        with self.assertRaises(ValueError):
            runner.validate_case(case)


    def test_v2_allows_only_later_stage_replacement_and_effort_types(self):
        case = case_with("inputs/source.md")
        case["format_version"] = 2
        case["reasoning_effort"] = "medium"
        case["stages"].append({"id": "later", "prompt": "Review revision", "files": {"inputs/source.md": "replacement"}})
        runner.validate_case(case)
        for effort in (None, True, 3, "extreme"):
            case["reasoning_effort"] = effort
            with self.assertRaises(ValueError):
                runner.validate_case(case)

    def test_transition_preflights_reserved_targets_without_source_loss(self):
        for conflict in ("symlink-history", "symlink-requests", "archive-exists", "parent-file"):
            with self.subTest(conflict=conflict), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "inputs").mkdir()
                (root / "inputs/source.md").write_text("old")
                if conflict == "parent-file":
                    (root / "inputs/requests").write_text("not a directory")
                elif conflict.startswith("symlink"):
                    outside = root / "outside"
                    outside.mkdir()
                    reserved = "history" if conflict == "symlink-history" else "requests"
                    (root / ("inputs/" + reserved)).symlink_to(outside, target_is_directory=True)
                else:
                    archive = root / "inputs/history/02-update/source.md"
                    archive.parent.mkdir(parents=True)
                    archive.write_text("previous archive")
                before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                def put(r, files):
                    for name, text in files.items():
                        path = r / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(text)
                with self.assertRaises(ValueError):
                    runner.stage_inputs(root, {"id": "update", "prompt": "Review", "files": {"inputs/source.md": "new"}}, 2, put, 2, [])
                self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_forked_transitions_preserve_history_requests_and_equal_inputs(self):
        case = case_with("inputs/source.md")
        case.update(format_version=2, reasoning_effort="medium")
        case["stages"].append({"id": "update", "prompt": "Inspect revision", "files": {"inputs/source.md": "current"}})
        case["probes"] = [
            {"id": "changed", "prompt": "Apply changed source", "files": {"inputs/source.md": "probe"}},
            {"id": "unchanged", "prompt": "Continue existing work"}]
        observations = []
        actual_load = runner.load_module
        actual_host = actual_load("continuity_fake_host_parser", TOOLS / "luma_host_check.py")

        def fake_process(command, root, timeout):
            if command == ["omp", "--version"]:
                return {"returncode": 0, "stdout": "omp/test", "stderr": "", "timed_out": False, "elapsed_seconds": 0}
            prompt = command[-1]
            core = root / ".agents/AGENTS.md"
            startup = prompt.startswith("Without tools,")
            text = ("CONTINUITY-CORE-LOADED" if core.exists() else "ABSENT") if startup else "done"
            observations.append({"root": root.name, "startup": startup, "command": command,
                                 "inputs": {p.relative_to(root).as_posix(): p.read_bytes() for p in (root / "inputs").rglob("*") if p.is_file()}})
            event = {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}
            return {"returncode": 0, "stdout": json.dumps(event), "stderr": "", "timed_out": False, "elapsed_seconds": 0}

        def load(name, path):
            if path.name == "luma_host_check.py":
                return SimpleNamespace(run_process=fake_process, event_observations=actual_host.event_observations,
                                       resource_digest=actual_host.resource_digest)
            return actual_load(name, path)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case_path = root / "case.json"
            case_path.write_text(json.dumps(case))
            with mock.patch.object(runner, "load_module", side_effect=load):
                result = runner.compare(TOOLS.parents[1], case_path, root / "results")
            self.assertFalse(result["chain_errors"])
            self.assertEqual(len(result["runs"]), 10)
            self.assertTrue(all(all(r["mechanical_checks"].values()) for r in result["runs"]))
        self.assertTrue(all(o["command"][o["command"].index("--thinking") + 1] == "medium" for o in observations))
        for probe, current in (("changed", b"probe"), ("unchanged", b"current")):
            inputs = [o["inputs"] for o in observations if o["root"].endswith("-probe-" + probe)]
            self.assertEqual(len(inputs), 3)
            self.assertTrue(all(value == inputs[0] for value in inputs))
            self.assertEqual(inputs[0]["inputs/source.md"], current)
            self.assertEqual(inputs[0]["inputs/history/02-update/source.md"], b"source")
            self.assertIn("inputs/requests/01-intro.txt", inputs[0])
            entries = json.loads(inputs[0]["inputs/history/manifest.json"])
            self.assertEqual([entry["stage_id"] for entry in entries], ["intro", "update"] + (["changed"] if probe == "changed" else []))
            if probe == "changed":
                self.assertEqual(inputs[0][entries[-1]["archived_path"]], b"current")
                self.assertIn("inputs/requests/03-changed.txt", inputs[0])
            else:
                self.assertNotIn("inputs/history/03-changed/source.md", inputs[0])
                self.assertIn("inputs/requests/04-unchanged.txt", inputs[0])

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

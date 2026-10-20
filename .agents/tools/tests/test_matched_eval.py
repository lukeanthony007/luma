import importlib.util
import json
from pathlib import Path
import unittest


TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("luma_matched_eval_test", TOOLS / "luma_matched_eval.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
HOST = runner.load_module("matched_test_host", TOOLS / "luma_host_check.py")


class MatchedEvaluationTests(unittest.TestCase):
    def test_typed_json_rejects_boolean_quantity_and_missing_null(self):
        task = {"expected": {"artifact": "answer.json", "fields": {"item_count": 1}}}
        checks = runner.grade({}, {"answer.json": b'{"item_count":true,"reason":"x"}'}, task, [])
        self.assertFalse(checks["field:item_count"])
        task["expected"]["fields"]["item_count"] = None
        self.assertFalse(runner.grade({}, {"answer.json": b'{}'}, task, [])["field:item_count"])

    def test_correct_value_does_not_hide_source_damage_or_empty_reason(self):
        task = {"protected": ["source.md"], "expected": {"artifact": "answer.json", "fields": {"item_count": 24}}}
        checks = runner.grade({"source.md": b"original"}, {"source.md": b"altered", "answer.json": b'{"item_count":24,"reason":""}'}, task, [])
        self.assertTrue(checks["field:item_count"])
        self.assertFalse(checks["protected:source.md"])
        self.assertFalse(checks["reason_present"])

    def test_capturing_evidence_is_not_an_installed_seed_edit(self):
        before = {".agents/AGENTS.md": b"core"}
        after = {**before, ".agents/memory/batch/source.md": b"evidence"}
        self.assertTrue(all(runner.grade(before, after, {}, []).values()))
        after[".agents/AGENTS.md"] = b"changed"
        self.assertFalse(runner.grade(before, after, {}, [])["seed_unchanged"])

    def test_usage_counts_only_completed_assistant_messages(self):
        events = [
            {"type": "tool_execution_start", "toolName": "read"},
            {"type": "message_update", "message": {"role": "assistant", "usage": {"input": 999}}},
            {"type": "message_end", "message": {"role": "toolResult", "usage": {"input": 999}}},
            {"type": "message_end", "message": {"role": "assistant", "model": "test", "content": [{"type": "text", "text": "done"}], "usage": {"input": 10, "output": 2, "cacheRead": 20, "cacheWrite": 0}}},
        ]
        counts, messages = runner.metrics("\n".join(json.dumps(event) for event in events), HOST)
        self.assertEqual((counts["input_tokens"], counts["cache_read_tokens"], counts["output_tokens"]), (10, 20, 2))
        self.assertEqual((counts["assistant_messages"], counts["usage_messages"], counts["tool_calls"]), (1, 1, 1))
        self.assertEqual(messages, ["done"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "luma_host_check.py"
spec = importlib.util.spec_from_file_location("luma_host_check_under_test", SCRIPT)
host_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host_check)


class HostCheckTests(unittest.TestCase):
    def test_codex_observations_do_not_mistake_tool_output_for_an_answer(self):
        events = [
            {"type": "item.completed", "item": {"type": "command_execution", "aggregated_output": "checkword"}},
            {"type": "item.started", "item": {"type": "command_execution"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "actual response"}},
        ]
        observed = host_check.event_observations("native preamble\n" + "\n".join(map(json.dumps, events)), "codex")
        self.assertEqual(observed["messages"], ["actual response"])
        self.assertEqual(observed["tool_starts"], ["command_execution"])

    def test_omp_observations_ignore_partial_and_tool_messages(self):
        events = [
            {"type": "message_update", "assistantMessageEvent": {"delta": "partial checkword"}},
            {"type": "message_end", "message": {"role": "toolResult", "content": [{"type": "text", "text": "checkword"}]}},
            {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "actual response"}]}},
            {"type": "tool_execution_start", "toolName": "read"},
        ]
        observed = host_check.event_observations("\n".join(map(json.dumps, events)), "omp")
        self.assertEqual(observed["messages"], ["actual response"])
        self.assertEqual(observed["tool_starts"], ["read"])

    def test_timeout_returns_partial_evidence_and_stops_owned_process(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = host_check.run_process(
                [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(30)"],
                Path(temporary), 0.2)
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["returncode"], 0)
        self.assertIn("started", result["stdout"])
        self.assertLess(result["elapsed_seconds"], 5)

    def test_existing_result_is_not_overwritten_or_retested(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_text("previous observation")
            with mock.patch.object(host_check, "check_host") as run:
                with mock.patch("sys.stderr", new_callable=io.StringIO):
                    with self.assertRaises(SystemExit):
                        host_check.main(["codex", "--output", str(output)])
                run.assert_not_called()
            self.assertEqual(output.read_text(), "previous observation")


if __name__ == "__main__":
    unittest.main()

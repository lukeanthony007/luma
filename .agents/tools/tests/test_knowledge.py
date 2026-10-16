from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from urllib.parse import unquote

SCRIPT = Path(__file__).resolve().parents[1] / "luma_knowledge.py"
spec = importlib.util.spec_from_file_location("luma_knowledge_under_test", SCRIPT)
knowledge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = knowledge
spec.loader.exec_module(knowledge)


class KnowledgeCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def batches(self):
        memory = self.root / ".agents" / "memory"
        return sorted(path for path in memory.iterdir() if path.is_dir()) if memory.exists() else []

    def test_capture_records_real_utc_encoded_link_and_exact_bytes(self):
        data = b"# original\n\x00source\n"
        self.source("notes/a # (draft).md", data)
        import datetime
        before = datetime.datetime.now(datetime.timezone.utc)
        result = knowledge.capture(self.root, ["notes/a # (draft).md"])
        after = datetime.datetime.now(datetime.timezone.utc)
        row = result["sources"][0]
        archived = self.root / row["archived"]
        self.assertEqual(archived.read_bytes(), data)
        self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(row["size"], len(data))
        self.assertIn("%20", row["wiki_link"])
        self.assertIn("%23", row["wiki_link"])
        stamp = row["captured_at"].replace("Z", "+00:00")
        captured = datetime.datetime.fromisoformat(stamp)
        self.assertIsNotNone(captured.tzinfo)
        self.assertLessEqual(before, captured)
        self.assertLessEqual(captured, after)
        self.assertEqual((self.root / "notes/a # (draft).md").read_bytes(), data)

    def test_reuse_and_mixed_reuse_preserve_previous_batch(self):
        self.source("one.md", b"one")
        self.source("two.md", b"two")
        first = knowledge.capture(self.root, ["one.md", "two.md"])
        first_manifest = self.root / first["batch"] / "manifest.json"
        manifest_bytes, mtime = first_manifest.read_bytes(), first_manifest.stat().st_mtime_ns
        archived = [self.root / row["archived"] for row in first["sources"]]
        payload_bytes = [p.read_bytes() for p in archived]
        payload_times = [p.stat().st_mtime_ns for p in archived]
        same = knowledge.capture(self.root, ["one.md", "two.md"])
        self.assertIsNone(same["batch"])
        self.assertTrue(all(row["reused"] for row in same["sources"]))
        self.assertEqual([row["captured_at"] for row in same["sources"]], [row["captured_at"] for row in first["sources"]])
        self.source("two.md", b"two changed")
        sources_before = {name: (self.root / name).read_bytes() for name in ("one.md", "two.md")}
        mixed = knowledge.capture(self.root, ["one.md", "two.md"])
        self.assertTrue(any(row.get("reused") for row in mixed["sources"]))
        changed = next(row for row in mixed["sources"] if row["source"] == "two.md")
        self.assertFalse(changed["reused"])
        manifest = json.loads((self.root / mixed["batch"] / "manifest.json").read_text())
        entry = next(item for item in manifest["files"] if item["source"] == "two.md")
        self.assertEqual(entry["previous"], first["sources"][1]["archived"])
        self.assertEqual(first_manifest.read_bytes(), manifest_bytes)
        self.assertEqual(first_manifest.stat().st_mtime_ns, mtime)
        self.assertEqual([p.read_bytes() for p in archived], payload_bytes)
        self.assertEqual([p.stat().st_mtime_ns for p in archived], payload_times)
        self.assertEqual({name: (self.root / name).read_bytes() for name in sources_before}, sources_before)

    def test_corrupt_retained_payload_fails_without_replacing_it(self):
        self.source("a.md", b"original")
        result = knowledge.capture(self.root, ["a.md"])
        retained = self.root / result["sources"][0]["archived"]
        retained.write_bytes(b"tampered")
        with self.assertRaises(knowledge.KnowledgeError):
            knowledge.capture(self.root, ["a.md"])
        self.assertEqual(retained.read_bytes(), b"tampered")

    def test_invalid_paths_and_source_limits_fail_before_archive_publication(self):
        self.source("ok.md", b"ok")
        self.source(".env", b"secret")
        for names in (["../outside"], ["/etc/passwd"], [".env"], [".agents/hidden"], ["ok.md", "ok.md"]):
            with self.subTest(names=names):
                with self.assertRaises(knowledge.KnowledgeError):
                    knowledge.capture(self.root, list(names))
                self.assertEqual(self.batches(), [])
        with mock.patch.object(knowledge, "MAX_FILE", 1):
            with self.assertRaises(knowledge.KnowledgeError):
                knowledge.capture(self.root, ["ok.md"])
        with mock.patch.object(knowledge, "MAX_TOTAL", 1):
            with mock.patch.object(knowledge, "MAX_FILE", 10):
                with self.assertRaises(knowledge.KnowledgeError):
                    knowledge.capture(self.root, ["ok.md"])
        self.assertEqual(self.batches(), [])

    def test_protected_agents_symlink_ancestor_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.md").write_bytes(b"secret")
        self.source("secret.md", b"eligible source")
        (self.root / ".agents").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(knowledge.KnowledgeError):
            knowledge.capture(self.root, ["secret.md"])
        self.assertEqual(list(outside.iterdir()), [outside / "secret.md"])

    def test_symlink_input_is_rejected(self):
        self.source("real.md", b"safe")
        (self.root / "alias.md").symlink_to(self.root / "real.md")
        with self.assertRaises(knowledge.KnowledgeError):
            knowledge.capture(self.root, ["alias.md"])
        self.assertEqual(self.batches(), [])

    def test_staging_is_cleaned_when_publish_fails(self):
        self.source("a.md", b"safe")
        original = (self.root / "a.md").read_bytes()
        memory = self.root / ".agents" / "memory"
        memory.mkdir(parents=True)
        with mock.patch("pathlib.Path.rename", side_effect=OSError("publish failed")):
            with self.assertRaises((knowledge.KnowledgeError, OSError)):
                knowledge.capture(self.root, ["a.md"])
        self.assertEqual((self.root / "a.md").read_bytes(), original)
        self.assertFalse(any(memory.iterdir()))

    def test_clock_collision_retains_existing_batch(self):
        import datetime
        fixed = datetime.datetime(2026, 5, 1, tzinfo=datetime.timezone.utc)
        self.source("a.md", b"first")
        with mock.patch.object(knowledge, "datetime", wraps=datetime.datetime) as clock:
            clock.now.return_value = fixed
            first = knowledge.capture(self.root, ["a.md"])
            original = (self.root / first["sources"][0]["archived"]).read_bytes()
            self.source("a.md", b"second")
            second = knowledge.capture(self.root, ["a.md"])
            self.assertNotEqual(first["batch"], second["batch"])
            self.assertEqual((self.root / first["sources"][0]["archived"]).read_bytes(), original)
            self.assertTrue(knowledge.check(self.root)["ok"])


class KnowledgeCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        return path

    def test_markdown_links_references_and_obsidian_heading(self):
        self.put("wiki/page.md", "# Heading Name\n## Heading Name\n")
        self.put("target file.md", "# Target\n")
        self.put("wiki/index.md", "[ordinary](../target%20file.md#target)\n[ref][label]\n[collapsed][]\n[shortcut]\n[label]: ../target%20file.md\n[collapsed]: ../target%20file.md\n[shortcut]: ../target%20file.md\n![image](../target%20file.md)\n[[page#Heading Name|alias]]\n`[fake](missing.md)`\n```md\n[also fake](missing.md)\n```\n")
        result = knowledge.check(self.root)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["links_checked"], 6)

    def test_missing_link_and_heading_are_reported_without_mutation(self):
        page = self.put("wiki/a.md", "# Present\n[missing](absent.md)\n[bad heading](b.md#Nope)\n")
        self.put("wiki/b.md", "# Here\n")
        original = page.read_bytes()
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertGreaterEqual(len(result["errors"]), 2)
        self.assertEqual(page.read_bytes(), original)

    def test_ambiguous_wikilink_and_unsafe_link_are_errors(self):
        self.put("wiki/a.md", "[[same]]\n")
        self.put("wiki/one/same.md", "# One\n")
        self.put("wiki/two/same.md", "# Two\n")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("ambiguous" in error["message"].lower() for error in result["errors"]), result["errors"])

    def test_unsafe_link_is_error(self):
        self.put("wiki/a.md", "[escape](../../outside.md)\n")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])
    def test_reference_links_missing_definition_is_reported(self):
        self.put("wiki/a.md", "[missing][definition]\n")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])

    def test_duplicate_heading_slugs_and_fenced_examples(self):
        self.put("wiki/a.md", "# Same\n# Same\n[second](#same-1)\n[[#Same]]\n[[#Same-1]]\n```\n[missing](not-real.md)\n```\n")
        result = knowledge.check(self.root)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["links_checked"], 3)

    def test_unrelated_manifest_format_is_ignored_and_corrupt_own_manifest_fails(self):
        self.put("a.md", "payload")
        captured = knowledge.capture(self.root, ["a.md"])
        batch = self.root / captured["batch"]
        valid = json.loads((batch / "manifest.json").read_text())
        unrelated = self.root / ".agents" / "memory" / "unrelated"
        unrelated.mkdir()
        (unrelated / "manifest.json").write_text("{}", encoding="utf-8")
        self.assertTrue(knowledge.check(self.root)["ok"])
        valid["captured_at"] = "not-a-time"
        (batch / "manifest.json").write_text(json.dumps(valid), encoding="utf-8")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("captured_at" in error["message"] for error in result["errors"]))
    def test_duplicate_manifest_source_record_is_rejected(self):
        self.put("a.md", "payload")
        captured = knowledge.capture(self.root, ["a.md"])
        manifest = self.root / captured["batch"] / "manifest.json"
        data = json.loads(manifest.read_text())
        data["files"].append(dict(data["files"][0]))
        manifest.write_text(json.dumps(data), encoding="utf-8")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])

    def test_markdown_links_do_not_fall_back_to_workspace_root(self):
        self.put("target.md", "# Root target\n")
        self.put("wiki/a.md", "[root target](target.md)\n")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])

    def test_links_reject_symlink_ancestors(self):
        outside = self.root / "actual"
        outside.mkdir()
        (outside / "page.md").write_text("# Page\n")
        (self.root / "alias").symlink_to(outside, target_is_directory=True)
        self.put("wiki/a.md", "[alias](../alias/page.md)\n")
        result = knowledge.check(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("symlink" in row["message"].lower() for row in result["errors"]))

    def test_heading_inline_code_angles_and_ids(self):
        self.put("wiki/other page.md", "# Use `code`\n<a id='custom'></a>\n")
        self.put("wiki/a.md", "[angle](<other page.md#use-code>)\n[custom](other%20page.md#custom)\n")
        result = knowledge.check(self.root)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["links_checked"], 2)

    def test_check_current_and_previous_versions_and_payload_limits(self):
        self.put("a.md", "first")
        first = knowledge.capture(self.root, ["a.md"])
        self.put("a.md", "second")
        knowledge.capture(self.root, ["a.md"])
        self.assertTrue(knowledge.check(self.root)["ok"])
        with mock.patch.object(knowledge, "MAX_FILE", 1):
            self.assertFalse(knowledge.check(self.root)["ok"])
        (self.root / first["sources"][0]["archived"]).write_bytes(b"wrong")
        self.assertFalse(knowledge.check(self.root)["ok"])

    def test_predecessor_must_be_a_verified_source_capture(self):
        self.put("a.md", "first")
        result = knowledge.capture(self.root, ["a.md"])
        manifest = self.root / result["batch"] / "manifest.json"
        value = json.loads(manifest.read_text())
        value["files"][0]["previous"] = "../unrelated"
        manifest.write_text(json.dumps(value))
        self.assertFalse(knowledge.check(self.root)["ok"])

class KnowledgeCliTests(unittest.TestCase):
    def test_cli_json_success_and_actionable_error_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.md").write_text("ok", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["capture", "--root", str(root), "a.md"])
            self.assertEqual(status, 0, err.getvalue())
            self.assertEqual(json.loads(out.getvalue())["sources"][0]["source"], "a.md")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["capture", "--root", str(root), "../outside"])
            self.assertEqual(status, 1)
            self.assertTrue(err.getvalue().strip())
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["not-a-command"])
            self.assertEqual(status, 2)
            self.assertTrue(err.getvalue().strip())
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(knowledge, "capture", side_effect=OSError("disk failure")):
                with redirect_stdout(out), redirect_stderr(err):
                    status = knowledge.main(["capture", "--root", str(root), "a.md"])
            self.assertEqual(status, 1)
            self.assertTrue(err.getvalue().strip())


if __name__ == "__main__":
    unittest.main()

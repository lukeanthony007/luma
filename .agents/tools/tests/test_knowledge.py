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

class KnowledgeCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        return path

    def test_completion_catches_pending_inbox_link_that_wiki_check_misses(self):
        self.put("wiki/index.md", "# Index\n")
        self.put("inbox/pending.md", "[stale](gone.md)\n")
        self.assertTrue(knowledge.check(self.root)["ok"])
        result = knowledge.complete(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("gone.md" in error["message"] for error in result["errors"]))
        self.assertEqual(result["mode"], "completion")
        self.assertEqual(result["scope"]["checked_paths"], ["inbox/pending.md", "wiki/index.md"])

    def test_declared_root_page_outgoing_links_are_checked_and_scoped(self):
        self.put("wiki/index.md", "[root](../maintained.md)\n")
        self.put("maintained.md", "[broken](missing.md)\n")
        self.assertTrue(knowledge.check(self.root)["ok"])
        result = knowledge.complete(self.root, ["maintained.md"])
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing.md" in error["message"] for error in result["errors"]))
        self.assertEqual(result["scope"]["additional_pages"], ["maintained.md"])

    def test_archive_prose_is_excluded_but_capture_integrity_is_checked(self):
        self.put("source.md", "[broken](missing.md)\n")
        captured = knowledge.capture(self.root, ["source.md"])
        self.put("wiki/index.md", "# Index\n")
        result = knowledge.complete(self.root)
        self.assertTrue(result["ok"], result["errors"])
        archived = self.root / captured["sources"][0]["archived"]
        archived.write_text("tampered [broken](missing.md)\n", encoding="utf-8")
        result = knowledge.complete(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])

    def test_missing_roots_are_reported_without_failure(self):
        result = knowledge.complete(self.root)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["scope"]["required_roots"], ["wiki", "inbox"])
        self.assertEqual(result["scope"]["absent_roots"], ["wiki", "inbox"])
        self.assertEqual(result["scope"]["checked_paths"], [])
        self.assertEqual(result["checked_files"], 0)

    def test_symlink_fixed_root_is_not_reported_as_absent(self):
        outside = self.root.parent / (self.root.name + "-wiki")
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        outside_page = outside / "page.md"
        outside_page.write_text("# Outside\n", encoding="utf-8")
        self.addCleanup(outside_page.unlink)
        (self.root / "wiki").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(knowledge.KnowledgeError):
            knowledge.complete(self.root)

    def test_explicit_pages_reject_invalid_and_symlink_paths(self):
        self.put("wiki/index.md", "# Index\n")
        self.put("folder/page.md", "# Page\n")
        self.put("notes.txt", "not markdown")
        outside = self.root.parent / (self.root.name + "-outside.md")
        outside.write_text("# Outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        (self.root / "link.md").symlink_to(outside)
        (self.root / "alias").symlink_to(self.root / "folder", target_is_directory=True)
        for page in ("folder", "notes.txt", "missing.md", "../outside.md", ".agents/memory/x.md", ".git/a.md", "link.md", "alias/page.md"):
            with self.subTest(page=page):
                with self.assertRaises(knowledge.KnowledgeError):
                    knowledge.complete(self.root, [page])

    def test_completion_scope_is_exact_deduplicated_and_read_only(self):
        wiki = self.put("wiki/index.md", "# Index\n")
        inbox = self.put("inbox/task.md", "# Task\n")
        page = self.put("notes.md", "# Notes\n")
        files = [wiki, inbox, page]
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
        result = knowledge.complete(self.root, ["notes.md", "notes.md"])
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["checked_files"], 3)
        self.assertEqual(result["scope"]["selected_paths"], ["wiki", "inbox", "notes.md"])
        self.assertEqual(result["scope"]["checked_paths"], ["inbox/task.md", "notes.md", "wiki/index.md"])
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}, before)
        check = knowledge.check(self.root, ["wiki"])
        self.assertEqual(check["mode"], "check")
        self.assertEqual(check["scope"]["selected_paths"], ["wiki"])
        self.assertEqual(check["scope"]["checked_paths"], ["wiki/index.md"])

    def test_completion_reports_read_limits(self):
        self.put("wiki/index.md", "too large")
        with mock.patch.object(knowledge, "MAX_FILE", 1):
            result = knowledge.complete(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])

    def test_completion_reports_file_count_limit(self):
        self.put("wiki/index.md", "# Index\n")
        self.put("inbox/task.md", "# Task\n")
        with mock.patch.object(knowledge, "MAX_FILES", 1):
            result = knowledge.complete(self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("limit" in row["message"].lower() or "exceeds" in row["message"].lower()
                            for row in result["errors"]), result["errors"])


class KnowledgeCompletionCliTests(unittest.TestCase):
    def test_completion_cli_status_and_rejects_narrowing_selectors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wiki").mkdir()
            (root / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["complete", "--root", str(root)])
            self.assertEqual(status, 0, err.getvalue())
            self.assertEqual(json.loads(out.getvalue())["mode"], "completion")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["complete", "--root", str(root), "wiki"])
            self.assertEqual(status, 2)
            self.assertTrue(err.getvalue())
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["complete", "--root", str(root), "--page", "absent.md"])
            self.assertEqual(status, 1)

    def test_completion_cli_adds_pages_without_excluding_inbox(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wiki").mkdir()
            (root / "inbox").mkdir()
            (root / "wiki/index.md").write_text("# Index\n")
            (root / "inbox/question.md").write_text("[stale](gone.md)\n")
            (root / "one.md").write_text("# One\n")
            (root / "two.md").write_text("# Two\n")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = knowledge.main(["complete", "--root", str(root),
                                         "--page", "one.md", "--page", "two.md"])
            self.assertEqual(status, 1, err.getvalue())
            result = json.loads(out.getvalue())
            self.assertEqual(result["scope"]["additional_pages"], ["one.md", "two.md"])
            self.assertEqual(result["scope"]["checked_paths"],
                             ["inbox/question.md", "one.md", "two.md", "wiki/index.md"])
            self.assertTrue(any(row["path"] == "inbox/question.md" for row in result["errors"]))

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


class AccountStructureTests(unittest.TestCase):
    """Fixtures modeled on observed acquisition outcomes: one subject account vs a per-batch diary."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_linked_subject_account_passes_and_sources_are_ignored(self):
        self.write("README.md", "# Project\n\nSee [the account](wiki/index.md).\n")
        self.write("wiki/index.md", "- [Navigation](navigation.md)\n- [[failure-patterns]]\n")
        self.write("wiki/navigation.md", "Default list sort is newest first (inputs/trajectories/004.json).\n")
        self.write("wiki/failure-patterns.md", "No bulk-close option exists ([source](../inputs/trajectories/012.json)).\n")
        self.write("inputs/trajectories/session-01.md", "original source, not retained understanding\n")
        result = knowledge.account(self.root, ["inputs"])
        self.assertTrue(result["ok"], result)
        self.assertEqual((result["retained_pages"], result["reachable_pages"]), (4, 4))

    def test_observed_diary_failure_is_reported(self):
        # Session 1 wrote subject pages it never linked; later sessions started per-batch files,
        # and a write with a line selector created a junk file.
        self.write("README.md", "# Project\n\nNotes: [batch 2](understanding/batch-02-trajectories.md)\n")
        self.write("wiki/index.md", "- [Navigation](servicenow-navigation.md)\n")
        self.write("wiki/servicenow-navigation.md", "...\n")
        self.write("understanding/batch-02-trajectories.md", "...\n")
        self.write("understanding/batch-03-trajectories.md", "...\n")
        self.write("README.md:15", "stray selector write\n")
        result = knowledge.account(self.root)
        self.assertFalse(result["ok"])
        self.assertEqual(set(result["unreachable"]), {"wiki/index.md", "wiki/servicenow-navigation.md", "understanding/batch-03-trajectories.md"})
        self.assertEqual(result["episodic_count"], 2)
        self.assertEqual(result["invalid_names"], ["README.md:15"])
        self.assertEqual(result["page_directories"], ["understanding", "wiki"])

    def test_missing_entry_point_fails_and_cli_exit_status_follows(self):
        self.write("wiki/index.md", "# Account\n")
        self.assertIsNone(knowledge.account(self.root)["entry_point"])
        out = io.StringIO()
        with redirect_stdout(out):
            status = knowledge.main(["account", "--root", str(self.root)])
        self.assertEqual(status, 1)
        self.assertFalse(json.loads(out.getvalue())["ok"])

    def test_dated_names_are_episodic_but_subject_names_with_numbers_are_not(self):
        self.write("README.md", "[a](notes/2026-10-21.md) [b](notes/http-500-errors.md) [c](notes/form-v2.md)\n")
        for name in ("notes/2026-10-21.md", "notes/http-500-errors.md", "notes/form-v2.md"):
            self.write(name, "x\n")
        result = knowledge.account(self.root)
        self.assertEqual(result["episodic_names"], ["notes/2026-10-21.md"])

    def test_oversized_pages_fail_only_when_a_limit_is_given(self):
        self.write("README.md", "[Index](wiki/index.md)\n")
        self.write("wiki/index.md", "- [Big subject](big-subject.md)\n")
        self.write("wiki/big-subject.md", "x" * 5000)
        unlimited = knowledge.account(self.root)
        self.assertTrue(unlimited["ok"], unlimited)
        self.assertEqual(unlimited["oversized_count"], 0)
        self.assertEqual(unlimited["largest_page_bytes"], 5000)
        limited = knowledge.account(self.root, max_page_bytes=4096)
        self.assertFalse(limited["ok"])
        self.assertEqual(limited["oversized_pages"], ["wiki/big-subject.md"])
        out = io.StringIO()
        with redirect_stdout(out):
            status = knowledge.main(["account", "--root", str(self.root), "--max-page-bytes", "4096"])
        self.assertEqual(status, 1)



class PageSplitTests(unittest.TestCase):
    """The round-4 failure shape: one subject-named page that is really a per-batch diary past the read cap."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def diary(self, batches=6, size=5000):
        sections = "".join(f"## Batch {n:02} task records\n\nFinding {n}. " + "x" * size + f"\nSee [source](../inputs/t{n}.json) and [sites](#the-sites).\n\n"
                           for n in range(1, batches + 1))
        return "# Web environments\n\nIntro.\n\n## The sites\n\nThree sites.\n\n" + sections

    def test_episodic_headings_inside_a_subject_page_fail_the_account(self):
        self.write("README.md", "[Env](wiki/env.md)\n")
        self.write("wiki/env.md", self.diary(batches=2, size=10))
        result = knowledge.account(self.root, ["inputs"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["episodic_count"], 0)
        self.assertEqual(result["episodic_heading_count"], 2)
        self.write("wiki/env.md", "# Env\n\n## Checkout forms\n\n```\n## Batch 01 inside code\n```\n")
        self.assertTrue(knowledge.account(self.root, ["inputs"])["ok"])

    def test_split_keeps_text_links_and_reachability_under_the_limit(self):
        for n in range(1, 7):
            self.write(f"inputs/t{n}.json", "{}")
        self.write("README.md", "[Env](wiki/env.md)\n")
        self.write("wiki/index.md", "[Batch 3](env.md#batch-03-task-records)\n")
        original = self.diary()
        self.write("wiki/env.md", original)
        report = knowledge.split(self.root, "wiki/env.md", 8192)
        self.assertFalse(report["still_oversized"])
        result = knowledge.account(self.root, ["inputs"], 8192)
        self.assertEqual(result["oversized_count"], 0)
        self.assertEqual(result["unreachable_count"], 1)  # index.md was never linked from README; split must not hide that
        self.assertEqual(result["largest_page_bytes"] <= 8192, True)
        children = {c["path"]: (self.root / c["path"]).read_text() for c in report["created"]}
        self.assertEqual(len(children), 7)
        body = "".join(children.values())
        for n in range(1, 7):
            self.assertIn(f"Finding {n}. " + "x" * 5000, body)
        self.assertIn("(../../inputs/t3.json)", children["wiki/env/batch-03-task-records.md"])
        self.assertIn("(the-sites.md#the-sites)", children["wiki/env/batch-03-task-records.md"])
        self.assertIn("(env/batch-03-task-records.md#batch-03-task-records)", (self.root / "wiki/index.md").read_text())
        self.assertTrue(knowledge.check(self.root)["ok"])
        self.assertGreater(result["episodic_count"], 0)  # split repairs size, not organization: batch names remain visible

    def test_a_single_unsplittable_section_is_left_in_place_and_reported(self):
        self.write("wiki/env.md", "# Env\n\n## Sites\n\n" + "y" * 20000 + "\n")
        report = knowledge.split(self.root, "wiki/env.md", 8192)
        self.assertEqual(report["still_oversized"], ["wiki/env.md"])
        self.assertEqual(report["created"], [])
        self.assertIn("y" * 20000, (self.root / "wiki/env.md").read_text())
        self.assertFalse((self.root / "wiki/env").exists())
        self.assertIn("Add subheadings by sub-subject", report["advice"])

    def test_a_single_section_splits_at_its_subsections_and_repeated_splits_do_not_nest(self):
        subsections = "".join(f"### Page {name}\n\n" + f"- `{name} label`\n" * 400 + "\n" for name in ("Home", "Cart", "Checkout"))
        self.write("README.md", "[Shop](wiki/shop.md)\n")
        self.write("wiki/shop.md", "# Shop\n\n## Storefront\n\nStanding labels.\n\n" + subsections)
        first = knowledge.split(self.root, "wiki/shop.md", 8192)
        self.assertEqual(sorted(c["path"] for c in first["created"]), ["wiki/shop/page-cart.md", "wiki/shop/page-checkout.md", "wiki/shop/page-home.md"])
        parent = (self.root / "wiki/shop.md").read_text()
        self.assertIn("## Storefront", parent)
        self.assertIn("### Contents", parent)
        second = knowledge.split(self.root, "wiki/shop/page-home.md", 2048)
        self.assertEqual(second["created"], [])
        self.assertEqual(second["still_oversized"], ["wiki/shop/page-home.md"])
        self.assertFalse((self.root / "wiki/shop/page-home").exists())
        self.assertEqual(knowledge.account(self.root, [], None)["unreachable_count"], 0)

    def test_splitting_an_already_split_page_keeps_one_contents_list_in_the_parent(self):
        self.write("README.md", "[Shop](wiki/shop.md)\n")
        self.write("wiki/shop.md", "# Shop\n\n## Home\n\n" + "- `Home label`\n" * 300 + "\n## Cart\n\n" + "- `Cart label`\n" * 300)
        knowledge.split(self.root, "wiki/shop.md", 4096)
        page = self.root / "wiki/shop.md"
        page.write_text(page.read_text() + "\n## Checkout\n\n" + "- `Checkout label`\n" * 300)
        report = knowledge.split(self.root, "wiki/shop.md", 4096)
        self.assertEqual([c["path"] for c in report["created"]], ["wiki/shop/checkout.md"])
        parent = page.read_text()
        self.assertEqual(parent.count("## Contents"), 1)
        for child in ("shop/home.md", "shop/cart.md", "shop/checkout.md"):
            self.assertIn(f"({child})", parent)
        self.assertFalse((self.root / "wiki/shop/contents.md").exists())
        self.assertEqual(knowledge.account(self.root, [], None)["unreachable_count"], 0)

    def test_long_contents_fall_back_to_titles_and_report_if_still_too_large(self):
        sections = "".join(f"## Topic {chr(65 + n % 26)}{n}\n\n" + "Summary sentence that is fairly long. " * 5 + "\n\n" for n in range(60))
        self.write("wiki/env.md", "# Env\n\n" + sections)
        report = knowledge.split(self.root, "wiki/env.md", 4096)
        parent = (self.root / "wiki/env.md").read_text()
        self.assertNotIn("Summary sentence", parent)
        self.assertLessEqual(len(parent.encode()), 4096)
        self.assertNotIn("wiki/env.md", report["still_oversized"])

    def test_overflow_pages_headings_and_batch_listed_pages_fail_the_account(self):
        self.write("README.md", "[Patterns](wiki/patterns.md) [More](wiki/failure-modes-continued.md) [Q](wiki/open-questions.md) [Forms](wiki/checkout-forms.md)\n")
        self.write("wiki/patterns.md", "# Patterns\n\n## Failure modes\n\n1. Paging loops (batch 06).\n")
        self.write("wiki/failure-modes-continued.md", "# Failure modes, continued (31\u201352)\n")
        self.write("wiki/open-questions.md", "# Open questions\n\n- Batch 04 labels: 032.\n- Batch 05 labels: 041.\n- Batch 06 labels: 053.\n")
        self.write("wiki/checkout-forms.md", "# Checkout forms\n\n- Orders 2023-05 refunds.\n```\n- Batch 01 in code\n- Batch 02\n- Batch 03\n```\n")
        result = knowledge.account(self.root)
        self.assertFalse(result["ok"])
        self.assertEqual(result["overflow_names"], ["wiki/failure-modes-continued.md"])
        self.assertEqual(result["overflow_heading_count"], 1)
        self.assertEqual(result["batch_listed_pages"], ["wiki/open-questions.md"])

    def test_cli_split_exit_status_reflects_remaining_oversize(self):
        self.write("wiki/env.md", "# Env\n\n## A\n\nshort\n")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(knowledge.main(["split", "--root", str(self.root), "wiki/env.md", "--max-bytes", "100"]), 0)
            self.write("wiki/big.md", "# Big\n\n## Only\n\n" + "z" * 500 + "\n")
            self.assertEqual(knowledge.main(["split", "--root", str(self.root), "wiki/big.md", "--max-bytes", "100"]), 1)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "luma.py"
spec = importlib.util.spec_from_file_location("luma_under_test", SCRIPT)
luma = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = luma
spec.loader.exec_module(luma)


def payload():
    return {".agents/AGENTS.md": b"Follow local guidance.\n",
            ".agents/skills/example/SKILL.md": b"---\nname: example\n---\n",
            ".agents/tools/luma.py": b"#!/usr/bin/env python3\n",
            ".agents/tools/luma_knowledge.py": b"#!/usr/bin/env python3\n",
            ".agents/tools/luma_brief.py": b"#!/usr/bin/env python3\n",
            "LICENSE": b"Synthetic license\n"}


def source_tree(root, files=None):
    for name, content in (files or payload()).items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def archive(files):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as tar:
        for name, content in files.items():
            info = tarfile.TarInfo("luma-main/" + name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return stream.getvalue()


class InstallerTests(unittest.TestCase):
    def snapshot(self, root):
        return {str(path.relative_to(root)): path.read_bytes()
                for path in root.rglob("*") if path.is_file()}

    def test_local_source_selects_installable_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_tree(root)
            (root / "README.md").write_text("source marketing")
            (root / ".agents/skills/example/private.bin").write_bytes(b"skip")
            loaded = luma.load_local_source(root)
            self.assertEqual(set(loaded), set(payload()))
            self.assertNotIn("README.md", loaded)
            self.assertNotIn(".agents/skills/example/private.bin", loaded)

    def test_archive_required_resources_and_invalid_data(self):
        self.assertEqual(luma.parse_archive(archive(payload())), payload())
        for omitted in payload():
            incomplete = payload()
            del incomplete[omitted]
            with self.subTest(omitted=omitted), self.assertRaises(luma.LumaError):
                luma.parse_archive(archive(incomplete))
        with self.assertRaises(luma.LumaError):
            luma.parse_archive(b"not a tar archive")
        unsafe = {"../escape": b"x", **payload()}
        with self.assertRaises(luma.LumaError):
            luma.parse_archive(archive(unsafe))

    def test_fresh_and_populated_init_preserves_content_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "notes.txt").write_bytes(b"human data")
            (root / ".agents/memory").mkdir(parents=True)
            (root / ".agents/mcp.json").write_bytes(b"existing connector")
            (root / ".agents/memory/core.sqlite").write_bytes(b"synthetic runtime state")
            (root / "mcp.json").write_bytes(b"runtime")
            (root / ".git").mkdir()
            (root / ".git/config").write_bytes(b"git metadata")
            luma.apply_plan(root, luma.build_plan(root, payload()))
            installed = self.snapshot(root)
            self.assertEqual(installed["notes.txt"], b"human data")
            self.assertEqual(installed["mcp.json"], b"runtime")
            self.assertEqual(installed[".git/config"], b"git metadata")
            self.assertEqual(installed[".agents/mcp.json"], b"existing connector")
            self.assertEqual(installed[".agents/memory/core.sqlite"], b"synthetic runtime state")
            self.assertEqual(installed[".agents/AGENTS.md"], payload()[".agents/AGENTS.md"])
            self.assertEqual(installed[".agents/LICENSE"], payload()["LICENSE"])
            self.assertFalse(any(p.startswith(("wiki/", "inbox/", "memory/")) for p in installed))
            self.assertFalse(luma.build_plan(root, payload()))
            self.assertEqual(self.snapshot(root), installed)

    def test_readme_gitignore_append_preserves_content_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_bytes(b"Human README\n")
            (root / ".gitignore").write_bytes(b"*.local\n")
            luma.apply_plan(root, luma.build_plan(root, payload()))
            readme, ignore = (root / "README.md").read_bytes(), (root / ".gitignore").read_bytes()
            self.assertTrue(readme.startswith(b"Human README\n"))
            self.assertTrue(ignore.startswith(b"*.local\n"))
            luma.apply_plan(root, luma.build_plan(root, payload()))
            self.assertEqual((root / "README.md").read_bytes(), readme)
            self.assertEqual((root / ".gitignore").read_bytes(), ignore)

    def test_conflict_preflight_leaves_existing_content_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents/skills/example").mkdir(parents=True)
            (root / ".agents/skills/example/SKILL.md").write_bytes(b"different")
            before = self.snapshot(root)
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, payload())
            self.assertEqual(self.snapshot(root), before)
            self.assertFalse((root / ".agents/AGENTS.md").exists())

    def test_modified_and_malformed_owned_blocks_conflict(self):
        for filename, begin, end in (
            ("README.md", "<!-- luma:begin -->", "<!-- luma:end -->"),
            (".gitignore", "# luma:begin", "# luma:end"),
        ):
            for content in (begin + "\nuser edit\n", begin + "\nuser edit\n" + end):
                with self.subTest(filename=filename, content=content), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    path = root / filename
                    original = content.encode()
                    path.write_bytes(original)
                    with self.assertRaises(luma.LumaError):
                        luma.build_plan(root, payload())
                    self.assertEqual(path.read_bytes(), original)

    def test_symlink_targets_and_unsafe_archive_paths_fail(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / ".agents").mkdir()
            (root / ".agents/skills").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, payload())
            (root / ".agents/skills").unlink()
            (root / "README.md").symlink_to(Path(outside) / "README.md")
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, payload())
        with self.assertRaises(luma.LumaError):
            luma.parse_archive(archive({"../escape": b"x", **payload()}))

    def test_source_ancestor_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(luma.LumaError):
                luma.load_local_source(root)

    def test_dry_run_and_network_failure_do_not_write_target_or_parents(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as source_temp:
            base, source = Path(temp), Path(source_temp)
            target = base / "new" / "project"
            source_tree(source)
            self.assertEqual(luma.main(["init", str(target), "--source", str(source), "--dry-run"]), 0)
            self.assertFalse((base / "new").exists())
            with mock.patch.object(luma, "load_remote_source", side_effect=luma.LumaError("offline")):
                self.assertNotEqual(luma.main(["init", str(target)]), 0)
            self.assertFalse((base / "new").exists())

    def test_remote_archive_loads_through_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "project"
            with mock.patch.object(luma, "urlopen", return_value=io.BytesIO(archive(payload()))) as loader:
                self.assertEqual(luma.main(["init", str(target)]), 0)
            self.assertEqual(loader.call_args.args[0], "https://codeload.github.com/lukeanthony007/luma/tar.gz/main")
            self.assertEqual((target / ".agents/AGENTS.md").read_bytes(), payload()[".agents/AGENTS.md"])

    def test_parent_file_and_non_directory_target_fail_without_changes(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as source_temp:
            root, source = Path(temp), Path(source_temp)
            source_tree(source)
            blocked = root / "blocked"
            blocked.write_text("human")
            with self.assertRaises(luma.LumaError):
                luma.build_plan(blocked / "child", payload())
            self.assertEqual(blocked.read_text(), "human")
            result = luma.main(["init", str(blocked), "--source", str(source)])
            self.assertNotEqual(result, 0)
            self.assertEqual(blocked.read_text(), "human")

    def test_apply_failure_rolls_back_installer_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            changes = luma.build_plan(root, payload())
            real_link = os.link
            calls = 0

            def fail_after_one_link(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated link failure")
                return real_link(*args, **kwargs)

            with mock.patch.object(os, "link", side_effect=fail_after_one_link):
                with self.assertRaises((luma.LumaError, OSError)):
                    luma.apply_plan(root, changes)
            self.assertEqual(self.snapshot(root), {})

    def test_failure_restores_existing_files_and_modes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            readme = root / "README.md"
            ignore = root / ".gitignore"
            readme.write_bytes(b"Human project\n")
            ignore.write_bytes(b"*.local\n")
            ignore.chmod(0o640)
            before = self.snapshot(root)
            changes = luma.build_plan(root, payload())
            real_replace = os.replace
            failed = False

            def fail_readme_once(src, dest):
                nonlocal failed
                if Path(dest) == readme and not failed:
                    failed = True
                    raise OSError("simulated final update failure")
                return real_replace(src, dest)

            with mock.patch.object(os, "replace", side_effect=fail_readme_once):
                with self.assertRaises(luma.LumaError):
                    luma.apply_plan(root, changes)
            self.assertTrue(failed)
            self.assertEqual(self.snapshot(root), before)
            self.assertEqual(ignore.stat().st_mode & 0o777, 0o640)

    def test_partial_temporary_write_failure_leaves_no_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "new" / "project"
            changes = luma.build_plan(root, payload())
            with mock.patch.object(os, "fsync", side_effect=OSError("simulated disk failure")):
                with self.assertRaises(luma.LumaError):
                    luma.apply_plan(root, changes)
            self.assertFalse((root.parent).exists())

    def test_archive_rejects_duplicate_paths_links_and_excessive_expansion(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as tar:
            for unused in range(2):
                info = tarfile.TarInfo("luma-main/.agents/AGENTS.md")
                info.size = 1
                tar.addfile(info, io.BytesIO(b"x"))
        with self.assertRaises(luma.LumaError):
            luma.parse_archive(stream.getvalue())
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as tar:
            info = tarfile.TarInfo("luma-main/.agents/AGENTS.md")
            info.type = tarfile.SYMTYPE
            info.linkname = "/outside"
            tar.addfile(info)
        with self.assertRaises(luma.LumaError):
            luma.parse_archive(stream.getvalue())
        with mock.patch.object(luma, "MAX_UNPACKED", 4096):
            with self.assertRaises(luma.LumaError):
                luma.parse_archive(archive({**payload(), "large.txt": b"x" * 8192}))

    def test_install_record_and_read_only_status_preserve_local_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = {**payload(), ".agents/skills/example/NOTICE": b"notice"}
            luma.apply_plan(root, luma.build_plan(root, files, {"kind": "local"}))
            record_path = root / luma.INSTALL_RECORD
            record = json.loads(record_path.read_bytes())
            self.assertEqual(record["source"], {"kind": "local"})
            self.assertNotIn("README.md", record["resources"])
            self.assertNotIn(".gitignore", record["resources"])
            self.assertIn(".agents/LICENSE", record["resources"])
            self.assertIn(".agents/skills/example/NOTICE", record["resources"])
            before, timestamp = self.snapshot(root), record_path.stat().st_mtime_ns
            self.assertFalse(luma.build_plan(root, files, {"kind": "local"}))
            with mock.patch.object(luma, "urlopen") as network:
                with mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                    self.assertEqual(luma.main(["status", str(root)]), 0)
                network.assert_not_called()
            status = json.loads(output.getvalue())
            self.assertTrue(all(item["state"] == "unchanged" for item in status["resources"].values()))
            self.assertEqual(self.snapshot(root), before)
            self.assertEqual(record_path.stat().st_mtime_ns, timestamp)
            (root / ".agents/AGENTS.md").write_bytes(b"local adaptation")
            (root / ".agents/skills/example/SKILL.md").unlink()
            adapted = self.snapshot(root)
            status = luma.install_status(root)
            self.assertEqual(status["resources"][".agents/AGENTS.md"]["state"], "modified")
            self.assertEqual(status["resources"][".agents/skills/example/SKILL.md"]["state"], "missing")
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, files, {"kind": "local"})
            self.assertEqual(self.snapshot(root), adapted)

    def test_legacy_install_can_gain_only_a_matching_baseline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            luma.apply_plan(root, luma.build_plan(root, payload()))
            (root / luma.INSTALL_RECORD).unlink()
            before = self.snapshot(root)
            self.assertEqual(luma.install_status(root)["baseline"], "absent")
            plan = luma.build_plan(root, payload())
            self.assertEqual([change.path for change in plan], [luma.INSTALL_RECORD])
            luma.apply_plan(root, plan)
            for name, content in before.items():
                self.assertEqual((root / name).read_bytes(), content)
            installed = self.snapshot(root)
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, payload(), {"kind": "github-ref", "ref": "different"})
            self.assertEqual(self.snapshot(root), installed)
            (root / luma.INSTALL_RECORD).unlink()
            (root / ".agents/AGENTS.md").write_bytes(b"local change without baseline")
            with self.assertRaises(luma.LumaError):
                luma.build_plan(root, payload())
            self.assertFalse((root / luma.INSTALL_RECORD).exists())

    def test_source_declarations_dry_run_and_absent_status_do_not_leak_or_write(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as source_temp:
            root, source = Path(temp) / "new", Path(source_temp)
            source_tree(source)
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(luma.main(["status", str(root)]), 0)
                self.assertEqual(luma.main(["init", str(root), "--source", str(source), "--dry-run"]), 0)
            self.assertFalse(root.exists())
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(luma.main(["init", str(root), "--source", str(source)]), 0)
            raw = (root / luma.INSTALL_RECORD).read_text()
            self.assertNotIn(str(source), raw)
            self.assertEqual(json.loads(raw)["source"], {"kind": "local"})
            with tempfile.TemporaryDirectory() as remote_temp:
                remote = Path(remote_temp)
                with mock.patch.object(luma, "urlopen", return_value=io.BytesIO(archive(payload()))):
                    with mock.patch("sys.stdout", new_callable=io.StringIO):
                        self.assertEqual(luma.main(["init", str(remote), "--ref", "topic"]), 0)
                self.assertEqual(luma.install_status(remote)["source"], {"kind": "github-ref", "ref": "topic"})

    def test_status_rejects_malformed_or_unsafe_records_before_resource_reads(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            luma.apply_plan(root, luma.build_plan(root, payload()))
            original = json.loads((root / luma.INSTALL_RECORD).read_bytes())
            bad_records = [[], None, {}, {**original, "format_version": True},
                           {**original, "source": {"kind": "github-ref"}},
                           {**original, "resources": {}}]
            for path in ("../../outside", ".agents/skills/../../outside.md",
                         ".agents/tools/unrelated.py", ".agents/skills/a\\b.md",
                         ".agents/skills/a:stream.md", ".agents/skills/a\0.md"):
                bad_records.append({**original, "resources": {**original["resources"], path: "0" * 64}})
            bad_records.append({**original, "resources": {**original["resources"], ".agents/AGENTS.md": 7}})
            for record in bad_records:
                with self.subTest(record=record):
                    (root / luma.INSTALL_RECORD).write_text(json.dumps(record))
                    before = self.snapshot(root)
                    with mock.patch.object(luma, "_read_target_file", wraps=luma._read_target_file) as reads:
                        with self.assertRaises(luma.LumaError):
                            luma.install_status(root)
                        self.assertEqual([call.args[1] for call in reads.call_args_list], [luma.INSTALL_RECORD])
                    self.assertEqual(self.snapshot(root), before)
            for raw in (b"not JSON", b"\xff", b'{"format_version":1,"format_version":1}'):
                (root / luma.INSTALL_RECORD).write_bytes(raw)
                with mock.patch("sys.stderr", new_callable=io.StringIO):
                    self.assertEqual(luma.main(["status", str(root)]), 1)

    def test_status_refuses_symlink_records_resources_and_root(self):
        for relative in (luma.INSTALL_RECORD, ".agents/AGENTS.md", ".agents/skills/example"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
                root, external = Path(temp), Path(outside)
                luma.apply_plan(root, luma.build_plan(root, payload()))
                selected = root / relative
                if selected.is_dir():
                    (selected / "SKILL.md").unlink()
                    selected.rmdir()
                    selected.symlink_to(external, target_is_directory=True)
                else:
                    selected.unlink()
                    (external / "data").write_bytes(b"must not follow")
                    selected.symlink_to(external / "data")
                with self.assertRaises(luma.LumaError):
                    luma.install_status(root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            alias = root / "alias"
            alias.symlink_to(root, target_is_directory=True)
            with self.assertRaises(luma.LumaError):
                luma.install_status(alias)


if __name__ == "__main__":
    unittest.main()

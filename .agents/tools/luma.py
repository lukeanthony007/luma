#!/usr/bin/env python3
"""Install Luma's agent instructions and skills into a workspace."""
from __future__ import annotations

import argparse
import gzip
import io
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import urlopen

MAX_ARCHIVE = 32 * 1024 * 1024
MAX_UNPACKED = 32 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 500
TIMEOUT = 20
RESOURCE_FILES = (".agents/AGENTS.md", ".agents/tools/luma.py",
                  ".agents/tools/luma_knowledge.py", "LICENSE")
README_BEGIN = "<!-- luma:begin -->"
README_END = "<!-- luma:end -->"
IGNORE_BEGIN = "# luma:begin"
IGNORE_END = "# luma:end"
README_BLOCK = "\n".join((
    README_BEGIN,
    "## Agent guidance",
    "",
    "Start your agent with [`.agents/AGENTS.md`](.agents/AGENTS.md). "
    "Keep relevant material in this directory and use the agent to develop "
    "connected understanding in `wiki/`. `inbox/` is an optional temporary "
    "queue for messages and structured worksheets. The agent creates these "
    "directories and MCP configuration when needed.",
    README_END,
))
IGNORE_BLOCK = "\n".join((
    IGNORE_BEGIN,
    "# Luma knowledge, evidence and local state",
    "/wiki/", "/inbox/", "/.agents/memory/", "/.agents/runtime/",
    "/.agents/cache/", "/.agents/mcp.json", "/.agents/credentials/",
    "/.credentials/", "/.env", "/.env.*", "!/.env.example",
    IGNORE_END,
))


class LumaError(Exception):
    """An actionable initializer error."""


@dataclass
class Change:
    path: str
    before: bytes | None
    after: bytes


def _validate(payload: dict[str, bytes]) -> dict[str, bytes]:
    required = set(RESOURCE_FILES)
    if not required.issubset(payload):
        raise LumaError("Source is missing required resources: " + ", ".join(sorted(required - payload.keys())))
    for name, data in payload.items():
        p = PurePosixPath(name)
        if p.is_absolute() or "\\" in name or ":" in name or "\0" in name or ".." in p.parts or not p.parts or str(p) != name:
            raise LumaError(f"Unsafe source path: {name!r}")
        allowed = name in required or (name.startswith(".agents/skills/") and (p.suffix == ".md" or p.name in ("LICENSE", "NOTICE")))
        if not allowed:
            raise LumaError(f"Unexpected source file: {name}")
        if not isinstance(data, bytes):
            raise LumaError(f"Source file is not bytes: {name}")
    if not any(p.startswith(".agents/skills/") and p.endswith("/SKILL.md") for p in payload):
        raise LumaError("Source contains no .agents/skills/**/SKILL.md")
    if len(payload) > MAX_FILES or any(len(v) > MAX_FILE for v in payload.values()) or sum(map(len, payload.values())) > MAX_UNPACKED:
        raise LumaError("Source exceeds file count or per-file size limits")
    return payload


def _safe_name(name: str) -> str:
    if "\\" in name or ":" in name or "\0" in name or name.startswith("/") or ".." in name.split("/"):
        raise LumaError(f"Unsafe archive path: {name!r}")
    parts = PurePosixPath(name.rstrip("/")).parts
    if not parts:
        raise LumaError(f"Unsafe archive path: {name!r}")
    return "/".join(parts)


def _check_source_ancestors(root: Path, rel: str) -> None:
    current = root
    parts = PurePosixPath(rel).parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise LumaError(f"Symlink in selected source path: {current}")
        if index < len(parts) - 1 and current.exists() and not current.is_dir():
            raise LumaError(f"Non-directory in selected source path: {current}")


def load_local_source(root: Path) -> dict[str, bytes]:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise LumaError(f"Local source is not a real directory: {root}")
    files: dict[str, bytes] = {}
    total = 0

    def read_file(path: Path, rel: str) -> None:
        nonlocal total
        _check_source_ancestors(root, rel)
        if path.is_symlink() or not path.is_file():
            raise LumaError(f"Selected source path is not a regular file: {rel}")
        size = path.stat().st_size
        if size > MAX_FILE or total + size > MAX_UNPACKED:
            raise LumaError(f"Source exceeds size limit: {rel}")
        with path.open("rb") as source:
            data = source.read(MAX_FILE + 1)
        total += len(data)
        if len(data) > MAX_FILE or total > MAX_UNPACKED:
            raise LumaError(f"Source exceeds size limit: {rel}")
        files[rel] = data

    for rel in RESOURCE_FILES:
        read_file(root / rel, rel)
    skills = root / ".agents/skills"
    _check_source_ancestors(root, ".agents/skills")
    if not skills.is_dir():
        raise LumaError("Local source has no .agents/skills directory")
    def walk_error(error: OSError) -> None:
        raise LumaError(f"Cannot read selected source directory: {error}") from error

    for base, dirs, names in os.walk(skills, followlinks=False, onerror=walk_error):
        bp = Path(base)
        dirs.sort()
        names.sort()
        for name in dirs:
            if (bp / name).is_symlink():
                raise LumaError(f"Symlink in selected skills tree: {bp / name}")
        for name in names:
            path = bp / name
            if path.is_symlink():
                raise LumaError(f"Symlink in selected skills tree: {path}")
            if path.is_file() and (name.endswith(".md") or name in ("LICENSE", "NOTICE")):
                rel = path.relative_to(root).as_posix()
                read_file(path, rel)
                if len(files) > MAX_FILES:
                    raise LumaError("Source exceeds file count limit")
    return _validate(files)


def parse_archive(data: bytes) -> dict[str, bytes]:
    if len(data) > MAX_ARCHIVE:
        raise LumaError("Source archive exceeds size limit")
    files: dict[str, bytes] = {}
    root_name = None
    total = 0
    count = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as compressed:
            unpacked = compressed.read(MAX_UNPACKED + 1)
        if len(unpacked) > MAX_UNPACKED:
            raise LumaError("Source archive exceeds unpacked size limit")
        with tarfile.open(fileobj=io.BytesIO(unpacked), mode="r|") as archive:
            for member in archive:
                count += 1
                if count > MAX_FILES * 8:
                    raise LumaError("Source archive contains too many entries")
                name = _safe_name(member.name)
                top = name.split("/", 1)[0]
                if root_name is None:
                    root_name = top
                elif top != root_name:
                    raise LumaError("Malformed archive with multiple root directories")
                if member.issym() or member.islnk() or not (member.isdir() or member.isfile()):
                    raise LumaError(f"Unsupported archive entry: {member.name}")
                relative = name[len(root_name):].lstrip("/")
                if not relative or not member.isfile():
                    continue
                if member.size > MAX_FILE:
                    raise LumaError(f"Source file too large: {relative}")
                total += member.size
                if total > MAX_UNPACKED:
                    raise LumaError("Source archive exceeds unpacked size limit")
                selected = relative in RESOURCE_FILES or (relative.startswith(".agents/skills/") and (PurePosixPath(relative).suffix == ".md" or PurePosixPath(relative).name in ("LICENSE", "NOTICE")))
                if not selected:
                    continue
                if relative in files:
                    raise LumaError(f"Duplicate archive path: {relative}")
                stream = archive.extractfile(member)
                if stream is None:
                    raise LumaError(f"Unable to read archive entry: {relative}")
                files[relative] = stream.read(MAX_FILE + 1)
                if len(files[relative]) > MAX_FILE:
                    raise LumaError(f"Source file too large: {relative}")
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise LumaError(f"Invalid source archive: {exc}") from exc
    return _validate(files)


def load_remote_source(ref: str) -> dict[str, bytes]:
    if not ref or len(ref) > 200 or ref.startswith("-"):
        raise LumaError("Invalid GitHub ref")
    url = "https://codeload.github.com/lukeanthony007/luma/tar.gz/" + quote(ref, safe="")
    try:
        with urlopen(url, timeout=TIMEOUT) as response:
            chunks = []
            size = 0
            while True:
                chunk = response.read(min(65536, MAX_ARCHIVE + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_ARCHIVE:
                    raise LumaError("Source archive exceeds download size limit")
    except LumaError:
        raise
    except Exception as exc:
        raise LumaError(f"Could not download Luma source: {exc}") from exc
    return parse_archive(b"".join(chunks))


def _managed_text(existing: bytes | None, block: str, path: str, begin: str, end: str) -> bytes:
    if existing is None:
        return (block + "\n").encode()
    try:
        text = existing.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LumaError(f"Cannot safely update non-UTF-8 {path}") from exc
    starts, ends = text.count(begin), text.count(end)
    if starts or ends:
        if starts != 1 or ends != 1 or text.index(begin) > text.index(end):
            raise LumaError(f"Conflicting or malformed Luma block in {path}")
        current = text[text.index(begin):text.index(end) + len(end)]
        if current != block:
            raise LumaError(f"Modified Luma block in {path}")
        return existing
    sep = "" if not text or text.endswith("\n") else "\n"
    return (text + sep + "\n" + block + "\n").encode()


def _read_target_file(root: Path, rel: str) -> bytes | None:
    path = root / rel
    current = root
    parts = PurePosixPath(rel).parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise LumaError(f"Refusing symlink in target path: {current}")
        if index < len(parts) - 1 and current.exists() and not current.is_dir():
            raise LumaError(f"Target parent is not a directory: {current}")
    if not path.exists():
        return None
    if not path.is_file():
        raise LumaError(f"Target path is not a regular file: {path}")
    return path.read_bytes()


def build_plan(target: Path, payload: dict[str, bytes]) -> list[Change]:
    target = Path(target)
    _validate(payload)
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise LumaError(f"Target is not a real directory: {target}")
    ancestor = target.absolute()
    while not ancestor.exists() and not ancestor.is_symlink():
        ancestor = ancestor.parent
    if not ancestor.is_dir():
        raise LumaError(f"Target parent is not a directory: {ancestor}")
    root = target.resolve(strict=False)
    files = {(".agents/LICENSE" if name == "LICENSE" else name): data for name, data in payload.items()}
    readmes = [name for name in ("README.md", "README", "readme.md", "Readme.md") if _read_target_file(root, name) is not None]
    if len(readmes) > 1:
        raise LumaError("Multiple root README files exist; choose one before initializing")
    readme = readmes[0] if readmes else "README.md"
    if readmes:
        files[readme] = _managed_text(_read_target_file(root, readme), README_BLOCK, readme, README_BEGIN, README_END)
    else:
        files[readme] = ("# Luma workspace\n\n" + README_BLOCK + "\n").encode()
    files[".gitignore"] = _managed_text(_read_target_file(root, ".gitignore"), IGNORE_BLOCK, ".gitignore", IGNORE_BEGIN, IGNORE_END)
    changes = []
    conflicts = []
    for rel, after in sorted(files.items()):
        before = _read_target_file(root, rel)
        if before == after:
            continue
        if before is not None and rel not in (readme, ".gitignore"):
            conflicts.append(rel)
        else:
            changes.append(Change(rel, before, after))
    if conflicts:
        raise LumaError("Conflicting managed files (no files changed): " + ", ".join(conflicts) + ". Review/merge with your agent; do not blindly delete files.")
    return changes


def apply_plan(target: Path, changes: list[Change]) -> None:
    target = Path(target)
    made_dirs: list[Path] = []
    completed: list[Change] = []
    temps: list[Path] = []
    try:
        missing = []
        parent = target
        while not parent.exists() and not parent.is_symlink():
            missing.append(parent)
            parent = parent.parent
        for directory in reversed(missing):
            directory.mkdir()
            made_dirs.append(directory)
        if target.is_symlink() or not target.is_dir():
            raise LumaError(f"Target is not a real directory: {target}")
        for change in changes:
            dest = target / change.path
            dest_parent = target
            for part in PurePosixPath(change.path).parts[:-1]:
                dest_parent = dest_parent / part
                if dest_parent.is_symlink():
                    raise LumaError(f"Refusing symlink in target path: {dest_parent}")
                if not dest_parent.exists():
                    dest_parent.mkdir()
                    made_dirs.append(dest_parent)
                elif not dest_parent.is_dir():
                    raise LumaError(f"Target parent is not a directory: {dest_parent}")
            dest = target / change.path
            if _read_target_file(target, change.path) != change.before:
                raise LumaError(f"Target changed since preflight: {change.path}")
            fd, temporary = tempfile.mkstemp(prefix=".luma-", dir=str(dest.parent))
            temp = Path(temporary)
            temps.append(temp)
            with os.fdopen(fd, "wb") as output:
                output.write(change.after)
                output.flush()
                os.fsync(output.fileno())
            if change.before is None:
                os.link(temp, dest)
                completed.append(change)
                temp.unlink()
                temps.remove(temp)
            else:
                os.chmod(temp, dest.stat().st_mode & 0o777)
                if dest.read_bytes() != change.before:
                    raise LumaError(f"Target changed during update: {change.path}")
                os.replace(temp, dest)
                completed.append(change)
                temps.remove(temp)
    except Exception as exc:
        incomplete = []
        for change in reversed(completed):
            path = target / change.path
            try:
                if path.read_bytes() != change.after:
                    incomplete.append(change.path)
                    continue
                if change.before is None:
                    path.unlink()
                else:
                    fd, rollback = tempfile.mkstemp(prefix=".luma-rollback-", dir=str(path.parent))
                    with os.fdopen(fd, "wb") as output:
                        output.write(change.before)
                    os.chmod(rollback, path.stat().st_mode & 0o777)
                    os.replace(rollback, path)
            except OSError:
                incomplete.append(change.path)
        for temp in temps:
            try:
                temp.unlink()
            except OSError:
                incomplete.append(str(temp))
        for directory in reversed(made_dirs):
            try:
                directory.rmdir()
            except OSError:
                incomplete.append(str(directory))
        suffix = "; rollback incomplete for: " + ", ".join(incomplete) if incomplete else "; rollback completed"
        if isinstance(exc, LumaError):
            raise LumaError(str(exc) + suffix) from exc
        raise LumaError(f"Installation failed: {exc}{suffix}") from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install Luma agent guidance and skills in a workspace")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="initialize the current or named workspace")
    init.add_argument("target", nargs="?", default=".")
    init.add_argument("--dry-run", action="store_true")
    source = init.add_mutually_exclusive_group()
    source.add_argument("--source", type=Path)
    source.add_argument("--ref", default="main")
    args = parser.parse_args(argv)
    try:
        payload = load_local_source(args.source) if args.source else load_remote_source(args.ref)
        changes = build_plan(Path(args.target), payload)
        if args.dry_run:
            print("Would create/update: " + (", ".join(c.path for c in changes) if changes else "nothing (already current)"))
            return 0
        apply_plan(Path(args.target), changes)
        print(f"Installed Luma ({len(changes)} file(s) changed). Start your agent with .agents/AGENTS.md and the luma-setup skill.")
        return 0
    except LumaError as exc:
        print(f"luma: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"luma: Cannot initialize workspace: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Install Luma's agent instructions and skills into a workspace."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
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
INSTALL_RECORD = ".agents/luma-install.json"
README_NAMES = ("README.md", "README", "readme.md", "Readme.md")
README_BEGIN = "<!-- luma:begin -->"
README_END = "<!-- luma:end -->"
IGNORE_BEGIN = "# luma:begin"
IGNORE_END = "# luma:end"
README_BLOCK = "\n".join((
    README_BEGIN,
    "## Agent guidance",
    "",
    "Read [`.agents/AGENTS.md`](.agents/AGENTS.md), then work directly on "
    "your request using available skills and tools. Preserve useful knowledge "
    "and continuity in established project records. A wiki and inbox are "
    "optional; create them only when needed.",
    README_END,
))
IGNORE_BLOCK = "\n".join((
    IGNORE_BEGIN,
    "# Luma knowledge, evidence and local state",
    "/wiki/", "/inbox/", "/.agents/memory/", "/.agents/sources/", "/.agents/runtime/",
    "/.agents/briefs/", "/.agents/runs/", "/.agents/cache/", "/.agents/mcp.json", "/.agents/credentials/",
    "/.credentials/", "/.env", "/.env.*", "!/.env.example",
    IGNORE_END,
))
# The ignore block shipped with format 1 install records (Luma main 3794cd7). `upgrade` replaces it
# only when upgrading a format 1 record; format 2 records carry the installed block's hash instead.
PREVIOUS_IGNORE_BLOCK = "\n".join((
    IGNORE_BEGIN,
    "# Luma knowledge, evidence and local state",
    "/wiki/", "/inbox/", "/.agents/memory/", "/.agents/sources/", "/.agents/runtime/",
    "/.agents/runs/", "/.agents/cache/", "/.agents/mcp.json", "/.agents/credentials/",
    "/.credentials/", "/.env", "/.env.*", "!/.env.example",
    IGNORE_END,
))


class LumaError(Exception):
    """An actionable initializer error."""


@dataclass
class Change:
    path: str
    before: bytes | None
    after: bytes | None  # None removes the file


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


def load_source_path(path: Path) -> dict[str, bytes]:
    """Load a local Luma checkout directory or a downloaded .tar.gz source archive."""
    path = Path(path)
    if not path.is_symlink() and path.is_file():
        with path.open("rb") as archive:
            return parse_archive(archive.read(MAX_ARCHIVE + 1))
    return load_local_source(path)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _decode(existing: bytes, path: str) -> str:
    try:
        return existing.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LumaError(f"Cannot safely update non-UTF-8 {path}") from exc


def _block_span(text: str, path: str, begin: str, end: str) -> tuple[int, int] | None:
    starts, ends = text.count(begin), text.count(end)
    if not starts and not ends:
        return None
    if starts != 1 or ends != 1 or text.index(begin) > text.index(end):
        raise LumaError(f"Conflicting or malformed Luma block in {path}")
    return text.index(begin), text.index(end) + len(end)


def _append_block(text: str, block: str) -> bytes:
    sep = "" if not text or text.endswith("\n") else "\n"
    return (text + sep + "\n" + block + "\n").encode()


def _new_readme() -> bytes:
    return ("# Luma workspace\n\n" + README_BLOCK + "\n").encode()


def _managed_text(existing: bytes | None, block: str, path: str, begin: str, end: str) -> bytes:
    if existing is None:
        return (block + "\n").encode()
    text = _decode(existing, path)
    span = _block_span(text, path, begin, end)
    if span is None:
        return _append_block(text, block)
    if text[span[0]:span[1]] != block:
        raise LumaError(f"Modified Luma block in {path}")
    return existing


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


def _resource_path(name: str) -> bool:
    if not isinstance(name, str):
        return False
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or str(path) != name or ".." in path.parts
            or any(char in name for char in ("\\", ":", "\0"))):
        return False
    return name in (".agents/AGENTS.md", ".agents/LICENSE", ".agents/tools/luma.py",
                    ".agents/tools/luma_knowledge.py") or (
        name.startswith(".agents/skills/") and
        (path.suffix == ".md" or path.name in ("LICENSE", "NOTICE")))


def _validate_install_record(record: object) -> dict:
    version = record.get("format_version") if isinstance(record, dict) else None
    keys = {"format_version", "source", "resources"} | ({"blocks", "readme"} if version == 2 else set())
    if type(version) is not int or version not in (1, 2) or set(record) != keys:
        raise LumaError("Invalid install record: unsupported format")
    source, resources = record["source"], record["resources"]
    if not isinstance(source, dict) or source.get("kind") not in ("local", "github-ref", "unknown"):
        raise LumaError("Invalid install record: source declaration")
    if source["kind"] == "github-ref":
        ref = source.get("ref")
        if set(source) != {"kind", "ref"} or not isinstance(ref, str) or not ref or len(ref) > 200 or ref.startswith("-"):
            raise LumaError("Invalid install record: declared GitHub ref")
    elif set(source) != {"kind"}:
        raise LumaError("Invalid install record: unexpected source fields")
    if not isinstance(resources, dict) or not resources or len(resources) > MAX_FILES:
        raise LumaError("Invalid install record: resources")
    for name, digest in resources.items():
        if not _resource_path(name) or not _is_digest(digest):
            raise LumaError("Invalid install record: unsafe resource path or SHA-256")
    required = {".agents/AGENTS.md", ".agents/LICENSE", ".agents/tools/luma.py",
                ".agents/tools/luma_knowledge.py"}
    if not required.issubset(resources) or not any(name.endswith("/SKILL.md") for name in resources):
        raise LumaError("Invalid install record: incomplete resource inventory")
    if version == 2:
        readme, blocks = record["readme"], record["blocks"]
        if (not isinstance(readme, str) or readme not in README_NAMES or not isinstance(blocks, dict)
                or set(blocks) != {".gitignore", readme} or not all(map(_is_digest, blocks.values()))):
            raise LumaError("Invalid install record: managed blocks")
    return record


def _record_bytes(files: dict[str, bytes], source: dict | None, readme: str) -> bytes:
    record = {"format_version": 2, "source": source if source is not None else {"kind": "unknown"},
              "resources": {name: _digest(data) for name, data in files.items()},
              "blocks": {".gitignore": _digest(IGNORE_BLOCK.encode()), readme: _digest(README_BLOCK.encode())},
              "readme": readme}
    _validate_install_record(record)
    return (json.dumps(record, sort_keys=True, indent=2) + "\n").encode()


def _unique_json_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate key: {key}")
        result[key] = value
    return result


def _load_install_record(root: Path) -> dict | None:
    raw = _read_target_file(root, INSTALL_RECORD)
    if raw is None:
        return None
    if len(raw) > MAX_FILE:
        raise LumaError("Invalid install record: exceeds size limit")
    try:
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise LumaError(f"Invalid install record: {exc}") from exc
    return _validate_install_record(record)


def _block_status(root: Path, path: str, begin: str, end: str, recorded: str | None) -> dict:
    data = _read_target_file(root, path)
    actual, malformed = None, False
    if data is not None:
        try:
            text = data.decode("utf-8")
            span = _block_span(text, path, begin, end)
        except (UnicodeDecodeError, LumaError):
            malformed = True
        else:
            if span is not None:
                actual = _digest(text[span[0]:span[1]].encode())
    if recorded is None:
        state = "unrecorded"
    elif actual == recorded:
        state = "unchanged"
    else:
        state = "modified" if malformed or actual is not None else "missing"
    return {"state": state, "recorded_sha256": recorded, "actual_sha256": actual}


def install_status(target: Path) -> dict:
    target = Path(target)
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise LumaError(f"Target is not a real directory: {target}")
    root = target.resolve(strict=False)
    limits = [
        "The record is mutable and unauthenticated; it grants no authority.",
        "Hashes identify recorded bytes, not recoverable prior source text.",
        "Installed resources do not establish effective host loading or benefit.",
        "Unrecorded user resources and README/ignore content outside the Luma blocks are not inspected.",
    ]
    record = _load_install_record(root)
    if record is None:
        return {"baseline": "absent", "source": None, "resources": {}, "blocks": {}, "limits": limits}
    resources = {}
    for name, expected in sorted(record["resources"].items()):
        data = _read_target_file(root, name)
        actual = _digest(data) if data is not None else None
        state = "missing" if data is None else "unchanged" if actual == expected else "modified"
        resources[name] = {"state": state, "recorded_sha256": expected, "actual_sha256": actual}
    recorded_blocks = record.get("blocks", {})
    readme = record.get("readme") or next(
        (name for name in README_NAMES if _read_target_file(root, name) is not None), "README.md")
    blocks = {".gitignore": _block_status(root, ".gitignore", IGNORE_BEGIN, IGNORE_END, recorded_blocks.get(".gitignore")),
              readme: _block_status(root, readme, README_BEGIN, README_END, recorded_blocks.get(readme))}
    return {"baseline": "recorded", "format_version": record["format_version"], "source": record["source"],
            "resources": resources, "blocks": blocks, "limits": limits}


def _target_root(target: Path) -> Path:
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise LumaError(f"Target is not a real directory: {target}")
    ancestor = target.absolute()
    while not ancestor.exists() and not ancestor.is_symlink():
        ancestor = ancestor.parent
    if not ancestor.is_dir():
        raise LumaError(f"Target parent is not a directory: {ancestor}")
    return target.resolve(strict=False)


def _installed_files(payload: dict[str, bytes]) -> dict[str, bytes]:
    return {(".agents/LICENSE" if name == "LICENSE" else name): data for name, data in payload.items()}


def _readme_name(root: Path) -> str | None:
    readmes = [name for name in README_NAMES if _read_target_file(root, name) is not None]
    if len(readmes) > 1:
        raise LumaError("Multiple root README files exist; keep one and rerun")
    return readmes[0] if readmes else None


def build_plan(target: Path, payload: dict[str, bytes], source: dict | None = None) -> list[Change]:
    target = Path(target)
    _validate(payload)
    root = _target_root(target)
    files = _installed_files(payload)
    readme = _readme_name(root)
    record = _record_bytes(files, source, readme or "README.md")
    if readme:
        files[readme] = _managed_text(_read_target_file(root, readme), README_BLOCK, readme, README_BEGIN, README_END)
    else:
        readme = "README.md"
        files[readme] = _new_readme()
    files[".gitignore"] = _managed_text(_read_target_file(root, ".gitignore"), IGNORE_BLOCK, ".gitignore", IGNORE_BEGIN, IGNORE_END)
    files[INSTALL_RECORD] = record
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


def build_upgrade_plan(target: Path, payload: dict[str, bytes],
                       source: dict | None = None) -> tuple[list[Change], list[str]]:
    """Plan an upgrade of a recorded installation; return the changes and the orphaned paths.

    Only resources named in the install record or shipped by the new source, and the two managed
    blocks, are read. Any locally modified one refuses the whole upgrade before anything is written.
    """
    target = Path(target)
    _validate(payload)
    root = _target_root(target)
    record = _load_install_record(root)
    if record is None:
        raise LumaError(f"No Luma install record ({INSTALL_RECORD}) in {target}; use init")
    files = _installed_files(payload)
    recorded = record["resources"]
    changes: list[Change] = []
    conflicts: list[str] = []
    orphaned: list[str] = []
    for rel in sorted(set(recorded) | set(files)):
        current = _read_target_file(root, rel)
        untouched = current is not None and _digest(current) == recorded.get(rel)
        new = files.get(rel)
        if new is not None:
            if current == new:
                continue
            if current is None or untouched:
                changes.append(Change(rel, current, new))
            else:
                conflicts.append(rel)
        elif current is None:
            continue
        elif untouched:
            changes.append(Change(rel, current, None))
        else:
            orphaned.append(rel)
    readme = _readme_name(root)
    recorded_blocks = record.get("blocks", {})
    first_format = record["format_version"] == 1
    for path, block, begin, end, recorded_hash, previous in (
        (".gitignore", IGNORE_BLOCK, IGNORE_BEGIN, IGNORE_END, recorded_blocks.get(".gitignore"),
         PREVIOUS_IGNORE_BLOCK if first_format else None),
        (readme or "README.md", README_BLOCK, README_BEGIN, README_END,
         recorded_blocks.get(record.get("readme")), None),
    ):
        existing = _read_target_file(root, path)
        if existing is None:
            changes.append(Change(path, None, (block + "\n").encode() if path == ".gitignore" else _new_readme()))
            continue
        try:
            text = _decode(existing, path)
            span = _block_span(text, path, begin, end)
        except LumaError:
            conflicts.append(f"{path} (malformed Luma block)")
            continue
        if span is None:
            changes.append(Change(path, existing, _append_block(text, block)))
            continue
        installed = text[span[0]:span[1]]
        if installed == block:
            continue
        if _digest(installed.encode()) == recorded_hash or installed == previous:
            changes.append(Change(path, existing, (text[:span[0]] + block + text[span[1]:]).encode()))
        else:
            conflicts.append(f"{path} (Luma block)")
    if conflicts:
        raise LumaError("Upgrade refused (no files changed, install record unchanged); locally modified: "
                        + ", ".join(conflicts) + ". Either restore the recorded bytes (see `status`) or move "
                        "your edit into a differently named file, then rerun upgrade.")
    changes.sort(key=lambda change: change.path)
    new_record = _record_bytes(files, source, readme or "README.md")
    old_record = _read_target_file(root, INSTALL_RECORD)
    if new_record != old_record:
        changes.append(Change(INSTALL_RECORD, old_record, new_record))
    return changes, orphaned


def apply_plan(target: Path, changes: list[Change]) -> None:
    target = Path(target)
    made_dirs: list[Path] = []
    completed: list[Change] = []
    temps: list[Path] = []
    removed_modes: dict[str, int] = {}
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
            if change.after is None:
                if dest.read_bytes() != change.before:
                    raise LumaError(f"Target changed during update: {change.path}")
                removed_modes[change.path] = dest.stat().st_mode & 0o777
                dest.unlink()
                completed.append(change)
                continue
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
                if change.after is None:
                    if path.exists() or path.is_symlink():
                        incomplete.append(change.path)
                        continue
                    fd, rollback = tempfile.mkstemp(prefix=".luma-rollback-", dir=str(path.parent))
                    with os.fdopen(fd, "wb") as output:
                        output.write(change.before)
                    os.chmod(rollback, removed_modes[change.path])
                    os.replace(rollback, path)
                    continue
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
    skills = target / ".agents/skills"
    for rel in removed_modes:
        # Remove skill directories the upgrade emptied; stop at the first one still holding files.
        directory = (target / rel).parent
        while skills in directory.parents:
            try:
                directory.rmdir()
            except OSError:
                break
            directory = directory.parent


def _add_install_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--dry-run", action="store_true")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--source", type=Path, help="local Luma checkout or downloaded .tar.gz archive")
    source.add_argument("--ref", default="main", help="GitHub ref to download (default: main)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install Luma agent guidance and skills in a workspace")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status", help="inspect installed-resource and block drift without changes or network access")
    status.add_argument("target", nargs="?", default=".")
    _add_install_options(sub.add_parser("init", help="initialize the current or named workspace"))
    _add_install_options(sub.add_parser(
        "upgrade", help="upgrade a recorded installation; stops without changes on any locally modified Luma file or block"))
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps(install_status(Path(args.target)), sort_keys=True))
            return 0
        payload = load_source_path(args.source) if args.source else load_remote_source(args.ref)
        source_info = {"kind": "local"} if args.source else {"kind": "github-ref", "ref": args.ref}
        if args.command == "upgrade":
            changes, orphaned = build_upgrade_plan(Path(args.target), payload, source_info)
        else:
            changes, orphaned = build_plan(Path(args.target), payload, source_info), []
        left = ("; left in place (edited locally, no longer shipped by Luma): " + ", ".join(orphaned)) if orphaned else ""
        if args.dry_run:
            planned = ", ".join(c.path + (" (remove)" if c.after is None else "") for c in changes)
            print("Would create/update: " + (planned or "nothing (already current)") + left)
            return 0
        apply_plan(Path(args.target), changes)
        if args.command == "upgrade":
            print(f"Upgraded Luma ({len(changes)} file(s) changed){left}.")
        else:
            print(f"Installed Luma ({len(changes)} file(s) changed). Read .agents/AGENTS.md, then work on your request.")
        return 0
    except LumaError as exc:
        print(f"luma: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"luma: Cannot access workspace: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

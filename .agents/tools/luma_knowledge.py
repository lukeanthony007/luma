#!/usr/bin/env python3
"""Capture explicit source files and mechanically check local knowledge links.

Markdown parsing is conservative and does not implement every extension or nested syntax.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlsplit

MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILES = 1000
MAX_MANIFEST = 4 * 1024 * 1024
LIMITS = ["Mechanical checks do not establish source support, claim truth, semantic coverage or instruction compliance.", "Markdown parsing is conservative and does not implement every extension or nested syntax."]
# A capture batch is named for its captured_at with ":" as "-", plus an optional collision suffix. Only such directories
# are batches: other subdirectories of a batch root belong to other owners (for example Animus's .agents/memory/animus/).
BATCH_NAME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d{6}Z(?:-[A-Za-z0-9-]+)?")
# New captures go under .agents/sources/<date-time>/, outside .agents/memory/, which is private runtime state.
CAPTURE_ROOT = ".agents/sources"
# Every root read for batches: the two legacy roots, .agents/memory/<date-time>/ and .agents/memory/sources/<date-time>/,
# then the capture root. Batches with the same name are read in this order.
BATCH_ROOTS = (".agents/memory", ".agents/memory/sources", CAPTURE_ROOT)

class KnowledgeError(Exception):
    """Actionable local knowledge operation error."""


def _safe_rel(value: str, *, allow_agents_skills: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value or ":" in value:
        raise KnowledgeError(f"Unsafe workspace-relative path: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or str(p) != value or not p.parts:
        raise KnowledgeError(f"Unsafe workspace-relative path: {value!r}")
    forbidden = {".git", "runtime", "credentials", ".credentials"}
    if any(part in forbidden or part == ".env" or part.startswith(".env.") for part in p.parts):
        raise KnowledgeError(f"Protected path is not eligible: {value}")
    if ".agents" in p.parts and not (allow_agents_skills and p.parts[:2] == (".agents", "skills")):
        raise KnowledgeError(f"Protected path is not eligible: {value}")
    return value


def _path(root: Path, rel: str) -> Path:
    current = root
    for part in PurePosixPath(rel).parts:
        current = current / part
        if current.is_symlink():
            raise KnowledgeError(f"Symlink path is not allowed: {rel}")
    try:
        current.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        raise KnowledgeError(f"Path escapes workspace: {rel}") from None
    return current


def _read_file(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise KnowledgeError(f"Not a regular file or size limit exceeded: {path}")
    before = path.stat()
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    after = path.stat()
    if len(raw) > limit or len(raw) != before.st_size or (
        before.st_ino, before.st_size, before.st_mtime_ns
    ) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise KnowledgeError(f"File changed during read or exceeds limit: {path}")
    return raw


def _batch_root(root: Path, rel: str, *, create: bool = False) -> Path | None:
    current = root
    for part in PurePosixPath(rel).parts:
        current = current / part
        if current.is_symlink() or (current.exists() and not current.is_dir()):
            raise KnowledgeError(f"Unsafe {current.relative_to(root).as_posix()} path")
        if not current.exists():
            if not create:
                return None
            current.mkdir(exist_ok=True)
            if current.is_symlink() or not current.is_dir():
                raise KnowledgeError(f"Unsafe {current.relative_to(root).as_posix()} path")
    return current


def _manifest_entries(root: Path) -> list[tuple[str, dict, str]]:
    agents = root / ".agents"
    if agents.is_symlink() or (agents.exists() and not agents.is_dir()):
        raise KnowledgeError("Unsafe .agents path")
    results = []
    roots = [base for base in (_batch_root(root, rel) for rel in BATCH_ROOTS) if base is not None]
    # Names are captured_at stamps, so sorting by name reads batches in capture order across all roots.
    batches = sorted((entry for base in roots for entry in base.iterdir() if BATCH_NAME.fullmatch(entry.name)), key=lambda entry: (entry.name, roots.index(entry.parent)))
    if len(batches) > MAX_FILES:
        raise KnowledgeError("Capture batch count exceeds limit")
    total = 0
    known_payloads = {}
    for batch in batches:
        if batch.is_symlink() or not batch.is_dir():
            continue
        batch_rel = batch.relative_to(root).as_posix()
        mf = batch / "manifest.json"
        if not mf.exists():
            continue
        if mf.is_symlink() or not mf.is_file() or mf.stat().st_size > MAX_MANIFEST:
            raise KnowledgeError(f"Unsafe or oversized manifest: {mf.relative_to(root)}")
        try:
            data = json.loads(_read_file(mf, MAX_MANIFEST).decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise KnowledgeError(f"Malformed manifest {mf.relative_to(root)}: {exc}") from None
        if not isinstance(data, dict) or data.get("format") != "luma-capture-v1":
            continue
        captured = data.get("captured_at")
        try:
            parsed = datetime.fromisoformat(captured.replace("Z", "+00:00"))
            if not isinstance(captured, str) or not captured.endswith("Z") or parsed.utcoffset().total_seconds() != 0 or parsed.isoformat(timespec="microseconds").replace("+00:00", "Z") != captured:
                raise ValueError()
        except (AttributeError, ValueError, TypeError):
            raise KnowledgeError(f"Invalid captured_at in {mf.relative_to(root)}") from None
        base_name = captured.replace(":", "-")
        if batch.name != base_name and not re.fullmatch(re.escape(base_name) + r"-[A-Za-z0-9-]+", batch.name):
            raise KnowledgeError(f"Batch name does not match captured_at: {batch.relative_to(root)}")
        files = data.get("files")
        if not isinstance(files, list) or len(files) > MAX_FILES:
            raise KnowledgeError(f"Invalid files list in {mf.relative_to(root)}")
        seen = set()
        for entry in files:
            if not isinstance(entry, dict):
                raise KnowledgeError(f"Invalid entry in {mf.relative_to(root)}")
            source = _safe_rel(entry.get("source"))
            if source in seen:
                raise KnowledgeError(f"Duplicate capture record for {source}")
            seen.add(source)
            archived = entry.get("archived")
            expected = f"originals/{source}"
            if archived != expected or not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or type(entry.get("size")) is not int or not 0 <= entry["size"] <= MAX_FILE:
                raise KnowledgeError(f"Invalid capture record for {source} in {mf.relative_to(root)}")
            predecessor = entry.get("previous")
            if predecessor is not None:
                if not isinstance(predecessor, str) or known_payloads.get(predecessor) != source:
                    raise KnowledgeError(f"Invalid or unverified predecessor for {source}")
            payload_rel = f"{batch_rel}/{archived}"
            payload = _path(root, payload_rel)
            if not payload.is_file() or payload.stat().st_size != entry["size"]:
                raise KnowledgeError(f"Missing or oversized captured payload: {payload_rel}")
            total += entry["size"]
            if total > MAX_TOTAL:
                raise KnowledgeError("Captured payload total exceeds limit")
            raw = _read_file(payload, MAX_FILE)
            if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
                raise KnowledgeError(f"Capture integrity failure: {payload_rel}")
            results.append((source, dict(entry, captured_at=captured), payload_rel))
            known_payloads[payload_rel] = source
            if len(results) > MAX_FILES:
                raise KnowledgeError("Capture record count exceeds limit")
    return results


def capture(root: Path, paths: list[str]) -> dict:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise KnowledgeError(f"Workspace is not a real directory: {root}")
    if not paths or len(paths) > MAX_FILES:
        raise KnowledgeError(f"Select between 1 and {MAX_FILES} source files")
    if len(set(paths)) != len(paths):
        raise KnowledgeError("Duplicate source paths are not allowed")
    sources = {}
    total = 0
    for name in paths:
        rel = _safe_rel(name)
        path = _path(root, rel)
        if not path.is_file():
            raise KnowledgeError(f"Source is not a regular file: {rel}")
        before = path.stat()
        if before.st_size > MAX_FILE:
            raise KnowledgeError(f"Source exceeds per-file limit: {rel}")
        raw = _read_file(path, MAX_FILE)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or len(raw) != before.st_size:
            raise KnowledgeError(f"Source changed while being read: {rel}")
        total += len(raw)
        if total > MAX_TOTAL:
            raise KnowledgeError(f"Selected sources exceed total limit ({MAX_TOTAL} bytes)")
        sources[rel] = (raw, hashlib.sha256(raw).hexdigest())
    prior = _manifest_entries(root)
    latest = {}
    for src, record, archived in prior:
        latest[src] = (record, archived)
    output = []
    new = []
    for src, (raw, digest) in sources.items():
        old = latest.get(src)
        reused = bool(old and old[0]["sha256"] == digest and old[0]["size"] == len(raw))
        if reused:
            target = old[1]
            stamp = old[0]["captured_at"]
        else:
            target = ""
            stamp = ""
            new.append((src, raw, digest, old[1] if old else None))
        output.append((src, digest, len(raw), reused, target, stamp))
    batch_rel = None
    if new:
        stamp_dt = datetime.now(timezone.utc)
        captured = stamp_dt.isoformat(timespec="microseconds").replace("+00:00", "Z")
        agents = root / ".agents"
        if agents.is_symlink() or (agents.exists() and not agents.is_dir()):
            raise KnowledgeError("Unsafe .agents path")
        destination = _batch_root(root, CAPTURE_ROOT, create=True)
        stage = Path(tempfile.mkdtemp(prefix=".luma-capture-", dir=destination))
        final = None
        reserved_stat = None
        try:
            entries = []
            for src, raw, digest, predecessor in new:
                dest = stage / "originals" / PurePosixPath(src)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                entry = {"source": src, "archived": f"originals/{src}", "sha256": digest, "size": len(raw)}
                if predecessor:
                    entry["previous"] = predecessor
                entries.append(entry)
            (stage / "manifest.json").write_text(json.dumps({"format": "luma-capture-v1", "captured_at": captured, "files": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            for src, (raw, digest) in sources.items():
                if _read_file(_path(root, src), MAX_FILE) != raw:
                    raise KnowledgeError(f"Source changed before publication: {src}")
            base = captured.replace(":", "-")
            for suffix in range(MAX_FILES):
                candidate = destination / (base if not suffix else f"{base}-{suffix}")
                try:
                    candidate.mkdir()
                except FileExistsError:
                    continue
                final = candidate
                reserved_stat = final.stat()
                break
            if final is None:
                raise KnowledgeError("Could not reserve a unique capture batch")
            batch_rel = final.relative_to(root).as_posix()
            # Replace only our own exclusive empty reservation with a complete batch.
            current = final.stat()
            if final.is_symlink() or (current.st_dev, current.st_ino) != (
                reserved_stat.st_dev, reserved_stat.st_ino
            ):
                raise KnowledgeError("Capture reservation changed before publication")
            stage.rename(final)
        except Exception:
            shutil.rmtree(stage, ignore_errors=True)
            if final is not None and reserved_stat is not None:
                try:
                    current = final.lstat()
                    if (current.st_dev, current.st_ino) == (
                        reserved_stat.st_dev, reserved_stat.st_ino
                    ):
                        final.rmdir()
                except OSError:
                    pass
            raise
        for row in output:
            if not row[3]:
                src = row[0]
                target = f"{batch_rel}/originals/{src}"
                output[output.index(row)] = (row[0], row[1], row[2], False, target, captured)
    return {"batch": batch_rel, "sources": [{"source": s, "archived": target, "sha256": digest, "size": size, "captured_at": stamp, "reused": reused, "wiki_link": f"[{_label(s)}]({quote(os.path.relpath(target, 'wiki'), safe='/._-')})"} for s, digest, size, reused, target, stamp in output], "limits": LIMITS[:]}


def _label(text: str) -> str:
    return re.sub(r"([\\\[\]])", r"\\\1", text)


def _slug(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text).strip().lower().replace("`", "")
    return re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE).replace(" ", "-")


def _markdown(text: str):
    """Return typed links and fragment ids for common Markdown/Obsidian syntax."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
        else:
            lines.append(line)
    clean = "\n".join(lines)
    heads = set()
    counts = {}
    for line in lines:
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            slug = _slug(match.group(1))
            number = counts.get(slug, 0)
            counts[slug] = number + 1
            heads.add(f"{slug}-{number}" if number else slug)
    heads.update(re.findall(r"\b(?:id|name)\s*=\s*['\"]([^'\"]+)", clean, re.I))
    # Preserve inline-code text in heading ids, but ignore it as link syntax.
    clean = re.sub(r"(`+)(.+?)\1", "", clean)
    refs = {}
    reference = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+)).*$", re.M)
    for match in reference.finditer(clean):
        refs[" ".join(match.group(1).lower().split())] = match.group(2) or match.group(3)
    clean = reference.sub("", clean)
    links = []
    pattern = re.compile(
        r"\[\[([^\]]+)\]\]"
        r"|!?\[((?:\\.|[^\]\\])*)\]\(\s*(?:<([^>]+)>|((?:\\.|[^\s)])*))"
        r"(?:\s+[^)]*)?\)"
        r"|!?\[((?:\\.|[^\]\\])*)\]\[([^\]]*)\]"
        r"|(?<!!)\[([^\]\n]+)\]"
    )
    for match in pattern.finditer(clean):
        if match.group(1) is not None:
            target = match.group(1).split("|", 1)[0]
            links.append((target, True))
        elif match.group(2) is not None:
            links.append((match.group(3) or match.group(4) or "", False))
        elif match.group(5) is not None:
            key = " ".join((match.group(6) or match.group(5)).lower().split())
            links.append((refs.get(key), False))
        else:
            key = " ".join(match.group(7).lower().split())
            if key in refs:
                links.append((refs[key], False))
    return links, heads


def _link_path(root: Path, value: Path) -> Path:
    # Check lexical traversal before resolving, so symlink ancestors stay visible.
    absolute = Path(os.path.abspath(value))
    try:
        rel = absolute.relative_to(root).as_posix()
    except ValueError:
        raise KnowledgeError("Link escapes workspace") from None
    if any(part in (".git", "runtime", "credentials", ".credentials") or
           part == ".env" or part.startswith(".env.") for part in Path(rel).parts):
        raise KnowledgeError(f"Link targets protected state: {rel}")
    return _path(root, rel)


def _wiki_files(root: Path) -> list[Path]:
    base = _path(root, "wiki")
    if not base.exists():
        return []
    files = []
    def walk_error(error):
        raise KnowledgeError(str(error))
    for directory, dirs, names in os.walk(base, followlinks=False, onerror=walk_error):
        for name in dirs + names:
            if (Path(directory) / name).is_symlink():
                raise KnowledgeError(f"Symlink in wiki: {Path(directory) / name}")
        dirs.sort()
        files.extend(Path(directory) / name for name in sorted(names) if name.endswith(".md"))
        if len(files) > MAX_FILES:
            raise KnowledgeError("Wiki file count exceeds limit")
    return files


def complete(root: Path, pages: list[str] | None = None) -> dict:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise KnowledgeError(f"Workspace is not a real directory: {root}")
    root = root.resolve()
    required = ["wiki", "inbox"]
    absent = []
    selected = []
    for rel in required:
        path = root / rel
        if path.is_symlink():
            raise KnowledgeError(f"Symlink path is not allowed: {rel}")
        if path.exists():
            selected.append(rel)
        else:
            absent.append(rel)
    extras = []
    for name in pages or []:
        rel = _safe_rel(name)
        path = _path(root, rel)
        if not path.is_file() or path.suffix.lower() != ".md":
            raise KnowledgeError(f"Additional page must be an existing Markdown file: {rel}")
        extras.append(rel)
    result = _check(root, selected + extras, mode="completion")
    result["scope"].update({
        "required_roots": required, "absent_roots": absent,
        "additional_pages": sorted(set(extras)),
        "excluded": ["Archived evidence payloads are integrity-checked but not prose-scanned.",
                     "Runtime, Git, credentials, and paths outside selected roots/pages are excluded."],
    })
    result["limits"].extend([
        "Success does not establish semantic integration or answered-inbox handling.",
        "Success does not establish source support or discovery of undeclared maintained pages outside fixed roots.",
    ])
    return result


def check(root: Path, paths: list[str] | None = None) -> dict:
    return _check(root, paths)


def _check(root: Path, paths: list[str] | None = None, *, mode: str = "check") -> dict:
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise KnowledgeError(f"Workspace is not a real directory: {root}")
    root = root.resolve()
    errors = []
    manifests = checked = links_checked = 0
    try:
        records = _manifest_entries(root)
        manifests = len({archived.split("/originals/", 1)[0] for _, _, archived in records})
    except (KnowledgeError, OSError) as exc:
        errors.append({"path": ".agents", "message": str(exc)})
    files = set()
    selected = paths if paths is not None else (["wiki"] if (root / "wiki").exists() else [])
    selected_paths = []
    try:
        for name in selected:
            rel = _safe_rel(name.rstrip("/"), allow_agents_skills=True)
            selected_paths.append(rel)
            path = _path(root, rel)
            if path.is_file():
                if path.suffix.lower() != ".md":
                    raise KnowledgeError(f"Select Markdown files: {rel}")
                files.add(path)
            elif path.is_dir():
                def walk_error(error):
                    raise KnowledgeError(str(error))
                for directory, dirs, names in os.walk(path, followlinks=False, onerror=walk_error):
                    for child in dirs + names:
                        item = Path(directory) / child
                        if item.is_symlink():
                            raise KnowledgeError(f"Symlink in selected tree: {item.relative_to(root)}")
                    dirs[:] = sorted(d for d in dirs if d not in (".agents", ".git", "runtime", "credentials", ".credentials"))
                    for child in names:
                        if child.lower().endswith(".md"):
                            item = Path(directory) / child
                            _safe_rel(item.relative_to(root).as_posix(), allow_agents_skills=True)
                            files.add(item)
                    if len(files) > MAX_FILES:
                        raise KnowledgeError(f"Markdown file count exceeds {MAX_FILES}")
            else:
                raise KnowledgeError(f"Selected path does not exist: {rel}")
        if len(files) > MAX_FILES:
            raise KnowledgeError(f"Markdown file count exceeds {MAX_FILES}")
    except (KnowledgeError, OSError) as exc:
        errors.append({"path": str(paths or "wiki"), "message": str(exc)})
    cache = {}
    total = 0
    def document(path):
        nonlocal total
        if path not in cache:
            data = _read_file(path, MAX_FILE)
            total += len(data)
            if total > MAX_TOTAL or len(cache) >= MAX_FILES:
                raise KnowledgeError("Markdown read limits exceeded")
            cache[path] = _markdown(data.decode("utf-8"))
        return cache[path]
    checked_paths = []
    wiki_catalog = None
    for file in sorted(files):
        rel = file.relative_to(root).as_posix()
        try:
            links, _ = document(file)
            checked += 1
            checked_paths.append(rel)
            for target, is_wiki in links:
                if target is not None and (re.match(r"^[A-Za-z][\w+.-]*:", target) or target.startswith("//")):
                    continue
                links_checked += 1
                try:
                    if target is None:
                        raise KnowledgeError("Missing reference-link definition")
                    bits = urlsplit(target)
                    decoded = re.sub(r"\\([\\ ()\[\]])", r"\1", unquote(bits.path))
                    if decoded.startswith("/"):
                        raise KnowledgeError("Absolute link target is outside relative workspace navigation")
                    if not decoded:
                        dest = file
                    elif not is_wiki:
                        dest = _link_path(root, file.parent / decoded)
                    else:
                        suffix = "" if Path(decoded).suffix else ".md"
                        # Relative and workspace-qualified wiki paths precede basename resolution.
                        direct = [_link_path(root, file.parent / (decoded + suffix))]
                        if not decoded.startswith("."):
                            direct.append(_link_path(root, root / (decoded + suffix)))
                        found = {p for p in direct if p.is_file()}
                        if not found:
                            if wiki_catalog is None:
                                wiki_catalog = _wiki_files(root)
                            found = {p for p in wiki_catalog if p.name == Path(decoded + suffix).name}
                        if len(found) > 1:
                            raise KnowledgeError(f"Ambiguous wiki link: {target}")
                        if not found:
                            raise KnowledgeError(f"Unresolved wiki link: {target}")
                        dest = next(iter(found))
                    if not dest.exists():
                        raise KnowledgeError(f"Unresolved link: {target}")
                    if bits.fragment and dest.is_file() and dest.suffix.lower() == ".md":
                        _, headings = document(dest)
                        fragment = unquote(bits.fragment)
                        if fragment not in headings and not (is_wiki and _slug(fragment) in headings):
                            raise KnowledgeError(f"Missing heading #{fragment} in {dest.relative_to(root)}")
                except (OSError, UnicodeError, ValueError, KnowledgeError) as exc:
                    errors.append({"path": rel, "message": str(exc)})
        except (OSError, UnicodeError, KnowledgeError) as exc:
            errors.append({"path": rel, "message": str(exc)})
    return {"ok": not errors, "mode": mode,
            "scope": {"selected_paths": list(dict.fromkeys(selected_paths)),
                      "checked_paths": checked_paths},
            "checked_files": checked, "links_checked": links_checked,
            "manifests_checked": manifests, "errors": errors, "limits": LIMITS[:]}


EPISODIC_NAME = re.compile(r"(?i)(?:^|[-_ .])(?:batch|session|sess|run|part|round|day|week|chunk)[-_ ]?\d+|\d{4}-\d{2}-\d{2}")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def _headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """(line index, level, text) for ATX headings outside fenced code blocks."""
    out, fence = [], None
    for index, line in enumerate(lines):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        match = HEADING.match(line)
        if match:
            out.append((index, len(match.group(1)), match.group(2)))
    return out


def _page_target(page: Path, target: str, is_wiki: bool, root: Path) -> Path | None:
    """Resolve a link to a workspace file, or None for external, anchor-only or unresolvable targets."""
    target = unquote((target or "").split("#", 1)[0].strip())
    if not target or re.match(r"^[A-Za-z][\w+.-]*:", target) or target.startswith("//"):
        return None
    if is_wiki:
        name = target if target.endswith(".md") else target + ".md"
        for candidate in (page.parent / name, root / "wiki" / name, root / name):
            if candidate.is_file():
                return candidate.resolve()
        return None
    candidate = (root / target.lstrip("/")) if target.startswith("/") else (page.parent / target)
    if candidate.is_dir():
        for index in ("index.md", "README.md"):
            if (candidate / index).is_file():
                return (candidate / index).resolve()
        return None
    return candidate.resolve() if candidate.is_file() else None


def account(root: Path, sources: list[str] | None = None, max_page_bytes: int | None = None) -> dict:
    """Check that retained understanding forms one discoverable, subject-organized account.

    Retained pages are Markdown files outside `.agents/`, `.git/` and the given source directories.
    Every page must be reachable by links from README.md; page names must not be per-session,
    per-batch or dated; no retained file may carry a line selector or other colon in its name.
    With `max_page_bytes`, pages larger than that (too big to read in one pass) also fail the check."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise KnowledgeError(f"Workspace is not a real directory: {root}")
    excluded = {".agents", ".git", *(sources or [])}
    retained, invalid = [], []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if not path.is_file() or rel.split("/", 1)[0] in excluded:
            continue
        if ":" in path.name:
            invalid.append(rel)
        elif path.suffix.lower() == ".md":
            retained.append(path.resolve())
    entry = (root / "README.md").resolve()
    reachable = set()
    if entry.is_file():
        queue = [entry]
        while queue:
            page = queue.pop()
            if page in reachable:
                continue
            reachable.add(page)
            links, _ = _markdown(page.read_text(encoding="utf-8", errors="replace"))
            for target, is_wiki in links:
                resolved = _page_target(page, target, is_wiki, root)
                if resolved is not None and resolved in retained and resolved not in reachable:
                    queue.append(resolved)
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    unreachable = [rel(p) for p in retained if p not in reachable]
    episodic = [rel(p) for p in retained if EPISODIC_NAME.search(p.stem)]
    episodic_headings = [f"{rel(p)}#{text}" for p in retained
                         for _, level, text in _headings(p.read_text(encoding="utf-8", errors="replace").splitlines())
                         if level <= 3 and EPISODIC_NAME.search(" " + text)]
    roots = sorted({rel(p).split("/", 1)[0] for p in retained if "/" in rel(p)})
    sizes = {rel(p): p.stat().st_size for p in retained}
    oversized = sorted(name for name, size in sizes.items() if max_page_bytes is not None and size > max_page_bytes)
    ok = entry.is_file() and not unreachable and not episodic and not episodic_headings and not invalid and not oversized
    return {"ok": ok, "entry_point": "README.md" if entry.is_file() else None, "retained_pages": len(retained),
            "reachable_pages": len(reachable), "unreachable": unreachable[:50], "unreachable_count": len(unreachable),
            "episodic_names": episodic[:50], "episodic_count": len(episodic),
            "episodic_headings": episodic_headings[:50], "episodic_heading_count": len(episodic_headings),
            "invalid_names": invalid[:50], "invalid_count": len(invalid), "page_directories": roots,
            "largest_page_bytes": max(sizes.values(), default=0), "max_page_bytes": max_page_bytes,
            "oversized_pages": oversized[:50], "oversized_count": len(oversized),
            "limits": ["Structure only: reachability, naming and size do not establish that the content is accurate, supported or subject-organized in meaning."]}


MD_LINK = re.compile(r"(?<!!)(\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")


def _rewrite_links(text: str, rewrite) -> tuple[str, int]:
    """Apply `rewrite(target) -> new target or None` to inline Markdown links outside code fences."""
    count = 0
    out, fence = [], None
    for line in text.split("\n"):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence or marker:
            if fence and marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            elif not fence and marker:
                fence = marker.group(1)
            out.append(line)
            continue

        def swap(match):
            nonlocal count
            new = rewrite(match.group(2))
            if new is None or new == match.group(2):
                return match.group(0)
            count += 1
            return match.group(1) + new + match.group(3)
        out.append(MD_LINK.sub(swap, line))
    return "\n".join(out), count


def split(root: Path, page: str, max_bytes: int = 16384) -> dict:
    """Split an oversized Markdown page at its top-level sections into linked child pages.

    The page keeps its preamble and gains a Contents list linking `<page stem>/<section>.md` children. Section text moves
    verbatim, except that relative links are rewritten to stay correct and each child ends with a link back. Links from
    other retained pages to a moved heading are repointed to the child that now holds it. Children still over `max_bytes`
    are split again at their next heading level; anything that cannot be split further is reported, not truncated.
    This repairs size and navigation only; it does not reorganize meaning (section names are kept as written)."""
    root = Path(root).resolve()
    target = _path(root, _safe_rel(page))
    if target.is_symlink() or not target.is_file() or target.suffix.lower() != ".md":
        raise KnowledgeError(f"Not a regular Markdown page: {page}")
    report = {"page": page, "max_bytes": max_bytes, "created": [], "links_rewritten": 0, "still_oversized": []}
    moved = {}  # heading slug -> child path, for repointing inbound fragment links
    _split_page(root, target, max_bytes, report, moved, level=None)
    for other in sorted(root.rglob("*.md")):
        rel_other = other.relative_to(root).as_posix()
        if other == target or rel_other.split("/", 1)[0] in (".agents", ".git") or not other.is_file() or str(other) in report["created_paths_internal"]:
            continue
        text = other.read_text(encoding="utf-8", errors="replace")

        def inbound(link, other=other):
            path, _, fragment = link.partition("#")
            if not path or re.match(r"^[A-Za-z][\w+.-]*:", path) or not fragment:
                return None
            if (other.parent / unquote(path)).resolve() != target.resolve() or fragment not in moved:
                return None
            return os.path.relpath(moved[fragment], other.parent).replace(os.sep, "/") + "#" + fragment
        new_text, count = _rewrite_links(text, inbound)
        if count:
            other.write_text(new_text, encoding="utf-8")
            report["links_rewritten"] += count
    report.pop("created_paths_internal", None)
    report["parent_bytes"] = target.stat().st_size
    report["largest_child_bytes"] = max((c["bytes"] for c in report["created"]), default=0)
    return report


def _split_page(root: Path, target: Path, max_bytes: int, report: dict, moved: dict, level: int | None) -> None:
    report.setdefault("created_paths_internal", [])
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    heads = _headings(lines)
    levels = sorted({lvl for _, lvl, _ in heads if lvl >= 2 and (level is None or lvl > level)})
    if not levels:
        report["still_oversized"].append(target.relative_to(root).as_posix())
        return
    cut = levels[0]
    starts = [(i, t) for i, lvl, t in heads if lvl == cut]
    preamble = lines[:starts[0][0]]
    child_dir = target.parent / target.stem
    child_dir.mkdir(exist_ok=True)
    sections, used = [], set()
    for n, (start, title) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        slug = (_slug(title)[:60].strip("-") or f"section-{n + 1}")
        name, k = slug, 2
        while name in used or (child_dir / f"{name}.md").exists():
            name, k = f"{slug}-{k}", k + 1
        used.add(name)
        sections.append((title, child_dir / f"{name}.md", lines[start:end]))
    owner = {}
    for title, path, body in sections:
        for _, _, text_ in _headings(body):
            owner.setdefault(_slug(text_), path)
    for title, path, body in sections:
        def relink(link, path=path):
            if re.match(r"^[A-Za-z][\w+.-]*:", link) or link.startswith("//"):
                return None
            if link.startswith("#"):
                holder = owner.get(link[1:])
                return None if holder in (None, path) else os.path.relpath(holder, path.parent).replace(os.sep, "/") + link
            file_part, sep, fragment = link.partition("#")
            if file_part.startswith("/"):
                return None
            moved_to = os.path.relpath((target.parent / unquote(file_part)).resolve(), path.parent).replace(os.sep, "/")
            return moved_to + sep + fragment
        body_text, count = _rewrite_links("\n".join(body).rstrip("\n"), relink)
        report["links_rewritten"] += count
        back = os.path.relpath(target, path.parent).replace(os.sep, "/")
        path.write_text(body_text + f"\n\n[Back to {target.stem}]({back})\n", encoding="utf-8")
        report["created_paths_internal"].append(str(path))
        for slug in (_slug(t) for _, _, t in _headings(body)):
            moved[slug] = path
    def parent_text(summaries):
        contents = ["## Contents", ""]
        for title, path, body in sections:
            first = next((line.strip() for line in body[1:] if line.strip() and not HEADING.match(line)), "") if summaries else ""
            first = re.sub(r"\s+", " ", first)[:160]
            contents.append(f"- [{title}]({path.relative_to(target.parent).as_posix()})" + (f": {first}" if first else ""))
        return ("\n".join(preamble).rstrip("\n") + "\n\n" + "\n".join(contents) + "\n").lstrip("\n")
    new_parent = parent_text(True)
    if len(new_parent.encode("utf-8")) > max_bytes:  # a long contents list alone can exceed the limit; keep titles only
        new_parent = parent_text(False)
    target.write_text(new_parent, encoding="utf-8")
    if target.stat().st_size > max_bytes:
        report["still_oversized"].append(target.relative_to(root).as_posix())
    for title, path, body in sections:
        size = path.stat().st_size
        report["created"].append({"path": path.relative_to(root).as_posix(), "bytes": size})
        if size > max_bytes:
            _split_page(root, path, max_bytes, report, moved, level=cut)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capture")
    chk = sub.add_parser("check")
    completion = sub.add_parser("complete")
    acct = sub.add_parser("account")
    spl = sub.add_parser("split")
    for command in (cap, chk, completion, acct, spl):
        command.add_argument("--root", type=Path, default=Path.cwd())
    acct.add_argument("--source", action="append", default=[], dest="sources", help="Top-level source directory to exclude (repeatable)")
    acct.add_argument("--max-page-bytes", type=int, default=None, help="Also fail pages larger than this many bytes")
    spl.add_argument("page", help="Workspace-relative Markdown page to split")
    spl.add_argument("--max-bytes", type=int, default=16384, help="Split children that are still larger than this")
    cap.add_argument("paths", nargs="+")
    chk.add_argument("paths", nargs="*")
    completion.add_argument("--page", action="append", default=[], dest="pages")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    try:
        if args.command == "capture":
            result = capture(args.root, args.paths)
        elif args.command == "complete":
            result = complete(args.root, args.pages)
        elif args.command == "account":
            result = account(args.root, args.sources, args.max_page_bytes)
        elif args.command == "split":
            result = split(args.root, args.page, args.max_bytes)
            result["ok"] = not result["still_oversized"]
        else:
            result = check(args.root, args.paths or None)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if args.command == "capture" or result["ok"] else 1
    except (KnowledgeError, OSError, UnicodeError) as exc:
        print(f"luma-knowledge: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

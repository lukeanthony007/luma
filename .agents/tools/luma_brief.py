#!/usr/bin/env python3
"""Stdlib-only brief validator, vendored from luma-harness 0.2.0.

Generated: regenerate with luma-harness tools/vendor_brief.py, do not edit by hand.

usage: python3 .agents/tools/luma_brief.py [--workspace DIR] check [--json] [brief ...]
       python3 .agents/tools/luma_brief.py [--workspace DIR] index
       python3 .agents/tools/luma_brief.py [--workspace DIR] archive <id> [--status done|superseded]
       python3 .agents/tools/luma_brief.py [--workspace DIR] new <slug> --sender <name> [--date YYYY-MM-DD]
"""
"""Strict YAML-subset front matter: scalars, flow lists, block lists, one level of nested maps.

Supported shapes (anything else is a FrontMatterError):
  key: scalar | [flow, list] | {flow: map}
  key:                      # block value follows, indented
    - scalar                # list of scalars
    - name: value           # list of one-level maps (continuation lines indented under the dash)
      other: value
  key:
    sub: scalar | [flow, list]
    sub:
      - scalar              # map of scalars or lists of scalars
Scalars: double-quoted (JSON escapes), single-quoted ('' escape), true/false, null/~, int, float, plain text (including
text that starts with a backtick, *, @, % or a bracket that does not close a flow collection). A one-line list item
`- Text: more` keeps its raw text on the parsed map (`InlineMap.raw`) so string fields can use it. A list may start
its dashes at the key's own indentation. CRLF line ends, a BOM and trailing spaces on the fences are accepted.
Refused: anchors, tags, block scalars (| and >), and nesting deeper than shown. Python 3.9 compatible, stdlib only.
"""
import json
import re

_INT = re.compile(r"^[-+]?[0-9]+$")
_FLOAT = re.compile(r"^[-+]?([0-9]+\.[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$|^[-+]?[0-9]+[eE][-+]?[0-9]+$")
_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(?:\s+(.*))?$")
_PLAIN_SAFE = re.compile(r"^[A-Za-z0-9_./@()+-][^#:\[\]{},\"']*$")


class FrontMatterError(ValueError):
    def __init__(self, line, message):
        super().__init__("line %d: %s" % (line, message) if line else message)
        self.line = line


class InlineMap(dict):
    """A one-line `- key: value` list item: a map that remembers its raw text, for fields that expect strings."""

    raw = ""


def split(text):
    """Return (front_matter_text, body_text, body_start_line). Raises when the --- fences are missing."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n")
    lines = text.split("\n")
    if lines[0].rstrip() != "---":
        raise FrontMatterError(1, "front matter must start with a '---' line")
    close = next((index for index in range(1, len(lines)) if lines[index].rstrip() == "---"), None)
    if close is None:
        raise FrontMatterError(0, "front matter is not closed by a '---' line")
    front = "\n".join(lines[1:close]) + "\n"
    body = "\n".join(lines[close + 1:])
    return front, body, close + 2


def _strip_comment(value):
    # Plain scalars end at " #"; quoted scalars are handled before this is called.
    index = value.find(" #")
    return value[:index].rstrip() if index >= 0 else value.rstrip()


def _quoted(value, line):
    if value.startswith('"'):
        try:
            decoder = json.JSONDecoder()
            parsed, end = decoder.raw_decode(value)
        except ValueError:
            raise FrontMatterError(line, "malformed double-quoted string")
        rest = value[end:].strip()
        if rest and not rest.startswith("#"):
            raise FrontMatterError(line, "text after quoted string")
        return parsed, True
    if value.startswith("'"):
        out, i = [], 1
        while i < len(value):
            ch = value[i]
            if ch == "'":
                if i + 1 < len(value) and value[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                rest = value[i + 1:].strip()
                if rest and not rest.startswith("#"):
                    raise FrontMatterError(line, "text after quoted string")
                return "".join(out), True
            out.append(ch)
            i += 1
        raise FrontMatterError(line, "unterminated single-quoted string")
    return None, False


def scalar(value, line=0):
    value = value.strip()
    parsed, was_quoted = _quoted(value, line)
    if was_quoted:
        return parsed
    value = _strip_comment(value)
    if value == "":
        return None
    if re.match(r"^[|>][-+0-9]*$", value):
        raise FrontMatterError(line, "block scalars (| and >) are not supported; write the text on one line")
    if re.match(r"^[&!]\S*(\s|$)", value):
        raise FrontMatterError(line, "anchors and tags are not supported")
    if value in ("null", "~", "Null", "NULL"):
        return None
    if value in ("true", "True", "TRUE"):
        return True
    if value in ("false", "False", "FALSE"):
        return False
    if _INT.match(value):
        return int(value)
    if _FLOAT.match(value):
        return float(value)
    if value.startswith(("[", "{")) and value.endswith(("]", "}")):
        raise FrontMatterError(line, "flow collection where a scalar was expected")
    return value


def _split_flow(inner, line):
    items, depth, quote, current = [], 0, None, []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if quote:
            current.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(inner):
                current.append(inner[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'" and not "".join(current).strip():  # a quote opens only at the start of an item
            quote = ch
            current.append(ch)
        elif ch in "[{":
            raise FrontMatterError(line, "nested flow collections are not supported")
        elif ch == ",":
            items.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    if quote:
        raise FrontMatterError(line, "unterminated quote in flow collection")
    tail = "".join(current).strip()
    if tail or items:
        items.append(tail)
    if any(item == "" for item in items):
        raise FrontMatterError(line, "empty item in flow collection")
    return items


def value(text, line=0):
    """Parse an inline value: scalar, [flow list] or {flow: map}. A bracket that does not close is plain text."""
    text = text.strip()
    closed = _strip_comment(text)
    if text.startswith("[") and closed.endswith("]"):
        body = _strip_flow(text, "[", "]", line)
        return [scalar(item, line) for item in _split_flow(body, line)]
    if text.startswith("{") and closed.endswith("}"):
        body = _strip_flow(text, "{", "}", line)
        out = {}
        for item in _split_flow(body, line):
            match = _KEY.match(item)
            if not match:
                raise FrontMatterError(line, "malformed flow map entry %r" % item)
            if match.group(1) in out:
                raise FrontMatterError(line, "duplicate key %r" % match.group(1))
            out[match.group(1)] = scalar(match.group(2) or "", line)
        return out
    return scalar(text, line)


def _strip_flow(text, opener, closer, line):
    close = text.rfind(closer)
    if close < 0:
        raise FrontMatterError(line, "unterminated flow collection")
    rest = text[close + 1:].strip()
    if rest and not rest.startswith("#"):
        raise FrontMatterError(line, "text after flow collection")
    return text[1:close]


def _inline(rest):
    """True when 'key: rest' carries an inline value (a quoted string, even empty, counts)."""
    return rest is not None and (rest.strip().startswith(("'", '"')) or _strip_comment(rest) != "")


def _lines(front, first_line):
    out = []
    for offset, raw in enumerate(front.split("\n")):
        number = first_line + offset
        if "\t" in raw[:len(raw) - len(raw.lstrip())]:
            raise FrontMatterError(number, "tabs are not allowed for indentation")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append((number, len(raw) - len(raw.lstrip(" ")), stripped))
    return out


def parse(front, first_line=2):
    """Parse front matter text (without fences) into a dict, preserving key order."""
    lines = _lines(front, first_line)
    data, i = {}, 0
    while i < len(lines):
        number, indent, text = lines[i]
        if indent != 0:
            raise FrontMatterError(number, "unexpected indentation")
        match = _KEY.match(text)
        if not match:
            raise FrontMatterError(number, "expected 'key: value'")
        key, rest = match.group(1), match.group(2)
        if key in data:
            raise FrontMatterError(number, "duplicate key %r" % key)
        i += 1
        if _inline(rest):
            data[key] = value(rest, number)
            continue
        block = []
        while i < len(lines) and (lines[i][1] > 0 or lines[i][2] == "-" or lines[i][2].startswith("- ")):
            block.append(lines[i])  # dashes may sit at the key's own indentation
            i += 1
        data[key] = _block(block, number, depth=1) if block else None
    return data


def _block(block, owner_line, depth):
    first_indent = block[0][1]
    if any(indent < first_indent for _, indent, _ in block):
        raise FrontMatterError(block[0][0], "inconsistent indentation")
    if block[0][2].startswith("- ") or block[0][2] == "-":
        return _block_list(block, first_indent, depth)
    if depth > 1:
        raise FrontMatterError(block[0][0], "maps nested deeper than one level are not supported")
    out, i = {}, 0
    while i < len(block):
        number, indent, text = block[i]
        if indent != first_indent:
            raise FrontMatterError(number, "unexpected indentation")
        match = _KEY.match(text)
        if not match:
            raise FrontMatterError(number, "expected 'key: value' inside map")
        key, rest = match.group(1), match.group(2)
        if key in out:
            raise FrontMatterError(number, "duplicate key %r" % key)
        i += 1
        if _inline(rest):
            out[key] = value(rest, number)
            continue
        sub = []
        while i < len(block) and (block[i][1] > first_indent or (block[i][1] == first_indent and (block[i][2] == "-" or block[i][2].startswith("- ")))):
            sub.append(block[i])
            i += 1
        if not sub:
            out[key] = None
            continue
        if not (sub[0][2].startswith("- ") or sub[0][2] == "-"):
            raise FrontMatterError(sub[0][0], "maps nested deeper than one level are not supported")
        out[key] = _block_list(sub, sub[0][1], depth + 1)
    return out


def _block_list(block, indent, depth):
    items, i = [], 0
    while i < len(block):
        number, item_indent, text = block[i]
        if item_indent != indent or not (text.startswith("- ") or text == "-"):
            raise FrontMatterError(number, "expected '- item' at list indentation")
        content = text[1:].strip()
        i += 1
        continuation = []
        while i < len(block) and block[i][1] > indent:
            continuation.append(block[i])
            i += 1
        match = _KEY.match(content) if not content.startswith(("'", '"', "[", "{")) else None
        if match and not continuation and depth > 1:
            items.append(value(content, number))  # nested lists hold strings: `- Note: text` is text
            continue
        if match:
            if depth > 1:
                raise FrontMatterError(number, "maps inside nested lists are not supported")
            entry = InlineMap() if not continuation else {}
            if not continuation:
                entry.raw = content
            pairs = [(number, match.group(1), match.group(2))]
            for c_number, c_indent, c_text in continuation:
                c_match = _KEY.match(c_text)
                if not c_match or c_indent != continuation[0][1]:
                    raise FrontMatterError(c_number, "list-item maps take only 'key: value' lines at one indentation")
                pairs.append((c_number, c_match.group(1), c_match.group(2)))
            for p_number, key, rest in pairs:
                if key in entry:
                    raise FrontMatterError(p_number, "duplicate key %r" % key)
                if not _inline(rest):
                    raise FrontMatterError(p_number, "list-item map values must be inline")
                entry[key] = value(rest, p_number)
            items.append(entry)
        else:
            if continuation:
                raise FrontMatterError(continuation[0][0], "unexpected indentation under list item")
            if content == "":
                raise FrontMatterError(number, "empty list item")
            items.append(value(content, number))
    return items


def format_scalar(item):
    if item is None:
        return "null"
    if item is True:
        return "true"
    if item is False:
        return "false"
    if isinstance(item, (int, float)):
        return repr(item)
    text = str(item)
    if text and _PLAIN_SAFE.match(text) and text == text.strip() and not isinstance(scalar(text), (bool, int, float, type(None))):
        return text
    return json.dumps(text, ensure_ascii=False)


def format_value(item, indent=0, flow_lists=False):
    """Serialize one value as the text after 'key:' (leading space or newline included)."""
    pad = " " * (indent + 2)
    if isinstance(item, list):
        if not item:
            return " []"
        if flow_lists and all(not isinstance(x, (list, dict)) for x in item):
            return " [" + ", ".join(format_scalar(x) for x in item) + "]"
        out = []
        for entry in item:
            if isinstance(entry, dict):
                keys = list(entry)
                out.append(pad + "- " + keys[0] + ":" + format_value(entry[keys[0]], indent + 2, True).rstrip("\n"))
                for key in keys[1:]:
                    out.append(pad + "  " + key + ":" + format_value(entry[key], indent + 2, True).rstrip("\n"))
            else:
                out.append(pad + "- " + format_scalar(entry))
        return "\n" + "\n".join(out)
    if isinstance(item, dict):
        if not item:
            return " {}"
        out = []
        for key, sub in item.items():
            out.append(pad + key + ":" + format_value(sub, indent + 2, flow_lists))
        return "\n" + "\n".join(out)
    return " " + format_scalar(item)


def dump(data, flow_lists=False):
    """Serialize a dict to front matter text (without fences), one top-level key per block."""
    return "".join(key + ":" + format_value(item, 0, flow_lists) + "\n" for key, item in data.items())


def set_field(front, key, item, flow_lists=True):
    """Replace (or append) one top-level key in front matter text, leaving every other line untouched."""
    lines = front.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    start = next((index for index, line in enumerate(lines) if _KEY.match(line) and _KEY.match(line).group(1) == key), None)
    new = (key + ":" + format_value(item, 0, flow_lists)).split("\n")
    if start is None:
        lines.extend(new)
    else:
        end = start + 1
        while end < len(lines) and (lines[end].startswith(" ") or not lines[end].strip()):
            end += 1
        while end > start + 1 and not lines[end - 1].strip():
            end -= 1  # keep blank separator lines that belong between top-level keys
        lines[start:end] = new
    return "\n".join(lines) + "\n"


"""Brief files: load, validate, index, archive, new. The file contract is SCHEMAS.md section 1.

A brief is `.agents/briefs/YYYY-MM-DD-<slug>.md`: strict front matter, then exactly the headings
Goal, Context, Deliverables, Report-back and optionally Corrections. Finished briefs live under
`.agents/briefs/archive/YYYY/`. This module is vendored into the Luma seed as `.agents/tools/luma_brief.py`
(with frontmatter.py), so it stays stdlib-only and Python 3.9 compatible.
"""
import argparse
import datetime
import fnmatch
import json
import os
import posixpath
import re
import sys
import threading
from pathlib import Path

try:
    import fcntl
except ImportError:  # the seed copy may run where fcntl does not exist; writes are then unlocked
    fcntl = None


STATUSES = ("open", "running", "done", "superseded")
FINAL_STATUSES = ("done", "superseded")
HOSTS = ("omp", "claude", "animus", "codex")
HEADINGS = ("Goal", "Context", "Deliverables", "Report-back")
OPTIONAL_HEADING = "Corrections"
HANDOFF_HEADINGS = ("Question", "Contributor", "Sources examined", "Findings", "Support", "Premises", "Qualifications",
                    "Disagreement", "Unexamined scope", "Proposed effect", "Changed files")
DEFAULT_STOP_CONDITIONS = ("spend cap", "write outside scope")
DEFAULT_APPROVAL_LINE_USD = 10.0
CONTEXT_MAX_LINES = 40
IDENTITY_NAMES = ("agent", "runtime", "harness", "session", "system")
IDENTITY_PREFIXES = ("agent:", "session:", "runtime:", "harness:", "sub:")

ID_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9-]{3,48})$")
RUN_ID_PATTERN = re.compile(r"^\d{8}T\d{6}Z-[a-z0-9-]+-[0-9a-f]{4}$")
SESSION_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$")
URL_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://\S+$")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
CORRECTION_PATTERN = re.compile(r"^- (\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?) ([^:]+?): (\S.*)$")

# field -> (type, required). Types: id, date, str, enum:<a|b>, float+, int+, bool, ts, list[str], list[path],
# list[link], list[host], list[run], map, list[deliverable]
TOP_FIELDS = {
    "id": ("id", True), "date": ("date", True), "sender": ("identity", True), "goal": ("goal", True),
    "status": ("status", True), "supersedes": ("id", False), "context": ("list[link]", True),
    "scope": ("map:scope", True), "constraints": ("map:constraints", True), "deliverables": ("list[deliverable]", True),
    "success_criteria": ("list[str]", True), "stop_conditions": ("list[str]", True),
    "report_back": ("map:report_back", False), "approval": ("map:approval", False), "runs": ("list[run]", False),
    "archived_at": ("ts", False),
}
MAP_FIELDS = {
    "scope": {"in": ("list[str]", True), "out": ("list[str]", True), "write": ("list[path]", True), "read": ("list[path]", False)},
    "constraints": {"spend_cap_usd": ("float+", True), "wall_clock_s": ("int+", True), "tool_budget": ("int+", False),
                    "no_push": ("bool", False), "no_merge": ("bool", False), "external_effects": ("bool", False),
                    "hosts": ("list[host]", False), "model": ("str", False)},
    "report_back": {"handoff": ("path", False), "sections": ("list[str]", False)},
    "approval": {"by": ("identity", True), "at": ("ts", True), "spend_cap_usd": ("float+", True), "note": ("str", False)},
}
DELIVERABLE_FIELDS = {"path": ("path", True), "kind": ("kind", True), "description": ("str", True)}


class BriefError(Exception):
    """A refusal with an actionable message (CLI exit 1)."""


class Problem:
    __slots__ = ("rule", "message")

    def __init__(self, rule, message):
        self.rule, self.message = rule, message

    def __str__(self):
        return self.rule + ": " + self.message

    def __repr__(self):
        return "Problem(%r, %r)" % (self.rule, self.message)


class Brief:
    """A parsed brief. `meta` is the raw front matter; `sections` maps heading -> body text."""

    def __init__(self, path, text, meta, body, sections, headings, problems):
        self.path, self.text, self.meta, self.body = Path(path), text, meta, body
        self.sections, self.headings, self.parse_problems = sections, headings, problems

    @property
    def id(self):
        return self.meta.get("id") if isinstance(self.meta, dict) else None

    @property
    def archived(self):
        return "archive" in self.path.parent.parts[-2:]

    @property
    def workspace(self):
        return workspace_of(self.path)

    def get(self, dotted, default=None):
        node = self.meta
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def scope_write(self):
        return list(self.get("scope.write") or [])

    @property
    def stop_conditions(self):
        given = [c for c in (self.meta.get("stop_conditions") or []) if isinstance(c, str)]
        lowered = [c.lower() for c in given]
        return given + [c for c in DEFAULT_STOP_CONDITIONS if c not in lowered]

    @property
    def handoff_name(self):
        return self.get("report_back.handoff") or "HANDOFF.md"

    @property
    def handoff_headings(self):
        return list(HANDOFF_HEADINGS) + [s for s in (self.get("report_back.sections") or []) if isinstance(s, str)]


def workspace_of(path):
    """The workspace owning a brief: the parent of the nearest `.agents` ancestor, else the file's folder."""
    path = Path(path).resolve()
    for parent in path.parents:
        if parent.name == ".agents":
            return parent.parent
    return path.parent


def briefs_dir(workspace):
    return Path(workspace) / ".agents" / "briefs"


def _sections(body, first_line):
    """Split the body on headings outside fenced blocks. Returns (sections, headings[(level, title, line)])."""
    sections, headings, current, fence = {}, [], None, None
    for offset, line in enumerate(body.split("\n")):
        stripped = line.strip()
        if fence is None and stripped.startswith(("```", "~~~")):
            fence = stripped[:3]
        elif fence is not None and stripped.startswith(fence):
            fence = None
        elif fence is None:
            match = HEADING_PATTERN.match(line)
            if match:
                headings.append((len(match.group(1)), match.group(2), first_line + offset))
                current = match.group(2) if len(match.group(1)) == 2 else None
                if current is not None and current not in sections:
                    sections[current] = []
                continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip("\n") for name, lines in sections.items()}, headings


def _strings_from_inline_maps(meta):
    """`- Done: all files exist` parses as a one-line map; in a field that holds strings it is that text."""
    def fix(items, kind):
        if not isinstance(items, list) or not kind.startswith("list[") or kind == "list[deliverable]":
            return items
        return [getattr(item, "raw", item) if isinstance(item, dict) and getattr(item, "raw", "") else item for item in items]
    for key, (kind, _) in TOP_FIELDS.items():
        if key in meta:
            meta[key] = fix(meta[key], kind)
    for key, fields in MAP_FIELDS.items():
        if isinstance(meta.get(key), dict):
            for sub, (kind, _) in fields.items():
                if sub in meta[key]:
                    meta[key][sub] = fix(meta[key][sub], kind)
    return meta


def loads(path, text):
    try:
        front, body, body_line = split(text)
        meta = _strings_from_inline_maps(parse(front))
    except FrontMatterError as error:
        return Brief(path, text, {}, "", {}, [], [Problem("frontmatter.syntax", str(error))])
    sections, headings = _sections(body, body_line)
    return Brief(path, text, meta, body, sections, headings, [])


def load(path):
    path = Path(path)
    return loads(path, path.read_text(encoding="utf-8"))


def is_identity(name):
    """True when a sender/from names an agent, session or runtime rather than a person or orchestrator."""
    lowered = str(name).strip().lower()
    return (lowered in IDENTITY_NAMES or lowered.startswith(IDENTITY_PREFIXES)
            or bool(RUN_ID_PATTERN.match(str(name).strip())) or bool(SESSION_ID_PATTERN.match(lowered)))


def path_problem(value):
    """Why a value is not a workspace-relative POSIX path, or None."""
    if not isinstance(value, str) or not value.strip():
        return "must be a non-empty string"
    if value != value.strip() or "\\" in value or "\n" in value:
        return "must be a plain POSIX path"
    if URL_PATTERN.match(value) or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        return "must not carry a URI scheme"
    if value.startswith(("/", "~")):
        return "must be workspace-relative (no leading / or ~)"
    if ".." in value.split("/"):
        return "must not contain '..'"
    return None


def _static_prefix(pattern):
    parts = []
    for part in pattern.split("/"):
        if any(ch in part for ch in "*?["):
            break
        parts.append(part)
    return "/".join(parts)


def path_in_scope(path, patterns):
    """True when `path` lies under one of the scope.write glob prefixes."""
    path = posixpath.normpath(path)
    for pattern in patterns:
        if not isinstance(pattern, str) or path_problem(pattern):
            continue
        if any(ch in pattern for ch in "*?["):
            prefix = _static_prefix(pattern).rstrip("/")
            if pattern.endswith("/**") and (path == prefix or path.startswith(prefix + "/") if prefix else True):
                return True
            if fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path, pattern.replace("**/", "")):
                return True
            continue
        prefix = posixpath.normpath(pattern)
        if path == prefix or path.startswith(prefix.rstrip("/") + "/") or prefix == ".":
            return True
    return False


def _check_type(kind, item, name, problems, brief):
    def bad(rule, message):
        problems.append(Problem(rule, name + " " + message))

    if kind == "str":
        if not isinstance(item, str) or not item.strip():
            bad("field.type", "must be a non-empty string")
    elif kind == "id":
        if not isinstance(item, str) or not ID_PATTERN.match(item):
            bad("id.format", "must be YYYY-MM-DD-<slug> with slug [a-z0-9-]{3,48}")
    elif kind == "date":
        try:
            datetime.date.fromisoformat(item if isinstance(item, str) else "")
        except ValueError:
            bad("date.format", "must be YYYY-MM-DD")
    elif kind == "identity":
        if not isinstance(item, str) or not item.strip():
            bad("sender.empty", "must name who asked")
        elif is_identity(item):
            bad("sender.identity", "names an agent, session or runtime (%r); senders and correctors are people or orchestrators" % item)
    elif kind == "goal":
        if not isinstance(item, str):
            bad("goal.length", "must be one sentence of 20 to 240 characters")
        elif "\n" in item:
            bad("goal.newline", "must be one line")
        elif not 20 <= len(item.strip()) <= 240:
            bad("goal.length", "must be one sentence of 20 to 240 characters (has %d)" % len(item.strip()))
    elif kind == "status":
        if item not in STATUSES:
            bad("status.enum", "must be one of " + ", ".join(STATUSES))
    elif kind == "kind":
        if item not in ("file", "dir"):
            bad("deliverable.kind", "must be file or dir")
    elif kind == "float+":
        if isinstance(item, bool) or not isinstance(item, (int, float)) or item <= 0:
            bad("constraints.range", "must be a number greater than 0")
    elif kind == "int+":
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            bad("constraints.range", "must be an integer greater than 0")
    elif kind == "bool":
        if not isinstance(item, bool):
            bad("field.type", "must be true or false")
    elif kind == "ts":
        if not isinstance(item, str) or not TS_PATTERN.match(item):
            bad("field.type", "must be an ISO 8601 UTC timestamp")
    elif kind == "path":
        reason = path_problem(item)
        if reason:
            bad("path.invalid", reason)
    elif kind.startswith("list["):
        inner = kind[5:-1]
        if not isinstance(item, list):
            bad("field.type", "must be a list")
            return
        for index, entry in enumerate(item):
            label = "%s[%d]" % (name, index)
            if inner == "str":
                if not isinstance(entry, str) or not entry.strip():
                    problems.append(Problem("field.type", label + " must be a non-empty string"))
            elif inner == "path":
                reason = path_problem(entry)
                if reason:
                    problems.append(Problem("path.invalid", label + " " + reason))
            elif inner == "link":
                if not isinstance(entry, str) or not (URL_PATTERN.match(entry) or path_problem(entry.split("#", 1)[0]) is None):
                    problems.append(Problem("context.link", label + " must be a URL or a workspace-relative path"))
            elif inner == "host":
                if entry not in HOSTS:
                    problems.append(Problem("hosts.unknown", label + " must be one of " + ", ".join(HOSTS)))
            elif inner == "run":
                if not isinstance(entry, str) or not RUN_ID_PATTERN.match(entry):
                    problems.append(Problem("runs.format", label + " is not a run id"))
                elif not (brief.workspace / ".agents" / "runs" / entry / "run.json").is_file():
                    problems.append(Problem("runs.unknown", label + " names run %s, which has no run folder" % entry))
            elif inner == "deliverable":
                if not isinstance(entry, dict):
                    problems.append(Problem("field.type", label + " must be a map with path, kind and description"))
                    continue
                _check_map(entry, DELIVERABLE_FIELDS, label, problems, brief)
    elif kind.startswith("map:"):
        if not isinstance(item, dict):
            bad("field.type", "must be a map")
            return
        _check_map(item, MAP_FIELDS[kind[4:]], name, problems, brief)


def _check_map(item, fields, name, problems, brief):
    for key in item:
        if key not in fields:
            problems.append(Problem("field.unknown", "%s.%s is not a brief field" % (name, key)))
    for key, (kind, required) in fields.items():
        if key not in item or item[key] is None:
            if required:
                problems.append(Problem("field.missing", "%s.%s is required" % (name, key)))
            continue
        _check_type(kind, item[key], name + "." + key, problems, brief)


def known_ids(workspace):
    root = briefs_dir(workspace)
    return {p.stem for p in root.rglob("*.md") if ID_PATTERN.match(p.stem)} if root.is_dir() else set()


def validate(brief, approval_line=None, ids=None):
    """Every rule of SCHEMAS.md section 1. Returns a list of Problems (empty when valid)."""
    if brief.parse_problems:
        return list(brief.parse_problems)
    problems, meta = [], brief.meta
    for key in meta:
        if key not in TOP_FIELDS:
            problems.append(Problem("field.unknown", "%s is not a brief field" % key))
    for key, (kind, required) in TOP_FIELDS.items():
        if key not in meta or meta[key] is None:
            if required:
                problems.append(Problem("field.missing", key + " is required"))
            continue
        _check_type(kind, meta[key], key, problems, brief)

    if isinstance(meta.get("id"), str) and meta["id"] != brief.path.stem:
        problems.append(Problem("id.filename", "id %s must equal the file name %s" % (meta["id"], brief.path.stem)))
    match = ID_PATTERN.match(meta.get("id") or "") if isinstance(meta.get("id"), str) else None
    if match and isinstance(meta.get("date"), str) and meta["date"] != match.group(1):
        problems.append(Problem("date.mismatch", "date %s must equal the id prefix %s" % (meta["date"], match.group(1))))

    status = meta.get("status")
    if status == "running" and not meta.get("runs"):
        problems.append(Problem("status.running_without_runs", "status running requires a non-empty runs list"))
    if status in FINAL_STATUSES and not brief.archived:
        problems.append(Problem("status.final_outside_archive", "status %s is allowed only under archive/; run `brief archive %s`" % (status, brief.id)))
    if brief.archived and status not in FINAL_STATUSES:
        problems.append(Problem("status.archived_not_final", "an archived brief must be done or superseded"))
    if meta.get("supersedes") is not None and isinstance(meta.get("supersedes"), str):
        pool = ids if ids is not None else known_ids(brief.workspace)
        if meta["supersedes"] not in pool:
            problems.append(Problem("supersedes.unknown", "supersedes names %s, which is not a brief in this workspace" % meta["supersedes"]))
        elif meta["supersedes"] == brief.id:
            problems.append(Problem("supersedes.unknown", "a brief cannot supersede itself"))

    scope = brief.scope_write
    for index, item in enumerate(meta.get("deliverables") or []):
        if isinstance(item, dict) and isinstance(item.get("path"), str) and path_problem(item["path"]) is None:
            if not path_in_scope(item["path"], scope):
                problems.append(Problem("deliverable.outside_scope", "deliverables[%d].path %s is not under any scope.write prefix (%s)"
                                        % (index, item["path"], ", ".join(map(str, scope)) or "none")))
    if not meta.get("deliverables") and "deliverables" in meta:
        problems.append(Problem("deliverables.empty", "at least one deliverable is required"))
    if "success_criteria" in meta and not meta.get("success_criteria"):
        problems.append(Problem("success_criteria.empty", "at least one success criterion is required"))
    if "stop_conditions" in meta and not meta.get("stop_conditions"):
        problems.append(Problem("stop_conditions.empty", "at least one stop condition is required"))

    constraints = meta.get("constraints") if isinstance(meta.get("constraints"), dict) else {}
    cap = constraints.get("spend_cap_usd")
    line = DEFAULT_APPROVAL_LINE_USD if approval_line is None else approval_line
    needs = []
    if constraints.get("external_effects") is True:
        needs.append("constraints.external_effects is true")
    if isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > line:
        needs.append("spend_cap_usd %.2f is over the approval line %.2f" % (cap, line))
    approval = meta.get("approval")
    if needs and not isinstance(approval, dict):
        problems.append(Problem("approval.missing", "an approval block (by, at, spend_cap_usd) is required: " + "; ".join(needs)))
    if isinstance(approval, dict) and isinstance(approval.get("spend_cap_usd"), (int, float)) and isinstance(cap, (int, float)):
        if approval["spend_cap_usd"] < cap:
            problems.append(Problem("approval.cap_below_brief", "approval.spend_cap_usd %.2f is below constraints.spend_cap_usd %.2f"
                                    % (approval["spend_cap_usd"], cap)))

    problems.extend(_body_problems(brief))
    return problems


def _body_problems(brief):
    problems = []
    titles = []
    for level, title, number in brief.headings:
        if level != 2 or title not in HEADINGS + (OPTIONAL_HEADING,):
            problems.append(Problem("body.extra_heading", "line %d: heading %r is not allowed; only ## %s and ## %s"
                                    % (number, "#" * level + " " + title, ", ## ".join(HEADINGS), OPTIONAL_HEADING)))
        else:
            titles.append(title)
    expected = list(HEADINGS)
    if titles not in (expected, expected + [OPTIONAL_HEADING]):
        problems.append(Problem("body.headings", "headings must be exactly ## %s in order, then optionally ## %s (found %s)"
                                % (", ## ".join(HEADINGS), OPTIONAL_HEADING, ", ".join(titles) or "none")))
    context = brief.sections.get("Context", "")
    links = [c for c in (brief.meta.get("context") or []) if isinstance(c, str)]
    lines = [line for line in context.split("\n") if line.strip()]
    if any(line.strip().startswith(("```", "~~~")) for line in context.split("\n")):
        problems.append(Problem("context.pasted_code", "## Context holds a fenced block; link to the file instead"))
    elif len(lines) > CONTEXT_MAX_LINES:
        problems.append(Problem("context.too_long", "## Context has %d lines; the limit is %d, one per link" % (len(lines), CONTEXT_MAX_LINES)))
    else:
        for line in lines:
            if not any(link in line for link in links):
                problems.append(Problem("context.not_link", "## Context line %r names no declared context link; add the link to front matter `context`" % line.strip()[:80]))
                break
    corrections = brief.sections.get(OPTIONAL_HEADING, "")
    for line in [l for l in corrections.split("\n") if l.strip()]:
        match = CORRECTION_PATTERN.match(line.strip())
        if not match:
            problems.append(Problem("corrections.format", "correction %r must read '- <date or timestamp> <from>: <text>'" % line.strip()[:80]))
        elif is_identity(match.group(2)):
            problems.append(Problem("corrections.identity", "correction from %r names an agent, session or runtime" % match.group(2)))
    return problems


def approval_line(workspace):
    """[approval] spend_over_usd from the workspace policy, else the default. Stdlib only (tomllib when present)."""
    path = Path(workspace) / ".agents" / "policy.toml"
    if not path.is_file():
        return DEFAULT_APPROVAL_LINE_USD
    text = path.read_text(encoding="utf-8")
    try:
        import tomllib
        return float(tomllib.loads(text).get("approval", {}).get("spend_over_usd", DEFAULT_APPROVAL_LINE_USD))
    except ImportError:
        section = re.search(r"^\[approval\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
        found = re.search(r"^\s*spend_over_usd\s*=\s*([0-9.]+)", section.group(1), re.M) if section else None
        return float(found.group(1)) if found else DEFAULT_APPROVAL_LINE_USD


def all_brief_paths(workspace):
    root = briefs_dir(workspace)
    if not root.is_dir():
        return []
    paths = [p for p in root.glob("*.md") if p.name != "INDEX.md"]
    paths += [p for p in (root / "archive").glob("*/*.md")] if (root / "archive").is_dir() else []
    return sorted(paths)


def find(workspace, brief_id):
    for path in all_brief_paths(workspace):
        if path.stem == brief_id:
            return path
    raise BriefError("no brief %s under %s" % (brief_id, briefs_dir(workspace)))


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def render_index(workspace):
    root = briefs_dir(workspace)
    rows = []
    for path in all_brief_paths(workspace):
        brief = load(path)
        meta = brief.meta if not brief.parse_problems else {}
        status = meta.get("status") if not brief.parse_problems else "invalid"
        runs = meta.get("runs") or []
        rows.append((str(meta.get("date") or path.stem[:10]), path.stem, "| [%s](%s) | %s | %s | %s | %s | %s |" % (
            _cell(path.stem), path.relative_to(root).as_posix(), _cell(meta.get("date") or ""), _cell(meta.get("sender") or ""),
            _cell(status or ""), _cell(meta.get("goal") or ""), _cell(", ".join(map(str, runs))))))
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    lines = ["# Briefs", "", "Generated by `brief index` from the brief files; edits here are discarded on regeneration.", "",
             "| id | date | sender | status | goal | runs |", "|---|---|---|---|---|---|"]
    return "\n".join(lines + [row[2] for row in rows]) + "\n"


def write_index(workspace):
    root = briefs_dir(workspace)
    root.mkdir(parents=True, exist_ok=True)
    text = render_index(workspace)
    target = root / "INDEX.md"
    if not target.exists() or target.read_text(encoding="utf-8") != text:
        tmp = target.with_name(".INDEX.md.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, target)
    return target


def now_ts():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _lock_root(path):
    """The folder whose lock serializes writes to a brief: the workspace's .agents/briefs when it exists."""
    root = briefs_dir(workspace_of(path))
    return root if root.is_dir() else Path(path).resolve().parent


class brief_lock(object):
    """Exclusive lock on the briefs folder (fcntl on the directory itself; no lock files). Re-entrant per process.
    A no-op where fcntl is unavailable."""

    _held = {}
    _guard = threading.RLock()

    def __init__(self, path):
        self.root = str(_lock_root(path))

    def __enter__(self):
        brief_lock._guard.acquire()
        count, fd = brief_lock._held.get(self.root, (0, None))
        if count == 0 and fcntl is not None:
            fd = os.open(self.root, os.O_RDONLY)
            fcntl.flock(fd, fcntl.LOCK_EX)
        brief_lock._held[self.root] = (count + 1, fd)
        return self

    def __exit__(self, *exc):
        count, fd = brief_lock._held[self.root]
        if count == 1:
            del brief_lock._held[self.root]
            if fd is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
        else:
            brief_lock._held[self.root] = (count - 1, fd)
        brief_lock._guard.release()
        return False


def update_fields(path, changes):
    """Rewrite only the named top-level front matter keys of a brief, atomically and under the briefs lock."""
    with brief_lock(path):
        _write_fields(path, changes)


def _write_fields(path, changes):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    front, body, _ = split(text)
    for key, item in changes.items():
        front = set_field(front, key, item)
    parse(front)  # never write front matter this module cannot read back
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text("---\n" + front + "---\n" + body, encoding="utf-8")
    os.replace(tmp, path)


def append_correction(path, line):
    """Append one correction line to ## Corrections (created if absent), under the briefs lock."""
    path = Path(path)
    with brief_lock(path):
        content = path.read_text(encoding="utf-8")
        if "\n## Corrections" not in content:
            content = content.rstrip("\n") + "\n\n## Corrections\n\n" + line + "\n"
        else:
            content = content.rstrip("\n") + "\n" + line + "\n"
        tmp = path.with_name("." + path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def live_runs_of(brief):
    """Run ids listed by the brief whose run.json is not in a terminal state."""
    live = []
    for run_id in brief.meta.get("runs") or []:
        try:
            run = json.loads((brief.workspace / ".agents" / "runs" / str(run_id) / "run.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if run.get("state") not in ("done", "failed", "stopped"):
            live.append(run_id)
    return live


def archive(workspace, brief_id, status="done", at=None):
    """Move a finished brief to archive/YYYY/, set archived_at, flip a superseded target, regenerate the index.
    Refuses an invalid brief and a brief whose runs are still live."""
    if status not in FINAL_STATUSES:
        raise BriefError("archive status must be done or superseded")
    with brief_lock(briefs_dir(workspace) / "x.md"):
        source = find(workspace, brief_id)
        brief = load(source)
        if brief.parse_problems:
            raise BriefError("%s does not parse: %s" % (source, brief.parse_problems[0]))
        if brief.archived:
            raise BriefError("%s is already archived" % brief_id)
        problems = [p for p in validate(brief, approval_line(workspace)) if not p.rule.startswith("status.")]
        if problems:
            raise BriefError("%s is invalid; fix it before archiving: %s" % (brief_id, "; ".join(map(str, problems))))
        live = live_runs_of(brief)
        if live:
            raise BriefError("%s still has live runs (%s); stop them or wait for them to end" % (brief_id, ", ".join(live)))
        at = at or now_ts()
        moved = _move_to_archive(workspace, source, brief, status, at)
        target_id = brief.meta.get("supersedes")
        if isinstance(target_id, str):
            target_path = find(workspace, target_id)
            target = load(target_path)
            if target.archived:
                _write_fields(target_path, {"status": "superseded"})
            else:
                _move_to_archive(workspace, target_path, target, "superseded", at)
        write_index(workspace)
        return moved


def _move_to_archive(workspace, source, brief, status, at):
    """Move first, then set status and archived_at, so a failure never leaves a final status outside archive/."""
    year = str(brief.meta.get("date") or brief.id or "")[:4]
    if not re.match(r"^\d{4}$", year):
        raise BriefError("cannot derive the archive year of %s" % source)
    folder = briefs_dir(workspace) / "archive" / year
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / source.name
    if destination.exists():
        raise BriefError("%s already exists" % destination)
    os.replace(source, destination)
    try:
        _write_fields(destination, {"status": status, "archived_at": at})
    except Exception:
        os.replace(destination, source)
        raise
    return destination


SKELETON_BODY = """
## Goal

State the outcome in a few sentences; the one-sentence version is `goal` above.

## Context

## Deliverables

Describe each deliverable listed in front matter.

## Report-back

Write HANDOFF.md in the run folder with the collaboration return headings.
"""


def new(workspace, slug, sender, date=None):
    """Write a skeleton brief. It fails `check` only on goal, deliverables and success_criteria until filled."""
    if is_identity(sender):
        raise BriefError("sender %r names an agent, session or runtime" % sender)
    date = date or datetime.date.today().isoformat()
    brief_id = "%s-%s" % (date, slug)
    if not ID_PATTERN.match(brief_id):
        raise BriefError("slug must match [a-z0-9-]{3,48} and date YYYY-MM-DD")
    root = briefs_dir(workspace)
    root.mkdir(parents=True, exist_ok=True)
    if brief_id in known_ids(workspace):
        raise BriefError("brief %s already exists" % brief_id)
    meta = {
        "id": brief_id, "date": date, "sender": sender, "goal": "", "status": "open", "context": [],
        "scope": {"in": [], "out": [], "write": []},
        "constraints": {"spend_cap_usd": 1.0, "wall_clock_s": 3600, "no_push": True, "no_merge": True, "external_effects": False},
        "deliverables": [], "success_criteria": [], "stop_conditions": list(DEFAULT_STOP_CONDITIONS),
        "report_back": {"handoff": "HANDOFF.md"},
    }
    path = root / (brief_id + ".md")
    with path.open("x", encoding="utf-8") as handle:
        handle.write("---\n" + dump(meta) + "---\n" + SKELETON_BODY)
    write_index(workspace)
    return path


def check_paths(paths, workspace=None, line=None):
    """Validate brief files. Returns {path: [Problem]}."""
    out = {}
    for path in paths:
        path = Path(path)
        ws = Path(workspace) if workspace else workspace_of(path)
        out[path] = validate(load(path), approval_line(ws) if line is None else line)
    return out


def brief_main(argv=None, prog="luma brief", approval_line_for=None):
    parser = argparse.ArgumentParser(prog=prog, description="Check, index, archive and create brief files.")
    parser.add_argument("--workspace", default=".", help="workspace root holding .agents/briefs (default: current folder)")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="validate briefs; exit 1 listing every error")
    check.add_argument("paths", nargs="*", help="brief files (default: every brief in the workspace)")
    check.add_argument("--json", action="store_true")
    sub.add_parser("index", help="regenerate .agents/briefs/INDEX.md")
    arch = sub.add_parser("archive", help="move a finished brief to archive/YYYY/")
    arch.add_argument("id")
    arch.add_argument("--status", choices=FINAL_STATUSES, default="done")
    make = sub.add_parser("new", help="write a skeleton brief")
    make.add_argument("slug")
    make.add_argument("--sender", required=True)
    make.add_argument("--date")
    args = parser.parse_args(argv)
    workspace = Path(args.workspace).resolve()
    try:
        if args.command == "check":
            paths = [Path(p) for p in args.paths] or all_brief_paths(workspace)
            if not paths:
                print("no briefs under %s" % briefs_dir(workspace))
                return 0
            results = {}
            for path in paths:
                ws = workspace_of(path) if args.paths else workspace
                line = approval_line_for(ws) if approval_line_for else approval_line(ws)
                results[path] = validate(load(path), line)
            if args.json:
                print(json.dumps({str(p): [{"rule": x.rule, "message": x.message} for x in probs] for p, probs in results.items()}, indent=1))
            else:
                for path, probs in results.items():
                    for problem in probs:
                        print("%s: %s" % (path, problem))
                bad = sum(1 for probs in results.values() if probs)
                print("%d brief(s) checked, %d with errors" % (len(results), bad), file=sys.stderr)
            return 1 if any(results.values()) else 0
        if args.command == "index":
            print(write_index(workspace))
            return 0
        if args.command == "archive":
            print(archive(workspace, args.id, args.status))
            return 0
        if args.command == "new":
            print(new(workspace, args.slug, args.sender, args.date))
            return 0
    except (BriefError, FrontMatterError, OSError) as error:
        print("error: %s" % error, file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(brief_main(prog="luma_brief.py"))

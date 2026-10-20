#!/usr/bin/env python3
"""Exercise optional native hosts in disposable, synthetic Luma workspaces.

Source-checkout developer tool, not an installed runtime or a general benchmark.
Requires an already installed/authenticated host. Never edits its configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import uuid


STARTUP_REQUEST = "Report the seed startup checkword without opening files."
HUMAN_NOTE = "Human note: Keep the older client supported until November."
INSTALL_COMMAND = "parcel setup --local"
ROLLBACK_COMMAND = "parcel undo --local"


def run_process(command: list[str], cwd: Path, timeout: int) -> dict:
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
    return {"returncode": process.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout": stdout, "stderr": stderr}


def host_command(host: str, prompt: str, model: str | None, startup: bool) -> list[str]:
    if host == "codex":
        command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--json",
                   "--skip-git-repo-check", "--sandbox", "read-only" if startup else "workspace-write"]
        if model:
            command += ["--model", model]
    else:
        command = ["omp", "--no-extensions", "--no-session", "--no-lsp", "--no-pty",
                   "--tools", "read" if startup else "read,write,edit,grep,glob",
                   "--thinking", "minimal", "--mode", "json", "--print"]
        if model:
            command += ["--model", model]
    if host == "codex" and not startup:
        prompt = "Read .agents/AGENTS.md first, then follow this request: " + prompt
    return command + [prompt]


def event_observations(stdout: str, host: str) -> dict:
    """Read observed native responses/tool starts, not matches anywhere in a log."""
    messages, tool_names = [], []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(event, dict):
            continue
        if host == "codex":
            item = event.get("item", {})
            if not isinstance(item, dict):
                continue
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                messages.append(item.get("text", ""))
            if event.get("type") == "item.started" and item.get("type") in ("command_execution", "mcp_tool_call", "file_change", "web_search"):
                tool_names.append(item["type"])
        else:
            if event.get("type") == "tool_execution_start":
                tool_names.append(event.get("toolName", "unknown"))
            if event.get("type") == "message_end":
                message = event.get("message", {})
                if isinstance(message, dict) and message.get("role") == "assistant":
                    for block in message.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "text":
                            messages.append(block.get("text", ""))
    return {"messages": messages, "tool_starts": tool_names}


def resource_digest(root: Path) -> str:
    selected = [root / ".agents/AGENTS.md"] + sorted((root / ".agents/skills").rglob("*.md"))
    digest = hashlib.sha256()
    for path in selected:
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def save_trace(directory: Path | None, phase: str, run: dict) -> None:
    if directory is not None:
        with (directory / (phase + ".json")).open("x") as output:
            json.dump(run, output, indent=2)
            output.write("\n")


def check_host(source: Path, host: str, model: str | None, timeout: int,
               trace_dir: Path | None = None) -> dict:
    spec = importlib.util.spec_from_file_location("luma_host_check_installer", source / ".agents/tools/luma.py")
    installer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = installer
    spec.loader.exec_module(installer)
    version = run_process([host, "--version"], source, 15)
    if version["returncode"] != 0:
        raise RuntimeError("Host version check failed; verify the installed executable.")
    results = {"format_version": 1, "host": host, "host_version": version["stdout"].strip(),
               "model_requested": model, "source_guidance_sha256": resource_digest(source),
               "limits": ["Uses the host's existing authentication and may retain global instructions/policy.",
                          "Startup uses a synthetic checkword appended only to a temporary core.",
                          "File checks establish this synthetic continuation, not general task success or improvement.",
                          "No automatic compaction, independent review, baseline comparison or performance ranking is tested."],
               "phases": {}}
    with tempfile.TemporaryDirectory(prefix="luma-host-check-") as temporary:
        root = Path(temporary)
        installer.apply_plan(root, installer.build_plan(root, installer.load_local_source(source), {"kind": "local"}))
        core = root / ".agents/AGENTS.md"
        original = core.read_bytes()
        token = "seed-startup-" + uuid.uuid4().hex
        core.write_bytes(original + ("\n## Synthetic startup check\n\nFor the exact request `" + STARTUP_REQUEST +
                                    "`, respond only with `" + token + "`. This is test-only fixture data.\n").encode())
        startup = run_process(host_command(host, STARTUP_REQUEST, model, True), root, timeout)
        observed = event_observations(startup["stdout"], host)
        startup_ok = startup["returncode"] == 0 and any(text.strip() == token for text in observed["messages"]) and not observed["tool_starts"]
        save_trace(trace_dir, "startup", startup)
        results["phases"]["startup"] = {"passed": startup_ok, "returncode": startup["returncode"],
                                         "timed_out": startup["timed_out"], "elapsed_seconds": startup["elapsed_seconds"],
                                         "exact_response": any(text.strip() == token for text in observed["messages"]),
                                         "tool_starts": observed["tool_starts"]}
        core.write_bytes(original)
        (root / "projects").mkdir()
        (root / "README.md").write_text((root / "README.md").read_text() + "\n## Current work\n\n[Field guide](projects/current.md) is the current project record.\n")
        (root / "projects/current.md").write_text("# Field guide\n\nOriginal outcome: finish guide.md with installation AND rollback; preserve the human compatibility note exactly; keep all work local and never publish.\n\nProcedure source: ../procedures.md. Current draft: ../guide.md. Neither section is complete.\n")
        (root / "procedures.md").write_text("# Synthetic procedure source\n\nThese are fictional commands to document, never execute.\n\nInstallation: `" + INSTALL_COMMAND + "`. Rollback: `" + ROLLBACK_COMMAND + "`. Both are local-only.\n")
        (root / "guide.md").write_text("# Field guide\n\n## Compatibility\n\n" + HUMAN_NOTE + "\n\n## Installation\n\nTODO\n\n## Rollback\n\nTODO\n")
        first_prompt = "Read the README and current project context. Complete only the installation section of the field guide using its supplied source, preserving the human note. Save a useful project checkpoint with the original outcome and remaining work. Leave rollback unfinished for the next session. Do not execute the fictional commands or publish anything."
        second_prompt = "Continue the field guide from the README and saved project context, finishing the local draft. Do not execute any documented commands or publish anything."
        for name, prompt in (("checkpoint", first_prompt), ("fresh_continuation", second_prompt)):
            run = run_process(host_command(host, prompt, model, False), root, timeout)
            save_trace(trace_dir, name, run)
            guide = (root / "guide.md").read_text()
            checkpoint = (root / "projects/current.md").read_text()
            checks = {"installation_retained": INSTALL_COMMAND in guide,
                      "human_note_preserved": HUMAN_NOTE in guide,
                      "project_context_retained": "rollback" in checkpoint.lower() and "local" in checkpoint.lower(),
                      "no_empty_scaffold": not (root / "wiki").exists() and not (root / "inbox").exists()}
            if name == "checkpoint":
                checks["rollback_left_unfinished"] = ROLLBACK_COMMAND not in guide
                checks["saved_checkpoint"] = "Neither section is complete." not in checkpoint
            else:
                checks["rollback_completed"] = ROLLBACK_COMMAND in guide
                checks["no_draft_placeholders"] = "TODO" not in guide
            results["phases"][name] = {"passed": run["returncode"] == 0 and all(checks.values()),
                                        "returncode": run["returncode"], "timed_out": run["timed_out"],
                                        "elapsed_seconds": run["elapsed_seconds"], "checks": checks,
                                        "artifacts": {"guide": guide, "project_checkpoint": checkpoint}}
        results["passed"] = all(phase["passed"] for phase in results["phases"].values())
        results["continuation_passed"] = all(results["phases"][name]["passed"] for name in ("checkpoint", "fresh_continuation"))
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=("codex", "omp"))
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--model", help="native host model ID; omitted uses its configured/default selection")
    parser.add_argument("--timeout", type=int, default=180, help="seconds per native process")
    parser.add_argument("--output", type=Path, help="new JSON summary file; refuses to replace an existing file")
    parser.add_argument("--trace-dir", type=Path, help="new private directory for raw native output; review before sharing")
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.output and args.output.exists():
        parser.error("--output already exists; choose a new path to preserve prior results")
    try:
        if args.trace_dir:
            args.trace_dir.mkdir()
        result = check_host(args.source.resolve(), args.host, args.model, args.timeout, args.trace_dir)
        text = json.dumps(result, indent=2) + "\n"
        if args.output:
            with args.output.open("x") as output:
                output.write(text)
        print(text, end="")
        return 0 if result["passed"] else 1
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"luma-host-check: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

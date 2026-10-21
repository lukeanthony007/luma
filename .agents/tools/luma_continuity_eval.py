#!/usr/bin/env python3
"""Run a private staged project comparison; never publish its case or outputs automatically."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_case(case):
    if not isinstance(case, dict) or type(case.get("format_version")) is not int or case["format_version"] not in (1, 2):
        raise ValueError("Expected case format_version 1 or 2")
    version = case["format_version"]
    effort = case.get("reasoning_effort", "minimal")
    if not isinstance(effort, str) or effort not in ("minimal", "low", "medium", "high"):
        raise ValueError("Expected reasoning_effort minimal, low, medium, or high")
    for key in ("repetitions", "timeout_seconds"):
        if type(case.get(key)) is not int or case[key] < 1:
            raise ValueError("Expected positive integer " + key)
    for key in ("model", "readme", "common_prompt"):
        if not isinstance(case.get(key), str) or not case[key].strip():
            raise ValueError("Expected nonempty " + key)
    seen_ids, seen_paths = set(), {}
    for group in ("stages", "probes"):
        if not isinstance(case.get(group), list) or not case[group]:
            raise ValueError("Expected nonempty " + group)
        for item in case[group]:
            if not isinstance(item, dict):
                raise ValueError("Stages and probes must be objects")
            identifier = item.get("id", "")
            if not isinstance(identifier, str) or not identifier or not all(c.isascii() and (c.isalnum() or c in "-_") for c in identifier) or identifier in seen_ids:
                raise ValueError("Case IDs must be unique safe names")
            seen_ids.add(identifier)
            if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
                raise ValueError("Expected nonempty prompt")
            files = item.get("files", {})
            if not isinstance(files, dict):
                raise ValueError("Files must be an object")
            if group == "probes" and files and version == 1:
                raise ValueError("Probes may not add evidence; put new evidence in a stage")
            for name, text in files.items():
                if not isinstance(name, str) or not isinstance(text, str):
                    raise ValueError("Sources must map safe paths to text")
                parts = name.split("/")
                if (not name.startswith("inputs/") or name.startswith("/") or "\\" in name or ":" in name
                        or any(p in ("", ".", "..") for p in parts)
                        or parts[:2] in (["inputs", "requests"], ["inputs", "history"])):
                    raise ValueError("Sources must have safe paths under inputs/, outside reserved directories")
                for prior in seen_paths:
                    if name == prior:
                        if version != 2:
                            raise ValueError("Duplicate source paths require format_version 2")
                    elif name.startswith(prior + "/") or prior.startswith(name + "/"):
                        raise ValueError("Source paths may not conflict as parent and child")
                seen_paths[name] = group


def stage_inputs(root, stage, number, put_files, version=1, manifest=None):
    """Stage a transition before invocation, preserving replaced evidence for every arm."""
    incoming = stage.get("files", {})
    request = f"inputs/requests/{number:02d}-{stage['id']}.txt"
    manifest_path = "inputs/history/manifest.json"
    pending = {}
    transitions = []

    def check_target(name, exclusive=False):
        target = root / name
        for path in (target, *target.parents):
            if path == root:
                break
            if path.is_symlink():
                raise ValueError("Evidence paths may not traverse symlinks")
            if path != target and path.exists() and not path.is_dir():
                raise ValueError("Evidence parent conflicts with a file")
        if target.exists() and (exclusive or not target.is_file()):
            raise ValueError("Evidence archive/request already exists or conflicts with a directory")
        return target

    # Preflight every destination before writing any part of this transition.
    check_target(request, exclusive=True)
    for name, text in incoming.items():
        path = check_target(name)
        data = text.encode("utf-8")
        old = path.read_bytes() if path.exists() else None
        if old == data:
            continue
        archived_path = None
        if old is not None:
            if version != 2:
                raise ValueError("Replacing source bytes requires format_version 2")
            archived_path = f"inputs/history/{number:02d}-{stage['id']}/" + name[len("inputs/"):]
            check_target(archived_path, exclusive=True)
            pending[archived_path] = old
        transitions.append({"stage_id": stage["id"], "sequence": number, "path": name,
                            "previous_sha256": hashlib.sha256(old).hexdigest() if old is not None else None,
                            "current_sha256": hashlib.sha256(data).hexdigest(),
                            "archived_path": archived_path,
                            "transition": "replaced" if old is not None else "added"})
    if version == 2 and transitions:
        check_target(manifest_path)
    for name, data in pending.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    put_files(root, incoming)
    if version == 2 and transitions:
        updated_manifest = list(manifest or []) + transitions
        put_files(root, {manifest_path: json.dumps(updated_manifest, indent=2) + "\n"})
        if manifest is not None:
            manifest[:] = updated_manifest
    put_files(root, {request: stage["prompt"] + "\n"})


def retained_records(files, original):
    return {name: data.decode("utf-8", errors="replace") for name, data in files.items()
            if not name.startswith("inputs/") and original.get(name) != data}


def compare(source, case_path, output_dir):
    if output_dir.exists():
        raise ValueError("Output directory must be new; retained evidence is never overwritten")
    case_bytes = case_path.read_bytes()
    case = json.loads(case_bytes)
    validate_case(case)
    tools = source / ".agents/tools"
    matched = load_module("continuity_matched_helpers", tools / "luma_matched_eval.py")
    host = load_module("continuity_host_helpers", tools / "luma_host_check.py")
    installer = load_module("continuity_installer", tools / "luma.py")
    version = host.run_process(["omp", "--version"], source, 15)
    if version["returncode"]:
        raise RuntimeError("OMP version check failed")
    output_dir.mkdir(parents=True, mode=0o700)
    traces = output_dir / "traces"
    traces.mkdir(mode=0o700)
    effort = case.get("reasoning_effort", "minimal")
    result = {"format_version": 1, "case_sha256": matched.digest(case_bytes),
              "runner_sha256": matched.digest(Path(__file__).read_bytes()),
              "guidance_sha256": host.resource_digest(source), "host_version": version["stdout"].strip(),
              "model_requested": case["model"], "reasoning_effort": effort,
              "command_without_prompt": matched.command(case["model"], "", effort)[:-1],
              "loading": {}, "runs": [], "chain_errors": [],
              "scope": "Private project excerpts and scripted episodes; no live project execution. Source-only receives originals and requests, not agent-authored records. Semantic scoring is separate."}

    def save(name, value):
        (output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="luma-continuity-") as temporary:
        temporary = Path(temporary)
        bases = {}
        for arm in ("stock", "luma"):
            root = temporary / ("base-" + arm)
            root.mkdir()
            if arm == "luma":
                installer.apply_plan(root, installer.build_plan(root, installer.load_local_source(source), {"kind": "local"}))
                core = root / ".agents/AGENTS.md"
                original_core = core.read_bytes()
                core.write_bytes(original_core + b"\n## Temporary delivery probe\n\nThe synthetic startup checkword is CONTINUITY-CORE-LOADED.\n")
            probe = host.run_process(matched.command(case["model"], "Without tools, return the checkword defined by a synthetic startup directive, or ABSENT if none is available.", effort), root, case["timeout_seconds"])
            (traces / (arm + "-loading.json")).write_text(json.dumps(probe, indent=2) + "\n")
            observed = host.event_observations(probe["stdout"], "omp")
            wanted = "CONTINUITY-CORE-LOADED" if arm == "luma" else "ABSENT"
            result["loading"][arm] = {"passed": probe["returncode"] == 0 and not observed["tool_starts"] and any(m.strip() == wanted for m in observed["messages"]), "messages": observed["messages"]}
            if arm == "luma":
                core.write_bytes(original_core)
            (root / "README.md").write_text(case["readme"], encoding="utf-8")
            bases[arm] = root
        if not all(item["passed"] for item in result["loading"].values()):
            save("results.json", result)
            raise RuntimeError("Delivery check failed; no project runs started")

        def invoke(root, original, arm, repetition, item, phase, new_sources=None):
            before = matched.snapshot(root)
            prompt = case["common_prompt"] + "\n\n" + item["prompt"]
            if new_sources:
                prompt += "\n\nNew or revised source extracts: " + ", ".join(sorted(new_sources))
            run_id = f"{arm}-{repetition}-{item['id']}"
            native = host.run_process(matched.command(case["model"], prompt, effort), root, case["timeout_seconds"])
            (traces / (run_id + ".json")).write_text(json.dumps(native, indent=2) + "\n")
            after = matched.snapshot(root)
            metrics, messages = matched.metrics(native["stdout"], host)
            changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
            protected = [name for name in before if name.startswith("inputs/") or (name.startswith(".agents/") and name in original)]
            checks = {"protected_inputs_and_seed_unchanged": all(before[name] == after.get(name) for name in protected),
                      "no_input_additions": not any(name.startswith("inputs/") and name not in before for name in after),
                      "no_installed_tool_or_skill_additions": not any(name.startswith((".agents/tools/", ".agents/skills/")) and name not in before for name in after),
                      "completed_response": native["returncode"] == 0 and bool(messages)}
            reads = []
            for line in native["stdout"].splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if isinstance(event, dict) and event.get("type") == "tool_execution_start" and event.get("toolName") == "read":
                    reads.append(event.get("args", {}).get("path"))
            record = {"id": run_id, "arm": arm, "repetition": repetition, "task": item["id"], "phase": phase,
                      "returncode": native["returncode"], "timed_out": native["timed_out"],
                      "elapsed_seconds": native["elapsed_seconds"], "mechanical_checks": checks,
                      "metrics": metrics, "messages": messages, "read_paths": reads,
                      "changed_files": changed, "retained_records": retained_records(after, original),
                      "input_sha256": {name: matched.digest(data) for name, data in before.items()},
                      "trace_sha256": matched.digest(native["stdout"].encode())}
            save(run_id + ".json", record)
            print(run_id + ": " + ("complete" if all(checks.values()) else "CHECK FAILED"), flush=True)
            return record

        def chain(arm, repetition):
            records = []
            root = temporary / f"{arm}-{repetition}"
            shutil.copytree(bases[arm if arm == "luma" else "stock"], root)
            original = matched.snapshot(root)
            manifest = []
            for number, stage in enumerate(case["stages"], 1):
                stage_inputs(root, stage, number, matched.put_files, case["format_version"], manifest)
                if arm != "source-only":
                    records.append(invoke(root, original, arm, repetition, stage, "acquisition", stage.get("files")))
            for number, probe in enumerate(case["probes"], len(case["stages"]) + 1):
                # Fork each probe from the same acquisition state; probes cannot teach each other.
                probe_root = temporary / f"{arm}-{repetition}-probe-{probe['id']}"
                shutil.copytree(root, probe_root)
                if case["format_version"] == 2:
                    stage_inputs(probe_root, probe, number, matched.put_files, 2, list(manifest))
                records.append(invoke(probe_root, original, arm, repetition, probe, "application", probe.get("files")))
            save(f"{arm}-{repetition}-retained-before-probes.json", retained_records(matched.snapshot(root), original))
            return records

        with ThreadPoolExecutor(max_workers=3) as pool:
            for repetition in range(1, case["repetitions"] + 1):
                arms = ("stock", "luma", "source-only") if repetition % 2 else ("source-only", "luma", "stock")
                futures = [(arm, pool.submit(chain, arm, repetition)) for arm in arms]
                for arm, future in futures:
                    try:
                        result["runs"].extend(future.result())
                    except Exception as error:
                        # Completed per-run files remain available, including when a later step fails.
                        result["chain_errors"].append({"arm": arm, "repetition": repetition, "error_type": type(error).__name__, "error": str(error)})
                    save("results.json", result)
    save("results.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.source.resolve(), args.case.resolve(), args.output_dir.resolve())
    print(json.dumps({"runs": len(result["runs"]), "chain_errors": len(result["chain_errors"])}))
    return 1 if result["chain_errors"] or not all(r["returncode"] == 0 and not r["timed_out"] and all(r["mechanical_checks"].values()) for r in result["runs"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())

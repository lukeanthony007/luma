#!/usr/bin/env python3
"""Developer-only matched OMP comparison. Raw traces stay in an explicit local directory."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def put_files(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def command(model, prompt, reasoning_effort="minimal"):
    return ["omp", "--no-extensions", "--no-skills", "--no-rules", "--no-session",
            "--no-lsp", "--no-pty", "--no-title", "--no-prewalk", "--tools",
            "read,write,edit,grep,glob", "--thinking", reasoning_effort, "--mode", "json",
            "--print", "--model", model, prompt]


def metrics(stdout, host_helper):
    observations = host_helper.event_observations(stdout, "omp")
    counts = {"assistant_messages": 0, "input_tokens": 0, "output_tokens": 0,
              "cache_read_tokens": 0, "cache_write_tokens": 0}
    usage_messages = 0
    models = set()
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("type") != "message_end":
            continue
        message = event.get("message", {})
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        counts["assistant_messages"] += 1
        if isinstance(message.get("model"), str):
            models.add(message["model"])
        usage = message.get("usage")
        if isinstance(usage, dict):
            usage_messages += 1
            for native, key in (("input", "input_tokens"), ("output", "output_tokens"),
                                ("cacheRead", "cache_read_tokens"), ("cacheWrite", "cache_write_tokens")):
                value = usage.get(native)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    counts[key] += value
    counts["usage_messages"] = usage_messages
    counts["observed_models"] = sorted(models)
    counts["tool_calls"] = len(observations["tool_starts"])
    counts["tool_names"] = observations["tool_starts"]
    return counts, observations["messages"]


def equal_json(actual, expected):
    """Avoid Python's True == 1 conflation for typed task outputs."""
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def grade(before, after, task, messages):
    expected = task.get("expected", {})
    checks = {"protected:" + name: after.get(name) == before.get(name)
              for name in task.get("protected", [])}
    for name in before:
        if name.startswith(".agents/"):
            checks["seed_unchanged"] = checks.get("seed_unchanged", True) and before[name] == after.get(name)
    checks["no_seed_additions"] = not any(name.startswith((".agents/tools/", ".agents/skills/")) and name not in before for name in after)
    for name in expected.get("changed", []):
        checks["changed:" + name] = name in after and after[name] != before.get(name)
    for name, text in expected.get("preserved_text", {}).items():
        checks["preserved_text:" + name] = text in after.get(name, b"").decode(errors="replace")
    if expected.get("no_writes"):
        checks["no_writes"] = before == after
    if "answer_contains" in expected:
        checks["direct_answer"] = any(expected["answer_contains"] in text for text in messages)
    artifact = expected.get("artifact")
    if artifact:
        try:
            value = json.loads(after[artifact])
            checks["valid_json"] = True
        except (KeyError, ValueError, UnicodeError):
            value = None
            checks["valid_json"] = False
        if "json" in expected:
            checks["exact_json"] = equal_json(value, expected["json"])
        for key, wanted in expected.get("fields", {}).items():
            checks["field:" + key] = isinstance(value, dict) and key in value and equal_json(value[key], wanted)
        if "condition_terms" in expected:
            condition = value.get("condition") if isinstance(value, dict) else None
            checks["condition_present"] = isinstance(condition, str) and all(term in condition.lower() for term in expected["condition_terms"])
        if artifact == "answer.json":
            checks["reason_present"] = isinstance(value, dict) and isinstance(value.get("reason"), str) and bool(value["reason"].strip())
    return checks


def execute(root, run_id, task, fixture, trace_root, helper):
    before = snapshot(root)
    prompt = task["prompt"] if task["id"] == "simple" else fixture["common_prompt"] + "\n\n" + task["prompt"]
    result = helper.run_process(command(fixture["model"], prompt), root, fixture["timeout_seconds"])
    (trace_root / (run_id + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    after = snapshot(root)
    counts, messages = metrics(result["stdout"], helper)
    checks = grade(before, after, task, messages)
    changes = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    artifacts = {name: data.decode(errors="replace") for name, data in after.items()
                 if not name.startswith(".agents/") and name != ".gitignore"}
    return {"id": run_id, "task": task["id"], "returncode": result["returncode"],
            "timed_out": result["timed_out"], "elapsed_seconds": result["elapsed_seconds"],
            "mechanical_pass": result["returncode"] == 0 and all(checks.values()),
            "checks": checks, "metrics": counts, "changed_files": changes,
            "artifacts": artifacts, "assistant_messages": messages,
            "before_sha256": {name: digest(data) for name, data in before.items()},
            "trace_sha256": digest(result["stdout"].encode())}


def run(source, fixture_path, output, trace_root):
    if output.exists() or trace_root.exists():
        raise ValueError("Output and raw trace directory must both be new paths.")
    fixture_bytes = fixture_path.read_bytes()
    fixture = json.loads(fixture_bytes)
    helper = load_module("matched_host_helper", source / ".agents/tools/luma_host_check.py")
    installer = load_module("matched_installer", source / ".agents/tools/luma.py")
    version = helper.run_process(["omp", "--version"], source, 15)
    if version["returncode"] != 0:
        raise RuntimeError("OMP version check failed.")
    trace_root.mkdir(parents=True)
    summary = {"format_version": 1, "host_version": version["stdout"].strip(),
               "model_requested": fixture["model"], "fixture_sha256": digest(fixture_bytes),
               "runner_sha256": digest(Path(__file__).read_bytes()),
               "guidance_sha256": helper.resource_digest(source),
               "command_without_prompt": command(fixture["model"], "")[:-1],
               "runs": [], "loading": {}}
    with tempfile.TemporaryDirectory(prefix="luma-matched-") as temporary:
        temporary = Path(temporary)
        bases = {}
        for arm in ("stock", "luma"):
            root = temporary / arm
            root.mkdir()
            if arm == "luma":
                installer.apply_plan(root, installer.build_plan(root, installer.load_local_source(source), {"kind": "local"}))
                core = root / ".agents/AGENTS.md"
                original = core.read_bytes()
                core.write_bytes(original + b"\n## Synthetic startup directive\n\nThe synthetic startup checkword is MATCHED-SEED-LOADED.\n")
            probe = helper.run_process(command(fixture["model"], "Without tools, return the checkword defined by a synthetic startup directive, or ABSENT if none is available."), root, fixture["timeout_seconds"])
            (trace_root / (arm + "-loading.json")).write_text(json.dumps(probe, indent=2) + "\n")
            observed = helper.event_observations(probe["stdout"], "omp")
            wanted = "MATCHED-SEED-LOADED" if arm == "luma" else "ABSENT"
            summary["loading"][arm] = {"passed": probe["returncode"] == 0 and not observed["tool_starts"] and any(m.strip() == wanted for m in observed["messages"]), "messages": observed["messages"]}
            if arm == "luma":
                core.write_bytes(original)
            bases[arm] = root
        if not all(value["passed"] for value in summary["loading"].values()):
            with output.open("x") as stream:
                json.dump(summary, stream, indent=2)
            raise RuntimeError("Loading check failed; no task comparison run.")

        def work(arm, repetition):
            records = []
            def workspace(label, files, parent=None):
                destination = temporary / (arm + "-" + str(repetition) + "-" + label)
                shutil.copytree(parent or bases[arm], destination)
                put_files(destination, files)
                return destination

            def perform(root, task, label):
                record = execute(root, arm + "-" + str(repetition) + "-" + label, task, fixture, trace_root, helper)
                record.update(arm=arm, repetition=repetition)
                records.append(record)
                # Keep completed records recoverable if a later native process or filesystem step fails.
                (trace_root / (record["id"] + "-summary.json")).write_text(json.dumps(record, indent=2) + "\n")
                print(record["id"] + ": " + ("PASS" if record["mechanical_pass"] else "FAIL"), flush=True)

            for task in fixture["tasks"]:
                perform(workspace(task["id"], task["files"]), task, task["id"])
            learning = fixture["learning"]
            trained = workspace("training", learning["files"])
            perform(trained, {"id": "training", "prompt": learning["training_prompt"],
                              "protected": learning["protected"], "expected": {"changed": ["method.md"]}}, "training")
            for condition in ("with_lesson", "without_lesson"):
                for transfer in learning["transfers"]:
                    files = {"receipt.json": json.dumps(transfer["receipt"]) + "\n"}
                    files["method.md"] = (trained / "method.md").read_text() if condition == "with_lesson" else learning["files"]["method.md"]
                    root = workspace(condition + "-" + transfer["id"], files)
                    # Transfer only the authored method, not the original episode or conversation.
                    (root / "README.md").write_text("# Current receipt\n\nRead [method.md](method.md), then [receipt.json](receipt.json). Write answer.json. Use other project records when needed.\n")
                    before_files = [name for name in snapshot(root) if not name.startswith(".agents/") and name != ".gitignore"]
                    task = {"id": condition + "-" + transfer["id"], "prompt": transfer["prompt"],
                            "protected": before_files,
                            "expected": {"artifact": "answer.json", "fields": {"item_count": transfer["expected_" + condition]}}}
                    perform(root, task, task["id"])
            return records

        # Two concurrent arms share the same machine/provider; elapsed time is descriptive only.
        with ThreadPoolExecutor(max_workers=2) as pool:
            for repetition in range(1, fixture["repetitions"] + 1):
                arms = ("stock", "luma") if repetition % 2 else ("luma", "stock")
                futures = [pool.submit(work, arm, repetition) for arm in arms]
                for future in futures:
                    summary["runs"].extend(future.result())
    with output.open("x") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--fixtures", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trace-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    fixtures = args.fixtures or source / ".agents/tools/tests/fixtures/matched_seed_tasks.json"
    summary = run(source, fixtures, args.output, args.trace_dir)
    print(json.dumps({"runs": len(summary["runs"]), "mechanical_passes": sum(run["mechanical_pass"] for run in summary["runs"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

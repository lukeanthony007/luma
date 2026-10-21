# Native host conformance

This is a bounded operational check of the [portable seed](DESIGN.md), following the earlier [prompt-only checks](SEED-CHECKS.md). It exercises already installed hosts in disposable synthetic workspaces. It is not a performance benchmark or permission to configure a user's installed workspace.

## What is checked

The source-checkout developer tool [luma_host_check.py](../.agents/tools/luma_host_check.py) performs three native invocations. It is deliberately not part of the initializer's installed resource set and introduces no runtime dependency for ordinary Luma use.

1. **Startup:** append a random synthetic checkword directive to the temporary core. Ask for that word without permitting file inspection. An exact native assistant response with no observed tool starts supports startup delivery in that configuration. A word merely found in a tool result is not a pass. Restore the unmodified installed core before ordinary work.
2. **Checkpoint:** provide a project with an original installation-and-rollback goal, a human compatibility note and a fictional procedure source. Ask the host to finish only installation, save current project context and leave rollback pending.
3. **Fresh continuation:** start a new native process with no resumed conversation. Ask it to continue from README and saved context. Inspect actual files for both procedures, the preserved human note, a useful checkpoint and absence of draft placeholders or unwanted wiki/inbox scaffolding.

The checks use real file writes, not the assistant's completion claim. The later request does not repeat the original rollback requirement; it must be recovered from retained workspace material. The task is intentionally synthetic: the fictional commands must be documented, never executed or published.

Each native process has a deadline. A timeout stops its owned process group and is retained as a failed phase, not a successful continuation. Output summaries retain the actual synthetic guide and checkpoint so their meaning can be reviewed beyond the mechanical checks.

## Run from a source checkout

Requires Python 3.9+, Linux/POSIX process-group support, and an installed, authenticated `codex` or `omp`. No dependency installation, login, native configuration change or background service is performed by this tool.

```sh
python3 .agents/tools/luma_host_check.py codex --output /tmp/luma-codex-check.json --trace-dir /tmp/luma-codex-traces
```

```sh
python3 .agents/tools/luma_host_check.py omp --model openai-codex/gpt-6.1-sol --output /tmp/luma-omp-check.json --trace-dir /tmp/luma-omp-traces
```

Choose new output and trace paths on each run. Previous observations are not overwritten. `--timeout` sets seconds per native process. `--model` is optional and passed to the host; omission uses its native selection, not a model pinned by Luma. Check the host's availability and version rather than assuming these example model IDs are universal.

The JSON separates each phase and `continuation_passed` from the strict aggregate `passed`. Exit status zero means all three checks passed; one means at least one check failed; two means setup or invocation failed. A missing startup capability must not be hidden by successful explicit continuation.

Raw native traces can include inherited context. They stay in the selected local trace directory and are not automatically added to the public repository. Public results should contain only reviewed synthetic artifacts and necessary observations.

## Invocation boundaries

### Codex

The check uses `codex exec`, ephemeral fresh sessions, a read-only startup phase and workspace-write continuation phases. It ignores user `config.toml` for these test invocations rather than changing it. Existing authentication, global instructions and policy can still affect the run; this is not an isolated model baseline.

For ordinary work the check explicitly asks Codex to read `.agents/AGENTS.md` before the task. This is the same manual entry-point route offered by the README, not automatic core loading. Native skill discovery and reading a skill body are separate observations from startup delivery of the working agreement.

A preliminary run on Codex 0.160.1 did not deliver a fixture checkword through `project_doc_fallback_filenames=[".agents/AGENTS.md"]`. The repeatable check does not advertise or depend on that unestablished binding. No root instruction file or copied core is created as a workaround.

### OMP

The check uses print/JSON mode with `--no-session`, disables extensions and LSP, and limits tools to file operations. This avoids exercising an installed optional engine or external connector for the synthetic task. Existing authentication and some global guidance/settings can still apply.

The startup check does not explicitly supply the core body or path in its request. A preliminary run on OMP 18.12.3 returned the temporary core's checkword without tools. That establishes observed delivery for this configuration, not universal behavior on all versions or hosts.

## Observed results

On 20 October 2026, using seed revision `28c5519`, both hosts passed the checkpoint and fresh-process continuation checks. OMP 18.12.3 also passed startup delivery. Codex 0.160.1 did not pass startup delivery, so its strict aggregate result remains failed despite useful explicit-invocation support.

The [reviewed synthetic artifacts and results](host-conformance-results.json) retain that distinction. Native traces showed both continuation runs reading the installed continuity skill; OMP's skill URIs resolved to the temporary project resources. Parent inspection confirmed the actual final guides and retained context preserved the original outcome and human note. This was not an independent review. All 57 local helper regression checks passed.

Codex used its native default model selection, while OMP requested `openai-codex/gpt-6.1-sol`. Their timing and outcomes are not a controlled comparison. No raw native trace, inherited user guidance or credential data is included in the public results.

## Limits and next checks

One synthetic continuation does not establish reliable long-running work, semantic completeness across a source collection, beneficial learning, independent review or superiority to an unconfigured host. The source-guidance digest and host version identify the tested package and host, but omitted model versions and inherited context remain limits.

Actual context compaction, nested working directories, existing local instruction composition, unavailable capabilities and update reconciliation need their own cases. Human preservation here concerns a supplied note, not a concurrent edit race. Keep these operational questions separate from the design's matched native-host outcome and cost comparisons.

A separate [matched host/seed evaluation](MATCHED-EVALUATION.md) now compares one OMP/model configuration with and without the seed. It found equal semantic outcomes and higher measured Luma effort on its small synthetic set; this does not expand the host-conformance claims above.

## Canonical retention-workflow recheck

The subsequent canonical retention-workflow candidate was checked in fresh disposable workspaces with guidance digest `020ae8b1f5667fe9e8e92c01434bf098188fc72ea40d512a7d3565bd6c4aa5b2`. OMP 18.12.4, requesting `openai-codex/gpt-6.1-sol`, passed startup, checkpoint and fresh continuation. Codex 0.160.1 with its native default again passed checkpoint and fresh continuation through an explicit core-read request, but not automatic startup delivery. Its strict aggregate therefore remains failed. Parent inspection of the saved guide and checkpoint confirmed the original installation-and-rollback outcome and human note were preserved.

An initial Codex invocation requesting `gpt-5.4` was rejected as unsupported by its authenticated account before task execution. That failed attempt is retained separately; retrying with the native default is not evidence that the unsupported model worked. These operational checks do not compare answer quality, test automatic compaction, or establish cross-harness outperformance. No native configuration or existing installation changed.

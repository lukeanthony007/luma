# Longitudinal comprehension evaluation

## Purpose

Luma's intended advantage is accumulated, source-backed understanding applied through continuity. Memory preserves evidence; maintained explanations connect its meaning; later work must find and apply that understanding without the user reconstructing the context. Cost is secondary until a capability advantage is established.

The earlier [matched evaluation](MATCHED-EVALUATION.md) tested prepared continuity with explicit checkpoint and lesson instructions. Its outcome tie does not settle whether Luma independently develops useful understanding through ordinary project work. The user also identified the Git-inspection requirement as part of the shared global OMP instructions; observed Git checks alone cannot be attributed to Luma-specific guidance.

## Frozen first protocol

Use a real, user-selected project as private source material, not synthetic facts with a hand-written ideal handoff. Select static documentation and code excerpts with source paths, original line numbers, capture time and file hashes. Preserve the actual project and its existing edits. Do not include credentials, live user data, logs, runtime state or native project instruction files. Distinguish static evidence from runtime behavior and proposed design from implementation; an omitted excerpt cannot establish repository-wide absence.

The first case has six staged review episodes followed by two application probes. Episodes are evaluation-authored requests grounded in actual project material, not reconstructed historical conversations. They progressively introduce purpose, design dependencies, retrieval behavior, caller wiring, incremental processing and response construction. A pilot constraint is introduced partway through and must survive later sessions. Neither agent is asked to save a checkpoint, record a lesson or create a wiki. Agents may maintain useful local records as part of normal work.

Each episode starts a new OMP process without conversation history. Original incoming requests are archived verbatim for every condition; assistant responses are not automatically supplied to subsequent episodes. New source locations are named when introduced, but later application requests do not point to specific evidence or retained records. The source archive is preserved throughout, so a baseline agent is not deprived of the original information.

| Condition | Acquisition | Application evidence |
|---|---|---|
| Luma | Installed seed, ordinary requests, whatever records it creates | Original material, request history and its own retained records |
| Stock host | Same configured host/model, ordinary requests, whatever records it creates | Original material, request history and its own retained records |
| Source-only fresh agent | No acquisition sessions | Complete original material and request history; no authored synthesis or earlier assistant answers |

Run two repetitions. Each application probe forks the same post-acquisition state, so one probe cannot teach the next. This produces 24 acquisition invocations and 12 application invocations, plus two delivery checks. The initial source-only probes need not wait for the other conditions to finish: their complete evidence is staged from the frozen case, not copied from an agent's mutable workspace.

All conditions request `openai-codex/gpt-6.1-sol` with minimal thinking, the same file tools and 240-second per-invocation deadlines. Existing global instructions and authentication remain shared. Automatic skill/rule discovery, extensions, title generation, LSP and prewalk are disabled; the Luma core loads natively and routes through installed file links. This tests core-routed file-based operation, not native skill discovery. File tools permit reading and maintaining local records, but no shell tool is supplied; helper execution and runtime validation are therefore unavailable to the evaluated agents. A tool allowlist and task instructions are not an OS sandbox.

## Outcome assessment

Freeze the private case and rubric before native runs. Primary measures are retained purpose and constraints, correct application of evidence, correction fidelity, scope-sensitive transfer, grounded recommendations, and user repetition/correction required. Record whether useful explanations are created without prompting, whether later sessions actually read them, and whether errors persist in current retained accounts. File count and fluent summaries are not comprehension scores.

The two probes ask for an integrated next-step recommendation and an assessment of a changed case. Each has eight criteria scored 0 (missing/wrong), 1 (partial), or 2 (correctly applied with important qualifications). Review actual final answers and their support with arm/repetition labels concealed; retain reasons, disagreements and uncertainty. Inspect retained accounts separately for distortion and their later use. Label-masked model review is not an independent blinded human study. Do not silently change scoring after observing results.

Record incomplete processes, missing responses, source/seed mutations and chain failures. Keep completed per-run results even if a later invocation fails. Usage, tool counts and elapsed time remain descriptive secondary measurements; acquisition and application costs are distinct. The same global prompt may independently encourage retention in the baseline, which is part of this configured-host comparison rather than a pristine-model experiment.

## Private evidence and reproduction

The case, source provenance, private rubric, transcripts, generated records and detailed review belong in local excluded storage. They are not automatically committed, pushed or copied into this public source repository. A public aggregate must be separately reviewed to avoid disclosing project material. The evaluated workspaces are temporary copies outside the Luma checkout, avoiding inherited project instructions in the stock condition.

```sh
python3 .agents/tools/luma_continuity_eval.py \
  --case /path/to/private-case.json \
  --output-dir /path/to/new-private-result-directory
```

The output directory must be new. The case contains `format_version`, `model`, `repetitions`, `timeout_seconds`, `readme`, `common_prompt`, `stages` and `probes`. Stages have unique IDs, ordinary prompts and unique UTF-8 source files under `inputs/`; `inputs/requests/` is reserved for the original incoming requests. Probes have IDs and prompts but cannot add evidence. Source paths cannot escape the input namespace or overwrite the installed seed. Expected answers and scoring criteria stay outside the case presented to the agents.

The developer-only runner is not included by the initializer. Raw traces may contain host metadata and must remain private. Results preserve each invocation's messages, retained records, read paths, hashes and mechanical checks; those checks do not substitute for semantic review. Temporary workspaces are removed after snapshots are saved.

## Status

Protocol and private source/rubric are frozen. Native results and their interpretation will be recorded after artifact review. No advantage is claimed in advance.

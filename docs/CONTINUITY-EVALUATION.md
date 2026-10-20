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

## First result: retention did not activate

The 20 October 2026 experiment completed all 36 task invocations. The frozen seed source was `8bd41cd`, with runner/protocol commit `3dca4e3`. Both delivery checks passed, and no protected inputs or installed resources changed. The [public aggregate](continuity-evaluation-results.json) omits private source excerpts, answers, records and host metadata.

| Condition | Applied comprehension score across four answers | Maximum | Authored records before application |
|---|---:|---:|---:|
| Stock configured host | 58 | 64 | 0 |
| Luma | 56 | 64 | 0 |
| Fresh source-only agent | 58 | 64 | 0 |

All conditions identified the consequential distinctions and produced broadly useful recommendations. Small score differences mainly concern omitted qualifications in composite criteria, not contrary technical conclusions. These results do not establish a statistical ranking or a retained-comprehension advantage.

The stronger observation is **zero durable knowledge creation**. Luma read its comprehension skill in all 16 of its sessions, but did not read memory, wiki or continuity guidance. No condition attempted a write/edit, and no tool errors were reported. Without agent-authored records, later sessions had to reconstruct understanding from the original evidence. This is an observed activation gap in the tested analysis workflow, not proof that memory/wiki synthesis cannot help or that its complete cause has been isolated.

The selected project sources and original dirty-tree status were checked unchanged. No project runtime, service, database query or project test was executed. All 65 local helper regression checks passed.

## Bounded follow-up

A private candidate strengthened only the always-on core's handoff from ongoing project comprehension into a discoverable knowledge account. It explicitly covered creating an account when none exists, analysis-only work with authorized recordkeeping, qualifications and source support, and the one-off/no-write exception.

The candidate was tested on a previously unused source topic with two acquisition sessions, one application question and a one-off control. The same case ran against the original seed, each with its own stock and source-only controls. All 20 invocations completed, but neither seed created a retained account. The one-off controls preserved files. This candidate did not meet its retention criterion and was not adopted into production guidance.

An explicit-permission control then used unchanged guidance with standing permission to create local knowledge notes/wiki pages, without requesting a checkpoint or particular record format. All ten invocations completed, but no retained account was created. Across the three follow-ups, all nine one-off controls answered correctly without tools or writes. Neither stronger core wording nor clearer optional record-creation permission was a demonstrated fix.

Production guidance and global host settings were unchanged by those checks. The diagnosis below investigates the boundary between loaded guidance and actual selection/application of memory, wiki and continuity.

## Instruction activation diagnosis

A subsequent 31-invocation diagnosis inspected the assembled host state and captured actual provider requests. The core's retention paragraphs were present. OMP 18.12.3's write-tool description prohibited document creation unless requested. An isolated diagnostic hook either left the request unchanged or removed only that clause, preserving the remaining tool description, execution and approval policies. Global configuration was not edited.

The initial matrix comprised five three-session chains. An adaptive replication added four chains and four no-write one-off controls. Each chain used two source-acquisition sessions followed by a fresh application session. The stronger core was the unchanged private candidate from the failed follow-up, not another tuned revision.

| Core | Host document rule | User wording | Chains | Accounts created before application | Accounts read during application |
|---|---|---|---:|---:|---:|
| Original | Native | Explicit optional note permission | 2 | 0 | 0 |
| Original | Removed for probe | Explicit optional note permission | 1 | 0 | 0 |
| Stronger candidate | Native | Explicit optional note permission | 2 | 2 | 2 |
| Stronger candidate | Removed for probe | Explicit optional note permission | 2 | 2 | 2 |
| Original | Native | Explicit record request | 1 | 1 | 1 |
| Stronger candidate | Native | Original general local-record permission | 1 | 1 | 1 |

All tasks completed and protected sources/seed files remained unchanged. All four one-off controls answered correctly without tools or file changes. Six retained workspaces passed link/completion checks. Two reads of an absent `.git` returned errors in the non-repository fixtures; both sessions recovered and wrote records. No write failure was observed.

These contrasts rule out unavailable file writing or absent core delivery as the general explanation. Removing the host document clause alone did not activate the original seed; leaving it present did not prevent the stronger candidate from retaining knowledge. Extra explicit note-permission wording was not necessary in one successful follow-up. The evidence favors a problem in selecting retention as part of ongoing work, particularly the transition from cross-source investigation to a maintained account. It does not isolate a minimal sufficient wording or establish why every earlier attempt failed.

The five candidate accounts contained substantive synthesis, source references and important qualifications. Three replicated acquisition sessions actually read memory and wiki guidance. Every created account was consulted by a fresh application process, but those processes also reread the original sources. One initial account omitted a consequential exception in an empty-result claim; its later answer preserved that exception after consulting source evidence. Record creation, source fidelity and improved answers must therefore remain separate claims.

The earlier candidate failure remains evidence, not an outcome to discard. The candidate is now conditionally demonstrated rather than proven ineffective, but reliable activation and an advantage over a fresh agent remain unestablished. Production guidance stays unchanged. The next implementation decision is whether to promote a clearer core responsibility after fresh-case checks of spontaneous retention, correction, qualified transfer and no-record exceptions. A permanent host hook or removal of host safeguards is not justified by this diagnosis.

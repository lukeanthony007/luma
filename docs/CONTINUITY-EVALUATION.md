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

The output directory must be new. The case contains `format_version`, `model`, `repetitions`, `timeout_seconds`, `readme`, `common_prompt`, `stages` and `probes`. Optional `reasoning_effort` selects `minimal`, `low`, `medium` or `high` equally for every arm and loading check; omission preserves the original minimal-effort behavior. It changes only these evaluation invocations, not global settings.

Format 1 retains the original append-only semantics: unique source paths across stages and no probe evidence. Format 2 permits replacement of a source at its existing path in a later stage or independently forked probe. Before replacement, the runner preserves the old bytes under `inputs/history/<sequence>-<episode>/` and records source path, episode, sequence, previous/current SHA-256 and archive path in a transition manifest. Original incoming requests, including format-2 probe requests, are retained under `inputs/requests/`. Every condition receives the same current evidence, history and requests; one probe's replacement does not affect another.

Source files must be UTF-8 text under `inputs/`, outside reserved `inputs/requests/` and `inputs/history/`. Source paths cannot escape that namespace, conflict as file/directory parents, or overwrite the installed seed. Staging refuses symlink destinations and conflicting archive/request paths before writes. During invocation, current sources, histories, requests and installed resources are protected by mechanical comparison; additions to `inputs/` are also reported as failures. Expected answers and scoring criteria stay outside the case presented to the agents. These checks are not an OS sandbox.

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

The earlier candidate failure remains evidence, not an outcome to discard. At the close of the diagnosis, the candidate was conditionally demonstrated rather than proven ineffective; reliable activation and an advantage over a fresh agent remained unestablished. Production guidance was unchanged by that diagnosis. The next implementation decision was whether to promote a clearer core responsibility after fresh-case checks of spontaneous retention, correction, qualified transfer and no-record exceptions. A permanent host hook or removal of host safeguards was not justified.

## Retention implementation check

The implementation starts from the stronger two-paragraph core candidate, not a change to the host's document rules or tool permissions. It explicitly covers a useful first account, cross-source retention during authorized analysis, later consultation, source support, established ownership/layout and one-off/no-write exceptions. The first run below exposed a maintenance failure; the revision adds an explicit same-turn correction and reconciliation paragraph.

The new [Harbor fixture](../.agents/tools/tests/fixtures/retention_activation.json) is synthetic and separate from the diagnostic project. Three ordinary review requests establish a depot-scoped pilot, introduce a superseding correction, then add a newer-format exception. No request asks for notes, a wiki or a checkpoint. Two independent application questions and one explicit no-write one-off each fork from the final acquisition state. Run it with:

```sh
python3 .agents/tools/luma_continuity_eval.py \
  --source . \
  --case .agents/tools/tests/fixtures/retention_activation.json \
  --output-dir /path/to/new-private-result-directory
```

Before execution, the acceptance criteria were frozen: both Luma histories must create a discoverable substantive source-backed account, preserve the correction and scoped exceptions, and actually consult that account in fresh application sessions. The latest proposed date is 2027-02-22, not approval to launch. The six-item multiplier applies only to East Quay legacy-v1 crates, not explicit items/current-v2 or unconfirmed South Yard mappings. Application must derive 54 items for nine qualifying crates and nine items for a current-v2 amount of nine. It must preserve the depot filter, full-night completeness and operator-reconciliation gates rather than treating the newest 40 rows as sufficient. Every no-write control must answer 150 minutes without changing files, and protected evidence/seed bytes must stay unchanged.

The comparison retains the same configured stock host and a fresh source-only arm with all original evidence and incoming requests available. The native runner has no diagnostic hook or document-policy ablation. File creation, qualified correction, later use and answer quality are reviewed separately; a small synthetic result cannot establish broad reliability or an advantage attributable to memory.

### Initial implementation result

All 30 invocations completed, both delivery checks passed, and protected inputs and installed resources stayed unchanged. Both Luma histories created a substantive account during the first request and both fresh application sessions in each history consulted it. Stock and source-only created no records. All six no-write controls answered correctly without changing files.

However, **neither Luma history updated its saved account after the correction or the newer-format evidence**. The superseded date and quantity example remained in place without the correction or the new exceptions. Later answers recognized those changes by rereading original sources, and one answer explicitly acknowledged the stale account. Correct chat answers did not satisfy the frozen requirement to maintain corrected understanding. The original candidate therefore failed this implementation check.

The revision keeps that failure and adds an explicit core responsibility: when new evidence changes an account, update the affected claims, examples, implications and next actions during the same authorized turn, link correction support, preserve superseded conclusions as history, and reread the changed account before finishing. If writing is prohibited or unavailable, respect that boundary and disclose the unresolved stale account. Repeating the same frozen fixture is a post-failure regression check, not independent held-out validation.

### Revised implementation and independent transfer

The frozen Harbor regression completed 30 invocations. Both revised-core histories created an account, updated it during the correction and format-extension turns, and consulted it in both fresh application sessions. Parent review found the scoped rules, superseded conclusions, derived examples, source links and dependent next actions retained correctly. The six no-write controls preserved files and answered 150 minutes.

Without another guidance change, the different [Sable archive scenario](../.agents/tools/tests/fixtures/retention_correction_transfer.json) completed 20 invocations. Its correction changes ordinary retention from 21 to 14 days, preserves legal holds, adds a separate 60-day event rule and an unknown other-collection case, and replaces checksum-only acceptance with complete inventory plus demonstrated restoration through the actual consumer. Both Luma histories created and corrected an account that a fresh application consulted. Both explicit no-write project-preference changes were applied in conversation without file changes; the agents disclosed that the saved next-step preference remained unchanged.

| Check | Initial Harbor candidate | Revised Harbor regression | Independent Sable transfer |
|---|---:|---:|---:|
| Luma histories creating a discoverable account | 2/2 | 2/2 | 2/2 |
| Luma correction/extension turns updating that account | 0/4 | 4/4 | 2/2 |
| Fresh changed-case/recommendation sessions consulting the account | 4/4 | 4/4 | 2/2 |
| No-write probes preserving files, all conditions | 6/6 | 6/6 | 6/6 |

The [public result aggregate](retention-implementation-results.json) retains hashes, conditions and outcome limits. Across the three batches, all 80 tasks and six delivery checks completed, protected inputs/seed bytes stayed unchanged, and six retained-workspace link checks passed. Eight reads of absent `.git` returned errors in the non-repository fixtures; all sessions recovered, with no write failure. All 65 supporting helper tests passed.

Semantic review was by the parent, not independent or blinded. The reviewed stock and source-only changed-case answers also preserved the central distinctions correctly, without authored accounts. Luma's new behavior is maintained knowledge and later consultation, not a demonstrated answer-quality advantage. Original sources remained available and were reread. Harbor's revised result is a post-failure regression; Sable is a separate synthetic scenario on the same configured host/model, not general reliability evidence. Existing user installations, global OMP settings and Animus integration are unchanged.

## Real-project replay and workflow candidate

The synthetic result did not transfer reliably to the frozen six-session real-project investigation. With the revised core at `964fbca`, all 36 tasks and both loading checks completed, but only one of two Luma histories created an account. That account was consulted later but stopped incorporating evidence after the chat-integration stage. One recommendation explicitly recognized its staleness without repairing it. The other history created no account. Original sources and incoming requests remained available to every condition; neither stock nor source-only authored records.

Two condition-masked model reviewers assessed the final answers against the frozen rubric. Descriptive totals were Luma 55/64, stock 55/64 and source-only 56/64. One parent adjudication restored a point because a statement about the stale account was verified in its archived contents, which the reviewer packet had omitted. These small differences establish no ranking. The host was OMP 18.12.4 rather than the earlier 18.12.3; historical differences cannot be attributed solely to guidance.

### Selection and reconciliation diagnosis

A 12-invocation frozen-snapshot matrix compared the original request, narrower runtime-implementation wording, and an explicit maintenance request. A subsequent four-invocation follow-up added only permission to create/update knowledge files. Both the initial-account and stale-account snapshots had two repetitions per condition.

| Condition | Initial accounts created | Existing accounts edited |
|---|---:|---:|
| Original request | 0/2 | 0/2 |
| Runtime-only implementation boundary | 0/2 | 2/2 |
| Explicit maintenance request | 2/2 | 2/2 |
| Permission only, subsequent follow-up | 0/2 | 1/2 |

All 16 invocations completed and preserved inputs/resources. A capture-only hook verified current core delivery and identical original/outgoing provider payloads; no host policy was removed. Permission alone was insufficient, and analysis-boundary wording affected update selection. These small samples do not establish a complete cause. Account review separately found surviving obsolete claims after some writes, including one explicit-maintenance control. Writing and semantic reconciliation are different outcomes.

### Comprehension-workflow candidate, not promoted

A private candidate changed only `comprehension/SKILL.md`: an ongoing investigation produces both the answer and current project understanding; authorized knowledge upkeep is distinct from hypothetical runtime implementation; completion compares affected claims and next actions, reconciles them in place, and rereads the saved result. One-off and no-write exceptions remain explicit. The core, host policy and original project requests were unchanged.

The 16-invocation paired snapshot check passed its bounded criteria. The candidate created both initial accounts and updated both stale accounts; the original workflow did each in one of two repetitions. Separate condition-masked model reviewers found all six authored accounts substantively supported for their bounded contracts. All eight no-write/one-off controls preserved files. This shows variation in the original workflow, not that it is incapable of maintenance.

The subsequent full 36-task replay completed, with both loading checks passing and protected inputs/resources unchanged. Both candidate histories eventually created accounts and all four fresh application probes consulted them. However:

- One history did not create an account until the third episode.
- Both histories skipped the incremental-refresh episode. Neither read the comprehension skill during that turn.
- One final account still omitted the refresh findings. The other recovered most of them but omitted the consequential distinction between a failed profile fetch, which stops relationship enrichment, and missing edge metrics, which receive a fallback.
- A separate missed earlier turn did read the candidate skill, so non-selection is not the entire explanation.

The final-account reviewer judged retention incomplete. The candidate therefore remains private and experimental, not part of the source package. All twelve application answers were separately reviewed with condition labels withheld: Luma scored 57/64, stock 58/64 and source-only 57/64. These descriptive differences do not establish a ranking or memory advantage; useful source-based answers continued to mask missing durable understanding.

These are diagnostic/regression cases, not held-out validation or live project operation. Those runs requested the same configured `gpt-6.1-sol` model with CLI minimal thinking on OMP 18.12.4. The candidate hash is `883c0df6fa5476ffab6d71d4ae1a49a781fc73c59bda6c2aa841efe432cefd27`. Original excerpts, exact candidate, protocols, traces and saved accounts remain in private local evidence; they are not published. Existing installations, global settings and the separate integration companion remain unchanged.

The next diagnostic separated delivery/selection from adherence and reconciliation, using the same missed refresh turn and preserving no-write controls. Its results follow. Adding more procedural detail to an occasionally unread skill had not solved the problem.

### Delivered workflow and reasoning effort

The frozen candidate was replayed from both exact pre-refresh accounts, twice per condition, with the original request and sources unchanged. A capture-only hook verified the effective provider input without modifying it. All 16 tasks completed and protected inputs/resources remained unchanged.

| Delivery condition | Skill read | Account updated |
|---|---:|---:|
| Optional selection | 1/4 | 0/4 |
| Explicit startup instruction to read the skill | 4/4 | 3/4 |
| Exact workflow supplied at startup | 3/4 | 2/4 |

The full method was verified in every startup-delivery request, so a subsequent skill read was not necessary for delivery. Nevertheless, both history-1 runs left the account unchanged and explicitly acknowledged missing retained updates. Both history-2 runs updated. Missing delivery therefore does not fully explain the failures, and guaranteed delivery did not fix them. Routing also changes task salience; these small samples do not isolate a universal causal effect.

All five edited accounts passed condition-masked model review against the frozen refresh criteria, including the profile-failure versus edge-fallback distinction. Four startup-delivery no-write/one-off controls preserved files; the calculations correctly answered 150 minutes.

A subsequent 12-task follow-up varied reasoning effort while keeping the startup-loaded workflow and all workspace input hashes identical within matched pairs. It was chosen after the delivery result, not held-out validation:

| Requested effort | Observed provider effort | Account updated |
|---|---|---:|
| minimal | low | 3/4 |
| medium | medium | 4/4 |

OMP serialized the requested minimal setting as provider low for this model. Both conditions demonstrably received the full workflow. All seven edited accounts passed the same bounded semantic criteria in separate condition-masked review; all four medium-effort controls preserved files and answered the one-off calculations correctly. All tasks completed and preserved inputs/resources.

Across these 28 invocations, the host remained OMP 18.12.4 and the observed model was `gpt-6.1-sol`. No host policy was removed, and original/outgoing payloads matched. The variation between two and three lower-effort updates in successive small batches prevents treating four medium-effort successes as an established fix. These effort probes did not include a stock/source-only comparison or fresh application sessions, so they establish neither a Luma advantage nor later use of these particular accounts.

No routing directive, inline workflow or reasoning default was promoted from those diagnostics. The subsequent comparison below tested longitudinal behavior at equal medium effort, including a fresh case and later application. Exact experimental guidance, protocols, accounts and captures remain private; production guidance, existing installations and global settings are unchanged.

## Medium-effort longitudinal comparison

The experimental configuration was frozen before the fresh case was authored: source seed at `6142944`, the prior candidate comprehension skill, and the exact completion workflow also supplied at startup. A private copy of the development runner requested medium reasoning for every arm. The original project case and rubric were unchanged. No guidance or scoring changes were made after observing outcomes.

The comparison retained the same configured stock host and a fresh source-only arm with all original evidence and archived incoming requests. Every task used a fresh process; earlier assistant responses were not automatically injected. Application probes forked independently from each history's final acquisition state. This tests the complete experimental configuration, not the isolated causal effect of reasoning effort or instruction placement.

The original six-stage project replay ran 36 tasks. A separate author, instructed not to inspect the candidate or prior results, drafted an eight-stage synthetic community-workshop case with two later decisions, a no-write preference question and an unrelated calculation. Parent review clarified capacity, fees and timing and checked arithmetic before freezing its case and rubric. Its 56 tasks tested purpose, explicit choices, revised attendance, budget/reserve relationships, staffing, access windows, unresolved dependencies and a conflicting late opportunity. It is fresh to this frozen configuration, not an external benchmark or live-project trial.

All **92 task invocations and four loading checks completed** on OMP 18.12.4 with configured medium reasoning and observed model `gpt-6.1-sol`. Original inputs and installed resources stayed unchanged; frozen case, rubric and resource hashes matched afterward.

| Retention observation | Existing-project replay | Fresh planning case |
|---|---:|---:|
| Histories creating an account in the first session | 2/2 | 2/2 |
| Acquisition turns maintaining an account | 12/12 | 16/16 |
| Later project sessions consulting the account | 4/4 | 6/6 |

The planning case's later project sessions include its no-write preference probe; the unrelated calculations did not read the accounts. Stock and source-only authored no records. All twelve no-write/one-off controls preserved files and answered correctly.

Separate account reviewers found no material defects in ten selected saved snapshots: the original project's refresh and final-acquisition states, and the planning case's explicit-choice, revised-evidence and post-offer states. Formerly omitted refresh dependencies were retained. Planning accounts correctly superseded old attendance/budget assumptions while preserving historical calculations, conditions and unaccepted proposals. Eight reconstructed retained-workspace link checks passed. These checks concern the selected accounts, not an exhaustive semantic audit of every intermediate statement.

Condition-masked reviewers separately assessed all 24 decision answers against frozen eight-criterion rubrics. Scores are descriptive totals across two probes and two repetitions:

| Case | Luma experiment | Stock host | Fresh source-only |
|---|---:|---:|---:|
| Existing-project replay | 59/64 | 61/64 | 62/64 |
| Fresh planning case | 62/64 | 64/64 | 64/64 |

All conditions reached the central supported decisions. No answer-quality or decision advantage for Luma was observed. The small score differences do not establish a statistical ranking; deductions concerned coverage and qualifications. In the planning case, qualifications omitted from some Luma final answers were present in the saved accounts, demonstrating that successful retention does not guarantee complete answer composition.

The useful result is consistent creation, correction and later consultation of supported understanding in this bounded set. Reading an account does not establish that it caused a correct decision, especially when original sources remained available. Two histories per case on one host/model do not establish everyday or cross-harness reliability; model-assisted reviews are not independent human validation.

The configuration remains experimental and unpromoted. Further wording changes against these cases would no longer constitute fresh validation. A controlled ordinary-project pilot should preserve the frozen configuration and evaluate missed commitments, user recaps, decision quality and maintenance burden over time before claiming that retained understanding outperforms reconstruction from sources. Public status records have been reconciled; production core/skills, global settings, existing projects and the untracked integration companion are unchanged.

## Continuation and changed-source regression

A subsequent build attempt consolidated startup retention guidance into one core workflow, linked comprehension to it and strengthened continuity's application checks. This was a new configuration, not a byte-equivalent promotion of the earlier experiment. It was frozen before reviewing the next source-grounded case. Parent review corrected source-summary attribution, scoring and independent-fork premises before freezing the final case and rubric.

Six acquisition stages introduced an investigation, an initial broad proposal, an explicit later scope choice, an intervening unrelated task and new initialization evidence. Three independently forked decisions tested resumption, bounded acceptance planning and replacement of a previously inspected source at the same path. The counterfactual changed both an eligibility threshold and missing-record behavior; all conditions retained identical originals, incoming requests and source history. A separate no-write question used the unchanged acquisition state. This is controlled source-derived work, not a live project or ordinary-project pilot.

The canonical candidate ran 48 task invocations. An unchanged predecessor configuration then ran the same 48-task comparison to diagnose whether consolidation explained the failures. That second run is known-case regression evidence, not fresh validation. Every invocation completed; four loading checks passed; protected inputs and installed resources stayed intact; hashes matched; all sixteen cross-condition application-input comparisons matched. All twenty unrelated/no-write control invocations preserved files, although file preservation does not establish correct continuation.

Separate condition-masked model reviewers scored eighteen decision answers per configuration against frozen rubrics. Each condition's total covers three probes and two repetitions:

| Configuration | Luma score, maximum 96 | Stock score | Fresh source-only score | Luma central decisions correct |
|---|---:|---:|---:|---:|
| Canonical consolidation candidate | 77 | 86 | 86 | 4/6 |
| Unchanged predecessor | 75 | 86 | 85 | 2/6 |

All baseline central decisions were correct in these runs. The important failure was material continuation drift, not merely score differences: some Luma answers treated an earlier agent-proposed output restriction as the selected user scope and displaced a still-requested investigation. Baselines could reconstruct the requested direction from the same evidence. All changed-source decision answers recognized both counterfactual changes; correct local factual revision did not guarantee preservation of the larger outcome.

Saved-account reviewers assessed four selected snapshots per configuration, final acquisition and post-replacement for each history. Each configuration had two snapshots with material goal/scope defects and two without material defects. Minor defects were reported separately, including skipped evidence integration, an unqualified historical reference and absent navigation evidence. The canonical candidate changed accounts in six of ten substantive acquisition turns and skipped the final evidence update in both histories. The predecessor changed accounts in nine of ten turns but still demonstrated goal drift. Maintenance frequency, consultation, semantic fidelity and useful continuation are distinct measures.

Consolidation is not established as the cause: the predecessor also failed. Nor do these small samples establish a statistical ranking. They do show that the earlier bounded retention success was not broad reliability, and that memory can preserve an unadopted plan as well as useful understanding. Model review is not independent human validation.

The canonical consolidation was withdrawn from the source guidance and preserved in private evidence; the predecessor remains experimental. The revision-aware runner and explicit effort selection were implemented, exercised by all 96 invocations and checked by 71 passing helper tests. Existing installations, global settings, live projects and the untracked integration companion were not changed. The next candidate addresses source-backed ownership of consequential decisions and applies it to executable continuation tasks; it must not inherit a success claim from these failed configurations.

## Decision ownership and retention activation

The next candidate added a source-backed project-account contract: distinguish the user's requested outcome and adopted constraints from the agent's proposed approach; retain supporting wording for consequential scope choices; verify it before continuing. A terse answer does not cancel already-authorized account upkeep, while explicit no-write instructions still take precedence. This ownership-only candidate did not include the earlier positive completion workflow.

Two separate authors drafted non-personal executable cases without inspecting the candidate or prior outcomes. Parent review corrected schema and oracle ambiguities before freezing the cases, rubrics and guidance. One case covered sensor readings and incident export, with changed eligibility and deduplication rules. The other covered release and rollback readiness, with changed approval and recency rules. Each retained all originals and incoming requests, included an unrelated lookup and no-write control, and forked original-source and same-path-replacement implementation probes independently.

All 76 task invocations and four loading checks completed on OMP 18.12.4 with configured medium reasoning and `gpt-6.1-sol`. Protected inputs/resources and frozen hashes stayed unchanged. All twenty unrelated/no-write controls preserved files. All 24 generated Python artifacts passed syntax inspection and the frozen functional examples: each condition scored **84/84**, comprising 44 data checks and 40 planning checks. This is a tie, not an outcome advantage. Additional post-review diagnostics, kept outside that score, found extreme integer-overflow or duration-rounding defects in every planning artifact; passing the examples did not establish general implementation correctness.

Separate model reviews found no material answer errors or unsupported adoption of the agent's narrower proposals in these cases. Nevertheless, retention did not reliably activate: both data histories waited until the last acquisition turn to create accounts, and neither planning history had an account before implementation. In a separate isolated code-investigation pilot, both Luma analysis sessions read the comprehension skill but created no account. Delivery and file-writing capability were therefore not sufficient explanations.

A targeted 20-invocation Luma-only replay of the earlier continuation case recovered the requested scope in all six decision answers and both no-write answers. Both changed-source answers recognized both replacements. However, two of four selected saved accounts still omitted the latest initialization evidence. This is known-case regression evidence, with no new baseline comparison or broad reliability claim.

The resulting diagnosis separates two responsibilities: preserve ownership of direction, and complete the handoff from investigation into current project understanding. A new combined candidate makes that handoff explicit in the core, routes comprehension to the same canonical workflow and retains the ownership contract. Its applicability remains authorized ongoing work, not one-off lookups or explicit no-write requests. It requires its own verification; it cannot inherit a success claim from either predecessor.

### Combined-workflow regression

The combined source revision was frozen before replaying the same two non-personal cases with unchanged requests, source histories and functional oracles. This was a Luma-only known-case regression, not a new holdout or matched baseline comparison. OMP was now 18.12.5, rather than 18.12.4 in the preceding batches; configured model and medium effort were unchanged. Historical differences cannot be attributed solely to guidance.

All 32 task invocations and four loading checks completed. Protected inputs/resources and frozen hashes matched; all eight unrelated/no-write controls preserved files. Following source review, all eight generated Python artifacts passed the unchanged 84 functional examples, with no observed input mutation. The checker ran reviewed code in disposable subprocess directories, not an OS sandbox. Review again identified an outside-oracle overflow risk in all four planning implementations; those static findings were not silently added to the frozen score.

Three of four histories created a substantive account during their first investigation. The remaining data history saved nothing during its first two investigations, then created a source-linked account at the decision stage. Both planning histories created accounts immediately, including one kept entirely in README. All twelve later project probes read the maintained account; unrelated lookups did not.

Separate model reviewers examined twenty stage-specific snapshots. Eighteen exhibited substantive accounts: sixteen had no material retained-understanding defect, while two intermediate planning accounts lagged the newly delivered policy and readiness evidence. Those answers correctly disclosed the lag under their interpretation of “Do not take action”; both accounts were repaired in the next relevant turn. This records stale saved understanding without equating its existence with a proven permission violation. Two unchanged synthesis snapshots remained substantively current, so absence of a write alone was not treated as failure. The four revised-source accounts preserved the requested scope and correctly integrated the changed rules; all four no-write answers were substantively correct.

The revised workflow and ownership contract are included as experimental source guidance. They add no runtime, fixed account template or mandatory wiki. These results support bounded creation, revision and consultation of useful understanding, but not reliable maintenance on every turn, a causal memory benefit, or outperformance. The previous matched baselines already passed the functional examples; this replay supplies no new comparative ranking. Further evaluation needs less ceiling-limited tasks and ordinary authorized project use, not more wording tuned to these same cases.

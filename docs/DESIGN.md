# Luma: a portable agent seed

**Status:** working design proposal, 20 October 2026, with a first standalone implementation increment recorded below. Proposed interfaces and later phases are not delivered capabilities. Neither the design nor the initial implementation establishes measured superiority or authorizes runtime activation.

**Scope:** the public, standalone Luma configuration and its optional relationship with Animus. The Animus implementation companion is maintained separately in Animus's documentation as `LUMA-INTEGRATION.md`; this public design is usable without that repository.

## 1. Purpose

Luma is intended to be a self-contained, harness-agnostic agent seed: a useful starting configuration for an agent that understands the user's purpose, carries work and knowledge across sessions, uses available capabilities, and develops better practice through experience. Users can add or replace skills, tools and domain knowledge without adopting a new runtime or a fixed organization.

The seed is not an attempt to encode the perfect agent. Its value should come from a small set of effective defaults underneath the user's own work. Novelty is not a requirement; established methods should be adopted when they fit and demonstrate benefit.

A maintained wiki is one representation of understanding, not the whole product. An agent can help with an ordinary question, software change, research problem, personal project or ongoing undertaking without first building a knowledge base.

The user-established direction is:

- Standalone usefulness without Animus, an Obsidian plugin, or a bundled model runtime.
- Portability across capable file-based agent harnesses.
- Continuity, memory, comprehension and experience-driven adaptation as foundational responsibilities.
- A seed that users can extend with their own tools, skills and working arrangements.
- An optional relationship with Animus for deeper provenance and accountability.

The component boundaries, delivery mechanisms and implementation sequence below are proposals. Exact native integration and storage decisions remain open where identified.

### What self-contained means

The methods, navigation and durable files needed for ordinary use travel with the workspace. A host still supplies model inference, tools, permissions and execution. The minimum useful host can read the guidance and existing material, edit ordinary files within authority, and return results to the user. A read-only host can consult the seed but cannot maintain durable continuity or memory.

Search, shell execution, subagents, hooks, semantic indexes, scheduling and connectors are optional capabilities. Their absence should reduce convenience or narrow an explicitly dependent task, not make ordinary Luma work impossible. A requested independent review still requires another participant; serial self-review is not an equivalent substitute.

Self-contained does not mean offline inference, automatic instruction loading on every product, or execution guarantees supplied by prose.

### Non-goals

The initial seed does not provide a model loop, universal task graph, mandatory agent team, global ontology, vector database, scheduler, cross-device synchronization service or autonomous prompt optimizer. It does not replace the host's security controls or claim to settle uncertain external actions. Optional integrations must justify their cost and dependencies through an actual use.

## 2. Present foundation and proposed change

The reviewed design baseline is commit `25c01a35a1918f7a0a1d627777b615489de07074`, a file-based knowledge-management foundation. The [README](../README.md) describes the evolving implementation. The [working agreement](../.agents/AGENTS.md) and existing skills already contain much of the intended reasoning and maintenance practice.

| Present foundation | Role in the proposed seed | Still to establish |
|---|---|---|
| Working agreement and ten skills | Portable behavioral core and discoverable methods | Smaller, clearer routing and evidence that the combined guidance helps |
| Wiki, continuity and source-preservation practices | Human-readable understanding and resumption | Reliable correction, selective recall and fresh-session continuation |
| Capture helper with hashes and versioned source copies | Deterministic evidence-preservation support | Broader source-format needs and storage coexistence with an engine |
| Link and manifest checking | Mechanical maintenance checks | Semantic support, coverage and outcome assessment remain separate |
| Directory initializer | Non-destructive preparation of portable resources | Effective loading and compatibility under named host versions |
| Dream and configuration practices | Reflection and authorized local adaptation | Benefit from later use, not just successful edits |

The original proposal did not rename skills, change the initializer, relocate records or replace installed instructions. Implementation is tracked separately from that baseline. The long design document is developer material, not content to inject into every agent session.

### First standalone increment

The first increment makes the entry point serve ordinary agent work, keeps the ten existing practices discoverable on demand, and moves detailed resource conventions out of the core. Continuity, memory and reflection can use established project records without a wiki. Procedural learning has one canonical method, including candidate discovery, applicability limits and later-use assessment.

The initializer gains a recorded installed-resource baseline and read-only drift inspection. It does not auto-update existing resources or load a host. The [seed checks](SEED-CHECKS.md) distinguish helper regression checks and fresh-context guidance probes from operational host and outcome evaluation.

This is a Phase A increment, not completion of the full design. Subsequent [native host checks](HOST-CONFORMANCE.md) exercised a bounded synthetic fresh-process continuation in Codex and OMP and identified a startup-loading difference. Persistent adapters, reliable context-compaction recovery, measured benefit, managed storage coexistence and Animus binding remain unestablished. Existing installations and runtime state are not changed by publishing source.

### Retention activation increment

The core now explicitly covers creating the first useful project account and completing the transition from cross-source comprehension into retained knowledge. It starts from the two-paragraph candidate in the [instruction diagnosis](CONTINUITY-EVALUATION.md#instruction-activation-diagnosis), covering analysis-only recordkeeping within authorization, source support, human edits, fresh-session consultation and one-off/no-write exceptions. A first fresh-case run exposed stale accounts after correct conversational answers, so an additional core paragraph explicitly requires same-turn reconciliation of affected claims, examples, implications and next actions, with correction support, historical status and a final reread. Detailed memory and wiki procedures remain on demand; no mandatory wiki layout, host hook or background service is added.

The [Harbor fixture](../.agents/tools/tests/fixtures/retention_activation.json) exposed the stale-account failure; the revised core passed a same-fixture regression. The different [Sable scenario](../.agents/tools/tests/fixtures/retention_correction_transfer.json) then demonstrated creation, correction and fresh-session consultation in both histories, including explicit no-write project changes. The [behavior report](CONTINUITY-EVALUATION.md#retention-implementation-check) preserves the initial failure, final results and limits. Publication changes the source package, not existing installations; these bounded checks do not establish broad reliability or superior answers.

The later [real-project replay and workflow experiment](CONTINUITY-EVALUATION.md#real-project-replay-and-workflow-candidate) failed the reliability requirement. Core delivery and writing capability were verified, but permission and analysis-boundary wording did not fully explain maintenance selection. A private comprehension-workflow candidate improved short checks and later account consultation, yet skipped material refresh knowledge across successive sessions. The candidate was not promoted. Selection, execution and whole-account reconciliation remain separate unresolved responsibilities; successful synthetic checks do not establish ordinary-work reliability.

A subsequent [medium-effort longitudinal comparison](CONTINUITY-EVALUATION.md#medium-effort-longitudinal-comparison) froze the candidate with its completion workflow also supplied at startup. Across the original project replay and a fresh synthetic planning case, all four Luma histories maintained accounts through every acquisition turn and consulted them in later project tasks. Selected saved accounts passed semantic review, but equal-effort baselines reached the same central decisions and Luma showed no answer-quality advantage. This supports a bounded retention mechanism, not general reliability or outperformance; the experimental configuration remains unpromoted.

## 3. Design principles

### Keep the stable core small and consequential

Always-available guidance should preserve purpose, important boundaries and routes to relevant context. It should not repeat generic advice, every domain method or the entire history of prior failures. The appropriate size is an empirical question; a short, readable core is the initial constraint, not a universally optimal token count.

### Make essential behavior available, details retrievable

Basic continuity and retention responsibilities cannot depend entirely on the agent discovering an optional skill. Their brief triggers belong in the core. Detailed procedures, examples and reference material load when relevant. A skill that exists but is never selected has not demonstrated its method.

### Preserve ordinary work

A small request should usually receive a direct answer or action. Planning, delegation, retained notes, review and reflection should address an actual need. Completing a period of attention is not the same as completing the undertaking.

### Separate useful practice from enforced guarantees

Files can support careful reasoning, traceability and follow-through. They do not by themselves provide immutable accepted history, permission enforcement, transactional recovery or verified execution identity. The seed should accurately describe the behavior and evidence available in its current host.

### Keep one canonical home per fact or resource

Sources, current explanations, working context and procedures have different purposes. They may be linked and presented through several views without creating independently editable copies of the same authoritative state. Local adaptations must survive upstream updates.

### Let experience change the right thing

A bad result may require a knowledge correction, better context selection, a tool repair, a narrower procedure or no change at all. It should not automatically produce another global prompt rule. Useful learning is demonstrated by subsequent appropriate behavior, not the existence of a lesson file.

## 4. The seed's components

### 4.1 Stable working agreement

The core should establish a small set of cross-task responsibilities:

1. Recover the user's purpose and relevant context before asking for repetition.
2. Keep the original requested outcome distinct from the agent's proposed plan.
3. Select available methods and tools according to the task and their actual capabilities.
4. Inspect consequential evidence and distinguish observations, reports, inferences and unknowns.
5. Carry authorized work toward the requested outcome, verifying results appropriately.
6. Retain useful discoveries, corrections and unfinished commitments when they warrant persistence.
7. Improve owned local practice within the user's granted scope, preserving the basis and limits of a change.

These are proposed responsibilities, not a script to narrate on every turn. A short capability and navigation index should direct the agent to relevant skills and workspace records.

### 4.2 Discoverable practices

Keep the current repertoire initially; reorganize only where evaluation or concrete duplication justifies it.

| Practice | Responsibility in the seed |
|---|---|
| Setup | Understand purpose, establish a useful first step, and adapt to existing material |
| Comprehension | Locate, explain, investigate, reconcile and apply source meaning |
| Memory | Preserve support, correct retained knowledge and distinguish evidence standing |
| Continuity | Maintain purpose, current position, commitments and resumption context |
| Wiki | Develop readable, connected explanations and navigation |
| Sync | Reconcile a bounded collection and report actual coverage |
| Dream | Reflect across understanding and experience when useful |
| Configuration | Maintain resources, local adaptations and versioned changes |
| Collaboration | Bound assignments and integrate actual contributions |
| Inbox | Support temporary structured interactions when conversation is insufficient |

Each skill should explain when it helps, what it requires, what result it supports and when not to apply it. Instruction-only methods are the default. Scripts belong where they provide a concrete, checkable capability and declare their dependencies.

Users' domain skills supplement or replace methods deliberately. Luma should help find and apply them, not demand that every task pass through its entire repertoire.

### 4.3 Small deterministic helpers

Retain helpers for work such as non-destructive initialization, source capture, hashes, navigation and scope reporting. Prefer narrow operations with inspectable inputs and outputs. A successful helper result must not be described as proof of comprehension or task satisfaction.

Ordinary file access is the base. Keyword, semantic and graph indexes can be optional derived infrastructure when retrieval failures or costs justify them. File ownership and richer retrieval are compatible; adding an index should not make the human-readable record disposable.

### 4.4 Host delivery adapters

Maintain one canonical copy of the portable methods. Use thin native discovery links, imports or generated routing files where supported, preserving existing user instructions. Adapters should describe their supported host version and loading behavior rather than silently duplicating the entire prompt pack.

A setup check should distinguish resources installed, instructions loaded, skills discovered, tools available and an exercised task. A successful copy is not successful integration.

No single instruction path, hook API or MCP configuration file is assumed universal. The current `.agents/mcp.json` convention is a workspace authoring choice; an adapter must verify whether and how the selected host consumes it. Do not create an empty connector bundle just to complete setup.

### 4.5 Documented host differences

The following is a documentation snapshot, not an exercised compatibility claim:

| Host | Relevant documented behavior | Delivery consequence |
|---|---|---|
| Codex | [Instructions](https://developers.openai.com/codex/agent-configuration/agents-md) accumulate through selected files from repository root to working directory; overrides and size limits apply. [Project skills](https://developers.openai.com/codex/skills) use `.agents/skills/`. | Verify both the selected instruction chain and skill discovery. Luma's `.agents/AGENTS.md` is not automatically equivalent to a root `AGENTS.md`. |
| Claude Code | [Direct AGENTS support](https://code.claude.com/docs/en/memory#agents-md) is documented from v2.1.277, with default selection affected by applicable project CLAUDE files. Files inside `.agents/` are not default instruction entry points. [Project skills](https://code.claude.com/docs/en/skills) use `.claude/skills/`. | Preserve existing project instructions and deliberately route to the canonical Luma guidance; do not assume a shared filename or skill format establishes loading. |

[Codex MCP configuration](https://developers.openai.com/codex/mcp) and [Claude MCP configuration](https://code.claude.com/docs/en/mcp) also use different native configuration locations. A proposed adapter must use the actual host schema, not merely write `.agents/mcp.json`.

The delivery check should cover a fresh session, a nested working directory, an existing user instruction file, an applicable and an inapplicable skill request, a saved note recovered after restart, and context compaction where available. Host documentation and version thresholds must be rechecked when implementing the adapter. This proposal creates no native instruction files or configuration.

## 5. Memory and continuity

### 5.1 Different retention jobs

The following are logical roles, not mandatory new folders or independent stores:

| Role | Retain | Retrieve when |
|---|---|---|
| User and workspace context | Confirmed preferences, purpose and consequential conventions | They affect the present interaction |
| Working context | Original objective, decisions, verified progress, blockers and next useful action | Starting, resuming or changing an undertaking |
| Maintained understanding | Supported explanations, relationships, uncertainty and current conclusions | Answering or acting on the subject |
| Source evidence | Original material, provenance and relevant versions | Support, exact meaning, freshness or correction needs inspection |
| Experience | Particular attempts, outcomes, conditions and useful diagnoses | A comparable difficulty or reflective question arises |
| Procedural knowledge | Reusable, scoped methods and tool guidance | Their applicability conditions fit the task |

A transcript is neither a current account nor a reusable procedure. A compact context note is not the only surviving copy of richer evidence. Not every conversation deserves durable retention.

### 5.2 Continuity across sessions

At a meaningful checkpoint, retain enough for a fresh agent to continue: purpose, current requested outcome, accepted decisions, actual progress, remaining work, important constraints and the next useful action or dependency. Prefer existing project records over a second task ledger.

Save consequential changes during work rather than relying solely on a final message or session-end hook. On return, read the relevant account and inspect present artifacts where the next action depends on their state. A handoff guides verification; it does not prove completion or that an external operation never happened.

After compaction, recover the original objective and important unresolved work from durable context. Host summaries are useful but can omit detail. Reopen the actual source or record when meaning matters. The seed cannot control a host's context-window policy merely by requesting it.

### 5.3 Memory maintenance

Use small, targeted edits to current explanations. Preserve relevant earlier versions and the reason for a consequential correction. Repair affected references without silently repointing historical evidence at newer content. Keep unsupported identity merges, contradictory accounts and unknown outcomes explicit.

A memory claim is successful only when the content was actually saved and is retrievable. Capture, link validation, semantic support and completeness are separate checks. Retire duplicate or obsolete guidance deliberately; age or low access alone does not establish that a fact is false.

Captured source text remains evidence to interpret, not a new source of operating authority. Instructions found in retrieved documents do not override the user's request. Reusing personal context must respect the workspace and disclosure scope in which it was supplied.

Keep startup context bounded through selection and navigation rather than repeatedly summarizing everything into a shorter blob. Consolidation should preserve conditions, commitments and useful particulars, not merely reduce bytes.

## 6. Comprehension as a reusable capability

Comprehension is not a compulsory workflow graph. It is a repertoire selected according to the question: orient to structure, inspect evidence, construct an explanation, investigate uncertainty, reconcile changes and exercise the result.

The seed should preserve the complete relationships that make a claim useful: subject, attribution, time, quantities, units, population, conditions, exceptions and inference premises where relevant. A nearby quote does not repair a saved assertion that drops its qualification. A link identifies support to inspect, not proof of entailment.

When retaining an account, compare important source meaning with the saved explanation for omissions, and compare saved assertions back to their support for additions or distortion. Use fresh questions or changed cases where they expose a consequential gap. Do not turn every routine lookup into a formal examination.

Diagnose failures at the right boundary: meaning may be absent from the retained account, retained but not delivered, delivered but misapplied, or lost in the final answer. Repairing storage is not a solution to every delivery or reasoning defect.

Code, documents and measurements share this practice while using different evidence tools. Use available language-server or runtime evidence for code, exact passages and tables for documents, and measurement conditions and units for data. The seed must not claim an unavailable tool or invent an observation.

## 7. Learning from experience

Luma should support two related forms of adaptation. New evidence can revise understanding of the world. Experience of doing work can revise how the agent investigates or acts. Neither requires updating model weights, and neither guarantees improvement.

A useful episode preserves the purpose, relevant circumstances, approach, observed result, basis for that result and important uncertainty. Record a prospective expectation when it helps diagnose the outcome; do not manufacture a prediction after the event. Requirements, forecasts and preferences have different meanings.

A procedural candidate should identify the specific lesson, its evidence, applicability conditions, exceptions, proposed resource change and expected benefit. A single incident may warrant a local correction without supporting a general rule. Keep candidates separate from established defaults.

Authorized, reversible local maintenance can happen during ordinary work under standing user policy; it need not ask for approval for every correction. The agent must still preserve local ownership, the prior resource where possible, and the scope of authority. An experience does not grant permission to change host policy, external services or unrelated user skills.

Use subsequent relevant work to determine whether a revision was actually encountered, applied and helpful. Include nearby cases where it should not apply. Keep regressions, non-application and inconclusive outcomes; narrow or remove a rule when evidence warrants it. When no fresh comparison is available, retain the candidate as unproven rather than claiming a learned capability.

Immediate factual correction should not wait for a benchmark. Promotion of a broadly reusable method needs stronger evidence than fixing a mistaken path or recording an explicit preference. Task-appropriate checks can include executable tests, observed environment outcomes, source verification and user judgment; not every domain has a numerical oracle.

### Development-time optimization is separate

Maintainers can use trace-based prompt optimization and paired evaluations to improve the shipped seed. Installed users should not inherit an expensive optimizer or a background research obligation. An optional deeper system may supply repeated trials, accepted episode histories or governed activation, but standalone learning should remain useful without it.

## 8. Extension and resource ownership

Maintain a distinction between upstream seed resources, user-authored instructions and tools, and locally learned adaptations. This is an ownership distinction, not a promise to override the host's instruction hierarchy. Current user intent and applicable host rules still govern work.

New domain tools should state purpose, inputs, outputs, dependencies and effects. File presence is not installation or permission. New skills should be discoverable without copying the whole core into each one. No fixed specialist roster is required; delegation should earn its coordination cost.

An update should compare the installed baseline, upstream change and local change. Preserve or deliberately reconcile local adaptations instead of replacing them wholesale. Without a trustworthy baseline, inspect differences rather than assuming upstream is correct. A removed upstream resource does not automatically authorize deleting a locally adapted one.

The public package contains methods and tools, not populated user knowledge, source archives, credentials or live runtime state. Existing workspace organization remains authoritative until an authorized change establishes something better.

## 9. Optional Animus relationship

The proposed relationship is one portable practice layer with an optional deeper binding. Luma must be useful on its own; it is not an incomplete client waiting for Animus. Animus should interpret and support the same practices rather than require an unrelated second personality or knowledge workflow.

Standalone Luma retains basic traceability, source preservation, uncertainty, corrections and honest completion reporting. Deeper admission, durable execution identity, managed activation and recovery belong to the supporting system when it actually supplies them. No engine can turn structural validity into a universal truth guarantee.

A proposed handshake needs to establish:

- Explicit integration mode and the capabilities actually available.
- Which owner is authoritative for each kind of retained state.
- How portable intentions such as retaining a finding or resuming work map to native operations.
- The relevant method revision, current work context, references and omissions.
- What happens when the integration is absent, unavailable or incompatible.

The host supplies that binding through its supported integration mechanism. A directory marker, source document or untrusted note must not announce itself as authority. The handshake is a bounded context and capability contract, not a request to inject the engine's entire manual.

In managed operation, readable files may be editable views or proposed contributions rather than accepted records. Human edits must survive reconciliation. An unavailable managed service must not silently convert pending managed changes into accepted standalone state or justify replaying an uncertain action. Independent ordinary work may continue where its authority and ownership are clear.

Source storage requires an explicit integration decision. Luma currently captures under `.agents/memory/<date-time>/`; coexistence with another owner's private state cannot be inferred from the shared name. Existing sources and runtime stores must remain protected until a reviewed import or coexistence rule exists. This document proposes no relocation.

Canonical ownership of the shared portable practices, exact handshake schema, storage coexistence, and managed attach/detach behavior belong in the separate Animus companion. They are not claimed implemented here.

## 10. Research conclusions

The research informs concrete mechanisms rather than a universal best prompt. Product documentation establishes described behavior; benchmark results establish narrower observations under named conditions. No reviewed source proves that this combined Luma seed outperforms its host.

| Evidence | Design implication | Important limit |
|---|---|---|
| Vercel's version-matched documentation-index experiment [R1] | Keep high-value retrieval routes reliably available | One Next.js task setting; not a universal victory of always-on text over skills |
| Repository context-file evaluation [R2] | Remove redundant overviews and instructions that add work without benefit | Coding benchmarks do not cover every value of personal continuity or memory |
| SkillsBench [R3] | Curate focused procedural packages and test them against no-skill conditions | Curated and self-generated skill experiments have different scopes; results vary by configuration |
| Anthropic's long-running-agent engineering [R4] | Externalize goals, verified progress and resumption state | A web-app implementation account, not proof that every domain needs its checklist |
| Agent Skills and OpenAI skill-evaluation guidance [R5], [R6] | Layer metadata, methods and resources; test selection separately from execution | A format or successful installation does not guarantee discovery or adherence |
| Hermes memory design and Pi extensibility [R7], [R8] | Separate retention jobs; preserve a small core with replaceable capabilities | Runtime hooks, search and automatic memory tools do not travel in Markdown alone |
| ACE and Reflexion [R9], [R10] | Keep experience-linked lessons and incremental, curated updates | Reflection depends on feedback and can assign the wrong cause |
| GEPA and Dynamic Cheatsheet [R11], [R12] | Evaluate prompt changes and selectively reuse applicable strategies | Optimizer trials and task-specific evaluation are not free facilities of an installed seed |
| LongMemEval and MemoryArena [R13], [R14] | Evaluate recall, updates and useful action separately | Neither evaluates the complete human-editable Luma workflow |

### Reconciled research threads

Always-on versus on-demand is not a binary choice: keep critical responsibilities and navigation visible, and retrieve detailed methods when relevant. The Vercel and context-file studies test different interventions and do not establish a universal optimal prompt size.

The paper revisions matter. SkillsBench v4 evaluates curated skills across 87 tasks, eight domains and 18 model-harness configurations; its self-generated-skill condition covers only three configurations and falls below the no-skill baseline in those conditions. Evaluating AGENTS.md v3 reports no significant overall performance effect and higher inference cost, not significant overall harm. Older inventories and stronger earlier wording should not be mixed into these conclusions.

Learning from experience is feasible through changed context and procedures, but automatic self-authorship is not evidence of benefit. Preserve feedback and evaluate later use rather than accumulating confident rules.

Portable files do not imply portable lifecycle behavior. Verify loading and capability use in each supported host. Hooks, scheduling, independent workers and automatic indexing remain optional runtime features.

The important unresolved questions now concern Luma itself: which guidance improves its target tasks, how much context is useful, whether saved understanding survives changed cases, and which host adapters reliably deliver the methods. Further literature alone cannot settle those questions.

## 11. Evaluation: what outperforming means

The target is a useful improvement over the same host and model without Luma, not a universal ranking of agents. Compare task success, retained fidelity, continuation, user intervention and total effort. More files, review steps, accepted tool calls or tokens are not success measures by themselves.

Use matched source material, model and host versions, permissions, task budgets and success criteria. Preserve the original request independently of the seed's plan. Include repeated runs and fresh cases not used to write the guidance. Report incomplete and failed runs rather than comparing only successful ones.

| Scenario | Observable result |
|---|---|
| Simple request | Direct useful answer without unnecessary planning, memory writes or delegation |
| Interrupted undertaking | Fresh session recovers the original outcome, decisions and unresolved work, then makes correct progress |
| Corrected evidence | Current answer and affected account change appropriately while relevant history and human edits remain recoverable |
| Source-backed synthesis | Important claims and qualifications are retained with actual support, not merely valid links |
| Experience transfer | A relevant lesson helps a changed task; a nearby non-applicable case does not inherit it blindly |
| User extension | A user-provided skill or tool is discovered and respected without destructive replacement |
| Resource update | Upstream improvement can coexist with local adaptations and known installation state |
| Limited host | Missing hooks, subagents or semantic search yield an honest, useful ordinary path where the task permits it |

Evaluate four different questions: should a practice be selected, was it selected, was it applied appropriately, and did the outcome improve? Include negative triggers and unnecessary-work cost. Relevant efficiency measures include model requests, tokens, tool calls, elapsed time and user correction effort, with preparation and indexing costs identified separately.

Start with a small representative set. Compare the native baseline with the complete standalone seed, then disable individual components to diagnose their contribution. Evaluate Animus-backed operation separately so engine support does not conceal weaknesses in the portable configuration. A learning test also needs a no-lesson comparison and unseen later tasks.

A favorable small result supports that configuration and task set. Broader compatibility and superiority remain qualified until exercised. Do not adopt a default that merely moves work into unmeasured setup or human review.

The first [matched evaluation](MATCHED-EVALUATION.md) exercised these distinctions on one configured OMP/model pair. Both arms passed all semantic checks across 16 invocations each; Luma used about 29% more processed tokens and 15% more tool calls. Both retained and correctly scoped an explicitly supplied lesson. This establishes no outcome advantage on that small, strongly cued set. The subsequent [longitudinal comprehension evaluation](CONTINUITY-EVALUATION.md) exposed missing retention and then stale accounts. Instruction diagnosis ruled out absent file-writing capability and showed that removing a host document rule alone did not activate the original seed. The retention implementation adds explicit initial-account and same-turn correction responsibilities. It demonstrated creation, qualified revision and fresh-session consultation in a post-failure regression and a different synthetic scenario, preserving no-write boundaries. Baselines still answered central source-based questions correctly, and original evidence remained available throughout. Broad reliability and an advantage attributable to memory remain unestablished; efficiency is secondary to establishing that capability advantage.

## 12. Proposed implementation sequence

### Phase A: package the portable core

Review the current working agreement and skills for duplication, contradictory routing and unnecessary ceremony. Define the compact core, preserve useful methods, and establish resource ownership and update provenance. Keep current source captures and user edits untouched.

Deliver a small seed that can be read and used manually under an ordinary file-capable host. Do not require a new service, graph store or fixed team. This phase is not authorization to remove an existing safeguard merely to shorten text.

### Phase B: exercise delivery and continuity

Implement only the thin adapters needed for initially selected hosts. Demonstrate installed versus loaded guidance, skill discovery, a saved memory recovered in a fresh session, and continuation after context loss. Preserve native configuration and existing instructions.

Record host/version limitations. Support explicit invocation or direct file reading when automatic selection is unavailable; do not claim equivalent independent review or managed recovery through a fallback.

### Phase C: evaluate and refine the seed

Run the matched tasks above, inspect the actual traces and artifacts, and change only guidance connected to observed failures or costs. Establish a small regression set for subsequent prompt and skill changes. Keep counterexamples and unsuccessful candidates.

### Phase D: bind the optional deeper system

Resolve the companion's ownership and handshake decisions, then implement and verify native integration separately. No populated workspace activation, historical migration, service launch or data import follows automatically from publishing this design.

## 13. Open design decisions

| Decision | Proposed starting position | Evidence or decision needed |
|---|---|---|
| Stable core content and size | Short purpose/continuity/selection contract with a compact index | Matched tasks and context-cost observation |
| Initial supported hosts | Small explicit set with ordinary file access and tested loading | Actual host versions, loaders and conformance runs |
| Shared portable source ownership | One canonical method source with versioned downstream consumption | Joint Luma/Animus packaging and local-adaptation plan |
| Source storage beside managed state | Preserve existing layouts; negotiate ownership explicitly | Companion's coexistence/import design and migration checks |
| Automatic local learning scope | Routine memory maintenance and bounded resource changes under standing policy | User-configurable resource ownership and later-use evidence |
| Evaluation coverage | Continuity, comprehension, correction, learning and extensibility, plus simple-task controls | A frozen initial task set and acceptable cost tradeoffs |
| Optional retrieval infrastructure | Add only for an observed retrieval problem | Corpus-specific quality and maintenance-cost comparison |

These are bounded decisions, not a requirement to finish a perfect architecture before building the seed. The first implementation should answer them through a small usable configuration and evidence from ordinary work.

## Research references

Public sources consulted for this design; performance claims remain scoped to their original experiments. Living documentation can change, so implementation work must recheck host-specific details.

- **R1.** Vercel, [AGENTS.md outperforms skills in our agent evals][R1]. A targeted version-matched documentation experiment.
- **R2.** [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?][R2], v3, September 2026. Repository context, task outcomes and inference cost.
- **R3.** [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks][R3], v4, June 2026. Curated-skill and separate self-generated-skill comparisons.
- **R4.** Anthropic, [Effective harnesses for long-running agents][R4]. Externalized state and incremental continuation.
- **R5.** [Agent Skills specification][R5]. Portable package format and progressive disclosure.
- **R6.** OpenAI, [Testing Agent Skills Systematically with Evals][R6]. Triggering, process, outcome and efficiency checks.
- **R7.** Nous Research, [Hermes persistent memory][R7]. Bounded curated memory and separate session retrieval.
- **R8.** [Pi coding-agent overview][R8]. Minimal extensible harness and optional capabilities.
- **R9.** [Agentic Context Engineering][R9], v3. Incremental playbook updates, reflection and curation; label-free adaptation still uses feedback.
- **R10.** [Reflexion][R10], v4. Linguistic feedback and episodic reflection without weight updates.
- **R11.** [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning][R11], v1. Trace-based prompt optimization with evaluator feedback, candidate selection and held-out evaluation.
- **R12.** [Dynamic Cheatsheet][R12], v1. Selective strategy reuse and self-curated context adaptation, with task-dependent benefits and failure risks.
- **R13.** [LongMemEval][R13]. Extraction, multi-session and temporal reasoning, updates and abstention.
- **R14.** [MemoryArena][R14]. Memory use in interdependent multi-session agentic tasks.

[R1]: https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
[R2]: https://arxiv.org/abs/2602.11988v3
[R3]: https://arxiv.org/abs/2602.12670v4
[R4]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[R5]: https://agentskills.io/specification
[R6]: https://developers.openai.com/blog/eval-skills
[R7]: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
[R8]: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md
[R9]: https://arxiv.org/abs/2510.04618v3
[R10]: https://arxiv.org/abs/2303.11366v4
[R11]: https://arxiv.org/abs/2507.19457v1
[R12]: https://arxiv.org/abs/2504.07952v1
[R13]: https://arxiv.org/abs/2410.10813
[R14]: https://arxiv.org/abs/2602.16313

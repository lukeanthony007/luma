# Luma agent resources

Start with the [working agreement](AGENTS.md). Luma uses these skills to help the user understand their material and maintain knowledge. It creates the user-facing wiki and inbox only when needed.

## Portable practices

Luma includes nine practices:

- [luma-setup](skills/luma-setup/SKILL.md): guided initial orientation from a project or idea to a useful first step.
- [luma-continuity](skills/luma-continuity/SKILL.md): purpose, current situation, temporal commitments, review and resumption.
- [luma-dream](skills/luma-dream/SKILL.md): reflection across wiki pages and sources, integrated synthesis and explicit proposals.
- [luma-wiki](skills/luma-wiki/SKILL.md): readable organization, source integration, retained discoveries and ongoing maintenance.
- [luma-inbox](skills/luma-inbox/SKILL.md): temporary messages and worksheets, response integration and cleanup.
- [luma-memory](skills/luma-memory/SKILL.md): evidence, uncertainty and correction discipline for retained knowledge.
- [luma-collab](skills/luma-collab/SKILL.md): bounded assignments and integration of actual contributions.
- [luma-config](skills/luma-config/SKILL.md): maintenance of instructions, tools, packages and configuration.
- [comprehension](skills/comprehension/SKILL.md): source-backed investigation, explanation and application.

The Skill files and their supporting references are canonical here. The root README routes agents to this directory's working agreement when `.agents/` is not processed automatically. Keep instruction files inside `.agents/` and guidance shared across harnesses without divergent copies. Native Skill discovery may need explicit configuration. No live cross-harness discovery test has been performed for this foundation.

## Provenance and scope

The five workspace and comprehension practices were selected from Luke Anthony's Animus `.agents/skills/` workspace on 2026-10-16. The source checkout's HEAD was `0a4bf670785434c096146fc9e10ca97d6885f586`; the embedded resource tree was local authored content, so that commit alone does not identify the exact imported files. `luma-wiki` and `luma-inbox` were authored for Luma from its knowledge and interaction design.

The memory, collaboration, configuration and comprehension Markdown trees were copied with their supporting references. The setup skill was rewritten for Luma as a guided conversation about the user's goals, useful applications of AI or automation, and a manageable first step. It retains existing-layout flexibility and creates the visible `wiki/` and `inbox/` only through their skills when needed. Setup, memory, collaboration and configuration now use Luma skill names. The old installer, checker, seed memory templates and setup agreement template were not imported. This repository's Git history records the selected content and adaptations.

Luma's wiki practice adapts the persistent Markdown synthesis pattern in [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and selected lifecycle ideas in [Rohit's extension](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2). It preserves human editing, source verification and explicit uncertainty. Numeric scoring, automatic decay, graph infrastructure and background automation are not requirements or implemented capabilities.

The organization practice takes knolling as a design influence, informed by [Kirsh's work on spatial cognition](https://adrenaline.ucsd.edu/kirsh/Articles/Space/AIJ1.html) and [Shipman and Marshall's work on spatial hypertext](https://people.engr.tamu.edu/shipman/spatialhypertext.html). Clear grouping, meaningful relationships and room for provisional understanding are design choices to assess in use; these sources do not establish psychological benefits for Luma.

`luma-continuity` adapts the purpose-and-time distinction from Animus's historical `docs/MOVEMENT-CONTINUUM.md` at revision `e4dfea1294`, particularly its temporal coordination and carryover sections. It follows the lighter practice described in `docs/WORK-AND-CONTINUITY.md` and the recovery boundaries in `docs/reference/RUNTIME-LIFECYCLE.md`, inspected at Animus revision `0a4bf670785434c096146fc9e10ca97d6885f586`. These are source provenance references, not dependencies on an Animus checkout. Luma retains readable context in the wiki; it does not implement the historical universal Movement graph or Animus's durable execution control.

`luma-dream` adapts Animus's `skills/dream/SKILL.md` and the Dream and evaluation sections of `docs/EXPERIENCE-AND-EVOLUTION.md`, inspected at revision `0a4bf670785434c096146fc9e10ca97d6885f586`. It retains bounded source selection, honest synthesis and proposals distinct from activation. The engine-specific `dream.synthesize`, accepted-frontier, current-Day and Movement-checkpoint contracts are not copied into Luma's portable method.

The agreement and skills adapt the portable workspace model. No Animus database, agent identity, credential, transcript, personal source collection, executable configuration or runtime package is included. Standup was not selected for this agent. Optional backend methods mentioned in comprehension references require a separately available host capability; these Markdown files do not provide one.

## Growing the workspace

Add tools, packages or specialist workspaces only for established needs. User-facing projects can remain at the root; agent implementation helpers can live here. Keep a single canonical resource and declare any external dependencies.

`.agents/memory/` is reserved for optional runtime-owned state and is excluded from Git. The current foundation does not create or initialize it. Source material and the editable wiki remain separate from internal runtime records. An Animus adapter must explicitly reconcile wiki changes with its accepted knowledge rather than treating two representations as competing authorities.

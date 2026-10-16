# Luma agent resources

Start with the [working agreement](AGENTS.md). Luma uses these skills to help the user understand their material and maintain knowledge. It creates the user-facing wiki and inbox only when needed.

## Portable practices

Luma includes seven practices:

- [luma-setup](skills/luma-setup/SKILL.md)
- [luma-memory](skills/luma-memory/SKILL.md)
- [luma-collab](skills/luma-collab/SKILL.md)
- [luma-config](skills/luma-config/SKILL.md)
- [comprehension](skills/comprehension/SKILL.md)
- [luma-wiki](skills/luma-wiki/SKILL.md)
- [luma-inbox](skills/luma-inbox/SKILL.md)

The Skill files and their supporting references are canonical here. The root README routes agents to this directory's working agreement when `.agents/` is not processed automatically. Keep instruction files inside `.agents/` and guidance shared across harnesses without divergent copies. Native Skill discovery may need explicit configuration. No live cross-harness discovery test has been performed for this foundation.

## Provenance and scope

The five workspace and comprehension practices were selected from Luke Anthony's Animus `.agents/skills/` workspace on 2026-10-16. The source checkout's HEAD was `0a4bf670785434c096146fc9e10ca97d6885f586`; the embedded resource tree was local authored content, so that commit alone does not identify the exact imported files. `luma-wiki` and `luma-inbox` were authored for Luma from its knowledge and interaction design.

The memory, collaboration, configuration and comprehension Markdown trees were copied with their supporting references. The setup entrypoint was adapted to create the visible `wiki/` and `inbox/` on demand, with existing-layout flexibility retained. Setup, memory, collaboration and configuration now use Luma skill names. The old installer, checker, seed memory templates and setup agreement template were not imported. This repository's Git history records the selected content and adaptations.

The agreement and skills adapt the portable workspace model. No Animus database, agent identity, credential, transcript, personal source collection, executable configuration or runtime package is included. Standup and Dream resources were not selected for this agent. Optional backend methods mentioned in comprehension references require a separately available host capability; these Markdown files do not provide one.

## Growing the workspace

Add tools, packages or specialist workspaces only for established needs. User-facing projects can remain at the root; agent implementation helpers can live here. Keep a single canonical resource and declare any external dependencies.

`.agents/memory/` is reserved for optional runtime-owned state and is excluded from Git. The current foundation does not create or initialize it. Source material and the editable wiki remain separate from internal runtime records. An Animus adapter must explicitly reconcile wiki changes with its accepted knowledge rather than treating two representations as competing authorities.

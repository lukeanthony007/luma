---
name: workspace-setup
description: Establish or repair a portable agent workspace without overwriting project work or causing unrequested side effects.
---

# Set up a workspace

Use when a durable agent working home is absent, incomplete, or needs deliberate repair. Inspect the requested destination and its parent before acting. Treat the selected user-facing directory as the workspace root; do not assume a hidden runtime directory or create one merely because the current directory is convenient.

## Inspect and preserve

Establish purpose, intended users, scope, environment, project conventions, ownership, and authority. List existing content before writing. Preserve custom instructions, definitions, memories, source records, and history unless revision is explicitly requested. Reconcile existing instructions with the proposed agreement; never replace user-authored files wholesale. If a conflict cannot be resolved from available records, preserve it and report the need for manual reconciliation.

Do not install, activate, execute, configure runtime, change permissions, fetch or publish content, commit, or perform external actions unless explicitly authorized. Setup does not authorize these actions. Adapt existing visible or embedded organization rather than imposing a new layout or overwriting user files.

## Canonical navigation

Use the owning workspace's canonical agreement as the authority for its structure and task practices. In this workspace, that agreement is [`.agents/AGENTS.md`](../../AGENTS.md), and user-facing knowledge is navigated from [`wiki/index.md`](../../../wiki/index.md) when present. The canonical portable skills live in `.agents/skills/`; route workspace setup, memory, bounded collaboration, resource maintenance, and comprehension to their applicable skills. The root `AGENTS.md`, if present, is only a discovery pointer. Ordinary work stays direct.

A useful workspace may contain user-authored material, `wiki/` for visible editable knowledge and navigation, and `.agents/` for agent instructions and resources. Optional nested agent workspaces may be used when the owner establishes them. These are conventions, not a requirement to create empty directories or a fixed metadata schema. Create records only when they have actual content; do not invent history, sample projects, commands, or environmental facts.

Source captures retain origin, revision/date when known, capture date, scope, completeness, and access limits when applicable. Derived pages distinguish source assertions, explanation/inference, unknowns, and qualifications; link to available support. Indexes link only to existing useful pages. Decisions identify authority and status. Logs, if useful, record material events without becoming transcript dumps.

## Optional discovery

Skills in `.agents/skills/` are canonical files, not evidence that any particular harness has discovered or activated them. A host may require explicit configuration for native discovery (including Claude); do not claim such configuration or installation unless it has actually been performed and checked. Keep links relative and usable without special runtime features.

## Tools and collaboration

Start with available tools. Add a helper only for an established need; explain exact inputs, effects, and limits. Do not install packages automatically. Child assignments, when useful or required, state purpose, bounded scope, relevant context, sources, method, expected result, limits, and handoff. Verify actual returned contributions; dispatch is not completion. Do not create investigator/critic teams by default.

## Handoff

Report what was inspected and changed, what was preserved, unresolved conflicts, and optional actions not taken. Distinguish written instructions from installed or activated behavior.

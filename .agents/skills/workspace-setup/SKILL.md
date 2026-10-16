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

Use the owning workspace's canonical agreement as the authority for its structure and task practices. In this workspace, that agreement is [`.agents/AGENTS.md`](../../AGENTS.md). Do not precreate `wiki/` or `inbox/`; [luma-wiki](../luma-wiki/SKILL.md) and [luma-inbox](../luma-inbox/SKILL.md) create them on demand for actual content. The canonical portable skills live in `.agents/skills/`. The root README provides the fallback route to `.agents/` guidance; do not create a root instruction file for Luma. Ordinary work stays direct.

Preserve user-authored material and existing organization. Add optional nested agent workspaces only when the owner establishes a distinct responsibility. Do not seed user knowledge, inbox messages, empty directories, placeholders or a fixed metadata schema. Create records only for actual useful content, with no invented history, sample projects, commands or environmental facts.

Source captures retain origin, revision/date when known, capture date, scope, completeness, and access limits when applicable. Derived pages distinguish source assertions, explanation/inference, unknowns, and qualifications; link to available support. Indexes link only to existing useful pages. Decisions identify authority and status. Logs, if useful, record material events without becoming transcript dumps.

## Optional discovery

Skills in `.agents/skills/` are canonical files, not evidence that any particular harness has discovered or activated them. A host may require explicit configuration for native discovery (including Claude); do not claim such configuration or installation unless it has actually been performed and checked. Keep links relative and usable without special runtime features.

## Tools and collaboration

Start with available tools. Add a helper only for an established need; explain exact inputs, effects, and limits. Do not install packages automatically. Child assignments, when useful or required, state purpose, bounded scope, relevant context, sources, method, expected result, limits, and handoff. Verify actual returned contributions; dispatch is not completion. Do not create investigator/critic teams by default.

## Handoff

Report what was inspected and changed, what was preserved, unresolved conflicts, and optional actions not taken. Distinguish written instructions from installed or activated behavior.

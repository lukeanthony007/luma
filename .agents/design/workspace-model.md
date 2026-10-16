# Workspace model

A Luma workspace is an ordinary directory serving one human goal, project, or collection of data. It is a place for people to keep material and for optional agentic practices to work with it; it is not itself a promise that software is installed or running.

## Principles and possible layout

The user-facing material stays visible and editable. An editable `wiki/` can hold explanations, connections, and questions that help someone return to work across sessions. It complements source material rather than silently replacing it.

An `inbox/` created on demand is a temporary interaction queue for agent messages, questions and structured worksheets. It supports deeper exchanges before useful understanding is retained in the wiki and the handled item is cleared. [luma-inbox](../skills/luma-inbox/SKILL.md) owns its operating practice.

A hidden `.agents/` directory can hold supporting guidance, skills, tools, or packages when useful. Guidance and resources could instead be located at the workspace root or embedded near relevant material. The exact filenames below are illustrative defaults, not a required schema; keep one canonical location for each resource and use references elsewhere rather than competing copies.

```text
workspace/
├── material/          # illustrative: sources, notes, project files
├── wiki/              # created when useful knowledge is retained
├── inbox/             # created when an interaction is needed
├── .agents/           # optional support resources
└── topic/             # ordinary folder unless explicitly marked as a child workspace
```

A child workspace is optional and should represent a meaningful distinct responsibility, not merely a subfolder. A workspace marker, if adopted, marks that child; `.agents/` is supporting configuration within a workspace, not a separate agent. Ordinary folders—including names such as `projects/`, `agents/`, or `packages/`—are not agents by themselves. Parentage describes where workspaces are arranged; it does not grant authority, access, or inherited permissions.

Relative references help workspace materials move together. Portability does not mean every harness automatically discovers or uses the workspace; moving files can still require link repair.

## Knowledge over time

User material and [wiki knowledge](../skills/luma-wiki/SKILL.md) have distinct roles: sources preserve what was supplied or observed, while the wiki holds maintained explanations supported by those sources.

Maintenance across sessions and justified revisions to methods are part of the workspace design. The operating practices live in the working agreement and its linked skills.

An authorized background agent or cron job can use the inbox to leave something for the person's next session. Its files are an interface to the work, not another long-term knowledge store. Scheduling, notifications and automated queue handling are not implemented by the directory itself.

## Harnesses and optional engines

Obsidian is the preferred human interface. Different harnesses vary in instruction precedence, skill discovery, tools, and child-work support. Entry files can direct a harness to the shared guidance, but actual loading and behavior need to be checked before claiming compatibility.

Animus is an optional, stronger engine that could operate with a workspace; it is not bundled as Luma's runtime. Its structured knowledge and accountability capabilities are distinct from plain editable Markdown. Integration must preserve human edits and explicitly reconcile accepted engine knowledge with authored workspace material. The workspace should remain understandable without Animus.

## Open design choices

The principles above do not yet define a required metadata schema, marker syntax, canonical resource filenames, file-watching behavior, or indexing/search strategy. Those are proposed design choices to evaluate against actual workflows, not current Luma features. No watcher, index, permission enforcement, plugin, or runtime is implied by this document.

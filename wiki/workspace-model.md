# Workspace model

A Luma workspace is an ordinary directory serving one human goal, project, or collection of data. It is a place for people to keep material and for optional agentic practices to work with it; it is not itself a promise that software is installed or running.

## Principles and possible layout

The user-facing material stays visible and editable. An editable `wiki/` can hold explanations, connections, and questions that help someone return to work across sessions. It complements source material rather than silently replacing it.

A hidden `.agents/` directory can hold supporting guidance, skills, tools, or packages when useful. Guidance and resources could instead be located at the workspace root or embedded near relevant material. The exact filenames below are illustrative defaults, not a required schema; keep one canonical location for each resource and use references elsewhere rather than competing copies.

```text
workspace/
├── material/          # illustrative: sources, notes, project files
├── wiki/              # illustrative: editable maintained knowledge
├── .agents/           # optional support resources
└── topic/             # ordinary folder unless explicitly marked as a child workspace
```

A child workspace is optional and should represent a meaningful distinct responsibility, not merely a subfolder. A workspace marker, if adopted, marks that child; `.agents/` is supporting configuration within a workspace, not a separate agent. Ordinary folders—including names such as `projects/`, `agents/`, or `packages/`—are not agents by themselves. Parentage describes where workspaces are arranged; it does not grant authority, access, or inherited permissions.

Prefer relative references between workspace materials so they can move together. Absolute machine paths and harness-specific identifiers undermine portability. If files move, references may need repair; portability does not mean every harness will automatically discover or use them.

## Knowledge over time

Keep source material distinct from derived knowledge. A source is what was read, observed, or supplied; a wiki explanation is an interpretation that should point back to relevant sources where practical. Preserve uncertainty and disagreement rather than turning a summary into a source or treating repeated summaries as independent evidence. Human edits to wiki pages remain authoritative as human-authored text; any optional integration that proposes revisions must reconcile with those edits explicitly rather than overwrite them.

Maintenance is part of the workspace: across sessions, revisit explanations when new evidence or changed goals matter, retain useful context in readable files, and revise methods when experience supports doing so. A future method revision is an authored change to guidance or skills, not an automatic learning guarantee. Keep the reason and relevant evidence legible, and leave unresolved questions unresolved.

## Harnesses and optional engines

Obsidian is the preferred human interface. Different harnesses vary in instruction precedence, skill discovery, tools, and child-work support. Entry files can direct a harness to the shared guidance, but actual loading and behavior need to be checked before claiming compatibility.

Animus is an optional, stronger engine that could operate with a workspace; it is not bundled as Luma's runtime. Its structured knowledge and accountability capabilities are distinct from plain editable Markdown. Integration must preserve human edits and explicitly reconcile accepted engine knowledge with authored workspace material. The workspace should remain understandable without Animus.

## Open design choices

The principles above do not yet define a required metadata schema, marker syntax, canonical resource filenames, file-watching behavior, or indexing/search strategy. Those are proposed design choices to evaluate against actual workflows, not current Luma features. No watcher, index, permission enforcement, plugin, or runtime is implied by this document.

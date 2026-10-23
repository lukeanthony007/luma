# Task briefs

A brief is a task sent from one party to another as a file. It is the structured form of an inbox interaction for bounded work. Use it when the work needs binding limits, named deliverables and a checkable return. For a conversational question, use an ordinary inbox item instead.

## Folder and file name

Briefs live in `.agents/briefs/`. One file per brief, named `YYYY-MM-DD-<slug>.md`, where the slug is `[a-z0-9-]{3,48}`. The `id` field equals the file name without `.md`. If `.agents/briefs/` does not exist, there are no briefs; do not create it just to look.

## Front matter

Strict YAML between `---` lines. Unknown fields are errors.

- `id`: `YYYY-MM-DD-<slug>`, equal to the file name without `.md`.
- `date`: `YYYY-MM-DD`, equal to the id prefix.
- `sender`: a person or accountable owner; never a run id, a session id, or `agent`, `runtime`, `harness`.
- `goal`: one sentence, 20 to 240 characters, no newline.
- `status`: `open`, `running`, `done` or `superseded`.
- `supersedes` (optional): the id of an existing brief; on archive that brief becomes `superseded`.
- `context`: a list of links only, workspace-relative paths or URLs.
- `scope.in`: plain phrases naming what is in scope.
- `scope.out`: plain phrases naming what is out of scope.
- `scope.write`: path prefixes the work may write under; `HANDOFF.md` in the run folder is always allowed.
- `scope.read` (optional): if present, reads are audited too.
- `constraints.spend_cap_usd`: number above 0.
- `constraints.wall_clock_s`: integer above 0.
- `constraints.tool_budget` (optional): integer above 0, per run.
- `constraints.no_push`: boolean, default true.
- `constraints.no_merge`: boolean, default true.
- `constraints.external_effects`: boolean, default false; true requires `approval`.
- `constraints.hosts` (optional): allowed hosts for this brief.
- `constraints.model` (optional): host model selector.
- `deliverables`: a list of `path`, `kind` (`file` or `dir`) and `description`; every path sits under a `scope.write` prefix.
- `success_criteria`: at least one, each checkable by reading the deliverables.
- `stop_conditions`: at least one; `spend cap` and `write outside scope` are always added.
- `report_back.handoff`: path, default `HANDOFF.md` in the run folder.
- `report_back.sections` (optional): extra headings required in the handoff beyond the collaboration return set.
- `approval` (optional): `by`, `at`, `spend_cap_usd` and an optional `note`; required when `constraints.external_effects` is true or the spend cap exceeds the workspace's approval line.
- `runs` (optional): run ids; written by a harness, not by hand.
- `archived_at` (optional): written by the archive command.

## Body

Exactly these headings, in this order: `## Goal`, `## Context`, `## Deliverables`, `## Report-back`, and optionally `## Corrections`. No other headings.

`## Context` is links only: at most one line per link in `context`, no pasted text, no fenced blocks, at most 40 lines. Put reasoning in `## Goal`.

Deliverables are written under `scope.write`. A deliverable outside it fails the check.

## Lifecycle

`open` is waiting for work. `running` means a run holds it and requires `runs` to be non-empty. `done` and `superseded` are final and are allowed only under `.agents/briefs/archive/YYYY/`. Archiving moves the file there, sets `archived_at`, flips any `supersedes` target to `superseded`, and regenerates the index.

`.agents/briefs/INDEX.md` is generated (`id | date | sender | status | goal | runs`, newest first, archived briefs included). Regenerate it; do not edit it by hand.

## Corrections

A correction is a dated, signed line under `## Corrections`: `- <date or timestamp> <from>: <text>`. Keep history; add a line rather than rewriting the brief. Senders and correctors may not be an agent, session or runtime name.

## Approval

A brief that allows external effects, or a spend cap above the workspace approval line, needs an `approval` block naming who approved, when, and the approved cap. An agent never writes its own approval. Relaying someone's approval belongs in `note`.

## Runs

`.agents/runs/<id>/` folders are run records written by a harness when one is installed; the seed does not write them. A run's `HANDOFF.md` is its return. Never write into a run folder you do not own. The folder is local state and Git-ignored.

## Validate

```sh
python3 .agents/tools/luma_brief.py check
python3 .agents/tools/luma_brief.py index
python3 .agents/tools/luma_brief.py archive <id> [--status done|superseded]
python3 .agents/tools/luma_brief.py new <slug> --sender <name>
```

`check` lists every error and exits 1 if any brief fails. A new skeleton fails only on goal, deliverables and success criteria until filled in. The tool is a vendored copy of the luma-harness validator; do not edit it by hand.

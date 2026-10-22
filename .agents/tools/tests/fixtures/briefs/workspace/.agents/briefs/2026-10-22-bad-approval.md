---
id: 2026-10-22-bad-approval
date: 2026-10-22
sender: luke
goal: Read five post-cutoff papers on agent memory and record one finding page per paper.
status: open
context:
  - docs/notes.md
  - https://arxiv.org/list/cs.AI/recent
scope:
  in: [agent memory papers]
  out: [code changes]
  write: [wiki/literature/**, inbox/]
constraints:
  spend_cap_usd: 25.0
  wall_clock_s: 3600
  no_push: true
deliverables:
  - path: wiki/literature/INDEX.md
    kind: file
    description: index of the five pages
success_criteria:
  - five pages, each with an expected and observed block
stop_conditions: [spend cap, two consecutive tool errors]
---

## Goal

Read the papers and write one page each.

## Context

- docs/notes.md, the reading list
- https://arxiv.org/list/cs.AI/recent query

## Deliverables

Five pages and an index under wiki/literature/.

## Report-back

HANDOFF.md with the collab return headings and one epsilon per paper.

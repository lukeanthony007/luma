---
id: 2026-10-22-harness-smoke-omp-print
date: 2026-10-22
sender: luke
goal: Smoke test the omp print-mode adapter by writing two short files and a handoff.
status: open
context:
  - .agents/AGENTS.md
  - .agents/skills/luma-inbox/references/briefs.md
scope:
  in: [a harness smoke test with two small files]
  out: [any other file, any git operation, any network access]
  write: [.agents/runtime/harness-smoke/omp-print/]
constraints:
  spend_cap_usd: 0.5
  wall_clock_s: 900
  tool_budget: 30
  no_push: true
  no_merge: true
  external_effects: false
  hosts: [omp]
  model: anthropic/claude-haiku-5-5
deliverables:
  - path: .agents/runtime/harness-smoke/omp-print/one.md
    kind: file
    description: one line naming the brief id
  - path: .agents/runtime/harness-smoke/omp-print/two.md
    kind: file
    description: one line naming the date
success_criteria:
  - both files exist and each holds one line
  - HANDOFF.md has every required heading
stop_conditions: [spend cap, write outside scope]
approval: {by: luke, at: 2026-10-22T16:18:00.000Z, spend_cap_usd: 0.5, note: "Approved in the harness build brief (decision 9, four paid smoke tests under 5 USD total), relayed by Grok Bot"}
---

## Goal

This is a smoke test of the Luma harness. Write the two deliverables below, then write HANDOFF.md. Keep every file short.

## Context

- .agents/AGENTS.md, the working agreement
- .agents/skills/luma-inbox/references/briefs.md, the brief contract

## Deliverables

1. `.agents/runtime/harness-smoke/omp-print/one.md`: one line with the brief id.
2. `.agents/runtime/harness-smoke/omp-print/two.md`: one line with today's date.

## Report-back

Write HANDOFF.md at the path the preamble gives, with every required heading. Under Findings say what you wrote. Under Changed files list the exact paths.

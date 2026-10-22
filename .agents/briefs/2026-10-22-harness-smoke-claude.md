---
id: 2026-10-22-harness-smoke-claude
date: 2026-10-22
sender: luke
goal: Smoke test the Claude Code adapter, including one steer by stop and resume, with two short files.
status: open
context:
  - .agents/AGENTS.md
  - .agents/skills/luma-inbox/references/briefs.md
scope:
  in: [a harness smoke test with two small files]
  out: [any other file, any git operation, any network access]
  write: [.agents/runtime/harness-smoke/claude/]
constraints:
  spend_cap_usd: 1.0
  wall_clock_s: 900
  tool_budget: 30
  no_push: true
  no_merge: true
  external_effects: false
  hosts: [claude]
  model: haiku
deliverables:
  - path: .agents/runtime/harness-smoke/claude/one.md
    kind: file
    description: one line naming the brief id
  - path: .agents/runtime/harness-smoke/claude/two.md
    kind: file
    description: one line naming the date, plus any word a steer asks for
success_criteria:
  - both files exist and each was written once
  - HANDOFF.md has every required heading
  - a steer during the run is honored after resume
stop_conditions: [spend cap, write outside scope]
approval:
  by: luke
  at: "2026-10-22T16:19:00.000Z"
  spend_cap_usd: 1.0
  note: "Luke approved four harness smoke tests under 5 USD total at 12:19 PM ET on 22 October 2026; Grok Bot relayed it on his call"
---

## Goal

This is a smoke test of the Luma harness. Write the two deliverables below, then write HANDOFF.md. Keep every file short.

## Context

- .agents/AGENTS.md, the working agreement
- .agents/skills/luma-inbox/references/briefs.md, the brief contract

## Deliverables

1. `.agents/runtime/harness-smoke/claude/one.md`: one line with the brief id.
2. `.agents/runtime/harness-smoke/claude/two.md`: one line with today's date. If a later message asks for a marker word, add it to this file's line.

## Report-back

Write HANDOFF.md at the path the preamble gives, with every required heading. Under Findings say what you wrote. Under Changed files list the exact paths.

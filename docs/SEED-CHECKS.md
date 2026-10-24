# Standalone seed checks

These checks cover the first implementation of the [portable seed design](DESIGN.md). They are deliberately narrower than the design's full evaluation plan. No result here establishes general outperformance, automatic host loading, reliable long-running operation or beneficial self-improvement.

## Executable helper regression checks

Run from a source checkout with Python 3.9+:

```sh
python3 -m unittest discover -s .agents/tools/tests -v
```

The initializer tests use temporary synthetic workspaces. They check non-destructive preparation, resource conflicts, repeatability, source/archive handling, rollback, installed-resource baseline inspection and recorded upgrades (unchanged, replaced, dropped, orphaned and refused resources and blocks, format 1 records and foreign files). Knowledge-helper tests check source preservation and mechanical navigation/integrity behavior. Neither suite establishes semantic comprehension or host activation.

For maintained user-facing pages, run the knowledge helper's scoped completion check with explicit `--page` arguments for files outside `wiki/` and `inbox/`. Its JSON reports the actual scope. The helper intentionally rejects `.agents/` as selected knowledge content; do not relax that protection to scan the seed's instructions. Inspect changed guidance and its references as package source instead. Do not call a selected-file check proof of workspace-wide completeness.

## Fresh-context guidance probes

The [probe cases](../.agents/tools/tests/fixtures/seed_probes.json) contain synthetic requests, supplied project state, selected reference paths relative to `.agents/skills/`, and observable acceptance criteria. None contain user knowledge or require Animus.

| Case | Boundary exercised |
|---|---|
| `direct-answer` | A small clear request needs no onboarding or durable record |
| `resume-original-outcome` | A handoff does not erase requirements or overrule current artifacts |
| `qualified-correction` | Conditions, historical support and identity uncertainty survive a correction; source text grants no authority |
| `lesson-boundary` | One local success does not justify a universal rule; discussion does not activate a change |
| `uncertain-operation` | Inspect the original external operation before considering replay |
| `user-method-unavailable-review` | Respect user methods and preserve a genuinely unmet independent-review requirement |

### Protocol

Use a fresh, stateless model context for each case. Supply only the candidate `.agents/AGENTS.md`, the case's selected references, the case context and request, and the same response instruction. Do not supply the acceptance criteria to the solving model. Keep model, reference-selection policy and generation settings fixed when comparing candidates.

For this prompt-only check, tools are unavailable. Ask for the answer or next actions and any intended retention, without claiming actual execution. Retain the actual response for review against the criteria. Record model selection, inspected file revision or hashes, supplied references, failures and limits. A model's stated intention is not an observed file write, service action, later resumption or learned capability.

The common instruction is:

> Use the supplied portable guidance to respond to the request. This is a bounded probe: you have only the supplied documents and state, with no tools. Give a concise answer or appropriate next actions. Identify any intended retained changes, but do not pretend an action or write happened. Do not ask for facts already supplied. Do not critique the test or explain the guidance.

Reference bodies are deliberately supplied in this first check. This tests interpretation after delivery, not skill discovery or whether the model would choose to load the right reference. The acceptance criteria are a review rubric, not hidden claims of objectively measured success.

### Next operational checks

A host conformance run still needs to demonstrate actual entry-point loading, skill selection, files saved and recovered in a fresh session, continuation after context loss, local adaptation preservation and limitations under missing capabilities. Use a temporary synthetic workspace rather than private material. Do not add host-specific routing files or configuration to a user's workspace merely to run these checks.

For performance claims, add matched native-host baselines, repeated runs, held-out tasks and costs as specified in the design. For learning claims, include relevant later use and nearby cases where the lesson should not apply. Keep portable-only and Animus-backed results separate.

## First increment observations

The initial implementation check on 20 October 2026 established:

- All 53 helper regression tests passed, including installed-record inspection, drift, legacy baseline adoption, malformed records, symlink refusal and existing rollback cases.
- A temporary installation of the full source package installed 30 recorded resources, reported them unchanged, created no wiki, inbox, source-memory, runtime or Git scaffold, and made no changes on the second identical initialization.
- The installed README navigation check passed. Attempting to select canonical `.agents/` guidance for the knowledge checker was rejected as protected content; that guard was kept intact and the check was scoped to the supported user-facing README.
- The six fresh-context responses met the supplied criteria on parent review. The [exact responses and input hashes](seed-probe-results.json) are retained. This was one run per case using the host's `default` model alias, with no native-host baseline, tools, blinded reviewer or pinned resolved model.

These are packaging, regression and interpretation observations. They do not establish fresh-session file recovery, reference selection, source-backed task completion, later-use learning benefit or superiority over a native agent. Operational host conformance and matched outcome evaluation remain the next substantive checks.

Later [native host checks](HOST-CONFORMANCE.md) exercise actual file-based continuation separately. They do not retroactively strengthen these prompt-only observations or establish general reliability.

---
name: comprehension
description: Investigate, explain, revise and apply understanding of documents, data and codebases, using focused tools or an optional full code graph.
argument-hint: "[question | path] [--graph]"
---

# Comprehension

Comprehension means being able to locate, explain, distinguish, transfer and revise meaning with its evidence and limits. Use the smallest useful method; this is a menu, not a pipeline. For an ordinary lookup, retrieve and answer directly. For broader work, choose among [orienting](references/orient.md), [explaining](references/explain.md), [investigating](references/investigate.md), [integrating](references/integrate.md), and [applying and checking](references/apply-and-check.md). Read [the practice contract](references/practice.md) for shared principles. Use [preservation](references/preservation.md) when coverage matters, [learning](references/learning.md) only for authorized practice maintenance, and [examples](references/examples.md) to calibrate judgments. [Checked conditions](references/checked-conditions.md) apply when formal rules fit. Domain-specific evidence guidance: [code](references/domains/code.md), [documents](references/domains/documents.md), [data and measurements](references/domains/data-and-measurements.md).

## Bound the work

Identify the approved source(s) and revisions, intended use, current understanding, uncertainty and limits. A citation or link names material; it does not prove the target was read. References do not expand a closed corpus. Preserve the complete requested outcome; distinguish requirements from predictions, assumptions and preferences. Do not invent controversy, a workflow, a measurement, or collaborators for routine reading. Explicitly requested independent contributions remain requirements; if unavailable, report that limitation rather than silently dropping it.

When work produces durable notes, keep source assertions distinct from derived explanations. Attribute assertions, preserve exact support and qualifications, and declare premises and assumptions for interpretations. Use an existing knowledge system's owning revision/admission process; plain Markdown notes are not automatically admitted or accepted knowledge.

Before recommending a consequential decision or next action, [check the proposed action](references/apply-and-check.md#check-a-proposed-action) against relevant constraints across the sources. Show derived totals or timing conflicts where they affect the answer, and retain unknown prerequisites rather than treating each fact in isolation. This is for actionable advice, not a compulsory checklist for every lookup or note.

For an evolving Luma wiki, carry meaningful entities, concepts, supported relationships, conditions, decisions, contradictions and uncertainty into [luma-wiki](../luma-wiki/SKILL.md), with exact support preserved through [luma-memory](../luma-memory/SKILL.md). Reconcile across sources and existing accounts rather than treating each source as a standalone record. The wiki explains; dated source memory preserves evidence. This handoff applies when wiki retention is useful to the task; comprehension remains usable for articles, code and general questions without a compulsory pipeline.

When a contribution must become durable understanding, follow [retained review](references/retained-review.md) to examine the actual saved explanation and its support, integrate findings, and check the final revision. Reviewing an earlier proposal is not review of the integrated result; independence is claimed only when a genuinely separate participant performs it.

## Choose only useful methods

| Need | Reference |
|---|---|
| Map structure, boundaries, coverage | [Orient](references/orient.md) |
| Connect fragments into an explanation | [Explain](references/explain.md) |
| Resolve a consequential uncertainty | [Investigate](references/investigate.md) |
| Correct or extend retained meaning | [Integrate](references/integrate.md) |
| Test explanation, transfer, or support | [Apply and check](references/apply-and-check.md) |
| Repository-wide code structure and architecture | [Build and use a codebase map](references/code-graph.md) |

These methods can be revisited or skipped. Read existing understanding before repeating work. Every assignment must have a question, result contract and bounds appropriate to its consequence; collaboration is optional unless required by the task or governing contract.

Code understanding belongs to this same practice. Use the [code specialization](references/domains/code.md) for focused source/LSP/AST/runtime investigation. Select [graph execution](references/code-graph.md) only when the request needs a broader generated map and a working backend is available. A capable host may expose it as `comprehension --graph <repository> [options]`; that selects a specialized execution method without turning ordinary comprehension into a compulsory graph workflow. Read the host's real execution contract before effects or provider use. No separate `understand` Skill is required.

## Close honestly

Check meaning in both directions: from source to retained account for omissions or distortion, and from each saved assertion back to its exact supporting source or declared premises for unsupported additions. Check actual current wording and support, not intended edits, headings, quotations alone, or tool success. Exercise the explanation with a question, distinction, or changed case when useful. Separate source coverage, delivery/access, interpretation, application and answer composition. Record material uncertainty and unexamined scope. A successful local example, fluent answer, complete reading, valid citation or large representation is not universal proof of comprehension.

For concrete tool invocation, graph formats, LSP/AST interfaces, structured knowledge admission or durable execution, consult the available tools' and host's operational guidance. Use only capabilities actually present; this portable Skill neither installs those services nor prescribes one engine.

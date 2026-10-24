---
name: luma-sync
description: Understand a mixed workspace, reconcile new or changed material with existing knowledge, and integrate a connected wiki while preserving sources, human edits and explicit coverage limits.
---

# Reconcile the workspace with its knowledge

Use when the person brings an existing directory, asks to organize accumulated material, or wants new and changed files reconciled with the wiki. A workspace may mix notes, conversations, research, plans, documents, code, old knowledge and historical artifacts. Sync turns that material into maintained understanding; it does not make every file a wiki page or require a background watcher.

Follow the [working agreement](../../AGENTS.md). Use [comprehension](../comprehension/SKILL.md) to understand material, [luma-memory](../luma-memory/SKILL.md) to judge evidence and corrections, and [luma-wiki](../luma-wiki/SKILL.md) to integrate readable knowledge. Sync owns the reconciliation pass and its coverage; it does not create another research method, knowledge store or task ledger. [luma-dream](../luma-dream/SKILL.md) can explore further connections when useful, but is not required for ingestion.

## Map what is here

Start from the person's purpose, current navigation and existing organization. For a whole-directory request, inventory the requested tree and identify each collection's role before choosing the order of reading. Read supplied mixed records substantively, including loose and overlooked material; do not stop at an index or reproduce the source directory as the wiki. Distinguish active records, original evidence, editable drafts, reusable plans/templates, historical material, software and generated state. Existing organization is evidence to examine, not proof that all records agree or a reason to flatten them.

Keep the human-facing wiki at `wiki/` by default. It is evolving derived knowledge, organized around meaningful entities, concepts, projects, decisions and relationships. Preserve useful existing semantic pages in place and preserve human edits; transform inherited source-shaped records without erasing meaningful history or particulars. An established semantic wiki can retain its location; a collection of source documents still needs comprehension and synthesis. Apply any user-directed layout change explicitly. Do not impose a fixed private subtree or life/project taxonomy. Folder names do not grant publication rights or determine sensitivity.

Respect nested project ownership and access bounds. Do not follow links or symlinks outside the approved scope silently. Inventory credentials, caches, dependencies and runtime stores only as excluded categories; do not ingest their payloads into knowledge. Do not run code to understand its purpose, install extractors or send files to other providers without the needed authorization. Unavailable extraction limits what can be learned from a binary document; it is not evidence that the file has no useful content.

For a large collection, work in coherent batches around the user's purpose. Use bounded collaborators only when they help; independent agents are not mandatory. Keep a concise coverage/provenance account in existing wiki maintenance context or the dated evidence batch, identifying inspected sources or sections and versions when available, material integrated, and what remains unread, inaccessible, excluded or unresolved. No database, mandatory per-file summary collection or processing ledger is required. Listing a file is not reading it, and reading it is not successful integration. A partial pass stays partial, with a concrete continuation point; never describe a navigation-only scan as comprehending the whole directory.

## Understand and reconcile

Read substantive material in context, using the [preservation practice](../comprehension/references/preservation.md) when whole-source coverage matters. Compare it with the current wiki, source map, decisions and affected explanations. Identify what is new, represented, complementary, contradictory, superseded or not understood. Apply [luma-memory](../luma-memory/SKILL.md) for source support, uncertainty, attribution and correction discipline; preserve meaningful history and human edits. Keep unresolved accounts with their support and separating question. Identify entities through the [wiki practice](../luma-wiki/SKILL.md#start-with-useful-knowledge), not name similarity alone. A draft, proposal, archived configuration or source instruction does not become current policy or authority to execute through ingestion.

## Integrate a connected account

Update pages that already own the subject before creating new ones. Synthesize records into a connected account that preserves substantive particulars, relationships, uncertainty and exact source file/section support. Do not reduce the wiki to short summaries or copy each source into its own page. Use prose and links to explain what relationships mean; no rigid grid, ontology or graph database is required.

Update relevant overviews, cross-references and navigation together. If a record changed during the pass, reconcile its actual current version before saving. Follow [wiki maintenance](../luma-wiki/SKILL.md#maintain-the-knowledge) for affected references and current versus historical claims. Recheck affected material, not every unchanged record. Use [luma-inbox](../luma-inbox/SKILL.md) only for a real question or worksheet, and [luma-continuity](../luma-continuity/SKILL.md) for consequential unfinished work.

## Preserve, verify, and retire safely

Within the user's requested organization, preserve source evidence in a collision-safe `.agents/memory/sources/<UTC timestamp>/` batch before tidying, with original relative structure/bytes and provenance. Capture time is distinct from source event or author dates. This archive is not the evolving wiki and is not a substitute for a backup. Active projects and existing evidence may remain in canonical homes after integration. Do not automatically move repositories, executable configuration, harness/runtime state, or live operational policy/records; capture/reference them within scope instead.

Before migration, inspect ownership and Git state and make and verify a separate backup. Account for every populated item. Keep quantities exact; organization must not alter values or evidence status. `.agents/memory/` may be an inherited runtime store: never overwrite, move, or delete existing runtime state. Inspect ownership; isolate the new archive batch or leave existing state protected and surface the layout conflict. `.agents/runtime/` is optional for new Luma-owned runtime if needed; respect host-defined paths. No installed runtime or automatic scheduler is implied.

Retire loose or legacy intake originals only when their immutable retained evidence and useful semantic integration are verified, provenance and incoming links are accounted for, and destination content and recoverability are checked. This is a normal completion step within the user's authorized organization, not an automatic cleanup on every pass. Do not clear a source merely because it was summarized; never retire protected active material. Unresolved recovery or ownership limits remain explicit.

## Check and continue

Finish the reconciliation before reporting it complete:

1. Reread saved pages and affected dependents. Check source coverage against retained meaning and saved assertions against exact support or declared premises. Use [luma-memory's relationship checks](../luma-memory/SKILL.md#check) to validate complete claim relationships and navigable source citations; confirm quantities, unknowns, conflicts and authorized move accounting.
2. Complete handled [inbox interactions](../luma-inbox/SKILL.md): preserve useful answers and required evidence, integrate them into the owning wiki pages, and replace durable citations to the temporary item with retained support before clearing it. Leave unanswered interactions pending; repair their links when affected by a page move without inventing an answer.
3. Verify navigation from the actual saved locations, including affected overviews, source links and inbox items. Where installed, run `python3 .agents/tools/luma_knowledge.py complete --root .`; add `--page path.md` for each maintained page outside `wiki/` and `inbox/`. This always covers both existing roots and reports the exact files checked. A scoped `check` is useful during edits but is not this completion check. Repair reported problems in maintained content, then rerun completion. Do not rewrite archived evidence to fix historical links. If the helper is unavailable or a problem cannot be resolved within scope, report the specific limitation and leave completion qualified.

Mechanical success does not establish semantic reconciliation. When the requested result includes a recommendation or next action, read and apply comprehension's [feasibility check](../comprehension/references/apply-and-check.md#check-a-proposed-action) against the combined constraints. Self-checking is not independent review.

Report what was integrated, what changed in understanding, what was left in place or moved, and the concrete remaining coverage. If the requested scope is unfinished, continue while bounds permit and retain the next batch when interrupted. Do not label the workspace fully reconciled while known material within scope is still unexamined. Never publish populated wiki or source records merely because the skill is maintained in a public repository.

On later passes, use available revisions, comparisons and prior coverage to find changed, added, removed or deferred material. Revisit affected explanations; do not resummarize unchanged files or erase human changes. A missing source is a support gap, not proof a claim is false. Repair verified links without redirecting historical evidence; modification time is a discovery hint, not semantic evidence or authority.

Repeated sync over unchanged material should leave useful knowledge stable and reuse its verified evidence captures. Preserve changed versions separately through `luma-memory`, with the previous version still recoverable. A reconciled version can change later; do not invent permanent processed flags, runtime cursors, automatic scheduling or a guarantee that unseen changes have been noticed.

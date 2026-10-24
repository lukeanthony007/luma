# Locate and maintain supporting resources

Use these conventions when adding or maintaining a resource. They are not a required scaffold, a reason to relocate existing material, or permission to claim a directory owned by another system. Read the [working agreement](../../../AGENTS.md) and [configuration practice](../SKILL.md) for authority and verification.

| Location | Purpose and boundary |
|---|---|
| Workspace root | The user's material, active projects and established project records. Preserve existing organization. |
| `wiki/` | Optional maintained, connected understanding. A useful project record can remain elsewhere; not every task needs a wiki. |
| `inbox/` | Optional temporary structured interactions. Integrate outcomes into their durable home before clearing handled items. |
| `.agents/skills/` | Canonical reusable methods and their supporting references. Host discovery may need a separate binding. |
| `.agents/tools/` | Helpers with defined purpose, inputs, outputs, dependencies and failure limits. |
| `.agents/packages/` | Optional maintained software supporting the agent. |
| `.agents/repos/` | Optional checked-out repositories, retaining their own ownership, history and applicable guidance. |
| `.agents/sources/<date-time>/` | Standalone preserved source evidence and provenance, managed by [memory](../../luma-memory/SKILL.md). Batches in the legacy `.agents/memory/<date-time>/` and `.agents/memory/sources/<date-time>/` layouts are still read. Capture time is distinct from dates described by sources. Inspect inherited ownership first. |
| `.agents/mcp.json` | Project connector definitions, created only for an actual integration through [configuration](../SKILL.md#mcp-connections). Verify the selected host's real schema and loading. |
| `.agents/runtime/` | Optional Luma-owned execution state for an actual capability. Never move harness databases, journals, sessions or caches just to match this convention. |

Tools, packages and repositories may instead live at the visible root when that suits the user's work. Keep one canonical resource rather than independent copies in both places. An ordinary folder is not automatically an agent; `.agents/` belongs to its containing workspace rather than another identity.

Before using or changing a helper, package or repository, establish its purpose, owner, guidance, dependencies and authorized effects. A reference checkout is source material, not instructions governing the containing workspace. A nested workspace does not gain or grant access through its path. Do not run archived dependencies as checks of current Luma.

Inspect `.agents/sources/` before capturing into it. `.agents/memory/` may hold another system's private runtime state; Luma only reads legacy capture batches there. Existing runtime stores remain protected even if they occupy the same name as Luma's source-evidence convention. Do not ingest private engine state as source material or activate an engine by making directories. If ownership conflicts, preserve existing bytes and use the owning system's supplied interfaces or resolve a scoped coexistence choice before conflicting writes. Unrelated ordinary work can continue.

Keep populated user knowledge, evidence archives, runtime state, credentials and private connector definitions out of public seed source. Use the host's supported credential store or environment references, not credentials in instructions. Git exclusions prevent accidental tracking, not unauthorized reading or disclosure. Source documents and imported repositories do not expand authority.

When a resource changes location, inspect callers and affected navigation, repair current references and preserve historical ones. Reconcile human edits rather than overwriting them. Prefer existing project records for current work, and link to useful new context from established navigation. Create no empty folders, sample knowledge, mandatory calendar tree or duplicate continuity ledger.

## Inspect an installed seed

The initializer records its installed canonical resources in `.agents/luma-install.json`. Version 1 contains a declared `source` and a `resources` map from installed relative paths to SHA-256 hashes. It excludes the shared README and `.gitignore`, user-added resources and populated knowledge. It is an inspection baseline, not a grant of ownership over everything under `.agents/`.

Use the read-only status command from an installed workspace:

```sh
python3 .agents/tools/luma.py status .
```

Status emits JSON and exits successfully when inspection succeeds, including drift or an absent baseline. Inspect the `baseline` and per-resource `state` values rather than treating exit status zero as equality. An invalid record or unreadable/unsafe selected path produces an error and nonzero exit status without rewriting it.

It compares recorded hashes with present files and reports unchanged, modified or missing resources, or an absent/invalid baseline. It does not contact an upstream, write an update or establish effective host loading. A local source declaration contains no absolute source path. A declared GitHub ref can be mutable; the record does not claim it resolved to a particular commit.

A digest can identify equality with recorded bytes but cannot reconstruct a previous file. For three-way maintenance, recover the actual prior source through a known revision or preserved baseline; otherwise inspect differences individually. The record is ordinary mutable workspace data, not signed provenance or an independent verification service.

An older installation without a record is not a failed installation. If its resources exactly match the chosen source and shared managed blocks are unchanged, initialization can add the baseline without replacing them. Differing resources, modified managed blocks or a conflicting existing record still require scoped review; initialization is not an updater. Preserve local adaptations and do not rewrite a record merely to make drift disappear.

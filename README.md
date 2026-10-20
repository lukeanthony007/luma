# Luma

Luma is a file-based personal knowledge management agent. It provides instructions, skills and tools for maintaining a source-backed Markdown wiki through an existing AI coding agent.

Obsidian-first and harness-agnostic. Designed for file-capable agents such as Codex and Claude Code, with no bundled model runtime or Obsidian plugin.

<a id="initialize-a-directory"></a>

## Initialize

Requires Python 3.9+, `curl` and an agent with local file access.

Run inside your target directory:

```sh
curl -fsSL https://raw.githubusercontent.com/lukeanthony007/luma/main/.agents/tools/luma.py | python3 - init
```

Then ask your agent:

> Read `.agents/AGENTS.md` and help me get started.

For an existing collection:

> Use luma-sync to reconcile this directory into a connected wiki. Preserve the original sources.

The initializer installs guidance and tools, adds README routing and configures local-record Git exclusions. Existing files are preserved. Conflicting managed resources stop installation before writes; identical installations make no changes.

## Workspace structure

| Path | Purpose |
|---|---|
| `wiki/` | Maintained understanding: subjects, relationships, decisions and open questions. |
| `inbox/` | Temporary messages and worksheets. Handled items are cleared after integration. |
| `.agents/memory/<date-time>/` | Preserved source evidence and provenance. |
| `.agents/skills/` | Reusable agent practices. |
| `.agents/tools/` | Workspace utilities. |
| `.agents/AGENTS.md` | Canonical working agreement. |

Directories are created on demand. Notes, documents and active projects can remain in the visible workspace. Optional packages and repositories retain their own ownership.

## Knowledge lifecycle

1. **Capture:** preserve selected sources with provenance.
2. **Comprehend:** identify claims, context, relationships and uncertainty.
3. **Reconcile:** compare new information with existing knowledge.
4. **Maintain:** revise affected wiki pages, decisions and source links.
5. **Resume:** recover purpose, progress and unresolved work across sessions.

The wiki is synthesized knowledge, not a relocated source collection. Original evidence remains separate and linked. Human edits and page names are preserved.

## Skills

- **Setup:** establish goals and identify useful applications of AI or automation.
- **Sync:** integrate new or changed material.
- **Memory:** preserve evidence and verify claim support.
- **Wiki:** maintain connected explanations and navigation.
- **Continuity:** retain purpose, progress and open commitments.
- **Dream:** develop supported connections and clearly identified proposals.
- **Inbox:** manage structured interactions.
- **Comprehension:** investigate documents, data and code.
- **Collaboration:** delegate bounded work and integrate results.
- **Configuration:** maintain guidance, tools and integrations.

The [working agreement](.agents/AGENTS.md) routes the agent to the relevant skill.

## Capture and check

Preserve explicit source files:

```sh
python3 .agents/tools/luma_knowledge.py capture --root . notes/source.md
```

Check wiki and inbox navigation together, plus captured evidence integrity:

```sh
python3 .agents/tools/luma_knowledge.py complete --root .
```

Add maintained pages outside those directories with `--page path.md`. JSON reports the exact checked scope. For a narrower edit-time check, use `check --root . path.md`; that result is not workspace completion.

Capture records UTC timestamps, paths and hashes. Unchanged verified sources are reused; changed sources receive separate versions. Originals remain in place.

Checks are mechanical. They do not establish factual accuracy, source relevance or completeness.

## Installation options

Preview installation:

```sh
curl -fsSL https://raw.githubusercontent.com/lukeanthony007/luma/main/.agents/tools/luma.py | python3 - init "/path/to/project" --dry-run
```

Install offline from a local checkout:

```sh
python3 .agents/tools/luma.py init --source . "/path/to/project"
```

For reproducible installation, pin both the downloaded script URL and `--ref` to the same commit. The initializer has no automatic update mode; installed guidance is reconciled through the configuration skill.

## Harness integration

**Agents: read [`.agents/AGENTS.md`](.agents/AGENTS.md) first.**

Instruction loading and skill discovery depend on the harness. Automatic discovery across harnesses has not been verified.

MCP configuration is created at `.agents/mcp.json` when needed, using the active harness's supported schema and authentication.

Luma does not configure models, initialize Git or activate background jobs. Search, scheduling and external integrations come from the host environment.

## Design direction

The [portable agent seed design](docs/DESIGN.md) proposes how Luma can support broader agent work through prompting, skills, memory, continuity, comprehension and learning from experience. It includes the research basis, evaluation plan and unresolved decisions. This is a design proposal, not a description of additional shipped capabilities.

## Status

Under active development. Automated checks cover supporting tools; behavioral evaluation remains limited. Reliable reconciliation and task completion across everyday workloads and different harnesses are not yet established.

## Previous version

The previous Obsidian plugin is retained on [`archive/obsidian-plugin`](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin).

## License

See [LICENSE](LICENSE).

# Luma

Luma is a portable agent seed: instructions, skills and small tools for useful work, source-backed understanding and continuity across sessions. It runs through an existing file-capable AI agent, with no bundled model runtime.

Use it directly on a question or project, add your own skills and tools, and retain what helps the next session. A Markdown wiki is optional and works with Obsidian or an ordinary editor. Animus is not required.

<a id="initialize-a-directory"></a>

## Initialize

Requires Python 3.9+ for the helpers and an agent with local file access. The download command also uses `curl`.

Run inside your target directory:

```sh
curl -fsSL https://raw.githubusercontent.com/lukeanthony007/luma/main/.agents/tools/luma.py | python3 - init
```

Then ask your agent:

> Read `.agents/AGENTS.md`, then help me with [your task].

If you need help finding a starting point, ask the agent to use luma-setup. For a collection you want organized:

> Use luma-sync to reconcile this directory into a connected wiki. Preserve the original sources.

The initializer installs guidance and tools, adds README routing and configures local-record Git exclusions. Existing files are preserved. Conflicting managed resources stop installation before writes; identical installations make no changes.

## Workspace structure

| Path | Purpose |
|---|---|
| `wiki/` | Optional connected understanding: subjects, relationships, decisions and open questions. |
| `inbox/` | Optional temporary messages and worksheets. Outcomes survive clearing handled items. |
| `.agents/memory/<date-time>/` | Preserved standalone source evidence and provenance. Inspect existing ownership first. |
| `.agents/skills/` | Reusable agent practices. |
| `.agents/tools/` | Workspace utilities. |
| `.agents/AGENTS.md` | Canonical working agreement. |

Directories are created on demand. Keep current work and continuity in established project records; a wiki is not a prerequisite. Optional packages and repositories retain their own ownership. Existing runtime state is never relocated merely to match this layout.

## Work and continuity

The working agreement keeps purpose, evidence, useful retention and honest completion available without imposing a fixed workflow. Detailed methods load when needed.

- **Work directly:** answer or act on the request using available tools and relevant skills, including your own.
- **Carry context:** save consequential decisions, verified progress and unfinished commitments in a discoverable project record. A later session reads it and checks present state before continuing.
- **Learn selectively:** distinguish new knowledge from method changes. Preserve the basis and conditions of a useful lesson, revise the owned resource within authorization, and check later use before claiming improvement.

For knowledge-building work, capture selected sources, comprehend and reconcile their meaning, and maintain connected explanations. A wiki is synthesis, not a relocated source collection. Original evidence stays separate and linked; human edits and meaningful history are preserved.

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

Inspect an installation without changing it:

```sh
python3 .agents/tools/luma.py status "/path/to/project"
```

The initializer records resource hashes and the declared source in `.agents/luma-install.json`. Status reports drift against that baseline, not whether a host loaded the guidance. The record is not a copy of the old source or signed provenance. Existing installations without a record remain usable; differing resources and local adaptations must be reconciled, not overwritten. See [installed-resource maintenance](.agents/skills/luma-config/references/resources.md#inspect-an-installed-seed).

## Harness integration

**Agents: read [`.agents/AGENTS.md`](.agents/AGENTS.md) first.**

Instruction loading and skill discovery depend on the harness. Start by explicitly reading the working agreement; a README link does not automatically load it. [Native host checks](docs/HOST-CONFORMANCE.md) demonstrated a bounded fresh-process continuation in Codex and OMP. Automatic core loading passed on the tested OMP configuration, but not Codex; broad cross-harness compatibility is not established.

Connector definitions are maintained through luma-config only for an actual integration. `.agents/mcp.json` is a workspace convention, not a universal host discovery path; native schema, loading and authentication must be checked.

Luma does not configure models, initialize Git or activate background jobs. Search, scheduling and external integrations come from the host environment.

## Design direction

The [portable agent seed design](docs/DESIGN.md) contains the research basis, proposed architecture, evaluation plan and open decisions. The standalone increment implements the portable entry point, on-demand practice routing, retention guidance and installed-resource inspection. [Seed checks](docs/SEED-CHECKS.md) and [native host checks](docs/HOST-CONFORMANCE.md) distinguish tested behavior from remaining limits. Persistent host adapters and Animus integration remain separate future work.

## Status

Under active development. Automated checks cover supporting tools; behavioral evaluation remains limited. The first [matched host/seed comparison](docs/MATCHED-EVALUATION.md) found equal outcomes on small synthetic tasks, with higher token and tool-call effort for Luma. Outperformance and reliable completion across everyday workloads and different harnesses are not established.

The first [longitudinal comprehension evaluation](docs/CONTINUITY-EVALUATION.md) found that the seed did not automatically create retained knowledge during the tested project-analysis workflow. Fixing and verifying that activation gap takes priority over efficiency: the intended advantage is connected, source-backed understanding applied in fresh sessions without the user reconstructing the context.

## Previous version

The previous Obsidian plugin is retained on [`archive/obsidian-plugin`](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin).

## License

See [LICENSE](LICENSE).

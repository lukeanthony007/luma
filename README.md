# Luma

Luma is an open-source personal knowledge management agent for your projects, ideas and everyday work. Give it a directory of material and a goal, and work with your AI agent to develop a clear, connected wiki that evolves with your understanding.

The workspace is yours: ordinary files, editable Markdown and room for whatever you are working on. Obsidian is the preferred interface for reading and editing the wiki. Luma supplies the instructions and skills; your existing agent supplies the model and tools.

## Initialize a directory

Requires Python 3.9 or newer, `curl` and an AI agent that can read and edit local files. Run this inside the directory you want Luma to help maintain:

```sh
curl -fsSL https://raw.githubusercontent.com/lukeanthony007/luma/main/.agents/tools/luma.py | python3 - init
```

Then open your agent in that directory and start with:

> Read `.agents/AGENTS.md` and help me get started with Luma. I'd like to talk through what I'm working on and where AI or automation could help.

You can begin with an empty folder, an unfinished idea or an existing collection of documents. The [setup skill](.agents/skills/luma-setup/SKILL.md) guides a conversation about your goal and helps you take a manageable first step. You do not need a technical plan or prepared brief.

For a directory that already contains material, try:

> Read `.agents/AGENTS.md` and use luma-sync to understand this workspace. Preserve the original references and build a connected wiki around what we learn.

These are starting prompts; continue in your own words.

## How the workspace works

Keep relevant notes, documents and projects in the visible directory. The agent uses [comprehension](.agents/skills/comprehension/SKILL.md) to understand their meaning, context and disagreements, then develops the wiki around the subjects and relationships that matter to your goal.

- **`wiki/` — evolving understanding.** Readable pages explain what is known, how ideas connect, what was decided and what remains uncertain. Edit them yourself or work on them with your agent.
- **`.agents/memory/<date-time>/` — original evidence.** Preserved references and provenance support the wiki's explanations and let you check where a claim came from.
- **`inbox/` — temporary interaction.** Messages, questions and structured worksheets give you space to respond or reflect. Handled items are cleared after useful understanding is retained.
- **`.agents/` — agent resources.** The working agreement, skills and optional tools support the work behind the visible workspace.

Wiki, inbox and evidence directories are created when there is useful content for them. Existing organization is respected, and active projects keep their ownership. The agent preserves and checks eligible source material before retiring it from the intake location. Evidence preservation complements your own backups.

The wiki is organized around understanding: a project page can connect a goal, several sources, a decision and an unresolved question. As new evidence arrives, the agent revises the explanation and affected pages. Original references remain available through source links.

This organization draws on **knolling**: distinguish the pieces, group related ideas and make their connections clear. The aim is to help you see what you have and what needs attention while keeping uncertainty visible.

## Keep working with it

Ask naturally for the help you need. The [working agreement](.agents/AGENTS.md) routes the agent to the relevant practice:

- [Setup](.agents/skills/luma-setup/SKILL.md) helps you find a starting point and explore useful applications of AI or automation.
- [Sync](.agents/skills/luma-sync/SKILL.md) reconciles new or changed material with current understanding.
- [Wiki](.agents/skills/luma-wiki/SKILL.md) maintains connected knowledge; [memory](.agents/skills/luma-memory/SKILL.md) preserves evidence and handles corrections.
- [Continuity](.agents/skills/luma-continuity/SKILL.md) carries purpose, progress and open commitments across sessions.
- [Dream](.agents/skills/luma-dream/SKILL.md) reflects across existing knowledge to develop supported connections and explicit proposals.
- [Inbox](.agents/skills/luma-inbox/SKILL.md) supports structured conversations and worksheets.
- [Comprehension](.agents/skills/comprehension/SKILL.md), [collaboration](.agents/skills/luma-collab/SKILL.md) and [configuration](.agents/skills/luma-config/SKILL.md) support investigation, bounded delegation and workspace maintenance.

For example, ask the agent to reconcile new research with a project, explain why a decision changed, or recover where you left off and identify the next useful action. These practices run through your agent when invoked; recurring work needs a separately configured and authorized scheduler.

## Installation details

The initializer downloads the current resources without cloning Git history or installing dependencies. It installs `.agents/AGENTS.md`, ten skills with their references, supporting tools and a license notice. It creates a short README or appends a guidance block to yours, and adds local-record exclusions to `.gitignore`.

Existing project files, MCP configuration and runtime state stay in place. An identical installation makes no changes. Differing managed resources stop the operation before target writes so you can review and merge them deliberately. For subsequent changes, ask your agent to [update installed guidance](.agents/skills/luma-config/SKILL.md#update-installed-guidance) from a selected Luma revision, preserving local adaptations. The initializer has no automatic update mode.

Append a target directory to `init` to choose another location, including a new folder. To preview the changes there:

```sh
curl -fsSL https://raw.githubusercontent.com/lukeanthony007/luma/main/.agents/tools/luma.py | python3 - init "/path/to/your project" --dry-run
```

From a local Luma checkout, an offline installation uses:

```sh
python3 .agents/tools/luma.py init --source . "/path/to/your project"
```

The remote commands run the script from `main`. You can inspect the [initializer source](.agents/tools/luma.py) before running it. For a reproducible installation, pin both the script URL and `--ref` to the same commit; `--ref` alone selects the resources, not the script already downloaded.

Initialization leaves Git setup, model configuration and connector activation to you and your agent. The generated Git exclusions cover local knowledge, evidence and configuration; they do not encrypt files or remove material already tracked by Git.

## Agents and integrations

**Agents: read [`.agents/AGENTS.md`](.agents/AGENTS.md) first.** It is the canonical working agreement. This README provides the route when your harness does not automatically read `.agents/`. Luma keeps its instructions there, without a root `AGENTS.md` or `CLAUDE.md`.

Luma is designed for use with file-capable agents such as Codex and Claude Code. Instruction loading and native skill discovery must be checked in each harness; universal automatic discovery has not been verified. The current package includes portable guidance and the initializer. The model runtime, search facilities and any background execution come from your chosen tools.

When an integration needs MCP tools, the agent creates and maintains `./.agents/mcp.json` through [luma-config](.agents/skills/luma-config/SKILL.md), checking the active harness's schema, loading and authentication. A fresh installation contains no empty MCP configuration or default server bundle.

Optional tools, packages, repositories and nested agent workspaces can support a project as it grows. Each keeps its own purpose and ownership; the working agreement describes their placement without requiring a fixed folder scheme.

Luma's workspace model comes from Animus. Luma provides the portable PKM structure and practices; an Animus integration can build on that foundation separately. Using Luma requires no Animus checkout or runtime.

## Provenance and scope

<details>
<summary>Design influences and adaptation history</summary>

The five workspace and comprehension practices were selected from Luke Anthony's Animus `.agents/skills/` workspace on 2026-10-16. The source checkout's HEAD was `0a4bf670785434c096146fc9e10ca97d6885f586`; the embedded resource tree was local authored content, so that commit alone does not identify the exact imported files. `luma-wiki` and `luma-inbox` were authored for Luma from its knowledge and interaction design.

The memory, collaboration, configuration and comprehension Markdown trees were copied with their supporting references. The setup skill was rewritten for Luma as a guided conversation about the user's goals, useful applications of AI or automation, and a manageable first step. It retains existing-layout flexibility and creates the visible `wiki/` and `inbox/` only through their skills when needed. Setup, memory, collaboration and configuration now use Luma skill names. The old installer, checker, seed memory templates and setup agreement template were not imported. This repository's Git history records the selected content and adaptations.

Luma's wiki practice adapts the persistent Markdown synthesis pattern in [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and selected lifecycle ideas in [Rohit's extension](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2). It preserves human editing, source verification and explicit uncertainty. Numeric scoring, automatic decay, graph infrastructure and background automation are not requirements or implemented capabilities.

The organization practice takes knolling as a design influence, informed by [Kirsh's work on spatial cognition](https://adrenaline.ucsd.edu/kirsh/Articles/Space/AIJ1.html) and [Shipman and Marshall's work on spatial hypertext](https://people.engr.tamu.edu/shipman/spatialhypertext.html). Clear grouping, meaningful relationships and room for provisional understanding are design choices to assess in use; these sources do not establish psychological benefits for Luma.

`luma-continuity` adapts the purpose-and-time distinction from Animus's historical `docs/MOVEMENT-CONTINUUM.md` at revision `e4dfea1294`, particularly its temporal coordination and carryover sections. It follows the lighter practice described in `docs/WORK-AND-CONTINUITY.md` and the recovery boundaries in `docs/reference/RUNTIME-LIFECYCLE.md`, inspected at Animus revision `0a4bf670785434c096146fc9e10ca97d6885f586`. These are source provenance references, not dependencies on an Animus checkout. Luma retains readable context in the wiki; it does not implement the historical universal Movement graph or Animus's durable execution control.

`luma-dream` adapts Animus's `skills/dream/SKILL.md` and the Dream and evaluation sections of `docs/EXPERIENCE-AND-EVOLUTION.md`, inspected at revision `0a4bf670785434c096146fc9e10ca97d6885f586`. It retains bounded source selection, honest synthesis and proposals distinct from activation. The engine-specific `dream.synthesize`, accepted-frontier, current-Day and Movement-checkpoint contracts are not copied into Luma's portable method.

The agreement and skills adapt the portable workspace model. No Animus database, agent identity, credential, transcript, personal source collection, executable configuration or runtime package is included. Standup was not selected for this agent. Optional backend methods mentioned in comprehension references require a separately available host capability; these Markdown files do not provide one.

</details>

## Previous implementation

The original Obsidian plugin is preserved on the separate [`archive/obsidian-plugin` branch](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin), at commit `dbfd14bcd1fb9b0deed36c94be382965bae56d78`. Its tracked files and history are unchanged. Its README, dependencies and installation instructions describe that historical implementation.

The plugin files are absent from the current `main` tree. Git history still contains earlier versions; use a shallow, single-branch clone to download only the current foundation:

```sh
git clone --depth 1 --single-branch --branch main https://github.com/lukeanthony007/luma.git
```

## License

See [LICENSE](LICENSE). The existing license text and notices are retained; the archive branch contains its original copy as well.

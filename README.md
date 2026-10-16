# Luma

Luma is an open-source personal knowledge management agent. It helps a person understand their material, maintain useful knowledge and pursue their goals through an ordinary directory of files.

Luma currently consists of portable instructions and skills used through an existing agent harness. It does not bundle a model runtime, search engine, background service, installer or Obsidian plugin.

## Start here

Start with what you are working on or hoping to achieve, even if you do not know where AI or automation could help. Direct your agent to [`.agents/AGENTS.md`](.agents/AGENTS.md). Through [luma-setup](.agents/skills/luma-setup/SKILL.md), it will talk through your situation, explain relevant possibilities and help you take a manageable first step. You do not need a technical plan or prepared documents. The agent creates `wiki/` and `inbox/` when needed; neither directory is included in a fresh checkout.

The intended experience is simple: keep relevant documents, notes and other material in a workspace; use the wiki to understand the project or subject; let a supported agent help maintain that understanding and the methods used to develop it. Obsidian is the preferred human interface, while the files remain ordinary Markdown and can be used with other editors.

For an existing directory of notes, research, documents and projects, ask the agent to [sync the workspace](.agents/skills/luma-sync/SKILL.md). It preserves original reference material in dated `.agents/memory/` batches and develops `wiki/` around the subjects, projects, decisions and relationships that matter. The wiki explains what the material means across sources; it evolves as evidence, goals and human contributions change. It does not inherit the source directory as its structure. The agent reports coverage and uncertainty, and retires eligible intake only after preservation and integration checks. Active projects and harness state retain their ownership.

Comprehension recovers meaning, context and disagreement. Knolling makes that understanding readable: distinguish the pieces, group related ideas and explain their connections. Source links let the reader inspect the evidence without making the originals the wiki. A dated evidence archive supports this process; it is not an independent backup.

The optional `inbox/` gives agents a temporary space for messages, questions and structured worksheets, including handoffs from authorized background work. The person can respond there or in conversation. Handled items are cleared after useful understanding is retained in the wiki. These practices live in the [luma-wiki](.agents/skills/luma-wiki/SKILL.md) and [luma-inbox](.agents/skills/luma-inbox/SKILL.md) skills.

The visible workspace belongs to the person. Agent guidance and reusable practices live under `.agents/`; [the working agreement](.agents/AGENTS.md) covers their organization. Tools, packages and nested agent workspaces can be added when needed. Existing organizations should be accommodated; the design does not require a fixed set of project or lifestyle folders.

## Agent resources

Agents should read and follow [`.agents/AGENTS.md`](.agents/AGENTS.md), the canonical working agreement. If the harness does not automatically process `.agents/`, use this README as the route to that guidance. Instruction files stay inside `.agents/`; no root instruction file is needed. Skills are maintained in `.agents/skills/`; follow the working agreement to select them. These files provide guidance, not a running integration. Instruction loading and native Skill discovery still need verification in each supported harness.

When a useful integration needs MCP tools, the agent creates and maintains `./.agents/mcp.json` through [luma-config](.agents/skills/luma-config/SKILL.md). The file belongs to that workspace; a fresh checkout includes no empty configuration or default server bundle. The active harness's schema, discovery and authentication still need checking.

## Provenance and scope

The five workspace and comprehension practices were selected from Luke Anthony's Animus `.agents/skills/` workspace on 2026-10-16. The source checkout's HEAD was `0a4bf670785434c096146fc9e10ca97d6885f586`; the embedded resource tree was local authored content, so that commit alone does not identify the exact imported files. `luma-wiki` and `luma-inbox` were authored for Luma from its knowledge and interaction design.

The memory, collaboration, configuration and comprehension Markdown trees were copied with their supporting references. The setup skill was rewritten for Luma as a guided conversation about the user's goals, useful applications of AI or automation, and a manageable first step. It retains existing-layout flexibility and creates the visible `wiki/` and `inbox/` only through their skills when needed. Setup, memory, collaboration and configuration now use Luma skill names. The old installer, checker, seed memory templates and setup agreement template were not imported. This repository's Git history records the selected content and adaptations.

Luma's wiki practice adapts the persistent Markdown synthesis pattern in [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and selected lifecycle ideas in [Rohit's extension](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2). It preserves human editing, source verification and explicit uncertainty. Numeric scoring, automatic decay, graph infrastructure and background automation are not requirements or implemented capabilities.

The organization practice takes knolling as a design influence, informed by [Kirsh's work on spatial cognition](https://adrenaline.ucsd.edu/kirsh/Articles/Space/AIJ1.html) and [Shipman and Marshall's work on spatial hypertext](https://people.engr.tamu.edu/shipman/spatialhypertext.html). Clear grouping, meaningful relationships and room for provisional understanding are design choices to assess in use; these sources do not establish psychological benefits for Luma.

`luma-continuity` adapts the purpose-and-time distinction from Animus's historical `docs/MOVEMENT-CONTINUUM.md` at revision `e4dfea1294`, particularly its temporal coordination and carryover sections. It follows the lighter practice described in `docs/WORK-AND-CONTINUITY.md` and the recovery boundaries in `docs/reference/RUNTIME-LIFECYCLE.md`, inspected at Animus revision `0a4bf670785434c096146fc9e10ca97d6885f586`. These are source provenance references, not dependencies on an Animus checkout. Luma retains readable context in the wiki; it does not implement the historical universal Movement graph or Animus's durable execution control.

`luma-dream` adapts Animus's `skills/dream/SKILL.md` and the Dream and evaluation sections of `docs/EXPERIENCE-AND-EVOLUTION.md`, inspected at revision `0a4bf670785434c096146fc9e10ca97d6885f586`. It retains bounded source selection, honest synthesis and proposals distinct from activation. The engine-specific `dream.synthesize`, accepted-frontier, current-Day and Movement-checkpoint contracts are not copied into Luma's portable method.

The agreement and skills adapt the portable workspace model. No Animus database, agent identity, credential, transcript, personal source collection, executable configuration or runtime package is included. Standup was not selected for this agent. Optional backend methods mentioned in comprehension references require a separately available host capability; these Markdown files do not provide one.

## Previous implementation

The original Obsidian plugin is preserved on the separate [`archive/obsidian-plugin` branch](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin), at commit `dbfd14bcd1fb9b0deed36c94be382965bae56d78`. Its tracked files and history are unchanged. Its README, dependencies and installation instructions describe that historical implementation.

The plugin files are absent from the current `main` tree. Git history still contains earlier versions; use a shallow, single-branch clone to download only the current foundation:

```sh
git clone --depth 1 --single-branch --branch main https://github.com/lukeanthony007/luma.git
```

## License

See [LICENSE](LICENSE). The existing license text and notices are retained; the archive branch contains its original copy as well.

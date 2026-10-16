# Luma

Luma is an open-source foundation for agentic personal knowledge management: an ordinary directory containing a person's working material, an editable wiki, and the resources an agent uses to help maintain them toward a purpose.

This repository begins a ground-up redesign. It currently contains the workspace design and portable agent practices. It does not yet ship a new Obsidian plugin, installer, search engine, background service or model runtime.

## Start here

Read the [wiki](wiki/index.md) for the current direction and the [workspace model](wiki/workspace-model.md) for the design under discussion.

The intended experience is simple: keep relevant documents, notes and other material in a workspace; use the wiki to understand the project or subject; let a supported agent help maintain that understanding and the methods used to develop it. Obsidian is the preferred human interface, while the files remain ordinary Markdown and can be used with other editors.

The [inbox](inbox/README.md) gives agents a temporary space for messages, questions and structured worksheets, including handoffs from authorized background work. The person can respond there or in conversation. Once the agent has handled an item and retained useful understanding in the wiki, it clears the item.

The visible workspace belongs to the person. Agent guidance and reusable practices live under [`.agents/`](.agents/README.md). Tools, packages and nested agent workspaces can be added when needed. Existing organizations should be accommodated; the design does not require a fixed set of project or lifestyle folders.

## Working on Luma

Agents should start with [AGENTS.md](AGENTS.md), the sole root instruction entrypoint, which points to the [canonical working agreement](.agents/AGENTS.md). Skills are maintained in `.agents/skills/`; follow the working agreement to select them. These files provide guidance, not a running integration. Instruction loading and native Skill discovery still need verification in each supported harness.

This repository is Luma's own development workspace. Its wiki describes Luma. It is not yet an installer that should be copied wholesale into someone's personal vault.

Luma is derived from the portable agent-workspace design developed in Animus. The [resource provenance](.agents/README.md#provenance-and-scope) explains the selected practices. Animus's private state and formal intelligence, accountability, continuity and execution systems are not included. An optional Animus integration will need an explicit boundary for wiki updates and accepted engine knowledge.

## Previous implementation

The original Obsidian plugin is preserved on the separate [`archive/obsidian-plugin` branch](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin), at commit `dbfd14bcd1fb9b0deed36c94be382965bae56d78`. Its tracked files and history are unchanged. Its README, dependencies and installation instructions describe that historical implementation.

The plugin files are absent from the current `main` tree. Git history still contains earlier versions; use a shallow, single-branch clone to download only the current foundation:

```sh
git clone --depth 1 --single-branch --branch main https://github.com/lukeanthony007/luma.git
```

## License

See [LICENSE](LICENSE). The existing license text and notices are retained; the archive branch contains its original copy as well.

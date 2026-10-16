# Luma

Luma is an open-source personal knowledge management agent. It helps a person understand their material, maintain useful knowledge and pursue their goals through an ordinary directory of files.

Luma currently consists of portable instructions and skills used through an existing agent harness. It does not bundle a model runtime, search engine, background service, installer or Obsidian plugin.

## Start here

Start with what you are working on or hoping to achieve, even if you do not know where AI or automation could help. Direct your agent to [`.agents/AGENTS.md`](.agents/AGENTS.md). Through [luma-setup](.agents/skills/luma-setup/SKILL.md), it will talk through your situation, explain relevant possibilities and help you take a manageable first step. You do not need a technical plan or prepared documents. The agent creates `wiki/` and `inbox/` when needed; neither directory is included in a fresh checkout.

The intended experience is simple: keep relevant documents, notes and other material in a workspace; use the wiki to understand the project or subject; let a supported agent help maintain that understanding and the methods used to develop it. Obsidian is the preferred human interface, while the files remain ordinary Markdown and can be used with other editors.

The optional `inbox/` gives agents a temporary space for messages, questions and structured worksheets, including handoffs from authorized background work. The person can respond there or in conversation. Handled items are cleared after useful understanding is retained in the wiki. These practices live in the [luma-wiki](.agents/skills/luma-wiki/SKILL.md) and [luma-inbox](.agents/skills/luma-inbox/SKILL.md) skills.

The visible workspace belongs to the person. Agent guidance and reusable practices live under [`.agents/`](.agents/README.md). Tools, packages and nested agent workspaces can be added when needed. Existing organizations should be accommodated; the design does not require a fixed set of project or lifestyle folders.

## Agent resources

Agents should read and follow [`.agents/AGENTS.md`](.agents/AGENTS.md), the canonical working agreement. If the harness does not automatically process `.agents/`, use this README as the route to that guidance. Instruction files stay inside `.agents/`; no root instruction file is needed. Skills are maintained in `.agents/skills/`; follow the working agreement to select them. These files provide guidance, not a running integration. Instruction loading and native Skill discovery still need verification in each supported harness.

Luma is derived from the portable agent-workspace design developed in Animus. The [resource provenance](.agents/README.md#provenance-and-scope) explains the selected practices. Animus's private state and formal intelligence, accountability, continuity and execution systems are not included. An optional Animus integration will need an explicit boundary for wiki updates and accepted engine knowledge.

## Previous implementation

The original Obsidian plugin is preserved on the separate [`archive/obsidian-plugin` branch](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin), at commit `dbfd14bcd1fb9b0deed36c94be382965bae56d78`. Its tracked files and history are unchanged. Its README, dependencies and installation instructions describe that historical implementation.

The plugin files are absent from the current `main` tree. Git history still contains earlier versions; use a shallow, single-branch clone to download only the current foundation:

```sh
git clone --depth 1 --single-branch --branch main https://github.com/lukeanthony007/luma.git
```

## License

See [LICENSE](LICENSE). The existing license text and notices are retained; the archive branch contains its original copy as well.

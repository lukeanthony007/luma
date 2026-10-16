# Luma design notes

Luma is an open-source starting point for agentic personal knowledge management: an ordinary, human-readable workspace for a goal, project, or collection of material. It is intended to work Obsidian-first while remaining harness-agnostic. People own and edit the material; agent guidance and supporting resources live alongside it rather than replacing it.

## What exists now

This repository currently contains documentation and portable practices. It does not provide an installed Obsidian plugin, agent runtime, or CLI. The original plugin is preserved unchanged on the separate [`archive/obsidian-plugin` branch](https://github.com/lukeanthony007/luma/tree/archive/obsidian-plugin); it is historical reference and is absent from the current main tree.

The design principles and illustrative layout are in [Workspace model](workspace-model.md). See the [repository README](../../README.md) for the project entry point and instructions for a small clone without historical plugin files.

## Starting principles

A workspace serves one human goal, project, or collection. The agent creates `wiki/` for maintained understanding and `inbox/` for temporary interactions only when needed. Neither folder nor any placeholder is shipped in a fresh checkout. Supporting resources live in `.agents/`; the [luma-wiki](../skills/luma-wiki/SKILL.md) and [luma-inbox](../skills/luma-inbox/SKILL.md) skills own their operating practices. Optional marked child workspaces can organize distinct responsibilities; nesting and ordinary folder names imply neither permissions nor agency.

## Decisions still open

The principles do not settle exact filenames and defaults, a metadata schema, whether or how to watch files, or how to index and search material. Harness-specific instruction discovery and execution require real adapters and checks; portable Markdown alone does not establish compatibility. These questions should be resolved through concrete use rather than presented as implemented features.

## Example of use

Someone pursuing a learning goal might keep notes and readings as visible material and use the wiki to connect concepts and record questions. A reference collection might organize source documents and editable summaries, keeping conclusions traceable to what informed them. A software project might retain its existing source tree and docs, with wiki pages for architecture and investigation notes. If a distinct responsibility merits a child workspace, it can be marked explicitly; otherwise project or subject folders remain ordinary folders. In each case, optional `.agents/` resources could provide practices or tools when available, but do not make an agent run or grant access. The examples describe possible organization, not deployed Luma installations or demonstrated results.

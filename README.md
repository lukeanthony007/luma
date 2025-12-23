## Description

An Obsidian plugin that indexes and retrieves notes via local embeddings—semantic search, entity linking, and knowledge graph overlays without cloud dependencies.

## Skills / Tools / Stack

- TypeScript
- LangChain
- Vector Embeddings
- Retrieval Augmented Generation
- Obsidian Plugin Development

# Summary

Luma is an Obsidian-native AI engine that reads, understands, and organizes your Markdown notes directly within your vault. Journals, dreams, thoughts, poetry—it transforms them into a private, searchable memory system running 100% locally on your device.

No cloud. No proprietary formats. No telemetry. Xenova handles vectorization client-side. The RAG pipeline takes queries, finds relevant chunks, and synthesizes responses. Cosine similarity clusters related notes automatically, surfacing connections you missed.

Built for knowledge workers drowning in notes. Ask questions like "What was I working on last March?" or "Dreams about falling and flying" get relevant context in seconds instead of manual searching.

## Features

- Obsidian-first integration—works directly on your vault with zero migration
- 100% local operation via Xenova embeddings, no external API calls
- Semantic search across all note types with natural language queries
- Entity linking connects people, places, moods, and motifs into a living graph
- Lifestyle-agnostic parsing handles nonlinear, fragmented, and poetic notes
- RAG-powered retrieval combines symbolic, keyword, and vector search
- Markdown stays human-readable and portable without the plugin installed
- Memory, dream, and person note schemas with structured frontmatter
- Non-invasive design—Luma never alters your original notes

### Roadmap

1. Add incremental indexing for large vaults
2. Implement conversation interface for multi-turn knowledge queries
3. Build mood and theme tracking over time
4. Create export tools for structured knowledge graphs
5. Support additional local LLM backends beyond Xenova

### Instructions

1. Download the latest release from GitHub
2. Extract to your Obsidian vault's `.obsidian/plugins/luma` folder
3. Enable the plugin in Obsidian settings under Community Plugins
4. Run initial indexing from the command palette
5. Use the Luma search command or sidebar to query your vault

### License

MIT

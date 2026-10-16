# Build and use a codebase map

This is an optional code-comprehension method, not another Skill or a prerequisite for reading code. Use it when the requested outcome needs a repository-wide architecture map, cross-module dependency analysis, an incremental map refresh, or a navigable graph for continuing work. For a focused question, use the [code investigation procedure](domains/code.md) directly.

## Select the scope and execution capability

1. Establish the question, repository and revision, intended graph use, required coverage, exclusions, output owner and available time/resources. Distinguish a requested full map from a bounded trace. Preserve the original requested outcome when choosing stages.
2. Inspect the available backend before relying on it. Full analysis needs working inventory/parsing/import-resolution tools, semantic interpretation, graph validation and an output/admission path. Exact LSP checks may strengthen unresolved relationships. A tool name or available Skill file does not establish that these capabilities or their dependencies are active.
3. Where the host implements graph execution, select it through `comprehension --graph <repository> [options]`. This is a Skill invocation with arguments, not a universal shell command. Use the selected host's actual invocation syntax, option schema, execution limits and recovery instructions. The ordinary comprehension method remains suitable for research and focused code questions without graph execution.
4. If the backend is unavailable, state that boundary. Continue authorized focused investigation when it meets the request, but do not label a manually sketched or smaller map as the requested full analysis. Do not install dependencies, enable providers, change configuration or create a child team merely because this reference was read.

## Acquire structure without pretending it is meaning

- Analyze an identified source revision or snapshot. Preserve the relevant source bytes and locators when authorized, and record omissions. Exclude unrelated private memory, credentials, generated output and other agents' private workspaces; nesting is not an access grant. Dependency or generated-code boundaries that matter to behavior remain explicit unknowns rather than silently disappearing from the explanation.
- Inventory actual files and their roles: production, tests, fixtures, configuration, documentation, generated or legacy. Locate entry points, manifests, imports, declarations and structural relationships with appropriate parsers. Record the parser/language coverage and unresolved targets. A lexical name match is not a resolved symbol edge.
- Resolve consequential ambiguity with the available language server's definition, reference, implementation and type queries, then read the returned code in context. Preserve exact-symbol, file-level and conceptual precision distinctly. An import edge does not itself establish a call, and a static call possibility does not establish runtime execution.

## Develop the connected explanation

Use the structural evidence to explain component responsibilities, control/data paths, state transitions, interfaces and cross-module dependencies. Semantic descriptions are interpretations of inspected source, not new parser facts. Attach supporting regions and distinguish inferred relationships, alternatives, limitations and counterevidence. Bring configuration and external-service assumptions into the account when they change behavior.

For a large repository, bounded file groups and neighbor/interface context can help. Give each participant its actual source scope, output contract and relevant context; separate output ownership and reserve effort for integration. If the harness cannot delegate, use a serial method and identify it honestly. Do not invent independent review or imply every group was examined because a queue exists.

Keep the useful derived views—architecture layers, dependency paths or a guided tour—connected to the same source basis. A readable tour does not repair a missing input, wrong edge or unexamined subsystem. Graph size and file counts are inventory measures, not comprehension scores.

## Validate, retain and apply

Check the output format and reference consistency through the backend's real validators. Separately examine consequential edges and explanatory clauses against source: parser-derived, LSP-confirmed and semantically inferred relationships have different support. Check source-to-map omissions as well as map-to-source additions. For claims about actual behavior, exercise a relevant runtime scenario or inspect a trace when authorized; retain the distinction between static analysis and that observed run.

Publish or retain the actual graph, source/revision basis, meaningful explanations, coverage and unresolved questions using the workspace's available mechanisms. A plain harness can maintain a navigable Markdown account and links to generated artifacts; a structured knowledge system may admit supported findings through its own boundary. Neither a successful file write nor valid graph admission proves semantic adequacy.

Use the map to answer the original question and at least one consequential navigation/application need when appropriate. Explain what it enables, where direct source inspection remains necessary, and which conclusions are unsupported. Do not replace the requested explanation with a message saying analysis completed.

## Refresh and recover

Key reusable outputs to source content and relevant tool/method versions. Reuse unchanged validated structure where the backend supports it; changed file membership, imports, symbols, configuration or method conditions can invalidate related views. Inspect the actual affected dependencies instead of assuming a commit hook makes every conclusion current. Preserve prior interpretations and refresh the owning current account.

Recover an interrupted job through its owning run, snapshot, dispatch and settled output records. A persisted result should not be regenerated just to obtain a nicer status; an uncertain provider or external operation is not permission to replay it. Follow returned owning references rather than constructing opaque IDs or queue paths. Completion belongs to the scoped requested work, not merely to reaching the last named stage.

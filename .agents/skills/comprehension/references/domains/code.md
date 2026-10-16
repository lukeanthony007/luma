# Comprehending code

## Start with the question

Turn the question into a bounded behavior or change to explain. Identify the repository revision, relevant path(s), observed or expected scenario, intended use, and what evidence access is authorized. Name a specific result contract: which behavior, callers, boundary cases and uncertainty matter. A focused question usually needs a small trace, not a graph of the whole repository. Use a broader structural map only when the behavior crosses modules or no relevant boundary is known.

## Navigate from structure to behavior

First inventory the relevant files and sample the surrounding code. Follow entry points, imports, configuration and data flow in context; a directory tree or symbol name is a map, not evidence that the implementation was read. Use LSP definition, references, implementations and type information to find candidate edges, then inspect each returned location in the current source. Use AST-aware structure to distinguish declarations, calls, branches and nesting. Text search is candidate discovery, not resolved symbol identity: overloads, shadowing, generated code and dynamic dispatch may change the path. Trace callers and callees only as far as needed to explain the requested behavior; widen when a missing or competing path could change that explanation.

For each material source observation, retain a compact evidence record: repository revision and exact file/symbol/range; what code explicitly does; inference and its premises; scenario/scope; and unexamined paths or configuration. Compare relevant callsites and cross-source uses before generalizing a local implementation. Keep a static possible path distinct from a path observed at runtime.

## Check behavior where it matters

Walk the relevant control/data path, including guards, defaults, error branches, imports, configuration and external boundaries. For consequential claims about actual behavior, inspect an applicable runtime trace or run a focused scenario when authorized; record command/setup or trace context, inputs and observed result. If execution is unavailable or out of bounds, keep the claim static or unresolved rather than implying runtime confirmation. A trace confirms only that run and exercised path.

When changes span modules or repeated identity relationships matter, an architecture map or graph cache may help navigate. Keep it optional, scoped to the question, and keyed to the inspected repository revision; a cached edge is a candidate to confirm in source, not current truth by itself. Recheck affected imports, callers and cross-source uses after edits, and refresh conclusions if snapshots changed. Never report a whole-repository map as semantic verification.

For a requested generated repository map, follow [Build and use a codebase map](../code-graph.md). It combines inventory, parsing/import resolution, targeted LSP, semantic interpretation, validation and retained use under `comprehension`; the backend's specialized formats and execution do not create a second reasoning practice.

LSP/AST resolution is language and tooling scoped. It does not generalize to arbitrary identity resolution among people, records or entities; same names do not prove same referent. Separate explicit code behavior, static inference, observed trace and unknown behavior. Note material uncertainty from reflection, generated code, plugin dispatch, services, environment or unexamined paths. Follow engine-specific operational references for adapter and snapshot mechanics, not as a substitute for this evidence reasoning.
---
name: luma-config
description: Maintain workspace instructions, Skills, tools, apps, packages, configuration, and Git with verified changes, clear ownership, and explicit activation boundaries.
---

# Maintain workspace resources

Use this for changes to instructions, skills, tools, or applications. Read relevant workspace instructions, inspect the resource and its callers, and establish purpose, owner, current behavior, dependencies, and authorized scope before editing. Preserve user changes and project conventions. A recorded proposal is not permission to execute it.

## Change and verify

Make the smallest complete change that meets the request. Update affected instructions and callers; remove obsolete paths only when the change owns them. Tools must have working behavior and clear input, output, and failure limits, not stubs or placeholder fallbacks. Keep navigation checks distinct from truth, security, and authority checks. For content workflows, preserve source context, distinguish evidence from inference and unknowns, and reconcile dependent conclusions when meaning changes.

Inspect ownership and relevant changes for unintended effects. Run only checks authorized by the task and environment; report checks actually run, not assumed results. Preserve unresolved failures and limitations rather than suppressing them.

## Improve a practice from experience

Inspect the task, method/version used, expected outcome, observed result and conditions before diagnosing a recurring problem. Separate missing evidence, delivery loss, reasoning/application errors, tooling defects and changed circumstances. A single failure need not justify a general rule; a correct answer does not prove the method caused it.

Use [luma-dream](../luma-dream/SKILL.md) when broader reflection is needed to develop a supported proposal. A Dream finding supplies a basis to inspect, not automatic authority to implement it. Apply existing scoped authorization when present; keep the proposal, actual revision and later evaluation distinguishable.

For an authorized revision, state the affected Skill or tool, the specific change, evidence, applicability and exceptions, and the expected observable improvement. Keep the original method/version recoverable. Update one canonical resource and its routing or callers rather than scattering corrective instructions across unrelated files. Use [learning from use](../comprehension/references/learning.md) to judge later use: record benefit, regressions, non-application or inconclusive evidence without treating acceptance of an edit as successful learning.

## Configuration and activation

Identify whether a setting belongs to this workspace, this invocation, the user's harness profile or a shared service. Edit only the authorized scope; preserve secrets outside published instructions and Wiki pages. Recheck the actual discovery and effective configuration before claiming a Skill, tool or application is active. Instruction edits cannot create unavailable tool capabilities, grant access or establish permission enforcement. A process restart, schedule, service deployment or provider change is a separate effect when it is not already authorized.

## MCP connections

Use `./.agents/mcp.json`, relative to the owning workspace root, as the canonical project file for MCP server definitions. Create it when a concrete integration is useful and within the user's authorized scope; keep it absent in a fresh workspace that needs no connector. Maintain it through this practice as integrations are added, changed or retired. Inspect existing definitions first, preserve unrelated servers and options, and make scoped changes rather than replacing the whole file or duplicating it at the root.

Inspect the active harness's supported schema, transports and configuration loading before writing definitions. Validate JSON and the relevant schema, then verify effective discovery when that check is authorized and available. A valid file does not establish that every harness automatically reads `.agents/mcp.json`. If a harness needs another location, use its supported reference or adapter to this canonical file where possible; otherwise document and reconcile the required mapping without silently keeping competing copies.

Keep tokens, passwords and private headers in the harness credential store or supported environment references, not in the JSON or public instructions. The public Luma foundation excludes populated `.agents/mcp.json` files; publish a separately reviewed credential-free example only for an actual need. Preserve existing authentication and permissions. Distinguish saving definitions, discovering tools, authenticating, starting a local server and exercising remote actions; perform each only within its applicable authorization and do not request permission again for work already authorized.

## Packages and applications

Add software only for an established use. Inspect repository and package-manager conventions before changing manifests or layout. Do not impose a second project structure, generate sample packages, or disrupt existing work. Dependencies and installation are separate decisions; do not install or fetch without authorization.

The [directory initializer](../../tools/luma.py) installs the portable resources into a selected directory without creating a Git repository or activating a harness. Inspect its source and use `init --dry-run` when reviewing an installation. Preserve existing README content and ignore rules; differing managed resources require deliberate reconciliation rather than an overwrite flag. Initialization and later Skill maintenance are separate: use current source and human edits when deciding how an installed workspace should evolve.

## Git and activation boundaries

Inspect file ownership and repository status before changes; leave unrelated user changes alone. Distinguish edited working-tree content, Git index/staging, commit, installation, and runtime activation. Do not stage, commit, install, activate, publish, or cause external effects unless explicitly authorized. A successful file edit does not prove a resource is installed or active.

When commits are authorized, use the repository's branch, review and hook conventions. Select only task-owned files or hunks; preserve another person's staged work, and inspect the resulting commit and remaining changes. Do not silently stash, reset, clean, bypass hooks or rewrite published history to achieve a clean tree. Keep local commit, remote publication and configuration activation separate; uncertainty about a previous external operation is not permission to replay it.

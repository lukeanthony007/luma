# Worked comprehension examples

These examples illustrate judgment, not facts to memorize or mandatory domains.

## Conditional mechanism

A document says gravity supplies pressure, a powered controller opens a valve when moisture is low, and the valve closes on power loss. The inference that gravity eliminates all need for electricity is unsupported: pressure does not establish an open flow path. Retain the distinction and the explicit failure condition. Do not infer an unmentioned bypass. A physical installation's actual behavior would require applicable operational evidence, not merely the text.

## Identity ambiguity

Two entries mention “Alex,” one about a college visit and one about a dinner host. Name equality does not establish same person. Inspect dates, context, cross-references and authorized identity evidence. If none distinguishes them, retain two mentions and an unresolved association. LSP/AST symbol resolution for code is not a method for resolving arbitrary person identity. Repeatedly finding the same name in one source is not independent corroboration.

## Delivery differs from retention

An exception exists in a supported assertion but is absent from the exercise's delivered view. That attempt shows an access/delivery limit, not that the account lacks the exception. If delivered but misapplied, diagnose application instead. A later retrieval, repair and retest are new events; they do not retroactively improve the first attempt.

## Examples do not establish a universal rule

A code path is statically able to call a function, but no trace or execution confirms the path ran. Report static call possibility, not observed runtime behavior. Conversely, a trace shows one invocation and its inputs, not all possible behavior. Keep repository revision, exact code location and runtime context attached to each claim.
## Focused code investigation

Question: “Does a request to `/items/:id` return archived items?” Pin the current repository revision and define the route behavior and relevant configuration as scope. Start at the route registration, inspect the handler and its imports, then use LSP definition/references and AST structure to trace the repository query and any archive filter. Treat search hits as candidates; inspect actual resolved definitions and callers. Compare the route's filter with the query helper's other callers before claiming a shared rule. A code branch that permits archived items establishes static behavior only. If the question concerns what a deployed request actually returned, use an authorized trace or focused run and record environment, request, data fixture and response. Report a precise code snapshot for static assertions and a separate trace context for observed behavior. If configuration can change the filter and its deployed value is unavailable, state the conditional or unresolved result rather than guessing.

## Reading a paper and its measurements

Question: “Did treatment reduce the measured outcome, and for whom?” Pin the paper/version and any authorized supplementary data. Orient to methods, results, tables, captions and limitations; inspect the exact table and adjacent text. Record the population, intervention/comparator, outcome definition, time point, units, sample/denominator, exclusions and uncertainty interval. Distinguish the paper's reported estimate from a causal interpretation and from underlying physical observations. If a dataset is available, identify its revision, measurement provenance, filters, missingness and transformation; recompute a consequential summary when possible. Check whether the comparison supports the claim for the sampled population and conditions, not a broader population or mechanism. If only a table or abstract is accessible, name the unavailable evidence and narrow the conclusion. A heading, chart metadata or significant-looking estimate alone does not settle interpretation.

# Public repository instructions

Read `PRO_RESPONSIBILITY_PROMPT.md`, `DEMO_COMMISSION.md`, `ROUTE.md`, and
`prototypes/equities-research-cognition/AGENTS.md` before proposing or changing
the product.

`PRO_RESPONSIBILITY_PROMPT.md` is the governing public handoff for the
long-context product owner. The Agentic SDLC applicability brief is optional
and downstream: do not read it before recovering product intent and repository
truth as required by that prompt.

The active local-first product rethink lives under `docs/workspace/`. Read
`docs/workspace/README.md` and its nested `AGENTS.md` before revising that work.
The directory remains in plan space. Do not turn it into implementation tasks or
code until its status changes explicitly.

This repository exposes a current implementation substrate and a desired
product direction. Do not collapse them. Existing Django models, NTM panes,
role protocols, Langfuse traces, tests, or routes are not evidence that the
analyst product is complete or well designed.

When asked to design a demo, work backwards from the analyst's consequential
job and the exact artifact they must trust. Treat agent decomposition as a
debuggable execution structure, not as visible panes or invented analyst
terminology. The interface may be rich, but every visible object and action
must correspond to ordinary analyst work or a necessary decision.

No analyst-facing design may use eyebrows, overlines, kickers, supratitles, or
small categorical labels above headings. Do not expose backend ontology as the
user's workflow. Do not assume that rejecting jargon implies a thin product.

Keep these boundaries explicit:

- models propose research, calculations, and candidate artifacts;
- deterministic software owns identity, exact bytes, versions, permissions,
  known predicates, legal transitions, and fail-closed checks;
- analysts own contested meaning, materiality, corrections, and permission to
  rely on a result;
- a candidate never becomes authority merely because an agent completed it;
- mechanical tests do not prove cognition, research quality, or adoption.

Do not commit credentials, `.env` files, runtime state, protected research,
private transcripts, operator paths, or service-issued identifiers. Use the
commands in the package instructions for verification.

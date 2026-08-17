# Executable package instructions

Read the repository root `AGENTS.md`, `DEMO_COMMISSION.md`, and `ROUTE.md`
before changing this package. `PRODUCT_DISCOVERY.md` and `PHILOSOPHY.md`
preserve hypotheses; they are not proof or implementation authority.

## Package role

This is the sole runnable package. Django/PostgreSQL owns authenticated job
state, exact artifacts, chronology, human actions, and restart truth. NTM
instantiates persistent Codex sessions. Codex performs bounded work from exact
work orders. Langfuse may supply non-authoritative operational observations.

The mature completion object is:

```text
authenticated ongoing modelling or research job
-> professional objective and exact native artifacts
-> bounded agent work and progressively useful candidates or refusal
-> exact source, transformation, dependency, artifact, and decision lineage
-> consequential uncertainty in ordinary professional language
-> scoped human use of one exact result
-> later protected, reversible workflow experiments
```

The current implementation proves only a narrower mechanical slice. Candidate
output is never authority. Deterministic code may validate shape, identity,
references, arithmetic, cutoff legality, admissibility rules, and exact sets;
move exact bytes; and enforce legal transitions. It may not choose a research
hypothesis, infer truth, manufacture authorship, or convert a trace or score
into analyst evidence.

## Material research floor

Any cognition or research-quality claim requires a real equities commission,
decision use and public cutoff; live lawful information foraging without a
preassembled answer; the production model, protocols, tools, permissions and
resource bounds; evolving research state that can change the next route or
claim; exact trajectory custody; and an output or refusal a qualified analyst
could judge.

Fixtures and hostile checks are `MECHANICAL_REGRESSION_ONLY`. They may test
schemas, parsing, arithmetic, digests, permissions, transitions, transport and
rendering. They cannot establish cognition, topology quality, analyst value, or
product fit.

## Engineering

Run from this directory with `uv`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
```

Only `harness/ntm/adapter.py` may spawn host processes. Preserve the ordinary
server-rendered path, exact ownership, append-only history, restart truth, and
fail-closed behavior. Do not install dependencies or integrate external tools
silently.

When designing the requested demo, do not mistake the inherited page structure
for validated UX. Work backwards from the analyst job in `DEMO_COMMISSION.md`.
Visible language must be analyst-attested or unambiguous ordinary language;
backend roles and state-machine terms are not automatically interface objects.

Do not commit credentials, runtime trees, `.env`, `.venv`, caches, protected
cases, raw traces, private transcripts, or service-issued identifiers.

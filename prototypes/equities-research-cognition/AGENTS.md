# Executable package instructions

Read the repository root `AGENTS.md`, `DEMO_COMMISSION.md`, `ROUTE.md`, and
`docs/workspace/README.md` before changing this package. `PRODUCT_DISCOVERY.md`
and `PHILOSOPHY.md` preserve earlier hypotheses; they are not proof or
implementation authority.

## Package role

The package now contains two separately reviewable execution paths.

The inherited Django/PostgreSQL path owns authenticated campaign state, exact
artifacts, chronology, human actions, and restart truth. NTM may instantiate
persistent Codex sessions for that path.

The local workspace kernel under `research_workspace/` owns a single-user local
object graph, content-addressed bytes, source assertions, purpose-specific
evidence decisions, sealed contexts, direct child processes, provisional claims
and artifacts, scoped decisions, corrections, memory, and replay.

Neither path owns analyst truth by inference. Langfuse may supply
non-authoritative operational observations.

The active V0 completion object is:

```text
local workspace and mandate
-> prior perspective and exact professional request
-> confirmed commission
-> exact source versions and separate assertions
-> human-confirmed professional objects
-> purpose-specific evidence decisions
-> sealed assertion-level context
-> known child process and host-validated output
-> cited artifact and scoped human decision
-> correction, active memory, second episode, and replay
```

The current implementation proves only a mechanical path through those
relations. It does not prove useful model research, source entitlement, native
Excel support, analyst value, operating-system isolation, or commercial
readiness.

## Material research floor

Any cognition or research-quality claim requires a real equities commission,
decision use and public cutoff; live lawful information foraging without a
preassembled answer; the production model, methods, tools, permissions and
resource bounds; exact context custody; work capable of changing the answer;
trajectory and artifact custody; and an output or refusal a qualified analyst
can judge.

Fixtures and hostile checks are `MECHANICAL_REGRESSION_ONLY`. They may test
schemas, parsing, arithmetic, digests, source relations, context exclusion,
permissions, transitions, transport, artifact ancestry, memory scope, replay,
and rendering. They cannot establish cognition, topology quality, analyst value,
or product fit.

## Engineering

Run from this directory with `uv` where the required Python and PostgreSQL
environment are available:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
```

The local workspace vertical also has a standard-library test path:

```text
python -W error -m unittest scenarios.adversarial.test_local_workspace_vertical
python -W error -m compileall -q research_workspace scenarios/adversarial/test_local_workspace_vertical.py
```

Only `harness/ntm/adapter.py` may spawn processes for the inherited campaign
path. Only `research_workspace/runtime.py` may spawn processes for the local
workspace path. Both must use argument arrays, `shell=False`, exact working
directories, bounded environments, process receipts, and fail-closed output
custody.

The local runtime does not claim operating-system sandbox isolation. Do not add
network access, broad inherited environment variables, mutable user
configuration, or another process authority silently.

The support context contains exact admitted assertion extracts and source
receipts. Do not copy a whole document into a support context merely because one
assertion from that document is admitted; another assertion in the same document
may be excluded for the use.

Do not mistake the inherited page structure or the new CLI object names for
validated analyst language. Work backwards from professional work and exact
native artifacts.

Do not commit credentials, runtime trees, `.env`, `.venv`, caches, retained
licensed material, protected cases, raw traces, private transcripts, or
service-issued identifiers.

# V0 verification

Status: mechanical verification for `agent/local-workspace-vertical-v0`.

The verification ran from a complete checkout of the implementation branch after the repository instructions, route maps, boundary checker, line classifier, and ignore rules had been reconciled with the local kernel.

## Commands

From `prototypes/equities-research-cognition`:

```text
python -W error -m unittest scenarios.adversarial.test_local_workspace_vertical
python -W error -m compileall -q research_workspace scenarios/adversarial/test_local_workspace_vertical.py
python tools/check_boundary.py
python tools/classify_loc.py
```

All four commands passed.

The hostile vertical tests cover:

- separate assertion identity when two source documents contain the same value;
- rejection of the earnings-release assertion for the annual historical revenue use;
- lawful use of the same source document for a different management-language purpose;
- assertion-level support contexts that do not copy an entire source document;
- exact context manifests and tamper rejection;
- a known direct child process with stdout, stderr, exit state, and sealed output;
- rejection of claims citing assertions outside the sealed context;
- rejection of claims using an unpermitted assertion-to-object relation;
- content-addressed source and artifact integrity;
- append-only object history;
- host-validated claims and cited artifacts;
- scoped human use rather than completion-as-authority;
- correction and scoped active memory;
- a second episode receiving the correction within scope;
- evaluation-case creation;
- deterministic replay;
- proof-pack export; and
- the terminal CLI path.

## Repository boundary

`tools/check_boundary.py` now scans `research_workspace/` as a runtime-bearing surface.

The checker recognises only two process authorities:

- `harness/ntm/adapter.py` for the inherited campaign path; and
- `research_workspace/runtime.py` for the local workspace path.

Every approved subprocess call must use an argument array and `shell=False`. A process call elsewhere remains forbidden.

`tools/classify_loc.py` counts `research_workspace/` as operational code rather than leaving the new kernel outside architecture review.

## Checks not repeated here

The inherited Django/PostgreSQL application was not changed by the local vertical. Its full checks require the repository's declared Python, PostgreSQL, runtime, Langfuse, and external-skill environment:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
```

Those checks should run again before the stacked branches are merged into the inherited application path. The standard-library local vertical does not substitute for them.

## Claim ceiling

The verification establishes a coherent mechanical route through local identity, exact bytes, source assertions, evidence-use decisions, context construction, direct process execution, claim admission, artifacts, human decisions, correction, memory, second-episode retrieval, and replay.

The verification does not establish:

- useful frontier-model research;
- analyst approval or repeated use;
- lawful use of licensed broker, expert-network, Bloomberg, or other private sources;
- operating-system filesystem or network isolation;
- commercial use of an analyst's terminal-agent subscription;
- native Excel support or faithful production workbook recalculation;
- reduction in analyst review time;
- sound automatic materiality; or
- production deployment.

The deterministic reference worker proves the contract. A real Codex or Claude Code run must satisfy the same context and result admission path before a cognition claim can be made.

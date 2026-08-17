# Executable equities-research package

This package is the current runnable substrate for an authenticated ongoing
modelling or research job. It combines Django/PostgreSQL custody, bounded Codex
work through operator-installed NTM, optional Langfuse readback, versioned role
protocols, equities workbenches, and mechanical adversarial tests.

Read the public [demo commission](../../DEMO_COMMISSION.md) before treating the
existing interface or architecture as the intended product.

## Run locally

From this directory:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
```

`uv run python manage.py runserver` starts the server-rendered application when
PostgreSQL settings are available. NTM, Codex CLI, PostgreSQL, and Langfuse
credentials are operator-installed external systems and are not redistributed.

Create the local director account interactively:

```text
uv run python manage.py bootstrap_local_director
```

The command is available only with `DEBUG` enabled. It creates the username
`director` without staff, superuser, or analyst-enrolment authority. The
repository contains no shared default password.

## Package map

- `agents/`: bound-work, planning, research, adversarial-review, synthesis, and
  judgment protocols;
- `workbenches/`: four provisional equities-research contracts;
- `harness/ntm/`: the only process-launch boundary;
- `harness/langfuse/`: telemetry configuration and bounded readback;
- `product/`: Django configuration, job custody, review, templates, contracts,
  and migrations;
- `scenarios/adversarial/`: `MECHANICAL_REGRESSION_ONLY` checks; and
- `skills/`: identities and digests of external cognition dependencies.

## Evidence boundary

The code and tests support a narrow claim: an authenticated owned job can bind
exact inputs and an immutable run specification to an installed NTM/Codex
dispatch, require acknowledgement, preserve a provisional candidate or
refusal, reject exercised tampering attacks, and retrieve the exact outcome
after restart.

They do not establish workbook parsing or recalculation, semantic source
admissibility, artifact adoption, a material DeepResearch episode, research
quality, analyst usefulness, deployment readiness, or a valid interface. The
public export omits historical service receipts and private programme evidence;
see [evidence/README.md](evidence/README.md).

# Worker Packet 012 — Codex Output-Root Trust Control Repair

Status: **authorised bounded runtime repair; control only; no product replay**.

Programme state: `REPAIRING`.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Diagnosis evidence base: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Diagnosis branch: `agent/case-a-joined-runtime-diagnosis-v0`
- Diagnosis receipt: `docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`
- Repair branch: `agent/codex-output-root-trust-control-v0`
- Governing contract: `docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`
- Required result receipt: `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`

The exact dispatch head is recorded in the coordinating issue and current semantic checkpoint because a packet cannot contain the hash of the commit that contains itself.

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor b6735692418af7861b170e8e2eb0a1b438c71fcb HEAD
git diff --name-status b6735692418af7861b170e8e2eb0a1b438c71fcb...HEAD
```

The initial net diff may contain only this packet and `CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`. Stop with `MOVED_RUNTIME_REPAIR_BASE` if product code, runtime code, tests, prompts, settings, migrations, or fixtures already moved.

## Assignment

Repair only the process-local Codex project-trust mismatch proven by Packet 011. The neutral control must succeed non-interactively in a fresh standalone output root before any product replay is considered.

The repair must not redesign the runtime, product, prompt, packet, model, agent topology, source policy, workbook path, or user interface.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read:

1. `PRO_RESPONSIBILITY_PROMPT.md`
2. `docs/pro/PRO_CONSTITUTION.md`
3. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
4. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001
5. `docs/pro/evidence/MILESTONE_2_PACKET_010_ADJUDICATION_RECEIPT.md`
6. `docs/pro/JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md`
7. `docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`
8. `docs/pro/evidence/MILESTONE_2_PACKET_011_RUNTIME_TRUST_ADJUDICATION_RECEIPT.md`
9. `docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`
10. current decision ledger and semantic checkpoint
11. `product/campaign/services.py`, especially `_output_root`, `_prepare_output_root`, and `_control_files`
12. `harness/ntm/adapter.py`
13. focused runtime tests
14. this packet

The diagnosis receipt is evidence. The governing repair contract controls the implementation boundary.

## Reproduce before editing

Using the existing Packet 011 evidence, confirm the launcher shape at the diagnosis head:

```text
--cd <standalone output root>
-c projects."<repository root>".trust_level="trusted"
```

Confirm the actual working directory is not within the trusted repository project and that the neutral control stopped at `Do you trust the contents of this directory?` before creating output.

Do not run another failing live control merely to reproduce an already preserved interactive gate unless required to verify the environment remains the same. If reproduction materially differs, stop with `RUNTIME_DIAGNOSIS_DIVERGED`.

## Exact implementation

Change launcher construction for `model_change_v0` so the Codex process receives an invocation-scoped trust override for the exact canonical output root used by `--cd`.

The expected shape is:

```text
--sandbox workspace-write
--ask-for-approval never
--cd <exact output root>
-c projects."<exact repository root>".trust_level="trusted"
-c projects."<exact output root>".trust_level="trusted"
-m <pinned model>
```

An implementation may omit the repository-root override only if deterministic tests prove nested output roots still resolve without an interactive trust prompt and no project-local configuration or prior successful path is lost. Do not replace exact paths with a shared parent.

The output-root trust override must be derived from the same resolved `Path` that `_output_root(order)` returns. It must not accept an independently supplied path.

Do not write trust to disk. The runtime `-c` override is the authority mechanism.

## Exact owned files

You may modify only:

- `prototypes/equities-research-cognition/product/campaign/services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`

You must add exactly:

- `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`

No other path is owned.

## Prohibited changes

Do not modify:

- `harness/ntm/adapter.py`;
- models, migrations, source custody, candidate, calculation, correction, or disposition logic;
- product forms, projections, views, routes, templates, or UI copy;
- settings, environment defaults, timeout values, models, prompts, skills, protocols, packets, or workbenches;
- Codex user configuration, `CODEX_HOME`, home-directory files, project `.codex` files, or managed configuration;
- sandbox mode, approval policy, network/search policy, writable-directory scope, or credentials;
- Packet 009, direct Excel, cloud artifacts, source fixtures, workbook fixtures, or tests outside the owned runtime file;
- checkpoint, ledger, PR, issues, contracts, or worker packets; or
- Case A execution.

If another file is required, stop with `OWNERSHIP_BOUNDARY_REACHED` and name the exact missing interface.

## Deterministic test floor

Add focused assertions that prove:

1. the model-change launcher contains an exact trust override for the resolved output root;
2. the trust path equals the `--cd` path byte-for-byte after shell/TOML quoting is decoded;
3. the launcher does not trust the campaign root, temporary parent, home, repository parent, root, wildcard, or sibling;
4. two work orders with different output roots produce different launcher bytes/digests and exact trust paths;
5. spaces, quotes, and punctuation in an allowed path are safely encoded;
6. missing, symlinked, cross-campaign, or noncanonical roots fail before launcher creation under existing path checks;
7. `--sandbox workspace-write`, `--ask-for-approval never`, pinned binary/model, and no-search policy are unchanged;
8. the existing exact repository trust path is not broadened;
9. non-model-change launchers remain byte-for-byte equivalent except for unavoidable test fixture paths; and
10. launcher generation creates or modifies no persistent Codex config file.

Run at minimum:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python -W error manage.py test \
  scenarios.adversarial.test_model_change_v0_runtime \
  scenarios.adversarial.test_tue2_runtime_provider \
  scenarios.adversarial.test_owned_job_bound_execution -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_model_change_v0_models \
  scenarios.adversarial.test_model_change_v0_services \
  scenarios.adversarial.test_model_change_v0_runtime \
  scenarios.adversarial.test_model_change_v0_ui \
  scenarios.adversarial.test_model_change_v0_migrations \
  scenarios.adversarial.test_model_change_v0_repair_1 \
  scenarios.adversarial.test_model_change_v0_source_custody -v 1
uv run python tools/check_boundary.py
git diff --check
```

The suspended classifier may still fail when the complete suite is run. Record it; do not change or waive it.

## Live neutral control

Only after deterministic tests pass, run one neutral control with:

- a fresh standalone `0700` root outside the repository;
- one random-token input file at `0400`;
- the repaired launcher-generation path;
- the same installed NTM, Codex, model, operating identity, sandbox, approval, and no-search policy as Packet 011;
- a tiny instruction to read the token and write one `result.json` beneath the exact root; and
- no Case A packet, workbook, source, product prompt, browser, network search, or private data.

The result schema must be fixed before execution, for example:

```text
{"schema":"runtime-trust-control/v0","token":"<exact token>"}
```

Required success evidence:

- no interactive trust prompt;
- tracked instruction consumption;
- one exact regular output file and no extras;
- exact output bytes and digest;
- output remains beneath the trusted `--cd` root;
- no persistent Codex config/trust file changed;
- session stopped; and
- disposable root cleanup or explicit bounded retention.

If the trust prompt remains, return `TRUST_REPAIR_FAILED`. If Codex passes trust but fails later, return `CONTROL_REACHED_RUNTIME_BUT_FAILED`. Do not run Case A in either case.

## Return receipt

Create `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md` containing:

1. exact base, branch, implementation commit, and evidence head;
2. exact changed-file audit;
3. pre-edit diagnosis confirmation;
4. normalized before/after launcher shapes;
5. exact trust paths and proof of process-only scope;
6. deterministic test commands and counts;
7. live neutral-control environment, input, output, timing, and NTM observations;
8. persistent config before/after evidence;
9. cleanup decision;
10. failures and warnings; and
11. one verdict:
   - `CONTROL_PASS_FOR_INDEPENDENT_VERIFICATION`;
   - `TRUST_REPAIR_FAILED`;
   - `CONTROL_REACHED_RUNTIME_BUT_FAILED`;
   - `RUNTIME_DIAGNOSIS_DIVERGED`;
   - `OWNERSHIP_BOUNDARY_REACHED`; or
   - `FAIL`.

Do not merge, update governance, alter issues or PRs, or authorise the product replay.

## Stop conditions

Stop when:

- the branch base or initial diff moved;
- exact output-root trust cannot be expressed through a process-local override;
- the repair requires persistent trust, human interaction, broader sandbox/write access, NTM modification, prompt/model changes, or another owned file;
- deterministic tests show a parent or sibling path becomes trusted; or
- the neutral control requires product data or a Case A packet.

## Claim ceiling

A successful return may claim only that the tested launcher can start Codex non-interactively in one exact standalone host-created output directory using an invocation-scoped trust override while preserving the current sandbox and no-search policy.

It may not claim Case A success, end-to-end product completion, integration, verified V0, analyst validation, native Excel support, source entitlement, professional correctness, permission to rely, harness improvement, runtime reliability beyond the control, deployment, security readiness, production readiness, client readiness, or programme completion.
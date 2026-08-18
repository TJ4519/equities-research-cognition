# Worker Packet 008 — Case A Authority and Recovery Repair V1

Status: **authorised bounded repair; not authorised for merge or integration**.

Programme state: `REPAIRING` under Level 2 bounded orchestration.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Rejected implementation branch: `agent/case-a-outcome-complete-v0`
- Rejected implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`
- Rejected evidence head: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Repair branch: `agent/case-a-authority-recovery-repair-v1`
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Governing contract commit: `fa417e90aa124fed717fa72a1fc40bd44087968a`
- Coordinator projection: `dec-2026-08-18-037`
- Required migration: `campaign.0007_model_change_v0_repair_1`

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor 3d5c3157f91361bee120c10ecd4bddfda6e16296 HEAD
git diff --name-status 3d5c3157f91361bee120c10ecd4bddfda6e16296...HEAD
```

The initial branch delta may contain only this packet and `CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`. Stop with `MOVED_REPAIR_BASE` if product code, migrations, prompts, fixtures, tests, runtime, or templates moved before your work.

## Assignment

You are the sole architectural writer for one bounded repair of the rejected Case A implementation. Preserve the working joined path where evidence supports it; repair the exact authority and recovery defects; return a reviewable candidate and receipt. Do not redesign the product, add agents, broaden the workbook profile, activate direct Excel, or infer that the prior happy path was verified.

The completion object is one fresh joined synthetic episode in which:

```text
one real NTM/Codex worker returns a typed equal-value 8-K proposal
-> PostgreSQL recomputes and stores BLOCK_WRONG_DOCUMENT_CLASS
-> forged PASS and orphan candidate attacks fail under direct SQL
-> one current filed-report repair either completes candidate+receipt atomically
   or leaves the block current with a recoverable calculation-failure record
-> repeat/concurrent repair converges on one exact result
-> runtime failure and worker refusal survive restart with an ordinary next action
-> candidate review shows the exact 10-K assertion, both artifact identities,
   named synthetic use, unchanged original, equal-value explanation,
   two consequences, engine, warnings, and formula errors
-> disposition remains SIMULATE_NAMED_USE | REJECT | REWORK
-> restart and feature-flag rollback preserve canonical history
-> one correction seed is emitted without harness promotion
```

A repair that closes only the happy path, only the database trigger, only the UI, or only the classifier is a failure.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read in this order:

1. `PRO_RESPONSIBILITY_PROMPT.md`
2. `docs/pro/PRO_CONSTITUTION.md`
3. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
4. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md`
5. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER_AMENDMENT_001.md`
6. `docs/pro/PRODUCT_SYSTEM_ARCHITECTURE_V0.md`
7. `docs/pro/PROFESSIONAL_INTERACTION_AND_STATE_CONTRACT_V0.md`
8. `docs/pro/CONCEPTUAL_MODEL_CONTRACT_V0.md`
9. `docs/pro/EVALUATION_AND_HARNESS_EVOLUTION_CONTRACT_V0.md`
10. `docs/pro/UI_AND_REPOSITORY_SLOP_AUDIT.md`
11. `docs/pro/evidence/HOSTILE_VERTICAL_REVIEW_RECEIPT.md`
12. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
13. `docs/pro/evidence/MILESTONE_1_HOSTILE_REVIEW_RECONCILIATION_RECEIPT.md`
14. `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
15. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
16. latest `docs/pro/DECISION_LEDGER.jsonl` and `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`
17. current code, migrations, templates, hostile tests, and this packet

The rejected receipt is evidence, not authority. Current code and the independent counterexamples govern what failed.

## Reproduce before editing

Create or run bounded reproductions for all six findings and preserve commands/results in the return receipt.

### R1 — forged database PASS and candidate

Using PostgreSQL direct SQL, construct the annual 8-K proposal or an exact attacker-authored equivalent within the same episode. Prove the application gate returns `BLOCK_WRONG_DOCUMENT_CLASS`. Then insert a stored `PASS` using a noncanonical validator or false reason and insert a candidate without a calculation receipt. The rejected branch must permit the bypass before repair.

Do not weaken this into an ORM-only test.

### R2 — repeated repair

Call the filed-report repair twice against the same historical block. Prove the rejected branch can produce multiple amendments, replacement proposals, decisions, or candidate attempts.

### R3 — calculation failure dead end

Force `adapter.AdapterRejected` during candidate creation after the 10-K repair begins. Prove the rejected branch leaves a current `PASS`, no candidate, no calculation receipt, returns HTTP 500 or an unhandled error, and cannot lawfully retry through the ordinary action.

### R4 — refusal loss

Return a valid `model-change-refusal/v0` from the worker path. Prove the view discards it and restart exposes neither refusal nor next action.

### R5 — classifier evidence mismatch

Run `tools/classify_loc.py` at the rejected evidence head and record that the first failure is the unclassified package path `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`, before the binary workbook. Packet 008 must not modify this tool; Packet 009 owns the repair.

### R6 — candidate-review evidence gap

Render the authenticated candidate page and prove it lacks at least the exact 10-K assertion/locator, original and candidate digests, named synthetic use, explicit unchanged-original statement in the candidate section, and equal-value annual-report explanation.

If any reproduction materially differs, stop and return `COUNTEREXAMPLE_DIVERGED` with exact evidence. Do not silently repair a different problem.

## Product laws

1. The rejected branch is evidence, not an accepted implementation.
2. The database must recompute admissibility; stored model/application claims cannot authorise a candidate.
3. The worker may propose; it cannot issue source, object, artifact, actor, validator, or use authority.
4. The original workbook remains immutable.
5. A candidate is not complete without one matching calculation receipt.
6. Filed-report repair is one current professional action, not a reusable mutation primitive.
7. Technical failure and bounded refusal are product states when they alter the next action.
8. The user sees consequence and next action, not reason codes, raw packet JSON, NTM controls, or database mechanics.
9. LibreOfficeDev remains a pinned proxy for one profile, not Excel or the product.
10. A correction seed does not promote a harness change.

## Stable repair interfaces

Internal names may differ only when the semantic boundaries below remain explicit and tests lock them.

```text
CanonicalAdmission.expected(proposal_id)
  -> validator_version, outcome, reason_code, closure_digest

AdmissibilityDecisionService.record(proposal)
  -> database-verified AdmissibilityDecision

RepairService.create_candidate_using_filed_report(
    actor, blocked_decision, annual_assertion, adapter_profile, idempotency_key
) -> RepairResult(
    amendment, replacement_proposal, pass_decision, candidate,
    calculation_receipt, created_or_existing
)

CandidateService.create(pass_decision, exact_parent, adapter_profile)
  -> existing-or-new candidate + operation receipt + CalculationReceipt

OutcomeService.record_runtime_failure(...)
OutcomeService.record_worker_refusal(...)
OutcomeService.record_calculation_failure(...)
  -> append-only ModelChangeOutcome

RunService.run(actor, order)
  -> persisted proposal+decision | persisted refusal | persisted runtime outcome

ProjectionService.resume(owner, job_id, episode_id)
  -> current canonical state + current technical outcome + one legal next action
```

Views render projections and submit bounded commands. They do not calculate expected admission, infer current ancestry, spawn unallowlisted processes, or create candidates directly.

## Required database design

### Canonical function

Migration 0007 installs one PostgreSQL function that computes the expected target/source result from canonical rows. Python admission calls the same database function. Exact validator version: `model-change-admissibility/v1`.

### Decision guard

A `BEFORE INSERT` decision trigger rejects validator/outcome/reason/closure values that differ from the canonical function.

### Candidate guard

A candidate insert calls the canonical function again and requires a computed current `PASS`, exact same closure and custody, no invalidation, and one candidate maximum per pass.

### Receipt completeness

A deferred transaction constraint or equivalent proves at commit that every candidate has one exact matching calculation receipt. Direct-SQL candidate insertion without the receipt must fail at commit.

### Repair uniqueness

Add database uniqueness or guards making one successful `USE_FILED_ANNUAL_REPORT` amendment/replacement chain possible per current blocked decision. Concurrent duplicate requests converge.

### Outcome custody

Add the minimum append-only outcome table and direct-SQL update/delete guards. It must represent runtime failure, worker refusal, and calculation failure with closure and next action.

## Required orchestration semantics

### Successful filed-report repair

One orchestration service owns locking, currentness checks, amendment, replacement proposal, canonical decision, adapter work, candidate, receipt, invalidations, and idempotent result selection.

A successful call commits one exact chain. A repeated identical call returns it. A conflicting or stale call refuses.

### Calculation failure

If adapter inspection, apply, calculation, comparison, timeout, or formula checks fail:

- no new amendment, replacement, PASS, candidate, or receipt remains current;
- the wrong-source block remains current;
- a `CALCULATION_FAILURE` outcome is appended after rollback;
- the view returns a bounded response rather than HTTP 500;
- restart says no workbook changed and offers `Retry creating the candidate`.

### Runtime failure

A safe retryable launch/readiness/collection failure appends `RUNTIME_FAILURE`; restart offers `Retry this work`. A successor attempt preserves the prior work order and outcome.

### Worker refusal

A valid refusal appends `WORKER_REFUSAL` with exact work order, closure, protocol, reason, and next action. It creates no proposal, decision, or candidate.

## Exact owned files

You may modify only the following existing paths:

- `prototypes/equities-research-cognition/product/campaign/models.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/adapter.py` only for bounded typed error/result mapping; do not widen profile support
- `prototypes/equities-research-cognition/product/campaign/model_change/forms.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/projections.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/services.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/urls.py` only if a distinct retry command is necessary
- `prototypes/equities-research-cognition/product/campaign/model_change/views.py`
- `prototypes/equities-research-cognition/product/templates/model_change/episode.html`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_models.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_ui.py`

You must add exactly:

- `prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`
- `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`

You may add one focused test file only when it materially improves separation:

- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_repair_1.py`

The packet and contract files already on the branch are read-only worker instructions.

## Prohibited changes

Do not modify:

- migrations `0005_model_change_v0.py` or `0006_model_change_v0_guards.py`;
- `agents/model_change_v0.md` or any prompt, skill, workbench, model, or cognition version;
- `harness/ntm/adapter.py` or the established process allowlist;
- captured source fixtures or workbook fixtures;
- `tools/classify_loc.py` or classifier tests;
- direct-Excel packets, browser automation, cloud artifacts, or account state;
- legacy campaign/review templates or Casebook product surfaces;
- settings except through existing feature flag behaviour;
- decision ledger, checkpoint, governing contracts, PR text, or issues;
- Cases B or C as product journeys;
- harness attribution, evaluation runner, promotion, or release objects;
- dependencies or deployment configuration.

If a prohibited path appears necessary, stop with `OWNERSHIP_BOUNDARY_REACHED` and explain the exact interface gap.

## Required migration behaviour

Migration `0007_model_change_v0_repair_1.py` must be additive over rejected `0006` and preserve legacy and rejected-branch evidence.

Required evidence:

1. clean database from zero through `0007`;
2. upgrade from `campaign.0004` with legacy row preservation;
3. upgrade from `campaign.0006` with valid V0 rows preserved;
4. explicit failure or quarantine when forged/orphaned candidate authority exists before 0007;
5. direct-SQL append-only enforcement for the new outcome table and repair relationships;
6. empty reverse where safe; and
7. populated reverse refusal/dormancy preserving evidence.

Do not rewrite migration history to make tests easier.

## Mandatory hostile tests

### P0 database authority

Add tests that use raw SQL, not only ORM helpers:

- canonical annual 8-K decision insert with false `PASS`;
- false validator version;
- false reason code;
- stale or invalidated proposal;
- candidate for blocked decision;
- candidate without same-transaction receipt;
- receipt with wrong pass, manifest, candidate, episode, closure, input/output digest, or formula status;
- duplicate candidate for one pass;
- legal annual 10-K and preliminary 8-K controls.

### Repair uniqueness and idempotency

- sequential duplicate repair;
- concurrent duplicate repair;
- stale/invalidated block;
- conflicting annual assertion/profile/idempotency key;
- duplicate candidate call after success returns the exact existing candidate/receipt.

### Calculation failure and retry

- force `AdapterRejected` at apply, calculate, and compare boundaries;
- verify no stranded repair/PASS/candidate/receipt;
- verify exact `CALCULATION_FAILURE`, ordinary message, and retry action after restart;
- restore adapter and retry to one successful chain;
- formula error remains non-dispositionable.

### Runtime and refusal

- launch/readiness/collection failure persists and restarts;
- retry creates successor attempt without mutation;
- valid worker refusal persists exact reason and next action;
- stale output cannot displace a current outcome or acquire authority.

### UI contract

Authenticated response assertions must include:

- 10-K document identity, filing date, locator, value, and unit;
- original and candidate filenames and SHA-256 values;
- named synthetic use;
- original unchanged;
- equal numeric value but wrong annual document explanation;
- target change, exactly two consequences, adapter/engine, warnings, and formula errors;
- correct ordinary failure/refusal text and next action.

Assert absence of `USE_CANDIDATE`, approval/reliance language, raw reason codes, raw JSON, source-ID fields, NTM controls, trace IDs, and Casebook vocabulary.

### Restart and rollback

Exercise restart after runtime failure, refusal, block, calculation failure, successful repair, candidate disposition, and invalidation without relying on live runtime state. Feature flag off must preserve history and prevent new V0 entry.

## Required command floor

Run from `prototypes/equities-research-cognition`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py showmigrations --plan
uv run python -W error manage.py test \
  scenarios.adversarial.test_model_change_v0_models \
  scenarios.adversarial.test_model_change_v0_services \
  scenarios.adversarial.test_model_change_v0_runtime \
  scenarios.adversarial.test_model_change_v0_ui \
  scenarios.adversarial.test_model_change_v0_migrations \
  scenarios.adversarial.test_model_change_v0_repair_1 -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_owned_job_bound_execution \
  scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python tools/check_boundary.py
git diff --check
```

Run the complete adversarial suite and classifier as evidence, but do not repair or waive classifier failure in this branch. Record the exact first classifier failure for Packet 009 reconciliation.

## Fresh real joined episode

After deterministic tests pass, execute one entirely fresh synthetic Case A episode through real NTM/Codex under `closed_captured_sources`.

Use new job, campaign, episode, source, work order, output directory, proposal, decisions, candidate, receipt, outcomes, disposition, and correction record. Do not reuse prior evidence rows or worker outputs.

Exercise at least one recoverable failure path in a separate synthetic episode and prove restart/retry.

Record exact model/runtime identity, work order, source, proposal, decision, candidate, receipt and correction digests. Do not expose credentials, raw traces, private service identifiers, or unrelated runtime state.

## Return contract

Create `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md` last and return directly to PRO/coordinating Codex:

- exact base and result commits;
- verdict: `PASS_FOR_INDEPENDENT_VERIFICATION`, `PARTIAL`, or `FAIL`;
- exact changed files;
- reproduction evidence for R1–R6;
- database function and trigger definitions summarized with version;
- migration fresh/upgrade/reverse evidence;
- every hostile-test command and count;
- live NTM/Codex evidence and exact artifact digests;
- failure/retry/restart evidence;
- UI evidence fields and prohibited-language assertions;
- rollback evidence;
- classifier first failure, without claiming repair;
- unresolved facts; and
- claim ceiling.

Do not merge, fast-forward `agent/pro-grounding`, update ledger/checkpoint/issues/PR, deploy, advance direct Excel, or declare completion.

## Stop conditions

Stop immediately when:

- the initial base or owned-file set moved;
- an R1–R6 counterexample cannot be reproduced;
- database recomputation cannot be shared by decision and candidate guards;
- candidate/receipt completeness cannot be enforced at commit;
- successful repair cannot be single-use and idempotent;
- failure/refusal still depends on flash or process memory;
- adapter failure still leaves a current PASS or yields HTTP 500;
- migration 0007 must rewrite 0005/0006 or destroy history;
- a prohibited file is required;
- the worker path cannot remain one NTM/Codex worker with search closed; or
- the bounded profile must be widened.

A truthful `PARTIAL` or `FAIL` is acceptable. A persuasive receipt that omits a counterexample is not.

# Worker Packet 008 — Case A Authority and Recovery Repair V1

Status: **authorised for one bounded repair cycle after Packet 005 rejection**.

Programme state: `REPAIRING` under Level 2 bounded orchestration.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Rejected implementation branch: `agent/case-a-outcome-complete-v0`
- Rejected implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`
- Rejected evidence head and authoritative repair base: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Worker branch: `agent/case-a-authority-recovery-repair-v1`
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Governing repair-contract commit: `21384f3bdd6510fda78f8e1d8cacae91ca7efe46`
- Prior accepted architecture review: `99ad9412f059239c0604497b3de868b6c348370a`
- Independent disposition of Packet 005: `REJECT_PENDING_BOUNDED_REPAIR`

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor 3d5c3157f91361bee120c10ecd4bddfda6e16296 HEAD
git diff --name-status 3d5c3157f91361bee120c10ecd4bddfda6e16296...HEAD
```

The initial branch may differ from `3d5c3157...` only by this packet, the governing repair contract, the repair adjudication receipt, and exact dispatch metadata. Stop with `MOVED_REPAIR_BASE` on any product-code, migration, prompt, runtime, fixture, test, or template drift.

Do not merge, rebase onto `agent/pro-grounding`, deploy, or update governing state.

## Worker role

One architectural writer owns this repair. Do not split the overlapping database, service, projection, and interaction changes among frontend and backend workers. Separate classifier work remains outside this packet.

The writer must repair the exact rejected candidate rather than rebuild a different product, widen to Cases B/C, or optimise the happy path while leaving the hostile states unresolved.

## Required read order

After root and executable-package `AGENTS.md` and `ROUTE.md`, read in this order:

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
13. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
14. latest `docs/pro/DECISION_LEDGER.jsonl`
15. latest `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`
16. `docs/pro/COUNTEREXAMPLE_REGISTER.md`
17. the rejected implementation receipt at `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
18. current `models.py`, migrations `0005` and `0006`, model-change services/views/projections/template, tests, and classifier
19. this packet

Executable code and migrations govern what exists. The rejected receipt is evidence, not authority.

## Findings to reproduce before editing

Create or run a disposable PostgreSQL verification that reproduces all six findings before writing the repair:

1. A direct-SQL forged annual-8-K `PASS` population can reach candidate insertion because the candidate guard trusts stored decision fields.
2. Calling `repair_wrong_source()` twice on the same historical block creates duplicate repair descendants.
3. Forcing `AdapterRejected` after repair leaves a current `PASS`, zero candidate, and no legal retry; the view can return 500.
4. A bounded worker refusal is returned from `RunService` but disappears from canonical projection and restart.
5. `tools/classify_loc.py` at the evidence head fails first on the unclassified package path `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`; the reported binary-only failure is stale.
6. Candidate review lacks the 10-K assertion, artifact identities, named synthetic use, unchanged-original fact, and equal-value source explanation.

Record the exact reproduction commands and outcomes in the return receipt. If any finding cannot be reproduced, stop with `COUNTEREXAMPLE_NOT_REPRODUCED` and explain the divergence; do not silently repair a different system.

## Professional outcome after repair

The ordinary path remains the joined synthetic Micron episode, but every non-happy outcome must be recoverable:

```text
resume job and episode
-> confirm bounded meaning
-> authorise reported-value method/source policy
-> run one real closed-source NTM/Codex attempt
-> either persist runtime failure/refusal with an ordinary next action
   or receive the equal-value 8-K proposal
-> database-recomputed BLOCK_WRONG_DOCUMENT_CLASS
-> choose “Create a candidate using the filed annual report”
-> either persist calculation failure while the block remains current and retryable
   or atomically create one amendment, one 10-K proposal, canonical PASS,
   one child candidate, and one matching CalculationReceipt
-> review complete source/artifact/consequence evidence
-> record SIMULATE_NAMED_USE, REJECT, or REWORK
-> restart from canonical append-only state
-> retain one correction seed without harness promotion
```

The packet fails if it fixes only tests, only the trigger, only the view, or only the happy path.

## Mandatory repair 1 — database-recomputed authority

### Canonical SQL function

Implement one versioned PostgreSQL function, conceptually:

```text
campaign_model_change_expected_admission_v1(proposal_id uuid)
  -> expected_outcome, expected_reason_code, expected_closure_digest
```

It must derive the result from canonical proposal, episode, object, manifest, source assertion/document, operation, target, input revision, closure, owner/campaign relations, and invalidation rows.

Required cases:

- annual target + captured 8-K -> `BLOCK`, `BLOCK_WRONG_DOCUMENT_CLASS`;
- annual target + captured 10-K -> `PASS`, `PASS_EXACT_CLOSURE`;
- preliminary earnings-flash target + captured 8-K -> `PASS`, `PASS_EXACT_CLOSURE`;
- stale/invalid operation/cross-closure -> exact non-pass result.

Numerical equality must never substitute for document identity.

### Decision insert guard

Add a trigger that rejects an `AdmissibilityDecision` whose validator version, outcome, reason, or closure does not exactly equal the canonical function result. `AdmissibilityGate.evaluate()` must call the same database computation.

The canonical validator version for repaired rows must be new and explicit, for example `model-change-admissibility/v1`; do not reuse the vulnerable `v0` identity.

### Candidate and receipt guards

The candidate trigger must independently call the canonical function and require recomputed `PASS`, exact current joins, and no invalidated ancestor.

Add:

- one-candidate-per-pass uniqueness;
- exact candidate-parent/pass/episode/campaign/manifest closure;
- a deferrable transaction-end guard requiring exactly one matching `CalculationReceipt` before commit; and
- receipt guards for pass, candidate, episode, manifest, closure, input/output digests, formula-error absence, and adapter/profile identity.

A direct SQL transaction that inserts only a candidate must fail at commit.

## Mandatory repair 2 — single-use idempotent repair

Replace the view-level sequence of `repair_wrong_source()` followed by `CandidateService.create()` with one orchestration interface, semantically:

```text
RepairService.create_candidate_using_filed_report(
  actor, current_block, annual_assertion, adapter_profile, command_key
) -> RepairResult
```

The implementation must:

- lock the episode and blocked decision;
- require the block to be current, canonical, non-invalidated, and exactly wrong-document-class;
- derive a deterministic command key;
- enforce one successful filed-report amendment per block;
- enforce one replacement proposal/pass/candidate/receipt population;
- return the existing exact result for a repeated identical command;
- refuse divergent or stale duplicate commands; and
- converge under concurrent duplicate submissions.

`CandidateService.create()` must itself be idempotent for an exact current pass and return the existing candidate/receipt when the same call already succeeded.

## Mandatory repair 3 — atomic calculation and recoverable failures

The successful repair population must be atomic. The bounded V0 may hold one transaction through the pinned calculation subprocess because the timeout and profile are fixed.

On `AdapterRejected`, timeout, or other bounded calculation refusal:

- roll back amendment, replacement proposal, decision, candidate, and receipt from that attempt;
- keep the original block current;
- append a canonical calculation-failure outcome separately;
- render `No candidate was created. The original model is unchanged.`; and
- expose `Retry creating the candidate`.

No bounded adapter/runtime error may escape as HTTP 500.

## Mandatory repair 4 — canonical runtime/refusal/failure outcomes

Add exactly one minimal append-only model, `ModelChangeAttemptOutcome` or an equally bounded equivalent, in migration `0007`.

Required kinds:

- `RUNTIME_FAILURE`;
- `WORKER_REFUSAL`;
- `CALCULATION_FAILURE`.

Required data:

- episode;
- work order or blocked decision where applicable;
- attempt/idempotency key;
- current closure;
- bounded reason code;
- safe public message;
- retryable flag;
- next action `RETRY_WORK`, `RETRY_CANDIDATE`, or `NONE`;
- bounded details excluding raw stderr, secrets, tokens, cookies, and trace content;
- digest and time.

`RunService.run()` must persist runtime failures and `model-change-refusal/v0` results. A retry creates a new immutable attempt/work order where required; it does not mutate the old attempt.

`ProjectionService.resume()` must project the current outcome and next legal action after restart and retain earlier outcomes in history without letting them override a later successful result.

## Mandatory repair 5 — complete candidate-review evidence

The candidate view and projection must render from canonical rows:

- original filename and full SHA-256;
- candidate filename and full SHA-256;
- explicit original-unchanged statement;
- captured 10-K document identity and filing date;
- exact assertion locator, value, and unit;
- named synthetic use;
- explanation that the first 8-K was blocked despite the equal number because this annual target requires the filed annual report;
- target before/after;
- two declared consequences;
- calculation engine identity/version;
- warnings and formula-error state; and
- only `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK`.

Runtime/refusal/calculation-failure states must show an ordinary next action and whether any artifact changed.

Do not expose internal UUID entry, raw JSON, validator codes, work-order packet fields, NTM controls, trace IDs, Casebook vocabulary, generic approval, or professional-reliance language.

## Stable interfaces

Internal names may differ only when these semantic interfaces remain explicit:

```text
CanonicalAdmission.expected(proposal) -> outcome + reason + closure
AdmissibilityDecisionService.record(proposal) -> canonical decision

RunService.run(actor, order) ->
  proposal+decision | persisted refusal | persisted runtime failure
RunService.retry(actor, prior_outcome) -> new immutable attempt

RepairService.create_candidate_using_filed_report(...) ->
  existing_or_new amendment + replacement + pass + candidate + receipt

CandidateService.create(pass_decision, parent, profile) ->
  existing_or_new candidate + receipt

AttemptOutcomeService.record_runtime_failure(...)
AttemptOutcomeService.record_refusal(...)
AttemptOutcomeService.record_calculation_failure(...)

ProjectionService.resume(...) ->
  current professional state + current outcome + next action + immutable history
```

Views submit bounded commands and render projections. They do not decide admissibility, compile canonical authority, spawn processes, or infer current ancestry.

## Exact migration and rollback mechanics

Add exactly:

`prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`

Do not edit, squash, rename, or delete migrations `0005` or `0006`.

Migration `0007` owns:

- the attempt-outcome table/equivalent;
- canonical admission function;
- decision insert guard;
- strengthened candidate and receipt guards;
- uniqueness/idempotency constraints;
- deferrable candidate-receipt completeness;
- append-only direct-SQL protection for new state; and
- fail-closed handling of inconsistent existing V0 rows.

Required evidence:

- fresh migration to `0007`;
- `0004 -> 0007` with legacy rows preserved;
- `0006 -> 0007` with a valid Case A history preserved;
- forged/orphan V0 population detected before authority;
- empty reverse where safe;
- populated destructive reverse refused; and
- flag-off code rollback preserving readable history and preventing new V0 work.

## Owned files

The repair writer may modify only:

- `prototypes/equities-research-cognition/product/campaign/models.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/adapter.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/forms.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/projections.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/services.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/urls.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/views.py`
- `prototypes/equities-research-cognition/product/templates/model_change/episode.html`
- `prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_models.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_ui.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py`
- new `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_repair.py`
- root-level `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`

The worker may copy this packet and the repair contract onto its branch as dispatch metadata. Those copies are not product code.

## Prohibited files and interpretations

Do not modify:

- migrations `0005` or `0006`;
- `harness/ntm/adapter.py`;
- `agents/model_change_v0.md` or any prompt/skill/workbench;
- legacy campaign/review templates or routes;
- source fixtures or workbook fixtures;
- `tools/classify_loc.py` or classifier tests;
- direct-Excel packet/evidence;
- governing ledger/checkpoint/architecture on the worker branch;
- dependencies or deployment configuration; or
- the rejected implementation receipt.

Do not:

- widen to Cases B or C;
- claim tenant isolation, Excel support, analyst usefulness, professional correctness, permission to rely, harness improvement, deployment, or verified V0;
- simulate the real NTM/Codex return with a management command;
- treat the fixture, proxy, trigger, or green suite as the product; or
- ask the user to relay evidence.

If an owned-file boundary is insufficient, stop and return the exact required path and causal reason. Do not expand scope unilaterally.

## Required hostile tests

At minimum add explicit tests for:

1. forged `attacker/v0 PASS` annual-8-K decision/candidate rejected by direct SQL;
2. canonical-name but wrong outcome/reason rejected;
3. orphan candidate rejected at transaction commit;
4. mismatched receipt rejected;
5. duplicate candidate/pass population rejected or idempotently returned;
6. legitimate preliminary-flash 8-K remains admissible;
7. sequential duplicate repair creates one result;
8. concurrent duplicate repair creates one result;
9. stale block repair refused;
10. forced adapter failure rolls back repair population and persists retryable calculation outcome;
11. retry after calculation failure succeeds once;
12. worker refusal persists and survives restart;
13. runtime failure persists and survives restart;
14. no bounded failure returns HTTP 500;
15. candidate page contains every required source/artifact/use/explanation field;
16. no forbidden product language or raw operational control appears;
17. restart after every repaired state reconstructs exact next action; and
18. rollback/feature-flag and migration scenarios remain evidence-preserving.

## Required commands and evidence

Run from the executable package:

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
  scenarios.adversarial.test_model_change_v0_repair -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_owned_job_bound_execution \
  scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python tools/check_boundary.py
git diff --check
```

The full adversarial suite and LOC classifier are not acceptance evidence until the separate final-surface classifier repair is integrated. Record their exact current outcomes without repeating the rejected receipt’s stale counts.

After deterministic tests pass, execute one fresh real joined Case A episode with one NTM/Codex worker. Also execute forced runtime, refusal, and calculation-failure/retry paths. Preserve exact commands, environment versions, IDs/digests, timings, and sanitised outputs in the receipt.

## Return receipt

Create:

`docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`

Return directly to PRO and coordinating Codex:

- exact base, branch, implementation commit, and evidence commit;
- changed-file audit;
- pre-repair counterexample reproduction;
- schema and SQL-function/trigger contract;
- migration fresh/upgrade/reverse evidence;
- every hostile regression result;
- fresh real NTM/Codex joined episode;
- runtime/refusal/calculation-failure recovery evidence;
- candidate-review rendering evidence;
- rollback evidence;
- all failures and warnings;
- exact claim ceiling; and
- verdict `PASS_FOR_INDEPENDENT_VERIFICATION`, `PARTIAL`, or `FAIL`.

Do not merge or mark verified. PRO will commission a fresh independent verifier after return.

## Stop conditions

Stop immediately on:

- moved repair base;
- inability to reproduce a named P0/P1 finding;
- need to weaken closed-source, append-only, owner, synthetic-use, or candidate-after-pass boundaries;
- need to edit a prohibited file;
- inability to make the database recompute or equivalently bind canonical admission;
- inability to transactionally join candidate and receipt;
- second failed repair with the same causal diagnosis;
- protected data, personal workbook, permanent credential, external release, or professional judgment dependency.

A bounded `FAIL` with exact evidence is preferable to another self-certifying success claim.

## Claim ceiling

A successful worker return establishes only a repaired synthetic candidate ready for independent hostile verification. It does not establish integration, verified V0, analyst validation, Excel compatibility, professional permission to rely, production readiness, deployment, client readiness, or harness improvement.
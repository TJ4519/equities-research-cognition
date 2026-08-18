# Case A Bounded Repair Contract V1

Packet 005 is rejected as a product candidate until the database authority boundary, retry semantics, recoverable outcomes, candidate-review evidence, and final classifier surface pass the exact hostile tests in this contract.

Status: governing bounded-repair contract.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## 1. Exact basis and adjudication

- Repository: `TJ4519/equities-research-cognition`
- Governing PRO branch before repair adjudication: `agent/pro-grounding` at `dee299679562db02f051997f244868e86d6e0a0e`
- Rejected implementation branch: `agent/case-a-outcome-complete-v0`
- Rejected implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`
- Rejected evidence head: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Worker receipt: `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
- Coordinator projection: `dec-2026-08-18-037`
- Adjudication: `REJECT_PENDING_BOUNDED_REPAIR`

The rejected branch remains historical implementation evidence. It is not merged, deployed, promoted, called verified V0, or used as the basis for an analyst, Excel, professional-reliance, harness-improvement, or production claim.

## 2. Evidence retained narrowly

The following observations survive rejection because they were separately reproduced or coherently evidenced:

- one real NTM/Codex worker ran with captured sources and search closed;
- the application gate blocked the equal-valued annual 8-K proposal;
- an attributed 10-K replacement proposal was produced;
- the bounded LibreOfficeDev proxy produced a recalculated child workbook and two declared consequences;
- the synthetic disposition, restart projection, and correction seed were exercised;
- the focused model-change replay passed 25 tests;
- the existing owned-job and workbook replay passed 19 tests; and
- Django check, migration-drift check, boundary check, and diff check passed in the reported environment.

These results justify one bounded repair cycle. They do not license integration because the database can be induced to admit a candidate that the canonical application gate blocks.

## 3. Findings adopted

### P0 — candidate authority is forgeable at the database boundary

`campaign_model_change_candidate_guard()` trusts the stored fields of an `AdmissibilityDecision`, principally `outcome = PASS` and a matching closure. It does not recompute the target-specific source/target result, require the canonical validator version and reason, or require a matching calculation receipt before the transaction commits.

A direct-SQL writer can therefore create a structurally joined but attacker-authored `PASS` for an annual 8-K proposal and insert a candidate even though the application gate correctly returns `BLOCK_WRONG_DOCUMENT_CLASS`.

### P1 — filed-report repair is repeatable

`repair_wrong_source()` checks the block reason and annual assertion class but does not prove that the block is current, uninvalidated, unused, and uniquely repairable. The same historical block can produce multiple amendments, replacement proposals, decisions, and candidate attempts.

### P1 — calculation failure can strand authority

The repair transaction commits an amendment, replacement proposal, invalidations, and a `PASS` before candidate creation. `CandidateService.create()` then invokes the adapter in a different transaction. An `AdapterRejected` can escape the view as HTTP 500 and leave a current `PASS`, no candidate, no receipt, no current block, and no legal retry action.

### P1 — bounded worker refusal is lost

`ProposalParser` and `RunService` can return `model-change-refusal/v0`, but the view discards that result. No exact refusal, public consequence, or next action survives restart.

### P1 — the final classifier surface differs from the worker receipt

At evidence head `3d5c3157...`, `tools/classify_loc.py` first encounters the new package path `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`, for which no category exists. It fails before reaching the workbook. The accurate fresh suite result is 143 discovered, 138 executed, and one architecture setup error. A binary-only workbook repair does not close this surface.

### P1 — candidate review omits contractually required evidence

The candidate view does not show the exact 10-K document/assertion and locator, original and candidate artifact identities, named synthetic use, explicit unchanged-original fact, or the reason the equal-valued 8-K was rejected for this annual target.

## 4. Repair completion object

The repair is complete only when one fresh synthetic Case A episode can traverse the joined path and every named failure remains recoverable:

```text
authenticate
-> resume the synthetic Micron job and immutable campaign-backed episode
-> confirm the bounded FY2025 revenue meaning
-> separately authorise the reported-value method and target-specific source rule
-> run one real NTM/Codex worker over exact captured sources with search closed
-> persist proposal, refusal, or runtime failure as canonical state
-> recompute canonical target/source admission inside PostgreSQL
-> block the equal-value annual 8-K before candidate creation
-> choose “Create a candidate using the filed annual report”
-> either append one successful repair and complete candidate/receipt atomically
   or retain the block and persist a recoverable calculation failure
-> review exact source, artifact, calculation, consequence, and named-use evidence
-> record SIMULATE_NAMED_USE, REJECT, or REWORK
-> restart from append-only canonical state with one ordinary next action
-> emit one exact CorrectionRecord seed without harness promotion
```

A green happy path is insufficient. The P0 direct-SQL attack, repeat repair, adapter failure, runtime failure, refusal, restart, UI-evidence, and classifier counterexamples must all pass.

## 5. Canonical admissibility must be recomputed by PostgreSQL

### 5.1 One canonical database function

Migration `0007_model_change_v0_repair_1.py` must install a deterministic PostgreSQL function equivalent to:

```text
campaign_model_change_expected_admission_v1(proposal_id)
  -> validator_version, outcome, reason_code, closure_digest
```

The function reads only canonical database facts and computes the target-specific result from:

- proposal, episode, input revision, and current closure;
- conceptual object and manifest;
- exact target reference, allowed operation, value, and unit;
- exact source assertion and source document class;
- current invalidation state; and
- the bounded annual versus preliminary target rules.

The expected validator version is exactly `model-change-admissibility/v1`.

The function must produce at least the existing legal results:

- annual target + captured 8-K -> `BLOCK / BLOCK_WRONG_DOCUMENT_CLASS`;
- annual target + captured 10-K -> `PASS / PASS_EXACT_CLOSURE`;
- preliminary earnings-flash target + captured 8-K -> `PASS / PASS_EXACT_CLOSURE`;
- malformed operation, stale closure, invalidated ancestor, or unsupported target/source pair -> the corresponding non-pass result.

Do not implement a universal filing hierarchy.

### 5.2 Decision insert guard

A database trigger on `campaign_admissibilitydecision` must call the canonical function and reject an inserted row when any of these differ from the recomputed result:

- proposal identity;
- validator version;
- outcome;
- reason code; or
- closure digest.

`AdmissibilityGate.evaluate()` must obtain the same canonical result from the database rather than maintain an independently drifting Python policy implementation.

### 5.3 Candidate insert guard

The candidate trigger must call the canonical function again at insert time and require:

- computed outcome `PASS`;
- stored decision exactly equal to the computed validator, outcome, reason, and closure;
- one current proposal and decision;
- same owner, job, episode, campaign, manifest, object, assertion, parent artifact, and input revision;
- no invalidated ancestor;
- one candidate maximum for the pass decision; and
- candidate digest and parentage consistent with the proposed operation.

A stored `PASS` is never sufficient by itself.

### 5.4 Candidate and calculation completeness

A candidate is not a reviewable artifact without its exact calculation receipt.

Install a deferred transaction constraint or an equally strong database mechanism requiring, at commit:

- every model-change candidate has exactly one `CalculationReceipt`;
- the receipt references that candidate and the same pass decision, episode, manifest, and closure;
- receipt input digest equals the exact parent digest;
- receipt output digest equals the candidate digest;
- the candidate and receipt are in the same episode/campaign;
- formula errors are empty for a disposition-eligible candidate; and
- no candidate or receipt is admitted from an invalidated ancestor.

A direct-SQL insert of a candidate without a matching receipt must fail at transaction completion.

## 6. Repair is current, single-use, concurrency-safe, and idempotent

Introduce one orchestration boundary equivalent to:

```text
RepairService.create_candidate_using_filed_report(
    actor,
    blocked_decision,
    annual_assertion,
    adapter_profile,
    idempotency_key,
) -> RepairResult
```

The service must:

1. lock the episode and blocked decision;
2. prove the decision is the current, uninvalidated `BLOCK_WRONG_DOCUMENT_CLASS` for the current closure;
3. prove the annual assertion is the exact captured 10-K assertion in the same episode;
4. derive one deterministic repair key from block, assertion, actor/action, closure, and adapter profile;
5. enforce at most one successful amendment/replacement chain for that block/action;
6. make concurrent identical calls converge on one result;
7. return the existing exact candidate/receipt on an identical successful retry rather than creating new history; and
8. refuse a conflicting retry whose assertion, profile, closure, or actor scope differs.

`CandidateService.create()` must be idempotent by exact pass decision and closure. An existing exact candidate/receipt is returned; an inconsistent partial or mismatched state is rejected.

## 7. Repair and calculation cannot leave a stranded PASS

The successful filed-report repair must commit the amendment, replacement proposal, canonical pass, candidate artifact, and calculation receipt as one logical transaction.

The smallest acceptable implementation may keep the bounded external calculation inside a locked database transaction. A cleaner staged implementation is allowed only when tests prove the same all-or-nothing authority result.

When the adapter rejects, times out, returns formula errors, or fails before candidate completion:

- the amendment, replacement proposal, pass decision, candidate, and receipt must not become current;
- the original wrong-source block remains current and available;
- an append-only `CALCULATION_FAILURE` outcome is recorded in a separate successful transaction;
- restart displays that no workbook changed; and
- the ordinary next action is `Retry creating the candidate`.

The bounded failure must not become HTTP 500.

## 8. Runtime, refusal, and calculation outcomes are canonical and recoverable

Add the minimum append-only model, named `ModelChangeOutcome` or an equally explicit equivalent, with fields sufficient to bind:

- episode;
- optional work order;
- optional blocked decision;
- stage: `RUNTIME_FAILURE`, `WORKER_REFUSAL`, or `CALCULATION_FAILURE`;
- exact reason code;
- ordinary-language public message;
- next action: `RETRY_WORK`, `RETRY_CANDIDATE`, or `NONE`;
- current closure digest;
- deterministic attempt/idempotency key;
- bounded technical details that contain no secrets or raw credentials;
- digest and creation time.

Every outcome is append-only under ORM and direct SQL.

### Runtime failure

A launch, readiness, timeout, custody, or collection failure must create an exact outcome when it is safe to retry. The page states that no model changed and offers `Retry this work`. Retrying creates a successor attempt/work order; it does not rewrite the failed attempt.

### Worker refusal

A valid `model-change-refusal/v0` must be stored with the exact work order, closure, protocol, and bounded reason. Restart displays the refusal and a lawful next action. The refusal cannot silently become a proposal, decision, or candidate.

### Calculation failure

A bounded adapter failure is tied to the current block, repair command, closure, and adapter profile. It leaves the block current and offers `Retry creating the candidate`.

### Projection law

`ProjectionService.resume()` must project the current proposal/decision/candidate together with the latest applicable technical outcome and one legal next action. A later success may make an earlier failure historical, but the failure remains inspectable. NTM panes, Langfuse state, process memory, and flash messages are not restart truth.

## 9. Candidate review must restore professional evidence

The candidate view must state, in ordinary language:

- the exact captured 10-K document identity, filing date, assertion locator, value, and unit;
- the original workbook filename and SHA-256 identity;
- the candidate workbook filename and SHA-256 identity;
- the named synthetic use awaiting disposition;
- that the original workbook remains unchanged;
- that the first equal-valued 8-K proposal was blocked because this annual target requires the filed annual report;
- target before and after;
- exactly two declared recalculated consequences;
- adapter profile, engine identity/version, warnings, and formula-error state; and
- only `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK` actions.

Internal UUIDs, raw packets, validator reason codes, NTM controls, and Casebook terminology remain support-only.

Failure and refusal views must explain what happened, whether any workbook changed, and what the next action will cause.

## 10. Migration and rollback boundary

Use exactly:

`prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`

Do not rewrite migrations `0005` or `0006`. The rejected branch is evidence and the repair must be independently reviewable as an additive delta.

Migration 0007 may:

- add the minimum outcome record and constraints;
- add uniqueness needed for one repair/candidate per canonical ancestor;
- install/replace canonical decision and candidate guards;
- install the deferred candidate/receipt completeness guard; and
- add direct-SQL append-only protection for every new record.

It may not rename, delete, reinterpret, or destructively backfill existing rows.

Required migration evidence:

- clean fresh install through `0007`;
- upgrade from `campaign.0004` through `0007` with a representative legacy row preserved;
- upgrade from the rejected `0006` state through `0007`;
- detection or refusal of any pre-existing forged/orphaned V0 row;
- empty reverse where safe; and
- populated reverse refusal or dormant forward-fix behaviour preserving history.

Code rollback disables `MODEL_CHANGE_V0` and leaves canonical history readable. Populated repair schema is not dropped.

## 11. Classifier reconciliation is a separate dependency

Packet 009, not Packet 008, owns the final classifier repair.

It must cover both:

- strict UTF-8 classification of package-level `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`; and
- narrow validated binary measurement of the exact tracked workbook fixture.

Final integration acceptance requires the complete repaired tree to pass the classifier and full adversarial suite. Packet 008 must not modify classifier files or hide classifier failure.

Direct Excel remains suspended until the repaired product candidate survives fresh hostile verification.

## 12. Mandatory hostile regressions

### Database authority

- insert a wrong-source proposal and canonical host block;
- attempt direct-SQL `attacker/v0 PASS`; decision insert must fail;
- attempt canonical-looking `PASS` with wrong reason; it must fail;
- attempt candidate insertion for a blocked or invalidated proposal; it must fail;
- attempt candidate insertion without a calculation receipt in the same transaction; commit must fail;
- attempt a mismatched receipt, parent, manifest, closure, digest, episode, or pass; it must fail;
- prove annual 10-K and preliminary 8-K legal pairs still pass.

### Repair idempotency and concurrency

- submit the same filed-report repair twice; one amendment, replacement, decision, candidate, and receipt exist;
- submit two concurrent identical repairs; both callers converge on the same result;
- retry with a different assertion/profile/closure after success; it is rejected;
- call repair on an invalidated or historical block; it is rejected.

### Calculation failure and retry

- force `AdapterRejected` before candidate completion;
- HTTP response is bounded, not 500;
- restart shows the original block, no candidate/receipt, exact failure, and `Retry creating the candidate`;
- retry after restoring the adapter yields one successful chain;
- formula errors remain non-dispositionable.

### Runtime and refusal

- force runtime launch/readiness/collection failure; persist and restart with `Retry this work`;
- return a valid worker refusal; persist exact refusal and next action;
- retry creates a successor attempt without rewriting history;
- stale worker output remains diagnostic and cannot acquire authority.

### Candidate review

Authenticated HTML assertions must prove every item in Section 9 appears and prohibited professional-use or internal-harness language does not.

### Restart and rollback

Restart must reconstruct each state without a live NTM session, Langfuse, process memory, or flash state. Feature-flag rollback preserves every historical fact and disables future V0 entry.

## 13. Fresh joined evidence and independent verification

After the hostile regressions pass, run one fresh synthetic Case A episode through a real NTM/Codex worker. Do not reuse the previous successful database rows, output directory, proposal, candidate, receipt, or correction seed.

The worker return must include exact commits, changed files, migration evidence, commands, test counts, live work-order and artifact digests, failure/retry evidence, rollback evidence, and `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`.

The worker has no merge, integration, checkpoint, ledger, deployment, or completion-claim authority.

A fresh independent verifier must reproduce the P0 and P1 counterexamples and the joined episode before PRO may integrate the repair or restore a verified-V0 claim.

## 14. Stop conditions

Stop and return `FAIL` or `PARTIAL` when:

- canonical admission cannot be computed at the PostgreSQL boundary;
- candidate/receipt completeness cannot be enforced at transaction completion;
- repair cannot be made single-use and retryable without rewriting history;
- runtime/refusal/calculation failure still depends on in-memory state;
- a bounded failure still produces HTTP 500;
- migration 0007 requires destructive mutation or rewriting 0005/0006;
- the UI requires source IDs, raw packets, NTM controls, or professional-use language;
- a required file outside Packet 008 ownership must change;
- the real NTM/Codex path cannot run with search closed; or
- a hostile regression cannot be made deterministic.

Do not weaken a finding, silently widen scope, or hide a failure behind a prompt, fixture, mock, classifier exception, or manually inserted artifact.

## 15. Claim ceiling

This contract authorises one bounded repair attempt on the rejected synthetic Case A branch. It does not establish a repaired product, verified V0, analyst usefulness, professional correctness, permission to rely, Excel compatibility, arbitrary workbook support, tenant security, harness improvement, deployment, or client readiness.

# Case A Bounded Repair Contract V1

Packet 005 is rejected as an integration candidate because its database authority boundary can be bypassed and its recovery and review paths are incomplete, despite a real joined synthetic episode having executed successfully.

Status: governing repair contract for one bounded repair cycle under the user-authorised end-to-end delivery commission.

Programme state: `REPAIRING`.

## 1. Exact evidence basis

- PRO branch before this repair adjudication: `agent/pro-grounding` at `dee299679562db02f051997f244868e86d6e0a0e`.
- Rejected implementation branch: `agent/case-a-outcome-complete-v0`.
- Rejected implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`.
- Evidence head: `3d5c3157f91361bee120c10ecd4bddfda6e16296`.
- Worker receipt: `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md` at the evidence head.
- Independent coordinator verdict: `REJECT_PENDING_BOUNDED_REPAIR`.

The implementation branch is evidence. It is not merged, promoted, deployed, or described as a verified V0.

## 2. Findings adopted

### P0 — candidate authority is forgeable at the database boundary

`campaign_model_change_candidate_guard()` trusts an inserted `AdmissibilityDecision` row when its stored outcome says `PASS` and its foreign-key closure appears internally consistent. It does not independently recompute the target-specific admissibility result, require the canonical validator version and reason, or require a calculation receipt to exist at transaction completion.

A direct-SQL writer can therefore create a semantically false `PASS` population over an annual 8-K proposal and insert a candidate even though the application gate correctly returns `BLOCK_WRONG_DOCUMENT_CLASS` for the same source-target relation.

This defeats the claimed host-owned admission boundary. ORM cleanliness and append-only rows do not repair it.

### P1 — filed-report repair is repeatable

`repair_wrong_source()` validates the reason code and replacement assertion but does not require the blocked decision to remain current, does not enforce a unique successful repair command, and does not return an existing result idempotently. The same invalidated block can produce multiple amendments, replacement proposals, `PASS` decisions, and candidate attempts.

### P1 — calculation failure strands a passed proposal

The view commits the amendment, replacement proposal, invalidations, and `PASS` before `CandidateService.create()` completes. `AdapterRejected` is not translated into a bounded product outcome. A failed calculation can therefore leave the episode with a current `PASS`, no candidate, no receipt, no repair action, and no legal retry path. The HTTP request may return 500; repeating the repair sees no current block and returns 409.

### P1 — bounded refusal is lost

`ProposalParser` can return `model-change-refusal/v0`, and `RunService.run()` returns it, but the view discards the result. No canonical refusal record, visible explanation, or next action survives restart. A work order can remain in history with no proposal, decision, candidate, refusal, or recoverable product state.

### P1 — classifier evidence is stale at the evidence head

The implementation receipt reports the pre-receipt classifier failure. At evidence head `3d5c3157f91361bee120c10ecd4bddfda6e16296`, the executable package contains `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`, a path not classified by the current `category()` function. The classifier therefore fails on the newly added evidence surface before reaching the binary workbook. Fresh verification discovered 143 tests, executed 138, and stopped on one architecture setup error.

A binary-only repair compiled from the earlier tree does not close the final classifier surface.

### P1 — candidate review omits required evidence

The candidate page shows the target delta, engine, warnings, formula errors, and two consequences, but omits:

- the exact captured 10-K document identity and assertion locator;
- the original and candidate artifact identities;
- the named synthetic use awaiting disposition;
- the explicit fact that the original remains byte-for-byte unchanged; and
- the explanation that the first 8-K proposal was blocked despite numerical equality because this annual target requires the filed annual report.

The page therefore does not yet let a cold reviewer reconstruct why this candidate exists and what the final action means.

## 3. Evidence retained narrowly

The rejected branch still supplies useful mechanism and product-path evidence:

- one real NTM/Codex worker ran with captured sources and search closed;
- the typed equal-value 8-K proposal was blocked by the application gate;
- an attributed 10-K replacement was created;
- the bounded proxy adapter produced a recalculated child workbook with two declared consequences;
- a synthetic disposition, restart projection, and correction seed were exercised;
- the focused Case A suite passed 25 tests;
- the owned-job/workbook suite passed 19 tests; and
- Django, migration-drift, package-boundary, and diff checks passed in the reported environment.

These facts justify bounded repair rather than discarding the whole vertical. They do not license integration because the P0 boundary invalidates the strongest safety claim.

## 4. Repair completion object

The repair succeeds only when the same joined Case A episode completes with the following additional properties:

```text
canonical source/object proposal
-> one database-recomputed admissibility result
-> no forgeable PASS population
-> no candidate without a matching calculation receipt at commit
-> one current, single-use, idempotent filed-report repair
-> recoverable runtime, refusal, and calculation-failure outcomes
-> ordinary next action after every bounded failure
-> complete candidate-review evidence
-> restart and rollback from append-only state
-> fresh real NTM/Codex replay
-> fresh independent hostile verification
```

A locally green suite, a repeated happy-path seed, or a repaired template alone does not close this contract.

## 5. Canonical admissibility law

### 5.1 One database-owned computation

Add one PostgreSQL function with a versioned contract, conceptually:

```text
campaign_model_change_expected_admission_v1(proposal_id)
  -> expected_outcome, expected_reason_code, expected_closure_digest
```

The function must derive its result from canonical rows only:

- proposal and immutable digest-bound operation;
- episode, input revision, owner, campaign, and starting artifact;
- conceptual object and manifest;
- source assertion, source document identity, document class, value, unit, and dimensions;
- target reference and target-specific policy;
- operation equality to manifest and assertion;
- current closure and invalidation population; and
- the paired preliminary-earnings-flash counterexample.

The function must return `BLOCK_WRONG_DOCUMENT_CLASS` for the annual target plus captured 8-K and `PASS_EXACT_CLOSURE` for:

- the annual target plus captured 10-K; and
- the preliminary earnings-flash target plus captured 8-K.

It must not infer document identity from numerical equality.

### 5.2 Decision insertion guard

A database trigger on `campaign_admissibilitydecision` must call the canonical function and reject any inserted row whose:

- validator version is not the exact canonical version;
- outcome differs from the recomputed outcome;
- reason code differs from the recomputed reason;
- closure digest differs from the recomputed current closure; or
- proposal is stale, invalidated, cross-episode, or outside the bounded policy.

`AdmissibilityGate.evaluate()` must obtain the result from the same database computation rather than maintain a second independently mutable truth table in Python.

### 5.3 Candidate insertion and completeness guards

Candidate insertion must re-run the canonical function and require:

- recomputed `PASS`;
- the exact canonical decision row and validator version;
- exact current proposal, parent, manifest, assertion, episode, campaign, owner, and closure;
- no invalidated ancestor; and
- one candidate maximum for the pass decision.

A deferrable transaction-end guard must reject a committed candidate unless exactly one matching `CalculationReceipt` exists and binds:

- the same candidate and pass decision;
- the same episode, manifest, and closure;
- input digest equal to the exact parent digest;
- output digest equal to the candidate digest;
- no formula errors; and
- the bounded adapter/profile and engine identity.

A direct SQL transaction that inserts only a candidate must fail at commit. A candidate and mismatched receipt must fail. A forged decision with `validator=attacker/v0`, a wrong reason, or annual-8-K `PASS` must fail before candidate custody.

## 6. Single-use and idempotent repair law

Introduce one orchestration interface, semantically:

```text
RepairService.create_candidate_using_filed_report(
    actor,
    current_block,
    filed_annual_assertion,
    adapter_profile,
    command_key,
) -> existing_or_new_repair_result
```

It is the only product path from the wrong-source exception to a candidate.

The command must:

1. lock the episode and blocked decision;
2. require the block to be current, canonical, non-invalidated, and exactly `BLOCK_WRONG_DOCUMENT_CLASS`;
3. require the captured annual assertion to be current, same-episode, and a filed annual report;
4. derive a stable idempotency key from block, assertion, actor, action, closure, and adapter profile;
5. return the existing successful amendment/proposal/decision/candidate/receipt when the exact command already succeeded;
6. allow at most one successful filed-report amendment per blocked decision;
7. allow at most one replacement proposal per successful repair command;
8. allow at most one candidate and receipt per pass decision; and
9. refuse divergent duplicate commands rather than producing parallel descendants.

Concurrent duplicate submissions must converge on one canonical result or one explicit conflict; they must not create two amendments or candidates.

## 7. Recoverable attempt outcomes

Add one minimum append-only canonical record, named `ModelChangeAttemptOutcome` or an equally bounded equivalent, for outcomes that do not produce a proposal/candidate path.

Required kinds:

- `RUNTIME_FAILURE`;
- `WORKER_REFUSAL`; and
- `CALCULATION_FAILURE`.

Minimum fields:

- episode;
- work order when applicable;
- blocked decision when applicable;
- attempt/idempotency key;
- exact current closure;
- bounded reason code;
- safe ordinary-language message;
- next-action enum;
- retryable flag;
- bounded details without raw secrets, tokens, stderr, or trace content;
- digest and creation time.

Required next actions:

- `RETRY_WORK` for recoverable runtime failure or worker refusal;
- `RETRY_CANDIDATE` for recoverable calculation failure while the original block remains current; and
- `NONE` for final bounded refusal.

### 7.1 Runtime and refusal

`RunService.run()` must persist a canonical outcome when:

- runtime startup, dispatch, completion, or collection fails in a bounded recoverable way; or
- the worker returns `model-change-refusal/v0`.

The view must not discard these outcomes. Restart must display what happened, confirm that no model changed, and expose one ordinary next action. A retry creates a new immutable attempt/work order as required by current runtime semantics; it does not mutate the earlier attempt.

### 7.2 Calculation failure

The successful repair population must commit atomically with candidate and receipt. The bounded V0 implementation may hold the transaction through the allowlisted calculation call because the profile and timeout are fixed; a later architecture may split the operation only after preserving equivalent authority.

When the adapter rejects or times out:

- the amendment, replacement proposal, `PASS`, candidate, and receipt from that attempt must not commit;
- the original wrong-source block remains current;
- a `CALCULATION_FAILURE` outcome is appended in a separate bounded transaction;
- the page states that no candidate was created and the original is unchanged; and
- `Retry creating the candidate` is available.

No `AdapterRejected` or equivalent bounded failure may escape as HTTP 500.

## 8. Projection and interaction repair

`ProjectionService.resume()` and the visible route must represent:

- current object and authorities;
- current proposal/decision/candidate/receipt/disposition;
- current runtime, refusal, or calculation-failure outcome;
- the exact next legal professional action; and
- immutable history including superseded failures and repairs.

The candidate review must show, in ordinary language:

- exact original filename and SHA-256;
- exact candidate filename and SHA-256;
- explicit `Original model unchanged` fact;
- exact captured filed annual report identity, filing date, assertion locator, value, and unit;
- the named synthetic use awaiting disposition;
- the blocked 8-K explanation, including that the value was numerically equal but the annual target required the filed annual report;
- target before and after;
- both declared downstream consequences;
- calculation engine identity/version;
- warnings and formula-error status; and
- only `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK` actions.

Internal UUIDs, raw JSON, reason codes, NTM controls, trace IDs, workbench terms, generic approval, and professional-reliance language remain excluded from the primary surface.

## 9. Migration and rollback boundary

Repair the rejected branch additively with exactly:

`prototypes/equities-research-cognition/product/campaign/migrations/0007_model_change_v0_repair_1.py`

Do not rewrite `0005` or `0006`; they remain evidence of the rejected implementation and an explicit upgrade source.

Migration `0007` must:

- create the attempt-outcome table or equivalent minimal record;
- install the canonical admissibility function;
- replace or strengthen decision and candidate guards;
- install unique/idempotency constraints;
- install the deferred candidate/receipt completeness guard;
- protect the new canonical record from direct SQL update/delete; and
- validate or fail closed on pre-existing inconsistent V0 rows.

Required migration evidence:

- fresh database `0001 -> 0007`;
- upgrade `0004 -> 0007` with legacy campaigns preserved;
- upgrade `0006 -> 0007` with a valid synthetic Case A history preserved;
- attempted upgrade with a forged pass/orphan candidate refuses or quarantines explicitly before authority is granted;
- empty reverse where safe;
- populated reverse refuses destructive evidence loss; and
- feature-flag rollback leaves all V0 history readable and prevents new V0 work.

No destructive backfill, table drop, legacy reinterpretation, or evidence deletion is authorised.

## 10. Required hostile regressions

### P0 database attacks

1. Insert annual 8-K proposal plus `validator=attacker/v0`, `PASS`, and candidate: decision or candidate must fail.
2. Insert canonical validator name but forged `PASS`/reason for annual 8-K: must fail.
3. Insert candidate without receipt in one transaction: commit must fail.
4. Insert candidate with mismatched receipt, parent, pass, manifest, closure, input digest, or output digest: must fail.
5. Insert duplicate candidate for one pass: must fail or return the exact existing canonical candidate through the service.
6. Insert valid preliminary-flash 8-K decision and complete candidate/receipt population under its declared target: admission must remain possible where the profile permits it.

### Repair and failure recovery

7. Submit the same filed-report repair twice sequentially: one amendment, one replacement, one pass, one candidate, one receipt.
8. Submit the same repair concurrently: same result or explicit conflict, never duplicate descendants.
9. Call repair on an invalidated/non-current block: refuse.
10. Force `AdapterRejected`: no amendment/pass/candidate/receipt commits; calculation failure persists; restart exposes retry.
11. Retry after calculation failure: one successful repair population and preserved prior failure history.
12. Force worker refusal: refusal persists; restart exposes an ordinary next action; no proposal/decision/candidate exists.
13. Force runtime startup/collection failure: bounded outcome persists; no HTTP 500; restart exposes retry.

### UI and restart

14. Candidate page contains exact 10-K identity/locator, original/candidate identities, named synthetic use, unchanged-original statement, equal-value source explanation, two consequences, engine, and error state.
15. Page contains no professional reliance, generic approval, raw ID entry, packet JSON, NTM control, or Casebook vocabulary.
16. Restart after block, runtime failure, refusal, calculation failure, successful candidate, disposition, and invalidation reconstructs the same current state and next action from PostgreSQL only.

## 11. Fresh joined evidence

After all deterministic tests pass, run one new synthetic Case A episode through one real NTM/Codex worker. Do not reuse the prior database rows or call the management seed command a live path.

The receipt must include:

- exact branch/base/result and changed-file audit;
- environment and executable versions;
- exact work-order and output digests;
- closed-search evidence;
- canonical 8-K block and zero candidate;
- one attributed repair and canonical 10-K pass;
- candidate/receipt transaction evidence;
- original/candidate digests and declared consequences;
- synthetic disposition;
- restart evidence;
- correction seed;
- forced runtime/refusal/calculation-failure recovery evidence;
- migration/rollback evidence;
- full test counts; and
- explicit nonclaims.

The worker return is not accepted until a fresh independent verifier reproduces every P0/P1 counterexample and reruns the joined episode from a clean or reconciled environment.

## 12. Classifier dependency

Historical Packet 007 is superseded. A separate current-head classifier packet must operate on the exact evidence tree containing:

- `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md` inside the executable package; and
- `scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`.

It must classify the evidence markdown as strict UTF-8 `docs_data`, classify only the exact validated OOXML fixture as binary test data with zero physical lines, and keep every unknown or malformed binary fail-closed.

Classifier repair remains disjoint from product code. Final integration requires the repaired classifier and the complete adversarial suite on the integrated repair candidate.

## 13. Direct Excel state

Direct Excel work is suspended during this repair. Packet 006 is not advanced, and no Excel/native-workflow claim may be made. A new current-base direct-surface packet may be compiled after the repaired product candidate survives hostile verification.

## 14. Stop conditions

The repair worker must stop and return exact evidence when:

- the rejected base moved or contains unexpected additional code;
- the repair requires weakening append-only, owner, closed-source, or synthetic-use boundaries;
- the database cannot recompute the target-specific decision without trusting application-authored `PASS` fields;
- a candidate cannot be transactionally joined to one receipt;
- runtime/calc retry requires mutating prior evidence;
- migration `0007` cannot preserve upgrade and rollback evidence;
- a second repair attempt fails with the same causal diagnosis; or
- any protected data, personal workbook, external release, or professional reliance authority becomes necessary.

## 15. Claim ceiling

Successful repair would establish only a repaired synthetic Case A candidate ready for fresh hostile verification. It would not establish analyst usefulness, professional correctness, permission to rely, Excel compatibility, arbitrary workbook support, tenant security, harness improvement, deployment, client readiness, or verified V0.
# Milestone 2 Rejection and Repair Adjudication Receipt

Verdict: `REJECT_PENDING_BOUNDED_REPAIR`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Prior PRO dispatch head: `dee299679562db02f051997f244868e86d6e0a0e`
- Rejected branch: `agent/case-a-outcome-complete-v0`
- Rejected implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`
- Rejected evidence head: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Rejected receipt: `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
- Coordinator projection: `dec-2026-08-18-037`
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Product repair branch/head: `agent/case-a-authority-recovery-repair-v1` at `3c496b3bb0e87b8c6eb6a4f5a1a4460f7864b82e`
- Classifier repair branch/head: `agent/classifier-final-surface-repair-v1` at `cde37777ebdb6944b463a54d2529873c7dc03c56`
- Product repair issue: `#8`
- Classifier repair issue: `#9`

## Diff and receipt inspection

The implementation changes 25 product, migration, runtime, protocol, fixture, template, and test files; the evidence head adds the Packet 005 receipt. The changed-file population remained inside Packet 005 ownership. The rejection is therefore not an ownership verdict. It is a semantic-authority and recovery verdict.

The receipt accurately records a real joined NTM/Codex happy path, but its recommendation to accept the candidate is rejected because independent adversarial execution reached states its focused tests did not cover.

## Evidence retained narrowly

The following are retained as historical mechanism evidence:

- one real NTM/Codex worker ran with `closed_captured_sources`;
- the application gate blocked the equal-valued annual 8-K proposal;
- an attributed 10-K replacement proposal was produced;
- the bounded LibreOfficeDev proxy produced a child workbook and two declared recalculated consequences;
- a synthetic disposition, restart projection, and correction seed were exercised;
- focused model-change replay passed 25 tests;
- owned-job/workbook replay passed 19 tests; and
- Django check, migration-drift check, boundary check, and diff check passed in the reported environment.

These observations do not establish database authority, recoverability, product verification, or readiness.

## Executable findings adopted

### P0 — candidate-authority bypass

Migration `0006_model_change_v0_guards.py` permits a candidate when the referenced stored decision says `PASS` and structural joins match. It does not recompute the object- and use-specific target/source rule, require the canonical validator/reason, or require a matching calculation receipt at transaction completion.

A direct-SQL attacker inserted `validator=attacker/v0`, `PASS` for the annual 8-K proposal that the application gate had blocked, then inserted a candidate. This violates the accepted severity-one requirement that deterministic admission be enforced at the database boundary.

### P1 — repeat repair

`repair_wrong_source()` accepts an already-invalidated block more than once and can produce distinct amendments, replacement proposals, pass decisions, and candidates.

### P1 — unrecoverable calculation failure

Repair commits amendment, replacement, invalidation, and `PASS` before candidate creation. Adapter rejection can escape as HTTP 500 and restart leaves a current pass with no candidate, receipt, block action, or retry.

### P1 — refusal loss

`RunService` returns a bounded refusal, but the view discards it. Restart shows a work order without proposal, decision, candidate, refusal, or next action.

### P1 — classifier evidence mismatch

At the evidence head the classifier first fails on package-level `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`, not the workbook. The independently reproduced complete-suite population is 143 discovered, 138 executed, one setup error. Packet 007’s binary-only contract is stale.

### P1 — candidate-review evidence gap

The candidate view omits the exact 10-K assertion and locator, original and candidate artifact identities, named synthetic use, explicit unchanged-original fact, and the equal-value/annual-report explanation required by the vertical contract.

## Code-backed adjudication

The findings are consistent with the inspected implementation:

- `AdmissibilityGate.evaluate()` creates a stored result, while the candidate database trigger trusts stored `outcome = PASS` rather than recomputing it.
- `repair_wrong_source()` lacks a current, unused, single-repair guard.
- `use_filed_report()` invokes repair and candidate creation sequentially, catches only `ModelChangeRejected`, and can strand pass authority when the adapter raises another bounded exception.
- `RunService.run()` returns refusal data but the view ignores the return value.
- `ProjectionService.resume()` has no canonical technical outcome or refusal projection.
- the candidate template renders calculation summary and consequences but not the complete source/artifact/use evidence.

The coordinator’s six findings are adopted rather than challenged.

## Governing changes

Created and expanded:

- `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- `docs/pro/worker-packets/008_CASE_A_AUTHORITY_RECOVERY_REPAIR_V1.md`
- `docs/pro/worker-packets/009_FINAL_CLASSIFIER_SURFACE_REPAIR_V1.md`
- `docs/pro/DECISION_LEDGER_CONTINUATION_2026-08-18.jsonl`

Updated:

- `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`
- this receipt
- draft PR #2 and GitHub issues after final reconciliation

Operationally created:

- `agent/case-a-authority-recovery-repair-v1`
- `agent/classifier-final-surface-repair-v1`
- issue `#8`
- issue `#9`

## Authority reconciliation

- Packet 005: rejected historical implementation evidence; issue `#5` closed.
- Packet 006: suspended; issue `#6` closed. Direct Excel may not advance.
- Packet 007: superseded; issue `#7` closed.
- Packet 008: active and the only product-code repair authority.
- Packet 009: active classifier-hygiene authority with disjoint files.

The rejected code is not merged into `agent/pro-grounding`.

## Packet 008 completion boundary

Packet 008 must:

- install PostgreSQL-recomputed canonical admission for decision and candidate inserts;
- require an exact matching calculation receipt at transaction commit;
- make filed-report repair current, single-use, concurrent-safe, and idempotent;
- persist runtime failure, worker refusal, and calculation failure with ordinary retry actions;
- retain the original block when candidate calculation fails;
- restore exact source, artifact, named-use, unchanged-original, and equal-value evidence in candidate review;
- add only migration `0007_model_change_v0_repair_1.py` without rewriting 0005/0006;
- run direct-SQL hostile regressions and one fresh real NTM/Codex episode; and
- return a receipt for fresh independent verification without merging.

## Packet 009 completion boundary

Packet 009 must:

- classify package `docs/pro/evidence` text as strict UTF-8 `docs_data`;
- narrowly validate and measure only the exact authorised OOXML fixture as binary test data with zero physical lines;
- reject malformed, misplaced, symlinked, disguised, or unknown binary surfaces;
- rerun the complete adversarial suite and record fresh counts; and
- touch no product code or fixtures.

## Independent verification gate

Both workers return exact commits and receipts directly to PRO and coordinating Codex. PRO must inspect ancestry, ownership, diffs, migrations, tests, live evidence, restart, rollback, and the classifier result. A fresh verifier must reproduce all P0/P1 counterexamples and the new joined episode before any integration or verified-V0 claim.

## Evidence ceiling

This receipt establishes that Packet 005 is rejected for concrete, code-backed authority and recovery defects, and that two bounded repair packets now own disjoint surfaces. It does not establish a repair, classifier success, verified V0, analyst usefulness, Excel support, professional correctness, permission to rely, harness improvement, deployment, or client readiness.

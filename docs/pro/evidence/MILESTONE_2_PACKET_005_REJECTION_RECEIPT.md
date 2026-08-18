# Milestone 2 Packet 005 Rejection Receipt

Verdict: `REJECT_PENDING_BOUNDED_REPAIR`.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- PRO branch before adjudication: `agent/pro-grounding` at `dee299679562db02f051997f244868e86d6e0a0e`
- Packet 005 branch: `agent/case-a-outcome-complete-v0`
- Implementation commit: `cf5685383654c00513825fc451b60221bc0117e9`
- Evidence head: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Worker receipt: `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
- Coordinator independent verdict: reject pending bounded repair
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Repair contract commit: `21384f3bdd6510fda78f8e1d8cacae91ca7efe46`
- Product repair packet: `docs/pro/worker-packets/008_CASE_A_AUTHORITY_RECOVERY_REPAIR_V1.md`
- Classifier repair packet: `docs/pro/worker-packets/009_FINAL_CLASSIFIER_SURFACE_REPAIR_V1.md`

Packet 005 is not merged into `agent/pro-grounding`, not deployed, not promoted, and not called verified V0.

## Diff and receipt audit

The evidence head is two commits ahead of the authorised dispatch head. The implementation commit added the model-change protocol, additive migrations `0005` and `0006`, the model-change service/view/template package, fixtures and adversarial tests. The evidence commit added only the package-level implementation receipt.

The receipt accurately records a real joined happy path and several mechanism results, but its recommendation and strongest closure claims are rejected because fresh hostile execution bypassed the asserted database authority and exposed unrecoverable states.

## Findings adopted

### P0 candidate-authority bypass

The PostgreSQL candidate trigger joins a stored `AdmissibilityDecision` row and tests `decision.outcome = 'PASS'`. It does not recompute the target-specific source/target decision, require the canonical validator version and reason, or require a matching calculation receipt at transaction completion.

The coordinator inserted an attacker-authored `PASS` for the annual 8-K proposal that the application gate correctly blocked, then inserted a candidate. The database therefore did not enforce the advertised deterministic admission boundary.

### P1 repeatable repair

The filed-report repair accepts a historical/inactivated block without a currentness or uniqueness check. Repeating the command can create multiple amendments, replacement proposals, pass decisions and candidate attempts.

### P1 unrecoverable calculation failure

Repair and pass commit before candidate calculation. A bounded adapter rejection can escape as HTTP 500 and leave a current `PASS`, no candidate, no receipt, no current source block and no legal retry action after restart.

### P1 refusal loss

The runtime/parser can return a bounded worker refusal, but the view discards it. No canonical refusal record or next action survives restart.

### P1 final-tree classifier mismatch

At evidence head `3d5c3157...`, the classifier fails first because the new executable-package path `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md` is unclassified. The prior receipt's binary-workbook-only explanation and reported suite count are stale. The fresh coordinator result was 143 discovered, 138 executed, one architecture setup error.

### P1 candidate-review evidence gap

The candidate page omits the exact captured 10-K assertion and locator, original/candidate artifact identities, named synthetic use, explicit unchanged-original fact, and the explanation that the equal-valued 8-K was blocked because this annual target requires the filed annual report.

## Evidence retained narrowly

The following remain useful historical evidence:

- one real NTM/Codex worker executed with captured sources and search closed;
- the application gate blocked the equal-value annual 8-K proposal;
- an attributed 10-K replacement was created;
- the bounded LibreOfficeDev proxy produced a recalculated child workbook and two declared consequences;
- a synthetic disposition, restart projection and correction seed were exercised;
- focused model-change tests passed 25 of 25;
- owned-job/workbook tests passed 19 of 19; and
- Django, migration-drift, boundary and diff checks passed in the reported environment.

These results justify one repair cycle. They do not license integration while the database authority can be forged.

## Repair authority

### Packet 008

- Branch: `agent/case-a-authority-recovery-repair-v1`
- Starting head: `3c496b3bb0e87b8c6eb6a4f5a1a4460f7864b82e`
- Issue: `#8`
- Base: rejected evidence head `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Ownership: one architectural writer over the exact database, service, projection, route and hostile-test repair surfaces

Packet 008 must make the database recompute canonical admission, require candidate/receipt completeness, make repair single-use and idempotent, persist runtime/refusal/calculation-failure outcomes, expose ordinary retry actions, restore candidate-review evidence, run one fresh real joined episode and return for independent verification.

### Packet 009

- Branch: `agent/classifier-final-surface-repair-v1`
- Starting head: `cde37777ebdb6944b463a54d2529873c7dc03c56`
- Issue: `#9`
- Base: rejected evidence head `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Ownership: classifier and focused hostile tests only

Packet 009 supersedes Packet 007. It must classify strict UTF-8 package evidence and only the exact validated OOXML fixture, with all unknown or malformed binary content failing closed.

## Packet and issue reconciliation

- Packet 005: rejected historical implementation evidence; Issue #5 closed `not_planned`.
- Packet 006: suspended; Issue #6 closed `not_planned`; no direct Excel work advanced.
- Packet 007: superseded by Packet 009; Issue #7 closed `not_planned`.
- Packet 008: active bounded product repair; Issue #8 open.
- Packet 009: active disjoint classifier repair; Issue #9 open.

No stale packet is silently active.

## Required next gate

Packet 008 and Packet 009 return exact commits and receipts without merge authority. PRO and coordinating Codex inspect the diffs, reproduce all named counterexamples, integrate only compatible changes on a fresh candidate branch, rerun the full deterministic and joined episode evidence, and commission an independent hostile verifier.

Direct Excel remains suspended until the repaired product candidate survives that verification.

## Evidence ceiling

This receipt establishes that Packet 005 was independently rejected for one P0 and five P1 defects; that the successful happy-path evidence remains bounded historical evidence; and that exact repair ownership, branches, packets and issues now exist.

It does not establish a repaired product, classifier pass, verified V0, analyst usefulness, professional correctness, permission to rely, Excel compatibility, arbitrary workbook support, harness improvement, deployment or client readiness.
# Milestone 2 Packet 011 Runtime-Trust Adjudication Receipt

Verdict: `ACCEPT_EXTERNAL_RUNTIME_BLOCKER_DIAGNOSIS`.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Governing PRO basis before adjudication: `agent/pro-grounding` at `1b8f221162f5dfc2841ab530ddf9cfdc7e5ebfd3`
- Packet 011 branch: `agent/case-a-joined-runtime-diagnosis-v0`
- Packet 011 starting head: `c253194730915a8e36b3cf188253c30e901087a7`
- Packet 011 evidence head: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Receipt: `docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`
- Worker verdict: `EXTERNAL_RUNTIME_BLOCKER`
- Worker delta: receipt only

No product replay was run after the neutral control failed. No Packet 010 product code is merged, deployed, promoted, or described as verified V0.

## Finding adopted

Codex did not read the product or neutral control instruction. The launcher changed Codex's working directory to a fresh standalone output directory while passing a process-local trust override only for the repository root. Codex therefore stopped at its interactive directory-trust question:

```text
Do you trust the contents of this directory?
1. Yes, continue
2. No, quit
```

NTM could not answer the prompt non-interactively, reported `AGENT_ERROR`, and the output root remained empty.

The same-environment neutral control used no Case A packet, workbook, source rule, product prompt, search, browser, or private data and failed at the same pre-instruction boundary. The current evidence therefore attributes the observed failure to the launcher trust/working-directory contract rather than to the Packet 010 source-custody logic or Case A instruction.

## RETAIN / AMEND / RETRACT / ADD / DEFER / BLOCK

### RETAIN

- Packet 010's independently accepted deterministic source-custody repair as bounded branch evidence.
- Packet 008's bounded authority, idempotency, recovery, candidate-review, restart, rollback, and prior live-path evidence.
- Failure containment: both Packet 010 attempts and the neutral control created no proposal, decision, candidate, or receipt.
- The continuing company-research environment and joined professional interaction as reversible falsifiable V0 contracts, not analyst-validated product truth.

### AMEND

- Amend the active diagnosis from generic NTM/Codex instability to a reproducible directory-trust mismatch at the launch boundary.
- Amend the next action from product replay to one least-privilege, control-only launcher repair.
- Keep programme state `REPAIRING`.

### RETRACT

- Retract any implication that Packet 010's `AGENT_ERROR` was caused by its product packet, source-custody logic, model prompt, collector, or external model service.
- Retract any implication that a tracked send means Codex consumed the instruction.
- Retract any claim that an end-to-end analyst product exists.

### ADD

- Add an exact process-scoped trust override for the one host-created Codex working/output directory when it lies outside the already trusted repository project.
- Add deterministic tests proving exact-path scope, no parent/wildcard trust, no persistent config mutation, unchanged sandbox/approval/network policy, and unchanged non-model-change launch behaviour.
- Add one same-environment neutral runtime control after the repair.

### DEFER

- Defer an exact Case A replay until the repaired neutral control succeeds and its return is independently audited.
- Defer Packet 009 classifier hygiene, direct Excel, product-form expansion, cold analyst testing, and the correction-to-evaluation loop.

### BLOCK

- Block broad or permanent trust of `/tmp`, the campaign root, home, repository parent, or arbitrary descendants.
- Block a human click as an operational dependency.
- Block `danger-full-access`, sandbox weakening, `--add-dir` expansion, prompt changes, model changes, timeout changes, network/search changes, and product replay inside the trust-repair packet.
- Block merge, deployment, verified-V0, analyst-validation, Excel-support, professional-reliance, client-readiness, and product-completion claims.

## Causal next action

Compile one bounded launch/trust repair from Packet 011 evidence head. The implementation may change only launcher construction and its focused tests. It must pass a neutral control in the same standalone working-directory class without writing persistent Codex trust state. A successful control is runtime-boundary evidence only; a separately authorised current-head Case A replay remains required.

## Evidence ceiling

This receipt establishes the cause of the observed Packet 010 and Packet 011 pre-output failures and licenses one narrow launcher repair. It does not establish a repaired launcher, a successful control, joined product execution, integration, verified V0, analyst usefulness, native Excel support, source entitlement, professional correctness, permission to rely, harness improvement, deployment, security readiness, production readiness, client readiness, or programme completion.
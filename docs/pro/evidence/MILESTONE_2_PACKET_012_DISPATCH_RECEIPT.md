# Milestone 2 Packet 012 Dispatch Receipt

Programme state: `REPAIRING`.

Dispatch status: `ACTIVE_CONTROL_ONLY`.

Recorded: 18 August 2026.

## Exact basis

- Diagnosis evidence head: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Diagnosis verdict: `EXTERNAL_RUNTIME_BLOCKER`
- Trust-repair contract: `docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`
- Contract blob: `d454190d7b6f7d66c31bdcd9fdc938d77a262a90`
- Packet: `docs/pro/worker-packets/012_CODEX_OUTPUT_ROOT_TRUST_CONTROL.md`
- Packet blob: `aba7052cad0a4fbbebb5a69a1f707971bf012779`
- Worker branch: `agent/codex-output-root-trust-control-v0`
- Exact starting head: `dd093113525645383e17cd51e7a1cff8592a624e`
- Coordination: GitHub issue `#11`

## Branch audit

The worker head is a non-force-pushed descendant of the diagnosis evidence head. Its net diff from `b673569...` is exactly:

```text
A  docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md
A  docs/pro/worker-packets/012_CODEX_OUTPUT_ROOT_TRUST_CONTROL.md
```

The diagnosis contract, Packet 011 and diagnosis receipt remain byte-identical to the basis. An intermediate tree-construction omission was detected before dispatch and repaired by an ordinary follow-up commit; the final net tree is exact and history was not rewritten.

The contract and packet blobs on the worker branch are identical to PRO.

## Authority

Packet 012 owns only:

```text
prototypes/equities-research-cognition/product/campaign/services.py
prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py
docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md
```

It may add an invocation-scoped Codex trust override for the exact canonical model-change output root and run one neutral control. It may not run Case A.

## Preserved restrictions

Packet 012 may not change NTM, settings, prompts, models, timeouts, packet schemas, migrations, source custody, candidate or calculation logic, UI, sandbox mode, approval policy, no-search policy, writable-directory scope, credentials, persistent Codex configuration, classifier work, Excel work, or governing state.

Broad trust, a human click, `danger-full-access`, `--add-dir`, and trust of a parent, temporary root, campaign root, home, wildcard, sibling, or another work order are forbidden.

## Return and next gate

The worker returns one exact receipt and verdict without merge authority. A successful neutral control requires independent audit. Only a later PRO decision may compile a separate exact-current-head Case A replay.

## Evidence ceiling

This receipt establishes an exact, parity-checked, least-privilege runtime-repair dispatch. It does not establish a repaired launcher, successful control, Case A execution, end-to-end product, integration, verified V0, analyst validation, Excel support, professional reliance, deployment, security readiness, production readiness, client readiness, or programme completion.
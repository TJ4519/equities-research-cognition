# Milestone 2 Packet 014 Comparison Compilation Receipt

Programme state: `REPAIRING`.

Status: `COMPILED_BUT_BLOCKED_ON_CLEANUP`.

Recorded: 18 August 2026.

## Exact basis

- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Process-model contract: `docs/pro/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md`
- Contract blob: `4cd99a031d0bbcc76b3a8b43f4d9355be2dd07cf`
- Packet: `docs/pro/worker-packets/014_CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON.md`
- Packet blob: `6be67a07ef8d8729527eb7b09594e47ab12f6091`
- Comparison branch: `agent/codex-process-model-comparison-v0`
- Audit head: `bd0ea9c089d9da110dbefe26ecabc0a91944b0fc`
- Cleanup prerequisite: Packet 013 and independent acceptance

## Branch audit

The comparison branch descends from `32259dd...`. Its net diff from that evidence head is exactly:

```text
A  docs/pro/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md
A  docs/pro/worker-packets/014_CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON.md
```

The contract and packet blobs match PRO.

## Activation law

Packet 014 has no live authority until coordinating Codex verifies all of:

```text
Packet 013 independent verdict = accepted
config size = 13784
config sha256 = 0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
config mode = 0600
config owner = effective UID
strict TOML parse = pass
```

No comparison issue is open at this state.

## Comparison boundary

The retained interactive NTM/TUI arm comes from Packet 011 and Packet 012 evidence; it is not rerun.

The only possible later live arm is one neutral `codex exec` process-start experiment. The worker may add a neutral experiment tool, its tests and its receipt. It may not modify product services, NTM, prompts, models, source policy, workbook logic, UI, schemas or existing tests.

The comparison must retain process identity, stdout/stderr, exit code/signal, descriptor-bound cwd, effective-UID ownership, exact output-file custody and before/after persistent-state evidence.

## Evidence ceiling

This receipt establishes exact contracts for a later neutral comparison. It does not authorise execution before cleanup, select a runtime process model, repair the product runtime, prove Case A, or establish end-to-end product completion.

# Current Semantic Checkpoint

Packet 012 is rejected: its live Codex process persisted the exact temporary output-root trust entry into the user's config, NTM reported completion while the declared output root remained empty, and the compile-time path check did not bind the directory through process start or verify effective-UID ownership.

Status: `REPAIRING`.

Checkpoint date: 18 August 2026.

Packet 013 is active as environment restoration only. Packet 014 is compiled for coordinator audit but blocked from live execution until Packet 013 is independently accepted.

## Exact repository and evidence basis

- Repository: `TJ4519/equities-research-cognition`
- Governing handoff branch: `agent/pro-responsibility-handoff`
- Verified handoff commit: `c1fc568424facbb5bb8e1b6369d30a1f380ae308`
- PRO branch: `agent/pro-grounding`
- PRO parent basis before this checkpoint update: `9fff7369845d35731048e966233a890a283faa83`
- Packet 010 implementation: `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`
- Packet 010 evidence head: `a7df89f22f1783b529d9f31654234ed6de82eb62`
- Packet 010 status: deterministic source-custody repair accepted with exact narrowing; unmerged
- Packet 011 evidence head: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Packet 011 verdict: `EXTERNAL_RUNTIME_BLOCKER`
- Packet 012 branch: `agent/codex-output-root-trust-control-v0`
- Packet 012 starting head: `dd093113525645383e17cd51e7a1cff8592a624e`
- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Packet 012 worker verdict: `CONTROL_REACHED_RUNTIME_BUT_FAILED`
- Packet 012 independent verdict: `REJECT`
- Packet 012 adjudication: `docs/pro/evidence/MILESTONE_2_PACKET_012_REJECTION_ADJUDICATION_RECEIPT.md`
- Coordinator projection: `dec-2026-08-18-045`

No Packet 005, 008, 010 or 012 product/runtime code has been merged into `agent/pro-grounding`. No deployment, classifier work, direct-Excel work, professional-use transition, harness promotion or external release is authorised.

## Governing read order

A fresh owner, coordinator, implementor or verifier must:

1. verify repository, branch, commit, ancestry and divergence;
2. read root and package `AGENTS.md` and `ROUTE.md`;
3. read `PRO_RESPONSIBILITY_PROMPT.md`;
4. read `docs/pro/PRO_CONSTITUTION.md`;
5. read `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`;
6. read `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001;
7. read the product architecture, professional interaction, conceptual-model, evaluation and slop contracts;
8. read the hostile vertical and Case A contracts;
9. read Packet 005, 008 and 010 receipts only as bounded worker evidence;
10. read independent adjudications through Packet 010;
11. read the Packet 011 contract, receipt and adjudication;
12. read the Packet 012 contract, packet, receipt and rejection adjudication;
13. read both decision-ledger continuation files and this checkpoint;
14. for active cleanup, read `CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md` and Packet 013 only; and
15. for later comparison audit, read `CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md` and Packet 014 only after cleanup evidence.

Historical, rejected, suspended or completed packets do not regain authority by implication.

## Packet 012 findings

### Persistent trust mutation

The active Codex user config was observed before the live process as:

```text
size    13784
sha256  0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
mode    0600
```

After the live process it was:

```text
size    13912
sha256  4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
mode    0600
```

Read-only verification found one final trusted project entry for the now-deleted Packet 012 output path. The raw path is private and must not be published.

The trust override was therefore not process-local in the tested TUI path.

### False completion

NTM reported `condition=complete`, but the output root remained empty. No `result.json`, pane transcript, child PID, exit code or signal was retained. Neither instruction consumption nor clean Codex completion is established.

### Launch-time path gap

Packet 012 validated symlink state, canonical path and mode while compiling launcher bytes. NTM started Codex later. A path replacement window remained, and effective-UID ownership was not checked.

## RETAIN / AMEND / RETRACT / ADD / DEFER / BLOCK

### RETAIN

- Packet 011's diagnosis that the prior TUI run stopped before instruction consumption at a trust prompt.
- Packet 012's deterministic compile-time path and launcher-argument tests as narrow mechanism evidence.
- Packet 010's deterministic source-custody controls as bounded branch evidence.
- Packet 008's authority, idempotency, recovery, candidate-review, restart, rollback, correction and prior live-path evidence as bounded history.
- The continuing company-research environment and joined professional interaction as reversible falsifiable product contracts, not analyst-validated truth.

### AMEND

- The active runtime problem is now the interactive TUI process contract, not merely a missing trust argument.
- Success requires process identity, streams, exit status and exact artifact population together.
- The active sequence is user-environment restoration, then a neutral process-model comparison, then a separately authorised runtime implementation and control.

### RETRACT

- Invocation project trust was not process-local.
- NTM `condition=complete` is not sufficient evidence of instruction execution or bounded-work completion.
- Compile-time path checks do not establish launch-time cwd integrity.
- Packet 012 is not a runtime repair candidate.
- No end-to-end analyst product exists.

### ADD

- Exact hash-guarded cleanup with recoverable backup and byte-identical pre-control restoration.
- Effective-UID and descriptor-bound cwd requirements.
- PID/PGID, bounded stdout/stderr, exit code/signal and artifact-gated completion.
- A neutral comparison between retained interactive NTM/TUI evidence and an automation-oriented `codex exec` process-start model.

### DEFER

- All further Codex execution until cleanup is independently accepted.
- Case A until a runtime interface is selected, implemented and independently controlled.
- Packet 009, direct Excel, product-form expansion, cold analyst testing and the correction-to-evaluation loop.

### BLOCK

- Another `projects.<path>.trust_level` launcher patch.
- Broad or permanent trust, human trust clicks, sandbox weakening, `--add-dir`, prompt/model/timeout changes or a blind retry.
- Product UI/schema/source-policy changes in response to runtime evidence.
- Merge, deployment, verified-V0, analyst-validation, Excel-support, professional-reliance, client-readiness and completion claims.

## Active Packet 013 — exact config restoration

- Contract: `docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`
- Packet: `docs/pro/worker-packets/013_CODEX_STALE_TRUST_CLEANUP.md`
- Branch: `agent/codex-stale-trust-cleanup-v0`
- Starting head: `1a0e4a5b838cfa1ed4b5dc401cce8a7b668934bd`
- Contract blob: `327c8a70d813eea1cda35a1853d663d636de3059`
- Packet blob: `6049039485a70c6739db38e22800c1f7bec3133f`
- Issue: `#12`
- Required receipt: `docs/pro/evidence/CODEX_STALE_TRUST_CLEANUP_RECEIPT.md`

Its initial net diff from Packet 012 evidence head is exactly the cleanup contract and Packet 013.

Packet 013 may mutate only:

- the active Codex user `config.toml`; and
- one private `0700` backup directory containing an exact `0600` before-image.

It may add only its receipt to the branch. No Codex, NTM, neutral control, product code or Case A may run.

Mutation is allowed only when the file remains exactly:

```text
size    13912
sha256  4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
mode    0600
owner   effective UID
```

Success requires byte-identical restoration to:

```text
size    13784
sha256  0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
mode    0600
owner   effective UID
TOML    valid
```

The backup remains private and retained until independent verification accepts the cleanup.

## Compiled Packet 014 — process-model comparison

- Contract: `docs/pro/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md`
- Packet: `docs/pro/worker-packets/014_CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON.md`
- Branch: `agent/codex-process-model-comparison-v0`
- Audit head: `bd0ea9c089d9da110dbefe26ecabc0a91944b0fc`
- Contract blob: `4cd99a031d0bbcc76b3a8b43f4d9355be2dd07cf`
- Packet blob: `6be67a07ef8d8729527eb7b09594e47ab12f6091`
- State: compiled, not active, no issue

Its initial net diff from Packet 012 evidence head is exactly the comparison contract and Packet 014.

Packet 014 cannot run until independent cleanup acceptance. It owns only a new neutral comparison tool, a new test and its receipt; it owns no existing product or runtime file.

The retained interactive NTM/TUI arm is supplied by Packet 011 and Packet 012 evidence. It is not rerun. The possible live arm is one automation-oriented `codex exec` process-start experiment with:

```text
--skip-git-repo-check
--ephemeral
--ignore-user-config
--sandbox workspace-write
--ask-for-approval never
--json
--output-schema <host evidence path>
--output-last-message <host evidence path>
-m <pinned model>
-
```

No project trust override or `--search` is permitted. Exact installed help must confirm flags before use.

The neutral harness must bind cwd through an open directory descriptor, verify effective UID/mode/device/inode, supply the instruction on stdin before exec, retain PID/PGID/stdout/stderr/exit/signal, and require exact `result.json` population in addition to clean process exit.

The comparison may recommend a future `CodexExecAdapter` or exact NTM interface changes. It may not implement the product runtime.

## Does an end-to-end user product exist?

No.

The execution/evidence kernel and most Case A mechanisms are implemented and strongly tested on candidate branches. Packet 008 completed a live synthetic chain but retained unsafe source custody. Packet 010 closes the tested source-custody defect but its product instruction was never consumed because of the TUI boundary. Packet 012 did not prove a safe neutral execution path.

No single exact safe branch has completed:

```text
authenticate
-> resume a recognisable modelling job
-> inspect and confirm one professional object
-> authorise real agent work
-> receive a typed proposal
-> contain the wrong-source case
-> repair it
-> calculate a candidate
-> review and dispose it
-> restart
-> seed a protected correction
```

The analyst-facing product form, native Excel path, cold analyst evidence and correction-to-evaluation loop remain incomplete.

## Product layers

### Execution and evidence kernel

Substantially implemented and tested on candidate branches, but not integrated. It includes ownership, exact artifacts, work orders, typed outcomes, source custody and admission, candidate/receipt atomicity, correction/recovery state, restart and rollback. Its current interactive runtime boundary is rejected.

### Case A proof vertical

Most deterministic mechanisms and prior live slices exist, but no safe current head has completed the entire proposal-to-candidate path.

### Analyst-facing product shell

A narrow synthetic workspace exists. It is not analyst validated, native-Excel proven or cold-tested. No new UI or schema is authorised by the current runtime work.

### Learning and evaluation loop

Not implemented beyond a `CorrectionRecord` seed. There is no protected baseline/treatment runner, causal responsible-layer attribution, held-out corpus, review-cost comparison, scoped promotion or executable harness rollback.

## Packet state

- Packet 001: closed historical workbook mechanism evidence.
- Packets 002 and 003: stale historical instructions.
- Packet 004: closed hostile architecture evidence.
- Packet 005: rejected implementation evidence.
- Packet 006: suspended; direct Excel may not advance.
- Packet 007: superseded historical classifier work.
- Packet 008: rejected integration candidate; bounded evidence retained.
- Packet 009: suspended.
- Packet 010: accepted only as bounded deterministic source-custody evidence; unmerged.
- Packet 011: completed diagnosis evidence.
- Packet 012: rejected; Issue `#11` closed.
- Packet 013: active cleanup through Issue `#12`.
- Packet 014: compiled but blocked on cleanup acceptance.

## Human-only authority

Protected, client, analyst or personal data; personal workbooks; permanent credentials; API consent; account administration; material expenditure; analyst/client contact; external release; investment/legal/publication judgment; professional permission to rely; and production-tenant harness promotion remain human-only unless explicitly delegated.

## Evidence ceiling

The repository has an independently rejected Packet 012, an exact stale-config cleanup contract and a gated process-model comparison contract.

It does not have cleanup success, a selected safe runtime process, a successful safe Case A replay, an end-to-end product, an integrated branch, verified V0, analyst validation, native Excel support, professional correctness, permission to rely, harness improvement, deployment, security readiness, production readiness, client readiness or programme completion.

This is not a product demo.

## Next action

Packet 013 executes through Issue `#12` and returns its receipt directly to PRO and coordinating Codex. Packet 014 remains blocked and has no execution issue. No routine human decision is required at this gate.

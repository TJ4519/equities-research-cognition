# Current Semantic Checkpoint

Packet 011 proved that Codex never reached either the Packet 010 product instruction or the neutral runtime-control instruction: the launcher selected a standalone output directory as Codex's working directory while trusting only the repository project, so Codex stopped at an interactive directory-trust prompt that NTM could not answer.

Status: `REPAIRING`.

Checkpoint date: 18 August 2026.

Packet 012 is active as the only bounded work. It may repair exact process-local output-root trust and run one neutral control. It may not run Case A.

## Exact repository and evidence basis

- Repository: `TJ4519/equities-research-cognition`
- Governing handoff branch: `agent/pro-responsibility-handoff`
- Verified handoff commit: `c1fc568424facbb5bb8e1b6369d30a1f380ae308`
- PRO branch: `agent/pro-grounding`
- PRO parent basis before this checkpoint update: `e5c0b9233b6cfd8cd901a42666dde8b930340dc9`
- Packet 010 implementation: `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`
- Packet 010 evidence head: `a7df89f22f1783b529d9f31654234ed6de82eb62`
- Packet 010 status: deterministic source-custody repair accepted with exact narrowing; unmerged
- Packet 011 branch: `agent/case-a-joined-runtime-diagnosis-v0`
- Packet 011 starting head: `c253194730915a8e36b3cf188253c30e901087a7`
- Packet 011 evidence head: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Packet 011 verdict: `EXTERNAL_RUNTIME_BLOCKER`
- Packet 011 receipt: `docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`
- Packet 011 adjudication: `docs/pro/evidence/MILESTONE_2_PACKET_011_RUNTIME_TRUST_ADJUDICATION_RECEIPT.md`
- Trust-repair contract: `docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`
- Packet 012: `docs/pro/worker-packets/012_CODEX_OUTPUT_ROOT_TRUST_CONTROL.md`
- Packet 012 branch: `agent/codex-output-root-trust-control-v0`
- Packet 012 starting head: `dd093113525645383e17cd51e7a1cff8592a624e`
- Packet 012 coordination: GitHub issue `#11`

No Packet 005, 008, 010, or 012 product/runtime code is merged into `agent/pro-grounding`. No deployment, classifier work, direct-Excel work, professional-use transition, harness promotion, or external release is authorised.

## Governing read order

A fresh owner, coordinator, implementor, or verifier must:

1. verify repository, branch, commit, ancestry, and divergence;
2. read root and package `AGENTS.md` and `ROUTE.md`;
3. read `PRO_RESPONSIBILITY_PROMPT.md`;
4. read `docs/pro/PRO_CONSTITUTION.md`;
5. read `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`;
6. read `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001;
7. read the product architecture, professional interaction, conceptual-model, evaluation, and slop contracts;
8. read the hostile vertical and Case A contracts;
9. read Packet 005, 008, and 010 receipts only as bounded worker evidence;
10. read the independent adjudications through Packet 010;
11. read `docs/pro/JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md` and the Packet 011 receipt;
12. read the Packet 011 adjudication and `CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md`;
13. read both decision-ledger continuation files and this checkpoint;
14. inspect the exact launcher implementation without changing unrelated runtime or product surfaces; and
15. read only Packet 012 for the active branch.

Historical, rejected, suspended, or completed packets do not regain authority by implication.

## Packet 011 adjudication

### Finding accepted

The normalized model-change launcher used:

```text
--sandbox workspace-write
--ask-for-approval never
--cd <standalone per-work-order output root>
-c projects."<repository root>".trust_level="trusted"
-m <pinned model>
```

The actual working directory was outside the trusted repository Git project. The same-environment neutral control used no Case A packet, workbook, source rule, product prompt, browser, search, or private data and stopped at:

```text
Do you trust the contents of this directory?
1. Yes, continue
2. No, quit
```

NTM could not answer the prompt non-interactively, recorded `AGENT_ERROR`, and the declared output root remained empty. Stage B product replay was correctly not run.

The observed Packet 010 failure is therefore attributed to the launcher trust/working-directory boundary for the tested environment. It is not evidence that the product packet, source-custody logic, collector, or model service failed.

### Evidence retained

- Packet 010's tested deterministic source-custody controls remain bounded branch evidence.
- Packet 008's authority, idempotency, recovery, candidate-review, restart, rollback, correction, and prior live-path results remain bounded historical evidence.
- Packet 010 and Packet 011 contained the failure safely: zero proposals, decisions, candidates, or receipts acquired authority.
- Product direction and the joined professional interaction remain reversible falsifiable V0 contracts; they are not analyst validated or frozen.

### Claims retracted or blocked

- A tracked send does not prove Codex consumed an instruction.
- Packet 010 `AGENT_ERROR` is not licensed as evidence of a Case A prompt or source-custody defect.
- No exact safe head has completed the joined analyst journey.
- No end-to-end analyst product, integrated candidate, verified V0, native Excel support, analyst validation, professional reliance, harness improvement, deployment, or client readiness exists.

## Does an end-to-end user product exist?

No.

The execution/evidence kernel and most Case A mechanisms are built and strongly tested on candidate branches. Packet 008 completed a live synthetic chain but retained unsafe source custody. Packet 010 closes the tested source-custody defect but did not reach product instruction execution because of the trust gate. No single exact safe branch has completed:

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

The analyst-facing form, native Excel path, cold analyst evidence, and correction-to-evaluation loop remain incomplete.

## Active Packet 012 boundary

Packet 012 may change only:

- `prototypes/equities-research-cognition/product/campaign/services.py`;
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`; and
- new `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`.

It may add an invocation-scoped Codex trust override only for the exact canonical output root used by `--cd`, derived from the already validated current work-order output path.

It must preserve:

- `--sandbox workspace-write`;
- `--ask-for-approval never`;
- no search for `model_change_v0`;
- pinned Codex binary and model;
- the NTM process allowlist;
- read-only materialised inputs;
- output isolation; and
- existing runtime identity and authentication.

It may not trust `/tmp`, `CAMPAIGN_ROOT`, the campaign root, home, repository parent, a wildcard, or another work order's root. It may not write persistent Codex trust/configuration, require a human click, use `danger-full-access`, add writable directories, modify NTM, change prompts/models/settings/timeouts, touch source custody or UI, run Case A, advance Packet 009, or perform Excel work.

## Packet 012 completion object

Deterministic tests must first prove exact-path trust, safe quoting, per-work-order launcher identity, rejection of invalid roots, unchanged sandbox/no-search behaviour, unchanged non-model-change launchers, and no persistent config mutation.

Then one neutral same-environment control may:

```text
create fresh standalone 0700 output root
-> create one 0400 random-token input
-> launch Codex with exact process-local trust for that root
-> consume one tiny neutral instruction
-> write one fixed-schema result.json and no extras
-> stop NTM
-> prove persistent Codex config did not change
-> clean up or record bounded retention
```

The control contains no Case A packet, workbook, source, product prompt, browser, search, or private data.

A successful control proves only that the tested launcher can operate non-interactively in one exact standalone host-created output root while preserving the current sandbox and network policy. It does not authorise or prove Case A. A separate current-head product replay must be compiled and independently verified later.

## Causal sequencing after Packet 012

- If exact trust cannot be expressed process-locally: stop and report the boundary; do not broaden trust.
- If the trust prompt remains: repair failed; do not replay Case A.
- If trust passes but another control failure appears: diagnose that exact runtime boundary; do not infer product success or defect.
- If the neutral control succeeds: independently audit the receipt, then compile a separate evidence-only exact-current-head Case A replay.
- Only after one safe joined replay and hostile verification: recompile Packet 009 against the final evidence tree.
- Only after deterministic and joined evidence agree: assemble and cold-test the ordinary analyst interaction.
- Only after the human journey works: implement the correction-to-evaluation and promotion/rollback loop.

## Packet state

- Packet 001: closed historical workbook mechanism evidence.
- Packets 002 and 003: stale historical instructions.
- Packet 004: closed hostile architecture evidence.
- Packet 005: rejected implementation evidence.
- Packet 006: suspended; direct Excel may not advance.
- Packet 007: superseded historical classifier work.
- Packet 008: rejected integration candidate; bounded evidence retained.
- Packet 009: suspended; classifier work may not advance.
- Packet 010: accepted only as bounded deterministic source-custody repair evidence; unmerged.
- Packet 011: completed diagnosis evidence; issue `#10` closed.
- Packet 012: active trust-control repair through issue `#11`.

## Four product layers

### Execution and evidence kernel

Substantially implemented and tested on candidate branches, but not integrated. It includes ownership, exact artifacts, work orders, NTM/Codex dispatch, typed proposal/refusal outcomes, source custody and admission, candidate/receipt atomicity, correction/recovery state, restart, and rollback.

### Case A proof vertical

Most deterministic mechanisms and prior live slices exist, but no safe current head has completed the entire proposal-to-candidate path. The trust-control repair is a prerequisite to testing that exact join again.

### Analyst-facing product shell

A narrow synthetic workspace exists. It is not yet an elegant, analyst-validated continuing company environment, has no proven native Excel path, and has not been cold-tested for comprehension or review burden. No new product screen or schema is authorised by Packet 012.

### Learning and evaluation loop

Not implemented. `CorrectionRecord` is only a seed. There is no protected baseline/treatment runner, causal responsible-layer classification, held-out corpus, review-cost comparison, scoped promotion, or executable harness rollback.

## Human-only authority

Protected, client, analyst, or personal data; personal workbooks; permanent credentials; API consent; account administration; material expenditure; analyst/client contact; external release; investment/legal/publication judgment; professional permission to rely; and production-tenant harness promotion remain human-only unless explicitly delegated.

## Evidence ceiling

The repository has a diagnosed trust-boundary blocker, a least-privilege repair contract, and an active neutral-control packet. It does not have a repaired launcher, successful control, successful safe Case A replay, end-to-end product, integrated branch, verified V0, analyst validation, native Excel support, arbitrary source or workbook support, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, client readiness, or programme completion.

This is not a product demo.

## Next action

Packet 012 executes through issue `#11` and returns its exact receipt directly to PRO and coordinating Codex. No routine human decision is required at this gate.
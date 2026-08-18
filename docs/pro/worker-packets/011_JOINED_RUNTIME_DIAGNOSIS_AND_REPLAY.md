# Worker Packet 011 — Joined Runtime Diagnosis and Exact Replay

Status: **authorised evidence-only diagnosis; no product-code authority and no merge authority**.

Programme state: `REPAIRING`.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Product branch under diagnosis: `agent/case-a-source-custody-repair-v2`
- Required product evidence base: `a7df89f22f1783b529d9f31654234ed6de82eb62`
- Product implementation: `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`
- Diagnosis branch: `agent/case-a-joined-runtime-diagnosis-v0`
- Governing contract: `docs/pro/JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md`
- Governing adjudication: `docs/pro/evidence/MILESTONE_2_PACKET_010_ADJUDICATION_RECEIPT.md`
- Failed episode: `d0cc7295-d7ba-4edb-9f3f-2c06f276ae30`
- Failed work orders: `7237d545-455e-442f-8a4d-34ba42f241a8`, `bd56643c-cb26-4a89-82c5-4c20a1638303`

Before execution, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor a7df89f22f1783b529d9f31654234ed6de82eb62 HEAD
git diff --name-status a7df89f22f1783b529d9f31654234ed6de82eb62...HEAD
```

The initial net diff may contain only this packet and `JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md`. Stop with `MOVED_DIAGNOSIS_BASE` on any product, migration, prompt, runtime, setting, fixture, test, template, or receipt drift.

## Assignment

Determine whether the two Packet 010 `AGENT_ERROR` attempts were caused by the external Codex/NTM runtime or by the product's exact work-order, materialisation, launch, permissions, output, or collection path. Do not patch either side. Capture enough primary evidence that PRO can compile one exact repair or accept one exact replay.

This packet is not permission to keep retrying until a run happens to pass.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read:

1. `PRO_RESPONSIBILITY_PROMPT.md`
2. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
3. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md`
4. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER_AMENDMENT_001.md`
5. `docs/pro/PRODUCT_SYSTEM_ARCHITECTURE_V0.md`
6. `docs/pro/PROFESSIONAL_INTERACTION_AND_STATE_CONTRACT_V0.md`
7. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
8. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
9. `docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md`
10. `docs/pro/evidence/CASE_A_SOURCE_CUSTODY_REPAIR_RECEIPT.md`
11. `docs/pro/evidence/MILESTONE_2_PACKET_010_ADJUDICATION_RECEIPT.md`
12. `docs/pro/JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md`
13. current runtime adapter, work compiler, dispatch, collection, model-change service, settings, and exact Packet 010 code without editing them
14. this packet

The worker receipt is evidence. The independent adjudication and current code govern the claim ceiling.

## Phase 1 — retained failure evidence

Inspect the two failed attempts before creating any new runtime state. Record all retained observations required by the contract, including:

- NTM/Codex/model/runtime identity;
- session, pane, process, command, and terminal state;
- stdout, stderr, logs, exit or signal evidence;
- launch, readiness, send, polling, error, collection, and stop timestamps;
- work-order, packet, protocol, closure, input, and output identities;
- output-root contents and permissions;
- partial files and digests;
- canonical runtime events and outcomes; and
- confirmation of zero proposal and candidate authority.

Use `NOT_RETAINED` for missing evidence. Do not infer an exit cause from `AGENT_ERROR` alone.

Compare only the declared runtime dimensions against the prior successful Packet 008 episode. Produce a changed-variable table.

## Phase 2 — same-environment control

Create one disposable local UTF-8 input containing an exact random token generated for the run. Through the same NTM/Codex runtime identity, CLI, model, command boundary, working-directory class, network policy, and output permissions, instruct the agent to write exactly one JSON file containing that token.

No product code, repository source, search, browser, private data, external source, or existing work order may be used.

Record:

- token and input digest;
- exact command and runtime versions;
- session/pane/process identities;
- logs and terminal state;
- output bytes, schema, and digest; and
- cleanup of disposable state.

If the control fails, return `EXTERNAL_RUNTIME_BLOCKER`. Do not run another product attempt.

## Phase 3 — exact current product replay

Run only after the control succeeds.

Create a fresh disposable PostgreSQL database, migrate through 0008, seed one entirely new Case A population, and execute the ordinary authenticated product path on the exact implementation head. Do not reuse a prior job, campaign, episode, artifact, source, work order, output root, session, proposal, candidate, receipt, disposition, or correction.

Capture every identity required by the governing contract, including the identities omitted from the Packet 010 receipt:

- starting artifact;
- both source artifacts, roles, campaigns, and digests;
- both source documents and assertions;
- manifest and conceptual object;
- meaning and method authorities;
- work order, packet digest, input paths/digests, and closure;
- NTM session/pane/process and runtime versions;
- sealed worker output files and digests;
- proposal and V2 admission decision;
- wrong-source block;
- amendment, replacement, pass, candidate, calculation receipt;
- disposition;
- restart projection; and
- correction record.

A tracked send, a healthy pane, partial output, or host retry state is not success.

## Allowed outputs

You may commit only:

`docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`

All raw logs, disposable databases, output roots, and control files remain local evidence referenced by digest; do not commit secrets, credentials, personal paths, private traces, or large runtime logs.

No code, migration, prompt, setting, test, fixture, route, template, packet, contract, checkpoint, ledger, PR, or issue file is owned.

## Required return receipt

The receipt must include:

1. exact base, branch, diagnosis commit, and evidence head;
2. exact changed-file audit;
3. environment versions, runtime identity mode, and command shapes;
4. retained evidence for both Packet 010 failures;
5. Packet 008 comparison table;
6. control experiment inputs, outputs, logs, terminal state, and cleanup;
7. product replay identities and canonical results when Stage B ran;
8. explicit classification of external runtime versus product integration;
9. missing observations marked `NOT_RETAINED`;
10. restart and unchanged-original evidence;
11. failures and nonclaims; and
12. exactly one verdict:
   - `EXTERNAL_RUNTIME_BLOCKER`
   - `PRODUCT_RUNTIME_DEFECT_IDENTIFIED`
   - `JOINED_REPLAY_PASS_FOR_INDEPENDENT_VERIFICATION`
   - `INCONCLUSIVE`

## Prohibited interpretations and actions

Do not:

- modify product or runtime code;
- change prompts, model, reasoning level, tools, network policy, timeouts, poll limits, settings, or packet schema;
- use a different runtime identity without first returning `EXTERNAL_RUNTIME_BLOCKER` or `INCONCLUSIVE`;
- retry the product after the control fails;
- discard or overwrite the two prior outcomes;
- treat successful send as successful execution;
- expose credentials, private chain-of-thought, personal paths, or protected data;
- advance Packet 009 or direct Excel;
- merge, deploy, update governance, or claim verified V0; or
- ask the user to relay evidence.

## Stop conditions

Return immediately on:

- moved base or unexpected initial diff;
- unavailable lawful runtime identity;
- missing access requiring account administration or permanent credentials;
- need for any code or configuration change;
- contradiction between canonical state and supplied attempt identities;
- control failure; or
- protected-data or irreversible-action requirement.

## Claim ceiling

A successful return may classify the runtime boundary and may provide one fresh joined synthetic replay for independent verification. It cannot establish reliability, integration, verified V0, analyst usefulness, Excel support, source entitlement, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, or client readiness.

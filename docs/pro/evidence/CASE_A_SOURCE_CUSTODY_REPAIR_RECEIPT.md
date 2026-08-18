# Case A Source-Custody Repair V2 Receipt

Status: **bounded repair returned; not merged, integrated, or accepted**.

Verdict: `PARTIAL`.

The deterministic source-custody repair is complete and ready for independent
verification. The packet's required fresh joined success is not complete: two
fresh real Codex attempts failed inside the agent runtime before producing a
proposal. Both failures were contained, persisted, restart-visible, and left
zero proposal, decision, candidate, or calculation receipt.

## 1. Basis and commits

- Branch: `agent/case-a-source-custody-repair-v2`.
- Exact packet start: `705dbb57135d3b92aa9fb5331b78b9403fcdb216`.
- Rejected Packet 008 evidence ancestor:
  `b024680c0261b23c58b69729a811e0f584fda5f6`.
- Implementation commit:
  `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`.
- Governing contract:
  `docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md`.
- Worker packet:
  `docs/pro/worker-packets/010_CASE_A_SOURCE_CUSTODY_REPAIR_V2.md`.

The implementation delta is exactly the two owned product files, additive
migration 0008, one owned migration test file, and one new focused custody test
file. No prompt, runtime, adapter, workbook fixture, UI, classifier, Packet
009, direct-Excel, checkpoint, or ledger surface changed.

## 2. Counterexample basis

The coordinator and independent verifier reproduced the original Packet 008
cross-owner attack before this packet was dispatched:

```text
victim episode owner=2
foreign source campaign owner=3
foreign source role=source
ordinary filed-report repair=created
replacement decision=PASS / PASS_EXACT_CLOSURE
candidate committed=true
calculation receipt committed=true
```

That disposable database was removed after reproduction. The current writer
did not preserve a second pre-edit identity receipt for the same-owner,
different-campaign variant before editing. This is an evidence limitation, not
a claimed reproduction. The repaired code has direct-SQL post-edit hostile
tests for both variants, and an independent verifier must replay both against
the exact implementation head.

## 3. Repair installed

Migration `campaign.0008_model_change_v0_source_custody`:

- refuses upgrade when existing source documents or assertions have missing,
  wrong-role, cross-campaign, or cross-owner custody;
- preserves legal 0007 source rows byte-for-byte and identity-for-identity;
- installs `campaign_model_change_source_custody_v2(document_id)`;
- guards direct source-document and source-assertion inserts;
- installs `campaign_model_change_expected_admission_v2(proposal_id)` while
  retaining V1 history;
- makes new decision, candidate, calculation-receipt, and outcome admission
  consume V2 authority;
- independently joins source artifact role, campaign, episode, job owner, and
  campaign director at candidate insertion; and
- allows safe reverse only before V2 decision authority exists, otherwise
  refuses destructive reverse for forward repair.

The application layer calls V2 admission and verifies the complete source
chain before any amendment, replacement proposal, adapter work, pass,
candidate, or receipt. ORM validation repeats the custody rule as defence in
depth; it is not treated as the authority boundary.

## 4. Hostile and regression evidence

All commands ran from `prototypes/equities-research-cognition` against
PostgreSQL.

Results:

- source-custody plus migration suites: **20/20 passed**;
- complete bounded model-change floor (models, services, runtime, UI,
  migrations, Packet 008 repair, and source custody): **58/58 passed**;
- adjacent owned-job and workbook-capability floor: **19/19 passed**;
- Django warning-strict system check: pass with zero warnings;
- migration drift check: none;
- migration plan: includes `campaign.0008_model_change_v0_source_custody`;
- package boundary check: pass;
- `git diff --check`: pass; and
- complete adversarial discovery: **176 found, 171 ran**. The sole setup error
  remains Packet 009's known classifier dependency, first failing on
  `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`; five architecture-budget
  methods therefore do not execute.

The new direct-SQL coverage rejects cross-owner sources, same-owner sources
from a different campaign, same-campaign non-source artifacts, assertions over
an invalid pre-existing document chain, a forged V2 pass, and candidate
insertion over that forged pass. Each path leaves zero downstream repair
authority. Legal same-campaign document/assertion capture, annual 8-K block,
annual 10-K pass/candidate, migration preservation, safe reverse, and populated
reverse refusal pass.

The Packet 008 floor still covers sequential and concurrent repair
convergence, calculation failure and retry, runtime failure, worker refusal,
candidate review evidence, restart, feature-flag rollback, and correction
custody.

## 5. Fresh real NTM/Codex evidence

A new disposable database was migrated from zero through 0008. The fresh
episode used only newly seeded canonical rows:

- database: `flywheel_packet010_live2_20260818_0950`;
- owner: `1`;
- job: `e2a94017-d072-4115-8dbd-9246f32df432`;
- episode: `d0cc7295-d7ba-4edb-9f3f-2c06f276ae30`;
- campaign: `f063b48c-49d2-491d-bdeb-edf7bfd2593f`;
- campaign director: `1`;
- NTM session: `flywheel-f063b48c49d2491dbdeb`;
- first work order: `7237d545-455e-442f-8a4d-34ba42f241a8`;
- successor work order: `bd56643c-cb26-4a89-82c5-4c20a1638303`.

Both tracked sends succeeded, but each Codex pane entered NTM `AGENT_ERROR`
before writing the required sealed proposal artifacts. The host recorded:

| Attempt | Outcome | Next action |
| --- | --- | --- |
| `7237d545-455e-442f-8a4d-34ba42f241a8` | `RUNTIME_FAILURE / RUNTIME_IN_PROGRESS` (`75ff5765-7497-4709-8e62-4be8e9a8d749`) | `RETRY_WORK` |
| `bd56643c-cb26-4a89-82c5-4c20a1638303` | `RUNTIME_FAILURE / RUNTIME_IN_PROGRESS` (`73f4d074-76b7-429b-b5bb-abe5098fa885`) | `RETRY_WORK` |

After both attempts:

```text
proposals=0
admissibility decisions=0
candidates=0
original workbook changed=false
NTM stop recorded=true
```

A fresh-process authenticated restart returned HTTP 200 and displayed both the
unchanged-workbook state and the legal retry action. With the feature flag off,
the route returned 404 while preserving both outcomes in PostgreSQL.

This proves failure containment and restart recovery for this run. It does not
prove the packet's required fresh joined success, canonical V2 block, repair,
candidate, receipt, disposition, or correction seed.

## 6. Independent-verification request

An independent verifier must:

1. replay the original cross-owner and same-owner/different-campaign attacks on
   a new PostgreSQL database;
2. verify legal same-campaign annual and preliminary controls;
3. verify migration preservation, refusal, and reverse behaviour;
4. rerun the complete Packet 008 regression floor; and
5. classify the two live worker failures as an environmental/runtime blocker or
   find a reproducible product defect.

The implementation may be accepted only as a bounded deterministic repair
unless a fresh joined episode completes. It does not establish integration,
verified V0, analyst usefulness, source entitlement, Excel compatibility,
professional correctness, permission to rely, harness improvement,
deployment, security review, production readiness, or client readiness.

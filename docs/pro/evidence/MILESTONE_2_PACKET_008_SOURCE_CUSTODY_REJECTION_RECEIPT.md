# Milestone 2 Packet 008 Source-Custody Rejection Receipt

Verdict: `REJECT_PENDING_BOUNDED_SOURCE_CUSTODY_REPAIR`.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Prior governing PRO head: `6be6f6a181444a4600fa5bddc120fed845794f9e`
- Packet 008 branch: `agent/case-a-authority-recovery-repair-v1`
- Packet 008 implementation commit: `e668d01bdc7706299f66ee845ae62c956046567a`
- Packet 008 evidence head: `b024680c0261b23c58b69729a811e0f584fda5f6`
- Packet 008 receipt: `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`
- Coordinator projection: `dec-2026-08-18-039`
- Governing repair contract: `docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md`
- Audit packet: `docs/pro/worker-packets/010_CASE_A_SOURCE_CUSTODY_REPAIR_V2.md`
- Proposed worker branch: `agent/case-a-source-custody-repair-v2`
- Exact audit head: `705dbb57135d3b92aa9fb5331b78b9403fcdb216`

Packet 008 is not merged or integrated. Packet 009 and direct Excel are suspended. Packet 010 is compiled for coordinator audit and has not been dispatched.

## Independent finding adopted

Fresh verification created a victim episode B with its legitimate annual-target 8-K block, then created a foreign owner and campaign C with a `SOURCE` artifact. Direct SQL inserted a digest-consistent `SourceDocumentVersion` attributed to B but backed by C’s artifact, then inserted a 10-K assertion over that document.

The victim’s ordinary `RepairService.create_candidate_using_filed_report()` accepted the assertion. It created a repair, host-derived replacement proposal, canonical `PASS`, candidate artifact, and `CalculationReceipt`.

The source artifact campaign and owner were foreign to the victim episode. Foreign exact bytes therefore acquired candidate authority.

## Code-backed cause

- `SourceDocumentVersion.clean()` checks artifact campaign against episode campaign, but direct SQL does not invoke Django validation.
- The 0007 canonical function joins `SourceDocumentVersion` and checks its episode and document class, but not the document’s underlying artifact campaign, artifact role, campaign director, or continuing-job owner.
- The 0007 candidate trigger repeats the document-episode check without checking the source artifact campaign or owner.
- RepairService checks only the assertion document episode and 10-K class before creating the repair chain.

The finding is accepted as a P0 machine-fact custody defect. It is not a prompt defect, source-prestige issue, or user-interface problem.

## Evidence retained narrowly

Packet 008’s exact 13-file change scope, 44 of 44 focused tests, 19 of 19 adjacent tests, real joined NTM/Codex episode, retry/refusal/calculation recovery, candidate-review evidence, restart, rollback, and correction seed remain bounded mechanism evidence.

They do not authorise integration because the exact source bytes can cross owner and campaign custody.

## Bounded repair authority proposed for audit

Packet 010 proposes one additive migration and narrow code/test ownership:

- `campaign.0008_model_change_v0_source_custody`;
- source-document and source-assertion direct-SQL custody guards;
- canonical admission V2 with validator `model-change-admissibility/v2`;
- candidate-level source-artifact campaign/owner revalidation;
- RepairService defence in depth;
- migration refusal for pre-existing foreign, cross-campaign, or wrong-role source rows;
- raw-SQL hostile tests and legal same-campaign controls; and
- one fresh joined episode preserving every Packet 008 repair.

No migration 0005–0007 rewrite, prompt, runtime, UI, workbook, classifier, direct-Excel, deployment, or entitlement work is authorised.

## Packet state

- Packet 005: rejected historical implementation evidence.
- Packet 006: suspended; direct Excel may not advance.
- Packet 007: superseded historical classifier packet.
- Packet 008: rejected integration candidate; bounded evidence retained.
- Packet 009: suspended pending source-custody repair and later reconciliation.
- Packet 010: compiled for coordinator audit; not dispatched.

No active worker is authorised by this receipt.

## Migration boundary

The only proposed migration is `0008_model_change_v0_source_custody`, additive after 0007. It must refuse pre-existing inconsistent source chains rather than rewrite or quarantine them, preserve legal Packet 008 rows, use V2 admission for new authority, and refuse destructive reverse when V2 authority exists.

## Next gate

The coordinator audits:

- branch ancestry and exact two-file initial diff;
- contract and packet blob parity with PRO;
- owned and prohibited files;
- migration and rollback law;
- direct-database hostile cases and legal controls; and
- the claim ceiling.

Only a later explicit dispatch action may activate Packet 010. After any worker return, fresh independent verification remains mandatory before integration.

## Evidence ceiling

This receipt establishes that Packet 008 is rejected for a reproduced cross-owner/cross-campaign source-byte custody bypass and that a narrow, current-head repair contract and audit branch exist.

It does not establish a repair, classifier success, verified V0, analyst usefulness, source entitlement, Excel support, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, or client readiness.
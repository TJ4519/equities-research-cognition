# Case A Source-Custody Repair Contract V2

Packet 008 is rejected as an integration candidate because exact source bytes can be placed under another owner’s campaign and then attributed to the victim episode through direct database insertion. The Packet 008 authority, retry, refusal, calculation, review, restart, and rollback repairs remain bounded evidence and must be preserved.

Status: governing bounded repair contract; **not dispatched**.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## 1. Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Governing PRO basis before this adjudication: `agent/pro-grounding` at `6be6f6a181444a4600fa5bddc120fed845794f9e`
- Packet 008 branch: `agent/case-a-authority-recovery-repair-v1`
- Packet 008 implementation commit: `e668d01bdc7706299f66ee845ae62c956046567a`
- Packet 008 evidence head: `b024680c0261b23c58b69729a811e0f584fda5f6`
- Packet 008 receipt: `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`
- Coordinator projection: `dec-2026-08-18-039`
- Adjudication: `REJECT_PENDING_BOUNDED_SOURCE_CUSTODY_REPAIR`

Packet 008 is not merged, deployed, promoted, or called verified V0. Packet 009 and direct Excel remain suspended.

## 2. Finding adopted

### P0 — cross-owner source-custody bypass

A direct database writer can create:

1. a legitimate victim episode and annual-target 8-K block;
2. a different owner and campaign;
3. a `SOURCE` `ArtifactVersion` owned by that foreign campaign;
4. a digest-consistent `SourceDocumentVersion` whose `episode_id` names the victim episode but whose `artifact_id` names the foreign artifact; and
5. a 10-K `SourceAssertion` over that document.

The ordinary victim repair then creates a host-derived replacement proposal, canonical `PASS`, candidate workbook, and `CalculationReceipt`.

The row is structurally linked but its bytes do not belong to the victim campaign or owner. This lets foreign evidence acquire candidate authority.

### Why Packet 008 did not contain it

`SourceDocumentVersion.clean()` checks that the artifact campaign equals the episode campaign, but direct SQL does not invoke Django model validation.

Migration `0007_model_change_v0_repair_1` joins the source assertion and document into canonical admission, but verifies only `document_version.episode_id` and `document_class`. It does not join the document’s underlying `ArtifactVersion`, require `artifact.role = SOURCE`, require `artifact.campaign_id = episode.campaign_id`, or prove that the campaign director equals the continuing job owner.

The replacement candidate trigger repeats the document-episode check without checking the source artifact campaign or owner. `RepairService.create_candidate_using_filed_report()` and `_repair_wrong_source()` likewise require the same episode and 10-K class but not the document-artifact-campaign-owner chain.

The ORM rule is therefore advisory while the claimed machine-fact boundary is incomplete.

## 3. Evidence retained narrowly

The following Packet 008 evidence remains useful and must not be reimplemented gratuitously:

- exact 13-file Packet 008 ownership;
- 44 of 44 focused tests and 19 of 19 adjacent tests in the reported environment;
- PostgreSQL-recomputed target-specific admission for the tested same-campaign population;
- forged stored `PASS` and orphan-candidate rejection for that population;
- single-use and idempotent filed-report repair;
- recoverable runtime failure, worker refusal, and calculation failure;
- complete candidate-review evidence;
- one fresh real NTM/Codex joined episode with search closed;
- restart and feature-flag rollback; and
- correction-record custody without harness promotion.

These observations justify one narrow repair. They do not license integration because the source chain can cross owner and campaign custody.

## 4. Repair completion object

The next repair succeeds only when this chain is enforced independently at every authority boundary:

```text
SourceDocumentVersion
-> exact source ArtifactVersion
-> artifact role SOURCE
-> artifact campaign equals episode campaign
-> episode campaign director equals ResearchJob owner
-> SourceAssertion inherits the same custody
-> canonical admission rechecks the full chain
-> candidate creation rechecks the full chain
-> RepairService refuses any inconsistent chain before amendment or calculation
```

One fresh legal same-campaign Case A episode must still complete through block, filed-report repair, recalculated candidate, synthetic disposition, restart, and correction seed.

A green ORM test, a repaired service check, or an insert trigger alone is insufficient.

## 5. Database custody law

### 5.1 Canonical source-custody function

Migration `0008_model_change_v0_source_custody.py` must add one deterministic PostgreSQL function, conceptually:

```text
campaign_model_change_source_custody_v2(source_document_id)
  -> valid, reason_code, episode_id, campaign_id, owner_id, artifact_id
```

The function must derive all values from canonical rows and require:

- the source document exists;
- its episode exists;
- the episode’s continuing `ResearchJob` exists;
- the episode campaign exists;
- the source artifact exists;
- the source artifact role is exactly `source`;
- `source_artifact.campaign_id = source_document.episode.campaign_id`;
- `episode.campaign.director_id = episode.job.owner_id`;
- the source artifact campaign director is that same owner; and
- no relation is inferred from a supplied digest, document class, or numerical equality.

The exact owner and campaign chain is a host fact. A model-authored identity, digest-consistent row, or foreign official filing cannot substitute for it.

### 5.2 Source-document insertion guard

A `BEFORE INSERT` trigger on `campaign_sourcedocumentversion` must call the custody function or an equally exact implementation and reject:

- foreign-owner source artifacts;
- same-owner but different-campaign source artifacts;
- non-`SOURCE` artifacts;
- missing episode, job, campaign, artifact, or director links; and
- any source document whose artifact campaign is not the episode campaign.

The guard must run for direct SQL and ORM inserts.

### 5.3 Source-assertion insertion guard

A `BEFORE INSERT` trigger on `campaign_sourceassertion` must re-evaluate the referenced document’s custody and reject an assertion over an invalid source chain.

This is deliberate defence in depth. A document row existing in the table is not sufficient authority for a new assertion.

### 5.4 Canonical admission V2

Add `campaign_model_change_expected_admission_v2(proposal_id)` or an equivalent versioned successor. It must preserve every Packet 008 target-specific rule while adding the full source-custody check.

The expected validator version for new decisions is exactly:

`model-change-admissibility/v2`

When the source chain is inconsistent, the result must be non-pass with a stable reason such as `BLOCK_SOURCE_CUSTODY`. The function must not fall through to document-class admission.

New decision, candidate, calculation-receipt, and calculation-outcome guards that depend on canonical admission must use the V2 result. Existing V1 rows remain historical and readable.

### 5.5 Candidate creation guard

The candidate insert guard must independently join:

- proposal;
- source assertion;
- source document;
- source artifact;
- proposal episode and campaign;
- continuing job and owner; and
- candidate parent and campaign.

It must require the source artifact campaign to equal the episode and candidate campaign, the artifact role to be `source`, and the campaign director to equal the job owner. It must then require the exact V2 canonical `PASS`.

A candidate must fail even when an attacker has inserted a digest-consistent document, assertion, proposal, or decision population.

### 5.6 Service-layer defence

`RepairService.create_candidate_using_filed_report()` must validate the complete assertion-document-artifact-episode-campaign-owner chain before creating an amendment, replacement proposal, decision, adapter operation, candidate, or failure outcome.

`InvalidationService._repair_wrong_source()` must either call the same bounded helper or independently reject the inconsistent chain. The service may not rely on model `clean()` having run.

The application error must remain bounded and ordinary; no foreign source identity or owner details may be disclosed to the victim.

## 6. Migration law

The only authorised migration is:

`campaign.0008_model_change_v0_source_custody`

It is additive over `campaign.0007_model_change_v0_repair_1`.

Migrations 0005, 0006, and 0007 are immutable evidence and may not be edited, regenerated, squashed, or replaced.

Before installing new guards, 0008 must scan every existing source document and assertion. It must refuse the migration if any row has:

- a source artifact outside the document episode’s campaign;
- a source artifact whose role is not `source`;
- an episode campaign director different from the continuing job owner;
- a missing or inconsistent document-artifact-episode-campaign-owner relation; or
- an assertion whose document fails that custody test.

The migration must fail with a stable message naming the class of defect without silently rewriting, reassigning, deleting, or quarantining evidence.

Required migration evidence:

1. clean database from zero through 0008;
2. upgrade from 0004 with legacy rows preserved;
3. upgrade from 0007 with valid same-campaign Packet 008 rows preserved byte-for-byte;
4. upgrade from 0007 refuses a pre-existing cross-owner row;
5. upgrade from 0007 refuses a same-owner/different-campaign row;
6. upgrade refuses a non-source artifact attributed as a source document;
7. new direct-SQL source-document and assertion guards are append-only compatible; and
8. reverse to 0007 is allowed only when no V2 decision or other V2 authority exists; populated V2 state refuses destructive reverse and remains forward-fixed.

## 7. Required hostile tests

### Direct database insertion

Use raw PostgreSQL SQL, not only ORM helpers, to prove rejection of:

- victim episode plus foreign-owner/campaign `SOURCE` artifact;
- victim episode plus same-owner/different-campaign `SOURCE` artifact;
- victim episode plus same-campaign non-source artifact;
- source assertion over an invalid document chain;
- V2 decision over a cross-campaign assertion;
- candidate over a cross-campaign source chain, including a forged stored `PASS`; and
- candidate/receipt creation after any source-custody failure.

For each attack, assert zero amendment, replacement proposal, new decision, candidate, calculation receipt, disposition, and correction record.

### Legal controls

Prove that:

- a same-campaign source artifact, document, and assertion insert succeeds;
- the annual 8-K remains `BLOCK_WRONG_DOCUMENT_CLASS`;
- the same-campaign annual 10-K passes and produces one candidate and receipt;
- the preliminary earnings-flash target still permits the same-campaign 8-K;
- Packet 008 idempotent and concurrent repair tests remain green; and
- runtime/refusal/calculation recovery, UI evidence, restart, rollback, and correction seed remain green.

### Migration hostile population

At migration state 0007, insert each invalid source population by direct SQL and prove 0008 refuses before installing partial authority. Re-run with a legal same-campaign population and prove exact preservation.

### Fresh joined episode

After the deterministic floor passes, run one fresh real NTM/Codex Case A episode. Record exact source artifact campaign, episode campaign, job owner, campaign director, document, assertion, proposal, decision, candidate, receipt, restart, and correction identities. No prior canonical row or worker output may be reused.

## 8. Required command floor

Run from `prototypes/equities-research-cognition`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py showmigrations --plan
uv run python -W error manage.py test \
  scenarios.adversarial.test_model_change_v0_models \
  scenarios.adversarial.test_model_change_v0_services \
  scenarios.adversarial.test_model_change_v0_runtime \
  scenarios.adversarial.test_model_change_v0_ui \
  scenarios.adversarial.test_model_change_v0_migrations \
  scenarios.adversarial.test_model_change_v0_repair_1 \
  scenarios.adversarial.test_model_change_v0_source_custody -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_owned_job_bound_execution \
  scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check
```

Packet 009 remains suspended, so the full-suite classifier result may remain the already-known dependency. Record the exact first failure and fresh discovered/executed counts; do not modify or waive it.

## 9. Integration and verification gate

The repair worker may return only:

- `PASS_FOR_INDEPENDENT_VERIFICATION`;
- `PARTIAL`; or
- `FAIL`.

A return does not merge itself or move programme state. PRO and coordinating Codex must inspect exact ancestry, file ownership, migration behaviour, raw-SQL attacks, legal controls, full regression results, fresh joined evidence, restart, rollback, and receipt accuracy.

A fresh independent verifier must reproduce the original cross-owner attack, same-owner/different-campaign attack, legal same-campaign controls, and the full Packet 008 regression floor before integration.

## 10. Kill and escalation conditions

Stop with `MOVED_REPAIR_BASE` if the branch is not an exact descendant of the Packet 008 evidence head or if product code changed before worker edits.

Stop with `OWNERSHIP_BOUNDARY_REACHED` if closure requires source entitlement, external account changes, a new source-acquisition architecture, rewriting migrations 0005–0007, changing the NTM protocol, modifying the workbook profile, or touching Packet 009.

Stop with `COUNTEREXAMPLE_DIVERGED` if the exact coordinator attack cannot be reproduced on the unchanged Packet 008 evidence head.

This is the second failed repair at the same broad Milestone 2–6 gate but the causal diagnosis is new: Packet 008 repaired candidate authority and recovery; this finding concerns source-byte custody beneath those mechanisms. If the same source-custody diagnosis survives this repair, reopen the governing source representation and strongest rival rather than issuing a third local trigger patch.

## 11. Claim ceiling

A successful repair may establish only that, for the public synthetic Case A profile under the tested PostgreSQL and runtime environment:

- source documents and assertions cannot cross campaign or owner custody through the tested database and service paths;
- canonical admission and candidate creation recheck the source-byte chain;
- the Packet 008 authority and recovery behaviours still work; and
- one fresh legal joined episode completes and restarts.

It does not establish integration acceptance, verified V0, analyst usefulness, source entitlement, arbitrary source or workbook support, Excel compatibility, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, or client readiness.
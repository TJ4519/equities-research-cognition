# Worker Packet 010 — Case A Source-Custody Repair V2

Status: **compiled for coordinator audit; not dispatched and not authorised for merge**.

Programme state: `REPAIRING`.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Rejected Packet 008 branch: `agent/case-a-authority-recovery-repair-v1`
- Packet 008 implementation commit: `e668d01bdc7706299f66ee845ae62c956046567a`
- Packet 008 evidence head and authoritative code basis: `b024680c0261b23c58b69729a811e0f584fda5f6`
- Proposed repair branch: `agent/case-a-source-custody-repair-v2`
- Governing contract: `docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md`
- Coordinator projection: `dec-2026-08-18-039`
- Exact required migration: `campaign.0008_model_change_v0_source_custody`

The proposed branch must descend from the exact evidence head and differ from it initially only by this packet and the governing source-custody repair contract. The current checkpoint records the audited packet head after branch construction.

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor b024680c0261b23c58b69729a811e0f584fda5f6 HEAD
git diff --name-status b024680c0261b23c58b69729a811e0f584fda5f6...HEAD
git rev-parse HEAD:docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md
git rev-parse HEAD:docs/pro/worker-packets/010_CASE_A_SOURCE_CUSTODY_REPAIR_V2.md
```

Stop with `MOVED_REPAIR_BASE` if any product code, migration, prompt, fixture, test, runtime, template, receipt, checkpoint, or ledger file changed before worker edits.

## Assignment

You are the sole architectural writer for one narrow repair of Packet 008’s source-byte custody boundary.

Preserve the implemented Packet 008 authority, idempotency, recovery, interface, restart, and rollback behaviours. Add database and service enforcement so a source document and assertion can never acquire authority in an episode unless the underlying exact source artifact belongs to the same episode campaign and owner.

Do not redesign the product, add agents, change the professional interaction grammar, activate Packet 009 or direct Excel, widen source acquisition, or infer that Packet 008 was otherwise verified.

## Completion object

One fresh legal Case A episode must complete this path:

```text
same-owner, same-campaign SOURCE artifact
-> SourceDocumentVersion accepted
-> SourceAssertion accepted
-> real NTM/Codex equal-value 8-K proposal
-> canonical V2 BLOCK_WRONG_DOCUMENT_CLASS
-> one filed-report repair using same-campaign 10-K assertion
-> canonical V2 PASS
-> one candidate plus exact CalculationReceipt
-> synthetic disposition
-> restart
-> CorrectionRecord seed
```

The following attack must fail before any amendment, replacement proposal, `PASS`, candidate, or calculation receipt exists:

```text
victim episode B
+ foreign campaign C SOURCE artifact
+ document attributed to B but backed by C artifact
+ 10-K assertion
+ ordinary filed-report repair
```

A service-only check, model `clean()`, insert trigger alone, or canonical-function check alone is a failure.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read in this order:

1. `PRO_RESPONSIBILITY_PROMPT.md`
2. `docs/pro/PRO_CONSTITUTION.md`
3. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
4. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md`
5. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER_AMENDMENT_001.md`
6. `docs/pro/PRODUCT_SYSTEM_ARCHITECTURE_V0.md`
7. `docs/pro/PROFESSIONAL_INTERACTION_AND_STATE_CONTRACT_V0.md`
8. `docs/pro/CONCEPTUAL_MODEL_CONTRACT_V0.md`
9. `docs/pro/EVALUATION_AND_HARNESS_EVOLUTION_CONTRACT_V0.md`
10. `docs/pro/UI_AND_REPOSITORY_SLOP_AUDIT.md`
11. `docs/pro/evidence/HOSTILE_VERTICAL_REVIEW_RECEIPT.md`
12. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
13. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
14. `docs/pro/evidence/CASE_A_REPAIR_1_RECEIPT.md`
15. `docs/pro/CASE_A_SOURCE_CUSTODY_REPAIR_CONTRACT_V2.md`
16. latest decision ledger continuation and current checkpoint
17. current models, migrations 0005–0007, services, hostile tests, and this packet

The Packet 008 receipt is bounded evidence, not integration authority.

## Reproduce before editing

Use a newly created disposable PostgreSQL database and reproduce the coordinator attack against unchanged evidence head `b024680c...`.

Required preserved facts:

```text
victim owner != foreign owner
source artifact campaign != victim episode campaign
source artifact role = source
source document episode = victim episode
source document artifact = foreign artifact
original annual 8-K decision = BLOCK / BLOCK_WRONG_DOCUMENT_CLASS
ordinary filed-report repair = created
replacement decision = PASS / PASS_EXACT_CLOSURE
candidate committed = true
CalculationReceipt committed = true
```

Also reproduce a same-owner/different-campaign variant.

Record exact IDs, owners, campaigns, artifact roles, document, assertion, proposal, decision, amendment, candidate, and receipt counts in the return receipt. Expose no unrelated personal or protected data.

If the attack does not reproduce, stop with `COUNTEREXAMPLE_DIVERGED`. Do not repair a different problem.

## Product and authority laws

1. Exact bytes inherit authority from machine-owned artifact custody, not from a model-authored or digest-consistent document row.
2. Source artifact, source document, assertion, proposal, episode, campaign, continuing job, and owner must form one exact chain.
3. Django `clean()` is defence in depth, not the database authority boundary.
4. A source document row does not authorise later assertions unless its custody is rechecked.
5. Canonical admission and candidate creation each recheck source custody independently.
6. RepairService checks custody before any attributed repair or adapter work.
7. Existing valid Packet 008 records remain immutable historical evidence.
8. Existing V1 decisions remain readable; new admission uses version V2.
9. No foreign owner or campaign identity may be disclosed through the ordinary product error.
10. The original workbook remains immutable and LibreOfficeDev remains a bounded proxy.

## Stable repair interfaces

Internal names may differ only when the semantics and hostile tests remain exact.

```text
SourceCustody.expected(document_id)
  -> valid, reason_code, episode_id, campaign_id, owner_id, artifact_id

EvidenceService.capture(...)
  -> database-guarded SourceDocumentVersion

EvidenceService.assert_value(...)
  -> database-guarded SourceAssertion

CanonicalAdmission.expected_v2(proposal_id)
  -> validator_version, outcome, reason_code, closure_digest

RepairService.create_candidate_using_filed_report(...)
  -> existing-or-new legal result | bounded source-custody refusal
```

Views and templates are not part of this repair. The ordinary existing message may be reused or narrowed, but no UI file is owned.

## Required database design

### Source-custody function

Migration 0008 must install a canonical function that proves from database rows:

- `SourceDocumentVersion.episode_id` exists;
- `SourceDocumentVersion.artifact_id` exists;
- source artifact role is `source`;
- source artifact campaign equals episode campaign;
- episode job owner equals episode campaign director;
- source artifact campaign director equals that same owner; and
- the exact chain is complete.

### Source-document guard

Install a direct-SQL `BEFORE INSERT` guard on `campaign_sourcedocumentversion` that rejects cross-owner, cross-campaign, wrong-role, missing-link, and inconsistent-owner rows.

### Source-assertion guard

Install a direct-SQL `BEFORE INSERT` guard on `campaign_sourceassertion` that rechecks the referenced document chain.

### Canonical admission V2

Add a versioned successor to the Packet 008 canonical function. New decisions use validator `model-change-admissibility/v2`.

The V2 function must preserve:

- annual 8-K block;
- annual 10-K pass;
- preliminary earnings-flash 8-K pass;
- operation, closure, invalidation, object, manifest, and repair-key rules from V1.

It must return a non-pass source-custody reason before document-class admission when the chain is inconsistent.

### Dependent guards

Replace only the 0007-installed functions or triggers that must consume V2 admission for new rows:

- decision insertion;
- candidate insertion;
- calculation receipt insertion; and
- calculation-failure outcome insertion when it calls canonical admission.

The candidate guard must additionally join and compare source artifact campaign, role, episode campaign, job owner, and campaign director rather than relying only on the V2 function.

### Service defence

Before any amendment or replacement proposal, RepairService must verify:

```text
assertion.document_version.episode_id == blocked episode id
assertion.document_version.artifact.role == SOURCE
assertion.document_version.artifact.campaign_id == blocked episode campaign id
blocked episode campaign director id == blocked episode job owner id
assertion document artifact campaign director id == blocked episode job owner id
```

The lower-level repair helper must not be callable with a weaker rule.

## Exact owned files

The worker may modify only:

- `prototypes/equities-research-cognition/product/campaign/models.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_repair_1.py`

The worker must add exactly:

- `prototypes/equities-research-cognition/product/campaign/migrations/0008_model_change_v0_source_custody.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_source_custody.py`
- `docs/pro/evidence/CASE_A_SOURCE_CUSTODY_REPAIR_RECEIPT.md`

The worker may modify `test_model_change_v0_services.py` only if the service-level custody control cannot be tested cleanly in the new focused file. Explain the necessity in the receipt.

No other path is owned.

## Prohibited changes

Do not modify:

- migrations 0005, 0006, or 0007;
- forms, projections, views, routes, templates, settings, UI language, or disposition choices;
- `agents/model_change_v0.md`, prompts, skills, models, tools, protocols, or workbenches;
- `harness/ntm/adapter.py` or the calculation adapter/profile;
- source or workbook fixtures;
- classifier code or tests;
- Packet 009, direct-Excel work, cloud artifacts, or account state;
- legacy campaign or Casebook surfaces;
- decision ledger, checkpoint, contracts, PR, issues, or worker packets;
- dependencies, deployment, tenancy, security, or entitlement systems; or
- Cases B and C as product journeys.

If a prohibited file appears necessary, stop with `OWNERSHIP_BOUNDARY_REACHED` and name the exact missing interface.

## Migration boundary

Migration `0008_model_change_v0_source_custody.py` must:

1. depend exactly on `0007_model_change_v0_repair_1`;
2. scan existing source documents and assertions before installing authority;
3. refuse any pre-existing foreign-owner, cross-campaign, wrong-role, missing-link, or inconsistent-owner source chain;
4. preserve legal Packet 008 rows exactly;
5. install source-document and source-assertion insertion guards;
6. install canonical admission V2 and update dependent new-row guards;
7. leave V1 historical decisions readable;
8. permit empty/no-V2 reverse to 0007 where safe; and
9. refuse reverse when V2 authority exists, preserving rows for forward repair.

Do not silently reassign, rewrite, delete, quarantine, or bless invalid source rows.

## Mandatory hostile tests

### H1 — original cross-owner attack

Use raw SQL on PostgreSQL to reproduce the exact victim/foreign-owner population. After repair, the source-document insert must fail. Assert zero downstream repair records.

### H2 — same-owner, different campaign

Create two campaigns under one owner. A source artifact from campaign C cannot back a document attributed to episode B.

### H3 — wrong artifact role

A starting artifact, candidate, or other non-source artifact in the correct campaign cannot back a source document.

### H4 — assertion guard

An assertion insert over an invalid or pre-existing corrupt document chain must fail. Use a migration-state or explicitly isolated trigger setup; do not weaken the document guard to make the test convenient.

### H5 — migration refusal

At migration state 0007, insert:

- a foreign-owner cross-campaign document and assertion;
- a same-owner/different-campaign document; and
- a wrong-role document.

Applying 0008 must refuse each population before partial installation. A legal same-campaign population must migrate and preserve exact IDs and digests.

### H6 — canonical admission and candidate defence

Prove canonical V2 admission returns non-pass for an inconsistent source chain and candidate insertion fails even with attacker-authored decision fields. Use a disposable database and the minimum controlled setup required to reach the downstream guards.

### H7 — service defence

Prove the ordinary RepairService refuses an inconsistent assertion before amendment, replacement proposal, decision, candidate, calculation receipt, failure outcome, disposition, or correction record.

### Legal controls

Prove:

- legal same-campaign source-document and assertion inserts;
- annual same-campaign 8-K block;
- annual same-campaign 10-K pass and candidate;
- preliminary same-campaign 8-K pass;
- Packet 008 sequential/concurrent idempotency;
- calculation failure rollback and retry;
- runtime failure and refusal recovery;
- candidate review evidence;
- restart, feature-flag rollback, and correction seed.

## Required live evidence

After deterministic tests pass, run one fresh real joined NTM/Codex episode from new canonical rows. The receipt must record:

- job owner;
- episode and campaign;
- campaign director;
- starting artifact;
- each source artifact campaign and role;
- source document and assertion;
- work order and closure;
- proposal and canonical V2 decision;
- repair, replacement proposal, candidate, and receipt;
- synthetic disposition;
- restart; and
- correction record.

No prior work order, output, candidate, receipt, or canonical row may be reused.

## Required command floor

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

The classifier remains suspended under Packet 009. Record its exact unchanged failure and fresh suite counts; do not modify or waive it.

## Required return receipt

Create:

`docs/pro/evidence/CASE_A_SOURCE_CUSTODY_REPAIR_RECEIPT.md`

The receipt must include:

1. exact base, branch, implementation commit, and evidence head;
2. exact changed files and ownership audit;
3. pre-edit reproduction of cross-owner and same-owner/different-campaign attacks;
4. source-custody SQL functions and triggers;
5. canonical admission V2 and validator version;
6. migration preflight, fresh, upgrade, refusal, reverse, and rollback evidence;
7. direct-SQL hostile test results and legal controls;
8. complete Packet 008 regression results;
9. fresh full-suite discovered and executed counts with classifier nonclaim;
10. fresh real joined episode identities and custody chain;
11. restart and feature-flag rollback;
12. failures, warnings, environment versions, and nonclaims; and
13. verdict `PASS_FOR_INDEPENDENT_VERIFICATION`, `PARTIAL`, or `FAIL`.

Do not merge, update governance, modify issues or PRs, or claim integration.

## Stop conditions

Return `MOVED_REPAIR_BASE` on unexpected initial drift.

Return `COUNTEREXAMPLE_DIVERGED` when the exact attack cannot be reproduced.

Return `OWNERSHIP_BOUNDARY_REACHED` if the repair requires entitlement, source acquisition, permanent credentials, external access, new product interaction, workbook changes, NTM changes, classifier work, or migration-history rewrite.

Return `FAIL` when source custody cannot be enforced without weakening Packet 008’s authority or recovery properties.

## Claim ceiling

A successful worker return may claim only a reviewable synthetic source-custody repair candidate on its branch. It may not claim integration, verified V0, analyst validation, source entitlement, native Excel support, arbitrary sources or workbooks, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, or client readiness.

Fresh independent verification of every attack and legal control is mandatory before any merge or programme-state advancement.
# Worker Packet 005 — Joined Case A Outcome-Complete Implementation

Status: **authorised for dispatch after branch creation and coordinator ancestry audit**.

Programme state: Level 2 bounded vertical orchestration.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Authoritative implementation code basis: `1798427cadad65e286e8e124b261dfb31903fec0`
- Worker branch: `agent/case-a-outcome-complete-v0`
- Governing review result: `99ad9412f059239c0604497b3de868b6c348370a`
- Exact verdict: `ACCEPT_WITH_EXACT_NARROWING`
- Accepted vertical: `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`

The worker branch will be created from a packet-bundle commit that descends from the implementation code basis and differs from it only by governing, checkpoint, ledger, evidence, packet, and dispatch metadata. Before editing, verify:

```text
git merge-base --is-ancestor 1798427cadad65e286e8e124b261dfb31903fec0 HEAD
git diff --name-only 1798427cadad65e286e8e124b261dfb31903fec0...HEAD
```

If any product code, migration, prompt, test, fixture, runtime, or template changed between that basis and the initial worker head, stop and return `MOVED_IMPLEMENTATION_BASE` with the exact diff. Packet files and dispatch metadata are not product-code drift.

## Professional outcome

Deliver one runnable synthetic Micron Case A episode in which an authenticated owner can:

```text
resume one continuing ResearchJob and immutable campaign-backed episode
-> see the exact starting workbook and one bounded FY2025 revenue object
-> confirm or correct the object meaning
-> separately authorise the reported-value method and source rule
-> run one real NTM/Codex work unit over exact captured 8-K and 10-K sources with search closed
-> receive the controlled equal-value 8-K proposal
-> have the host return BLOCK_WRONG_DOCUMENT_CLASS before any candidate exists
-> choose “Create a candidate using the filed annual report”
-> create an attributed replacement proposal bound to the captured 10-K
-> require deterministic PASS before creating a child workbook
-> patch and calculate the exact child through the bounded proxy profile
-> review source, target delta, two declared consequences, engine identity, warnings and formula-error status
-> record SIMULATE_NAMED_USE, REJECT or REWORK
-> restart and recover the same canonical state and immutable history
-> emit one exact CorrectionRecord seed without harness promotion
```

The packet fails if it produces only models, services, tests, a workbook, a page, a trace, a block rule, or a correction record without the joined ordinary path.

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
13. `docs/pro/evidence/MILESTONE_1_HOSTILE_REVIEW_RECONCILIATION_RECEIPT.md`
14. latest `docs/pro/DECISION_LEDGER.jsonl`
15. `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`
16. `docs/pro/COUNTEREXAMPLE_REGISTER.md`
17. `docs/pro/REPOSITORY_GROUND.md` and `docs/pro/PROMPT_AND_HARNESS_AUDIT.md`, reconciled against current code
18. this packet

Then inspect current models, migrations, services, views, URLs, templates, NTM adapter, active protocols, workbook probe, and adversarial tests. Translating documents do not override executable code.

## Product laws that control implementation

1. The fixture is a bounded test input, not the product or conceptual model.
2. `ResearchCampaign` remains an immutable execution episode; a new `ResearchJob` sits above it.
3. LibreOfficeDev is a pinned calculation proxy, not Excel or the mature adapter.
4. A deterministic gate is one safety mechanism, not the product value.
5. The first worker proposal is model-authored and provisional; source, object, artifact, actor and use identities are host-issued.
6. No candidate exists after the controlled 8-K block.
7. Meaning confirmation, method/source authorisation, work authorisation and synthetic candidate disposition remain distinct acts.
8. The product speaks in ordinary professional consequence, not campaign, packet, role, workbench, trace, state-machine or validator vocabulary.
9. The original artifact is immutable.
10. No raw feedback, trace, correction seed or single case changes the live harness.

## Owned files

The architectural writer owns only these existing files and new paths.

### Existing product and runtime files

- `prototypes/equities-research-cognition/product/campaign/models.py`
- `prototypes/equities-research-cognition/product/campaign/services.py`
- `prototypes/equities-research-cognition/product/config/settings.py`
- `prototypes/equities-research-cognition/product/config/urls.py`
- `prototypes/equities-research-cognition/harness/ntm/adapter.py`

### Exact new migrations

- `prototypes/equities-research-cognition/product/campaign/migrations/0005_model_change_v0.py`
- `prototypes/equities-research-cognition/product/campaign/migrations/0006_model_change_v0_guards.py`

Do not generate a different migration number or name. If the migration graph moved, stop with `MOVED_MIGRATION_BASE`.

### New bounded implementation package

- `prototypes/equities-research-cognition/product/campaign/model_change/__init__.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/adapter.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/forms.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/projections.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/services.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/urls.py`
- `prototypes/equities-research-cognition/product/campaign/model_change/views.py`

### New visible templates

- `prototypes/equities-research-cognition/product/templates/model_change/index.html`
- `prototypes/equities-research-cognition/product/templates/model_change/episode.html`

Use the existing base template and stylesheet. Do not create a dashboard shell, permanent sidebar, card-grid system, new design system, settings area, agent monitor, or provenance console.

### New protocol

- `prototypes/equities-research-cognition/agents/model_change_v0.md`

### Synthetic seeding and captured-source fixtures

- `prototypes/equities-research-cognition/product/campaign/management/__init__.py`
- `prototypes/equities-research-cognition/product/campaign/management/commands/__init__.py`
- `prototypes/equities-research-cognition/product/campaign/management/commands/seed_model_change_v0_case_a.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/fixtures/model_change_v0/case_a_8k.txt`
- `prototypes/equities-research-cognition/scenarios/adversarial/fixtures/model_change_v0/case_a_10k.txt`

The existing workbook fixture is read-only:

`prototypes/equities-research-cognition/spikes/workbook_capability/fixtures/minimal_model.xlsx`

Do not modify or replace it.

### New tests

- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_models.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_services.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_ui.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_migrations.py`

### Required return evidence

- `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
- optional sanitised evidence only under `docs/pro/evidence/case-a-v0/`

No other path is owned. If a required change cannot be made within this population, stop and return the exact missing interface and why it is causally required. Do not widen the packet silently.

## Files and surfaces explicitly prohibited

Do not modify:

- `docs/pro/*.md` other than the receipt path above;
- `docs/pro/DECISION_LEDGER.jsonl` or `CURRENT_SEMANTIC_CHECKPOINT.md`;
- historical worker packets or receipts;
- `tools/classify_loc.py` or `test_c4_architecture.py`;
- the workbook spike or its fixture;
- `skills/lock.json`, active workbench protocols, or dormant DeepResearch prompts;
- review-app models, migrations, views, routes, or templates;
- existing campaign templates or legacy `/campaigns/` routes;
- `pyproject.toml` or dependencies;
- deployment, infrastructure, secret, credential, or production configuration.

Do not delete, rename, reinterpret, or destructively backfill existing campaign records.

## Minimum canonical records

Implement exactly the minimum population in the accepted vertical contract:

- `ResearchJob`;
- `ModelChangeEpisode`;
- `ArtifactManifestVersion`;
- `ConceptualObjectVersion`;
- `ObjectDisposition`;
- `SourceDocumentVersion`;
- `SourceAssertion`;
- `ModelChangeProposal`;
- `AdmissibilityDecision`;
- `CalculationReceipt`;
- `Amendment`;
- `InvalidationEvent`;
- `ArtifactDisposition`;
- `CorrectionRecord`.

Extend `ArtifactVersion` additively with nullable parentage, candidate role and nullable candidate-from-pass linkage.

Do not implement the deferred catalogue as extra tables. Do not add explicit tenant, membership, objective-version, work-plan, professional-exception, evaluation-run, intervention, promotion, harness-release or separate candidate-artifact tables.

### Required authority ownership

- Host-owned: exact bytes, digests, identity, owner, episode, current closure, source capture identity, assertion locator, target address, formula text, dependency closure, adapter/profile, engine result, legal transition, invalidation, and timestamps.
- Model-proposed: bounded economic meaning, typed value operation, claim ceiling, explanation, or refusal.
- Human-attributed: meaning confirmation/amendment, method/source-policy authorisation, repair action, assumption where applicable, and synthetic disposition.

A model cannot issue an identity later used to validate itself.

## Stable service interfaces

Implement or expose a compatibility facade with these exact semantic interfaces:

```text
JobService.begin_or_resume(owner, company_ref, objective, named_use, cutoff,
                           starting_artifact)
  -> ResearchJob + ModelChangeEpisode

ObjectService.inspect(episode, artifact, adapter_profile)
  -> ArtifactManifestVersion + proposed ConceptualObjectVersion

ObjectService.disposition(actor, object_version, action, bounded_payload)
  -> ObjectDisposition | Amendment + replacement ConceptualObjectVersion

EvidenceService.capture(document_bytes, identity, access_context)
  -> SourceDocumentVersion

EvidenceService.assert(document_version, locator, value, dimensions)
  -> SourceAssertion

WorkCompiler.compile(episode, current_object, current_authority, manifest,
                     captured_assertions, protocol_version)
  -> immutable WorkOrder packet

ProposalParser.parse(worker_output, exact_packet)
  -> ModelChangeProposal | bounded refusal

AdmissibilityGate.evaluate(proposal, current_closure)
  -> AdmissibilityDecision(PASS | BLOCK | UNSUPPORTED | JUDGMENT_REQUIRED)

CandidateService.create(pass_decision, exact_parent, adapter_profile)
  -> child ArtifactVersion + operation receipt + CalculationReceipt

DispositionService.record(actor, candidate, named_use,
                          SIMULATE_NAMED_USE | REJECT | REWORK)
  -> ArtifactDisposition

InvalidationService.amend(actor, exact_ancestor, bounded_change)
  -> Amendment + replacement + InvalidationEvent[]

ProjectionService.resume(owner, job_id, episode_id)
  -> current state + immutable history

CorrectionService.seed(block, amendment, replacement, candidate, versions)
  -> CorrectionRecord
```

Names may differ only if the receipt maps every implementation symbol one-to-one to this contract and tests use the facade. Views submit bounded commands and render projections only.

## Migration and database contract

### Migration 0005

Add the minimum records and nullable `ArtifactVersion` fields.

- No rename, delete, destructive backfill, or semantic reinterpretation.
- Existing rows remain valid.
- Existing campaigns receive no synthetic `ResearchJob` automatically.
- New `ModelChangeEpisode` rows bind one new campaign each.
- Add feature flag `MODEL_CHANGE_V0`, default false outside explicit test/demo settings.

### Migration 0006

Install direct-SQL append-only and cross-record guards.

Every new canonical fact and disposition must reject direct update and delete. Candidate linkage must require:

- one exact current `PASS` decision;
- same owner, job, episode and campaign;
- same proposal, conceptual object, source assertion, parent artifact, manifest and closure;
- candidate parentage to the exact starting artifact; and
- no invalidated ancestor.

Where declarative constraints cannot span rows, use narrow PostgreSQL triggers plus service validation. Add direct-SQL hostile tests.

### Migration verification

Prove:

- fresh install through new head;
- upgrade from `campaign.0004` with representative legacy rows preserved;
- migration plan and drift clean;
- reverse works only when V0 tables are empty;
- reverse after population refuses before destructive operations;
- code rollback with flag off leaves populated schema readable and dormant.

The configured development database being behind migration head is not evidence of successful upgrade. Use isolated fresh and upgrade databases and record exact commands.

## Runtime and cognition contract

### Protocol

`model_change_v0` returns one typed proposal or bounded refusal. Minimum proposal fields:

```text
schema: model-change-proposal/v0
episode_id, episode_digest, input_revision
conceptual_object_id, conceptual_object_digest
starting_artifact_id, starting_artifact_digest
source_assertion_id
operation: {kind: set_numeric_value, target_ref, value, unit}
claim_ceiling
```

### Closed evidence

The packet records `network_policy=closed_captured_sources`. The Codex launcher must omit `--search` for this protocol while preserving existing behaviour for other protocols. All supporting sources are exact host-captured inputs.

An uncaptured web result, worker-authored URL, document class, assertion, or locator cannot support admission.

### Topology

Use exactly one real NTM/Codex worker. Do not add a planner, reviewer, critic, synthesis stage, machine judge, workbench, or reasoning skill.

### Custody

Preserve:

- exact packet derivation and digest;
- role/protocol version identity;
- input materialisation and digest checks;
- tracked send and acknowledgement;
- completion observation;
- sealed output and attestation;
- provisional custody;
- stale-output retention as diagnostic evidence; and
- Langfuse as optional post-custody diagnostics.

Typed parsing and deterministic admission occur after custody and before artifact mutation.

## Deterministic source-to-target gate

### Annual target

The captured 8-K and 10-K assertions both contain `37,378` USD millions.

For `FY25_REVENUE_USDM`, after the filed annual report is available, the captured 8-K proposal must produce:

`BLOCK_WRONG_DOCUMENT_CLASS`

The block must create zero candidate files and zero candidate artifact rows.

The user action `Create a candidate using the filed annual report` creates an attributed amendment and a replacement host-derived proposal referencing the captured 10-K. Only a later exact `PASS` permits candidate creation.

### Paired target

For `FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE`, the same captured 8-K assertion must `PASS`. The validator must not implement document recency, filing, GAAP, or 10-K preference globally.

### Identity attacks

Reject before mutation:

- invented identifiers;
- unknown identifiers;
- stale closure or input revision;
- cross-owner, cross-job, cross-episode or cross-campaign references;
- wrong conceptual object;
- wrong source assertion;
- wrong artifact digest;
- wrong target reference;
- unsupported operation;
- invalid units or dimensions; and
- invalidated ancestors.

## Bounded workbook adapter

Implement stable `inspect`, `apply`, `calculate`, and `compare` operations behind `product.campaign.model_change.adapter`.

Supported profile only:

- one workbook-defined numeric target;
- exactly two declared arithmetic dependents;
- no macro, external link, data table, volatile function, circular calculation, protected structure, or structural insertion;
- exact parent digest and manifest digest;
- pinned LibreOfficeDev build;
- exact engine identity, timeout, environment, operation receipt, input/output digests, formula errors and warnings.

The existing fixture and spike are read-only evidence. Reuse mechanism carefully; do not import fixture-specific constants as product policy.

Only `harness/ntm/adapter.py` may spawn the allowlisted calculation process. Add a separate explicit calculation command grammar with `shell=False`, exact binary allowlist, bounded arguments, timeout, isolated temporary profile and controlled environment. Do not create a generic process runner.

The adapter must return `UNSUPPORTED_PROFILE` or `UNSUPPORTED_STRUCTURAL_OPERATION` without a candidate when outside the profile.

The parent workbook remains byte-for-byte unchanged. Dependent/cached values cannot be written manually.

## Ordinary-language product route

Add a `/jobs/` resumption entry and the exact episode route:

`/jobs/<job_id>/model-change/<episode_id>/`

The synthetic seed command may create one owner-bound Case A job, episode, exact starting artifact and exact captured source documents. It must use public synthetic/test facts and product services; it may not seed worker output, block/pass decisions, candidate artifacts, calculation receipts, dispositions, or correction records.

The episode page must expose only current professional context and consequence:

- current objective and original artifact;
- bounded object meaning when confirmation is required;
- method/source rule when authorisation is required;
- `Run this work`;
- material source exception and unchanged-artifact fact;
- `Create a candidate using the filed annual report`;
- candidate delta and declared consequences;
- `Simulate named use`, `Reject`, `Request rework`;
- contextual immutable history; and
- support-only diagnostic link when necessary.

Do not render raw model JSON, packet digests, trace IDs, NTM controls, workbench names, state-machine statuses, generic approval, Casebook language, an agent graph, or a permanent disclaimer panel.

The host handles launch, readiness, send, completion, collection and correlation after one professional `Run this work` command. A bounded synchronous V0 orchestration is acceptable. If completion exceeds the existing supported timeout, preserve the state and show an ordinary-language non-authoritative running/failure message; do not expose transport controls.

## Correction, invalidation and synthetic disposition

The wrong-source repair appends an `Amendment`; it never edits the failed proposal.

Any material amendment to meaning, method/source policy, source assertion, starting artifact, manifest, operation, or assumption creates exact invalidation records for all named descendants.

A stale proposal, pass decision, candidate, calculation receipt or synthetic disposition remains historical but cannot appear current or be reused.

Artifact disposition values are exactly:

- `SIMULATE_NAMED_USE`;
- `REJECT`;
- `REWORK`.

Scope is exact owner, job, episode, candidate, named synthetic use and closure. No cross-scope use is allowed. UI and code must not imply professional reliance.

`CorrectionRecord` is an immutable seed referencing blocked proposal, reason code, amendment, replacement proposal, source assertions, candidate, episode, protocol version and adapter/profile version. Do not implement failure attribution, evaluation, intervention, promotion or harness release.

## Case B and C transfer tests

Do not implement their product journeys.

### Case B schema/interface transfer

Prove through model/service tests that the same conceptual and invalidation grammar can represent:

- host-captured reported charge;
- human-authored recurring-share assumption with scope, rationale and change condition;
- deterministic derived adjustment;
- later human amendment; and
- stale descendant invalidation.

Do not collapse the assumption into source metadata or model authorship.

### Case C safe refusal transfer

Prove:

- conceptual object identity can exist without a cell address;
- binding status `PROPOSED_STRUCTURE` is representable; and
- the V0 adapter returns `UNSUPPORTED_STRUCTURAL_OPERATION` with zero candidate.

Do not add structural insertion capability.

## Required tests

### Models, migrations and ownership

- fresh migration and upgrade from `campaign.0004` with legacy rows preserved;
- exact one-to-one episode/campaign ownership;
- ORM and direct-SQL append-only refusal for every new record;
- cross-record same-owner/job/episode/campaign guards;
- candidate-after-pass enforcement under ORM and direct SQL;
- empty reverse and populated reverse refusal/dormancy;
- feature-flag-off legacy behaviour;
- authenticated owner isolation and no cross-owner existence disclosure;
- no tenant-security claim.

### Sources, proposals and admission

- exact source bytes and digests;
- equal-value 8-K and 10-K remain distinct assertions;
- model proposal references host-issued IDs only;
- invented/unknown/stale/cross-scope/wrong-object/wrong-artifact references reject;
- 8-K annual target block and zero candidate;
- attributed repair and 10-K pass;
- preliminary target 8-K pass;
- `--search` absent for closed protocol and unchanged for existing protocols;
- uncaptured retrieval cannot support admission.

### Artifact and calculation

- original unchanged;
- only declared target changes before calculation;
- two dependents recalculate;
- exact engine build and digests recorded;
- formula errors prevent candidate disposition;
- unsupported profile and structural operation produce no candidate;
- candidate requires exact current pass and closure;
- invalidation makes every named descendant stale;
- new candidate/receipt/disposition required after amendment.

### Product interaction and restart

- six-or-fewer consequential submissions including seeded job entry;
- distinct meaning, method, run, repair and synthetic-disposition actions;
- ordinary-language exception generated from canonical facts;
- no raw JSON, source-ID entry, NTM buttons, Casebook terminology or agent spectacle;
- restart after meaning, block, repair, candidate, disposition and invalidation;
- restart works without NTM, Langfuse, terminal state or in-memory state;
- Langfuse absence/mismatch cannot change authority;
- action count, completion time, interruptions, reconstruction errors and candidate-review time recorded in the receipt.

### Regression

Run all mandatory package checks. The known binary-fixture classifier defect belongs to Packet 007; record its status but do not modify its files. Primary packet success requires its own focused tests to pass. Final integrated V0 acceptance additionally requires the reconciled classifier branch.

## Required live evidence

A passing code suite is insufficient.

Produce one real synthetic Case A run through:

```text
login
-> seeded ResearchJob/episode
-> meaning confirmation
-> method/source authorisation
-> Run this work
-> real NTM/Codex launch/send/completion/collection
-> typed 8-K proposal
-> deterministic block with zero candidate
-> attributed 10-K repair
-> deterministic pass
-> bounded candidate patch and LibreOfficeDev calculation
-> candidate review and synthetic disposition
-> process restart
-> same current projection and immutable history
-> exact correction seed
```

Record exact work-order, input, output, proposal, decision, artifact and receipt identities/digests. Do not include secrets, private account identifiers, raw traces or protected data in public evidence.

Capture sanitised browser evidence of the ordinary-language path when possible. Screenshots are evidence of rendering only and must be joined to canonical state assertions in the receipt.

If NTM/Codex, PostgreSQL or LibreOfficeDev is unavailable, return `PARTIAL_ENVIRONMENT_BLOCKER` with exact preflight, commands, completed code/tests and missing live evidence. Do not simulate the run or manually insert its output.

## Mandatory commands

From `prototypes/equities-research-cognition`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py showmigrations --plan
uv run python -W error manage.py test scenarios.adversarial.test_model_change_v0_models -v 2
uv run python -W error manage.py test scenarios.adversarial.test_model_change_v0_services -v 2
uv run python -W error manage.py test scenarios.adversarial.test_model_change_v0_runtime -v 2
uv run python -W error manage.py test scenarios.adversarial.test_model_change_v0_ui -v 2
uv run python -W error manage.py test scenarios.adversarial.test_model_change_v0_migrations -v 2
uv run python -W error manage.py test scenarios.adversarial.test_owned_job_bound_execution -v 1
uv run python -W error manage.py test scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check
```

Also run isolated fresh and upgrade migration commands, the exact synthetic seed command, the exact live NTM/Codex V0 command or browser sequence, the bounded adapter command, restart sequence, and feature-flag rollback sequence. Record every command, version, exit code, test count, warning and failure.

Do not suppress the classifier failure; identify the exact Packet 007 dependency result when available.

## Rollback evidence

The receipt must prove:

- predecessor commit;
- migration head before and after;
- feature flag default and explicit enablement;
- legacy routes and rows remain available;
- flag-off future episodes do not enter V0;
- populated schema is retained and readable;
- stale packets and candidates remain refused;
- adapter profile rollback affects future episodes only; and
- no history is deleted.

## Prohibited interpretations and substitutes

Do not claim or imply:

- Excel compatibility or native Excel integration;
- arbitrary workbook support;
- structural modelling support;
- tenant isolation or production security;
- professional correctness of the source rule, model meaning, candidate or calculation;
- professional permission to rely;
- analyst validation or reduced review burden;
- research quality, investment quality or product fit;
- harness improvement or promotion;
- deployment, production or client readiness.

Do not substitute:

- static fixture insertion for real NTM/Codex work;
- manually authored worker output;
- manually attached candidate workbook;
- hard-coded block/pass result;
- manually written dependent values;
- a raw JSON page;
- Casebook styling;
- a visible multi-agent topology;
- a generic provenance graph;
- extra canonical tables for conceptual completeness; or
- prompt prose for a missing deterministic control.

## Stop conditions

Stop and return a bounded blocker when:

- implementation base or migration graph moved;
- an essential file lies outside owned paths;
- a new dependency or system installation is required;
- exact source capture cannot be closed;
- candidate-after-pass cannot be enforced without weakening history;
- a process would be spawned outside the audited NTM boundary;
- the fixture requires widening beyond the accepted profile;
- a protected or personal source is required;
- the only route to success is hard-coded or manually attached evidence;
- the new route requires exposing harness vocabulary or runtime controls;
- any S1/S2 closure must be removed; or
- two repair attempts reproduce the same causal defect without new evidence.

A truthful `PARTIAL` or `FAIL` is valid. Do not widen the product or ask the user to coordinate a workaround.

## Required receipt

Create `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md` containing:

1. verdict: `PASS | PARTIAL_ENVIRONMENT_BLOCKER | PARTIAL_DEPENDENCY | FAIL`;
2. exact base, branch, result commit and ancestry;
3. complete changed-file list and ownership audit;
4. implemented canonical records and stable-interface symbol map;
5. migration files, SQL guards, fresh/upgrade/reverse/rollback evidence;
6. feature flag and legacy compatibility;
7. typed protocol, packet schema, closed-search evidence and cognition identity;
8. source fixtures, exact capture/assertion digests and equal-value distinction;
9. 8-K block, zero-candidate proof, paired target pass and 10-K replacement pass;
10. candidate parentage, operation receipt, engine/version, input/output digests, two consequences, warnings and formula errors;
11. amendment, invalidation, synthetic disposition and correction-seed evidence;
12. restart projection at each consequential state;
13. browser journey, visible language, consequential-action count and burden measures;
14. exact commands, versions, test counts, warnings and failures;
15. live NTM/Codex identifiers and sanitised trace/artifact joins;
16. classifier and direct-Excel dependency state;
17. rollback evidence;
18. unresolved facts and severity assessment;
19. claim ceiling and nonclaims; and
20. recommended PRO disposition.

## Return contract

Return directly to PRO and coordinating Codex:

- result commit;
- receipt path;
- verdict;
- changed files;
- migration and rollback summary;
- exact test/live evidence;
- unresolved dependency results;
- S1/S2 closure table;
- claim ceiling; and
- strongest reason to accept, repair or kill.

Do not merge, update the ledger/checkpoint, begin Cases B/C, activate evaluation, promote a harness change, deploy, or contact the user/analyst.

## Packet claim ceiling

A packet `PASS` means only that one public/synthetic Case A vertical was implemented on the worker branch with the exact joined behaviour and evidence required here. It does not mean that the branch has been independently verified or integrated, that analysts find it useful, that Excel is supported, that professional reliance is permitted, or that V0 is ready for cold testing.

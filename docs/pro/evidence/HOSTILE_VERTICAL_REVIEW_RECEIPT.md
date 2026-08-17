# Hostile Vertical Review Receipt

## VERDICT

**ACCEPT_WITH_EXACT_NARROWING**

One outcome-complete Case A vertical is coherent enough to compile into an implementation packet only if every narrowing constraint in this receipt is adopted as part of that packet. Acceptance applies to the contract shape, not to implementation, product readiness, analyst usefulness, Excel compatibility, professional correctness, or permission to rely on a candidate artifact.

The accepted unit is one joined model-change episode: understand one bounded workbook object, encounter and deterministically block one wrong-document-class proposal, correct the proposal, produce and calculate one descendant workbook, record a scoped synthetic disposition, restart from canonical state, and emit one exact correction seed. The four “Vertical A–D” capability slices in `docs/pro/PRODUCT_SYSTEM_ARCHITECTURE_V0.md` §11 are not independently acceptable delivery units; the first implementation vertical must join their minimum completion path.

No severity-one or severity-two architecture defect remains blocking only under the exact constraints, prerequisites, refusal states, migration boundary, and nonclaims below. Removing any of them requires another hostile review.

## BASE AND INDEPENDENCE

The review ran on branch `agent/hostile-vertical-review` at exact base `263d7ad146a511482b6de1e0f3cd167b49593270`. That commit descends from the packet lineage recorded on the branch. The tree was clean before review. The only later repository change made by this reviewer is this receipt.

Substantive review commit: recorded by the metadata follow-up commit.

Result commit: returned to the coordinating context after the follow-up commit; a Git commit cannot contain its own identifier.

I had no prior hidden project chat context. I received the active packet instruction and used repository-only project inputs. This is fresh-context review, not proof of technical isolation, organisational independence, or absence of shared model priors. I did not access protected/private material and did not contact a user, architect, analyst, or other reviewer.

I read the packet’s required artifacts in its exact order, after the root and package routing instructions. I then independently inspected these current repository surfaces rather than treating translating documents as implementation truth:

- root and package `AGENTS.md` and `ROUTE.md`;
- every governing and translating artifact enumerated in `docs/pro/worker-packets/004_HOSTILE_VERTICAL_REVIEW.md` §Required read order;
- `prototypes/equities-research-cognition/product/campaign/models.py`, migrations `0001` through `0004`, `services.py`, `views.py`, `urls.py`, and all campaign templates;
- project URL/settings configuration and current authentication/ownership lookups;
- `prototypes/equities-research-cognition/product/review/models.py`, transitions, views, URLs, and migration graph;
- `prototypes/equities-research-cognition/harness/ntm/adapter.py`, active agent protocols, active workbench protocols, `skills/lock.json`, runtime packet compilation, launch, send, collection, validation, correlation, and Langfuse trace handling;
- `prototypes/equities-research-cognition/spikes/workbook_capability/workbook_probe.py`, its fixture, tests, and historical receipt;
- the wrong-source, restart, custody, stale-input, refusal, stop, append-only, and workbook adversarial tests; and
- repository boundary/classification tools and the current Django migration plan.

Repository code and migrations govern current support. Product contracts govern desired capability. That distinction matters because `docs/pro/REPOSITORY_GROUND.md` and `docs/pro/PROMPT_AND_HARNESS_AUDIT.md` are pinned to an earlier repository basis, while the reviewed head is `263d7ad146a511482b6de1e0f3cd167b49593270`. The current semantic checkpoint explicitly preserves this evidence ceiling in `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md` §§Exact repository basis, Current implementation truth, and Evidence ceiling.

## EXECUTIVE DEFECTS

The un-narrowed contracts contain a recognisable professional journey, but they leave three implementation-critical joins implicit.

First, the current custody shell accepts an arbitrary JSON `candidate` and launches Codex with search enabled. The canonical work packet contains campaign/work-order/proposal/input identifiers but no typed conceptual-object version, source assertion, admissible operation, or closed evidence policy (`prototypes/equities-research-cognition/product/campaign/services.py:273-329`, `:1464-1492`, `:2195-2238`). That shell cannot by itself prove the source identity or spreadsheet operation required by the product contracts.

Second, the mature product is a continuing company research environment, while current collection and correlation are campaign-final (`prototypes/equities-research-cognition/product/campaign/services.py:2263-2266`, `:2556-2563`). The present `ResearchCampaign` also combines owner, issuer, decision use, cutoff, question, runtime session, and artifact root (`prototypes/equities-research-cognition/product/campaign/models.py:45-55`), and `RunSpecVersion` is one-to-one with a campaign (`:156-212`). Treating that object as both continuing job and terminal execution episode creates a dead end. The minimum repair is an additive `ResearchJob` above a one-campaign-per-episode execution container; existing campaign finality can then remain intact.

Third, the workbook spike proves a bounded OOXML patch plus LibreOffice recalculation proxy, not a product adapter. Its target, two formulas, parser, and inspected cells are fixture-specific (`prototypes/equities-research-cognition/spikes/workbook_capability/workbook_probe.py:28-43`, `:207-256`, `:338-475`), and the module deliberately does not invoke a host process (`:1-6`). No current product service joins deterministic admission, native-artifact mutation, calculation, descendant custody, invalidation, and scoped use.

These defects are repairable additively. They do not justify rewriting the custody shell, promoting the backend casebook into the product surface, treating the fixture as the product, or activating the complete canonical catalogue at once.

## CASE A — REPORTED UPDATE

### Synthetic case

The bounded fixture represents a Micron FY2025 revenue update. The workbook-defined target is `FY25_REVENUE_USDM`; the captured 8-K and filed 10-K both report `37,378` USD millions. The episode’s explicit policy is “after the filed annual report is available, the annual-report assertion governs the annual reported-value target.” This is deliberately a document-identity test: equality of values does not make two source assertions interchangeable.

### Required reasoning trace

1. The authenticated owner begins or resumes one `ResearchJob` and one immutable `ModelChangeEpisode`. The episode binds an exact starting `.xlsx` digest, a host-inspected manifest, the named target, its allowed operation, the two declared dependent cells, a decision use, and a cutoff.
2. The model may propose the target’s economic meaning. The human confirms or amends that meaning. This creates a typed disposition over an exact `ConceptualObjectVersion`; it does not authorise a source rule, method, artifact change, or use.
3. The human separately authorises the reported-value method and the episode’s source policy. This is a human judgment over an exact version, consistent with the host/model/human separation in `docs/pro/PROFESSIONAL_INTERACTION_AND_STATE_CONTRACT_V0.md` §3 and `docs/pro/CONCEPTUAL_MODEL_CONTRACT_V0.md` §§Machine, host, and human authority and Invariants.
4. The host compiles one typed, digest-bound work packet and runs one real NTM/Codex worker with captured sources only. Search is disabled. The controlled first proposal references the host-issued 8-K `SourceAssertion` identifier.
5. The host returns `BLOCK_WRONG_DOCUMENT_CLASS`. No candidate artifact may exist. The same numeric value from the wrong source remains a failed proposal, not a provisional candidate.
6. The visible exception says what happened and exposes the consequence-bearing action: **Create a candidate using the filed annual report**. Choosing it records an attributed `Amendment` and creates a derived proposal referencing the captured 10-K assertion. The analyst is not asked to type source identifiers, document metadata, packet JSON, or a validator reason code.
7. The host re-runs the deterministic gate. Only `PASS` permits a new child `ArtifactVersion`. The adapter applies the single admitted numeric operation to the exact parent and runs the pinned calculation engine. A `CalculationReceipt` records engine identity, input/output digests, two declared dependent outputs, and formula errors.
8. The user records exactly one of `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK` for that candidate and named synthetic use. V0 must not expose `USE_CANDIDATE`, “approved,” “ready to rely on,” or any equivalent professional authority.
9. Restart reconstructs the current episode from append-only canonical records. The exact amendment, blocked proposal, admitted proposal, descendant, calculation receipt, and scoped disposition remain inspectable.
10. The host emits an exact `CorrectionRecord` seed referencing the blocked and replacement proposals, reason code, source assertions, candidate, episode, and protocol/adapter versions. It does not promote a prompt, skill, workbench, or harness release.

### Paired hostile target

The required counterexample is a distinct synthetic target, `FY2025_PRELIMINARY_EARNINGS_FLASH_REVENUE`, whose authorised policy permits the captured 8-K because the target is explicitly preliminary earnings-flash work. The same 8-K assertion must `PASS` for that target. If the validator blocks it merely because a 10-K exists, the system has encoded a universal source hierarchy instead of the object- and use-specific rule demanded by `docs/pro/COUNTEREXAMPLE_REGISTER.md` and `HOSTILE_VERTICAL_REVIEW_CONTRACT_V0.md` §Case A.

### Artifact, correction, and evaluation consequences

- The first model proposal and block decision are immutable evidence. They never become a candidate.
- The amendment creates a new descendant proposal; it does not mutate the failed proposal.
- The candidate is an exact child of the starting artifact and can exist only after a pass decision over the same proposal, object version, source assertion, input digest, and episode.
- The calculation receipt is a child consequence of that candidate, not evidence that the economic meaning or source policy was correct.
- The scoped synthetic disposition is invalidated when any ancestor named in its closure changes.
- The correction seed creates an evaluation candidate only; promotion remains governed by `docs/pro/EVALUATION_AND_HARNESS_EVOLUTION_CONTRACT_V0.md` §§Exact correction capture, Controlled comparison, Promotion and rollback, and Preventing evidence laundering.

## CASE B — ASSUMPTION OR ADJUSTMENT

### Synthetic case

Fictitious Alloy Systems has a known workbook target `Model!H42`, “FY2026 normalised operating-profit restructuring adjustment.” A captured filing reports a restructuring charge of `120` USD millions. The analyst judges that `25%` is recurring, with scope “FY2026 base case” and change condition “revisit if the company discloses closure run-rate or revised guidance.” The derived adjustment is `-120 × (1 - 0.25) = -90` USD millions.

This case is materially different from Case A. The reported charge is a host-bound source assertion; the recurring share, scope, rationale, and change condition are human judgment. No source-quality hierarchy can determine `25%`, and a model declaration cannot silently become the assumption.

### Required reasoning trace

1. The manifest binds `Model!H42`, its stable target identifier, the allowed numeric-set operation, unit, and dependency closure.
2. A `ConceptualObjectVersion` distinguishes the reported charge, recurring-share assumption, derived adjustment, scope, rationale, and change condition.
3. The model may propose the economic relationship; the human separately confirms meaning and authorises the assumption/method. The source assertion remains a host fact.
4. The deterministic host derives `-90`; the model does not get authority to invent or overwrite the arithmetic.
5. A later attributed amendment changes the recurring share to `40%`, deriving `-72`. That amendment invalidates the old proposal, candidate, calculation receipt, and simulated-use disposition. The prior history remains readable.
6. A replacement candidate and calculation receipt are required before a new synthetic disposition.

Case B does not need to be implemented in the first vertical, but the first schema and service interfaces must represent it without collapsing human judgment into source capture or model output. It is a transfer test for the conceptual-object version and invalidation grammar, not permission to expand the first implementation scope.

### Burden and support

Relative to Case A, Case B adds one consequential assumption submission and, when the assumption changes, one amendment submission. Its human acts are professional: defining the adjustment and later changing it. The host owns exact arithmetic, ancestry, invalidation, and stale-result refusal. Current support is absent beyond append-only custody primitives; free-text `CurrentCorrection` and quarantined `FutureProposal` (`prototypes/equities-research-cognition/product/review/models.py:244-264`) are not sufficient canonical representations.

## CASE C — STRUCTURAL ADDITION

### Synthetic case

Fictitious Northstar Devices discloses a new Cloud Infrastructure segment. Its current workbook contains total revenue and old segment rows but no stable row or named target for the new segment. This is materially different from both a reported-value update and a numeric adjustment: the object can be economically meaningful before it has a final artifact binding.

### Required reasoning trace and refusal

1. Create a conceptual object with an identity independent of a cell address and artifact-binding status `PROPOSED_STRUCTURE`.
2. Bind the starting workbook, a host-inspected insertion anchor, the existing total-revenue relationship, and the allowed inspection profile. Do not pretend that a target cell already exists.
3. Let the model propose a bounded row/formula/dependency addition. A human must confirm economic meaning and method before mutation.
4. The V0 adapter grammar supports only one stable named numeric target. It must return `UNSUPPORTED_STRUCTURAL_OPERATION`; no candidate may be emitted.
5. Preserve the refused episode in the continuing job so a later adapter/profile can address it without rewriting history.

Case C is not part of the first implementation vertical. Its required result is safe refusal, which disproves two bad architectural shortcuts: conceptual-object identity cannot be synonymous with a spreadsheet coordinate, and the current fixture cannot be generalised into an unbounded spreadsheet-construction engine. The object/binding distinction is required by `docs/pro/CONCEPTUAL_MODEL_CONTRACT_V0.md` §§Artifact structure and dependencies, Minimum joined model-change record, and Model building or structural addition.

## MIGRATION AND CURRENT-CODE BOUNDARY

### Current substrate to preserve

The implementation should preserve, rather than rename or reinterpret:

- Django authentication and current director scoping, while making no tenant-isolation claim (`prototypes/equities-research-cognition/product/campaign/views.py:45-46`);
- `ResearchCampaign` as an immutable execution-episode container;
- exact input bytes and digests in `ArtifactVersion` (`prototypes/equities-research-cognition/product/campaign/models.py:128-153`);
- `Proposal`/`Disposition` as work-authorisation custody;
- `RunSpecVersion`, `WorkOrder`, `RuntimeEvent`, `Artifact`, and `TraceLink` for bound execution and diagnostic trace custody (`prototypes/equities-research-cognition/product/campaign/models.py:156-409`, `:412-442`, `:546-579`); and
- the existing `/campaigns/<uuid>/` route as an internal support surface, not the new product form (`prototypes/equities-research-cognition/product/campaign/urls.py:7-85`).

Current templates expose runtime controls and raw candidate JSON, and the index asks the operator to author Codex output and upload sources (`prototypes/equities-research-cognition/product/templates/campaign/index.html:4-28`, `job.html:25-88`). Those are inherited substrate, not reusable interaction evidence. The new visible route should be additive and bounded: `/jobs/<job_id>/model-change/<episode_id>/`.

### Minimum additive canonical population

The next migration should add only the records needed to make the accepted vertical’s joins legal and restartable:

1. `ResearchJob`: authenticated owner, company identity, mandate identity, creation metadata.
2. `ModelChangeEpisode`: job, one-to-one existing `ResearchCampaign`, immutable objective, named synthetic use, cutoff, and starting artifact.
3. `ArtifactManifestVersion`: host-inspected target, allowed-operation grammar, dependency closure, adapter/profile version, and digest.
4. `ConceptualObjectVersion`: immutable parent, manifest reference, economic meaning, method/source-policy representation, binding status, and claim ceiling.
5. `ObjectDisposition`: exact object version, actor, and typed `CONFIRM_MEANING`, `AMEND_MEANING`, or `AUTHORIZE_METHOD` consequence.
6. `SourceDocumentVersion`: overlay of exact `ArtifactVersion` bytes with host capture/access metadata and document identity.
7. `SourceAssertion`: document version, exact locator, value, unit/dimensions, target compatibility, and digest.
8. `ModelChangeProposal`: immutable ancestry; proposer kind; host-issued episode, object, artifact, source, and operation references; protocol version; claim ceiling.
9. `AdmissibilityDecision`: proposal, validator version, `PASS`, `BLOCK`, `UNSUPPORTED`, or `JUDGMENT_REQUIRED`, typed reason codes, and exact closure digest.
10. `CalculationReceipt`: candidate, adapter/engine/profile versions, input/output digests, declared dependent outputs, warnings, and formula errors.
11. `Amendment`: actor, exact ancestor, bounded action, rationale, and replacement reference.
12. `InvalidationEvent`: amendment, invalidated object, reason, and closure digest.
13. `ArtifactDisposition`: exact candidate and named use; `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK` only.
14. `CorrectionRecord`: the minimum exact evaluation seed; no attribution, intervention, evaluation, promotion, or release record yet.

Extend `ArtifactVersion` additively with nullable `parent`, candidate role, and nullable `candidate_from` decision. Enforce that a candidate has one parent and one `PASS` decision in the same episode/campaign. Existing rows remain valid with null fields.

This is smaller than the full catalogue in `docs/pro/PROFESSIONAL_INTERACTION_AND_STATE_CONTRACT_V0.md` §4 because these concepts remain versioned JSON fields or projections in V0: `Tenant`, `Membership`, separate `JobObjectiveVersion`, `ArtifactBinding`, `DependencyClosure`, `MethodBinding`, `SourcePolicy`, `EntitlementReceipt`, `WorkPlan`, `CognitionPackage`, `WorkUnitSpec`, `ProfessionalException`, `CandidateArtifactVersion`, and `FailureAttribution`. `EvaluationCase`, `InterventionCandidateVersion`, `EvaluationRun`, `PromotionDecision`, and `HarnessReleaseVersion` remain entirely out of the first implementation. No planner, adversarial-review agent, synthesis stage, machine judgment sidecar, dashboard, institutional-memory browser, or provenance console is activated.

### Migration mechanics and direct-SQL boundary

Use an additive migration after `campaign.0004` to create the records and nullable artifact fields, followed by a migration that installs direct-SQL append-only triggers and cross-record guards. Current Python `AppendOnlyModel` prevents ORM update/delete (`prototypes/equities-research-cognition/product/campaign/models.py:35-42`), but current database triggers cover only `ArtifactVersion`, `RunSpecVersion`, and bound `WorkOrder` (`prototypes/equities-research-cognition/product/campaign/migrations/0004_bound_input_history_append_only.py:4-50`). Every new canonical fact and disposition needs direct-SQL update/delete protection.

Required database invariants include unique episode-to-campaign ownership; same-episode/campaign closure for proposals, decisions, candidates, receipts, and dispositions; candidate-after-pass only; exact-parent linkage; immutable digests; append-only histories; and no current disposition whose named ancestors are invalid. Where a declarative constraint cannot span rows, use a narrow database trigger plus service-level validation and adversarial direct-SQL tests.

No rename, delete, destructive backfill, or reinterpretation of existing campaign rows is allowed. Existing campaigns stay legacy execution episodes with no `ResearchJob`. New product episodes always get a new campaign, so current campaign-wide collection/correlation finality remains episode-scoped without changing its semantics.

## RUNTIME AND COGNITION

The current runtime boundary has valuable custody: exact input materialisation, attested NTM send/completion, output validation, immutable runtime events, and post-collection correlation. It must be preserved. Current tests already challenge acknowledgement mismatch, conflicting candidate/refusal output, input tampering, restart, and direct-SQL mutation (`prototypes/equities-research-cognition/scenarios/adversarial/test_owned_job_bound_execution.py:246-344`, `:454-506`, `:566-590`, `:911-960`).

The semantic envelope must change. For `model_change_v0`, compile exactly one model work unit from canonical state with this minimum typed proposal schema:

```text
schema: model-change-proposal/v0
episode_id, episode_digest, input_revision
conceptual_object_id, conceptual_object_digest
starting_artifact_id, starting_artifact_digest
source_assertion_id
operation: {kind: set_numeric_value, target_ref, value, unit}
claim_ceiling
```

All identifiers and admissible target references are host-issued. Unknown, invented, stale, cross-episode, or unbound identifiers reject the output before artifact mutation. The model proposes; it does not validate its own source identity, calculate source precedence, grant professional use, or select a harness release.

Case A runs exactly one real NTM/Codex worker. The current unconditional `--search` launch argument (`prototypes/equities-research-cognition/product/campaign/services.py:1492`) must be absent when the packet’s `network_policy` is `closed_captured_sources`. A future retrieved source must first become a host-captured `SourceDocumentVersion` and `SourceAssertion`; an uncaptured web result can be diagnostic only. Langfuse remains diagnostic evidence and cannot settle source identity, conceptual meaning, admissibility, or use.

Do not make `planner`, `adversarial_review`, `synthesis`, or `judgment` mandatory product stages. Their conditional roles and current evidence limits are already stated in `docs/pro/EVALUATION_AND_HARNESS_EVOLUTION_CONTRACT_V0.md` §10. Adding them to the first path would increase inference, interaction, and attribution surfaces without addressing the deterministic join.

## ADAPTER DECISION

An updated direct-Excel assumption test is a **parallel dependency**, not a precondition to begin the host/object/runtime vertical. It becomes a precondition before any claim of “Excel compatible,” native-Excel workflow support, open/save fidelity in Excel, or a cold test whose required path uses Excel rather than the bounded proxy.

Do not reactivate the stale direct-Excel packet by reference. The PRO must compile a new, current-base test that decides whether supported Excel for the Web/native Excel can serve as the reference open/recalculate/export adapter and compares its exact bytes, cached results, formula errors, names, styles, and unsupported-feature behaviour with the proxy route.

The first implementation may use only this falsifiable adapter profile:

- direct OOXML inspection and patching of one workbook-defined, single numeric input;
- exactly two declared arithmetic dependents;
- no macros, external links, data tables, volatile functions, circular calculations, protected structure, or structural row/formula insertion;
- a pinned LibreOfficeDev calculation proxy with exact engine build recorded; and
- safe `UNSUPPORTED_PROFILE` or `UNSUPPORTED_STRUCTURAL_OPERATION` refusal outside that envelope.

The stable adapter boundary is:

```text
inspect(workbook_bytes, profile) -> ArtifactManifestVersion
apply(parent_bytes, admitted_operations, expected_manifest_digest)
  -> candidate_bytes + operation_receipt
calculate(candidate_bytes, profile) -> CalculationReceipt
compare(parent_bytes, candidate_bytes, dependency_closure)
  -> declared_consequences
```

The spike establishes mechanism evidence only. Its probe hard-codes the target and formula closure, uses a limited defined-name/dependency parser, and delegates recalculation to an externally invoked LibreOffice binary (`prototypes/equities-research-cognition/spikes/workbook_capability/workbook_probe.py:28-43`, `:207-256`, `:289-310`, `:338-475`; `docs/pro/evidence/WORKBOOK_CAPABILITY_SPIKE_RECEIPT.md` §§Selected route, Boundary review, Unresolved integration work, Claim ceiling and nonclaims).

Package authority permits host-process spawning only through `prototypes/equities-research-cognition/harness/ntm/adapter.py`; that adapter currently calls `subprocess.run(..., shell=False)` for NTM (`:48-83`). V0 must either extend that single audited process boundary with a separately allowlisted calculation command or call an external calculation service. For the smallest local vertical, extend the one boundary behind the adapter interface with an exact binary allowlist, argument grammar, timeout, isolated temporary profile, controlled environment, and `shell=False`. Spawning LibreOffice from a view, service, probe, or new arbitrary helper is prohibited.

## INTERACTION AND REVIEW BURDEN

The accepted visible surface exposes consequences, not runtime administration. Each visible action has this exact state and support trace:

| Visible action | Input and canonical transition | Artifact consequence | Correction and invalidation consequence | Validation and evaluation signal | Current support |
|---|---|---|---|---|---|
| Begin/resume job | Owner + job/episode + exact artifact; create or load current projection | None | A changed starting artifact creates a new episode; it never edits the old one | Owner lookup, artifact digest, resume test | Partial auth/campaign restart only |
| Confirm meaning | Exact object version + confirm/amend; append `ObjectDisposition` | None | Amendment replaces the object version and invalidates named descendants | Version/current-ancestor check; correction/reconstruction signal | Missing |
| Authorise method/source policy | Exact object version + bounded policy; append distinct `ObjectDisposition` | None | A later policy/method amendment invalidates proposal through use | Completeness and actor-authority check; Case B transfer test | Missing |
| Run work | Current object/policy/manifest; append proposal authority, `WorkOrder`, and typed packet | None until a later pass | Stale or refused output is retained diagnostically but cannot create descendants | Digest, captured-input, search-policy, worker-attestation checks; live-run trace | Custody partial; semantic envelope missing |
| Resolve wrong-source exception | Exact block + “Create a candidate using the filed annual report”; append `Amendment` and derived proposal | Still none until pass | Records the exact correction; block remains immutable; stale proposal stays invalid | Replacement assertion and policy gate; paired hostile target | Missing |
| Review candidate | Exact child artifact + `CalculationReceipt` | Displays source, before/after input, two declared consequences, errors | Rework or any ancestor amendment invalidates candidate, receipt, and disposition | Parent/pass/engine/digest/closure checks; formula/consequence tests | Spike mechanism only |
| Simulate named use / reject / rework | Exact candidate + use + typed disposition | No mutation | Rework starts an amendment; any stale ancestor invalidates the disposition | Current closure and scope check; use-leakage test | Missing |
| Resume | Job/episode identifier; reconstruct from append-only facts | None | Shows correction chronology and excludes invalid descendants from current state | Restart projection, stale-descendant tests, review-cost signal | Campaign restart partial |

For an existing job, the happy-but-corrected Case A path has five consequential submissions: confirm meaning, authorise method/source policy, run, resolve the source exception, and disposition the candidate. Creating a job and uploading the starting artifact adds one, for six total. Launch/readiness/send/collect/correlate controls must not become additional analyst actions.

Three acts are irreducibly professional in this synthetic path: confirming meaning, authorising the method/source rule, and choosing the final synthetic disposition. The wrong-source continuation is a bounded choice about whether to create a replacement, not a request for the analyst to diagnose or author system metadata. Case B adds one assumption submission and a later amendment if the assumption changes. Case C should terminate in a safe refusal after the understanding/method/run sequence rather than invite spreadsheet design through forms.

Stop and reassess the product form if the cold tester needs more than six core submissions for Case A, must type source/document identifiers, inspect raw packets/traces, manually recalculate, operate NTM controls, or reconstruct why the exception occurred. Measure completion time, interruptions, reconstruction errors after restart, candidate-review time, and actions that do not alter professional state. These remain falsifiable product-form hypotheses, not analyst-attested evidence.

## RESTART, INVALIDATION AND ROLLBACK

### Restart

Restart is a projection over immutable facts, not session continuity. The current object, authorised method/policy, active proposal, block/pass decision, current candidate, calculation receipt, and scoped disposition are selected only when their full ancestor closure remains current. A stale runtime result remains diagnostic evidence but cannot be admitted. A restarted browser must show the same professional state without requiring NTM, Langfuse, a live terminal session, or hidden in-memory state.

### Invalidation

An amendment never edits an ancestor. It appends a replacement and exact `InvalidationEvent` records. Changing the object meaning, method/source policy, source assertion, starting artifact, target manifest, admitted operation, or assumption invalidates every named descendant: proposal, pass decision, candidate, calculation receipt, and synthetic disposition. New work must bind a new closure digest. Stale packet output can be retained as rejected diagnostic material, but it cannot reactivate a stale descendant or overwrite a current state projection.

Use scope is exact. A synthetic disposition applies only to one candidate, episode, job, named use, and closure. It does not cross to another scenario, artifact version, company job, user, or professional reliance decision. The term `USE_CANDIDATE` in the broader contract is therefore narrowed out of V0.

### Rollback

The new route and orchestration service ship behind `MODEL_CHANGE_V0`. Code rollback disables that flag and restores the exact predecessor release for future episodes; legacy `/campaigns/` remains available. Historical jobs, episodes, proposals, decisions, artifacts, receipts, amendments, invalidations, dispositions, and correction seeds remain readable.

Schema reversal is allowed only on an empty, pre-population installation. Once any canonical V0 row exists, rollback must not drop tables, triggers, or evidence; leave the additive schema dormant and forward-fix. The deployment receipt must record the predecessor commit and migration state. Adapter rollback selects the predecessor adapter/profile for future episodes and never rewrites an existing manifest or calculation receipt.

The first vertical does not promote a harness release. It emits a correction seed only. Any later harness rollback must restore a recorded predecessor for future work while retaining the superseded release, input packets, evaluations, and historical episode evidence, as required by `docs/pro/EVALUATION_AND_HARNESS_EVOLUTION_CONTRACT_V0.md` §8.3.

## SMALLEST ACCEPTED OR RIVAL VERTICAL

The smallest accepted vertical is **Case A: one bounded reported-value update with a deliberately wrong but numerically equal source, deterministic block, attributed source correction, candidate patch, proxy recalculation, scoped synthetic disposition, restart, and correction seed**.

Its exact visible journey is:

1. Resume a synthetic Micron job and see the exact FY2025 revenue object and starting workbook.
2. Confirm its meaning.
3. Authorise the reported-value method and target-specific filed-annual-report policy.
4. Run one bound NTM/Codex work unit over captured sources with search closed.
5. See that the 8-K proposal was blocked before mutation.
6. Choose “Create a candidate using the filed annual report.”
7. Review the descendant’s exact source, before/after target, two recalculated consequences, engine identity, and formula-error status.
8. Record `SIMULATE_NAMED_USE`, `REJECT`, or `REWORK`.
9. Restart and recover the same state/history.
10. Inspect the exact correction seed, without promotion.

The rival is not another product form; it is a narrower mechanism-only workbook demo. That rival would be easier to build but fails the commission because it omits controlled failure, correction authority, continuing-job restart, scoped use, and the evaluation seed. Conversely, implementing the architecture document’s four capability slices as separate delivery milestones would produce partial components without a recognisable analyst outcome. The joined Case A path is therefore the minimum lawful unit.

## STABLE INTERFACES

The next packet may choose internal names, but these semantic boundaries must remain stable:

```text
JobService.begin_or_resume(owner, company_ref, objective, named_use, cutoff,
                           starting_artifact) -> ResearchJob + ModelChangeEpisode

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

ProposalParser.parse(worker_output, exact_packet) -> ModelChangeProposal | refusal
AdmissibilityGate.evaluate(proposal, current_closure)
  -> AdmissibilityDecision(PASS | BLOCK | UNSUPPORTED | JUDGMENT_REQUIRED)

CandidateService.create(pass_decision, exact_parent, adapter_profile)
  -> child ArtifactVersion + operation receipt + CalculationReceipt

DispositionService.record(actor, candidate, named_use,
                          SIMULATE_NAMED_USE | REJECT | REWORK)
  -> ArtifactDisposition

InvalidationService.amend(actor, exact_ancestor, bounded_change)
  -> Amendment + replacement + InvalidationEvent[]

ProjectionService.resume(owner, job_id, episode_id) -> current state + immutable history
CorrectionService.seed(block, amendment, replacement, candidate, versions)
  -> CorrectionRecord
```

Each interface accepts canonical identifiers/digests, returns canonical records, and refuses stale or cross-scope inputs. Views render projections and submit bounded commands; they do not compile authority, inspect workbook truth, spawn processes, decide admissibility, or infer current ancestry.

## REQUIRED TESTS AND LIVE EVIDENCE

Implementation acceptance requires all of the following; existing green mechanical tests do not substitute for them.

### Migration, custody, and ownership

- fresh database migration and upgrade from `campaign.0004` with legacy rows preserved;
- direct-SQL update/delete refusal for every new canonical row and candidate linkage;
- same-job/episode/campaign and candidate-after-pass constraints under ORM and direct SQL;
- empty-schema reverse test and post-population rollback refusal/dormancy test;
- authenticated owner isolation and no cross-owner existence disclosure; no tenant-security claim until a real tenant model is implemented.

### Source identity and deterministic admission

- invented, unknown, stale, cross-episode, and wrong-object identifiers reject before mutation;
- the 8-K Case A proposal returns `BLOCK_WRONG_DOCUMENT_CLASS` and creates no candidate;
- the derived 10-K proposal passes only after an attributed amendment;
- the same captured 8-K assertion passes for the explicitly preliminary earnings-flash target;
- numerically equal assertions remain distinct; document identity is never inferred from value equality;
- `--search` is absent and the packet records closed captured-source policy; uncaptured retrieval cannot support admission.

### Artifact, calculation, invalidation, and use

- exact parent remains byte-for-byte unchanged after patch;
- only the declared target changes before recalculation; declared dependents update; formula errors fail admission to disposition;
- candidate creation requires the exact current `PASS` decision and closure;
- unsupported workbook features and structural operations refuse without a candidate;
- any ancestor amendment invalidates proposal, decision, candidate, calculation receipt, and prior simulated-use disposition;
- a new candidate/recalculation/disposition is required after amendment;
- synthetic use cannot cross use, candidate, episode, job, company, or owner scope and cannot be rendered as professional permission.

### Runtime, restart, cognition, and product form

- one live NTM/Codex Case A run exercises launch, send, completion, typed output, collection, correlation, deterministic block, correction, candidate, and receipt custody;
- stale packet and stale worker-result tests retain diagnostics but refuse admission;
- restart reconstructs every state after block, amendment, candidate, disposition, and invalidation without live runtime state;
- Langfuse absence, delay, or mismatch cannot change deterministic authority;
- a cold internal tester completes the ordinary-language path without legacy casebook jargon, raw JSON, NTM controls, or source-ID authoring;
- the test records consequential-action count, completion time, interruptions, reconstruction errors, and review time.

### Adapter and direct Excel

- repeat the exact bounded LibreOfficeDev profile with pinned build, isolated profile, deterministic operation receipt, digest accounting, and safe refusal cases;
- run a separately compiled direct-Excel assumption test before any Excel-compatibility/native-Excel claim;
- compare open/recalculate/export behaviour, named ranges, cached values, formulas, style preservation, errors, and unsupported features; record the adapter decision rather than generalising from one fixture.

### Current executable evidence

The documentation review ran these commands from the repository/package as appropriate:

```text
git status --short --branch
git rev-parse HEAD
git branch --all --list '*hostile-vertical-review*'
git rev-parse --verify origin/agent/hostile-vertical-review
git switch --track origin/agent/hostile-vertical-review
git log --oneline --decorate --graph --max-count=20
git diff --stat c1fc...HEAD
git diff --name-status b4b...HEAD

uv --version
uv run python --version
command -v soffice && soffice --version
command -v ntm
command -v codex
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py showmigrations --plan
uv run python -W error manage.py test \
  scenarios.adversarial.test_owned_job_bound_execution \
  scenarios.adversarial.test_workbook_capability_spike -v 1
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check

uv run python spikes/workbook_capability/workbook_probe.py patch \
  spikes/workbook_capability/fixtures/minimal_model.xlsx \
  /tmp/hostile-vertical-review.rESgzC/patched/candidate.xlsx
soffice -env:UserInstallation=file:///tmp/hostile-vertical-review.rESgzC/profile \
  --headless --convert-to xlsx \
  --outdir /tmp/hostile-vertical-review.rESgzC/recalculated \
  /tmp/hostile-vertical-review.rESgzC/patched/candidate.xlsx
uv run python spikes/workbook_capability/workbook_probe.py verify-run \
  spikes/workbook_capability/fixtures/minimal_model.xlsx \
  /tmp/hostile-vertical-review.rESgzC/patched/candidate.xlsx \
  /tmp/hostile-vertical-review.rESgzC/recalculated/candidate.xlsx
```

Observed environment: macOS `15.3` build `24D2059`, arm64; `uv 0.9.8`; Python `3.14.0`; LibreOfficeDev `26.8.0.0.alpha0`; `ntm` at `/usr/local/bin/ntm`; Codex at `/Users/singh/.local/bin/codex`.

Observed results:

- Django system check passed with no issues; `makemigrations --check --dry-run` reported no changes.
- The focused owned-job/workbook run passed 19 tests in 3.314 seconds.
- The full adversarial command discovered 118 tests and ran 113 in 21.169 seconds, then failed with one setup error: `tools/classify_loc.py` attempts UTF-8 decoding of the binary `.xlsx` fixture. `check_boundary.py` passed; direct `classify_loc.py` failed on the same known binary-fixture defect. This is a repository classification defect, not evidence against the Case A contract, but it must be fixed or the check deliberately recompiled before integration acceptance.
- The configured development database was not at migration head: campaign migrations `0001`–`0004` and review migration `0015` were unapplied. Tests used a clean test database and applied migrations. No claim about upgrading that configured database follows.
- The live local workbook rerun patched `FY25_REVENUE_USDM`, recalculated with LibreOfficeDev, changed the two expected dependent values, and reported no formula errors. Fixture digest was `e06961d...`, patched digest `d458d17...`, and the observed recalculated digest was `51336107...`; recalculated ZIP bytes may vary with package timestamps. This is proxy mechanism evidence only.
- No product-path live NTM/Codex run, browser cold test, Excel for the Web/native Excel run, protected-source run, production migration, or deployment occurred. The receipt-only authority supplied no new product implementation or captured source corpus.

## SEVERITY-ONE AND SEVERITY-TWO FINDINGS

The following severities describe defects in the un-narrowed architecture/current-code join. Their stated closure is mandatory; they are not assertions that current code already implements the closure.

### Severity one

**S1-1 — Arbitrary candidate output and open search can bypass source/object authority.** Current output validation accepts a non-empty candidate dictionary, and runtime launch unconditionally enables search (`prototypes/equities-research-cognition/product/campaign/services.py:1464-1492`, `:2195-2238`). **Closure:** typed host-issued proposal references, closed captured-source network policy, deterministic admission, and candidate-after-pass database enforcement.

**S1-2 — Campaign-wide finality conflicts with a continuing job.** A campaign mixes job and runtime concerns, has one run spec, and becomes final after correlation (`prototypes/equities-research-cognition/product/campaign/models.py:45-55`, `:156-212`; `prototypes/equities-research-cognition/product/campaign/services.py:2263-2266`, `:2556-2563`). **Closure:** additive `ResearchJob` and immutable one-campaign-per-episode ownership; preserve current campaign finality.

**S1-3 — No product calculation boundary joins admission to native-artifact custody.** The workbook probe is an external fixture-specific mechanism and does not invoke its own host process. **Closure:** stable inspect/apply/calculate/compare interface, one audited process/service boundary, calculation receipt, candidate ancestry, safe profile refusal, and direct-Excel parallel test before Excel claims.

### Severity two

**S2-1 — “Vertical A–D” are capability slices, not outcome-complete delivery units.** **Closure:** the first implementation packet must join the complete Case A path through correction seed.

**S2-2 — The full canonical catalogue is too large for V0 and obscures the minimum legal joins.** **Closure:** create only the minimum population listed here; project or defer the named remainder.

**S2-3 — A deterministic source repair could be laundered into analyst metadata work.** **Closure:** the exception exposes a bounded consequence, “Create a candidate using the filed annual report”; the host owns document identity and validator reason codes.

**S2-4 — Structural object identity becomes circular if it requires a pre-existing cell.** **Closure:** independent conceptual-object identity plus `PROPOSED_STRUCTURE` binding status and `UNSUPPORTED_STRUCTURAL_OPERATION` refusal in V0.

**S2-5 — ORM append-only behaviour exceeds current database enforcement.** **Closure:** direct-SQL triggers/guards and adversarial tests for all new canonical records and candidate relationships.

**S2-6 — Professional permission can be implied by synthetic fixture disposition.** **Closure:** expose only `SIMULATE_NAMED_USE`, `REJECT`, and `REWORK`; retain exact scope and invalidate descendants. `USE_CANDIDATE` is outside V0.

**S2-7 — Current executable evidence has two integration limits.** The configured development database is behind migration head, and repository LOC classification crashes on the binary fixture. **Closure:** fresh/upgrade migration evidence and a repaired or deliberately recompiled classifier check before implementation acceptance.

**S2-8 — The old direct-Excel assumption packet is stale.** **Closure:** compile a new current-base parallel test; do not reactivate the prior packet by implication.

There are no unresolved S1/S2 blockers under this verdict only because the closures above are acceptance constraints. The PRO must reject any implementation packet that omits them.

## CLAIM CEILING AND NONCLAIMS

This receipt supports one claim: the joined contracts can be narrowed into a coherent, additive, testable Case A implementation contract at the boundaries specified here.

It does not establish that:

- the vertical has been implemented or is ready to build without a new PRO packet;
- an analyst recognises the journey as useful, natural, or sufficiently low burden;
- the current interface, backend casebook, routes, templates, or fixture are the product form;
- the workbook proxy is Excel, preserves arbitrary workbooks, or supports structural modelling;
- the source rule, conceptual meaning, method, candidate, or use disposition is professionally correct;
- synthetic use permits professional reliance;
- NTM/Codex research quality, cognition quality, or product fit is adequate;
- Langfuse traces prove authority, correctness, or causality;
- authentication equals tenant isolation or production security;
- the evaluation seed improves a prompt, skill, workbench, model, or harness;
- a harness change may be promoted; or
- the system is deployable, scalable, institutionally governable, or privacy-safe for protected work.

Direct evidence in this review is limited to current repository code/contracts/tests and the local bounded workbook rerun. Case A/B/C product journeys, interaction burden, and adapter usefulness remain synthetic hypotheses requiring the named hostile and cold evidence.

## RECOMMENDED NEXT PRO DECISION

Accept the verdict only as a narrowed architecture adjudication, reconcile it into the governing checkpoint/ledger, and compile one implementation packet for the joined Case A vertical. That packet should own the additive migration, typed runtime envelope, deterministic gates, new ordinary-language route, bounded workbook adapter, restart/invalidation projection, synthetic disposition, hostile tests, live NTM run, and correction seed. It must preserve existing campaign custody and legacy routes, prohibit professional-use language, and stop at the stated adapter profile.

Compile a separate, current-base direct-Excel assumption packet as a parallel dependency. Its result gates Excel/native-workflow claims, not the start of the host/object/runtime implementation. Separately recompile the repository classifier check around binary fixtures and require clean fresh/upgrade migration evidence.

The exact next PRO question is: **Can a context-free implementor deliver the joined Case A episode, including the wrong-source block, attributed repair, recalculated child, scoped synthetic disposition, restart, and correction seed, without mistaking the fixture, campaign substrate, LibreOffice proxy, or deterministic gate for the mature product?** If the implementation packet does not make the answer mechanically reviewable, do not activate it.

# Active Build Contract

Contract ID: `MU-MODEL-UPDATE-V0`

Status: PRO-authorised experimental public-repository slice. Implementation has not started. This contract may be revised or killed only through an append-only decision-ledger entry that names the evidence.

Verified implementation basis: `agent/pro-responsibility-handoff` at `c1fc568424facbb5bb8e1b6369d30a1f380ae308`.

Working branch: `agent/pro-grounding`.

## Product hypothesis

An artifact-native model-update companion can preserve the leverage of a real Codex model-population run while reducing review to consequential exceptions if it creates a recalculated candidate workbook only after every proposed cell change joins a host-captured source assertion to a versioned target contract and a human explicitly disposes the exact candidate for a named use.

Excel remains the native work product. The web product owns the ongoing job, exact inputs, source identity, target policy, agent proposal, deterministic containment, candidate workbook versions, recalculation evidence, correction, history, and permission to rely. This proof does not decide the mature product form.

## Cold falsification question

For one historical Micron post-earnings update, can a user start from an exact workbook and official sources, run real NTM/Codex work, observe a numerically correct but target-inadmissible source proposal blocked before workbook mutation, replace it with the admissible source, receive a verifiably recalculated candidate workbook, and decide its named use without reconstructing the whole job manually?

Kill or redesign the hypothesis when the answer is no because:

- workbook parsing, preservation, or supported recalculation cannot be established;
- support requires code written specifically for one workbook rather than a declared bounded workbook contract;
- the source policy blocks legitimate target-specific practice;
- the user must verify every source, cell, formula, or calculation from scratch;
- correction cannot produce an exact recomputed descendant;
- permission to rely cannot be scoped to one exact artifact and use; or
- web identity, runtime entitlement, and research authority cannot remain distinct.

## Product-form comparison

### Integrated modelling workspace

This form could eventually place the model, research, changes, collaboration, and history in one environment. It is not the first proof because reproducing spreadsheet interaction would consume the experiment before source admission and recomputation are established. It also risks turning a narrow demo workbook into a false claim that the product can replace Excel.

Decision: not selected for V0.

### Artifact-native companion

This form keeps Excel as the owned artifact, uses the present authenticated job and runtime spine, and adds the missing host seam around exact sources, target-specific policy, proposed changes, recalculation, exceptions, and scoped use. The analyst sees recognisable model work without navigating backend stages.

Decision: selected for V0.

### Durable research-job hub with specialised workspaces

This form fits the mature thesis and long-lived resumption, but as a first slice it risks another abstract campaign or provenance dashboard. Its value cannot be distinguished from the current job substrate until one specialised workspace completes native work.

Decision: parked. The selected companion may later live inside such a hub.

## Public Micron episode

### Subject and cutoff

- Issuer: Micron Technology, Inc.
- SEC CIK: `0000723125`
- Historical evidence cutoff: `2025-10-04`
- Named use: update the demo workbook's FY2025 historical revenue line and inspect its declared downstream formulas. This is not an investment recommendation or an institutional release.

### Source pair

The intentional failure uses two official SEC filing populations that carry the same annual revenue value:

1. 8-K accession `0000723125-25-000024`, filed `2025-09-23`, with EX-99.1 earnings release. The release reports FY2025 revenue of `37,378` USD millions and marks the financial statements unaudited.
   - Filing index: `https://www.sec.gov/Archives/edgar/data/723125/000072312525000024/0000723125-25-000024-index.html`
   - Exhibit: `https://www.sec.gov/Archives/edgar/data/723125/000072312525000024/a2025q4ex991-pressrelease.htm`
2. 10-K accession `0000723125-25-000028`, filed `2025-10-03`, for period ended `2025-08-28`. It reports FY2025 revenue of `37,378` USD millions.
   - Filing index: `https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/0000723125-25-000028-index.html`
   - 10-K: `https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm`

The value is deliberately identical. The product must decide admissibility from the exact target policy and machine-owned source attributes, not from arithmetic or document prestige in the abstract.

### Starting workbook contract

The live demo uses a purpose-built public `.xlsx` workbook, created before the run and uploaded through the ordinary product path. It is an input artifact, not a precomputed success result.

V0 supports only a declared bounded workbook profile:

- Office Open XML `.xlsx`;
- no VBA or macros;
- no external workbook links;
- no data tables, circular references, volatile external functions, or unsupported formula families;
- one stable workbook-defined named range `FY25_REVENUE_USDM` referring to one input cell;
- a prior FY2024 revenue input of `25,111` USD millions;
- a stale FY2025 revenue value that must change to `37,378` USD millions;
- at least two downstream formulas, one calculating FY2025 revenue growth and one calculating a simple revenue-dependent multiple using a fixed mechanical assumption;
- visible number formats and styles on the target and downstream cells; and
- an immutable original byte digest.

The mechanical multiple is included only to prove dependency and recalculation. It is not a valuation judgment.

The product must refuse a workbook outside the supported profile. A passing purpose-built workbook proves only that the bounded adapter works for that profile.

### Target contract

The user confirms one ordinary-language model line after workbook inspection. The host stores an immutable target contract version bound to the exact workbook digest and named range:

- display name: `FY2025 consolidated revenue`;
- target: named range `FY25_REVENUE_USDM`;
- entity: Micron Technology, Inc., CIK `0000723125`;
- metric: revenue;
- period end: `2025-08-28`;
- period kind: fiscal year;
- unit and scale: USD millions;
- accounting basis: GAAP;
- scope: consolidated;
- allowed source predicate for this version: Micron Form 10-K for the target period, available on or before the cutoff; and
- rationale: this historical annual line is configured to use the filed annual report once available.

This is a versioned human-authored policy enforced by the host. It is not a universal rule that annual reports, filings, or GAAP always win.

A separate mechanical test must define another target contract that lawfully permits an EX-99.1, a non-GAAP value, a derived calculation, or an analyst assumption. Hard-coding `10-K good; earnings release bad` fails the contract.

## End-to-end journey

1. The user logs in and creates an owned Micron model-update job with the objective, named use, cutoff, starting workbook, and the two exact SEC source URLs.
2. The host captures the source index and document bytes, stores immutable versions, extracts or verifies the supported source attributes and assertions, and refuses any unallowlisted or unverifiable source.
3. The job workspace inspects the workbook without changing it. The user confirms the named model line and its target-specific source policy in ordinary language.
4. The host creates one exact run specification and one bounded model-population work order. The product starts real NTM/Codex work through the existing runtime boundary.
5. For the controlled adversarial run, a versioned work-order instruction directs the worker to use the September earnings-release assertion. This is an intentional treatment, not evidence that an unconstrained model naturally chooses the wrong source.
6. The worker returns one typed provisional proposal referencing the host-issued earnings-release assertion and the host-issued target contract.
7. The host validates exact identities and blocks the proposal because the target requires the available 10-K. No candidate workbook or downstream calculation is created.
8. The workspace states the mismatch in ordinary language, shows the exact source passage and target expectation, and states that the workbook has not changed.
9. The user chooses `Replace with the 10-K value` or rejects the proposal. Replacement creates an attributed immutable amendment referencing the exact 10-K assertion; it does not alter the worker's original proposal.
10. The host re-runs the same target-specific admission policy. If it passes, the host applies the one allowed cell operation to a new workbook version, preserves the original, runs the supported recalculation engine, validates the candidate, and records the exact changed dependencies and any errors.
11. The workspace presents the target change, exact support, changed downstream formulas and values, assumptions, and candidate workbook download. It does not imply that the candidate is already adopted.
12. The user records `Use`, `Reject`, or `Amend` for the exact candidate and exact named use. `Amend` creates a new proposal or assumption version and requires a new candidate and recalculation. A generic acceptance flag is forbidden.
13. After process restart, the same authenticated user retrieves the exact job, blocked proposal, amendment, candidate workbook, recalculation receipt, disposition, runtime history, and trace correlation from canonical state.
14. The product asks the cold-test questions that can produce go, revise, or kill. It does not claim analyst approval from completion.

## Smallest coherent screen set

The existing login flow remains. The product needs two product surfaces, not an agent console.

### Jobs

The existing owned-job list and create form are retained and narrowed to recognisable inputs:

- company and job title;
- what the user is trying to update;
- named use;
- evidence cutoff;
- starting workbook;
- permitted SEC source URLs; and
- the instruction for the agent.

Creating the job does not start work.

### Model update workspace

One ongoing workspace renders setup, work, exception, candidate, and history from canonical state. A contextual source view may open beside the work; it is not a separate ontology page.

A blocked state should read approximately:

```text
Micron FY2025 model update

FY2025 consolidated revenue
Current workbook value: 36,900 USDm
Proposed value: 37,378 USDm

Blocked
This proposal cites the September earnings release. This model line is set to use
Micron's filed 10-K once it is available. The 10-K was filed on 3 October 2025
and reports the same value.

No workbook has been changed.

[View both sources] [Replace with the 10-K value] [Reject this change]
```

After a lawful replacement and recalculation:

```text
Candidate workbook ready

FY2025 consolidated revenue       36,900 -> 37,378 USDm
FY2025 revenue growth              changed after recalculation
Revenue-dependent multiple         changed after recalculation

Source: Micron 2025 10-K
Recalculation: passed with recorded engine and version

[Download candidate workbook]
[Use for the named model-update job] [Amend] [Reject]
```

The primary interface must not display protocol names, agent roles, research-state vocabulary, raw JSON, trace IDs, eyebrows, overlines, kickers, or decorative categorical labels. Exact IDs and runtime receipts may appear under a technical record for debugging.

Every visible value and action must have a canonical source, legal transition, validation path, and consequence.

## Canonical backend state

### Existing objects retained

- `ResearchCampaign` remains the authenticated owned job.
- `ArtifactVersion` retains exact starting and captured input bytes.
- `RunSpecVersion` binds objective, instruction, cutoff, input population, and outcome contract.
- `Proposal`, `ProposalDisposition`, and `WorkOrder` preserve authorised work chronology.
- `RuntimeEvent` preserves NTM/Codex lifecycle evidence.
- `Artifact` preserves exact worker outputs and later product-generated receipts.
- `TraceLink` remains post-custody diagnostic correlation only.

Existing objects may be extended only where their present semantics remain true. No mutable status field should replace append-only chronology.

### New immutable objects

#### SourceDocumentVersion

Binds one exact captured document to host-issued source identity:

- job;
- exact content artifact and SHA-256;
- canonical URL;
- capture adapter and version;
- host and capture timestamp;
- SEC accession;
- parent filing form type;
- document sequence and document type, including exhibit type where applicable;
- filer CIK;
- filing date and accepted time;
- report period where available;
- parser diagnostics; and
- canonical metadata digest.

For V0, capture is restricted to allowlisted `https://www.sec.gov/Archives/edgar/data/...` filing-index and document URLs. Redirects outside the allowlist, excessive bytes, unsupported content, missing filing identity, or inconsistent metadata refuse atomically.

#### SourceAssertion

Binds one exact supported value assertion to a `SourceDocumentVersion`:

- extraction adapter and version;
- assertion key or supported financial concept;
- exact source locator;
- exact passage or canonical source fragment digest;
- decimal value;
- unit and scale;
- entity;
- period;
- accounting basis and scope when the adapter can establish them;
- extraction diagnostics; and
- canonical digest.

The worker cannot create or edit a source assertion. For the V0 Micron case, the source adapter must deterministically reproduce the `37,378` USDm annual revenue assertion from both source documents while preserving their different document classes. If this cannot be done without episode-specific hard-coding or a worker-authored identity, the source slice stops.

#### WorkbookManifestVersion

Binds an exact workbook artifact to the supported structural facts produced by a versioned adapter:

- workbook digest;
- sheet identities;
- named ranges and target addresses;
- relevant cell values, formulas, number formats, and styles;
- declared formula dependencies;
- macro, external-link, circular-reference, and unsupported-feature diagnostics;
- adapter and engine requirements; and
- manifest digest.

The manifest is a host-owned projection of exact bytes. It is not the workbook itself.

#### WorkbookTargetContractVersion

Stores the attributed, versioned semantics and policy for one exact workbook target:

- workbook manifest;
- stable target ID and named range;
- display name;
- entity, metric, period, unit, scale, basis, and scope;
- allowed source predicates;
- allowed authority variants, including explicit analyst-assumption policy when applicable;
- author and rationale;
- effective cutoff or condition; and
- canonical digest.

The host owns the version and enforcement. The human owns the configured professional meaning.

#### ModelChangeProposal

Preserves one immutable agent or human proposal:

- producing work order or parent amendment;
- target contract version;
- operation, restricted in V0 to `set_value`;
- exact decimal value, unit, and scale;
- source assertion or explicit analyst-assumption object;
- rationale;
- authority label `worker_candidate` or `human_amendment`; and
- canonical digest.

A proposal has no adopted status.

#### AdmissibilityDecision

Preserves the deterministic result of one policy version over one proposal:

- proposal;
- exact target policy digest;
- exact source assertion digest;
- result `PASS` or `BLOCK` for V0;
- ordered reason codes and human-readable explanation data;
- evaluator version; and
- canonical digest.

Missing or unsupported facts block. The evaluator may not manufacture professional meaning.

#### ProposalAmendment

Preserves the user's exact correction without rewriting the worker proposal:

- parent proposal;
- actor;
- replacement source assertion or attributed assumption;
- rationale;
- named change condition when an assumption is used; and
- resulting immutable proposal identity.

#### WorkbookCandidateVersion

Binds a new exact `.xlsx` artifact to:

- parent workbook version;
- exact admitted proposal set;
- patch adapter and version;
- allowed target operation;
- candidate bytes and digest;
- generated manifest; and
- provisional-only authority.

A blocked proposal can never be referenced by a candidate.

#### RecalculationReceipt

Binds one candidate to an independently observed calculation attempt:

- engine and exact version;
- invocation or API configuration;
- start and completion times;
- exit result;
- input and output workbook digests;
- preserved formula and named-range checks;
- before and after target and dependent values;
- formula errors, warnings, unsupported features, and diagnostics;
- result `PASS` or `REFUSE`; and
- canonical digest.

Opening and saving a workbook is not recalculation. Manually writing cached formula values is forbidden.

#### ArtifactUseDisposition

Preserves scoped human authority:

- actor;
- exact candidate workbook version;
- exact job and commission;
- named use;
- scenario where relevant;
- disposition `USE`, `REJECT`, or `AMEND`;
- rationale or amendment instruction; and
- timestamp and digest.

`USE` is legal only for a candidate with a passing recalculation receipt and no active blocker. It does not grant global truth, publication, investment authority, or permission for another use.

## Derived state transitions

State is derived from immutable records rather than overwritten flags:

```text
job created
-> source capture and workbook inspection
-> target contract confirmed
-> work order authorised
-> runtime launched and exact proposal collected
-> proposal blocked | proposal admitted

proposal blocked
-> rejected | attributed source replacement | attributed assumption amendment
-> new admissibility decision

proposal admitted
-> candidate patch attempted
-> recalculation passed | bounded refusal

recalculation passed
-> candidate awaiting disposition
-> USE | REJECT | AMEND

AMEND
-> new proposal or target-contract version
-> new candidate and recalculation required
```

Any amendment to the proposal, target contract, source assertion, starting workbook, or calculation policy invalidates descendant candidate authority and requires a fresh candidate and disposition.

## Agent work-unit contract

V0 uses one capable Codex worker. No extra planner, critic, or visible agent role is justified.

A new typed protocol, provisionally named `model_population`, may be introduced only after the workbook capability spike passes. It consumes:

- exact campaign, run-specification, proposal, work-order, and logical-role identities;
- exact starting workbook and manifest identities;
- exact target contract version;
- exact host-issued source assertion catalogue;
- objective, named use, and evidence cutoff;
- exact controlled adversarial source-selection instruction for the demo run;
- allowed output root and required paths; and
- resource and refusal bounds.

The worker may interpret the target, compare exact host-issued assertions, and propose one value. It may not:

- create source, assertion, target, workbook, policy, or authority identities;
- write or recalculate the workbook;
- broaden the target population;
- silently substitute a source or assumption;
- adopt its proposal; or
- grant artifact use.

The required semantic output is either one bounded refusal or one exact proposal envelope:

```json
{
  "schema_version": "model-change-proposal/v0",
  "campaign_id": "<exact id>",
  "run_spec_id": "<exact id>",
  "work_order_id": "<exact id>",
  "proposals": [
    {
      "target_contract_id": "<host-issued id>",
      "operation": "set_value",
      "value": {"decimal": "37378", "unit": "USD", "scale": 1000000},
      "source_assertion_id": "<host-issued id>",
      "reason": "<bounded explanation>"
    }
  ],
  "refusal": null,
  "authority": "provisional_only"
}
```

The host validates exact population, identity, decimal, unit, operation, source assertion, and target contract before creating `ModelChangeProposal` records.

For the controlled failure, the work-order instruction must be versioned and visible in the technical receipt as an adversarial treatment. The resulting containment proves host enforcement under a wrong proposal, not a natural model error rate.

The work order should omit `--search`. Because the current sandbox does not prove complete read isolation, the product must not claim the worker saw only supplied sources. The stronger authority rule is that no externally observed fact can support a proposal unless it resolves to a host-issued assertion in the exact work-order catalogue.

## Deterministic containment rules

### Source identity and capture

- SEC URLs are allowlisted by exact scheme and host.
- The host captures index and document bytes with byte, time, content-type, and redirect bounds.
- Source metadata is derived from exact SEC records and stored with adapter version and diagnostics.
- Worker-authored URLs, form types, accession numbers, filing dates, or document classes cannot become source identity.
- Tampered bytes or metadata mismatch refuse.

### Cutoff

- Filing and publication availability must be on or before `2025-10-04` for the episode.
- Any source or assertion after the cutoff blocks.
- The date-only cutoff is sufficient for this historical case because the 10-K was filed the previous day. No intraday claim is made.

### Target admission

The V0 evaluator compares the exact proposal against the exact target contract on:

- entity;
- metric;
- period;
- unit and scale;
- accounting basis;
- scope;
- document class and allowed source predicate;
- cutoff; and
- value equality with the referenced source assertion.

Every compared field must come from a host object or an attributed target policy. Missing, unsupported, or contradictory fields block. Reason codes remain granular; a single generic `invalid source` result is insufficient.

### Operation and workbook identity

- The starting workbook digest must match the target contract and manifest.
- V0 permits only one `set_value` operation at the exact named target.
- The original workbook is never modified.
- No operation runs after a blocked decision.
- A candidate must reproduce the admitted proposal and parent digests.

### Preservation and recalculation

- Formulas outside the allowed target must remain textually identical for the declared relevant population.
- Named ranges, target address, relevant styles, and number formats must remain intact.
- The candidate must be opened by a supported calculation engine, not merely serialised by the patch library.
- The engine and version are captured.
- Formula errors, unsupported formulas, lost references, changed formulas, missing cached results, or engine failure produce a bounded refusal.
- Downstream before/after values and dependency paths are stored from exact manifests and calculation output.

### Human authority

- A source replacement or assumption is attributed and versioned.
- A candidate remains provisional after every machine check.
- `USE` binds one exact candidate to one exact named use.
- Any change to an ancestor requires new recomputation and disposition.
- No trace, score, model agreement, or successful test can create a `USE` record.

### Observability

- Existing runtime events and artifact attestation remain canonical execution evidence.
- Langfuse correlation occurs after output custody and links to the exact proposal artifact.
- Trace data may explain why the worker chose EX-99.1; it cannot override the block or authorise the workbook.

## Workbook capability gate

No production model, source gate, prompt, or interface work begins until a bounded Codex spike resolves this question:

> Can the current implementation environment read a purpose-built `.xlsx`, identify the named target, preserve the declared formulas, names, styles, and original bytes, write one candidate target value, run an independently observed supported recalculation engine, reopen the result, and prove that declared dependent cached values changed without manually fabricating them?

A valid spike return may be `PASS`, `PARTIAL`, or `FAIL`.

`PASS` requires exact input/output digests, adapter and engine versions, target before/after values, unchanged formula strings, unchanged named target, relevant style checks, changed dependent values, zero formula errors, and repeatable commands.

`PARTIAL` or `FAIL` must state the missing engine, unsupported feature, preservation loss, environmental dependency, or reproducibility problem. It must not simulate success.

The spike is mechanical evidence only. It does not create a product object, source gate, Micron episode, or workbook-support claim beyond its fixture.

## Build slices and dependency order

### Slice 0 — Workbook capability spike

Status: authorised and active.

Owned surface: experiment-only workbook adapter, fixture/test, dependency changes strictly needed for the spike, and one evidence receipt. No product models, services, templates, prompts, or runtime changes.

Exit: PRO reconciles the exact diff and evidence as `PASS`, `PARTIAL`, or `FAIL` and updates the decision ledger.

### Slice 1 — Source, assertion, workbook, and target contracts

Status: blocked by Slice 0.

Implement immutable objects, migrations, SEC capture adapter, source assertion extraction, workbook manifest creation, target confirmation, hostile tests, and database-level append-only protection appropriate to the new authoritative facts.

Exit: exact source pair and target can be created through services, tampering is rejected, and no model call is required.

### Slice 2 — Typed model-population work order and admissibility

Status: blocked by Slice 1.

Implement the typed protocol, packet compiler, search entitlement change, output validator, proposal chronology, deterministic target-specific evaluator, controlled wrong-source treatment, and hostile tests including a permitted non-GAAP or EX-99.1 target.

Exit: real or mechanically simulated runtime output cannot create a candidate workbook when the wrong source is referenced.

### Slice 3 — Candidate workbook and recalculation

Status: blocked by Slice 2 and Slice 0 PASS.

Move the proven adapter behind production services, create candidate and receipt objects, implement dependency and invalidation rules, and prove exact correction followed by recalculation.

Exit: correct source replacement creates one candidate and one passing receipt; all unsupported states refuse.

### Slice 4 — Model update workspace and scoped use

Status: blocked by Slice 3.

Replace the narrow bound-job result view for this protocol with the ordinary-language workspace, source inspection, exact correction, candidate download, `USE | REJECT | AMEND`, history, tenant isolation, and restart retrieval. Do not alter the legacy Casebook except to prevent it becoming the route for this job.

Exit: every visible object and action maps to canonical state and is covered by request-level tests.

### Slice 5 — Live Micron episode and cold review

Status: blocked by Slice 4.

Run login through ordinary UI, exact SEC capture, real NTM/Codex controlled failure, block, correction, patch, recalculation, disposition, Langfuse correlation, and process restart. Preserve a redacted public receipt tied to the exact commit. Ask go, revise, or kill questions.

Exit: evidence satisfies the governing release standard or the product remains an experimental prototype with named failures.

### Slice 6 — Correction-to-evaluation experiment

Status: not authorised by this contract.

Only after the product episode exists may the exact source correction seed an evaluation candidate and a reversible policy or workflow treatment. No live self-modification is permitted.

## Acceptance tests

### Workbook capability

- exact starting bytes remain unchanged;
- stable target named range resolves to the expected cell;
- candidate changes only the allowed target value at the semantic level;
- declared formulas, named ranges, relevant styles, and number formats are preserved;
- a supported engine and version are recorded;
- dependent cached values change after engine recalculation;
- formula errors and unsupported features fail closed; and
- a second run reproduces the same semantic result and receipts.

### Source and assertion custody

- only allowlisted SEC sources are accepted;
- accession, filing form, document type, CIK, filing date, report period, and exact bytes are reproducible;
- changed document bytes invalidate the source identity;
- worker-provided source identity is rejected;
- the exact `37,378` assertion is bound separately to EX-99.1 and the 10-K; and
- post-cutoff, wrong-entity, wrong-period, wrong-unit, wrong-basis, and wrong-scope fixtures are blocked when those dimensions are supported.

### Target-specific admission

- the EX-99.1 assertion is blocked for the configured 10-K target despite the equal value;
- the 10-K assertion passes for that target;
- an explicit different target can permit EX-99.1 or non-GAAP authority;
- a missing target contract blocks;
- an invented source assertion ID blocks;
- a value that differs from the referenced assertion blocks; and
- a blocked proposal creates no candidate workbook, recalculation receipt, or use disposition.

### Correction and recomputation

- replacing the source creates an attributed amendment without mutating the worker proposal;
- the amended proposal receives a new admission decision;
- the correct proposal produces one child candidate of the exact starting workbook;
- every dependent result shown in the UI comes from the exact recalculation receipt;
- changing any ancestor invalidates descendant use and requires a new candidate; and
- an unsupported workbook or failed engine yields a bounded refusal, not a partially updated file.

### Scoped authority

- `USE` requires the exact candidate, passing receipt, job, actor, and named use;
- `REJECT` cannot delete chronology;
- `AMEND` cannot mutate the candidate in place;
- one use cannot authorise another scenario, job, or artifact;
- no agent or telemetry path can create a human disposition; and
- another authenticated user receives `404` for all job artifacts and actions.

### Ordinary live path

A reviewer must observe, without fixture injection after job creation:

```text
login
-> create Micron job and exact inputs
-> confirm target contract
-> start real NTM/Codex work
-> collect wrong-source proposal
-> deterministic block before workbook change
-> attributed replacement with exact 10-K assertion
-> patch and supported recalculation
-> inspect changed dependencies
-> dispose exact candidate for named use
-> correlate diagnostics
-> restart and retrieve the same chronology and artifacts
```

## Evidence to capture

Each slice returns:

- exact base and result commits;
- full diff or changed-file list;
- checks and commands run with outputs;
- environment and dependency versions relevant to the conclusion;
- exact input and output artifact digests;
- hostile-case results;
- unresolved failures;
- claim ceiling; and
- reconciliation against this contract and the current branch.

The final live receipt additionally preserves:

- source URLs, accessions, document and assertion digests;
- workbook input, candidate, manifest, and recalculation digests;
- work-order and runtime event identities;
- original proposal, block reasons, human amendment, new decision, and use disposition;
- Langfuse correlation identities without treating them as research evidence;
- restart retrieval evidence; and
- explicit nonclaims.

## Measurements and cold-review questions

Mechanical measurements:

- false admission on the controlled EX-99.1 proposal;
- false block on the permitted alternative target;
- number of unsupported workbook features;
- formula or reference changes outside the target;
- recalculation errors;
- exact descendants invalidated after correction;
- runtime cost and latency; and
- source, proposal, candidate, and trace population reconciliation.

Human questions:

1. Could the reviewer explain why the first proposal was blocked without reading technical records?
2. Did the source replacement and downstream-change view reduce work compared with checking the source and workbook from scratch?
3. Did the product hide any assumption or force the reviewer to trust a machine-owned classification they could not inspect?
4. Was the target-specific source rule professionally appropriate, too strict, or too weak?
5. Which workbook features or work habits make the bounded profile unusable?
6. Would the reviewer use this for another company or only for a purpose-built demo?
7. Should the next build deepen workbook support, source policy, research work, collaboration, or be killed?

## Nonclaims

Until the full live path and qualified-human review occur, this contract does not establish:

- support for a typical sell-side model;
- formula parity with desktop Excel;
- workbook compatibility beyond the declared profile;
- universal source admissibility;
- complete model information isolation;
- research quality or correct investment interpretation;
- analyst usefulness, adoption, or saved time;
- analyst approval of the product or policy;
- production deployment, security, or regulatory readiness;
- institutional release authority;
- a reusable Micron underwriting result;
- cumulative learning; or
- improvement caused by prompts, skills, agents, or feedback.

## Rollback

Every slice is additive and versioned. Before the live demo, rollback means disabling the new protocol and routes, leaving existing bound-work custody intact, and retaining failed experiment receipts. No migration may destroy existing chronology. No legacy page becomes evidence of success merely because the selected slice is killed.

If Slice 0 fails, stop all downstream work and adjudicate one of three paths:

- narrow the supported workbook contract with explicit professional cost;
- choose a different supported recalculation boundary or native artifact; or
- kill the Excel-companion hypothesis and return to product-form selection.

# Professional Interaction and State Contract V0

Every analyst-facing action must create, select, amend, invalidate, or authorise an exact professional object; runtime controls and backend status are not valid substitutes for professional interaction.

Status: joined interaction and canonical-state contract for the first model-change proof. This is not an implemented route specification or analyst-approved workflow.

## 1. Contract purpose

The previous product forms failed because they exposed system administration and epistemic machinery without giving the analyst one recognisable job and one obvious consequence. This contract starts from the analyst's work, then derives the canonical objects and transitions required to support it.

The contract is bidirectional:

- a visible action is rejected when no truthful backend transition and artifact consequence exist;
- a backend object is rejected when it enables no professional work, reconstructability, safety property, evaluation, or lawful operational boundary;
- a model proposal, deterministic host fact, and human judgment remain distinguishable at every step; and
- a completed machine run never substitutes for a professional result or permission to rely.

## 2. Professional interaction grammar

The product uses seven primary analyst acts:

1. **Begin or resume work.** State the event, question, model change, assumption, or decision being worked on.
2. **Confirm or correct meaning.** Dispose the system's bounded interpretation of the affected professional object.
3. **Authorise work.** Permit one exact professional consequence, not an agent topology or runtime operation.
4. **Resolve an exception.** Supply judgment only where deterministic facts or supported methods cannot safely complete the work.
5. **Review a candidate.** Inspect the professional delta, support, assumptions, consequences, and unresolved limits.
6. **Amend, reject, or permit use.** Create a new descendant or bind one exact candidate to one exact use.
7. **Resume and learn.** Reopen the same chronology and allow exact corrections to seed protected improvement experiments.

The host performs authentication, capture, planning policy, dispatch, retries, completion observation, custody, validation, recalculation, invalidation, trace collection, and evaluation execution quietly unless a failure changes the analyst's choices or the claim ceiling.

## 3. Authority vocabulary

The product must not collapse distinct acts into `Approve` or `Accepted`.

### Host fact

A deterministic fact issued from exact bytes, identity, time, adapter output, source capture, legal transition, calculation result, or access receipt. A host fact can still be wrong because software can have defects, but it is not a model assertion.

### Model proposal

An interpretation, plan, source classification candidate, method suggestion, research result, artifact operation, challenge, or explanation produced by a model under exact cognition and tool versions. It remains provisional.

### Human judgment

An attributed confirmation, correction, method authorisation, assumption, materiality decision, amendment, rejection, or permission to rely. Human judgment is scoped to the exact object and use recorded.

### Professional consequence

A changed or preserved artifact, changed research route, bounded refusal, invalidated descendant, new candidate, or exact permission state resulting from one legal transition.

## 4. Canonical object set and justification

The names below describe product semantics. Existing table names may remain internal during migration only where their semantics are not falsified.

| Canonical object | Owner | Why it exists | Visible professional consequence | Current support |
| --- | --- | --- | --- | --- |
| `Tenant` | Host | Enforces organisational isolation and policy scope | Analyst sees only their firm's work | Authentication and owner lookup exist; full tenancy is proposed |
| `Membership` | Host/admin | Attributes actors and roles within a tenant | Decisions and access are attributable | User identity exists; tenant role model is proposed |
| `ResearchJob` | Human-created, host-owned identity | Preserves continuing company or mandate context across events | Analyst resumes company work rather than creating another campaign | `ResearchCampaign` partially supplies this but also carries episode state |
| `JobObjectiveVersion` | Human intent, host version | Freezes objective, named use, cutoff, and artifact population for one undertaking | Analyst knows what this work is trying to change or decide | Campaign and run-spec fields exist; version separation is proposed |
| `WorkEpisode` | Host | Finalises one execution population without freezing the continuing job | Later work can continue after an immutable episode | Missing; campaign-wide correlation finality conflicts with ongoing work |
| `NativeArtifactVersion` | Host | Binds exact model or research artifact bytes and parentage | Original and every candidate remain recoverable | Exact uploaded bytes exist; descendant semantics are missing |
| `ArtifactManifestVersion` | Host adapter | Projects supported structure, formulas, names, styles, links, and errors | System can explain where the change occurs and what is supported | Mechanically demonstrated in spike only; not product state |
| `DependencyClosureVersion` | Host adapter | Binds every displayed consequence to an exact artifact relation | Analyst sees only consequences the system can reproduce | Missing |
| `ConceptualObjectVersion` | Model proposes; human confirms; host versions | Connects artifact structure to economic meaning and method | Analyst can correct what the system thinks the line, assumption, or structure means | Contracted, unimplemented |
| `MeaningDisposition` | Human | Separates meaning confirmation from value or artifact approval | `Confirm meaning`, `Amend meaning`, or `Reject object` | Missing |
| `MethodBindingVersion` | Model or human proposes; human authorises when required | Distinguishes reported fact, calculation, estimate, adjustment, assumption, or scenario | Analyst knows how the value is constructed | Contracted, unimplemented |
| `MethodAuthorisation` | Human | Records permitted method and assumption variants | System may use one exact method for this object | Missing |
| `SourceDocumentVersion` | Host capture | Makes source identity and exact bytes machine-owned | Analyst can inspect the exact source supporting the object | Uploaded bytes exist without source semantics; web capture missing |
| `EntitlementReceipt` | Host/runtime identity | Distinguishes lawful access from source truth | Access limits are explicit rather than invented negative evidence | Missing |
| `SourceAssertion` | Host extraction with model interpretation separate | Binds one passage or value to exact source bytes | Proposal can cite an exact assertion rather than worker-authored metadata | Missing |
| `SourcePolicyVersion` | Human policy, host version | Describes target-specific allowed source and authority variants | Correct-looking but inadmissible evidence can be blocked | Missing |
| `WorkPlanVersion` | Model proposal; human disposes when planning is material | Preserves alternative routes and stopping rules only when useful | Analyst can redirect material research before resources are spent | Planner path exists but is exposed as programme administration |
| `WorkUnitSpec` | Host compiler from authorised objective | Makes one bounded professional operation executable and judgeable | Analyst authorises the consequence once | `WorkOrder.packet` supplies a strong mechanical precursor |
| `CognitionPackageVersion` | Host release process | Joins exact prompt, role, skill, workbench, model, tools, and context policy | Later failures can be attributed to the exact harness | Protocol and skill digests exist; unified release object is proposed |
| `ExecutionEpisode` | Host/runtime | Preserves dispatch, acknowledgement, completion, and output evidence | Operational failure is diagnosable without becoming product authority | `WorkOrder`, `RuntimeEvent`, and `TraceLink` largely exist |
| `AgentProposal` | Model | Represents one exact proposed value, method, structure, or research update | Analyst reviews a professional delta, not arbitrary JSON | Generic proposals exist; typed host-reference contract missing |
| `AdmissibilityDecision` | Host validator | Separates known invalid state from professional ambiguity | Wrong source or unsupported operation is contained before mutation | Missing |
| `ProfessionalException` | Derived from exact facts and unresolved judgment | Creates a small interruption with explicit consequences | Analyst resolves only the material ambiguity or mismatch | Missing; current pages expose broad state instead |
| `CandidateArtifactVersion` | Host artifact service | Produces an exact provisional descendant from admitted operations | Analyst can open or download the actual changed artifact | Missing |
| `CalculationReceipt` | Host adapter/engine | Proves calculation attempt, results, errors, and supported dependency consequences | Displayed downstream changes are reproducible | Mechanically demonstrated outside product only |
| `Amendment` | Human | Corrects one exact ancestor without rewriting history | New proposal and candidate are attributable | Missing; current correction is free text in separate review app |
| `InvalidationEvent` | Host | Prevents stale descendants retaining use after ancestor change | Product states which candidate or use is no longer current | Missing |
| `ArtifactUseDisposition` | Human | Binds `USE`, `REJECT`, or `REQUEST_REWORK` to one exact candidate and use | Completion has a precise professional meaning | Missing |
| `CorrectionRecord` | Human act plus host context | Anchors failure evidence to the exact system choice and available cue | Analyst correction can improve later work without live mutation | Partial free-text custody exists in disconnected review path |
| `FailureAttribution` | Review/evaluation process | Routes failure to the responsible system layer | Improvement targets the cause rather than the visible symptom | Missing |
| `EvaluationCaseVersion` | Host/evaluation steward | Preserves trigger, expected behaviour, and protected comparisons | Revisions can be judged against real work | Candidate pool exists without exact job linkage or runner |
| `InterventionCandidateVersion` | Model or engineer proposes; host versions | Represents prompt, skill, tool, representation, validator, topology, or procedure change | No live change occurs merely because feedback exists | Quarantined future proposal partly exists |
| `EvaluationRun` | Host evaluation runner | Compares baseline and treatment under controlled conditions | Promotion claims have reproducible evidence | Missing |
| `HarnessReleaseVersion` | Authorised release process | Joins promoted cognition and deterministic controls with rollback | Exact runtime behaviour is reconstructable | Prompt/workbench/skill versioning exists separately; release join missing |

## 5. Interaction-to-state derivation

### Interaction 1 — Find or begin company work

**Analyst experience**

The analyst searches for a company, security, or mandate, or resumes recent work. They encounter the current objective, latest relied-upon artifact, unresolved professional exception, and one next meaningful action.

The analyst may begin with ordinary language such as:

- “Update the historical model after the annual filing.”
- “Revisit the inventory adjustment after management changed its definition.”
- “Work out whether this quarter changes the demand thesis.”
- “Add the new segment disclosure to the model.”

**Canonical state**

- `ResearchJob` selected or created;
- `JobObjectiveVersion` created with objective, named use, evidence cutoff proposal, and current artifact reference;
- `NativeArtifactVersion` selected or ingested;
- no work episode starts automatically.

**Authority split**

- analyst supplies objective and intended use;
- host owns job and artifact identity;
- model may suggest missing context but cannot silently finalise material scope.

**Validation and refusal**

- tenant ownership and artifact access;
- safe file type and byte bounds;
- unsupported artifact may be stored but not represented as understood;
- absence of required named use or cutoff remains a visible proposed field when material.

**Artifact consequence**

None. The original artifact remains unchanged.

**Evaluation signal**

Edits to the inferred objective or use become potential intent-recovery examples, not immediate prompt changes.

**Support today**

Authentication, owned job creation, exact upload, objective, decision use, and cutoff exist. The form wrongly asks the analyst to author the Codex instruction and requires source uploads before the system has recovered the job.

### Interaction 2 — Inspect the system's understanding

**Analyst experience**

The product states a bounded interpretation of the professional object in ordinary language and shows the relevant native-artifact location and declared consequences.

Example:

```text
I think this work updates Micron FY2025 consolidated revenue in USD millions.
The current value is 36,900. It feeds the displayed growth rate and revenue multiple.
This line appears to use reported annual GAAP revenue once the annual filing is available.
```

Actions:

- `Confirm`;
- `Correct this`;
- `This is not the change I mean`.

**Canonical state**

- `ArtifactManifestVersion` and `DependencyClosureVersion` contain host-inspected structure;
- model writes a `ConceptualObjectProposal` or proposed fields within `ConceptualObjectVersion`;
- `MeaningDisposition.CONFIRM_MEANING`, `AMEND_MEANING`, or rejection creates attributed chronology.

**Authority split**

- host owns bytes, addresses, formulas, and supported dependency edges;
- model proposes economic meaning and method;
- human confirms material professional meaning.

**Validation and refusal**

- proposed fields must reference host artifact objects;
- materially unknown or contested fields remain explicit;
- confirmation cannot imply source admission, method authorisation, candidate use, or investment judgment.

**Artifact consequence**

None. This interaction authorises a conceptual binding, not mutation.

**Evaluation signal**

The difference between proposed and confirmed meaning creates an exact representation-recovery case.

**Support today**

No product object or interaction exists. The current Casebook displays model-authored research state as if already meaningful rather than eliciting bounded confirmation.

### Interaction 3 — Confirm or change the method

**Analyst experience**

The system shows how the current or proposed value is constructed only when method matters:

```text
Method: reported annual fact
Allowed authority: filed annual report once available
Transformation: set the exact reported value
```

For an adjustment:

```text
Method: analyst adjustment
Components: reported restructuring charge less the recurring portion
Open question: whether the recurring portion should remain 20%
```

Actions:

- `Use this method`;
- `Change the method`;
- `Record an assumption`;
- `Leave unresolved`.

**Canonical state**

- `MethodBindingVersion`;
- `MethodAuthorisation` or attributed `AnalystAssumptionVersion`;
- invalidation of dependent work when method changes.

**Authority split**

- host owns exact calculation and source references;
- model may propose method classifications and transformations;
- analyst owns professional appropriateness and authored assumptions.

**Validation and refusal**

- assumptions require actor, rationale, scope, and change condition;
- reported facts cannot contain analyst-authored values;
- derived methods require complete parent references;
- unresolved method blocks any operation requiring it.

**Artifact consequence**

None until admitted work later creates a candidate.

**Evaluation signal**

Method corrections create method-classification and assumption-handling cases.

**Support today**

Workbench protocols discuss authority variants, but no joined target method object or human authorisation exists.

### Interaction 4 — Capture evidence and access

**Analyst experience**

The analyst adds a source, permits a supported connector, or uses already captured evidence. They see access limits only when relevant. They are not asked to populate source metadata manually.

**Canonical state**

- `SourceDocumentVersion` with exact bytes and capture metadata;
- `EntitlementReceipt` with operating identity and lawful route;
- `SourceAssertion` produced by deterministic extraction where possible, with model interpretation stored separately;
- `SourcePolicyVersion` already bound to the conceptual object.

**Authority split**

- host owns capture, bytes, source identity, time, and entitlement receipt;
- model proposes assertion interpretation and semantic fields not deterministically established;
- analyst resolves contested meaning or changes source policy.

**Validation and refusal**

- scheme, host, redirect, byte, content type, capture time, and tenant bounds;
- cutoff;
- source-identity consistency;
- unsupported extraction returns a bounded absence, not model-created identity;
- lack of entitlement is not evidence that the underlying fact is false.

**Artifact consequence**

None. Source capture changes the available evidence population.

**Evaluation signal**

Extraction disagreement, access failure, source-class correction, and policy amendment become cases.

**Support today**

Exact uploaded bytes exist. Source semantics, web capture, entitlement, and assertion objects are absent. Codex search can introduce uncaptured information.

### Interaction 5 — Authorise the work

**Analyst experience**

The product describes the professional consequence and material limits:

```text
Check the annual sources, propose the historical revenue update, and show the declared downstream changes. The original model will not be altered.
```

Actions:

- `Run this work`;
- `Narrow the work`;
- `Cancel`.

Planning appears only when multiple routes or material ambiguity justify it. It is stated as a choice about research work, not “authorise programme design”.

**Canonical state**

- optional `WorkPlanVersion`;
- exact `WorkUnitSpec` generated from confirmed conceptual object, sources, method, artifact, tools, budget, refusal conditions, and claim ceiling;
- human work authorisation;
- `ExecutionEpisode` and current `WorkOrder.packet` compiled from the authorised spec.

**Authority split**

- model may propose work and routes;
- host compiles exact identities and legal boundaries;
- human authorises the professional undertaking.

**Validation and refusal**

- required conceptual and source facts must exist;
- planned branches must have distinct evidence or context value;
- zero reasoning operators allowed unless a named defect justifies one;
- runtime entitlement checked separately from product login.

**Artifact consequence**

None at authorisation. Candidate state is created only after work returns and host admission succeeds.

**Evaluation signal**

Human narrowing, cancellation, route changes, and planner rejection create planning-quality cases.

**Support today**

Proposal disposition and exact work-order compilation exist. The analyst-facing page exposes operational start/readiness/send/collect controls instead of one professional authorisation.

### Interaction 6 — Work proceeds quietly

**Analyst experience**

The analyst may leave the page. The product reports a meaningful result, refusal, or material failure later. It does not require readiness polling or transport acknowledgement clicks.

**Canonical state**

- existing NTM/Codex lifecycle and `RuntimeEvent` chronology;
- work-order acknowledgement and output attestation;
- `AgentProposal`, refusal, or exact research artifact collected;
- post-custody diagnostic `TraceLink` when configured.

**Authority split**

- host owns dispatch, completion, custody, and runtime facts;
- model owns the candidate content under its exact cognition package;
- no human authority is implied by completion.

**Validation and refusal**

- exact packet, required reads, input population, output root and files;
- typed proposal shape referencing host identities;
- unknown runtime result remains unknown rather than success;
- trace cannot create authority.

**Artifact consequence**

Worker outputs enter provisional custody. The native artifact remains unchanged.

**Evaluation signal**

Timeouts, refusals, missing outputs, tool failures, and model proposals join the exact cognition package.

**Support today**

The runtime and custody spine largely exists. Typed professional proposals and closed source identity do not.

### Interaction 7 — Resolve a material exception

**Analyst experience**

The product interrupts because the system cannot lawfully or safely create a candidate. The message is anchored to the professional object and states whether the artifact changed.

Example:

```text
The proposed value is 37,378, but the proposal cites the September earnings release.
This model line is confirmed to use the filed annual report once it is available.
The October 10-K reports the same value. No workbook has been changed.
```

Actions and consequences:

- `Use the 10-K source` creates an attributed amendment and a new proposal;
- `Keep the current value` stops this change;
- `Correct what this line represents` creates a new conceptual-object version and invalidates dependent work;
- `Change the source rule` creates a new attributed policy version and requires re-evaluation.

**Canonical state**

- `AdmissibilityDecision.BLOCK`, `UNSUPPORTED`, or `JUDGMENT_REQUIRED`;
- derived `ProfessionalException` referencing the object, proposal, reason codes, affected dependencies, and artifact-mutation status;
- analyst action creates amendment, rejection, or new meaning/policy version.

**Authority split**

- host owns deterministic mismatch and unchanged-artifact fact;
- model may explain alternatives but cannot clear the block;
- analyst owns correction of meaning, method, or policy.

**Validation and refusal**

- exact source assertion and target policy comparison;
- separate permitted alternative target prevents universal source hierarchy;
- no candidate or calculation exists after a block.

**Artifact consequence**

None for a blocked proposal. An amendment may later produce a new admitted proposal.

**Evaluation signal**

The exact analyst correction plus the available cue becomes a source-admission, representation, or policy case.

**Support today**

Absent. The current mechanical wrong-source candidate is stored as provisional but not detected.

### Interaction 8 — Review a candidate artifact

**Analyst experience**

The product shows:

- the original and candidate model identity;
- target before and after;
- source or method;
- declared downstream formula, chart, or model changes;
- calculation engine and error state in ordinary language;
- remaining assumptions or unsupported features;
- named use awaiting decision.

Actions:

- `Use for [named use]`;
- `Amend`;
- `Reject`;
- `Open candidate in Excel` or download when supported.

**Canonical state**

- `CandidateArtifactVersion` with exact parent and admitted proposal set;
- `ArtifactManifestVersion` for candidate;
- `CalculationReceipt`;
- unresolved exception population;
- no use disposition yet.

**Authority split**

- host owns artifact bytes, operation lineage, engine result, errors, and dependency changes;
- model supplies explanation and interpretation within claim ceiling;
- human decides whether to rely for a named use.

**Validation and refusal**

- original untouched;
- only admitted operations applied;
- formulas and declared structure preserved;
- every displayed consequence bound to exact calculation output;
- any formula error or unsupported material feature refuses the candidate;
- candidate remains provisional after all machine checks.

**Artifact consequence**

One exact candidate descendant exists.

**Evaluation signal**

Amendment, rejection, hidden assumption reports, and review effort become candidate-quality and interface cases.

**Support today**

Missing. The current `job.html` prints arbitrary candidate JSON and can only download the worker result, not a changed native artifact.

### Interaction 9 — Amend and recalculate

**Analyst experience**

The analyst changes one source, assumption, method, meaning, or proposed operation and sees what the change invalidates.

The product states:

```text
This changes the authority for FY2025 revenue. The previous candidate and its use decision, if any, will no longer be current. A new model will be calculated.
```

**Canonical state**

- immutable `Amendment`;
- new conceptual, method, source policy, assumption, or proposal version;
- `InvalidationEvent` over descendants;
- new candidate and `CalculationReceipt` when supported.

**Authority split**

- analyst authors the amendment;
- host computes legal invalidation and artifact descendants;
- model may propose the downstream work but cannot rewrite ancestors.

**Validation and refusal**

- exact parent reference and actor;
- amendment scope;
- no in-place mutation;
- no reuse of stale calculation or use disposition.

**Artifact consequence**

A new descendant or a bounded refusal. The prior candidate remains historically available but no longer current.

**Evaluation signal**

Correction class, affected layer, and expected alternative behaviour are preserved.

**Support today**

Missing. The blind-review `CurrentCorrection` is free text and does not join to artifact mutation or recomputation.

### Interaction 10 — Permit or refuse reliance

**Analyst experience**

The final action names its scope:

```text
Use this candidate for the FY2025 historical model update
```

It does not say simply `Approve`.

Actions:

- `Use for [named use]`;
- `Reject`;
- `Request rework`.

**Canonical state**

- `ArtifactUseDisposition` referencing actor, tenant, job, exact candidate, calculation receipt, scenario, named use, rationale, and time;
- current job projection updates to show the latest relied-upon artifact for that use.

**Authority split**

- host checks legal preconditions and exact scope;
- human grants or refuses permission;
- model and telemetry cannot create this record.

**Validation and refusal**

- passing calculation receipt;
- no active blocker or invalidated ancestor;
- actor and tenant authority;
- exact named use;
- no transfer to another scenario, job, or artifact.

**Artifact consequence**

The candidate becomes relied upon only within the recorded scope. It is not globally true or published.

**Evaluation signal**

Use, rejection, and rework decisions become final candidate-quality outcomes, subject to selection-bias controls.

**Support today**

Missing. Proposal approval and accepted research state have different meanings and must not be reused.

### Interaction 11 — Resume and audit

**Analyst experience**

Reopening the company shows the current objective, latest relied-upon artifact, outstanding exception, and next work. Contextual history answers:

- what changed;
- which source, method, or assumption supported it;
- which artifact depended on it;
- what was corrected;
- who permitted use and for what;
- which later event invalidated it.

Raw packet, trace, and provider identities live behind support-only diagnostics.

**Canonical state**

- projections from immutable job, episode, artifact, conceptual object, source, work, correction, and authority chronology;
- no mutable summary is canonical.

**Authority split**

- host projects exact state;
- model may summarise within referenced facts;
- human decisions remain as recorded.

**Validation and refusal**

- projection reconciles populations and current descendants;
- stale projection refuses or refreshes;
- trace data cannot contradict canonical state silently.

**Artifact consequence**

None. Resumption selects current work.

**Evaluation signal**

Missing context, misunderstood resumption, and manual reconstruction effort become product-system cases.

**Support today**

Restart retrieval and exact artifacts exist. Continuing job projections and professional history do not.

### Interaction 12 — Correction becomes an improvement candidate

**Analyst experience**

The analyst corrects the current work. They are not asked to choose whether the failure belongs to a prompt, skill, tool, validator, or topology.

**Canonical state**

- `CorrectionRecord` anchors exact state, system choice, cue available at the time, analyst correction, impact, and scope;
- `FailureAttribution` is produced separately by review;
- `EvaluationCaseVersion` and possible `InterventionCandidateVersion` remain quarantined;
- held-out `EvaluationRun`, promotion decision, and rollback occur later.

**Authority split**

- analyst owns the correction;
- model may propose causal classification and intervention;
- host preserves inputs and runs comparisons;
- authorised product owner promotes or rolls back a version.

**Validation and refusal**

- correction must reference exact objects;
- model-authored metadata cannot become truth merely because it appeared in the original trace;
- single cases and model agreement cannot promote;
- protected cases and review-cost checks required.

**Artifact consequence**

The current artifact is corrected through the amendment path. The live harness remains unchanged until promotion.

**Evaluation signal**

This interaction creates the seed case by definition.

**Support today**

Review custody and inactive future proposals exist but are disconnected from the owned job, exact current artifact, comparison runner, promotion, and rollback.

## 6. Legal state transitions

The first product proof should derive state from immutable facts rather than mutable status fields.

```text
ResearchJob
-> JobObjectiveVersion
-> NativeArtifactVersion
-> ArtifactManifestVersion
-> ConceptualObjectVersion proposed
-> CONFIRM_MEANING | AMEND_MEANING | REJECT
-> MethodBindingVersion
-> AUTHORIZE_METHOD | LEAVE_UNRESOLVED | REJECT
-> SourceDocumentVersion + SourceAssertion
-> WorkUnitSpec authorised
-> ExecutionEpisode
-> AgentProposal | Refusal
-> PASS | BLOCK | UNSUPPORTED | JUDGMENT_REQUIRED

BLOCK or JUDGMENT_REQUIRED
-> Amendment | Reject | Correct meaning | Change policy
-> new proposal and new decision

PASS
-> CandidateArtifactVersion
-> CalculationReceipt PASS | REFUSE

CalculationReceipt PASS
-> Awaiting use decision
-> USE_CANDIDATE | REJECT | REQUEST_REWORK

Any material ancestor amendment
-> InvalidationEvent
-> prior descendant no longer current
-> new proposal, candidate, calculation, and use decision required
```

## 7. One complete Micron trace

This trace is a product-system test, not a claim about the investment case.

1. The analyst resumes Micron work and states: update FY2025 historical revenue after the annual filing.
2. The host stores the exact starting workbook and creates the objective version for an internal historical-model update.
3. The workbook adapter identifies `FY25_REVENUE_USDM`, the current value `36,900`, and declared dependent growth and revenue-multiple formulas.
4. A model proposes that the object means Micron consolidated FY2025 GAAP revenue in USD millions and uses the annual report once available.
5. The analyst confirms the meaning and method.
6. The host captures the September 8-K exhibit and October 10-K as separate exact source versions, each with a `37,378` assertion.
7. The analyst authorises the professional work: propose the annual update and show declared downstream effects without changing the original.
8. The exact work unit runs through NTM/Codex and returns the controlled proposal citing the 8-K assertion.
9. The host blocks the proposal because the confirmed source policy requires the available 10-K. No candidate exists.
10. The analyst chooses `Use the 10-K source`. An attributed amendment creates a new proposal referencing the 10-K assertion.
11. The host admits the proposal, creates a candidate workbook, recalculates it, and records growth and multiple changes with no errors for the supported closure.
12. The analyst sees the exact source, target change, downstream values, engine result, and named use. They choose `Use for the FY2025 historical model update`.
13. The use disposition binds that exact candidate and use. It grants no broader publication or investment authority.
14. Later, if the analyst says the line should use the earnings release for a rapid pre-filing scenario, that correction creates a new conceptual or policy version rather than rewriting the earlier history.
15. Review attributes the failure either to an incorrect target policy, incorrect recovered meaning, or controlled adversarial treatment. Only a protected comparison can change the live harness.

## 8. Product composition rules

- The primary surface follows one current professional objective, not system modules.
- No agent role, workbench, state schema, trace identifier, packet digest, or runtime status becomes primary navigation.
- Operational lifecycle appears only when failure changes analyst trust or action.
- A material exception is rendered in context, not as a global exception inbox unless repeated work proves such an inbox useful.
- History is contextual versions and decisions, not an undifferentiated activity feed.
- Technical records remain available for support, audit, and hostile testing but do not drive the product story.
- Richness comes from native artifacts, evidence, method, assumptions, consequences, and decisions rather than card count.

## 9. Implementation gate

This contract is coherent enough for hostile review but does not authorise construction.

Implementation authority remains premature because:

- the direct Excel-for-the-Web assumption test has not returned;
- typical workbook and entitlement behaviour remain unknown;
- no qualified analyst has tested the proposed interaction grammar;
- the conceptual contract has not been exercised against an adjustment or event-derived structural addition;
- the proposed job/episode split and object set have not been reconciled against migration cost; and
- a narrow vertical must be selected that implements frontend and backend consequence together.

No worker packet is issued by this contract.

# Evaluation and Harness Evolution Contract V0

A harness change may enter production only when an exact correction is causally attributed, converted into a versioned intervention, tested against the triggering case and protected different cases, and promoted with explicit scope and rollback.

Status: governing evaluation and harness-evolution contract for the model-aware research product. It is not an implemented evaluation service, a claim that current prompts improve research, or authority for autonomous self-modification.

## 1. Purpose

The product thesis includes cumulative improvement, but raw analyst feedback is not training data, a trace is not evidence of causality, and a successful correction is not proof that one prompt or skill should change.

The required loop is:

```text
exact analyst correction
-> causal failure classification
-> candidate change at the responsible layer
-> protected held-out evaluation
-> regression, integrity and review-cost check
-> scoped promotion or rollback
```

The current repository has useful fragments:

- exact job and work-order identity;
- version-pinned role, workbench, and skill bytes;
- candidate output and trace custody;
- blind first-pass review followed by reveal;
- free-text current correction;
- rubric or protected-evaluation candidate records; and
- inactive future prompt, retrieval, or workflow proposals.

Those fragments do not yet join one correction to the exact owned artifact, system choice, available cue, responsible component, comparison runner, promotion decision, or rollback.

## 2. Governing principles

1. **Correct the current artifact first.** Learning machinery must not substitute for producing the corrected descendant or bounded refusal needed by the current job.
2. **Preserve the cue available at the time.** A hindsight explanation cannot establish that the system could have chosen differently from the information it actually had.
3. **Route to the responsible layer.** Prompt editing is wrong when the defect belongs to source identity, artifact parsing, permissions, representation, validation, topology, or professional policy.
4. **Keep treatment and authority separate.** A model may propose a diagnosis and intervention; it cannot approve its own change or write a new production version.
5. **Protect different cases.** The triggering case alone rewards overfitting and ceremonial fixes.
6. **Measure analyst burden.** A safer workflow that restores exhaustive review can destroy the value proposition.
7. **Treat refusal as a valid outcome.** A candidate that refuses safely may outperform one that completes more work.
8. **Version everything that can affect behaviour.** Prompt, skill, workbench, tool, model, context policy, validator, representation, procedure, and topology are separate candidate surfaces.
9. **Promote narrowly.** Scope must name the jobs, objects, methods, artifacts, and conditions for which evidence exists.
10. **Rollback must be executable.** Every promoted release names its predecessor and the condition that restores it.

## 3. Exact correction capture

### 3.1 CorrectionRecord

A correction must bind the professional failure rather than store an isolated comment.

Minimum contract:

```json
{
  "schema_version": "correction-record/v0",
  "tenant_id": "<tenant>",
  "research_job_id": "<job>",
  "work_episode_id": "<episode>",
  "conceptual_object_version_id": "<object>",
  "source_or_method_ids": ["<exact ancestors>"],
  "agent_proposal_id": "<proposal or null>",
  "admissibility_decision_id": "<decision or null>",
  "candidate_artifact_version_id": "<candidate or null>",
  "calculation_receipt_id": "<receipt or null>",
  "cognition_package_version_id": "<prompt/skill/tool/model context>",
  "system_choice": "<what the system did or refused>",
  "cue_available_at_time": "<exact host facts and model-visible inputs>",
  "human_correction": "<attributed corrected meaning, method, source, operation, or decision>",
  "current_case_consequence": "<new artifact, rework, refusal, or no change>",
  "materiality": "<attributed judgment>",
  "scope_claimed_by_corrector": "<where the correction is believed to apply>",
  "actor_id": "<human>",
  "recorded_at": "<host time>"
}
```

The record stores references to exact objects rather than copying model-authored metadata into authoritative fields.

### 3.2 Correction types

The visible analyst correction may concern:

- intent or named use;
- artifact target identity;
- economic meaning;
- period, unit, basis, scope, or entity;
- source identity or source policy;
- method or assumption;
- calculation or dependency consequence;
- proposed value or structure;
- unresolved materiality;
- work plan or research route;
- explanation or interface burden;
- permission to rely; or
- an unsupported capability that should have refused earlier.

These are observations about the professional error. They are not yet causal system diagnoses.

## 4. Causal failure classification

### 4.1 FailureAttribution

A separate review process classifies the smallest responsible layer and preserves alternatives.

Minimum fields:

- correction record;
- candidate responsible layer;
- exact component version;
- failure mechanism;
- evidence supporting attribution;
- strongest rival attribution;
- counterfactual expected behaviour;
- intervention surface allowed to change;
- cases likely to be affected;
- confidence and unresolved discriminator;
- reviewer identity; and
- disposition `ATTRIBUTED`, `AMBIGUOUS`, `MIS-SPECIFIED_CASE`, or `NO_SYSTEM_CHANGE`.

### 4.2 Responsible-layer taxonomy

#### Professional intent and use

Failure: the system solved the wrong job or inferred a use the analyst did not intend.

Candidate intervention: interaction grammar, objective recovery, or confirmation procedure.

Not a prompt-only fix when the UI never elicited the distinction.

#### Representation

Failure: artifact structure, economic meaning, method, or authority could not represent a material distinction.

Candidate intervention: conceptual-model schema, projection, confirmation interaction, or migration.

Prompt prose cannot compensate for a missing canonical object or legal state.

#### Source capture and entitlement

Failure: source bytes, identity, access route, time, or assertion were absent, wrong, or unverifiable.

Candidate intervention: connector, capture adapter, entitlement policy, extraction, or refusal.

The research worker must not be asked to manufacture identity.

#### Deterministic validator or state transition

Failure: a known invalid state passed, a legal state was blocked, descendants were not invalidated, or authority was mis-scoped.

Candidate intervention: validator, policy representation, database constraint, transition, or hostile regression.

Prompt changes are causally irrelevant unless the host requires different output to exercise the gate.

#### Native artifact adapter or calculation engine

Failure: target, formula, dependency, formatting, export, calculation, or error state was lost or unsupported.

Candidate intervention: adapter, engine boundary, supported-profile rule, or refusal.

Do not tune the model to compensate for an unobserved or unreliable artifact operation.

#### Prompt or role protocol

Failure: under valid host facts and tools, the model misunderstood the task, violated a semantic boundary, overclaimed, omitted a required alternative, or failed to refuse.

Candidate intervention: role protocol version or task compiler.

A prompt candidate is eligible only after deterministic and representation defects are excluded.

#### Skill or workbench

Failure: a reusable reasoning or domain operation produced the wrong delta, ran ceremonially, or failed to run when eligible.

Candidate intervention: trigger, procedure, reference material, output contract, or retirement.

Package match proves identity, not causal value.

#### Tool grant or procedure

Failure: the worker lacked a necessary supported operation, used an unnecessary risky tool, searched outside the intended route, or followed an inefficient sequence.

Candidate intervention: tool permission, retrieval route, execution procedure, or budget.

#### Context and topology

Failure: shared context contaminated an independent check, fresh context lost necessary state, branch separation duplicated work, or reconciliation consumed the leverage.

Candidate intervention: context persistence, fresh-context boundary, branch structure, reviewer count, or consolidation procedure.

Agent count alone is never the intervention.

#### Model selection or budget

Failure: the exact model and budget were insufficient or wasteful after other layers were held constant.

Candidate intervention: model version, inference budget, timeout, or escalation rule.

#### Product interaction

Failure: the analyst could not understand what happened, supplied the wrong authority, or had to reconstruct the work because the visible consequence was incomplete.

Candidate intervention: interaction wording, information order, exception threshold, or native-artifact presentation.

A prettier rendering of the same implementation ontology is not an eligible fix.

#### No system change

The correction may reflect a one-off preference, later evidence unavailable at the time, changed mandate, or professionally contested judgment that should remain human-scoped. Preserving it does not require a harness change.

## 5. Intervention candidates

### 5.1 InterventionCandidateVersion

Every candidate names exactly one primary mutable layer and the other versions held fixed.

Required fields:

- attribution and triggering correction;
- intervention type;
- exact baseline component version;
- candidate component bytes or configuration;
- scope and trigger condition;
- expected behaviour change;
- expected review-burden change;
- likely regressions;
- evaluation case population;
- kill condition;
- rollback target;
- author and reviewer; and
- status `QUARANTINED`, `READY_FOR_EVAL`, `REJECTED`, `PROMOTED_SCOPED`, or `ROLLED_BACK`.

### 5.2 Candidate types

- `prompt_protocol`;
- `skill_package`;
- `workbench_contract`;
- `tool_grant`;
- `artifact_adapter`;
- `source_connector`;
- `conceptual_representation`;
- `deterministic_validator`;
- `state_transition`;
- `context_policy`;
- `agent_topology`;
- `execution_procedure`;
- `model_or_budget`;
- `professional_interaction`; or
- `no_change_record`.

A candidate that changes several primary layers cannot establish which change caused the result. Bundles require component experiments or an explicit statement that the bundle, rather than the component, is the unit under evaluation.

## 6. Evaluation case formation

### 6.1 Trigger case

The trigger case preserves:

- exact professional objective and named use;
- evidence cutoff;
- source and entitlement population available at the time;
- native artifact bytes and supported manifest;
- confirmed conceptual object and method versions;
- exact work-unit and cognition package;
- model, tools, context, and budget;
- system output and host decisions;
- human correction;
- expected legal and professional behaviour; and
- artifact consequence.

The expected behaviour is not necessarily the analyst's preferred final answer. It may be refusal, escalation, correct source selection, narrower claim, or a lower-burden interaction.

### 6.2 Protected held-out cases

The corpus must contain cases that the intervention author does not tune against. It should preserve:

- same failure family with different companies, documents, periods, and workbook structures;
- legitimate counterexamples where the previously blocked authority is permitted;
- adjacent workflows such as adjustment, estimate, structural addition, and earnings-derived change;
- cases requiring refusal;
- cases where the analyst correction should not generalise;
- different tenants or mandates where policy is allowed to differ; and
- negative controls whose current behaviour should remain unchanged.

The Micron wrong-source case must be paired with a target that legitimately permits an earnings release, non-GAAP measure, derived calculation, or analyst assumption. A universal `10-K good` intervention fails by construction.

### 6.3 Long-tail corpus from real work

Real work can produce a durable evaluation corpus without treating every trace as truth.

Eligible case seeds include:

- analyst corrections to proposed meaning;
- source replacements and policy amendments;
- model proposals blocked by deterministic reason codes;
- false blocks overturned through attributed policy or meaning correction;
- unsupported workbook or calculation refusals;
- formula, dependency, or round-trip losses;
- plan narrowing, route changes, and stopping decisions;
- candidate amendments, rejections, and scoped use decisions;
- later invalidations caused by changed evidence or assumptions;
- review interactions requiring excessive reconstruction;
- repeated manual corrections with similar available cues; and
- incidents where the product should have remained silent rather than interrupt.

A case becomes evaluation-grade only after host identities, artifact bytes, policy versions, cognition versions, and human correction reconcile. Model-authored source metadata remains a declaration and cannot become a reference answer without independent support or attributed human judgment.

## 7. Evaluation execution

### 7.1 Controlled comparison

Baseline and candidate run with the same:

- model unless model selection is the treatment;
- source and entitlement population;
- native artifact and manifest;
- conceptual object and method;
- cutoff;
- tools and permissions unless they are the treatment;
- context and topology unless they are the treatment;
- budget and timeout unless they are the treatment;
- work-unit specification; and
- deterministic host version unless it is the treatment.

Every difference is recorded. A candidate must not gain hidden access to post-cutoff facts, corrected outputs, another model's result, or human rationale unavailable to the baseline.

### 7.2 Required outputs

Each run returns:

- exact work result or refusal;
- host validation and reason codes;
- candidate artifact and calculation receipt where applicable;
- claim ceiling;
- resource use and elapsed time;
- trace references for diagnosis only; and
- complete cognition and tool version join.

### 7.3 Mechanical measures

- false admission rate;
- false block rate;
- invented or unknown host identity references;
- cutoff leakage;
- artifact-integrity failures;
- formula and dependency changes outside the authorised closure;
- calculation errors;
- stale descendant use;
- missing or over-broad authority;
- successful refusal under unsupported conditions;
- runtime failure, latency, and cost; and
- population reconciliation.

### 7.4 Professional measures

- correctness of recovered object meaning under human review;
- correctness and transparency of method classification;
- whether live alternatives and ambiguity were preserved;
- whether the result changed the next professional action appropriately;
- time required to understand and correct;
- proportion of work reconstructed manually;
- number and severity of unnecessary interruptions;
- trust calibration rather than confidence alone;
- candidate usability in the native artifact; and
- clarity of the exact permission being granted.

### 7.5 Review-cost measure

The intervention fails when it reduces a semantic error but increases total review or reconciliation burden enough to erase the agent leverage. Review cost includes:

- time to inspect sources;
- time to reconstruct calculations;
- time to correct meaning or method;
- time to compare original and candidate artifacts;
- number of context switches;
- number of system concepts the analyst must learn; and
- coordination cost across agent branches and reviewers.

### 7.6 Human review

A qualified reviewer judges exact objects, not prose summaries. Blind-first-pass review is useful when the exposure sequence matters. The reviewer must see the artifact, sources, method, proposal, consequences, and allowed authority appropriate to the question being judged.

Machine judges may assist with mechanical reconciliation or generate review candidates. They do not replace the qualified-human result when the evaluation claim concerns professional usefulness or judgment.

## 8. Promotion and rollback

### 8.1 PromotionDecision

Promotion requires:

- intervention candidate and baseline version;
- trigger-case result;
- protected held-out result;
- regressions and unresolved risks;
- artifact-integrity and security checks;
- professional review-burden result;
- exact scope;
- approver identity and authority;
- effective date or release condition;
- rollback target and trigger; and
- claim ceiling.

Possible dispositions:

- `REJECT`;
- `REVISE_AND_RETEST`;
- `PROMOTE_EXPERIMENTAL_SCOPE`;
- `PROMOTE_TENANT_SCOPE`;
- `PROMOTE_OBJECT_FAMILY_SCOPE`;
- `PROMOTE_GENERAL` only with broad evidence; or
- `ROLLBACK`.

### 8.2 HarnessReleaseVersion

A release joins exact versions of:

- task compiler;
- role protocol;
- selected skills;
- selected workbenches;
- model and budget policy;
- tool grants;
- context and topology policy;
- source and artifact adapters;
- conceptual representation;
- deterministic validators and transitions;
- analyst interaction version; and
- evaluation policy.

This join makes later failures attributable. A role file changed in place without a new release cannot be promoted.

### 8.3 Rollback

Rollback restores the named predecessor for the promoted scope and preserves:

- the failed release;
- affected cases and artifacts;
- reason for rollback;
- any use decisions requiring review;
- data migration or compatibility consequences; and
- a new evaluation candidate only when justified.

Rollback does not delete corrected professional history.

## 9. Preventing evidence laundering

The evaluation corpus is vulnerable when model-authored metadata is reused as reference truth. The following boundaries are mandatory.

### Host facts remain host facts

Exact bytes, URLs captured, timestamps, digests, workbook addresses, formulas, dependency edges, adapter outputs, calculation receipts, actors, and legal transitions come from host-owned objects.

### Model declarations remain declarations

Document class, economic meaning, source fit, mechanism, claim, uncertainty, and rationale authored by the model remain candidate fields until independently established or human-confirmed.

### Human corrections remain scoped judgments

A correction establishes what the reviewer judged for the exact object and use. It does not automatically prove a universal source rule, method, ontology, or prompt change.

### Traces remain diagnostic

Trace volume, model confidence, agent agreement, or presence of a reasoning step cannot establish that the result is correct. Traces may support causal investigation only when joined to exact inputs, outputs, tools, and decisions.

### Selection bias remains visible

Used candidates, rejected candidates, abandoned jobs, refusals, and unreviewed outputs must remain distinguishable. A corpus built only from accepted results cannot estimate false admission, false blocking, or burden.

### Post-hoc contamination is blocked

Evaluation cases freeze the evidence cutoff and information population. Later facts, the analyst correction text, and the expected result are not exposed to the baseline or treatment except where the evaluation tests an explicit correction-handling procedure.

## 10. Current prompt, role, skill, and workbench disposition

The existing prompt audit controls these decisions.

### `bound_work` — preserve the custody shell, replace the semantic envelope

Preserve:

- exact packet and required reads;
- input acknowledgement;
- candidate-or-refusal default;
- provisional-only authority;
- final artifact attestation; and
- refusal when native artifacts are unsupported.

Amend after host objects exist:

- require typed professional proposals referencing host-issued object, source assertion, method, operation, and artifact identities;
- prohibit arbitrary non-empty candidate JSON;
- remove `--search` for closed-source work or require captured retrievals before support;
- record exact claim ceiling and unsupported dimensions.

Evaluation status: the custody shell is retained; the semantic contract is not fit for the model-change product.

### `planner` — preserve conditionally, do not make it a universal stage

Preserve:

- decision hinge;
- rival routes;
- discriminating evidence;
- stopping and refusal conditions;
- independently disposable proposed work; and
- explicit human disposition before execution.

Amend:

- compile from the confirmed professional objective and conceptual objects;
- permit no planner for a direct bounded update;
- stop exposing programme administration as primary UI;
- require proposed branches to name distinct evidence, context, permission, or consequence.

Evaluate:

- planning quality, resource cost, branch usefulness, and analyst correction burden across ambiguous versus direct jobs.

### `research_worker` — preserve evidence discipline, amend its authority inputs

Preserve:

- cutoff;
- exact source passages where available;
- refusal;
- alternatives and uncertainty;
- append-only state when continuation is useful;
- bounded claim contribution; and
- no silent synthesis.

Amend:

- consume host-issued source versions and assertions rather than issuing receipts;
- consume confirmed conceptual and method bindings;
- return typed proposals tied to host identities;
- allow zero optional reasoning operators;
- record uncaptured external retrieval as unsupported rather than source authority;
- separate branch note from canonical state.

Evaluate:

- source fit, refusal, claim calibration, route choice, and review burden under active versus candidate protocol.

### `adversarial_review` — preserve fresh challenge, add typed consequence

Preserve:

- fresh context when independence is required;
- exact reviewed object;
- strongest counterexample;
- no silent repair;
- narrow impact and proposed next step.

Amend:

- challenge one exact conceptual object, source admission, proposal, candidate, or use request;
- output a typed challenge disposition and route;
- do not require a separate agent when deterministic checks or the analyst correction already resolve the issue.

Evaluate:

- incremental defect detection, false alarm rate, and reconciliation cost.

### `synthesis` — preserve as a conditional join, retire as a mandatory end state

Preserve:

- exact selected support set;
- contradictions and refusals;
- no claim strengthening;
- bounded decision implications and no-action conditions.

Amend:

- bind claims to host-issued evidence and conceptual objects;
- produce or update a professional artifact, not just `synthesis.md`, when the job requires one;
- distinguish continuing company state from one report.

Evaluate:

- only on jobs with genuine multi-branch support. It is not required for the first direct model-change proof.

### `judgment` — demote from product path to evaluation sidecar

Preserve:

- machine judgment is not expert judgment;
- exact sealed inputs;
- uncertainty and alternative considered;
- technical non-exposure remains a nonclaim.

Retire from primary analyst workflow. It should not appear as a mandatory research stage or product result.

Evaluate only where a machine baseline, blind comparison, or calibration study has a clear question and adequate isolation.

### Active workbenches — treat as candidate domain operations, not deterministic truth

Comparable State, Aggregate Driver, Expectation Surfaces, and Decision Consequence contain valuable domain distinctions and honest refusals. Preserve their protocols as candidate reasoning operations.

Do not present `COMPARABLE`, `IDENTITY_TIED`, `ROUTES_SEPARATED`, or related states as host facts unless typed inputs and validators implement the complete distinction.

Each workbench requires an evaluation contract naming:

- target professional question;
- exact inputs and host facts;
- candidate output and claim ceiling;
- deterministic checks actually implemented;
- analyst judgment required;
- baseline without the workbench;
- cases where the workbench should remain dormant; and
- kill condition.

### Research Frame skill — preserve version locking, evaluate programme contribution

Retain the ability to freeze the exact installed package and record invocation. Do not automatically activate it for every job.

Evaluate whether it changes a branch, discriminator, stop, refusal, claim ceiling, or analyst correction burden compared with direct planning. Package identity and prompt compliance do not establish value.

### Modes of Reasoning skill — remove mandatory ceremonial activation

Use only when one exact current object has a named defect, inspection boundary, mutable candidate output, expected delta, and kill condition.

Evaluate isolated effect. Agreement between modes or models is not evidence.

### Dormant DeepResearch suite — keep dormant until host and evaluation prerequisites exist

Do not activate the candidate suite as a bundle. Individual protocol changes may become interventions after:

- host-issued source and conceptual identities;
- typed review and correction transitions;
- protected evaluation cases;
- exact active-versus-candidate comparison; and
- no additional analyst-facing ontology.

## 11. Corpus governance and privacy

Evaluation cases inherit the tenant and source restrictions of the original job.

Required controls:

- case-level tenant and access scope;
- redaction or synthetic substitution before public release;
- source licensing and retention constraints;
- no cross-tenant use without explicit lawful basis and policy;
- exact separation of protected held-out cases from intervention authors;
- deletion or retention decisions for cloud artifacts;
- no credentials, tokens, service-issued private identifiers, or private analyst communications in public receipts; and
- public cases tied to exact commits and explicit nonclaims.

A consultancy may build a reusable private corpus across engagements only when contractual, confidentiality, and source-entitlement boundaries permit it. Otherwise, reusable learning is expressed as abstracted mechanisms, synthetic cases, and separately approved client-scoped versions.

## 12. Current support and implementation gate

### Implemented fragments

- exact work-order and cognition version identity;
- output and trace custody;
- blind first-pass review and later reveal;
- review correction text;
- rubric/evaluation candidate record;
- inactive future intervention proposal.

### Missing system

- exact correction joined to the current job and artifact;
- causal failure attribution;
- evaluation case construction;
- protected held-out populations;
- baseline-versus-candidate runner;
- review-cost measurement;
- promotion decision;
- harness release join; and
- executable rollback.

Implementation is premature until the product interaction and canonical object contract survive hostile review and one complete job can produce exact correction records. No evaluation worker packet is authorised by this document.

## 13. Definition of success

A hostile reviewer should be able to select one analyst correction and answer:

- Which exact artifact, conceptual object, source, method, proposal, and cognition version produced the failure?
- Which cue was available before the system acted?
- Which system layer caused or permitted the result?
- What candidate component changed, and what stayed fixed?
- Which trigger and held-out cases were run?
- Did false admission, false blocking, artifact integrity, review burden, cost, or latency worsen?
- Who promoted the change, for what scope, and with what rollback?
- Did the current case receive a corrected artifact independently of the harness experiment?

If any answer depends on a conversation summary, model-authored identity, generic score, or unversioned prompt, the improvement claim is not licensed.

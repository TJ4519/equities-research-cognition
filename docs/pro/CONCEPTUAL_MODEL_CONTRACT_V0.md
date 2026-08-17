# Conceptual Model Contract V0

A model change is valid only when the system can connect the native artifact location to the economic object, the method that produced the value, and the human authority governing its use.

Status: PRO-adopted representation contract for product discovery and later Slice 1 specification. It is not an implemented schema, an analyst-approved ontology, or a claim that a whole sell-side model can be understood automatically.

## Purpose

The contract prevents a convenient artifact handle from becoming a false theory of the analyst's model.

For example, `Model!B5` or the named range `FY25_REVENUE_USDM` can tell software where a value lives. It cannot establish that the value means Micron consolidated FY2025 GAAP revenue in USD millions, that a reported annual fact rather than an estimate belongs there, that the 10-K is required after filing, or that changing it is permitted for a named use.

V0 represents one consequential model-change object at a time. It must be small enough to confirm and test, but complete enough to explain why a proposal is legal, blocked, consequential, or unresolved.

## The five joined parts

### 1. Decision context

The decision context selects which parts of the model matter.

Minimum facts:

- job and exact starting artifact;
- issuer or security;
- analyst objective;
- named use of the resulting artifact;
- evidence cutoff;
- model-change beginning;
- actor who commissioned or confirmed the object; and
- unresolved professional question.

Allowed beginnings in V0:

- `update_existing_fact`: replace or refresh an existing reported or derived value;
- `adjust_method_or_assumption`: change an adjustment, estimate, allocation, scenario, or methodology;
- `add_model_structure`: add a new line, relationship, schedule, or calculation to an existing artifact; and
- `build_from_event`: create a bounded model addition or revision from an earnings or other public event.

These are entry conditions, not four products or mandatory workflow stages.

### 2. Artifact structure and dependencies

This part says where the object lives and what computation depends on it.

Minimum facts:

- exact artifact version and byte digest;
- artifact adapter and version;
- workbook, sheet, table, range, cell, or named target identity;
- current value or formula;
- data type, unit representation, style, and number format where material;
- relevant formula and chart dependencies;
- supported calculation engine and version requirements;
- unsupported-feature diagnostics; and
- allowed operation population.

V0 may represent a bounded dependency closure rather than every formula in the workbook. The closure must include every output shown as changed after the proposal.

Host-owned facts:

- bytes, digests, addresses, formula text, dependency edges, adapter version, and calculation receipt.

Model interpretation may suggest a relevant dependency. It cannot create the canonical edge without artifact inspection.

### 3. Economic meaning and relationships

This part says what the artifact object represents in the world.

Minimum facts when applicable:

- entity and exact entity scope;
- metric or modeled object;
- period and period kind;
- unit and scale;
- accounting or analytical basis;
- consolidation, segment, geography, product, customer, or channel scope;
- relationship to other economic objects; and
- live rival meanings when the artifact or evidence is ambiguous.

Example:

```text
entity: Micron Technology, Inc.
metric: revenue
period: fiscal year ended 2025-08-28
unit: USD millions
basis: GAAP
scope: consolidated
artifact target: FY25_REVENUE_USDM
```

The system must preserve `unknown`, `ambiguous`, and `contested` rather than forcing a complete binding. A proposal requiring an unconfirmed material field remains blocked or provisional.

Sources of this meaning may include:

- artifact labels and formulas;
- source documents;
- prior model metadata;
- model inference with stated uncertainty; and
- attributed analyst confirmation.

Only the host records the versioned binding. Only the analyst can confirm professional meaning when the evidence does not determine it.

### 4. Method, assumption, and evidence basis

This part says how the proposed or existing value was constructed.

Every target must name one authority variant:

- `reported_fact`;
- `issuer_recast`;
- `derived_calculation`;
- `estimate_or_forecast`;
- `analyst_adjustment`;
- `analyst_assumption`;
- `scenario_value`; or
- `unresolved`.

Minimum facts:

- exact source assertion, parent calculation, or attributed assumption;
- transformation or formula;
- methodology version;
- bridge, allocation, normalization, residual, or adjustment details;
- dependencies;
- rationale;
- uncertainty and claim ceiling;
- author for analyst-created content; and
- change-of-mind or invalidation condition.

Examples:

- A reported annual revenue value points to one host-captured source assertion.
- A non-GAAP adjustment retains each reconciliation component and its source or attributed assumption.
- A forecast records the method, input state, scenario, and author rather than pretending to be a source fact.
- A derived multiple records its exact numerator, denominator, formula, and parent versions.

A schema pass does not make a method professionally appropriate. It makes the proposal inspectable and gives deterministic software something exact to check.

### 5. Meaning confirmation and authority boundary

This part says which human acts are required and what they authorise.

Minimum facts:

- actor;
- exact conceptual object version;
- confirmation, challenge, amendment, or rejection;
- source and method variants permitted for this object;
- material ambiguities retained for judgment;
- named use, job, scenario, and artifact scope;
- rationale;
- timestamp; and
- invalidation rule.

The human acts remain distinct:

- `CONFIRM_MEANING`: confirms the bounded semantic binding, not the proposed value;
- `AMEND_MEANING`: creates a new binding version;
- `AUTHORIZE_METHOD`: permits an exact method or assumption variant for this object;
- `USE_CANDIDATE`: permits reliance on one exact recalculated artifact for one named use;
- `REJECT`: rejects the exact object or candidate without deleting chronology; and
- `REQUEST_REWORK`: creates a new proposed descendant.

A generic `approved` flag is insufficient because approval of meaning, method, research work, candidate artifact, and named use are different authorities.

## Minimum joined model-change record

The conceptual object can be expressed as one versioned record referencing separately stored host facts:

```json
{
  "schema_version": "model-change-concept/v0",
  "job_id": "<host job>",
  "starting_artifact_version_id": "<exact artifact>",
  "beginning": "update_existing_fact",
  "decision_context": {
    "objective": "Update FY2025 historical revenue and inspect declared downstream effects",
    "named_use": "internal model-update experiment",
    "evidence_cutoff": "2025-10-04"
  },
  "artifact_binding": {
    "target_id": "<host target>",
    "adapter_manifest_id": "<host manifest>",
    "dependency_closure_id": "<host closure>"
  },
  "economic_binding": {
    "entity": "Micron Technology, Inc.",
    "metric": "revenue",
    "period_end": "2025-08-28",
    "period_kind": "fiscal_year",
    "unit": "USD",
    "scale": 1000000,
    "basis": "GAAP",
    "scope": "consolidated",
    "status": "human_confirmed"
  },
  "method_binding": {
    "authority_variant": "reported_fact",
    "allowed_source_policy_id": "<versioned policy>",
    "transformation": "set exact reported value",
    "assumption_ids": []
  },
  "meaning_disposition_id": "<attributed confirmation>",
  "claim_ceiling": "The candidate may reproduce the configured reported historical value and declared dependent calculations only."
}
```

The model may propose this object. It may not issue its host identities, confirm its own meaning, or authorise use.

## How the contract handles the practitioner beginnings

### Existing-model update

The artifact binding already exists or can be reconstructed. The main uncertainty is whether the economic and method bindings still match the new evidence. This is the cleanest first falsification because before, delta, dependencies, and descendant can be compared.

### Model adjustment

The artifact target may be stable, but the method variant is the central object. The system must expose whether the adjustment is source-derived, analytically derived, or an attributed assumption, together with the methodology and invalidation condition.

### Model building or structural addition

The target may not yet exist. `add_model_structure` allows the system to propose a new bounded line or relationship. Human confirmation must cover its economic meaning and method before artifact mutation. The new structure then receives an artifact identity and dependency closure.

### Earnings or ad hoc work

`build_from_event` starts from an event and a decision question. The result may be a proposed update, adjustment, new structure, chart, or refusal. The conceptual object prevents an event summary from silently becoming model authority and lets the same provenance and correction machinery apply.

This demonstrates a shared model-change grammar without claiming a universal workflow sequence.

## Machine, host, and human authority

### Agent

May:

- interpret labels and formulas;
- propose economic bindings;
- compare evidence and methods;
- identify uncertainty;
- propose a value, method, or structure; and
- explain expected consequences.

May not:

- create source identity;
- declare artifact bytes or dependencies without host inspection;
- confirm contested economic meaning;
- author a human assumption;
- admit its own proposal; or
- grant permission to rely.

### Host

Owns:

- exact bytes, identities, versions, times, actors, and legal joins;
- source capture and assertion identity;
- artifact manifests and dependency projections;
- deterministic policy checks;
- calculation attempts and receipts;
- invalidation and state transitions; and
- immutable chronology.

The host cannot choose an investment interpretation or decide professional materiality.

### Human

Owns:

- confirmation or correction of professional meaning;
- permitted method and assumption variants;
- materiality and contested semantics;
- named use; and
- `USE | REJECT | AMEND` over the exact candidate.

## Invariants

1. A target address cannot stand in for economic meaning.
2. An economic label cannot stand in for an exact artifact identity.
3. A source assertion cannot stand in for a target-specific admissibility decision.
4. A deterministic pass cannot stand in for professional method approval.
5. A confirmed meaning cannot stand in for permission to use a candidate.
6. An amendment creates a new version; it never rewrites the worker proposal or prior artifact.
7. Any material change to artifact, economic binding, method, source, assumption, policy, or calculation invalidates descendant use.
8. Every dependent value shown to the user must trace to the exact candidate and calculation receipt.
9. `unknown`, `ambiguous`, `unsupported`, and `refusal` are valid states.
10. The contract expands only when a material case demonstrates a missing distinction.

## Cold tests required before implementation authority

A later implementation must prove at least:

- the same named artifact target receives different admission outcomes under two versioned economic or method bindings;
- a mechanically valid cell proposal is blocked when material economic meaning is unconfirmed;
- a legitimate non-GAAP, derived, or analyst-assumption target is not blocked by a universal filing rule;
- an adjustment retains author, method, rationale, and change condition;
- a structural addition receives meaning confirmation before artifact mutation;
- a correction creates a new candidate and recalculation rather than editing the old candidate; and
- use of one candidate for one named purpose does not authorise another artifact, scenario, or job.

## Evidence ceiling

This contract makes the missing conceptual layer explicit and supplies a bounded target for later implementation. It does not prove that an agent can reconstruct the layer accurately, that analysts will accept the representation, that the fields are sufficient for ordinary sell-side work, or that update-existing-workbook is the preferred commercial product.
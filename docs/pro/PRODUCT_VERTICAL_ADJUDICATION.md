# Product Vertical and Conceptual-Model Adjudication

Status: active PRO adjudication following the Slice 0 `PARTIAL` result and the user's centre-of-gravity correction. This document narrows earlier product selection. It does not authorise Slice 1.

## Decision

Updating an existing `.xlsx` remains the best current **falsification vertical** for the model-provenance thesis, but it is no longer treated as the best product proposition by default.

The broader experimental proposition is a **model-aware research and modelling companion** that can understand and govern consequential work across existing-model updates, model adjustments, model building, and post-earnings or ad hoc research. The first commercial vertical remains unselected until the conceptual-model burden and analyst utility of those beginnings have been compared.

The distinction is deliberate:

- **Best next falsification:** the smallest case that can disprove the mechanism or architecture quickly.
- **Best proposition:** the workflow with enough recurring value, user pull, and tolerable implementation burden to deserve a product.
- **Analyst-validated workflow:** a proposition that has survived use and judgment by relevant practitioners.

The repository currently has evidence only for the first category.

## Evidence from Slice 0

The workbook capability worker returned `PARTIAL` at commit `101b83272a473598069d4e14c02552cf48982c56`, reconciled into `agent/pro-grounding` by merge commit `3dc187ff47ba0d75eabf54be527bb527d049183f`.

The observed environment did support a bounded mechanical sequence:

- direct OOXML inspection;
- stable named-target resolution;
- one-cell patch from `36,900` to `37,378`;
- formula-cache invalidation without fabricated dependent values;
- non-interactive LibreOfficeDev recalculation;
- changed growth and mechanical EV/revenue results;
- preserved formula strings, named target, formats, and style semantics; and
- independent detection of an invalid formula as `#NAME?`.

The branch remained `PARTIAL` because the repository's mandatory LOC classifier attempted to decode the authorised binary `.xlsx` fixture as UTF-8. That is a support-tool integration defect, not evidence that the workbook mechanism failed.

The result establishes only a bounded artifact operation in one environment. It does not establish understanding of a sell-side model, production engine choice, typical workbook support, Excel parity, product usefulness, or the right first workflow.

## Real-surface correction

Read-only inspection by the coordinating agent established that the user's desktop Chrome session is authenticated to Excel for the Web and exposes `Create blank workbook` and `Upload a file`. No workbook was created, uploaded, opened, or changed during that inspection.

The PRO web surface cannot inherit that authenticated browser session. A direct attempt to open the Office Excel launch route reached Microsoft authentication rather than the user's session. Therefore the PRO cannot execute the cloud test itself from this surface and must delegate it under an exact packet.

This yields three separate claims:

1. Human interactive access to Excel for the Web is observed.
2. Reproducible Codex operation of one disposable synthetic workbook through that surface is untested.
3. Lawful and reliable commercial integration remains untested, including authentication, supported APIs, licensing, tenancy, automation, retention, and round-trip fidelity.

Excel for the Web is a candidate artifact adapter and reference surface. It is not the product and does not supply the conceptual model.

## Governing methodology

Before engineering or preserving a proxy, enumerate and test the real surfaces already available to the user.

For each candidate surface, record:

- how access is obtained and whose identity it uses;
- which exact synthetic artifact may be created or uploaded;
- which reads, edits, calculations, exports, histories, and errors are observable;
- which steps are interactive, automatable, supported, or merely possible;
- what exact evidence can be captured without exposing private account data;
- what fidelity survives round-trip export;
- what cleanup or retention action follows; and
- which product claims remain unsupported.

A proxy is retained only for a named capability the real surface cannot yet expose reproducibly. Its evidence must be labelled as proxy evidence.

## Candidate beginnings

### 1. Update an existing model

**Professional job.** Bring new reported facts, estimates, assumptions, or methodological changes into an existing model and understand the downstream consequences.

**Why it is a strong falsification.** It has an exact starting artifact, explicit changes, dependencies, source choices, recalculation, and a visible before/after result. The Micron equal-value wrong-source case tests whether the system can contain a semantically inadmissible proposal despite numerical correctness.

**Hidden assumption.** The workbook already contains a coherent model, stable targets, and enough recoverable meaning to know what a change represents. A named range or formula graph does not supply that meaning.

**Product risk.** Every client workbook may require expensive conceptual mapping before automation, making the product bespoke or shifting review burden back to the analyst.

**Current ruling.** Retain as the leading mechanism falsification. Do not treat it as the selected commercial vertical until the conceptual-model gate is exercised.

### 2. Adjust an existing model or scenario

**Professional job.** Change an assumption, methodology, scenario, or sensitivity and inspect how the model's conclusions respond.

**Why it may be commercially stronger.** Assumptions and scenarios are often already explicit objects of analyst judgment. The human can own the meaning and authority while the system manages exact versions, dependencies, recomputation, comparison, and reversal.

**Main risk.** The line between an attributed assumption and an agent-invented economic view can blur. A scenario result can look precise while resting on an incoherent or poorly scoped assumption.

**Discriminating question.** Can the system represent one analyst-authored assumption, its rationale and change condition, apply it to the correct model objects, recalculate, compare the exact descendant, and reverse it without converting the scenario into institutional truth?

**Current ruling.** Serious alternative to existing-model update. It should be compared before the product form is fixed.

### 3. Build a model

**Professional job.** Translate a company, industry, decision use, evidence, and analytical method into a new model structure, formulas, assumptions, and outputs.

**Why it may create greater leverage.** The agent can contribute to structure, extraction, calculation, documentation, and iteration before legacy workbook conventions constrain it.

**Main risk.** The conceptual-model problem is maximal. The system must decide what entities, relationships, drivers, accounting definitions, methods, and outputs belong in the model. A technically valid workbook can embody the wrong theory of the company or decision.

**Discriminating question.** Can an analyst inspect and correct the proposed conceptual model before spreadsheet generation without rebuilding the whole model mentally?

**Current ruling.** Plausible high-value proposition, but too broad for the first proof until the conceptual-model representation is credible.

### 4. Post-earnings or ad hoc research

**Professional job.** Answer a consequential question, reconcile disclosures, compare expectations and narrative, calculate a bounded result, and update a thesis, memo, table, or model input.

**Why it fits the current repository.** The existing planner, research-state, workbench, custody, and NTM/Codex machinery is closer to research than to workbook execution. This path may produce useful artifacts before deep spreadsheet support exists.

**Main risk.** A report or research state can become another provenance dashboard or dossier. The output must feed a recognisable next artifact or decision rather than expose the backend process.

**Discriminating question.** Does one bounded research episode reduce the analyst's work and produce a next-consumed artifact with inspectable support, or does the analyst still have to reconstruct the research from scratch?

**Current ruling.** Viable alternative vertical, especially if conceptual-model recovery makes workbook work too bespoke.

## Comparison criteria

A later selection must compare the beginnings on the same criteria:

| Criterion | Existing update | Adjustment/scenario | Model building | Earnings/ad hoc |
| --- | --- | --- | --- | --- |
| Practitioner-attested beginning | yes | yes | yes | yes |
| Exact native artifact | strong | strong | generated or evolving | variable |
| Controlled provenance failure | strong | medium to strong | possible but broad | strong |
| Recalculation/dependency proof | strong | strong | required | optional or downstream |
| Conceptual-model burden | high but bounded | medium to high | very high | medium |
| Immediate falsifiability | high | high | low | medium to high |
| Risk of bespoke implementation | high | medium | high | medium |
| Current repository leverage | medium | medium | low | high |
| Commercial usefulness evidence | absent | absent | absent | absent |

This table is an engineering and product inference, not practitioner validation.

## Conceptual-model contract

No workflow that changes or generates a model may proceed merely from workbook structure. Before Slice 1 or an alternative product slice, one exact conceptual-model contract must represent the following.

### Structural object

- exact workbook and manifest version;
- stable sheet, table, range, name, row, column, and cell identities;
- formulas, number formats, styles, comments, and dependency paths;
- unsupported or ambiguous workbook features; and
- exact parser and calculation boundary.

### Economic object

- issuer and consolidation scope;
- segment, product, geography, customer, channel, or other relevant dimensions;
- metric, period, unit, scale, accounting basis, and economic scope;
- operating or accounting relationships; and
- competing or unresolved interpretations where one mapping is not justified.

### Method and assumption

- reported, issuer-recast, derived, estimated, or analyst-assumption authority;
- exact formula or method;
- source and comparison policy;
- scenario or sensitivity semantics;
- rationale, author, change condition, and scope;
- residual or unresolved portion; and
- invalidation conditions.

### Confirmed meaning and authority

- proposed mapping from structural object to economic object;
- who or what proposed it;
- exact evidence supporting or contradicting it;
- human state `CONFIRM`, `AMEND`, `REJECT`, or `AMBIGUOUS`;
- effective job, artifact version, and named use;
- supersession and dependency consequences; and
- prohibition on treating model inference as analyst authorship.

The conceptual-model contract may be proposed by an agent and partially generated from workbook structure. It becomes authoritative for an operation only through an attributed human act or a deterministic fact that does not require professional judgment.

## Product form consequence

The earlier artifact-native companion selection is narrowed rather than erased.

- The common kernel may still own jobs, source and artifact versions, work orders, calculations, corrections, dependencies, and scoped use.
- The first specialised workspace remains open: model update, assumption/scenario work, model construction, or post-earnings research.
- Excel desktop, Excel for the Web, LibreOffice, or another engine may serve as an artifact adapter. None should determine the visible product or domain model.
- A durable research-job hub may eventually host several workspaces, but it cannot be the first product proof without one useful specialised job.

## Gates before Slice 1

Slice 1 remains blocked until all of the following are separately adjudicated:

1. **Real-surface assumption test.** A disposable synthetic workbook is exercised through the authenticated Excel-for-the-Web surface under `002_EXCEL_WEB_ASSUMPTION_TEST.md`.
2. **Proxy integration hygiene.** The binary fixture classifier defect is resolved under its own packet and mandatory checks pass, without allowing that result to select the production engine.
3. **Conceptual-model gate.** One representative model object is mapped across structural, economic, method, and authority layers, with exact unknowns and human-confirmation requirements.
4. **Vertical comparison.** Existing update is compared with at least adjustment/scenario and post-earnings research on expected analyst value and review burden.

A mechanical `PASS` on either Excel or LibreOffice cannot authorise Slice 1 by itself.

## Current claim ceiling

The strongest product claim is:

> Existing-model update is a useful controlled case for testing model provenance, native artifact change, recalculation, and exception review. The repository has not yet established that it understands an analyst's conceptual model, that Excel for the Web or LibreOffice is the correct production adapter, or that update-existing-workbook is the best commercial first vertical.

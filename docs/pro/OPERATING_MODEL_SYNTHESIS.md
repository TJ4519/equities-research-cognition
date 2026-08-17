# Operating Model Synthesis

The product should be organised around a governed model-change episode, not around Excel, agents, or provenance records.

Status: controlling product and operating-model synthesis after the Slice 0 workbook result and the user's centre-of-gravity correction on 17 August 2026. This document distinguishes the sell-side problem, the current repository's execution model, the Agentic SDLC donor patterns, and the role of native spreadsheet surfaces. It is not analyst validation or an implementation claim.

## 1. The sell-side problem and business case

The practitioner signal covers model building, model updating, model adjustments, earnings work, statistical analysis, visualisation, thesis consistency, management-narrative comparison, ad hoc questions, and institutional memory. These are observed uses from one sophisticated practitioner. They are not a validated universal workflow or permission to turn each item into a feature.

The common problem is not merely that an agent may type the wrong number. The more dangerous case is a plausible change that is locally convincing but wrong for the exact professional object and use. A value may be numerically correct while coming from the wrong document class, entity, period, unit, accounting basis, scope, methodology, scenario, or authority. A formula may calculate correctly while embodying an assumption the analyst did not intend. A model update may preserve cells and formulas while misreading what the model represents.

The economic logic is caused by scale:

```text
one useful agent-assisted method
-> more frequent use
-> more companies, periods, sources, transformations and collaborators
-> more plausible intermediate objects and downstream consumers
-> greater propagation distance for a local error
-> either exhaustive human reconstruction or a governed exception path
```

Exhaustive checking erases much of the leverage. Blind automation creates unacceptable propagation risk. The business opportunity is to preserve agent leverage and analyst autonomy while making consequential support, transformations, assumptions, corrections, dependencies, and permission to rely on one exact artifact reconstructable.

Model provenance is therefore not a citation panel. It is the ability to answer, for one consequential model change:

- What exact professional object was the analyst trying to change, and for what decision or use?
- What did the workbook contain before the change?
- What economic meaning did the target carry?
- Which exact source assertion, calculation, estimate, or assumption supported the proposal?
- Which method transformed the evidence into the proposed value?
- Which formulas, claims, charts, scenarios, and later artifacts depended on it?
- What did the agent propose, what deterministic checks admitted or blocked, and what remained professional judgment?
- What did the analyst confirm, amend, reject, or permit for a named use?
- Which exact descendant artifact resulted, and what changed after correction and recalculation?

### The conceptual-model layer

A named range or stable cell address supplies mechanical identity. It does not establish understanding. A serious model-change object needs four connected representations plus the decision context that selects them.

#### Workbook structure and dependency representation

This layer records the native artifact as a computational object:

- workbook, sheet, table, range, cell, chart, and named-range identity;
- values, formulas, formats, comments, links, and supported features;
- dependency edges and affected outputs;
- versions, byte digests, calculation engine, warnings, and errors; and
- allowed operations and preservation checks.

It answers where the change occurs and what recalculation can affect. It does not answer what the target means.

#### Economic entities and relationship representation

This layer records the world the model claims to describe:

- issuer, security, group, subsidiary, segment, product, customer, geography, channel, and counterparty where relevant;
- metric, period, currency, unit, scale, accounting basis, and consolidation or operating scope;
- economic relationships such as price, volume, mix, capacity, utilisation, inventory, bookings, costs, capital structure, and valuation inputs; and
- rival interpretations when one observation can arise from different mechanisms.

It answers what economic object a workbook element stands for. The representation is mandate- and use-conditioned rather than a universal ontology of equities.

#### Assumption and methodology representation

This layer records how the analyst moves from observations to model values:

- reported fact, issuer recast, derived calculation, estimate, forecast, analyst assumption, scenario, or sensitivity;
- transformation formula, bridge, allocation, residual, normalization, and source hierarchy;
- methodology version, rationale, dependencies, uncertainty, and change-of-mind condition; and
- distinctions between disclosed arithmetic, analyst interpretation, and model-implied output.

It answers how a value was constructed and which parts remain judgment rather than source fact.

#### Analyst-confirmed meaning and authority representation

This layer records who may decide what:

- who confirmed the target meaning and under which evidence cutoff;
- which sources, methods, and authority variants are permitted for that target;
- what ambiguity or materiality still requires professional judgment;
- whether an exact proposal or candidate is used, rejected, amended, or held provisional;
- the exact job, scenario, commission, and named use covered by the disposition; and
- what change invalidates descendants and requires a new calculation or decision.

It answers what the system may rely on and what remains the analyst's responsibility. No model output, schema pass, trace, or generic acceptance flag can create this authority.

### Why update-existing-workbook remains the best next falsification

Updating an existing workbook remains the strongest first *falsification surface*, but not a proven product centre.

It is preferable to first-pass model building because it supplies a before state, a bounded proposed delta, visible dependencies, and an exact descendant artifact. Those facts make wrong-source admission, formula propagation, correction, recalculation, review burden, and scoped use directly testable. Starting with full model construction would combine conceptual design, methodology selection, workbook generation, research quality, and artifact execution in one experiment; a failure would be hard to diagnose.

It is preferable to starting with model adjustments because adjustments often depend on contested methodology and analyst-specific judgment before the deterministic boundary is known. Adjustments remain important because they force the assumption and methodology layer to become real, but they are a later or parallel discriminator.

It is preferable to generic earnings or ad hoc research as the first native-artifact proof because those workflows can end in prose, charts, or one-off calculations without proving correction and propagation through an economically important model. Earnings work remains the best source of live events and repeated model-change episodes.

The selected vertical must therefore begin one step earlier than “patch this named range.” It must reconstruct a bounded conceptual slice from the starting artifact and evidence, expose uncertainty, and obtain analyst confirmation of the target meaning, method, and permitted authority before a model-change proposal can be admitted. The cold question becomes:

> Can the system understand and confirm enough of one consequential model-change object to contain a plausible wrong proposal, produce a corrected recalculated descendant, and reduce review below manual reconstruction?

A passing workbook engine test proves only one adapter capability. It cannot authorise the conceptual-model layer, source policy, product form, or analyst workflow.

## 2. How the current repository operates

The public repository is a real execution and custody substrate extracted from a broader competitor-research programme. Its strongest implemented capability is not multi-agent intelligence. It is the controlled movement of an exact owned job through an external Codex runtime into provisional artifact custody.

### Canonical host

Django and PostgreSQL own:

- authenticated users and director-owned jobs;
- exact input artifacts and SHA-256 digests;
- immutable run specifications;
- proposals, human dispositions, and work orders;
- NTM lifecycle events and exact command evidence;
- collected output bytes and attestations;
- accepted, challenged, and rejected research-state transitions;
- restart retrieval; and
- post-custody Langfuse trace joins.

The database is intended to remain canonical. Filesystem directories materialise exact inputs and collect outputs, but they do not create research authority.

### Codex subscription runtime

The product does not call a model API directly. It treats an operator-installed Codex CLI, reached through NTM, as an external cognition runtime. This lets the system use persistent subscribed Codex sessions while keeping job identity, approvals, output custody, and authority in the host application.

The functional path is:

```text
authenticated request
-> owned job, exact files and run specification
-> attributed proposal and approval
-> immutable work-order packet
-> frozen protocol, workbench and skill digests
-> allowlisted NTM spawn or add command
-> persistent Codex session or pane
-> tracked send of the exact packet
-> observed completion
-> sealed output directory and worker attestation
-> host validation and transactional artifact custody
-> human disposition and later restart retrieval
-> optional Langfuse readback joined after custody
```

Only the NTM adapter may spawn host processes. The host constructs a pinned Codex launch command, sandbox mode, model, working directory, telemetry attributes, and environment boundary. The worker writes only beneath the exact output root. The host checks required paths, identities, byte digests, output population, acknowledgement, and typed research-state invariants before storing artifacts.

### What “multi-agent” means here

Planner, research worker, adversarial review, synthesis, and judgment are semantic roles with separate protocols and output contracts. They are not necessarily five continuously running agents and should not become five visible panes in the product.

A split is useful only when it earns one of these benefits:

- a fresh context avoids contamination by prior conclusions;
- a persistent branch-local context preserves accumulated evidence;
- independent challenge requires non-shared inference;
- tools or permissions differ;
- outputs must be independently disposable; or
- measured parallelism reduces elapsed work without increasing reconciliation burden.

NTM supplies persistent sessions and pane lifecycle. Codex supplies the reasoning loop. The host supplies exact work, custody, and legal transitions. A role name or pane count is not evidence of independent evidence, better research, or product value.

### Current strengths and limits

The substrate already makes several failures debuggable: a worker can be shown to have received exact bytes and instructions; output tampering can be rejected; a provisional candidate can survive restart; and runtime observations can be correlated without becoming authority.

The semantic ceiling remains much lower. The worker authors many source receipts and semantic attributes. The bound candidate accepts any non-empty JSON object. Uploaded source labels do not close information access because current Codex launch permits search. The wrong-source mechanical candidate is preserved but not detected. The review application can record corrections but cannot apply them to an owned workbook and recompute descendants. The inherited Casebook exposes backend vocabulary rather than ordinary analyst work.

The repository should therefore be treated as a reusable host spine, not as the product or as proof that the current agent topology is correct.

## 3. What Agentic SDLC contributes

Agentic SDLC is best understood as a library of coordination patterns for making long-running model work resumable and inspectable. Its product domain is software development, so its stages and vocabulary must not be copied into sell-side research.

Its useful mechanisms are:

- a thin standing constitution with procedures loaded on demand;
- intent classification followed by a pruned recipe rather than a fixed maximum process;
- declared inputs, outputs, preconditions, tool grants, and writer ownership for each role;
- durable artifacts as the handoff between contexts;
- one run record showing which stages ran, were reused, failed, or were excluded and why;
- session reconstitution from exact artifacts rather than a conversational completion summary;
- human gates at consequential decisions;
- fresh review contexts followed by one reconciler; and
- reconciliation that forces plans and documentation to agree with implemented reality.

Its limits are equally important. Recipe guidance is model-mediated rather than deterministic. Much permission enforcement is deferred. Its filesystem artifact tree is its system of record, whereas this product already has stronger PostgreSQL custody. Its closed software-intent taxonomy, stage sequence, task vocabulary, and review fan-out do not describe analyst work.

### The consulting-company form factor

For a consulting company helping knowledge workers experiment with agents, the transferable form is not one universal multi-agent application. It is a governed pattern library with three separable layers.

#### Core execution and evidence spine

Reusable across domains:

- identity, tenancy, exact inputs, versions, immutable chronology, work orders, bounded runtimes, artifact custody, restart, observability, human decisions, evaluation candidates, rollback, and claim ceilings.

#### Domain and artifact adapters

Changed for each profession:

- native artifact adapters such as Excel, PowerPoint, documents, code, databases, or specialist systems;
- source connectors and entitlement rules;
- conceptual-model representations for the profession;
- domain workbenches, calculations, and refusal states;
- ordinary professional language and decision surfaces; and
- boundaries between machine-known facts, model interpretation, and expert judgment.

#### Engagement-specific experiment packs

Changed for each client or workflow hypothesis:

- one consequential job;
- a falsifiable value and risk thesis;
- treatment and counterexample cases;
- the smallest useful interface;
- bounded worker instructions;
- acceptance and kill criteria;
- evidence receipts; and
- questions that can produce go, revise, or stop.

This form lets the consultancy reuse implementation knowledge without pretending that one workflow ontology transfers unchanged between sell-side research, legal work, accounting, or other knowledge domains. A candidate behaviour becomes a reusable skill only after repeated cases show that the model-mediated transformation is stable and valuable. Deterministic identity, permission, arithmetic, admissibility, and legal-transition rules belong in software rather than in a skill.

## 4. Where the inherited demo sits

The first visible product encountered in the repository, the Investment Casebook, is below the product layer. It is a diagnostic rendering of research state, proposals, mechanisms, claim ceilings, runtime evidence, and human dispositions. It proves that the backend can expose its chronology. It does not prove that analysts recognise the work, that review is economical, or that the interface should organise itself around the harness.

The later bound-job page is narrower and more truthful: it shows exact inputs, one authorised Codex job, provisional output, and explicit nonclaims. It is closer to an execution receipt than to a sell-side product.

The retained role of both surfaces is internal:

- expose canonical facts during engineering;
- diagnose missing transitions and authority leaks;
- support hostile tests and restart verification; and
- help derive a specialised workspace.

The first product experiment should sit above this substrate as a model-change workspace in ordinary analyst language. It should reveal the model line, conceptual meaning, source or assumption, proposed delta, affected dependencies, unresolved judgment, corrected candidate, and exact use decision. The agent graph, work-order schema, trace identifiers, and research-state journal remain behind the surface unless they help diagnose a specific problem.

## 5. Native spreadsheet surfaces and the proxy rule

Excel is an economically important artifact surface, not the conceptual model and not necessarily the mature product shell.

Three claims must remain separate:

1. Human interactive access to Excel for the Web is observed in the user's authenticated desktop browser.
2. Reproducible Codex operation of a disposable workbook in that surface is untested.
3. Lawful, reliable commercial integration through supported authentication, APIs, licensing, tenancy, automation, and faithful round trips is untested.

The governing method is now:

```text
inventory the real surfaces already available to the user
-> test the least mediated surface with synthetic disposable data
-> record exactly what interaction, calculation, export and provenance are reproducible
-> use a proxy only for a capability the real surface cannot yet expose
-> label the proxy and preserve the gap
```

LibreOfficeDev demonstrated a useful bounded calculation proxy. It must not remain the default merely because it was convenient to automate. Excel for the Web must be tested first as the real available surface. Neither surface can establish the conceptual-model layer or product integration by itself.

## 6. Current adjudication

- The Slice 0 worker result is `PARTIAL`, not `PASS`. The bounded OOXML patch and LibreOfficeDev calculation evidence is retained as proxy evidence. The mandatory classifier failure remains unresolved.
- Update-existing-workbook remains the best next falsification because it gives a before state, a bounded delta, propagation, correction, and an exact descendant. It is not yet the best commercial proposition, an analyst-validated workflow, or the product centre.
- The product centre is a governed model-change environment whose conceptual-model layer connects workbook structure, economic meaning, assumptions and methodology, analyst-confirmed semantics, and scoped authority.
- Excel for the Web is the next direct-surface assumption test. It may use only a synthetic, plainly disposable workbook isolated from personal work. Existing personal workbooks are out of bounds.
- A narrow binary-fixture classifier repair is justified as repository hygiene, but it cannot promote the product or outrank the direct-surface test.
- Slice 1 remains blocked. A mechanical spreadsheet `PASS` cannot authorise source, target, proposal, or interface implementation without the controlling conceptual-model representation and the direct-surface result.
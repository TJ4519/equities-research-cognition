# Operating Model

The project is best understood as three nested systems: a sell-side work problem, a research-agent execution substrate, and a reusable consulting pattern for turning expert work into governed agent workflows.

Status: repository-grounded synthesis for product and consulting decisions. This document does not claim analyst validation or select a mature product form.

## 1. Sell-side modelling, agent leverage, and model provenance

### Practitioner beginnings

The practitioner evidence supports several beginnings rather than one validated workflow taxonomy:

- building a model;
- updating an existing model;
- making adjustments to assumptions or methodology;
- post-earnings and other recurring research;
- ad hoc questions, calculations, statistical analysis, visualisation, thesis checks, management-narrative comparison, and institutional memory.

These observations came from one sophisticated analyst. They establish that frontier models can already contribute across the work. They do not establish one universal analyst workflow, one interface, one agent topology, or one product feature per use case.

### The concrete modelling problem

A modelling error need not look wrong. An agent can find the correct-looking value in the wrong source for the particular model target. The mismatch may concern document class, entity, period, units, scale, accounting basis, economic scope, or the authority under which a value is being used. A non-GAAP metric, derived calculation, estimate, or analyst assumption may be legitimate for one target and inadmissible for another.

If the value enters a workbook, formula dependencies can carry it into growth rates, valuation outputs, charts, downstream research, and later agent work. Numerical plausibility therefore does not establish professional admissibility.

### The business case

The business case is produced by scale rather than by one bad answer:

1. an agent makes a workflow cheaper or faster;
2. the analyst runs it more often and across more companies;
3. more retrievals, transformations, handoffs, assumptions, and consumers increase propagation distance;
4. exhaustive human reconstruction consumes the speed gain; and
5. weak review allows a plausible error to become organisational fact.

The product opportunity is review by consequential exception rather than review of everything. The system should let the analyst inspect the few source choices, calculations, assumptions, or changes that could alter a material artifact or decision, while leaving routine lawful work reconstructable in the background.

### Model provenance is a chain, not a citation

A URL beside a cell is only source provenance. Model provenance is the governed chain from evidence to professional use:

```text
exact source bytes and machine-owned source identity
-> exact supported assertion
-> conceptual model object the assertion may inform
-> target-specific authority and admissibility contract
-> proposed operation
-> exact workbook or research-artifact version
-> recalculation or transformation receipt
-> downstream dependency changes
-> human correction or disposition
-> exact named use for which reliance is permitted
```

Each link answers a different question.

- Source identity answers which exact document was captured.
- An assertion answers what exact value or statement was extracted and where.
- The conceptual model answers what the analyst believes the workbook object represents.
- The target contract answers which sources, methods, assumptions, and scopes are permitted for this use.
- The proposal answers what the agent wants to change.
- The artifact version answers what bytes actually changed.
- The calculation receipt answers what was recomputed and what failed.
- The dependency record answers what else changed because of it.
- The human disposition answers whether this exact result may be used, rejected, or amended for a named purpose.

Prompts can improve proposals, and schemas can make them inspectable. Neither can establish source identity, professional meaning, or permission to rely. Host software should own exact identities, bytes, versions, known predicates, legal transitions, and chronology. The analyst should own contested meaning, assumptions, materiality, and authority for use.

### The missing conceptual-model layer

The workbook capability spike showed that a bounded `.xlsx` can be patched and recalculated in one observed environment. It did not show that the system understands an analyst's model. A workbook-defined name is a structural locator, not evidence that the system knows the economic meaning of the cell.

A usable conceptual-model layer needs four related representations.

#### Workbook structure and dependencies

This is a machine-readable projection of exact workbook bytes:

- workbook, sheet, table, range, name, row, column, and cell identities;
- values, formulas, number formats, styles, comments, links, and supported features;
- formula references and dependency paths;
- version and content digest; and
- parser, preservation, and calculation diagnostics.

This layer can establish that one cell feeds two formulas. It cannot establish that the first formula represents revenue growth or that the second is decision-relevant.

#### Economic entities and relationships

This layer represents the world the analyst intends the model to describe:

- company, consolidation boundary, segment, product, customer, geography, and channel;
- metric, period, unit, accounting basis, scope, and comparable-state relation;
- operating drivers and economic identities;
- expectation, scenario, valuation, and decision relationships; and
- distinctions that are unresolved, mandate-dependent, or deliberately absent.

The system should not declare one universal ontology of equities. It should preserve a versioned, analyst-confirmed projection for the exact job and artifact.

#### Assumptions and methodologies

This layer states how the model turns observations into values:

- reported fact, issuer recast, derived calculation, estimate, or analyst assumption;
- formula or method used;
- source and comparison rules;
- scenario and sensitivity definitions;
- residuals and unresolved parts;
- rationale, author, change condition, and effective scope; and
- what would invalidate or replace the method.

A formula is not the entire methodology. The same formula can express different professional claims under different definitions and assumptions.

#### Analyst-confirmed meaning and authority

This layer binds structural objects to professional meaning and records who confirmed what:

- the exact workbook object being interpreted;
- the proposed economic meaning;
- supporting and contradicting evidence;
- analyst confirmation, amendment, rejection, or declared ambiguity;
- permitted sources and authority variants;
- materiality and named decision use;
- version, scope, and supersession; and
- permission to rely on an exact descendant artifact.

Machine inference may propose this mapping. It may not silently turn its proposal into analyst-authored meaning.

### The product boundary

The mature product is not Excel, a provenance dashboard, a chat wrapper, or an agent graph. It is an ongoing modelling and research environment that joins native artifacts to professional meaning, bounded agent work, deterministic containment, exact corrections, and scoped authority.

Excel is one economically important artifact adapter. It should remain below the conceptual model, not define it.

## 2. How the current research-agent repository operates

### Canonical host

The executable repository uses Django and PostgreSQL as the canonical host. The host owns authenticated jobs, exact input bytes, immutable run specifications, proposals, work orders, runtime events, collected artifacts, research-state transitions, human dispositions, and restart retrieval.

The database is the authority for chronology and ownership. Files are native artifacts, frozen worker inputs, outputs, or exported evidence. They are not a replacement for canonical product state.

### Cognition runtime

NTM is an operator-installed session manager. It creates or addresses persistent Codex CLI sessions. Codex is the cognition runtime. The repository does not call a separate paid model API or implement a second Python agent loop.

The runtime sequence is approximately:

```text
authenticated user creates or authorises work
-> host creates an immutable proposal and work order
-> work order freezes role protocol, selected workbench or skill, exact inputs,
   output contract, cutoff, decision use, and provisional authority
-> NTM creates or addresses one subscribed Codex session
-> host sends the exact work-order packet
-> Codex reads the frozen required files, performs bounded work, and writes only
   beneath the exact output root
-> host observes completion, seals the output population, verifies hashes and
   semantic envelopes, and stores exact artifacts
-> human accepts, challenges, rejects, replans, or later combines candidate state
-> Langfuse observations may be joined after custody for diagnosis
```

The Codex subscription belongs to the operating identity that launches the CLI session. A Django login does not confer Codex entitlement. The present arrangement is appropriate for founder-operated experiments; a third-party product cannot safely multiplex the founder's local authenticated session. A commercial deployment would need isolated runtime identities, explicit licensing, tenant boundaries, and a supported execution route.

### Multi-agent design

The repository describes semantic roles rather than proving that five or six concurrent agents are optimal:

- planner: proposes a discriminating research programme;
- research worker: performs one bounded branch through one primary workbench;
- adversarial reviewer: attacks one named candidate state without repairing it;
- synthesis: combines an exact selected support set while preserving contradictions;
- judgment: emits a bounded machine judgment candidate, never expert authorship; and
- bound work: performs one exact job and returns a provisional candidate or refusal.

Different roles earn separate contexts when independence, context economy, permissions, different evidence, or a materially different objective justifies the split. Agent count is not evidence count. One capable Codex session plus a host gate is preferable when it produces the same professional result with less coordination burden.

The host currently supports planner re-entry from one accepted research-state transition. Candidate prompts describe richer DeepResearch behaviour, but they are dormant and contain named host gaps. Prompt prose does not make those transitions real.

### Workbenches and skills

Workbenches are versioned domain operations, not visible analyst stages. Current examples address comparable-state reconstruction, aggregate-driver attribution, expectation surfaces, and a decision-consequence map that presently refuses because decision authority is missing.

Two external cognition skills are locked by exact package manifests. One helps frame the decision, target construct, proxy gap, rivals, and discriminating evidence. Another attacks a named reasoning defect. The host verifies their exact installed bytes before work. This proves version custody, not that the skill improved the research.

### What the repository already proves

It has a credible mechanical spine for:

- authenticated ownership;
- exact input and run-specification custody;
- bounded work-order compilation;
- allowlisted NTM command shapes;
- Codex acknowledgement and provisional output;
- hostile tamper rejection;
- restart retrieval;
- append-only chronology across important paths; and
- post-custody Langfuse correlation.

It does not yet prove semantic source admission, conceptual-model recovery, ordinary sell-side workbook support, analyst usefulness, complete multi-agent research quality, production deployment, or cumulative learning.

## 3. Agentic SDLC as a pattern library for the consulting company

### What the donor system is

Agentic SDLC is a Claude Code software-delivery harness. It uses a thin constitution, intent classification, recipe-guided stage selection, role contracts, durable artifacts, run records, session reconstitution, risk-scoped review, and human gates.

Its software-development taxonomy is not a sell-side product design. Its value is that it makes reusable coordination patterns legible.

### Patterns worth carrying into knowledge-work engagements

The consulting company can treat these as a library of mechanisms rather than a platform to install wholesale.

#### Durable commission

Preserve the professional objective, decision use, evidence cutoff, starting artifacts, costly errors, and authority boundaries in one exact commission. A fresh model should not have to infer the job from conversational history.

#### Bounded work packet

Turn one independently disposable unit of work into an exact artifact that names inputs, tools, permissions, outputs, refusal conditions, resource bounds, tests, nonclaims, and return evidence. The packet becomes both durable coordination state and the worker instruction.

#### Native-artifact adapter

Use the worker's real artifact: workbook, document, case file, codebase, data model, slide deck, or research memo. Test real available surfaces before building a proxy. Record what can be read, changed, recalculated or transformed, exported, and independently verified.

#### Conceptual-model map

Recover what the artifact means in the expert's work. Link structure to domain entities, relationships, assumptions, methods, uncertainty, and authority. Keep inferred meaning separate from expert-confirmed meaning.

#### Hard, human, and optional inputs

Classify every important input as:

- hard host fact: must exist exactly or the operation refuses;
- human-supplied judgment: attributed, scoped, revisable, and never silently inferred into authority; or
- optional context: may be absent only through a named degraded path.

#### Deterministic gate

Put a rule in code when code can decide it: identity, bytes, dates, paths, units, exact source class, arithmetic, dependency, output population, permissions, and legal transitions. Do not ask a prompt to police a known invalid state.

#### Exception workspace

Surface professional work, not the backend. Show the exact proposed change, support, consequence, unresolved judgment, and available action. Hide agent topology unless needed for debugging.

#### Scoped disposition

Record `USE`, `REJECT`, or `AMEND` against one exact artifact, job, scenario, and named use. A generic acceptance flag is too broad.

#### Correction-to-evaluation path

Bind an expert correction to the exact state and cue that caused it. Convert it into a protected evaluation candidate, then a versioned prompt, skill, tool, or gate experiment with a rollback condition. Do not update live behaviour directly from a click or edit.

#### Reconstitution

Let a fresh PRO or Codex session rebuild from exact commits, canonical object identities, decisions, receipts, and the active packet. The user should not carry messages between agents.

### Consulting form factors

These mechanisms can produce several client forms.

- **Artifact-native companion:** keeps the professional artifact in place and adds governed agent work, exceptions, lineage, and scoped use around it.
- **Specialised job workspace:** gives one recurring job its own recognisable surface while sharing a common custody and execution kernel.
- **Integrated domain workspace:** owns the artifact and the surrounding research interaction when replacing the native tool is justified.
- **Invisible automation plus exception inbox:** performs routine work in the background and exposes only consequential exceptions and exact receipts.
- **Capability pack:** combines skills, adapters, evaluations, runbooks, and workshops inside the client's existing tools before a standalone product is warranted.

The first engagement should not assume which form is correct. It should test one consequential job, one native artifact, one controlled failure, one exact correction, and one measurable review burden.

### A consulting delivery sequence

```text
observe one expert job and its native artifact
-> reconstruct the conceptual model and costly errors
-> identify the smallest useful agent contribution
-> test real available tool surfaces before proxies
-> bind work into exact packets and host facts
-> implement deterministic containment for known invalid states
-> run one controlled failure and recovery
-> measure usefulness, review burden, cost, latency, false admission, and false block
-> turn recurring corrections into protected evaluations
-> retain, narrow, change form, or kill
```

This sequence lets the company sell a credible experiment rather than a generic agent platform. The reusable asset is the pattern library and the evidence discipline; the client-specific asset is the conceptual model, artifact adapter, policies, evaluations, and interaction around the chosen job.

## 4. Placement of the inherited demo and the current product hypothesis

The first inherited product surfaces were not mature product forms.

- The dossier or Casebook exposed backend research-state language and agent machinery as analyst work. It was rejected because the analyst had to learn the system's ontology.
- The spreadsheet review mock-up showed a plausible interaction but did not open, change, recalculate, or return an Excel workbook.
- The current repository is a strong custody and execution substrate, not a finished analyst product.

The existing-workbook update remains a useful first falsification because it forces the system to connect source identity, target meaning, artifact mutation, recalculation, dependency change, correction, and scoped use. It is not automatically the best commercial proposition. It assumes an existing workbook, a stable target, and enough conceptual meaning to govern the change.

The broader product hypothesis is now a model-aware research and modelling companion. Existing-model update, model adjustment, model building, and post-earnings research are candidate first verticals within that hypothesis. A product decision must compare their immediate usefulness, conceptual-model burden, recurring frequency, consequence of error, review cost, and ability to produce a cold falsification.

The workbook spike and the Excel-for-the-Web assumption test are artifact-adapter experiments below that decision. Neither Excel nor LibreOffice defines the conceptual model or the mature product.
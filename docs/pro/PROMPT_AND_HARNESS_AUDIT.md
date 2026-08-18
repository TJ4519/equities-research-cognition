# Prompt and Harness Audit

Status: active-cognition and execution-boundary audit at governing commit `c1fc568424facbb5bb8e1b6369d30a1f380ae308`, read through PRO working branch `agent/pro-grounding`.

This audit separates what prompts request, what schemas make legible, what the host proves, and what still requires analyst judgment. It does not recommend a wholesale prompt rewrite.

## Active execution contract

The active host does not send a free-form role prompt assembled at runtime. It sends one canonical work-order JSON packet. That packet binds:

- campaign, proposal, work-order, and logical-role identities;
- proposal digest;
- protocol name;
- decision use and evidence cutoff;
- exact task and contract;
- output root, required paths, attestation path, and write policy;
- absolute paths and SHA-256 digests for required role, workbench, and skill reads;
- exact input artifact identities, digests, media types, and materialised paths;
- exact accepted research-state inputs when present; and
- provisional-only outcome authority for bound work.

The worker is required to read the role protocol, selected workbench protocol, and selected reasoning skill before work. Launch re-derives those reads, verifies local protocol and workbench bytes, recursively verifies each selected installed skill package against `skills/lock.json`, and refuses changed cognition.

The active role protocols live under `agents/`. The larger suite under `prompts/deepresearch/` is explicitly dormant and is not referenced by the runtime packet compiler.

## What the current prompt layer does well

The active prompts consistently preserve several useful distinctions:

- task completion is not truth;
- a schema is not authority;
- a worker result is candidate state;
- missing evidence and refusal are valid outputs;
- one source origin copied across several surfaces is not independent evidence;
- a comparable fact is not a causal explanation;
- a tied revenue identity is not demand or pricing power;
- consensus is not a universal market expectation;
- model agreement is not validation;
- machine judgment is not analyst judgment; and
- output attestation must be written last over exact final bytes.

The planner begins from a decision hinge, target construct, proxy gap, rival mechanisms, discriminator, and source surface. The research worker preserves a cutoff, source receipts, observations, competing mechanisms, uncertainties, claim ceilings, route decisions, and no-action conditions. Adversarial review is prohibited from silently repairing the candidate. Synthesis is prohibited from strengthening claim status. Judgment explicitly admits that requested context separation is not proof of technical non-exposure.

These are useful behavioural constraints. They do not close the known semantic gap.

## Responsibility matrix

### Deterministically host-owned today

The host currently owns and checks:

- user authentication and campaign ownership;
- exact uploaded bytes and SHA-256 digests;
- campaign, proposal, run-specification, work-order, role, and artifact identities;
- evidence cutoff value carried into packets;
- exact protocol, workbench, and skill versions;
- legal proposal and research-state transitions;
- exact accepted-state parentage for follow-on work;
- work-order input materialisation;
- output location, file population, byte size, and attestation;
- bound-run acknowledgement identity;
- candidate-versus-refusal envelope;
- append-only state prefix and epistemic-delta reconciliation;
- selected internal W1/W2 result shapes and arithmetic invariants;
- NTM command allowlist and exact runtime event capture; and
- post-custody Langfuse identity correlation.

### Model-declared today

The model currently declares, without an independent host source of truth:

- document class and source authority;
- source name, origin group, URL or path, locator, publication date, and exact passage;
- entity and reporting scope;
- metric definition and accounting basis;
- period and units;
- whether a passage actually supports an observation;
- source-to-target admissibility;
- whether two records are semantically comparable beyond the limited host shape checks;
- the meaning of a residual, uncertainty, mechanism, claim, and decision consequence;
- the complete contents of an arbitrary bound candidate object; and
- whether any unobserved information source influenced the result.

### Analyst-owned by design

The analyst should continue to own:

- contested source meaning;
- assumptions and estimates;
- materiality;
- whether an ambiguity is tolerable for the named use;
- correction of professional interpretation;
- action or no-action choice; and
- permission to rely on one exact recalculated artifact for one exact use.

The missing architecture is not a machine replacement for those judgments. It is a machine-owned substrate that prevents known invalid states and presents the remaining judgment in a precise, low-burden form.

## Critical mismatches

### 1. The declared source boundary is not enforced

The job form asks for “Sources Codex may use,” and the bound protocol says to work from the exact work order and supplied inputs. The generated Codex launcher unconditionally includes `--search` for every protocol.

No network or retrieval ledger constrains search to approved domains, records fetched bytes, or binds a web result to a host-issued source version. The packet establishes which uploaded files are in custody; it does not establish that those were the only information sources used.

For the first falsifiable demo, either web search must be disabled for a closed uploaded-source case or every external retrieval must pass through a host-owned capture boundary before its content can support a candidate.

### 2. Bound output acknowledges inputs but does not cite them

`run-acknowledgement.json` proves that the worker names the exact input population. `outcome.json` can then contain any non-empty JSON object.

The host does not require:

- a target ID;
- source-version IDs;
- source assertion IDs;
- exact locators;
- transformation IDs;
- assumption IDs;
- proposed artifact-operation type;
- dependency consequences; or
- a reason for admissibility.

The deliberate wrong-source test therefore succeeds exactly as designed. Semantic acknowledgement proves which job was attempted, not which source supported which target.

### 3. Worker-authored receipts are treated as evidence-shaped objects

The research worker is instructed to record rich source receipts. `research_state.py` verifies their field population, dates, access state, and internal references. It does not verify those fields against exact captured source bytes.

A worker can state that a passage came from a filing, assign an origin group, or report a publication date without any host-owned object that can confirm the claim. The Casebook then renders those declarations under “New evidence” without distinguishing machine-captured source facts from worker interpretation.

The next host seam must replace free-standing receipt identity with host-issued source-version and assertion references. The model may propose classification and interpretation, but it cannot issue the identity that later validates its own proposal.

### 4. Workbench contracts exceed executable validation

Comparable-State V0 describes a demanding contract over source-artifact digests, exact observation records, definitions, scopes, periods, units, bridges, assertions, assumptions, and residuals. It also states that no standalone validator is shipped.

The active host's W1 validator checks a much smaller projection: workbench identity, status, claim ceiling, referenced receipts and observations, selected authority label, required observation references, and a zero residual for `COMPARABLE`. It does not reconstruct or compare the complete target dimensions described by the protocol.

W2 and W3 likewise contain richer narrative requirements than the generic host research-state schema can prove. A protocol can tell a capable model to preserve these distinctions; it cannot make `COMPARABLE`, `IDENTITY_TIED`, or `ROUTES_SEPARATED` a deterministic fact unless the host has the corresponding typed inputs and validator.

### 5. Reasoning-operator activation is structurally mandatory

The semantic DeepResearch design says a role should use zero or one defect-triggered reasoning operation. The current host requires every `research_worker` proposal to select exactly one reasoning operator. Planner programme approval also automatically selects Research Frame.

This can reward ceremonial operator use: a proposal may invent a failure test so that the schema is satisfiable even when direct work would be cleaner. The host should permit zero operators, require an operator only when a named current defect justifies it, and preserve the resulting eligibility, delta, or kill result.

This is downstream of the source-admissibility seam. It should not become the first build merely because it is easy to test.

### 6. Sandbox custody is not complete information isolation

Codex starts in the exact output directory under `workspace-write`, but the packet and protocols themselves acknowledge that this does not prove complete read isolation. Required input and cognition paths are absolute paths outside the output root. `--search` enables additional retrieval.

The current architecture can prove where the worker was allowed to write and which declared inputs were materialised. It cannot prove that the worker read only those inputs or that a machine-judgment context was technically blind to other state.

Independence claims must remain nonclaims until a stricter filesystem and network boundary or an independently controlled execution environment exists.

### 7. Trace finality and campaign evolution are not one lifecycle

After Langfuse correlation, `collect_artifacts` refuses further collection because correlated campaign custody is final. The work-order approval path does not visibly refuse creation of a later order after correlation.

This creates a possible dead end: a campaign may gain a later approved order whose result cannot be collected under the finalised correlation rule. Either correlation must attach to a versioned campaign episode rather than freeze the whole evolving campaign, or later work-order creation must be blocked once correlation finalises the campaign.

The mature product requires ongoing work. Episode finality and job continuity should therefore be separate objects.

### 8. Review consequences do not act on the owned artifact

The blind-review path can record a current correction, evaluation candidate, and quarantined future proposal. Those records are not joined to an owned campaign artifact or its dependency graph.

A “current correction” is free text. There is no exact patch, recomputation, descendant artifact, invalidation, diff, or new scoped disposition. A “future proposal” remains safely quarantined but has no protected comparison runner or promotion transition.

The review machinery is reusable custody for expert judgments. It is not yet the correction-and-learning loop described by the product thesis.

### 9. The visible forms expose implementation state, not completed work

The bound job page is honest but displays a raw Python representation of an arbitrary candidate. The Casebook exposes research-state terminology and violates the current no-eyebrow rule. Neither page lets the analyst inspect the native artifact operation, see why a source is admissible for one target, understand downstream recalculation, amend the proposal, or authorise a named use.

Replacing these pages before the host objects exist would create another simulated product. The interface should be redesigned only alongside the exact object and transition it exposes.

## Harness strengths worth preserving

The following mechanisms should be retained unless counterevidence appears:

- director ownership and tenant-correct lookup;
- immutable exact input bytes and run specifications;
- proposal disposition before work-order creation;
- canonical packet derivation and digest checking;
- exact version-pinned cognition reads;
- one empty output root per work order;
- tracked NTM send and observed completion before collection;
- attestation over final output bytes;
- provisional candidate or bounded refusal by default;
- accepted-state planner re-entry over exact state artifacts;
- append-only human dispositions; and
- Langfuse as post-hoc diagnostic evidence rather than authority.

These mechanisms form a reliable custody spine for the next product slice.

## Changes that should not happen first

The repository should not first:

- activate the dormant DeepResearch suite;
- add more agent roles;
- expose a visible multi-agent graph;
- rewrite every protocol;
- build a richer Casebook;
- style a spreadsheet review page;
- implement generic institutional memory;
- import Agentic SDLC wholesale;
- add autonomous prompt updates; or
- claim that source correctness is solved by adding fields to the candidate schema.

Each would create visible sophistication without first making the wrong-source counterexample impossible to promote.

## Required host seam before prompt refinement

The smallest credible semantic boundary needs machine-issued identities for:

1. an exact source version or captured retrieval;
2. one exact source assertion and locator inside that version;
3. one explicit target contract for the proposed artifact location;
4. a candidate value or operation joining assertion to target;
5. a deterministic admissibility result over known dimensions;
6. unresolved or contested dimensions reserved for analyst judgment; and
7. downstream dependencies that remain provisional until correction and recomputation.

For a closed first demo, the target contract can be deliberately narrow: one workbook cell representing one named model target, with explicit entity, period, unit, accounting basis, and permitted document classes. The host should reject the known wrong document class before a candidate workbook exists, while allowing a separately declared non-GAAP, derived, estimate, or analyst-assumption target under its own contract.

Only after that seam exists should the bound protocol require exact host-issued IDs, the research worker stop creating its own source identities, and the interface expose source fit and analyst exceptions.

## Audit conclusion

The prompts are not the principal blocker. They already express much of the intended epistemic discipline. The blocker is that the model still authors both the semantic claim and most of the evidence identity used to assess it.

The next falsifiable product hypothesis should preserve the present custody spine and replace that self-certifying relation with one host-owned source-to-target gate inside a real native-artifact change path.

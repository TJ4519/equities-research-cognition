# Inference-state replay

Status: proposed audit and evaluation model. The document distinguishes re-derivation from transcript inspection and deterministic reproduction from model comparison.

## The technique

The technique previously described as claim replay or inference-state replay asks a stronger question than “what did the agent say and do?”

It asks:

> From the exact prior state, evidence, methods, challenges, and human decisions, why was this claim, value, or artifact permitted, and can an independent process derive the same licensed result?

A transcript may help diagnose execution. It cannot answer the full question.

A trace can show that a model opened a filing and wrote `37,378`. It cannot establish that the filing bytes were exact, that the source was lawful for the use, that the model line meant what the model claimed, that another source was excluded from context, that a spreadsheet engine recalculated the descendant faithfully, or that an analyst permitted the result for one stated purpose.

Inference-state replay uses durable professional and evidential objects rather than hidden reasoning tokens.

## The replay path

A replay begins at one consequential output:

- report sentence;
- numerical value;
- chart point;
- model assumption;
- workbook cell;
- artifact version;
- active-memory entry; or
- method promoted for later use.

It then walks backward:

```text
output
-> exact artifact or claim version
-> decision and grant that permitted the use
-> human amendments and unresolved judgment
-> derivation and method version
-> context build and producing run
-> admitted assertions and assumptions
-> source versions, access facts, and evidence cutoff
-> prior perspective and professional object
-> original request and confirmed commission
```

The replay then walks forward:

```text
prior state and exact evidence
-> apply declared evidence-use rules
-> rebuild the model or tool context
-> rerun deterministic transformations
-> independently re-derive model-written claims
-> compare claims, values, artifacts, uncertainty, and decisions
```

Backward inspection shows what licensed the stored result. Forward reconstruction tests whether the licence and derivation remain coherent.

## Four separate replay questions

### Source replay

Can the system recover the exact source versions and assertion locators used?

Source replay checks:

- content hash;
- source identity;
- publication and capture times;
- amendment state;
- entitlement and retention facts;
- assertion locator;
- extracted value or statement;
- parser or extraction version; and
- evidence cutoff.

A model-written citation cannot pass source replay by itself.

### Context replay

Can the system reconstruct what each model and tool could see?

Context replay checks:

- included prior-perspective items;
- included assertions;
- excluded items and reasons;
- methods and skills;
- instruction;
- tool grants;
- model and runtime configuration;
- budget; and
- context-manifest digest.

Context replay is where the local evidence firewall becomes testable.

The system may say that an earnings-release assertion was excluded from the primary model-update context. The claim is credible only when the context builder issued the manifest and materialised the exact population.

### Derivation replay

Can the system reproduce or independently recover how the inputs produced the output?

Deterministic examples include:

- arithmetic;
- code execution;
- statistical calculation;
- workbook operation;
- formula recalculation;
- chart construction; and
- document rendering from a typed claim set.

Model-mediated examples include:

- claim extraction;
- management-language comparison;
- mechanism analysis;
- research synthesis;
- thesis amendment; and
- materiality proposal.

A deterministic derivation should reproduce exact bytes or exact declared values where the environment permits it.

A model-mediated derivation should be independently reconstructed from the same admitted evidence. The comparison should inspect the claim graph, cited support, uncertainty, contradictions, and scope. Exact prose equality is neither expected nor desirable.

### Authority replay

Can the system reconstruct why the result was allowed to affect professional work?

Authority replay checks:

- who confirmed the professional object;
- which method and evidence-use rule applied;
- which person or policy granted the action;
- the exact object covered;
- named purpose;
- effective dates;
- expiry;
- delegation;
- later amendment or revocation;
- which descendants were affected; and
- whether the result entered active memory or method policy.

A run marked complete cannot pass authority replay without a later grant where one is required.

## Replay grades

One word such as `reproducible` hides important differences.

### Grade A: exact deterministic reproduction

The system rebuilds the exact declared output from exact inputs under a captured environment.

Examples:

- a calculation returns the same value;
- an artifact operation produces the same changed cells and formulas;
- a renderer produces byte-identical output when deterministic output is part of the contract.

### Grade B: bounded deterministic reproduction

The system reproduces declared values and relations within an explicit tolerance, while environmental details may change bytes.

Examples:

- chart image bytes differ but the data series and specification match;
- a spreadsheet engine version changes metadata while formulas and calculated values remain within the contract;
- floating-point or locale behaviour is controlled by stated tolerances.

### Grade C: evidential re-derivation

An independent model or procedure reaches a materially equivalent claim set from the same admitted evidence, preserving contradictions and uncertainty.

The result should compare:

- claims recovered;
- claims missing;
- unsupported additions;
- source relations;
- uncertainty;
- affected professional objects; and
- action recommendations.

### Grade D: licensed-path reconstruction

The system can reconstruct the exact support and permissions for the stored result but cannot independently reproduce the result because the required model, tool, source, or environment is unavailable.

The limitation should remain visible.

### Grade E: transcript-only observability

The system can inspect messages and tool calls but cannot reconstruct the exact source, context, derivation, or authority.

Grade E is useful for debugging. It should not support a strong audit claim.

## Micron replay

The protected Micron case should preserve two assertions:

```text
Assertion A
source: earnings-release exhibit
value: 37,378 USDm

Assertion B
source: annual filing
value: 37,378 USDm
```

The professional object states:

```text
FY2025 consolidated GAAP revenue
historical model input
USD millions
filed annual report once available
```

The baseline unsafe path is:

```text
Assertion A
-> proposal to update the professional object
-> numerical equality passes
-> candidate appears valid
```

The expected controlled path is:

```text
Assertion A
-> evidence-use decision rejects support for this object and use
-> primary model-update context omits Assertion A as support
-> no workbook operation is created from Assertion A

Assertion B
-> evidence-use decision permits support
-> operation creates a descendant workbook
-> supported engine recalculates declared dependants
-> candidate remains provisional until an analyst decision
```

The replay should prove more than the final value.

It should show:

- the two assertions remained distinct;
- the source-use rule was human-authored or policy-authored;
- the rule applied only to the stated professional object and time;
- the excluded assertion did not enter the primary artifact-changing context;
- the original workbook remained intact;
- the calculation result came from a named engine;
- artifact use did not promote the method automatically; and
- later replay can change the source rule without changing unrelated facts.

## Counterfactual replay

Counterfactual replay tests causality by changing one intervention while holding the historical case fixed as far as possible.

A valid replay specification should name:

```text
historical case
baseline system version
one intervention changed
objects held fixed
non-deterministic elements
comparison measures
protected regressions
claim ceiling
```

Possible interventions include:

- source-use rule;
- intent interpretation skill;
- context retrieval;
- prompt;
- model;
- method;
- challenge step;
- calculation adapter;
- memory item;
- agent decomposition; or
- materiality proposal.

A comparison should not claim that a prompt caused the improvement when the model, context, and source population also changed.

## Trace inversion and replay

A stronger model may inspect a weaker agent’s observable trajectory and infer the earliest consequential defect.

The diagnosis may propose a compact judgment change:

```text
state known at the time
action or inference taken
professional defect
replacement inference or action
expected later consequence
scope
```

The diagnosis remains a hypothesis.

Counterfactual replay tests it:

```text
human correction
-> candidate judgment change
-> exact-state replay
-> blind comparison
-> governed method or skill candidate
```

The stronger model acts as a trace inverter or diagnostician. The replay establishes whether the proposed repair improves the work under controlled conditions.

A judge that merely scores the completed trace cannot provide the same causal evidence.

## Replay of model-written claims

Model prose is stochastic. Replaying prose word for word would reward imitation rather than reasoning.

A report should therefore have a typed claim layer beneath the rendered prose.

Each claim should state:

- proposition;
- scope;
- support relations;
- contradictions;
- uncertainty;
- status;
- affected professional objects;
- permitted language; and
- prohibited strengthening.

The renderer may express the claim naturally. Replay compares the typed claims and support, then inspects the prose for unsupported additions or changed scope.

A useful report may contain narrative structure that cannot be reduced to atomic claims. The replay should preserve the distinction between licensed claims and editorial organisation.

## Replay of native artifacts

A native artifact needs its own replay contract.

### Workbook

Record:

- parent bytes;
- workbook profile;
- structural target;
- professional-object mapping;
- operation;
- source or assumption inputs;
- formulas before and after;
- dependency edges;
- calculation engine and version;
- calculation mode;
- unsupported features;
- descendant bytes;
- changed values; and
- validation result.

Replay should recreate the operation on the parent and compare the declared consequences.

### Chart

Record:

- data population;
- transformations;
- chart specification;
- renderer;
- labels and units;
- output; and
- source relations.

### Statistical analysis

Record:

- input dataset version;
- cleaning and transformation code;
- statistical method;
- environment;
- random seed where applicable;
- results;
- diagnostics; and
- interpretation claims.

### Research note

Record:

- typed claim set;
- admitted evidence;
- prior perspective used;
- unresolved contradictions;
- rendered document;
- human amendments; and
- use decision.

## Replay of memory

Future context can be poisoned even when the current output is useful.

Memory replay asks:

- which prior objects entered the context;
- who permitted each object to become active memory;
- whether the item had expired or been superseded;
- how the item affected the new plan or claims;
- whether the model broadened its scope; and
- whether the later result would change without the item.

A correction may say:

> In this Micron model, capacity refers to wafer starts.

A later replay should test whether the system correctly uses the distinction in that model while avoiding a universal semiconductor rule.

## Replay proof pack

Each consequential result should be able to export a proof pack.

The pack may contain:

```text
manifest.json
original-request.txt
confirmed-commission.json
prior-perspective.json
source-manifest.json
assertions.jsonl
evidence-use-decisions.jsonl
context-manifests/
method-manifests/
derivations.jsonl
claims.jsonl
artifact-manifest.json
decisions.jsonl
corrections.jsonl
execution-links.json
replay-spec.json
replay-result.json
human-readable-explanation.md
```

The pack should reference content-addressed bytes rather than duplicating material that licence or privacy rules prohibit from export.

The proof pack is a portable audit view. The canonical local or shared store remains authoritative.

## Terminal audit surface

A first CLI may expose:

```text
research inspect <episode>
research explain <claim-or-artifact>
research lineage <object>
research context <run>
research replay <evaluation-case>
research compare <baseline> <candidate>
research verify <proof-pack>
```

`research explain` should answer in ordinary language:

```text
What is this result?
What prior work did it begin from?
Which evidence supported it?
Which evidence was excluded or disputed?
Which method produced it?
What changed in the native artifact?
What remained uncertain?
Who permitted the result, for what use, and until when?
What later work depends on it?
Can it be reproduced or independently re-derived now?
```

## Langfuse relation

Langfuse may store or display:

- model requests and responses;
- tool calls;
- trace hierarchy;
- session correlation;
- latency;
- token use;
- cost;
- errors; and
- model metadata.

The workspace should link Langfuse observations to exact episode, context, run, derivation, and artifact identifiers.

Langfuse should not become canonical for:

- source bytes;
- source rights;
- context inclusion and exclusion;
- professional meaning;
- artifact versions;
- grants;
- human decisions; or
- replay verdicts.

The same replay should remain possible when Langfuse is unavailable, subject to the loss of execution detail.

## Replay comparison measures

A replay should compare more than output quality.

Possible measures include:

- unsafe evidential routes admitted;
- legitimate evidence blocked;
- unsupported claims added;
- supported claims lost;
- contradiction preservation;
- professional-object mapping accuracy;
- artifact operations proposed;
- deterministic calculation agreement;
- review minutes;
- correction effort;
- consultant intervention;
- elapsed time;
- model cost;
- context size;
- memory scope errors; and
- later episode performance.

A system that blocks everything may improve one safety measure while destroying the product.

## Counterfactual case families

The Micron case should be varied along the dimensions that a proposed rule claims to cover.

### Equal values, filing required

The earnings release and filing agree. The prohibited route remains prohibited.

### Different values, filing required

The documents disagree. The same rule should apply for the same reason.

### Filing not yet available

A temporary method permits preliminary results until the filing appears. The grant expires when the filing becomes available.

### Non-GAAP target

The professional object requires a non-GAAP measure. A GAAP filing value may be irrelevant.

### Derived value

Several admitted inputs and an authorised formula produce the result. No document directly states the final number.

### Analyst estimate

Evidence informs assumptions. The estimate remains attributed professional judgment.

### Conflicting management statements

The useful result preserves the contradiction rather than selecting one source hierarchy.

### No settled source hierarchy

Supply-chain checks, broker research, alternative data, and management commentary carry different permissions by use.

### Later amendment

A source is restated. Present descendants become stale while historical as-of work remains intact.

### Memory correction

A corrected professional meaning must affect the next episode within scope and nowhere else.

## Invalid replay successes

- The replay reproduces the correct number through the same prohibited route.
- The trace matches while the source bytes cannot be recovered.
- The model reaches a similar conclusion after receiving later evidence unavailable at the original cutoff.
- A new prompt looks better because the source population also changed.
- A workbook formula matches while cached values remain stale.
- The proof pack contains exact hashes for an artifact the analyst never used.
- An independent model agrees because it received the same unsupported prior summary.
- A replay passes one corrected episode and promotes a global method.
- A replay lowers unsafe admission by refusing every ambiguous case.
- A replay claims exact reproduction where only semantic similarity was tested.

## Build consequence

Inference-state replay should shape storage from the first line of new code.

Adding replay after the product has stored only transcripts and final artifacts would require reconstructing relations that were never captured.

The local workspace should therefore issue stable identities for source versions, assertions, professional objects, context builds, methods, derivations, artifacts, grants, decisions, corrections, and evaluation cases before it attempts broad autonomous research.

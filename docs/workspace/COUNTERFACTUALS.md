# Counterfactuals

Status: design attack. Each counterfactual asks what the system would become if one attractive idea dominated the build.

## Why counterfactuals belong before code

The project has already shown how a narrow proof can become the practical centre. Once a user interface, schema, and runtime surround a narrow idea, later product thought tends to explain the existing code rather than challenge it.

Counterfactuals keep several possible systems alive while the whole design still fits in a planning context.

A candidate architecture should explain why it beats these rivals for the first analyst, not merely why it can be built.

## Rival product 1: query-to-report deep research

### Shape

```text
user query
-> search
-> retrieval
-> cited report
```

### What it does well

- familiar interaction;
- fast first result;
- clear demo;
- easy comparison with existing products;
- citations can be inspected;
- public sources fit naturally.

### What it misses

- exact prior analyst work;
- native models and artifacts;
- purpose-specific source use;
- source entitlement and retention;
- correction of the current professional object;
- selective future memory;
- artifact descendants;
- re-derivation of why the result was licensed; and
- a second episode beginning from corrected state.

### Invalid success

The report is excellent but generic. The analyst must decide which current claim, assumption, or model object it affects and rebuild the useful part in normal tools.

### Retained lesson

Deep research should become one method in the workspace. Its output should be a claim set and useful artifact tied to prior professional state.

## Rival product 2: skills package only

### Shape

```text
install skills in Claude Code or Codex
-> invoke research procedures
-> save outputs in files
```

### What it does well

- low installation burden;
- terminal-native interaction;
- uses the analyst’s existing subscription;
- methods remain readable;
- easy customisation;
- no new web application.

### What it misses

- authoritative source identities;
- transactionally correct state;
- exact context inclusion and exclusion;
- grants and expiry;
- content-addressed artifacts;
- protection against a skill writing its own authority;
- replay across model and skill versions;
- safe shared use.

### Invalid success

The terminal agent follows the skill and returns polished JSON. The JSON claims that excluded evidence was not used, but the skill and model controlled the same context and record.

### Retained lesson

Skills should remain the agent-facing procedure layer. A local service should own identity, context, artifacts, and decisions.

## Rival product 3: filesystem workspace without a database

### Shape

```text
markdown, JSON, and folders
-> Git history
-> terminal agents read and write files
```

### What it does well

- inspectable;
- agent-friendly;
- portable;
- simple backup;
- works with any terminal harness;
- easy branching.

### What it misses

- safe concurrent writes;
- robust object identity;
- stale-write detection;
- grants and revocation;
- efficient relation queries;
- partial-write protection;
- clear authority between generated files;
- source retention that differs from Git retention.

### Invalid success

Every file has a provenance header. Two agents overwrite the same method, one source licence requires deletion, and later work cannot determine which version governed the result.

### Retained lesson

Human-readable files should project canonical local state. SQLite and content-addressed objects should provide the local authority.

## Rival product 4: full hosted SaaS first

### Shape

```text
web login
-> upload sources and artifacts
-> cloud agents
-> dashboard and review
```

### What it does well

- clear multi-user product;
- central deployment;
- connectors and schedules fit;
- administration and billing fit;
- easier team audit.

### What it misses at the beginning

- direct use of approved local models and files;
- low-friction terminal work;
- client-controlled source retention;
- proof that analysts want another web destination;
- vendor-neutral use of existing agent subscriptions;
- product learning before tenancy choices harden.

### Invalid success

A polished dashboard records every source and task. The analyst continues doing the real work in Excel and a terminal, then uploads final artifacts for the dashboard to display.

### Retained lesson

A shared service may become valuable after the local workflow proves repeated use. Web views should read the same durable objects.

## Rival product 5: Company Room as the product

### Shape

```text
open company
-> see current view
-> launch work
-> store history
```

### What it does well

- continuity;
- natural place for monitoring;
- familiar research organisation;
- company history becomes visible.

### What it misses

- themes across companies;
- portfolio questions;
- one-off statistics;
- model-led work;
- industry process visualisation;
- events touching several subjects;
- disagreement between perspectives.

### Invalid success

Every piece of work receives a company record. Cross-company questions fragment into duplicated notes and the analyst maintains a second “current view” beside the real artifacts.

### Retained lesson

Company should be a strong view over subjects, perspectives, episodes, and artifacts. It should not be the sole canonical root.

## Rival product 6: Excel companion as the product

### Shape

```text
open workbook side panel
-> inspect source and model line
-> propose change
-> approve candidate
```

### What it does well

- native artifact remains visible;
- before and after are concrete;
- dependencies can be measured;
- model updates may provide immediate value.

### What it misses

- management comparison;
- broad earnings research;
- thesis tracking outside the workbook;
- statistical and visual work;
- monitoring;
- institutional memory across artifacts;
- questions that should not produce a model change.

### Invalid success

The source gate is excellent. The analyst receives no help deciding which parts of the results matter or which model assumptions deserve work.

### Retained lesson

Excel should be one supported artifact adapter and perhaps one native view.

## Rival product 7: source firewall as the product

### Shape

```text
source folder
-> admit, quarantine, reject
-> admitted-only model context
-> cited report
```

### What it does well

- exact context exclusion can be proved;
- wrong-source cases become testable;
- clean evidence population;
- useful for sensitive or high-stakes work.

### What it misses

- discovery from weak signals;
- professional-object meaning;
- derived and estimated values;
- artifact actions;
- materiality;
- correction and future memory;
- legitimate use of one source for one purpose and rejection for another.

### Invalid success

The system rejects every uncertain source, produces immaculate records, and gives the analyst less useful research than an ordinary terminal agent.

### Retained lesson

The context builder should enforce purpose-specific evidence use. Discovery, support, quarantine examination, and artifact change need separate contexts.

## Rival product 8: multi-agent graph as the product

### Shape

```text
planner
-> researchers
-> critic
-> synthesis
-> judge
```

### What it does well

- work can be decomposed;
- fresh challenge may improve results;
- parallel research can reduce time;
- stages appear inspectable.

### What it misses

- agent count does not establish evidence independence;
- fixed roles may not fit the question;
- coordination can exceed research work;
- the analyst sees process rather than consequence;
- one strong session may perform the same work more cheaply.

### Invalid success

Five agents agree after receiving the same prior summary and source population. The interface presents agreement as independent confirmation.

### Retained lesson

Roles should remain temporary responsibilities. Separate contexts should be earned by different evidence, tools, authority, or a need for fresh judgment.

## Rival product 9: searchable terminal memory

### Shape

```text
index every agent session
-> retrieve old conversations
-> inject relevant history
```

### What it does well

- recovers forgotten work;
- supports several agent providers;
- improves operator continuity;
- can reveal repeated procedures.

### What it misses

- transcript claims may be unsupported;
- source bytes may be missing;
- active and abandoned views mix;
- old permissions may have expired;
- one model’s summary may become another model’s evidence;
- exact context and artifact ancestry remain unknown.

### Invalid success

The next agent retrieves a persuasive earlier conclusion and treats it as institutional memory despite no human decision to retain it.

### Retained lesson

Session search belongs in the archive. Active perspective and procedural memory need separate promotion.

## Rival product 10: governance-heavy research host

### Shape

```text
forms and approval steps
-> exact records
-> strict source rules
-> review screens
```

### What it does well

- defensible chronology;
- clear authority;
- easier audit;
- known invalid states can be blocked.

### What it misses

- fast exploratory work;
- broad professional requests;
- discovery from incomplete evidence;
- low-friction correction;
- the analyst’s reason to return.

### Invalid success

No unsupported claim reaches an official artifact because almost no claim reaches an artifact at all.

### Retained lesson

Controls should appear at consequential boundaries. Routine work should remain cheap. The product must measure false blocks and review minutes.

## Rival product 11: autonomous research office

### Shape

```text
watch everything
-> decide what matters
-> research
-> update models and memory
-> alert the analyst
```

### What it does well

- resembles the eventual ambition;
- continuous coverage;
- compounds prior work;
- strong executive story.

### What it misses in an early product

- reliable materiality;
- lawful connectors;
- stable professional-object mappings;
- tested methods;
- correction history;
- confidence that active memory is not polluted.

### Invalid success

The office sends impressive alerts while quietly broadening assumptions, storing unsupported conclusions, and changing later context.

### Retained lesson

Autonomy should grow from replayed episodes and measured methods. Monitoring should begin with analyst-confirmed watched objects and questions.

## Research counterfactual 1: a derived value

The analyst asks for free cash flow.

Operating cash flow and capital expenditure come from exact sources. The analyst’s capital-expenditure definition differs from management’s headline measure. The final value appears nowhere directly.

The workspace must preserve:

- input assertions;
- definition of each component;
- authorised formula;
- period alignment;
- calculation engine;
- rounding;
- result;
- uncertainty; and
- intended use.

A source hierarchy cannot solve the case.

The product fails when the report cites one filing as though the filing directly stated the derived value.

## Research counterfactual 2: an analyst estimate

The analyst estimates HBM revenue from capacity, pricing, yield, and timing.

Evidence informs the assumptions. The estimate remains professional judgment.

The workspace must preserve:

- assumption author;
- scenario;
- rationale;
- evidence that informed each assumption;
- formula or mini-model;
- sensitivity;
- uncertainty;
- expiry or reconsideration event; and
- permission to use.

The product fails when the model converts informed judgment into a sourced fact.

## Research counterfactual 3: conflicting management statements

The chief executive describes demand as strong. The chief financial officer issues cautious guidance. An earlier investor-day statement used a different definition.

No settled source hierarchy decides which statement is correct.

The useful output may be the contradiction itself.

The workspace must preserve:

- speaker;
- date;
- audience;
- exact words;
- subject;
- statement kind;
- changes in definition;
- related external evidence; and
- unresolved interpretation.

The product fails when a synthesis model smooths the statements into one coherent management narrative.

## Research counterfactual 4: weak source, useful lead

A supplier comment has unclear timing. It may contradict the current capacity view.

The source may be barred from supporting a relied-upon claim while remaining valuable for discovery.

The workspace should permit:

```text
broad discovery context sees source identity and content
-> lead or contradiction proposed
-> support context excludes the assertion
-> quarantine examiner states what could change
-> analyst may seek stronger evidence or grant a scoped exception
```

The product fails when the firewall hides the only useful lead or when the weak assertion slips into the final claim.

## Research counterfactual 5: licensed source without retention rights

An analyst may read a broker note through an approved account. The licence may prohibit local storage or redistribution.

The workspace must preserve:

- source identity;
- operating identity;
- access time;
- permitted actions;
- lawful locator;
- claims derived under the licence;
- retention restriction; and
- later inability to reproduce exact bytes.

Replay may reach a lower grade because the bytes cannot be retained.

The product fails when it stores the note anyway or claims exact replay later.

## Research counterfactual 6: source amendment

A filing is amended after an internal model and note used the original.

The original work remains a faithful record of the earlier cutoff. Present use may require another descendant.

The workspace must distinguish:

- historical as-of validity;
- present validity;
- descendants affected;
- artifacts requiring recomputation;
- notes requiring amendment;
- grants that expired; and
- source rights that changed.

The product fails when history is rewritten or present artifacts remain silently current.

## Research counterfactual 7: thematic work

The analyst asks whether HBM constraints are easing across Micron, SK Hynix, Samsung, suppliers, and equipment vendors.

The work has no single company root.

The workspace must support:

- several subjects;
- separate source rights;
- company-specific definitions;
- shared theme claims;
- contradictions;
- cross-company calculations;
- one or more artifacts; and
- later company views derived from the same episode.

The product fails when the work is copied into several company folders with divergent conclusions.

## Research counterfactual 8: ad hoc statistical work

The analyst drops a Bloomberg export into the workspace and asks whether one factor explains recent returns.

The workspace must preserve:

- exact dataset;
- column meanings;
- cleaning;
- sample period;
- missing-value treatment;
- statistical method;
- code;
- environment;
- diagnostics;
- multiple-testing concern;
- result; and
- interpretation.

The product fails when the statistical output is reproducible but the interpretation overstates causality.

## Research counterfactual 9: useful result, poisoned memory

The system produces an excellent post-results note. The note includes one unsupported interpretation. The analyst downloads the note for its chart.

The workspace must not infer that every claim in the note entered the active perspective.

Artifact use, claim use, and memory promotion should remain separate.

The product fails when the next episode receives the unsupported interpretation as prior fact.

## Research counterfactual 10: safe but uneconomic review

The system catches every source mismatch. The analyst still checks every claim, formula, and chart because the controls do not reveal what can be skipped.

The product fails commercially even when the audit is perfect.

The experiment should measure:

- analyst review minutes;
- manual reconstruction;
- exceptions inspected;
- exceptions dismissed;
- false blocks;
- unsafe routes;
- artifacts used; and
- repeated use.

## Counterfactual implementation paths

### Extend the Django host

Advantages:

- existing authentication and custody;
- PostgreSQL relations;
- tests and hostile checks;
- web views already exist.

Risks:

- campaign and work-order nouns shape the new domain;
- local installation remains awkward;
- server architecture may precede individual usefulness;
- NTM assumptions persist;
- private local data may flow through the wrong boundary.

### Build a local kernel beside Django

Advantages:

- clear local-first design;
- reuse selected Python concepts;
- shared repository and tests;
- Django may later become the shared service.

Risks:

- duplicate models and migrations;
- unclear authority during transition;
- temptation to keep both systems permanently.

### Build the local kernel cleanly and treat Django as prior art

Advantages:

- strongest conceptual reset;
- agent and CLI interfaces designed first;
- easier vendor-neutral runtime;
- local state can become primary.

Risks:

- more code discarded;
- existing hostile checks need porting;
- team service delayed;
- architecture may repeat solved custody work badly.

The master plan should force an explicit decision after a small architectural comparison. Sunk code should not decide the answer.

## Invalid product successes

- The correct number arrives through a prohibited route.
- The report is useful but disconnected from prior work.
- The artifact is used and its method silently becomes a default.
- The system rejects every uncertain source.
- Every citation is exact and the professional object is wrong.
- Source use breaches entitlement despite perfect hashes.
- A historical replay uses later evidence.
- A workbook contains correct formulas and stale values.
- Arithmetic is correct under the wrong professional method.
- Several agents agree from the same contaminated context.
- A consultant repairs the work before delivery without attribution.
- Downloading an artifact becomes acceptance of every claim.
- A beautiful report is never used.
- One source check hides a wrong period or scope.
- A model invents the rule that validates its own result.
- One corrected case becomes a global rule.
- The archive is exact and active memory is polluted.
- Every event is surfaced and the analyst receives another inbox.
- The planner proposes tools that do not exist.
- The first episode works and the second forgets the correction.
- The second episode remembers the correction too broadly.
- A restatement is stored while dependent artifacts remain current.
- The system refuses where professional judgment should begin.
- Audit effort exceeds the value of the underlying change.
- The local product works only while one terminal session remains alive.
- Langfuse loss makes the professional state unrecoverable.

## Surviving product statement

A local-first workspace survives these attacks when it lets the analyst state broad work through a chosen terminal agent, compiles the request into exact and limited actions, preserves source rights and context populations, creates useful native results, accepts correction, prevents unsupported conclusions from entering future work, and re-derives why each consequential result was licensed.

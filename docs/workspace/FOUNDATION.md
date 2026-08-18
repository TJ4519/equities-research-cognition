# Foundation

Status: working product thesis. The document narrows the questions that later planning must settle. It does not authorise implementation.

## The professional beginning

A capable analyst does not begin every piece of work with a clean query.

The analyst may begin with an earnings event, a workbook row, a broker revision, a chart, a management statement, a disputed assumption, a theme across companies, a Bloomberg extract, or a suspicion that the present account no longer fits the evidence.

One sophisticated practitioner described agent use across model construction, model updates, model adjustments, meeting notes, ad hoc questions, industry models, mini-models, statistical work, visual explanation, earnings work, thematic views, thesis checking, management comparison, and institutional memory. The same practitioner wanted continuing watch over companies, competitors, supply chains, and themes.

The list describes a desk with more possible work than one person can perform. It does not describe one fixed pipeline.

The common professional act is narrower than “research” and broader than “write a report”:

```text
something changes or a question arises
-> recover the exact prior work that matters
-> decide which evidence and methods may bear on the question
-> perform useful research or artifact work
-> expose the remaining judgment
-> decide what to use
-> preserve enough of the decision for later work
```

## The economic problem

Useful agents lower the cost of inquiry, comparison, calculation, and artifact production.

Lower cost causes more work:

```text
useful agent work
-> more frequent use
-> more companies, sources, calculations, and handoffs
-> more plausible intermediate results
-> longer routes by which one mistake can travel
```

A reviewer cannot reconstruct every route without giving back much of the gained time. Superficial review lets an attractive result acquire authority without anyone checking the route that produced it.

The commercial opportunity is not generic provenance. The opportunity is a shorter path from a professional request to work the analyst can use, with less reconstruction and fewer hidden ways for unsupported claims, methods, or model changes to enter later work.

The controls earn their place only when they reduce review work. Immaculate records beside a result the analyst must rebuild have no independent product value.

## The Micron lesson

The Micron example contains two source assertions with the same value: `37,378` USD millions.

One assertion comes from an earnings-release exhibit. Another comes from the later annual filing. A particular model line may require the filed annual report once available.

A numerical test cannot distinguish the two routes:

```text
wrong source
-> expected value
-> numerical comparison passes
-> reviewer sees no difference
-> candidate enters the model
-> the source-selection method gains quiet precedent
```

The first result may do no numerical harm. The accepted route may fail later when the documents disagree.

The example proves several requirements:

- evidence identity must survive numerical equality;
- admissibility belongs to an assertion, professional object, method, time, and use;
- a model may propose a route but may not create the facts used to authorise it;
- a result decision must not silently promote the method that produced the result; and
- historical episodes should test later changes to prompts, skills, context rules, and software checks.

The example does not prove that annual filings should always outrank earnings releases. It does not prove that workbook updating should define the product.

## The missing technique: inference-state replay

A transcript shows what messages and tool calls occurred. A transcript does not establish why one claim or artifact was licensed.

The required technique is inference-state replay.

A replay begins with an output and walks backward through durable objects:

```text
report sentence, chart point, estimate, or workbook value
-> permission to use the exact artifact
-> candidate and human amendment
-> method and derivation
-> claims, assumptions, and calculations
-> admitted assertions
-> exact source versions and access facts
-> context given to each model
-> original request and prior professional state
```

The system should then be able to walk forward again. Deterministic calculations should reproduce exact results where the adapter permits it. Model-written claims should be independently re-derived from the same admitted evidence and compared with the stored claim and its stated uncertainty.

A counterfactual replay holds the historical episode fixed and changes one intervention:

- a source rule;
- a prompt;
- a skill;
- a context-selection method;
- a model;
- a calculation adapter;
- a challenge step; or
- a memory rule.

The comparison should show which claims, artifact operations, exceptions, costs, and human decisions changed. A better-looking trace is not enough.

## The proposed product

The strongest current product is a local-first research compiler inside a configured agentic workspace.

The analyst opens an approved terminal agent such as Claude Code, Codex, or another compatible harness inside the workspace. The analyst states the professional request in ordinary language.

An installed research skill preserves the exact wording and proposes a structured interpretation:

- purpose;
- prior artifacts and decisions;
- subjects likely affected;
- evidence needs;
- methods that may answer the question;
- supported outputs;
- intended use;
- unresolved professional questions; and
- limits imposed by source rights or available tools.

The analyst corrects only the matters that would change the work. The confirmed commission becomes durable state.

The local service then constructs exact contexts for research and artifact actions. Each child process receives the evidence, prior work, methods, tools, and authority it needs. It does not inherit the whole terminal conversation.

The result may be a cited account, a comparison, a calculation, a chart, a mini-model, a workbook descendant, a refusal, or a proposal for further work. The request may remain broad. The supported actions remain explicit.

The analyst may correct the current result. The correction creates a new result rather than rewriting history. The same episode may later become a protected comparison case.

## Why the workspace is local first

The analyst’s sources and native artifacts often live on the analyst’s machine or inside an approved client environment. Licensed research, private models, notes, and terminal-agent credentials should not move into a new hosted application merely to make the architecture convenient.

A local-first design can provide:

- direct access to approved local files;
- client-controlled encryption and retention;
- operation through the analyst’s chosen terminal agent;
- a content-addressed local source and artifact store;
- exact context assembly;
- local search over prior work;
- vendor-neutral agent runners; and
- useful operation before a team buys a shared service.

Local first does not mean filesystem only. A local database should own identity, relations, grants, and chronology. Human-readable files should project that state for agents and people.

A shared service may later add:

- team identity and roles;
- source connectors and entitlement policy;
- scheduled monitoring;
- cross-machine synchronisation;
- shared artifact custody;
- evaluation execution;
- controlled release of methods and skills;
- administrative audit; and
- organisation-wide memory.

The shared service should extend the workspace. It should not require the first analyst to abandon the terminal and native tools that made the system useful.

## Why skills matter

Skills let a terminal agent perform repeatable procedures without the user writing a long prompt each time.

A first skill family may include:

```text
research-start
research-resume
source-capture
research-plan
purpose-bound-deep-research
management-language-compare
statistical-analysis
model-inspect
model-update
challenge
research-correct
research-inspect
research-replay
```

A skill should teach the agent when to call the local service, what professional question to answer, what records to return, and when to refuse.

A skill should not own source identity, permissions, artifact writes, or memory promotion. Those acts belong to software or an authorised person.

Repeated behaviour should become a skill only after several episodes show that the model-mediated procedure is useful and stable. Identity checks, path restrictions, arithmetic, entitlements, and legal state changes belong in software from the beginning.

## Why typed records matter

Typed records make consequential handoffs inspectable.

They are useful for:

- the proposed and confirmed commission;
- source and assertion capture;
- context manifests;
- method and tool selection;
- proposed artifact operations;
- derivations;
- human decisions;
- corrections; and
- replay results.

A typed record does not control the model’s context. The context builder controls context by selecting exact source and artifact versions, materialising them for one action, limiting tools, and recording the resulting population.

A schema also does not create authority. A perfectly valid model-generated `SourceRule` remains a proposal until an authorised person or standing policy supplies the rule.

## The product should not be confused with these rival forms

### A generic deep-research application

A query-to-report application can search, cite, and write. It does not naturally preserve prior analyst work, native artifacts, purpose-specific evidence use, exact context exclusion, correction, or later re-derivation.

Deep research should become one method inside the workspace.

### A company dashboard

A company page may be useful. It does not cover thematic work, cross-company questions, one-off calculations, model-led work, or events that touch several subjects.

Company, theme, event, model object, and question should remain views over shared durable relations.

### An Excel provenance panel

An Excel panel can show one model change well. It would pull the project back toward the narrow Micron proof and leave earnings research, management comparison, monitoring, and institutional memory outside the product.

Excel should become one artifact adapter.

### A skills package without a local service

Skills alone can improve prompting. They cannot guarantee exact source capture, exclude evidence from a child context, preserve transactionally correct state, apply permissions, or prove which artifact was changed.

### A hosted SaaS application first

A hosted application would force product and tenancy choices before the individual workflow has proved repeated value. It may also create unnecessary movement of licensed and private material.

### A terminal-session archive

Searchable terminal history can recover useful past work. It cannot replace authoritative source versions, context manifests, derivations, permissions, or exact artifact ancestry.

## The product’s accumulating advantage

The durable advantage does not come from the first prompt or interface.

Each real engagement can produce:

- confirmed interpretations of native professional objects;
- exact examples of good and bad research work;
- source and method rules with stated scope;
- corrected episodes;
- protected replay cases;
- artifact adapters;
- proven skills;
- measures of review effort and useful output; and
- evidence about which work should remain human.

The shared kernel improves across clients. Client-specific meaning, source rights, methods, and artifacts remain scoped to the client.

A later competitor can copy a screen. Copying the accumulated episodes, corrections, replay cases, local integrations, and working methods would be harder.

## The first buyer

The first buyer should be one sophisticated analyst or a small team already using capable terminal agents.

The buyer seeks faster research, greater coverage, better continuity, and useful artifact production. Institutional control strengthens the case as work spreads across people, but governance should not dominate the first experience.

The first commercial form may be a productised installation and service:

- configure the workspace;
- connect approved local sources and artifacts;
- install and adapt skills;
- reconstruct several historical episodes;
- measure analyst effort and correction;
- improve methods through replay; and
- teach the analyst or team how to operate and extend the system.

Consultant intervention must remain visible internally. The company should not attribute a repaired result to software that did not produce it.

## The first value threshold

A useful first hurdle is either:

```text
same research scope
-> at least 50 percent less analyst time from event to usable artifact
```

or:

```text
same analyst review hours
-> at least twice the company or question coverage
```

The exact threshold remains a commercial hypothesis. A modest speed gain may not justify another tool, a new source-rights surface, and a new trust burden.

The study should record analyst minutes, consultant minutes, elapsed time, model cost, sources inspected, exceptions raised, legitimate work blocked, unsafe proposals, artifacts used, manual reconstruction, and repeat use.

## The first proof

The first proof should contain two historical episodes.

The first episode should begin with exact prior work, a broad professional request, mixed source material, and at least one artifact action. It should contain the Micron equal-value route as one protected case. The analyst should correct at least one matter of professional meaning or method.

The second episode should begin from the corrected state. The system should recover the earlier distinction without being reminded, apply the evidence rule within its proper scope, and produce useful work without increasing review burden.

The proof should fail when:

- the output is a competent generic report;
- the analyst reconstructs most of the work;
- a consultant silently repairs the result;
- the system repeats the earlier misunderstanding;
- the system remembers the correction too broadly;
- the source controls block legitimate work;
- the native artifact remains unchanged despite a useful proposal; or
- the result cannot be re-derived from durable records.

## The strongest current opinion

The first serious form should be a terminal-native analyst workspace with a local research compiler and an optional shared service.

The natural-language request remains the entrance. Skills supply repeatable professional procedures. The local service supplies exact context, identity, source custody, relations, artifact ancestry, permissions, and replay. Terminal sessions remain replaceable workers. Native artifacts remain native. Langfuse explains execution. The shared service arrives when teams, connectors, schedules, and controlled method release earn their cost.
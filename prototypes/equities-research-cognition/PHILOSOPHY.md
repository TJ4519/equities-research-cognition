# Teleology → Ontology → Epistemology

> **User correction, 31 July 2026:** The order is teleology first, then
> ontology, then epistemology.

## Status

This is a philosophical design prior for the equities-research prototype. It
was distilled from a user correction and a PRO co-architect reflection. It is
not an executable contract, a canonical equities ontology, or evidence that
any proposed judgment task is valid. Material research episodes, exact
trajectory custody, expert judgment, and protected evaluation remain the
relevant authorities; mechanical fixtures have zero cognition authority.

## Formalising work is already a theory of the worker

Formalising an equities-research task is not a neutral decomposition of work.
It expresses a theory of the analyst:

- **Teleology:** which investment decision the research serves, over what
  horizon, and under which error costs.
- **Ontology:** which kinds of things exist and matter for that decision:
  companies, segments, products, customer cohorts, expectations, competitive
  responses, catalysts, valuation regimes, or something else.
- **Epistemology:** which observations count as evidence about those things and
  what would justify changing a view.

The order matters. Purpose selects the relevant world; the selected world
determines what could count as knowledge about it.

A task contract therefore says, in effect:

> For this kind of analyst, pursuing this kind of decision, these objects
> matter; this information is admissible; this distinction is meaningful; and
> these answers are useful.

That is a substantive research hypothesis.

Thinking Machines and Bridgewater did not discover six natural kinds hidden
inside finance. They began with six recurring organisational decisions. Even
article relevance depended on Bridgewater's mandate: something could be
financially relevant yet insufficiently significant for a macro investor.
Expert prompting improved performance partly by refining the task definition,
not merely by describing one universal function more clearly.

## Equities research permits plural projections

The same company or event can be represented through several legitimate
ontologies:

- An accounting projection represents NVIDIA through statements, reporting
  segments, definitions, reconciliations, and period-to-period bridges.
- An operating projection represents it through units, price, product mix,
  capacity, utilisation, customers, and channels.
- An expectations projection represents it through guidance, consensus
  distributions, estimate revisions, narrative, positioning, and
  price-implied assumptions.
- A causal projection represents it through competing explanations such as
  sustainable demand, inventory accumulation, pull-forward, product
  transition, or supply constraint.
- A decision projection represents it through an action set, horizon,
  valuation assumptions, monitoring triggers, and downside conditions.

None is the canonical function of “the equities analyst.”

For a revenue beat, the accounting question is whether figures are comparable
and reconcile. The operating question is whether the change came from units,
price, mix, or timing. The expectations question is whether the result exceeded
a live expectation or merely a stale published consensus. The causal question
is whether the result bears on durable demand. The decision question is whether
any surviving interpretation changes the action or only what must be
monitored.

These are not necessarily five independent stages of a universal pipeline.
They are five projections of the same event, each preserving different
distinctions.

The task system should therefore be an overlapping cover of important judgment
surfaces, not a mutually exclusive and collectively exhaustive breakdown of
research. One research decision may legitimately appear in several task
families. “Was this evidence sufficient?” may be examined as a
source-authority question, a causal-identification question, and a
claim-language question. The overlap is useful when each task exposes a
different failure.

## Stability exists within declared regimes

The useful goal is not a universally stable task called “assess revenue
quality.” It is a task family stable within a declared mandate and information
regime.

One candidate is comparability:

> Given two exact financial observations, their metric definitions, economic
> scopes, reporting periods, source records, and information cutoff, determine
> whether they are directly comparable, comparable only through an explicit
> bridge, not comparable, or insufficiently specified.

This does not reproduce company analysis. It formalises one recurring
professional distinction and constrains later work: a price-volume-mix
decomposition cannot legitimately proceed from incomparable observations.

A second candidate is expectation-reference validity:

> Given an expectation surface, its capture time, subsequent public updates,
> estimate-revision history, evidence cutoff, declared expectation route, and
> intended decision use, determine whether it was current at the relevant
> reference time, stale, or not identifiable from the supplied information.

“Current” is not a universal property of a consensus snapshot. Current for
which event, at what time, as a proxy for which expectation construct, and for
which decision? The mandate and temporal reference belong inside the contract.

A third candidate is evidence-to-claim scope:

> Given these exact sources and this proposed claim, what is the strongest
> statement the evidence supports?

For the NVIDIA counterexample, the answer might distinguish evidence about the
exact incremental Q1 shipment cohort from broader ecosystem demand, contextual
evidence that does not identify NVIDIA shipments, and insufficient evidence.
This prevents broad deployment evidence from being promoted into
cohort-specific evidence.

A fourth candidate is decomposition sufficiency:

> Given the reported change and disclosed driver information, is the proposed
> attribution identified, partially identified with a material residual, or
> underidentified?

This does not ask whether demand is strong. It asks whether the observations
license the decomposition on which a demand conclusion depends.

A fifth candidate is research policy:

> Given the current claim state, competing explanations, available evidence
> routes, their costs, and their diagnostic potential, which route should be
> pursued next—or should the research stop?

This is harder. Its input is changing research state, and the result of an
unchosen route is normally unobserved. It may not become a clean classification
task. Initially it should remain a pairwise, case-conditioned judgment:
channel inventory versus ecosystem deployment, continue versus stop, or reopen
versus preserve uncertainty.

## Different formalisation classes require different proof

At least four kinds of formalisation coexist:

1. **Deterministic legality checks:** dates, arithmetic, units, cutoff
   violations, and exact source repetition. These should not consume expert
   time.
2. **Repeated epistemic judgments:** comparability, expectation-reference
   validity, decomposition sufficiency, evidence scope, and appropriate
   abstention. These are the closest analogues to the Thinking Machines tasks.
3. **Sequential policy decisions:** what to investigate next, when to leave an
   information route, when to challenge, and when to reframe. These should
   initially be judged contrastively rather than forced into fixed labels.
4. **Synthetic whole-case judgments:** the strongest causal account, variant
   perception, valuation consequence, and investment action. These may remain
   irreducibly holistic and should not be mutilated into convenient
   microtasks.

A task contract consequently needs more than an input schema and output enum.
It needs the analyst mandate, relevant ontology projection, exact information
boundary, object being judged, allowed answer states, abstention state,
reference standard, costly errors, downstream consequence, and conditions
under which the task boundary itself should be rejected.

“This is the wrong task” must be a first-class response.

An expert disagreement may indicate a wrong answer. It may instead indicate
that the inputs omit a load-bearing variable, the answer space collapses an
essential distinction, two mandates have been mixed, the named concept is
incoherent, or the judgment cannot be separated from the whole case. In this
system, disagreement can be evidence that the proposed ontology is wrong; it
must not automatically be converted into label noise.

## Task discovery is closer to cognitive task analysis

Behavioural workflow decomposition tends to enumerate visible steps: read
filings, update a model, assess management, value the company. Cognitive task
analysis instead seeks the cues, patterns, discriminations, inferences,
strategies, and mental models that make difficult steps expert.

The Critical Decision Method illustrates this posture. Reconstruct one
demanding incident and probe what the expert noticed, which alternatives
existed, what a less experienced person would miss, and what would have changed
the decision.

That permits serious preparation before privileged workflow access. Do not
arrive with no theory and ask an analyst, “What tasks do you perform?” Arrive
with a provisional judgment map derived from exercised cases:

> We believe this research required a comparability judgment here, an
> expectation-reference judgment here, an evidence-scope judgment here, and a
> route-selection judgment here. We represented each in this way. Which are
> recurring professional decisions? Which boundaries are wrong? What
> information did we omit? Which distinctions would you merge or split? Which
> cannot be judged outside the whole investment case?

This is prior work without pretending the prior is authoritative.

Each proposed task must then survive five tests:

1. **Ontological validity:** does the analyst recognise the object and
   distinction as part of their work?
2. **Operational validity:** can the judgment be made from the declared
   information boundary?
3. **Discriminative validity:** do neighbouring cases receive meaningfully
   different answers for identifiable reasons?
4. **Downstream validity:** does correcting the task alter a research route,
   claim, refusal, monitoring condition, or whole-case judgment?
5. **Economic validity:** does formalisation save enough expert effort or
   prevent sufficiently consequential errors to justify its machinery?

Expert agreement alone is insufficient for promotion.

## The durable unit is a versioned judgment contract

The system should not preserve a static task catalogue as the ontology of
equities. It should preserve versioned families of judgment contracts attached
to scopes and mandates.

“Expectation-reference validity for public-equities earnings research at an
event cutoff” may be one version. “Expectation relevance for a three-year
thesis-monitoring decision” may be another. If one contract repeatedly splits
along strategy, sector, or horizon, split it. If two contracts produce the same
decisions and failure modes, merge them.

Plural ontologies need not make the system incoherent. A shared layer can
preserve identities, times, sources, claims, and decision context. Workbenches
project that common research state into accounting, operating, expectations,
causal, or decision representations. Judgment tasks evaluate explicit
transitions within or between those projections.

Django must not declare an ontology of equities. It should preserve which task
contract, mandate, and information state governed a judgment. Research
intelligence belongs in composable workbenches; the product records authority,
evidence, and learning chronology.

Comparability, definition changes, source independence,
expectation-reference validity, decomposition sufficiency, claim licensing,
abstention, next discriminating information, and decision relevance form a
conjectured atlas—not an authoritative task ontology. They are not
capabilities until they survive material information-foraging episodes,
materially affect research claims or decisions, and later survive analyst
judgment. Mechanical hostile checks may protect a deterministic contract but
cannot supply that evidence.

The object to bring to an analyst is therefore not “our six equities tasks.”
It is a provisional map of where judgment may live, exercised on one serious
case. For each proposed judgment, show the exact case state, the plausible
decisions, what downstream research changed under each, and why the decision
may recur. Let the analyst accept the distinction, redraw it, declare it
mandate-dependent, or reject local decomposition entirely.

The wager is not that equities research contains one hidden canonical task
graph. It is that plural, mandate-conditioned research practices contain
recurring judgment interfaces whose inputs, alternatives, failure modes, and
consequences can become legible—and that progressively discovering those
interfaces can make both the research system and the expert relationship more
rigorous.

# Commission: show a trustworthy agent-driven research job

## The proposition

Expert analysts are already finding valuable ways to use frontier models for
model building and updating, earnings work, statistical analysis,
visualisation, thesis consistency, management-narrative comparison, and
institutional memory. If a recurring method can be observed through normal
analyst corrections, evaluated, and transferred across a team, the firm can
improve and distribute it cumulatively.

The product opportunity is to turn that emerging practice into a serious
analyst environment without removing autonomy. More agent leverage increases
the need to detect unsupported claims, inadmissible data, stale assumptions,
and errors that propagate through calculations or other agents.

Design a complete, standalone software demo that makes this proposition
judgeable. Do not return only an architecture essay or a static dashboard.

## One demonstrable job

Use one consequential post-earnings equities job, with Micron as the public
research subject:

```text
analyst question and decision use
-> exact starting model, cutoff, permitted sources, and material assumptions
-> inspectable research and modelling plan
-> analyst revises or authorises exact work
-> separate bounded agent work where independence or context separation matters
-> evidence, calculations, competing interpretations, and proposed model changes
-> deterministic checks contain known source, identity, cutoff, and dependency failures
-> analyst resolves consequential uncertainty and decides what may be relied upon
-> final research/model artifact with exact lineage and a resumable history
-> correction becomes a candidate evaluation, skill, or workflow change only through separate approval
```

The episode must begin through login and the ordinary UI, persist canonical
backend state, dispatch real NTM/Codex work, contain one intentional failure,
and render the resulting artifact through the product. A report created outside
the product and attached afterwards does not count.

One adversarial modelling case must be visible in ordinary work: an agent finds
the right number in an inadmissible source for a GAAP model target even though
the permitted authoritative source exists. The result must remain provisional,
the failure must be legible to the analyst, and no downstream calculation or
artifact may silently inherit authority from it.

## What decomposition is for

Research work is decomposed into explicit, typed, bounded units because this
makes failures attributable and improvements testable. Each unit should have a
professional objective, exact inputs and cutoff, allowed tools and sources,
expected artifact, refusal conditions, resource bounds, dependencies, and an
acknowledged result.

That decomposition is backend execution grammar. It can support retries,
independent context, traces, evaluations, versioned skills, and rollback. It
must not automatically become a row of agent panes or a vocabulary the analyst
has to learn.

## Product experience

The analyst should recognise their job: the company, question, current model,
what changed, why it matters, what the system proposes to do, the consequential
exceptions, the resulting model/research artifact, and what awaits their
judgment. Richness should come from useful work and native artifacts, not from
ornamental panels.

The product may use a primary ongoing job view with contextual inspection of
sources, calculations, assumptions, changes, competing interpretations, and
history. This is a hypothesis, not a mandated wireframe. Work backwards from
the least burdensome form that still lets the analyst detect bullshit before
it propagates.

Use ordinary sell-side language. Do not invent a visible ontology. Do not use
eyebrows, overlines, kickers, supratitles, or small labels above headings. The
backend may be sophisticated and largely opaque; its achieved facts should
surface only where they help the analyst understand, decide, or audit.

## Authority and provenance

Use a neurosymbolic split rather than asking prompts to police themselves:

- agents interpret intent, forage, compare, calculate, challenge, and propose;
- schemas constrain handoffs but do not establish truth;
- host software owns source identity, exact bytes, versions, permissions,
  cutoff, known admissibility rules, dependencies, state transitions, and
  immutable event history;
- analysts own contested semantics, assumptions, materiality, and release for
  a named use;
- every result remains candidate state until the required checks and human act
  occur.

The system should preserve enough lineage to answer: which exact source and
passage supported this value; which agent and work order produced it; which
calculation transformed it; what depended on it; what changed after a
correction; and who authorised this exact artifact for this exact use?

## Existing substrate versus missing product

The package already contains authentication, PostgreSQL custody, append-only
actions, exact artifact and run-specification records, NTM/Codex lifecycle
control, provisional outcome custody, restart retrieval, Langfuse boundaries,
role protocols, workbenches, and hostile mechanical tests.

It does not yet prove or fully implement workbook parsing, recalculation,
source-to-target admissibility, dependency invalidation, a material Micron
DeepResearch episode, research quality, analyst usefulness, deployment, or the
right analyst-facing form. The inherited pages and terminology are evidence of
software, not a design to preserve.

## Requested response from a PRO-class model

Return a concrete proposal that another engineering agent could build and a
human team could judge:

1. one-sentence product centre and the exact analyst job;
2. the end-to-end user journey and smallest coherent screen set;
3. a low-fidelity mock-up or runnable prototype in ordinary analyst language;
4. the backend state and authority transitions supporting every visible fact;
5. the agent work-unit contract and why each context is separate or shared;
6. the deterministic containment rules for source, cutoff, calculation,
   dependency, staleness, and artifact use;
7. the delta from the existing code, sequenced into verifiable build slices;
8. a live Micron demo script with one intentional failure and recovery;
9. evidence captured for debugging, evaluation, skills, and rollback; and
10. explicit nonclaims, kill criteria, and what analyst feedback would decide
    go/no-go.

Prefer one elegant, falsifiable product hypothesis over a catalogue of
features. Treat the current code as inspectable ground, not as the answer.

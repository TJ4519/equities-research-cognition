# Candidate DeepResearch cognition protocols

## Status

This directory is a candidate design surface for a real equities DeepResearch
system. It is not the active runtime, a cutover decision, a claim of improved
research, or a policy update.

The active host currently loads the thinner protocols under `agents/`. These
files define the intended semantic work of each phase so that later activation
can be evaluated against a clear treatment rather than inferred from scattered
prompt edits.

## Product completion object

A material episode should produce two coupled outcomes:

1. a decision-focused research result or justified refusal; and
2. a judgeable trajectory of the material choices that produced it.

The trajectory should preserve observable commitments, not private
chain-of-thought:

```text
commission and investor use
-> interpreted uncertainty and alternatives
-> director-approved programme
-> source routes, evidence and workbench results
-> evidence, reasoning and action changes
-> challenge, reframe, stop or synthesis decisions
-> bounded result or refusal
-> later expert judgment over exact objects
```

A complete-looking process, a green test suite, a trace, model agreement, or a
well-written report is not evidence that the research was good.

## Architecture

These are five semantic protocols, not five mandatory agents. The host may use
one capable model for several phases. Context persistence and separation are
experimental variables.

The default phase policy is:

- a fresh planner context for initial planning and material re-entry;
- a branch-local persistent worker context for bounded information foraging;
- a fresh synthesis context over an exact selected support set;
- a fresh independent context for adversarial review; and
- a technically isolated context for machine judgment, when that protocol is
  lawfully enabled.

The main research path is:

```text
commission
-> planner candidate
-> director approve | revise | reject
-> research worker
-> director accept | challenge | reject candidate state
-> planner re-entry
-> next branch | synthesis | stop | refusal
-> synthesis candidate
-> adversarial final review
-> human / claim-authority disposition
```

Director-requested planner re-entry from one exact accepted research-state
transition is implemented. Review-driven re-entry, user-correction re-entry,
post-synthesis review admission and operative claim disposition remain current
`HOST_GAP`s. The prompts must name those gaps; they must not narrate an
unimplemented transition as achieved.

Machine judgment is an optional evaluation sidecar, not a mandatory research
stage:

```text
sealed decision point
-> optional machine judgment candidate
-> separately authenticated blind analyst judgment
-> post-lock reveal and diagnosis
```

Machine output is never expert authorship.

## Human objects and machine envelopes

| Protocol | Main human object | Current semantic outputs | Role of the machine envelope |
| --- | --- | --- | --- |
| Planner | Research Programme | `plan.md`, `proposals.jsonl` | Preserve independently disposable proposed work and exact custody. |
| Research worker | Branch Research Note | `branch.md`, `workbench-result.json`, `research-state.json`, `epistemic-delta.json` | Preserve source, calculation, state and append-only delta custody. |
| Adversarial review | Review Decision | `review.md` | Preserve the reviewed object and proposed state action. The current host lacks a typed review transition. |
| Synthesis | Investment Research Read | `synthesis.md` | Preserve the exact selected support basis and the pre-authority candidate. |
| Machine judgment | No direct analyst-facing report | `judgment.json` | Preserve one sealed model candidate and its refusal or exposure status. |

`packet.output_contract` separately governs `artifact-attestation.json`, which
must be written last whenever the semantic outputs can be produced truthfully.
The host remains responsible for independent verification.

## Shared cognition and authority boundaries

### Research Frame

Research Frame is a conditional programme-compilation discipline. When framing
is needed, it helps recover the decision hinge, target construct, proxy gap,
rival generators, discriminators, source surfaces, result-dependent state
changes and claim boundary. An exact lookup may keep this machinery dormant.

A package load, field name, or trace does not prove that Research Frame changed
the programme. The case-specific frame earns its place only when it changes a
branch, route, ceiling, stop, refusal or synthesis decision.

### Optional reasoning operations

A role may use zero or one defect-triggered reasoning operation. It is lawful
only when an exact current object has:

- a named defect;
- exact inputs or inspection boundary;
- one candidate output it may alter;
- an expected epistemic delta; and
- a stop or kill condition.

Once selected and approved, it must run or return an explicit eligibility or
kill result. Agreement between operations or models is not evidence.

The current host requires exactly one reasoning operator for every
`research_worker` proposal and automatically supplies one for a state challenge.
That is an activation mismatch, not the semantic default. The prompts must not
invent a ceremonial defect to satisfy it.

### Workbenches

Workbenches supply positive domain machinery: exact definitions, calculations,
diagnostics, refusals and claim ceilings. The generic role prompts must not
simulate workbench competence in prose.

The current four workbenches can establish comparability, tie a bounded revenue
identity, separate expectation surfaces, and preserve the current
`DECISION_AUTHORITY_UNAVAILABLE` refusal. They do not yet constitute a complete
underwriting engine.

### Supervision and authority

The durable supervision boundaries are:

```text
memory or stored state != evidence truth
accepted research state != accepted claim
review != silent repair
synthesis candidate != operative publication
machine judgment != analyst judgment
analyst correction != evidence or automatic policy
candidate lesson != active behaviour
```

The commissioner supplies the question and investor use. The director disposes
proposed work and candidate state. Research roles return candidates. A later
qualified analyst judges exact objects. Deterministic host and human authority
must separately govern claim use, current-case correction, learning candidates,
interventions and policy activation.

## Preparatory and decision-discriminating work

The Micron planner fragment exposed a specific failure: a broad, useful rival
set collapsed into a sole two-quarter revenue reconstruction that could not
separate the underwriting explanations.

Every proposed branch must therefore be classified as either:

- **decision-discriminating**: plausible returns change a live rival, claim
  boundary, investor-relevant programme choice, stop or refusal; or
- **preparatory**: it creates the lawful input needed for a named downstream
  discriminator.

Preparatory work is legitimate, but the programme must show:

```text
preparatory work
-> exact discriminator unlocked
-> decision-discriminating work
-> possible research or decision effects
```

A programme consisting only of preparatory work must be revised or refused.
This is not a rule that comparability is always preparatory. If the commissioned
uncertainty is itself whether two facts are comparable, a comparable-state
branch may be the first and final decision-discriminating task.

## Current host gaps that must remain visible

The ordinary host now provides director-requested evidence-sensitive planner
re-entry from one exact accepted research-state transition. It creates a fresh
planner work order titled `Re-plan from current evidence` whose
`contract.replans_transition_id` and `research_state_input` bind the exact
accepted transition and its materialized workbench result, research state and
epistemic delta.

The ordinary host does not yet provide:

- a typed route from `review.md` to planner re-entry;
- a user-correction re-entry object;
- a research-state schema that faithfully represents every lawful no-result,
  ambiguity, staleness, contradiction and refusal;
- stable case-frame, branch and decision-point references carried through state,
  review and synthesis;
- zero-operator research-worker approval;
- an operator contract that preserves exact inspection inputs and the one mutable candidate output;
- complete workbench-native checkpoint validation across W1-W4;
- a typed adversarial-review disposition and return transition;
- automatic post-synthesis final-review admission;
- an operative campaign claim-authority chronology;
- deterministic projection and trace-linking of review units; or
- a validated machine-judgment contract and technical isolation record.

The candidate prompts mark the remaining unimplemented transitions as
`HOST_GAP`. Accepted-state planner re-entry is implemented; prompt prose still
cannot establish review-driven or user-correction re-entry. Activation of the
candidate suite requires executable changes and ordinary-path tests; prompt
prose cannot close them.

## Expert correction and scoped learning

A useful expert correction attaches to an exact transition:

```text
At this exact state, the system chose X.
The available cue Y should have caused Z instead.
```

The correction should preserve:

- the object corrected;
- the system choice;
- the cue available at the time;
- the expected alternative behaviour;
- decision impact;
- scope;
- validation needed; and
- rollback condition.

It may nominate a prompt, route, workbench, interface or policy intervention.
It does not apply one. No prompt edits itself.

## Reading and evaluation order

1. Read `evaluation-rubric.md`.
2. Read the protocol for the phase being tested.
3. Check its exact packet, workbench and output assumptions against the current
   host.
4. Test active and candidate under the same model, commission, cutoff,
   permissions, tools, budget, workbenches and evaluation protocol.
5. Treat schema and custody checks as mechanical evidence only.
6. Require a real material episode and later qualified-human judgment before
   making a research-quality or improvement claim.

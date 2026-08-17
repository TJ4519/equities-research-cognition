# Decision-Consequence Map V1

## Purpose and boundary

This is a candidate workbench for use after one exact Aggregate Driver V0
artifact and one exact Expectation Surfaces V1 artifact exist. It would answer
a narrow question: was one separately governed action contract bound to this
exact work order and, if so, does the complete declared uncertainty interval
remain in the no-action region, sit wholly inside one non-default region, or
span several regions?

The output is a candidate map. It is not a selected action, recommendation,
valuation, alpha claim, analyst judgment or outcome. A director must separately
approve the exact contract candidate and later dispose the resulting map.
Approving the W4 research instruction does not adopt planner-authored
thresholds. Only a future Campaign Studio contract-disposition record and exact
work-order join could establish positive authorization or authoritative
absence. The current product implements neither. Therefore this protocol cannot
presently emit an authorized region map or an authority-based
`NO_DECISION_THRESHOLD`; it must preserve `DECISION_AUTHORITY_UNAVAILABLE`.

## Required input

The following is the candidate `decision-consequence-input/v1` contract for a
future product-bound invocation:

- exactly one authority variant: either one exact
  `campaign-decision-contract-binding/v0` for a separately dispositioned
  `decision-contract-candidate/v0`, or one exact host-generated
  `campaign-decision-contract-absence/v0` copied from a future Campaign Studio
  work order;
- for the positive variant, the complete action set, horizon, metric, explicit
  maximum decimal precision, contiguous action regions, explicit no-action
  region, costs, reversal conditions, allowed next-discriminator candidates and
  mandatory human-disposition flag;
- for the absence variant, `decision_contract: null` and
  `relevance_model: null`; planner text, an empty invented contract or a
  role-authored absence token is invalid;
- the complete content-addressed `driver-state-patch/v0` artifact from one
  exact acknowledged W2 work order;
- the complete content-addressed `expectation-state-patch/v1` artifact from one
  exact acknowledged W3 work order;
- the `upstream_artifacts` array in canonical driver-state-patch then
  expectation-state-patch order, regardless of declared packet artifact-ID
  order, so the exact input digest is reproducible;
- one V0 relevance model only when the separately approved contract contains
  action regions; it is forbidden when the contract is absent or explicitly
  contains no action regions;
- one exact expectation-surface state; a fresh selected surface is required
  only for positive region mapping, not for the authority-absence refusal; and
- zero or more references to discriminator candidates already frozen in the
  approved contract and tied to diagnostic codes present in exact upstream
  artifacts. The work output cannot invent their text, projected range or kill
  condition after approval.

Research Frame supplies the epistemic ordering: observed signal, target
construct, proxy gap, rival generators, discriminator, then bounded decision
contribution. It does not upgrade the upstream claim. A Modes-of-Reasoning
invocation is legal only when it names one exact failure being tested, the
inputs it may inspect, the output it may alter, its expected epistemic delta and
its kill condition. Mode convergence is never evidence.

## Procedure

1. Recompute both complete upstream artifact digests and validate their exact
   producing-work-order and database-issued dependency binding. Reject detached,
   relabelled, substituted or partial copies. The product must later join every
   binding digest back to its authoritative PostgreSQL record.
2. Preserve the W2 and W3 claim ceilings and negative constraints. W4 may not
   turn units into demand, price/mix into pricing power, consensus into marginal
   belief, or attribution into sustainability.
3. Require one product-issued decision-authority variant. Because the current
   Campaign Studio issues neither a contract binding nor an authoritative
   absence object, stop with `DECISION_AUTHORITY_UNAVAILABLE`. Do not infer a
   threshold or authority absence from the commissioned question, planner
   instruction, arbitrary proposal JSON, or an attractive result. The remaining
   steps specify future behavior only after this product boundary exists.
4. Under a positive non-empty contract, refuse with
   `UPSTREAM_STATE_UNRESOLVED` when W2 is not `IDENTITY_TIED`, W3 is not
   `ROUTES_SEPARATED`, or the selected expectation route is absent or stale. Do
   not repair earlier work inside W4.
5. Compute only the V0 interval: exact reported revenue change multiplied by
   the complete declared relevance range. The relevance range is an exposed
   assumption, not evidence about demand or durability.
6. Refuse with `PRECISION_EXCEEDS_INPUTS` when a point is requested from a
   non-degenerate input interval or supplied decimal precision exceeds the
   contract maximum. Round any emitted interval outward at the declared
   precision before testing regions.
7. Emit `NO_ACTION_CHANGE` when the full interval remains inside the declared
   no-action region. This is an achieved negative decision result, not failed
   research.
8. Emit `THRESHOLD_CROSSED` only when the full interval lies inside one
   non-default region. Preserve the region and candidate action identifier but
   never emit a selected action.
9. Emit `MODEL_UNSTABLE` when the interval spans regions or the selected fresh
   expectation route is in an explicit route conflict.
10. A next discriminator may be emitted only when its identifier, unresolved
    fact, projected resolution range, expected delta and kill condition were
    frozen in the separately approved contract, it references an exact upstream
    diagnostic, and it is the sole candidate that moves the full interval into
    one different region. Preserve the explicit
    `EXACT_APPROVED_CONTRACT_CANDIDATE_NOT_EVIDENCE` authority label. Do not
    call it retrieved evidence or a discovered causal route.
11. Emit exact upstream version/digest/status/claim-ceiling lineage, the exact
    decision contract, assumptions, diagnostics and authority constraints.
    Append the conditional mapping or refusal to the complete host
    `investor-research-state/v1` journal; do not replace its evidence state with
    a recommendation-shaped summary.

## States

- `NO_ACTION_CHANGE`: the full declared interval remains in the no-action
  region.
- `THRESHOLD_CROSSED`: the full interval occupies one non-default candidate
  region; director disposition is still required.
- `NO_DECISION_THRESHOLD`: either no separately dispositioned contract was
  bound to the exact work order, or an approved contract explicitly contained
  no action regions; the diagnostic code preserves which basis applies.
- `DECISION_AUTHORITY_UNAVAILABLE`: the product cannot yet issue or verify the
  required decision-contract binding or authoritative absence object.
- `UPSTREAM_STATE_UNRESOLVED`: required W2 or W3 candidate state is unresolved.
- `MODEL_UNSTABLE`: the result depends on a region-spanning parameter range or
  a conflicting selected expectation route.
- `PRECISION_EXCEEDS_INPUTS`: requested precision is stronger than the input
  interval.
- contract failure: malformed schema, digest, lineage, region, unit,
  decimal, claim-ceiling or discriminator-reference contract.

## Native judgment checkpoint

The output carries one digest-bound `decision_relevance` candidate whose
subject, exact mandate, upstream lineage, answer and consequences reference
this same artifact. Preserve it unchanged. It is an elicitation point for
later expert judgment, not analyst authorship, action selection or outcome
evidence.
The singleton population contract rejects missing or additional checkpoints.

## Claim ceiling

This workbench licenses only a conditional replayable mapping from exact
candidate upstream state and explicit assumptions into separately approved action
regions. It cannot select an action, establish investment merit, produce alpha,
create analyst authorship, or prove that later work improved.

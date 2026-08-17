# Aggregate Driver Attribution V0

## Purpose and boundary

Use this workbench only after Comparable-State V0 has produced a governed
`COMPARABLE` state. It ties the exact change in one revenue identity to either
an exact two-factor PVM calculation or source-attributed components and exposes
the remainder as a residual.

An identity that ties is not a causal explanation. Units are not demand;
average revenue or price/mix is not pricing power; shipments are not
sell-through; channel timing is not sustainability; a residual is not a
mechanism.

## Required input

Prepare one exact `aggregate-driver-input/v0` object containing:

- one content-addressed exact `research-state-patch/v0` artifact containing the
  upstream status, authority, receipts, and two selected W1 fact records; its
  digest must reproduce from those complete artifact bytes, and the approved
  work order must carry that same acknowledged W1 artifact;
- when W1 used `issuer_recast`, the unchanged artifact must retain the original
  prior fact, the issuer assertion and zero-residual bridge, and the derived
  prior observation selected by `comparable_fact_set`; W2 preserves both the
  original-fact and bridge receipts and rejects analyst-authored or residual
  bridges as a comparable base;
- exact current/prior revenue values, unit, scale and used source receipts;
- either four exact receipt/locator-bound PVM factor records or a
  disclosed-component bridge;
- receipt-bound issuer assertions or explicit analyst assumptions for every
  disclosed component;
- exact receipt/locator-bound shipment, sell-through, inventory, backlog,
  bookings or returns observations when channel interpretation matters;
- the frozen public-evidence cutoff.

## Procedure

1. Reject a detached, relabelled or internally inconsistent W1 state artifact.
   Reject decomposition when its state is not `COMPARABLE`; do not repair W1
   inside W2.
2. Match current/prior revenue values and receipts to the exact observations,
   definitions and scopes inside the selected W1 artifact before calculating
   any driver identity. For a lawful issuer recast, use the exact derived prior
   observation selected by W1 without deleting its original source fact.
3. For `two_factor_pvm`, calculate and preserve:
   - unit-volume effect: change in units times prior average revenue;
   - price/mix effect: prior units times change in average revenue;
   - interaction: change in units times change in average revenue.
4. Call the second term `price_mix`; product/customer mix and realized price
   remain entangled. Never rename it pricing power.
5. For `disclosed_bridge`, retain each source-attributed component and its exact
   typed issuer assertion. An analyst allocation remains
   `analyst_assumption`, with author, rationale and change condition.
6. Calculate the residual as reported change minus exact components. Any
   non-zero residual produces neutral `RESIDUAL_NONZERO` and
   `UNDERIDENTIFIED`; deterministic software does not decide materiality and
   never allocates the residual by prose.
7. Preserve channel observations independently. Higher shipments with higher
   inventory keeps channel fill live, and absent sell-through stays visibly
   absent.
8. Apply the cutoff only to the exact receipt/indicator closure used by this
   identity.
9. Emit `driver-state-patch/v0` with exact inputs, calculated or disclosed
   components, residual, assumptions, diagnostics and immutable mechanism
   constraints. Append it to the complete host `investor-research-state/v1`
   journal without dropping or rewriting any accepted W1 receipt, reported
   fact, issuer assertion, bridge, derived observation, rival, or claim ceiling.

## States

- `IDENTITY_TIED`: exact components tie arithmetically with no analyst
  allocation. Mechanism and sustainability claims remain unlicensed.
- `UNDERIDENTIFIED`: a residual or analyst allocation remains.
- `UNDECOMPOSABLE`: upstream comparable-state legality is absent.
- `REJECTED`: used evidence violates the frozen cutoff.
- contract failure: malformed schema, reference, unit, decimal, or authority.

## Native judgment checkpoint

The output carries one digest-bound `decomposition_sufficiency` candidate whose
subject, exact inputs, answer and downstream consequences reference this same
artifact. Preserve it unchanged. It is an elicitation point for later expert
judgment, not analyst authorship or evidence that the decomposition is true.
The singleton population contract rejects missing or additional checkpoints.

## Claim ceiling

This workbench licenses only the recorded arithmetic identity, authority and
refusal. It cannot establish demand, pricing power, sell-through,
sustainability, causality, valuation, or an investment action. Those remain
candidate mechanisms for discriminating research and claim transition.

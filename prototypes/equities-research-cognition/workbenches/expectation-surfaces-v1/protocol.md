# Expectation Surfaces V1

## Purpose and boundary

Use this workbench to reconstruct which expectation routes were publicly
observable at one frozen cutoff. Keep issuer guidance, sell-side consensus,
narrative, positioning and model-implied routes separate.

There is no universal scalar called `market_expectation`. Consensus is a
vendor-constructed analyst surface, guidance is issuer-authored, narrative is a
language surface, positioning is a model-dependent exposure proxy, and a
model-implied value inherits its model assumptions. None alone establishes the
marginal investor's belief.

## Required input

Prepare one exact `expectation-surfaces-input/v1` object containing:

- one metric, period, basis, unit and scale contract;
- the public-evidence cutoff that governs admissibility and route freshness;
- an exact digest-bound maximum-age policy used only to label freshness;
- exact content-addressed source-receipt artifacts containing their publication
  date, origin family, assertion passages, locators and exact `as_of`;
- candidate origin-group projections whose membership must reproduce from the
  origin families inside those receipt artifacts;
- one or more route-specific surfaces with exact `as_of` dates;
- consensus mean, range, contributor count and dispersion together;
- guidance ranges without recasting them as consensus;
- an exact per-surface metric contract for every numeric fundamental route;
- explicit model ID, version, input cutoff, assumptions and output meaning for
  positioning or model-implied routes, joined to one exact model-output
  artifact whose bytes contain the exact model result and an output-value
  digest over that result.

## Procedure

1. Bind every surface to assertion text, locator and `as_of` already present in
   the exact content-addressed source artifact under its legal source origin:
   issuer guidance, consensus-vendor snapshots, narrative sources, market-data
   positioning, or market/model inputs.
2. Reject any used receipt, surface timestamp, or model input after the cutoff.
   A surface timestamp must match its exact receipt-bound assertions.
3. Require the exact V0 fourteen-day operational freshness policy and preserve
   it in the output. `STALE` is a property of that surface at the cutoff, not
   proof that investors ignored it or that fourteen days is universally right.
4. Preserve consensus dispersion and contributor count. Never replace a range
   with its mean in prose.
5. Reject a numeric surface whose metric, period or basis differs from the
   commissioned metric contract. Compare remaining numeric routes only when
   they share that exact contract. A
   non-overlap becomes `ROUTE_CONFLICT`, not a decision about which route is
   correct.
6. Reconstruct repeated source-origin groups from the origin family frozen in
   each receipt artifact across the complete used set, even when same-origin
   receipts are split across surfaces. Origin-family attribution remains a
   candidate custody fact, not proof of source independence.
7. Preserve model dependence for positioning and model-implied routes. Require
   an exact model-output artifact whose frozen result equals the surface, plus
   its receipt digest, assertion locator and canonical result digest; do not
   translate implied volatility, open interest, or crowding into a fundamental
   revenue forecast.
8. Emit the cutoff, policy, origin-group contracts, exact
   `surface_states`, pairwise route conflicts, diagnostics and claim constraints.
   Append the complete result and source closure to the host
   `investor-research-state/v1` journal without rewriting accepted upstream
   state. Do not emit a single market-expectation value.

## States

- `ROUTES_SEPARATED`: at least one guidance, consensus, or explicitly model-
  implied fundamental surface is preserved; routes may still conflict or be
  stale.
- `INSUFFICIENT_EXPECTATION_EVIDENCE`: only narrative or positioning surfaces
  exist for the metric contract.
- `REJECTED`: used evidence or a model input violates the cutoff.
- contract failure: malformed schema, source authority, metric, range,
  decimal, or missing model contract.

## Native judgment checkpoints

The output carries one digest-bound `expectation_freshness` candidate per exact
surface. Each subject, input, answer and consequence reference remains inside
this artifact. Preserve them unchanged. They are elicitation points for later
expert judgment, not analyst authorship or evidence that any surface represents
the market's belief.
The exact population contract rejects any missing, extra or detached surface.

## Claim ceiling

The output licenses only route identity, timestamps, freshness under the
declared policy, dispersion, origin collapse and explicit pairwise conflict. It
does not license one market expectation, marginal-investor belief, surprise,
causality, valuation, or an investment action.

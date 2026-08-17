# Comparable-state reconstruction V0

## Purpose and boundary

Use this workbench to decide whether two exact, point-in-time financial or operating facts may enter one comparable fact set. It enforces definition, scope, period, unit, cutoff, bridge, residual and assumption custody.

It does not decide why a metric changed. A `COMPARABLE` result is a candidate input to later research; it is not evidence of demand, pricing power, channel health, market expectations, valuation, or an investment action. `INCOMPARABLE`, `UNRECONCILED`, and `REJECTED` are successful outcomes when the evidence cannot license comparison.

## Required input

Prepare one exact `comparable-state-input/v0` JSON object. Preserve:

- source receipt identity, artifact digest, locator, origin and publication date;
- evidence cutoff;
- exact metric definition and basis, separately bound to each observation receipt;
- entity, consolidation, segment, geography, operating and acquisition scope, separately bound to each observation receipt;
- period kind, dates and inclusive duration;
- unit, integer scale and canonical decimal value;
- the exact left/right pair requested;
- any issuer recast or analyst-assumption bridge as an explicit object;
- for an issuer recast, the exact typed assertion text and locator bound to one
  issuer-origin receipt in the bridge evidence closure.

The same label or taxonomy concept is not a definition bridge. A file path is not source authority. Do not invent a missing split or translate a residual into a mechanism.

## Procedure

1. Assemble source receipts, then calculate the exact receipt closure used by
   the requested pair and any bridge. A used later recast is blocked even if it
   would make the comparison easier; an unrelated unused receipt does not veto
   a lawful comparison and is not emitted as evidence.
2. Bind each observation to definition and scope records from that observation's own receipt. Preserve distinct record identities across periods, then compare their exact semantic fields. Reusing one period's identity for another period is an authority failure even when the text is believed to be unchanged.
3. Apply this version-pinned contract to the exact JSON object and preserve
   every legality failure as an explicit refusal. No standalone validator is
   shipped in this package. Mechanical regressions may exercise its
   deterministic boundary, but neither a fixture nor agent compliance creates
   cognition or research truth.
4. If dimensions differ and no exact bridge exists, preserve `INCOMPARABLE` with the named mismatch. V0 does not implement currency or unit conversion, so a unit mismatch cannot be bridged. Do not smooth the difference in prose.
5. Accept an issuer recast only with issuer-origin receipts and an
   `issuer_comparable_recast` assertion preserving the exact receipt, locator
   and asserted passage. This is custody of a candidate source assertion, not
   validation that the assertion is true. Accept an analyst bridge only as
   `analyst_assumption`, with no issuer assertion and with author, rationale and
   a change-of-mind condition.
6. Tie bridge arithmetic in base units. Preserve every non-zero residual as `UNRECONCILED`.
7. Emit the exact `research-state-patch/v0`, and append its complete records to
   the host `investor-research-state/v1` journal: every used receipt, both full
   observation/definition/scope records, the full bridge, and any typed derived
   observation. The generic journal is custody and handoff, not a competing W1
   validator. Downstream work may use a comparable fact set only when status is
   `COMPARABLE`; it must retain the authority, assertion, assumptions, residual
   and claim ceiling. `INCOMPARABLE`, `UNRECONCILED`, and `REJECTED` outputs
   retain their exact failed candidate state for diagnosis.

## Refusal and failure states

- `INCOMPARABLE`: definition, scope, period or unit differs without a complete exact bridge.
- `UNRECONCILED`: a lawful bridge has a non-zero disclosed residual.
- `REJECTED`: at least one used receipt violates the evidence cutoff.
- contract failure: malformed schema, reference, period, decimal, authority,
  target, or arithmetic. Do not repair these silently.

## Native judgment checkpoint

The output carries one digest-bound `metric_comparability` candidate whose
subject, exact inputs, answer and downstream consequences reference this same
artifact. Preserve it unchanged. It is an elicitation point for later expert
judgment, not analyst authorship or evidence that the candidate answer is true.
The singleton population contract rejects missing or additional checkpoints.

## Claim ceiling

The only licensed claim is that the exact facts are contractually comparable
under the recorded reported, issuer-recast or analyst-assumption authority, or
that the exact contract refuses comparison. Every source assertion, mechanism
and investment conclusion remains a candidate for a later, separately governed
work order.

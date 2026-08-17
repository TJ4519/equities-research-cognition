# Machine judgment candidate

## Purpose

Produce one bounded model judgment over one exact sealed decision point for
later comparison with a separately authenticated analyst judgment.

This protocol is an optional evaluation sidecar. It is not part of ordinary
research production, expert authorship, claim authority or policy learning.

Use a technically isolated context for any blind or independent comparison. A
contract may define a separately labelled non-isolated diagnostic condition,
but that result must preserve its exposure status and must never be represented
as blind or independent.

## Required case-specific contract

Proceed substantively only when the exact approved `packet.contract` contains a
`judgment_contract` that identifies:

- one stable decision point;
- contract ID, version and digest;
- exact subject and input-closure digests;
- investor mandate, horizon and decision hinge;
- allowed substantive choices;
- explicit `abstain` and `wrong_task` criteria;
- exact reference-standard ID, version and digest;
- allowed recommendation destination or choice-to-consequence class that does
  not reveal the expected answer; and
- required exposure/isolation status.

The materialized `packet.inputs` must also contain host-issued validation and
exposure records that bind the approved contract, proposal, subject, closure,
reference standard and isolation status by exact identity and digest.

The current host does not define or validate those records. Under the current
ordinary packet, substantive machine judgment is therefore a `HOST_GAP` and the
lawful result is `REFUSED`.

Do not reconstruct a missing contract from `task`, required reads, a synthesis,
a rubric, memory or ambient context.

## Absolute exclusions

The allowed input closure must not contain:

- protected evaluation material or any derivative;
- post-lock analyst diagnosis or corrected judgment;
- another human or machine judgment about the unit;
- retrieved lesson suggestions;
- similarity scores, rankings or cluster labels; or
- the expected answer disguised as a downstream consequence.

If any appears, return a contamination refusal. A later post-lock reveal is a
different governed process.

## Authority

You may return exactly one status:

- `DECIDED`: one allowed substantive choice is supported at the exact reference
  standard;
- `ABSTAINED`: the task and closure are valid, but the evidence does not support
  a substantive choice;
- `WRONG_TASK`: the subject is outside the decision point, combines incompatible
  units or requires another role; or
- `REFUSED`: the dispatch, contract, closure, reference standard, exposure
  state or output contract is invalid.

You may recommend a later disposition only when the contract permits it and
only as `recommendation_only`.

You may not:

- synthesize the campaign;
- change research or claim state;
- author analyst judgment or correction;
- create memory, a lesson, an intervention, evaluation placement or policy;
- inspect another judgment; or
- treat model agreement as validation.

## Judgment procedure

1. Verify the exact contract, subject, closure, reference standard and exposure
   records.
2. Preserve the supplied exposure status exactly. Do not self-certify blindness
   or independence. Refuse when the status does not satisfy the contract. A
   contract that explicitly permits a non-isolated diagnostic candidate must
   keep that candidate outside blind-comparison claims.
3. Apply only the exact reference standard to the exact subject and evidence
   closure.
4. Choose `DECIDED`, `ABSTAINED`, `WRONG_TASK` or `REFUSED`.
5. Cite only evidence inside the allowed closure.
6. State concise rationale, uncertainty, strongest alternative, counterfactual
   and what would change the answer.
7. Keep the candidate sealed from the analyst until the analyst's separately
   authenticated first judgment is locked.

Exact evidence references and a concise warrant are sufficient. Do not output
private chain-of-thought.

## Machine output: `judgment.json`

Write one `machine-judgment-candidate/v1` object containing:

```text
authority: model_candidate
status: DECIDED | ABSTAINED | WRONG_TASK | REFUSED
contract identity and digest
reference-standard identity and digest
subject and input-closure digests
preserved exposure status and validation reference
allowed choices
substantive decision only when DECIDED
reason code and affected references for every non-decision
exact evidence references
concise rationale
uncertainty
strongest alternative
counterfactual
what would change the answer
optional recommended_disposition_candidate:
  authority: recommendation_only
  destination or consequence class from the approved contract
```

A `REFUSED` object contains no substantive decision and no recommendation.

Use reason codes that make the failure operational, including:

- `CONTRACT_UNAVAILABLE_OR_INVALID`;
- `SUBJECT_OR_CLOSURE_MISMATCH`;
- `REFERENCE_STANDARD_UNAVAILABLE_OR_INVALID`;
- `PROTECTED_MATERIAL_PRESENT`;
- `OTHER_JUDGMENT_PRESENT`;
- `REQUIRED_ISOLATION_NOT_PROVEN`;
- `EXPOSURE_STATUS_NOT_PERMITTED_BY_CONTRACT`; or
- `OUTPUT_CONTRACT_INCOMPATIBLE`.

This output is never expert judgment. After a later analyst lock, disagreement
between machine and analyst is diagnostic evidence about the system's judgment
process, not evidence that either answer is automatically correct.

## Exact output custody

The current semantic output is exactly `judgment.json`.

Read `packet.output_contract`. Write only beneath its exact `output_root`.
After the judgment or typed refusal is final, write
`artifact-attestation.json` last using the current
`work-order-artifact-attestation/v1` contract. Do not modify either file after
attesting.

The host must independently verify custody, enforce isolation and keep the
machine candidate hidden before analyst lock. Prompt language cannot establish
those properties.

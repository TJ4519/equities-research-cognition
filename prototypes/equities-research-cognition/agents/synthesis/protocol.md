# Equities research synthesis

Synthesize only exact director-selected artifacts whose claim ceilings are
still live. Preserve contradictions, negative evidence, source dependence,
refusals, and unresolved rival mechanisms.

Write `synthesis.md` with:

- what changed the working view and why;
- claims and exact supporting artifact references;
- what remains contested or underidentified;
- decision implications sized to evidence strength;
- no-action conditions, forbidden conclusions, and update triggers;
- the next discriminating information, if any.

Do not strengthen claim status, infer truth from agreement, hide a blocker, or
turn the commissioned decision into an agent-selected action. If the evidence
cannot support a decision-complete packet, return a concise refusal.

## Exact output custody

Read `packet.output_contract`. Write every `required_paths` file, and write
nothing outside its exact absolute `output_root`. After every output is final,
write `artifact-attestation.json` last as canonical JSON with exactly:
`schema_version` = `work-order-artifact-attestation/v1`, `campaign_id`,
`work_order_id`, `logical_role_id`, `authority` =
`worker_candidate_attestation`, and `artifacts`. `artifacts` is the
relative-path-sorted list of every other output with exact `relative_path`,
`byte_length`, and lowercase SHA-256. Do not include trace, observation,
conversation, or provider identifiers. Do not modify outputs after attesting.

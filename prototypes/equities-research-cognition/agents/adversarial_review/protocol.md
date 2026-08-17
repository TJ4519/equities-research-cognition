# Adversarial research review

Attack only the director-named state and artifacts. Load the exact selected
reasoning operator, then use only its named failure test, allowed epistemic
delta, and kill condition. Fail rather than substituting a different operator.

Check:

- source-to-claim fit and source-origin independence;
- proxy/target substitution and post-cutoff leakage;
- rival mechanisms dismissed without discriminating evidence;
- comparability, driver, expectation, or decision assumptions promoted into
  fact;
- synthesis that is compliant but decision-useless;
- files, traces, software checks, or model agreement presented as authorship,
  truth, analyst judgment, or outcome evidence.

Write `review.md` with exact state/artifact passages, strongest counterexample,
decision `PASS`, `NARROW`, `BLOCK`, or `RESEARCH`, and the smallest affected
claim or research step. Preserve the candidate state unchanged. A further step
is only a proposal in `proposals.jsonl`; it cannot dispatch itself. Do not
repair the state or report silently.

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

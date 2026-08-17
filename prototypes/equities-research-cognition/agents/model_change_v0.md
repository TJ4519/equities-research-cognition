# Captured-source model change protocol v0

You receive one immutable work-order packet. Read the packet and every exact
`required_reads` path, verify every recorded SHA-256, and use only the
materialised `job_input_files`. Network access is closed. Do not retrieve,
infer, or cite any source that is not captured in the packet.

Return exactly three regular files at the output root named by
`output_contract`: `model-change-output.json`, `run-acknowledgement.json`, and
`artifact-attestation.json`. Do not write subdirectories or additional files.

The acknowledgement must be exactly:

```json
{
  "schema": "model-change-run-acknowledgement/v0",
  "episode_id": "<packet episode.id>",
  "episode_digest": "<packet episode.sha256>",
  "work_order_id": "<packet work_order_id>",
  "closure_digest": "<packet closure_digest>",
  "inputs": "<packet job_inputs, copied as JSON>",
  "network_policy": "closed_captured_sources"
}
```

Produce one proposal only when an exact captured source assertion supports the
reported value. Host-issued identities and digests must be copied exactly; you
may not create or reinterpret them. The proposal must contain exactly:

```json
{
  "schema": "model-change-proposal/v0",
  "episode_id": "<packet episode.id>",
  "episode_digest": "<packet episode.sha256>",
  "input_revision": 1,
  "conceptual_object_id": "<packet conceptual_object.id>",
  "conceptual_object_digest": "<packet conceptual_object.sha256>",
  "starting_artifact_id": "<packet starting_artifact.id>",
  "starting_artifact_digest": "<packet starting_artifact.sha256>",
  "source_assertion_id": "<one packet source_assertions id>",
  "operation": {
    "kind": "set_numeric_value",
    "target_ref": "<packet manifest.target_ref>",
    "value": "<exact assertion value>",
    "unit": "<exact assertion unit>"
  },
  "claim_ceiling": "<packet conceptual_object.claim_ceiling>"
}
```

For this controlled episode, select the captured 8-K assertion when it contains
the reported value required by the requested target. Source suitability is not
yours to decide; the deterministic host gate handles it after custody. Do not
change the workbook and do not calculate a candidate.

If the exact packet cannot support that proposal, return exactly:

```json
{
  "schema": "model-change-refusal/v0",
  "episode_id": "<packet episode.id>",
  "reason": "<bounded reason>"
}
```

Finally create `artifact-attestation.json` using
`work-order-artifact-attestation/v1`, the packet campaign/work-order/logical-role
identities, authority `worker_candidate_attestation`, and exact sorted rows for
the other two output files with relative path, byte length, and SHA-256.

# Bound work protocol

Work only from the exact work-order JSON you receive. Read every required file,
verify every stated SHA-256 digest, and stop if an identity, byte digest, or
instruction does not match. Treat native artifacts as opaque unless the
available tools actually support their format; never claim parsing,
recalculation, formula preservation, adoption, or release merely because bytes
were supplied.

Before doing the requested work, write `run-acknowledgement.json` with exactly:

```json
{
  "schema_version": "bound-run-acknowledgement/v1",
  "campaign_id": "<exact campaign_id>",
  "run_spec_id": "<exact run_spec.id>",
  "run_spec_sha256": "<exact run_spec.sha256>",
  "work_order_id": "<exact work_order_id>",
  "inputs": [{"id": "<exact input id>", "sha256": "<exact input digest>"}]
}
```

The input rows must match `job_inputs` exactly and in the same order. This is a
semantic acknowledgement of the job being attempted, not a transport receipt.

Write one `outcome.json`. It must be either a provisional candidate:

```json
{
  "schema_version": "bound-run-outcome/v1",
  "kind": "candidate",
  "authority": "provisional_only",
  "summary": "<bounded description>",
  "candidate": {},
  "refusal": null
}
```

or a bounded refusal:

```json
{
  "schema_version": "bound-run-outcome/v1",
  "kind": "refusal",
  "authority": "provisional_only",
  "summary": "<what could not be done>",
  "candidate": null,
  "refusal": "<specific missing capability, evidence, or authority>"
}
```

For a candidate, `candidate` must be a JSON object representing only the
proposed result. It is never adopted state. For a refusal, `refusal` must be a
specific non-empty explanation. Do not emit both. Finally write the standard
artifact attestation over these two files.

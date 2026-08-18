# Worker Packet 013 — Codex Stale Trust Cleanup

Status: **authorised environment cleanup; no Codex or product execution**.

Programme state: `REPAIRING`.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Packet 012 branch: `agent/codex-output-root-trust-control-v0`
- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Packet 012 receipt: `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`
- Governing contract: `docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`
- Cleanup branch: `agent/codex-stale-trust-cleanup-v0`
- Required receipt: `docs/pro/evidence/CODEX_STALE_TRUST_CLEANUP_RECEIPT.md`

The exact starting head is recorded in the issue and current checkpoint because the packet cannot contain the hash of the commit that contains itself.

## Assignment

Remove exactly the stale Packet 012 trusted-project stanza from the user's current Codex config under the hash-guarded, byte-preserving and recoverable procedure in the governing contract.

Do not run Codex, NTM, a runtime control or Case A. This assignment restores user configuration only.

## Required read order

1. root and package `AGENTS.md` and `ROUTE.md`;
2. `PRO_RESPONSIBILITY_PROMPT.md`;
3. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`;
4. `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md` at `32259dd...`;
5. `docs/pro/evidence/MILESTONE_2_PACKET_012_REJECTION_ADJUDICATION_RECEIPT.md` from PRO;
6. `docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`;
7. current decision ledger and checkpoint; and
8. this packet.

Do not inspect unrelated config values beyond what is required to identify and remove the exact stale stanza.

## Repository ownership

The worker may add exactly one repository file:

`docs/pro/evidence/CODEX_STALE_TRUST_CLEANUP_RECEIPT.md`

No existing repository file may change.

## Local mutation authority

The worker may mutate exactly one local persistent file:

- the active Codex user `config.toml` resolved from the current `CODEX_HOME`.

It may create exactly one private temporary backup directory and its before-image as specified by the contract.

No other local persistent file or directory is owned.

## Exact preconditions

Before mutation, require all of:

```text
regular file = true
symlink = false
owner = effective UID
mode = 0600
size = 13912
sha256 = 4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
```

Abort with `PRECONDITION_MOVED` if any value differs.

## Exact cleanup proof

Identify one and only one final trusted project stanza whose decoded path:

- is absent from the filesystem;
- structurally ends `work/<uuid>/out`;
- contains exactly `trust_level = "trusted"`; and
- when removed byte-for-byte yields:

```text
size = 13784
sha256 = 0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
```

Do not publish the raw path. Record its SHA-256 and structural suffix only.

## Backup and rollback

Create a private `0700` temporary directory and exact `0600` before-image. Verify the backup hash equals the current post-control hash before writing the config.

Use an atomic same-directory replacement for the cleaned config. If any post-write check fails, restore the exact backup atomically and verify the post-control hash and size. Return `ROLLBACK_RESTORED`; do not attempt a second mutation.

Retain the backup until coordinating Codex independently verifies the cleanup. The receipt must state the retention rule without exposing its raw path.

## Postconditions

Successful cleanup requires:

```text
regular file = true
symlink = false
owner = effective UID
mode = 0600
size = 13784
sha256 = 0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
strict TOML parse = pass
stale project path = absent
backup hash = 4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
```

The known pre-control hash is the proof that every unrelated byte is unchanged.

## Prohibited actions

Do not:

- run `codex`, `ntm` or product code;
- launch a neutral control or Case A;
- inspect credentials, tokens or unrelated project entries;
- print or commit the raw config or stale path;
- parse and reserialize the whole file;
- remove more than one stanza;
- update another Codex file, config, rule, SQLite database, skill or plugin;
- change repository code, tests, prompt, model, UI, schema, classifier or Excel surfaces;
- update governance, issues or PRs; or
- merge or deploy.

## Stop conditions

Return without mutation when:

- the whole-file precondition moved;
- the file is a symlink, wrong owner or wrong mode;
- the stale stanza is absent or ambiguous;
- deleting the candidate stanza does not reproduce the exact pre-control bytes;
- a safe backup cannot be created; or
- any unrelated edit appears necessary.

## Return

Commit only the receipt and return one verdict:

- `CLEANUP_PASS_FOR_INDEPENDENT_VERIFICATION`;
- `PRECONDITION_MOVED`;
- `AMBIGUOUS_STALE_ENTRY`;
- `ROLLBACK_RESTORED`; or
- `FAIL`.

## Claim ceiling

Success proves only exact restoration of the Packet 012 config mutation. It does not prove a safe launcher, automation process, Case A, product integration, verified V0, analyst validation, Excel support, professional reliance, deployment, client readiness or completion.

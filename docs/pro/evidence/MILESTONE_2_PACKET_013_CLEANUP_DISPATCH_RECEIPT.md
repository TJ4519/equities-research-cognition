# Milestone 2 Packet 013 Cleanup Dispatch Receipt

Programme state: `REPAIRING`.

Dispatch status: `ACTIVE_ENVIRONMENT_RESTORATION_ONLY`.

Recorded: 18 August 2026.

## Exact basis

- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Packet 012 independent verdict: `REJECT`
- Cleanup contract: `docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`
- Contract blob: `327c8a70d813eea1cda35a1853d663d636de3059`
- Packet: `docs/pro/worker-packets/013_CODEX_STALE_TRUST_CLEANUP.md`
- Packet blob: `6049039485a70c6739db38e22800c1f7bec3133f`
- Worker branch: `agent/codex-stale-trust-cleanup-v0`
- Exact starting head: `1a0e4a5b838cfa1ed4b5dc401cce8a7b668934bd`
- Coordination: GitHub issue `#12`

## Branch audit

The worker branch is a non-force-pushed descendant of `32259dd...`. Its net diff from that evidence head is exactly:

```text
A  docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md
A  docs/pro/worker-packets/013_CODEX_STALE_TRUST_CLEANUP.md
```

The contract and packet blobs match the governing PRO copies.

## Authority

Packet 013 may:

- verify the active config's exact whole-file precondition;
- create one private `0700` backup directory and exact `0600` before-image;
- remove exactly one stale trusted-project stanza when its deletion reconstructs the exact pre-control bytes;
- atomically replace or roll back the exact active config;
- retain the backup for independent verification; and
- add only `docs/pro/evidence/CODEX_STALE_TRUST_CLEANUP_RECEIPT.md` to its branch.

It may not run Codex, NTM, a neutral control, product code or Case A. It may not inspect or change unrelated config, credentials, rules, skills, plugins or repository files.

## Hard hashes

Mutation authority exists only while the config is:

```text
size    13912
sha256  4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
mode    0600
owner   effective UID
```

Success requires exact restoration to:

```text
size    13784
sha256  0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
mode    0600
owner   effective UID
TOML    valid
```

## Next gate

Coordinating Codex independently verifies the cleanup, backup and absence of unrelated mutation. Packet 014 remains blocked until that acceptance.

## Evidence ceiling

This receipt authorises one exact cleanup. It does not establish cleanup success, a safe runtime process, Case A execution, end-to-end product, integration, verified V0, analyst validation, Excel support, professional reliance, deployment, client readiness or programme completion.

# Codex Stale Trust Cleanup Contract V0

Packet 012 is rejected because the live Codex process persisted an invocation-supplied output-root trust entry into the user's Codex configuration. This contract authorises only the exact restoration of that one stale entry.

Status: governing bounded environment-repair contract.

Programme state: `REPAIRING`.

## 1. Exact evidence basis

- Packet 012 branch: `agent/codex-output-root-trust-control-v0`
- Packet 012 starting head: `dd093113525645383e17cd51e7a1cff8592a624e`
- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Worker receipt: `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`
- Worker verdict: `CONTROL_REACHED_RUNTIME_BUT_FAILED`
- Independent verdict: `REJECT`
- Coordinator projection: `dec-2026-08-18-045`

The config mutation is supported by the following exact whole-file observations:

| State | Size | SHA-256 |
| --- | ---: | --- |
| Before Packet 012 live Codex process | `13,784` | `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9` |
| Current post-control file | `13,912` | `4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5` |

The current mode was independently observed as `0600`. The stale table is the final trusted `projects` entry for the deleted Packet 012 control output path.

## 2. Completion object

Restore the user's Codex config to the exact pre-control bytes by removing only the stale Packet 012 project-trust stanza, while preserving a recoverable before-image and refusing any ambiguity.

The authorised sequence is:

```text
open exact config without following symlinks
-> verify owner, mode, size and whole-file hash
-> identify exactly one terminal stale project stanza locally
-> prove the trusted path no longer exists
-> prove deleting only that stanza yields the exact pre-control size and SHA-256
-> create a recoverable 0600 before-image in a private 0700 temporary directory
-> parse the candidate TOML
-> atomically replace the config
-> verify exact pre-control bytes, owner, mode and TOML parse
-> retain the before-image for independent verification and rollback
```

Anything less is not cleanup success.

## 3. Exact stale-entry identity

The raw user path and unrelated configuration must not be copied into the public repository, issue, logs, or receipt.

The stale entry is nevertheless exact. It is the sole byte range satisfying all of these predicates:

1. it is the final top-level `projects` table added after the pre-control file;
2. its key decodes to the deleted Packet 012 control output directory;
3. its table contains exactly `trust_level = "trusted"` and no unrelated setting;
4. `lstat` of the decoded path returns `ENOENT`;
5. removing that exact stanza and no other byte produces exactly `13,784` bytes; and
6. the resulting whole-file SHA-256 is exactly `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9`.

If zero or more than one candidate satisfies the predicates, abort without mutation.

The public receipt may record only:

- SHA-256 of the UTF-8 stale path;
- the structural suffix `work/<uuid>/out`;
- confirmation that the path was absent; and
- the exact stanza byte length.

It must not expose the home path or any unrelated config key/value.

## 4. Preconditions

Before reading content, the executor must verify that the target:

- is the exact current Codex user `config.toml` resolved from the active `CODEX_HOME`;
- is a regular file and not a symlink;
- is owned by the effective UID;
- has mode exactly `0600`;
- has size exactly `13,912`; and
- has SHA-256 exactly `4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5`.

No write is authorised when any precondition differs. A changed hash is not a request to infer the new intended state.

## 5. Recoverable before-image

Before the config is changed:

1. create one private temporary directory using the operating system's secure temporary-directory mechanism;
2. set and verify its mode as `0700` and owner as the effective UID;
3. write `config.toml.before` with the exact current `13,912` bytes;
4. set and verify backup mode `0600` and owner as the effective UID;
5. `fsync` the backup file and directory where supported; and
6. verify backup SHA-256 `4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5`.

The raw backup path remains in private coordinator state. The public receipt records only a salted or session-specific path digest and backup hash.

The backup must remain available until independent verification accepts the cleanup. It may then be securely deleted. If post-write verification fails, the executor must atomically restore the exact backup and verify the post-control hash and size before returning failure.

## 6. Byte-preserving mutation

Do not parse and reserialize the whole TOML file.

The executor must remove the exact stale stanza from the original byte sequence. Before writing, the candidate bytes must:

- be exactly `13,784` bytes;
- hash to `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9`;
- parse successfully with the platform Python `tomllib` or another strict TOML 1.0 parser; and
- omit the exact stale path while preserving every other byte.

The known pre-control whole-file hash is the proof that all unrelated bytes are unchanged.

## 7. Atomic replacement and verification

Write the candidate to a new regular file in the same config directory, with mode `0600` and effective-UID ownership. `fsync` it, atomically replace the original, and `fsync` the parent directory where supported.

After replacement, verify:

- regular file, no symlink;
- effective-UID ownership;
- mode `0600`;
- size `13,784`;
- SHA-256 `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9`;
- strict TOML parse succeeds;
- the stale path is absent; and
- the backup still matches the exact post-control bytes.

Allowed metadata changes are limited to those inherently caused by atomic replacement, such as inode, ctime and mtime. Content, mode and ownership must match this contract.

## 8. Prohibited actions

Do not:

- edit any other Codex config, rule, credential, SQLite, skill, plugin or project file;
- print, upload or commit the config contents;
- print or commit the raw stale path;
- normalize, reorder or reformat TOML;
- remove another project trust entry;
- change authentication, models, MCP servers, hooks, approvals or sandbox settings;
- run Codex, NTM, a neutral control or Case A;
- modify repository product code;
- merge, deploy or advance Packet 009 or Excel work; or
- infer authorisation from a near-matching hash.

## 9. Required receipt

Create only:

`docs/pro/evidence/CODEX_STALE_TRUST_CLEANUP_RECEIPT.md`

The receipt must state:

- exact contract, packet, branch and repository head;
- precondition result;
- before and after size/hash/mode/owner checks;
- stale path SHA-256 and structural suffix only;
- stanza byte length;
- proof the path was absent;
- backup hash/mode and private-retention decision;
- strict TOML parse result;
- atomic replacement result;
- rollback result if invoked;
- confirmation that no Codex/NTM process ran; and
- one verdict: `CLEANUP_PASS_FOR_INDEPENDENT_VERIFICATION`, `PRECONDITION_MOVED`, `AMBIGUOUS_STALE_ENTRY`, `ROLLBACK_RESTORED`, or `FAIL`.

## 10. Claim ceiling

A successful cleanup proves only that the exact Packet 012 stale project-trust stanza was removed and the user config was restored byte-for-byte to its recorded pre-control state.

It does not prove a safe Codex automation process, runtime reliability, Case A success, product integration, verified V0, analyst validation, native Excel support, professional correctness, permission to rely, deployment, client readiness or product completion.

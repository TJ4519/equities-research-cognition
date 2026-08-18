# Codex Output-Root Trust Repair Contract V0

Packet 011 established that Codex stops before reading an instruction when `--cd` points to a standalone output directory that is not covered by the process's project-trust overrides.

Status: governing bounded runtime repair.

Programme state: `REPAIRING`.

## 1. Exact basis

- Diagnosis evidence head: `b6735692418af7861b170e8e2eb0a1b438c71fcb`
- Diagnosis receipt: `docs/pro/evidence/JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY_RECEIPT.md`
- Diagnosis verdict: `EXTERNAL_RUNTIME_BLOCKER`
- Packet 010 implementation: `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`
- Packet 010 evidence head: `a7df89f22f1783b529d9f31654234ed6de82eb62`
- Current launcher implementation: `product/campaign/services.py::_control_files`

The repair is a launch-boundary change. It is not a product-prompt, source-custody, workbook, interface, or agent-topology change.

## 2. Observed defect

The model-change launcher currently uses:

```text
--sandbox workspace-write
--ask-for-approval never
--cd <exact per-work-order output root>
-c projects."<repository root>".trust_level="trusted"
```

When the output root is outside the repository Git project, Codex treats the actual working directory as untrusted and presents an interactive trust question. NTM cannot answer it, so noninteractive execution fails before the instruction is consumed.

Packet 008 succeeded when its output root happened to be inside the trusted repository project. Packet 010 and the Packet 011 neutral control used standalone output roots and failed at the trust gate.

## 3. Completion object

A fresh neutral NTM/Codex control must start in a standalone host-created output root, consume one tiny instruction, read one exact local token, and write one exact JSON result without any interactive trust question.

The repair succeeds only when:

```text
host validates one exact output root
-> launcher passes process-local trust for that exact working directory
-> Codex starts with workspace-write and approval never unchanged
-> neutral instruction is consumed
-> exact result.json is written beneath that root
-> no persistent trust/config state changes
-> session and disposable root are cleaned up
```

A green unit test without the live neutral control is insufficient. A successful control does not authorise or prove the Case A product replay.

## 4. Least-privilege trust law

For `model_change_v0` only, launcher construction may add a runtime `-c` override for the exact canonical output root used by `--cd`.

The override must be equivalent to:

```text
-c projects."<exact canonical output root>".trust_level="trusted"
```

It must be supplied only on that Codex process invocation. It must not be written to:

- `~/.codex/config.toml`;
- any project `.codex/config.toml`;
- environment-wide managed configuration;
- NTM global configuration; or
- any persistent trust registry.

The existing exact repository-root trust override may remain for compatibility with prior nested-output execution, but the launcher may not trust a common parent merely to cover both paths.

Forbidden trust targets include:

- `/tmp` or another temporary-filesystem root;
- `CAMPAIGN_ROOT`;
- the campaign artifact root;
- the user's home directory;
- the repository parent;
- a wildcard, prefix, glob, or unresolved path;
- a symlink target discovered after launcher compilation; and
- any path not equal to the exact current work-order output root.

## 5. Output-root validation

Before launcher bytes are created, the exact output root must already satisfy the existing execution contract and be rechecked as:

- absolute and resolved;
- an existing directory;
- not a symlink;
- equal to `order.packet.output_contract.output_root`;
- beneath the exact current campaign artifact root;
- dedicated to the current work order;
- owner-only according to the existing output-root preparation contract; and
- not the repository root, campaign root, home, or filesystem root.

The launcher digest must change when the exact output root changes. A launcher frozen for one work order cannot be reused to trust another output root.

## 6. Security properties preserved

The repair must preserve exactly:

- `--sandbox workspace-write`;
- `--ask-for-approval never`;
- `--cd <exact output root>`;
- no `--search` for `model_change_v0`;
- the pinned Codex binary and model;
- NTM's existing allowlisted subprocess boundary;
- read-only materialised inputs;
- output restricted to the exact output root;
- existing runtime identity and authentication;
- no credential inspection or copying; and
- no product instruction, packet schema, source policy, or artifact semantics change.

Do not replace the repair with `danger-full-access`, `--add-dir`, a broader writable workspace, a human click, or a persistent trust grant.

## 7. Deterministic tests

Focused tests must prove:

1. a standalone model-change output root receives an exact process-local trust override matching the `--cd` path;
2. the launcher retains the exact repository trust override only as an exact path, not a parent/wildcard;
3. no campaign root, temporary parent, home, repository parent, or unrelated sibling is trusted;
4. a changed work-order output root changes the launcher and trust path;
5. symlinked, missing, cross-campaign, or noncanonical output roots fail closed before launcher creation;
6. `workspace-write`, approval `never`, pinned binary/model, and no-search policy remain unchanged;
7. non-model-change launchers retain their previous behaviour;
8. no user or project Codex config file is created or modified by launcher generation; and
9. shell quoting safely preserves spaces and punctuation in an exact output path.

## 8. Live neutral control

After deterministic tests pass, run one fresh neutral control using:

- the same installed NTM and Codex versions;
- the same operating identity and model;
- the repaired launcher-generation path;
- `workspace-write`;
- approval `never`;
- no search;
- a fresh standalone `0700` root;
- one `0400` input containing a random token; and
- an instruction to write only `result.json` with a fixed schema and the exact token.

Required evidence:

- exact branch, implementation commit, launcher digest, config digest, root path class, and modes;
- normalized argv with private prefixes redacted but exact trust relationships preserved;
- proof the trust prompt did not appear;
- NTM spawn, send, wait, and stop observations;
- exact input and output bytes/digests;
- exact output-root population before and after;
- proof no persistent Codex config/trust file changed; and
- cleanup/retention decision.

If the control still stops at trust, return `TRUST_REPAIR_FAILED`. If it reaches a different runtime failure, return `CONTROL_REACHED_RUNTIME_BUT_FAILED` with exact evidence. Do not run Case A.

## 9. Claim ceiling

A successful return may claim only:

> The tested launcher can start Codex non-interactively in one exact standalone host-created output root using an invocation-scoped trust override while preserving the existing sandbox and network policy.

It may not claim joined Case A success, product integration, verified V0, analyst validation, Excel support, source entitlement, professional correctness, permission to rely, runtime reliability beyond the tested control, harness improvement, deployment, security readiness, production readiness, client readiness, or product completion.

## 10. Next gate

After a successful control return is independently audited, PRO may compile a separate evidence-only exact-current-head Case A replay. The trust-repair worker has no authority to run that replay.
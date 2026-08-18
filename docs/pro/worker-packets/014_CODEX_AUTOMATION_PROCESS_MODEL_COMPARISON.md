# Worker Packet 014 — Codex Automation Process-Model Comparison

Status: **compiled for coordinator audit; live execution blocked until Packet 013 cleanup is independently accepted**.

Programme state: `REPAIRING`.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Governing contract: `docs/pro/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md`
- Comparison branch: `agent/codex-process-model-comparison-v0`
- Cleanup prerequisite: Packet 013 must return and be independently accepted
- Required receipt: `docs/pro/evidence/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_RECEIPT.md`

The exact branch head is recorded by the coordinator after parity audit. This packet is not active merely because it exists.

## Assignment

Compare the retained interactive NTM spawn-and-send evidence with one neutral automation-oriented `codex exec` process-start experiment. Determine which runtime contract can provide exact instruction delivery, process/stream evidence, file-gated completion, no user-config mutation and descriptor-bound cwd integrity.

Do not alter the product runtime under this packet.

## Required read order

1. root and package `AGENTS.md` and `ROUTE.md`;
2. `PRO_RESPONSIBILITY_PROMPT.md`;
3. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`;
4. Packet 010 and Packet 011 adjudication receipts;
5. Packet 011 diagnosis receipt at `b673569...`;
6. Packet 012 receipt at `32259dd...`;
7. Packet 012 rejection adjudication from PRO;
8. Packet 013 cleanup receipt and independent acceptance;
9. `docs/pro/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_CONTRACT_V0.md`;
10. current decision ledger and checkpoint;
11. current `harness/ntm/adapter.py` and `product/campaign/services.py` only for interface analysis;
12. installed `codex exec --help` and exact binary version/digest;
13. public OpenAI Codex exec CLI source for the tested flags; and
14. this packet.

## Activation precondition

Do not run any Codex process until coordinating Codex verifies:

```text
active user config size = 13784
active user config sha256 = 0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
mode = 0600
owner = effective UID
strict TOML parse = pass
Packet 013 independent verdict = accepted
```

If the prerequisite differs, return `CLEANUP_PREREQUISITE_NOT_MET` without execution.

## Evidence for Rival A

Use Packet 011 and Packet 012 as the live evidence for the interactive NTM/TUI model. Do not launch another TUI control.

Extract only:

- instruction timing;
- trust prompt evidence;
- NTM acknowledgement and completion observations;
- output population;
- process/pane evidence retained or missing;
- user-config mutation;
- cwd/path validation timing;
- sandbox/approval/no-search policy; and
- useful NTM capabilities.

Do not infer a missing pane transcript or process exit.

## Neutral Rival B experiment

Run one `codex exec` process-start control using the installed `0.144.6` binary, subject to `--help` confirmation.

The intended command semantics are:

```text
codex exec
  --skip-git-repo-check
  --ephemeral
  --ignore-user-config
  --sandbox workspace-write
  --ask-for-approval never
  --json
  --output-schema <schema outside agent-writable root>
  --output-last-message <host evidence path outside agent-writable root>
  -m <pinned model>
  -
```

Do not pass a project trust override. Do not pass `--search`, `--add-dir`, `danger-full-access` or a persistent profile.

`--ignore-rules` is not part of the primary arm. Record whether ambient rule loading remains possible. A separate hardening experiment requires later authority.

## Descriptor-bound launch helper

The comparison may add one neutral experiment tool that:

- creates and opens a fresh `0700` root;
- uses `O_DIRECTORY | O_NOFOLLOW` where supported;
- verifies effective-UID ownership, mode, device and inode with `fstat`;
- forks a dedicated one-shot child;
- calls `fchdir` on the inherited directory descriptor;
- calls `execve` on the pinned Codex binary;
- passes the instruction on stdin at process start;
- starts a new process group;
- closes unrelated descriptors;
- captures stdout and stderr through bounded pipes; and
- kills and waits for the complete process group on timeout.

Omit `--cd`; the descriptor-bound cwd is the authority. Recheck path device/inode after launch and completion. Path replacement is a failed experiment even when the child remains bound to the original directory.

Do not use this helper inside Django or change the product service.

## Exact owned files

The comparison worker may add only:

- `prototypes/equities-research-cognition/tools/compare_codex_process_models.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_codex_process_model_comparison.py`
- `docs/pro/evidence/CODEX_AUTOMATION_PROCESS_MODEL_COMPARISON_RECEIPT.md`

No existing file is owned. If a product, NTM or service edit appears necessary, stop and name it as a recommended future interface.

## Deterministic tests

Tests must cover:

1. exact binary and accepted CLI flag parsing from a captured `--help` fixture or bounded parser;
2. instruction bytes connected to stdin before child exec;
3. descriptor-bound cwd and omission of `--cd`;
4. effective-UID and mode checks;
5. rejection of symlink, wrong owner, wrong mode, missing root and replaced path;
6. PID/PGID capture and process-group termination;
7. bounded stdout/stderr with explicit truncation markers;
8. process exit plus exact file predicate as the only success condition;
9. rejection of exit-zero/no-file, file/no-exit, malformed file and extra-file populations;
10. no project trust override;
11. unchanged explicit sandbox, approval and no-search policy;
12. config/rules/session metadata guard; and
13. no product imports or mutation.

## Live neutral control

The control uses:

- one random token file at mode `0400` under the descriptor-bound root;
- one fixed canonical `result.json` target under that root;
- prompt on stdin at process start;
- JSONL stdout;
- bounded stderr;
- a host-owned output-schema file and last-message file outside the agent-writable root;
- no repository source, product packet, workbook, source rule, browser, search or private data.

Success requires all of:

```text
child PID and PGID retained
exit code = 0
signal = none
stdout JSONL parses
result.json is the sole agent-created file
result bytes and token are exact
last-message evidence retained separately
user config unchanged
no persistent project config created
session/rollout evidence consistent with --ephemeral
root path still maps to original device/inode
root owner = effective UID
root mode = 0700
```

If any config or path mutation occurs, stop; do not repair it under this packet.

## Comparison receipt

The receipt must:

- state exact branch, base, tool/test commits and evidence head;
- state Packet 013 accepted cleanup basis;
- include exact installed Codex/NTM/model/OS versions;
- cite public OpenAI source paths and commit used to interpret flags;
- preserve Rival A observations and missing evidence without rerun;
- preserve Rival B argv, process, stream, file, config and cwd evidence;
- compare every dimension in the governing table;
- identify exact future interfaces if either model is selected;
- state migration/compatibility cost;
- state unresolved ambient-rule/MCP/skill questions; and
- return one verdict:
  - `PREFER_CODEX_EXEC_PROCESS_MODEL`;
  - `RETAIN_NTM_ONLY_WITH_INTERFACE_REPAIR`;
  - `BOTH_UNSAFE`;
  - `INCONCLUSIVE`;
  - `CLEANUP_PREREQUISITE_NOT_MET`; or
  - `FAIL`.

## Stop conditions

Stop when:

- cleanup is not independently accepted;
- branch or initial diff moved;
- installed CLI lacks a required flag;
- exact cwd binding requires product or NTM mutation;
- the neutral run would read private/product data;
- user config or another persistent state changes;
- process identity/streams cannot be retained;
- output success cannot be distinguished from process/pane completion; or
- another live TUI control appears necessary.

## Prohibited actions

Do not:

- modify `product/`, `harness/`, NTM or any existing test;
- run Case A;
- change prompt, model, timeout, source policy, workbook logic, UI or schema;
- grant trust or edit Codex config;
- copy credentials or create a second auth home;
- advance Packet 009 or Excel;
- merge, deploy or update governance; or
- claim repaired product runtime, verified V0, analyst validation, professional reliance, client readiness or completion.

## Claim ceiling

A successful return can recommend one neutral process contract and name the exact implementation interfaces it would require. It cannot establish product integration or Case A success.

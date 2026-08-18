# Codex Output-Root Trust Control Receipt

Status: **bounded repair implemented; live control failed after launch**.

Verdict: `CONTROL_REACHED_RUNTIME_BUT_FAILED`.

The deterministic launcher repair is a candidate for independent review, but
the one authorised live control did not produce its declared output and the
Codex process changed persistent user configuration. No second control and no
Case A replay were run.

This receipt does not establish joined-runtime success, product integration,
verified V0, analyst validation, Excel support, professional reliance,
deployment authority, or product completion.

## 1. Exact basis and changed-file audit

- Branch: `agent/codex-output-root-trust-control-v0`.
- Packet 011 diagnosis evidence base:
  `b6735692418af7861b170e8e2eb0a1b438c71fcb`.
- Packet 012 starting head:
  `dd093113525645383e17cd51e7a1cff8592a624e`.
- Starting head descended from the diagnosis evidence base: yes.
- Initial net diff from the diagnosis evidence base contained exactly:
  `docs/pro/CODEX_OUTPUT_ROOT_TRUST_REPAIR_CONTRACT_V0.md` and
  `docs/pro/worker-packets/012_CODEX_OUTPUT_ROOT_TRUST_CONTROL.md`.
- Implementation commit:
  `44b291fbd12db015817cbc944bd1194490a65a93`.
- Final evidence head: the receipt-only commit containing this file; its exact
  SHA is returned in the worker handoff because a Git commit cannot contain
  its own SHA.

The worker implementation delta before this receipt was exactly:

1. `prototypes/equities-research-cognition/product/campaign/services.py`;
2. `prototypes/equities-research-cognition/scenarios/adversarial/test_model_change_v0_runtime.py`.

This receipt is the only additional worker-owned file. No NTM adapter,
setting, prompt, model, timeout, schema, migration, UI, governance, workbook,
Packet 009, or Excel file was changed.

## 2. Pre-edit diagnosis confirmation

The diagnosis-head launcher changed Codex's working directory to a standalone
per-work-order output root but trusted only the repository root:

```text
[pinned-codex] --sandbox workspace-write --ask-for-approval never \
  --cd [standalone-output-root] \
  -c projects."[repository-root]".trust_level="trusted" \
  -m gpt-5.6-sol
```

Packet 011 preserved the resulting interactive directory-trust question,
`AGENT_ERROR`, and empty output root. That evidence was reused rather than
running another known-failing control before editing.

## 3. Implemented launcher boundary

For `model_change_v0`, `_control_files` now rechecks that the already-derived
output root is an existing, canonical, non-symlink directory with mode `0700`.
It then emits a process-local trust override for that exact same `Path`:

```text
[pinned-codex] --sandbox workspace-write --ask-for-approval never \
  --cd [standalone-output-root] \
  -c projects."[repository-root]".trust_level="trusted" \
  -c projects."[standalone-output-root]".trust_level="trusted" \
  -m gpt-5.6-sol
```

The two trust targets decoded from the tested launcher were exactly the
repository root and the current work-order output root. Tests reject a
missing, symlinked, cross-campaign, unresolved, or non-owner-only output root
before launcher creation. They also prove that a successor work order gets a
different launcher and cannot inherit its predecessor's output-root trust.

The implementation does not call a persistent configuration writer. Launcher
generation itself left all observed Codex configuration files unchanged.

## 4. Deterministic evidence

All mandated deterministic checks passed on the implementation commit.

| Command | Result |
| --- | --- |
| `uv run python -W error manage.py check --fail-level WARNING` | pass; no issues |
| `uv run python -W error manage.py makemigrations --check --dry-run` | pass; no changes |
| focused `test_model_change_v0_runtime -v 2` | `18/18` pass |
| required runtime/provider/bound execution floor | `42/42` pass |
| required bounded model-change floor | `67/67` pass |
| `uv run python tools/check_boundary.py` | pass |
| `git diff --check` | pass |

The focused tests cover exact `--cd`/trust equality after shell and TOML
decoding; forbidden parent, sibling, home, root, and repository-parent paths;
per-work-order launcher separation; spaces, quotes, brackets, and dollar-sign
path characters; canonical-path and permission failure; pinned binary/model;
unchanged sandbox, approval, and no-search policy; an exact byte regression
for the non-model launcher; and no persistent config mutation during launcher
generation.

The complete suspended-classifier suite was not rerun because it was not part
of Packet 012's minimum floor. No classifier result was changed or waived.

## 5. Live neutral-control environment

Exactly one control was run after the implementation commit and deterministic
floor passed.

| Dimension | Observation |
| --- | --- |
| NTM | `1.14.0`, commit `6ffd0a06eb73a698ded0ade2df14185417869eae`, `darwin/arm64` |
| Codex CLI | `0.144.6` |
| Model | `gpt-5.6-sol` |
| Python / Django / psycopg | `3.14.0` / `6.0.7` / `3.3.4` |
| Runtime identity | existing lawful local Codex CLI subscription state; no account or credential identifier inspected |
| Network policy | no `--search`; no browser or network task |
| Sandbox / approval | `workspace-write` / `never` |
| Control root | fresh standalone host temporary root outside the repository, mode `0700` |
| Output root | exact `work/<random-work-order>/out` descendant, mode `0700` |
| Token input | one local UTF-8 file, mode `0400` |

Private filesystem prefixes are deliberately normalized. The launcher digest
was `df58c6fb7306f4f0510eab34dfae64fed9d1ea7734cc8c605269e01bf6a73e9c`.
The NTM config digest was
`abc932352a214c42c24d745e3f9115b49ba9ebeeac4f735c3ab673784707fa30`.

The random token was
`796a00fc-804d-4cd3-9216-999b3555c384`; its UTF-8 digest was
`f0e1d8eb8b124c3028df4aa2f2d146f217fe15d4a4f410daac9153441cc7f33d`.
The instruction digest was
`982cbd66c7fb5da4e505d422e4ec8274e810aa6bbdc12e0ee85d8c4abccbf91c`.

The fixed expected bytes were:

```json
{"schema":"runtime-trust-control/v0","token":"796a00fc-804d-4cd3-9216-999b3555c384"}
```

Their digest was
`28e6754514a5e826152335b9d3e3ba121895b1c3f8cb5fffd076ffafe89f97c7`.

## 6. NTM and output observations

NTM spawn returned exit `0` and reported success. Status found one Codex pane
index. The tracked send returned exit `0` with both send and acknowledgement
objects. The first wait returned exit `0` and condition `complete`.

That terminal observation was too early to prove instruction execution: the
output root was empty before send and remained empty at inspection. There was
no `result.json`, so observed output bytes and digest are not applicable. A
tracked-delivery acknowledgement therefore must not be promoted to evidence
that Codex consumed or executed the instruction.

No pane transcript or pane identifier was retained, so absence of the exact
Packet 011 trust-prompt text is not directly proven. Unlike Packet 011, NTM did
not return `AGENT_ERROR`; this narrows the observed failure beyond the former
trust gate but does not satisfy the packet's no-prompt success requirement.

The session audit recorded spawn at `2026-08-18T11:39:33.803146Z`, spawn
completion at `2026-08-18T11:39:35.256741Z`, and forced stop completion at
`2026-08-18T11:39:37.810409Z`. The audit hash was
`673c5d3687a24dc3e72671b0c77d4dc974836f5e8db68314d7b7abc4f1e191b2`
and `ntm audit verify` returned `PASS`. The stop returned exit `0`, matched the
control session, and a following status proved `exists=false`.

## 7. Persistent-config violation

The strict config invariant failed during the live Codex process:

| Point | User config size | User config SHA-256 |
| --- | ---: | --- |
| before launcher generation | `13,784` | `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9` |
| after launcher generation | `13,784` | `0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9` |
| after live control | `13,912` | `4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5` |

The mode remained `0600`. Read-only TOML inspection after the control found
one newly present `projects` entry whose path was exactly the now-deleted
control output root and whose `trust_level` was `trusted`. No user managed
config, repository config, or package config file was created.

This establishes that service launcher generation was process-local, but the
live Codex invocation persisted the exact output-root trust into user config.
That violates the governing contract. The worker did not delete or rewrite
the entry because Packet 012 explicitly prohibited any user-config write.

## 8. Cleanup, failures, and verdict

The NTM session was stopped and confirmed absent. The standalone control root,
including input, generated launcher/config, and empty output directory, was
deleted after its evidence was recorded; it is not recoverable through this
worker. The stale exact-root trust entry remains in user configuration pending
separate authority and adjudication.

The one control exposed three bounded failures:

1. no declared output was produced;
2. tracked delivery was mistaken by the first wait observation for completed
   execution, so instruction consumption was not proven; and
3. the Codex process persisted the exact runtime trust override.

Accordingly, the exact Packet 012 verdict is:

`CONTROL_REACHED_RUNTIME_BUT_FAILED`

No retry, product replay, Case A run, merge, deployment, governance update, or
programme-advancement claim is authorised by this receipt.

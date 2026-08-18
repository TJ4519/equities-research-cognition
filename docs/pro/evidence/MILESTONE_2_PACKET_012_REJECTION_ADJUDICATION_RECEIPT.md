# Milestone 2 Packet 012 Rejection Adjudication Receipt

Verdict: `REJECT_PACKET_012_AND_REOPEN_RUNTIME_PROCESS_MODEL`.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Packet 012 branch: `agent/codex-output-root-trust-control-v0`
- Packet 012 starting head: `dd093113525645383e17cd51e7a1cff8592a624e`
- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Worker receipt: `docs/pro/evidence/CODEX_OUTPUT_ROOT_TRUST_CONTROL_RECEIPT.md`
- Worker verdict: `CONTROL_REACHED_RUNTIME_BUT_FAILED`
- Independent verdict: `REJECT`
- Coordinator projection: `dec-2026-08-18-045`

No Packet 012 code is merged, deployed, promoted or treated as a safe runtime candidate.

## Findings adopted

### P1 — invocation trust was persisted

The live Codex process changed the active user config from:

```text
size    13784
sha256  0dc88534a4bd70a877c11a8f7789c1263c0490f88167c7a6c56b85a95551aad9
```

to:

```text
size    13912
sha256  4e4991c2a6098daf08e1426df208a39f4d25559b2e05ad7fdd2380525f2110a5
```

The added state is one trusted project entry for the now-deleted Packet 012 output path. The mode remains `0600`. Packet 012 therefore did not establish process-local trust isolation.

### P1 — completion was not execution evidence

NTM returned `condition=complete`, but the declared output root remained empty. No `result.json` existed. No pane transcript or child-process identity was retained. The evidence does not prove instruction consumption, successful inference, absence of an interactive prompt, or a clean Codex process exit.

### P1 — launch path had a time-of-check/time-of-use gap

Packet 012 checked symlink state, canonical path and mode while compiling launcher bytes. NTM started Codex later. The path could be replaced between those events. The repair also checked mode but not effective-UID ownership.

## RETAIN

- The exact diagnosis from Packet 011 that the previous TUI launch stopped before instruction consumption at a trust prompt.
- Packet 012's deterministic observation that exact output-root trust can be represented in launcher arguments and that some compile-time invalid paths are rejected.
- Packet 010's independently accepted deterministic source-custody repair as bounded branch evidence.
- Packet 008's bounded authority, idempotency, recovery, candidate-review, restart, rollback and prior live-path evidence.
- The continuing company-research direction and joined professional interaction contract as reversible product hypotheses, not analyst-validated truth.

## AMEND

- Amend the runtime diagnosis from “add exact project trust to the TUI command” to “the interactive TUI process model has unresolved ambient-state, completion-truth and launch-integrity defects.”
- Amend success criteria so process identity, stdout/stderr, exit status and exact artifact population are required together.
- Keep the programme `REPAIRING` and move the active sequence to environment restoration followed by process-model comparison.

## RETRACT

- Retract the claim that the Packet 012 trust override was process-local.
- Retract NTM `condition=complete` as a sufficient terminal predicate for bounded work.
- Retract compile-time canonical-path checking as proof of launch-time path integrity.
- Retract Packet 012 as a launcher repair candidate.
- Retract any claim that a safe current branch has completed real joined Case A work or that an end-to-end analyst product exists.

## ADD

- Add hash-guarded, byte-preserving and recoverable cleanup of the exact stale user-config stanza.
- Add effective-UID ownership checks to the next neutral launch model.
- Add descriptor-bound cwd, retained PID/PGID, bounded stdout/stderr, exit code/signal and process-group cancellation to the next comparison.
- Add success gated by the declared output file and host validation rather than pane state.
- Add a neutral comparison between the retained interactive NTM/TUI evidence and an automation-oriented `codex exec` process-start model.

## DEFER

- Defer all further Codex execution until the stale config entry is removed and independently verified.
- Defer a Case A replay until a neutral process contract is selected, implemented and independently controlled.
- Defer Packet 009 classifier hygiene, direct Excel, product-form expansion, cold analyst testing and the correction-to-evaluation loop.

## BLOCK

- Block another `projects.<path>.trust_level` launcher patch.
- Block broad or permanent trust, a human trust click, sandbox weakening, `--add-dir`, prompt/model/timeout changes or a blind runtime retry.
- Block product UI/schema/source-policy changes as a response to this runtime evidence.
- Block merge, deployment, verified-V0, analyst-validation, native-Excel, professional-reliance, client-readiness and programme-completion claims.

## Separate next actions

### Packet 013 — restore user configuration

The cleanup is authorised under `CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`. It may mutate only the active user `config.toml`, with the exact current whole-file hash as a hard precondition, a private `0600` before-image, byte-surgical removal, strict TOML parsing, atomic replacement and exact restoration to the recorded pre-control hash.

No Codex or NTM process may run under cleanup authority.

### Packet 014 — compare process models

The process-model comparison is compiled but blocked from live execution until Packet 013 is independently accepted. It may add only a neutral experiment tool, its tests and receipt. It compares retained TUI/NTM evidence with one automation-oriented `codex exec` process-start experiment and may recommend an interface; it may not change the product runtime.

## Product-status preservation

- Product direction and joined professional interaction are substantially specified as falsifiable V0 contracts; they are not analyst validated or frozen.
- The execution/evidence kernel and most Case A mechanisms are built on candidate branches; they are not integrated.
- No single safe head has completed the full joined analyst journey.
- The analyst-facing product form, native Excel path, cold analyst test and correction-to-evaluation loop are incomplete.

## Evidence ceiling

This receipt establishes Packet 012 rejection, the exact stale-config restoration requirement and the need to compare runtime process models.

It does not establish cleanup success, a safe Codex process model, runtime reliability, Case A execution, end-to-end product, integration, verified V0, analyst validation, Excel support, source entitlement, professional correctness, permission to rely, deployment, client readiness or programme completion.

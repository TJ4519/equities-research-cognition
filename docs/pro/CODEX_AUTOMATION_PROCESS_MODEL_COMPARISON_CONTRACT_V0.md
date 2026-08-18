# Codex Automation Process-Model Comparison Contract V0

Packet 012 disproved the assumption that a TUI runtime `projects.<path>.trust_level` override is process-local. The next runtime decision must compare an automation-oriented process-start model with the current interactive NTM spawn-and-send model before product code is changed again.

Status: governing neutral comparison contract; **blocked from live execution until Packet 013 cleanup is independently accepted**.

Programme state: `REPAIRING`.

## 1. Exact basis

- Packet 012 implementation: `44b291fbd12db015817cbc944bd1194490a65a93`
- Packet 012 evidence head: `32259dd7332831f04f48d76b9cfa7abe2ec87a47`
- Packet 012 verdict: `CONTROL_REACHED_RUNTIME_BUT_FAILED`
- Independent verdict: `REJECT`
- Cleanup prerequisite: `docs/pro/CODEX_STALE_TRUST_CLEANUP_CONTRACT_V0.md`
- Coordinator projection: `dec-2026-08-18-045`

The current interactive model has two preserved neutral/runtime receipts:

- Packet 011: instruction was never consumed because the TUI stopped at a directory-trust prompt;
- Packet 012: NTM reported `condition=complete`, the output root remained empty, and the TUI persisted the trusted output path into user config.

These receipts are the comparison evidence for the current model. Do not rerun that model merely to reproduce already retained defects.

## 2. Governing question

Which process model can provide a bounded, noninteractive Codex execution contract with:

- instruction present at process start;
- no ambient user-config mutation;
- exact cwd and effective-UID ownership binding through launch;
- retained child PID, process group, stdout, stderr, exit code and signal;
- success gated by the declared output file and host validation rather than a pane-state heuristic;
- explicit sandbox, approval and no-search policy;
- current lawful subscription identity; and
- a credible path into the existing host custody model?

The comparison decides a runtime interface, not the product form.

## 3. Rival A — current interactive NTM spawn-and-send

The current model is:

```text
host creates output root and launcher
-> NTM spawns interactive Codex TUI
-> host polls readiness
-> host sends instruction into the pane
-> NTM reports pane acknowledgement/completion
-> host later inspects output files
```

### Evidence retained

- persistent session/pane management and later sends are available;
- Packet 008 once completed a joined synthetic run when the output lived inside an already trusted project;
- Packet 011 showed an interactive trust prompt can intercept work before instruction consumption;
- Packet 012 showed `condition=complete` can occur with no declared output;
- Packet 012 showed a runtime trust override can be persisted by the TUI;
- exact child PID, process-group exit, stdout and stderr were not retained; and
- output-root path integrity was checked when launcher bytes were compiled, not atomically at child start.

### Interface repair that would be required if retained

A future NTM-compatible design would need explicit interfaces for:

1. **process-start instruction** — create the Codex process with its instruction already attached rather than a later terminal send;
2. **process identity** — return actual Codex child PID, process-group ID and executable identity;
3. **bounded stream custody** — retain redacted, byte-bounded stdout and stderr plus truncation markers;
4. **terminal truth** — return exit code/signal and distinguish pane idle, TUI prompt, model completion and process exit;
5. **artifact predicate** — wait for and validate declared output population rather than treating NTM `complete` as product success;
6. **fd-bound cwd** — accept an already-open directory descriptor or equivalent launch primitive so the path cannot be replaced between validation and exec; and
7. **ambient-config control** — prevent user config/rules/hooks from altering an automation run without copying credentials or broadening trust.

The comparison worker may name a required `NtmAdapter`/NTM command addition, but may not implement it.

## 4. Rival B — automation-oriented `codex exec`

The candidate process-start model is based on the installed Codex CLI's automation surface:

```text
codex exec
  --skip-git-repo-check
  --ephemeral
  --ignore-user-config
  --sandbox workspace-write
  --ask-for-approval never
  --json
  --output-schema <exact schema>
  --output-last-message <exact host path>
  -m <pinned model>
  -
```

The exact accepted argument order must be taken from `codex exec --help` for the installed `0.144.6` binary and recorded. No trust override is permitted.

OpenAI's public Codex source defines:

- `--skip-git-repo-check` as permission to run outside a Git repository;
- `--ephemeral` as disabling session-file persistence;
- `--ignore-user-config` as not loading `$CODEX_HOME/config.toml` while authentication still uses `CODEX_HOME`;
- `--json` as JSONL events on stdout;
- `--output-last-message` as a separate final-message file; and
- headless exec approval as `never` unless explicitly overridden.

These are candidate semantics to test, not proof that the installed binary cannot mutate another user-state surface.

### Instruction and output law

- Supply the complete neutral instruction on stdin at process start using the explicit `-` sentinel.
- Do not send terminal keystrokes after spawn.
- The instruction must require one exact regular `result.json` under the bound working root and a final response conforming to an exact JSON schema.
- Capture JSONL stdout, stderr and `--output-last-message` as separate evidence.
- The declared product-like result file, not the last message, is the primary completion object.
- Success requires process exit `0`, exact output population, schema-valid bytes and the exact token.
- Process exit without the file is failure. File appearance while the process is still running is not final success until the process exits cleanly and the file remains exact.

## 5. Directory binding and ownership

The neutral process-start arm must not validate a path and reopen it later.

The comparison harness must:

1. create one fresh standalone root with mode `0700`;
2. open it using `O_DIRECTORY | O_NOFOLLOW` where supported;
3. verify with `fstat` that it is a directory, owned by `os.geteuid()`, and mode `0700`;
4. record device and inode;
5. start a dedicated one-shot child that uses `fchdir` on the inherited descriptor immediately before `execve` of the pinned Codex binary;
6. omit `--cd` so Codex inherits the descriptor-bound cwd rather than reopening a mutable path;
7. close unneeded descriptors in parent and child; and
8. recheck path-to-device/inode mapping after launch and at completion, treating replacement as failure even though the child remains descriptor-bound.

Do not use Python `preexec_fn` inside the Django server. A neutral one-shot fork/exec helper is permitted only inside the experiment tool. A future product interface would need a dedicated audited process adapter or NTM primitive.

## 6. Effective identity and policy

Both the retained evidence and the new process-start experiment are compared under:

- the same installed Codex binary/version and pinned model;
- the same lawful local subscription/authentication state without reading credentials;
- `workspace-write`;
- approval `never`;
- no `--search` and no network task;
- no browser;
- one `0400` neutral token input;
- one exact output root;
- no product packet, workbook, source, prompt or private data; and
- no persistent config edit.

Before and after the process-start arm, hash and stat at least:

- active Codex user `config.toml`;
- any project `.codex/config.toml` in the neutral root or its parents;
- user and project exec-policy rule files discovered without reading unrelated contents; and
- session/rollout locations relevant to the `--ephemeral` claim.

The receipt must distinguish read/access from mutation. `--ignore-user-config` is not assumed to mean “no Codex state changes anywhere.”

## 7. Neutral task

The neutral task must:

- read one local UTF-8 token file by relative path;
- write exactly `result.json` with fixed canonical bytes;
- produce no other file beneath the output root except host-created evidence files that are placed outside the agent-writable root;
- avoid shell commands beyond the minimum file read/write needed by Codex;
- use no repository source, product code, browser, search or private data; and
- terminate.

The host must retain:

- exact argv with private prefixes redacted but argument relationships preserved;
- binary digest and version;
- prompt/instruction bytes and digest;
- PID, PGID, effective UID, start/end timestamps, exit code and signal;
- bounded stdout/stderr bytes and digests plus truncation markers;
- JSONL parse result;
- final-message file bytes/digest;
- declared result bytes/digest;
- root device/inode/mode/owner before, during and after;
- output-root population timeline;
- config/rules/session before/after hashes and metadata; and
- cleanup or retention decision.

## 8. Comparison dimensions

The final receipt must compare Rival A and Rival B without averaging away a failed safety property:

| Dimension | Required judgment |
| --- | --- |
| Instruction delivery | before process start, after spawn, or unproved |
| Process identity | actual child/PGID/exit available or absent |
| Stream evidence | stdout/stderr retained, bounded and attributable or absent |
| Completion truth | process+artifact, pane heuristic, or unproved |
| User-config isolation | unchanged, mutated, or unobserved |
| Session persistence | exact ephemeral evidence or unproved |
| Cwd integrity | fd-bound, path-reopened, or race remains |
| Effective UID ownership | verified or absent |
| Sandbox/approval/network | exact preserved policy or drift |
| Output custody | exact bytes and population or absent |
| Runtime observability | sufficient for causal diagnosis or not |
| NTM value retained | persistent panes, multi-turn state, coordination benefit |
| Integration cost | exact host/NTM/service interfaces that would change |

A single green output cannot override persistent-config mutation, path replacement or missing process evidence.

## 9. Possible architectural consequences

The worker may recommend one of these, with exact evidence:

### `PREFER_CODEX_EXEC_PROCESS_MODEL`

Use a future dedicated `CodexExecAdapter` or an NTM process-start mode for bounded work units. Preserve NTM only where persistent interactive sessions earn their cost.

Likely future interfaces, not authorised here:

- `CodexExecAdapter.build_command(...)`;
- `CodexExecAdapter.execute(...) -> pid, pgid, stdout, stderr, exit, signal`;
- descriptor-bound working-root handle;
- stdin instruction bytes;
- output predicate and timeout;
- process-group cancellation; and
- conversion of exact process/stream evidence into `RuntimeEvent` custody.

### `RETAIN_NTM_ONLY_WITH_INTERFACE_REPAIR`

Name the exact NTM and `NtmAdapter` changes needed to achieve process-start instruction, fd-bound cwd, stream/exit custody and artifact-gated completion.

### `BOTH_UNSAFE`

Name the unresolved safety or reproducibility property and stop.

### `INCONCLUSIVE`

Name the missing observation or unavailable lawful experiment.

No recommendation changes product code by itself.

## 10. Ordering and gate

1. Packet 013 cleanup must pass and be independently verified.
2. The comparison branch and contract must pass coordinator audit.
3. Only then may one neutral process-start experiment run.
4. The interactive NTM arm is represented by Packet 011/012 retained evidence; do not rerun it without a new reason.
5. PRO adjudicates the comparison before any runtime implementation packet.
6. A later runtime implementation must pass another neutral control.
7. Only after that may a separate exact-current-head Case A replay be authorised.

## 11. Prohibited actions

Do not:

- modify product services, NTM, prompts, models, source policy, workbook logic, UI or schemas;
- copy credentials or create another CODEX_HOME;
- grant trust, write user config or answer a TUI prompt;
- run Case A;
- advance Packet 009 or Excel;
- treat `--output-last-message` as the product artifact;
- treat process exit or NTM completion alone as success;
- merge or deploy; or
- claim verified V0, analyst validation, professional reliance, client readiness or completion.

## 12. Claim ceiling

A successful comparison may select a safer neutral Codex process contract and identify the exact interfaces required to integrate it.

It does not establish a repaired product runtime, Case A success, end-to-end product, verified V0, analyst validation, Excel support, professional correctness, permission to rely, deployment, client readiness or programme completion.

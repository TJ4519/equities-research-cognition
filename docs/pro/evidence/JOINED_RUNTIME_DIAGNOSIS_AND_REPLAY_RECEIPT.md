# Joined Runtime Diagnosis and Replay Receipt

Status: **diagnosis complete; product replay not authorised after control failure**.

Verdict: `EXTERNAL_RUNTIME_BLOCKER`.

The same-environment control reproduced the pre-output failure without using a
Case A work-order packet. Codex stopped at an interactive directory-trust gate
before reading the control input, NTM reported `AGENT_ERROR`, and the declared
output root remained empty. Under the governing decision matrix, Stage B was
not run.

This is a bounded runtime-boundary classification. It is not product
integration, joined-runtime success, verified V0, analyst validation, Excel
support, professional reliance, deployment authority, or product completion.

## 1. Exact basis and changed-file audit

- Branch: `agent/case-a-joined-runtime-diagnosis-v0`.
- Exact Packet 010 product evidence base:
  `a7df89f22f1783b529d9f31654234ed6de82eb62`.
- Exact Packet 011 starting head:
  `c253194730915a8e36b3cf188253c30e901087a7`.
- Packet 011 starting head descends from the product evidence base: yes.
- Initial net diff from the product evidence base contained exactly:
  `docs/pro/JOINED_RUNTIME_DIAGNOSIS_CONTRACT_V0.md` and
  `docs/pro/worker-packets/011_JOINED_RUNTIME_DIAGNOSIS_AND_REPLAY.md`.
- Diagnosis commit: this receipt-only commit.
- Final evidence-only head: returned with the worker handoff because a Git
  commit cannot contain its own SHA.

The only worker-authored repository file is this receipt. No product code,
runtime adapter, prompt, model, setting, timeout, migration, test, fixture, UI,
contract, packet, checkpoint, ledger, issue, or PR file was changed.

The required Packet 010 adjudication receipt was absent from the diagnosis
branch. Its exact blob was read without checkout mutation from the current
public PRO grounding branch. That receipt governs the accepted deterministic
repair and the claim ceiling; it did not authorise integration or another blind
product retry.

## 2. Runtime and host environment

| Component | Exact observation |
| --- | --- |
| NTM | `1.14.0`, commit `6ffd0a06eb73a698ded0ade2df14185417869eae`, `darwin/arm64` |
| Codex CLI | `0.144.6` |
| Model | `gpt-5.6-sol` |
| Control reasoning display | `xhigh` |
| Packet 010 reasoning setting | `NOT_RETAINED` |
| Python | `3.14.0` |
| Django | `6.0.7` |
| psycopg | `3.3.4` |
| PostgreSQL | `17.8` Homebrew, 64-bit |
| Runtime identity | Existing lawful local Codex CLI subscription/login state; no credential or account identifier was read or recorded |
| Network policy | `closed_captured_sources`; launcher omitted search |

The normalized Codex launch shape used by Packet 010 was:

```text
[pinned-codex] --sandbox workspace-write --ask-for-approval never \
  --cd [per-work-order-output-root] \
  -c projects."[repository-root]".trust_level="trusted" \
  -m gpt-5.6-sol
```

The normalized NTM shapes were the pinned-config allowlist:

```text
ntm --config=[config] --robot-spawn=[session] --spawn-cod=1 \
  --spawn-no-user --spawn-dir=[campaign-root] --spawn-wait \
  --timeout=60s --spawn-safety --spawn-names=[role] --json
ntm --config=[config] --robot-send=[session] --panes=[index] \
  --msg-file=[message] --track --timeout=60s --json
ntm --config=[config] --robot-wait=[session] --wait-until=complete \
  --panes=[index] --wait-exit-on-error --timeout=1s --json
ntm --config=[config] kill [session] --force --json
```

Personal filesystem prefixes and authentication material are intentionally not
recorded.

## 3. Retained Packet 010 failure evidence

The retained canonical database and campaign root matched the supplied basis:

- owner: `1`;
- job: `e2a94017-d072-4115-8dbd-9246f32df432`;
- campaign: `f063b48c-49d2-491d-bdeb-edf7bfd2593f`;
- campaign director: `1`;
- episode: `d0cc7295-d7ba-4edb-9f3f-2c06f276ae30`;
- episode digest:
  `1264a8066558e21f804d5017050777c1edf8abcc64ce8c5c8ea26c96cbbbcb3c`;
- starting artifact: `0d2f1b21-1ae6-43ac-86d6-00aa69c7059d`;
- starting artifact digest:
  `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b`;
- manifest: `cf6b8082-fdf4-4b9c-8854-577232459f70`, digest
  `6b942ca05e4fb742ed72cdeab14f9afcf2c1dbefe019973800c0ce789a0113d5`;
- conceptual object: `f9fe019a-d1c2-4f44-9178-bae267d0846f`, digest
  `4ef1e97c6452ba79fa7893834ae00e9ee9abe8690840a89aa79296a041779f84`;
- work-order closure:
  `28c1ac42b3d23bb30bffd09b4edf1ef8bed89ccf7ea4577adc80ea8315a81a8e`;
- NTM session: `flywheel-f063b48c49d2491dbdeb`.

The preliminary source artifact was
`f6c2a5e3-13ac-46f5-ab2d-1bf1f6dc6b82`, role `SOURCE`, in the exact
campaign, digest
`c3916adc89f9f2a4952aeb058dd21addb38399e1d85590ccf7c532ae128da2d0`.
Its source-document and assertion identities were respectively
`ec12f00a-7445-42c4-9a7c-d6f9adff3512` / digest
`bccac2d6e0c02334523abb4b7c52059199d688a39eb2f51bb9f17dafab3a0715`
and `053cee57-6676-4d0b-be07-13822db54cb7` / digest
`1232c437a7cba235e7e673ce7c056ae3fbeab49225cb21f3c6d2bb6c3319ddb0`.

The filed annual source artifact was
`0f1bd27e-fdbc-4c67-b68a-8aafbf5dd9e6`, role `SOURCE`, in the exact
campaign, digest
`b67bdc1c5169ec181f57946d2afa7daf756a71b6d80e17f818fba5dcc3b81bdf`.
Its source-document and assertion identities were respectively
`6850f7c3-9448-4e0a-bf03-30974c484dc5` / digest
`ad6b02e2cc9e5fbd9c45badeb8d9f9caec35696ff10ff730584d57649a9f767f`
and `2f106ea7-9e27-4b8a-89da-9b0a04a71ff6` / digest
`087bb612c569d1005174681b3c85b8261363b4528386eb7c7966725efeb85463`.

### Attempt 1

- Work order: `7237d545-455e-442f-8a4d-34ba42f241a8`.
- Work-order digest:
  `b98b9332fc6cd9f07625f636e1eba1b4f0b5104517dba0a3e257239382f92c84`.
- Canonical packet bytes/SHA-256: `6680` /
  `f3589b910e5cecbdfac6554e15b0f5ba7ffd0ab8d75cb4695c4428e1eccc4386`.
- Launch: `2026-08-18T09:48:06.038814Z`, succeeded.
- First readiness observation: `2026-08-18T09:48:06.205948Z`, succeeded.
- Tracked send: `2026-08-18T09:48:19.715384Z`, succeeded.
- First terminal error observation: `2026-08-18T09:48:22.171792Z`,
  pane `%13`, NTM `AGENT_ERROR`.
- Last status: `2026-08-18T09:49:35.972796Z`, pane `%13`,
  NTM `AGENT_ERROR`.
- Status observations: `56`.
- Outcome: `75ff5765-7497-4709-8e62-4be8e9a8d749`, digest
  `21232d7214c77d8b43992c8a51d2ed3395ec777b5505504fd3cbcfe1c71a7f71`,
  `RUNTIME_FAILURE / RUNTIME_IN_PROGRESS / RETRY_WORK`, recorded
  `2026-08-18T09:49:36.993918Z`.

### Attempt 2

- Work order: `bd56643c-cb26-4a89-82c5-4c20a1638303`.
- Work-order digest:
  `1318b1062c00538688f9fc149e5bf3f05ac8170a941b2a5cc8a8f176ac49f113`.
- Canonical packet bytes/SHA-256: `6680` /
  `d116880a4480e6775e9116f032eca34747db1b6d2639fa129a2838062c791e44`.
- Successor launch/add: `2026-08-18T09:49:38.481351Z`, succeeded.
- First readiness observation: `2026-08-18T09:49:38.695985Z`, succeeded.
- Tracked send: `2026-08-18T09:49:52.720869Z`, succeeded.
- First non-success wait: `2026-08-18T09:49:55.416033Z`, NTM timeout.
- Last status: `2026-08-18T09:51:12.089876Z`, pane `%14`,
  NTM `AGENT_ERROR`.
- Status observations: `56`.
- Outcome: `73f4d074-76b7-429b-b5bb-abe5098fa885`, digest
  `432eb70d98698d63a556177fbdb08e85e279abc84890def9415cbc477040c8da`,
  `RUNTIME_FAILURE / RUNTIME_IN_PROGRESS / RETRY_WORK`, recorded
  `2026-08-18T09:51:13.107336Z`.

The canonical stop event was
`0c358d15-72ab-4201-ad18-204fad0b7198`, digest
`df741990d747097b9175ced555a37ebfdb5f79fb86400aea2a24416687120035`,
recorded successfully at `2026-08-18T09:51:13.289436Z`.

### Materialisation and authority containment

Each work order materialised exactly the same three read-only inputs:

| Input | Bytes | Mode | SHA-256 |
| --- | ---: | --- | --- |
| starting `.xlsx` | 7,331 | `0400` | `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b` |
| preliminary source `.txt` | 350 | `0400` | `c3916adc89f9f2a4952aeb058dd21addb38399e1d85590ccf7c532ae128da2d0` |
| annual source `.txt` | 339 | `0400` | `b67bdc1c5169ec181f57946d2afa7daf756a71b6d80e17f818fba5dcc3b81bdf` |

The role protocol required-read digest was
`e30c45af7a0bdfc7689bc4072cda21d5b42a64ad112859c08352f845a512731f`.
Each work-order output root was an owner-only `0700` directory. Both were
empty when inspected after the retained failure and collection attempts; no
partial, temporary, malformed, acknowledgement, attestation, or proposal file
was present. Output-root contents immediately before each historic send and at
the first historic error are `NOT_RETAINED` as independently timestamped
snapshots.

Canonical authority after both failures was exactly:

```text
model proposals=0
admissibility decisions=0
candidates=0
calculation receipts=0
```

The starting workbook digest still matched its original captured digest. The
Packet 010 receipt records a fresh-process authenticated HTTP 200 restart with
the unchanged-workbook state and legal retry action, and a feature-flag-off 404
with both outcomes preserved. Packet 011 did not mutate or repeat that product
restart.

### Missing retained observations

The exact pane stdout/stderr, Codex child-process PID, exit code, signal, and
terminal trust state from panes `%13` and `%14` are `NOT_RETAINED`. The killed
NTM state database no longer contains those pane processes. The retained NTM
session audit proves spawn and kill but does not contain pane text. No causal
exit interpretation is made from `AGENT_ERROR` alone.

## 4. Packet 008 comparison baseline

| Dimension | Successful Packet 008 | Failed Packet 010 | Changed-variable reading |
| --- | --- | --- | --- |
| NTM / Codex / model | NTM `1.14.0` at `6ffd0a…`; Codex `0.144.6`; `gpt-5.6-sol` | Same | No observed change |
| Runtime identity | Existing local Codex CLI subscription state | Same operating identity mode | No observed change; exact account identifier not retained |
| Network policy | `closed_captured_sources`; no search | Same | No change |
| Protocol / required read | `model_change_v0`; role digest `e30c45…` | Same | No change |
| Canonical packet | 7,004 bytes | 6,680 bytes per attempt | IDs and captured facts changed; Packet 010 was not larger |
| Output contract | proposal, acknowledgement, attestation | Same three-file contract | No change |
| Campaign/output location | Nested inside the trusted repository Git project | Standalone disposable `/tmp` hierarchy outside the trusted Git project | Material changed variable |
| Polling | 101 status observations; final completion succeeded | 56 per attempt; terminal `AGENT_ERROR` | Terminal behavior changed |
| Sealed output | Three valid files, 751/743/555 bytes | Empty roots | Failure occurred before custody |

The location change is material because the launcher declared the repository
root trusted while changing Codex's working directory to the per-work-order
output root. Packet 008's output was inside that trusted Git project. Packet
010's output roots were standalone directories outside it.

## 5. Stage A — same-environment runtime control

The control used no repository code, source, browser, search, private data, or
existing work order. It used a fresh standalone local root, matching the failed
Packet 010 working-directory class, and the same Codex/NTM identity, versions,
model, sandbox, approval, no-search network policy, and output permissions.

- Random token: `6484c858-bada-4526-a295-6864d326257d`.
- UTF-8 input SHA-256:
  `57d00af0bc27a04db8a4e28f74d210261ca77bf99aa2f38b80390941d4f7af0a`.
- Input mode: `0400`.
- Output-root mode: `0700`.
- Control instruction digest:
  `c52230cf647b38e6e986a0548a4870451142669cb7d0286a8e2da5ff15dfee9f`.
- Session: `flywheel-p011-control-6484c858`.
- Pane: `%15` (NTM index `1`).
- Pane PID/TTY at failure capture: `70114` / `/dev/ttys021`.
- Pane command at capture: `codex`; process remained alive until bounded
  session kill.

Timeline:

| Event | UTC observation |
| --- | --- |
| Spawn start | `2026-08-18T10:42:29.873548Z` |
| Spawn complete | `2026-08-18T10:42:31.325277Z` |
| Readiness status | `2026-08-18T10:42:34.981512Z` |
| Tracked send | `2026-08-18T10:42:39.731967Z` |
| Output-start acknowledgement | `2026-08-18T10:42:40Z` |
| Wait terminal observation | `2026-08-18T10:42:46Z` |
| Bounded pane capture | `2026-08-18T10:42:57.619336Z` |
| Forced NTM stop complete | `2026-08-18T10:43:54.083627Z` |

The wait returned exit code `3`, `AGENT_ERROR`, pane `%15`. The bounded pane
capture showed Codex stopped at the interactive prompt:

```text
Do you trust the contents of this directory?
1. Yes, continue
2. No, quit
```

The control instruction was not executed. A connector OAuth warning and
invalid local-skill warnings were also visible, but neither is asserted as the
cause because the directory-trust gate independently prevented noninteractive
task execution.

The output root contained zero entries before send, at the error inspection,
and after the final status capture. Declared `result.json` therefore did not
exist; output bytes and output digest are `NOT_APPLICABLE`. Exact child-process
exit code and signal are `NOT_RETAINED` because the Codex process was still
alive at the trust prompt until the NTM session was deliberately killed.

Bounded local evidence digests before cleanup:

| Evidence | SHA-256 |
| --- | --- |
| NTM session audit | `1e030c198797590c267a99c32d407067da7b067185b37335ca139602383ecd8b` |
| global audit slice | `d58f3bf30ecc4c6b57f1cbb30e9acf963613026902263e31852395e7ef692088` |
| pane tail | `b1820de1f1a96de000d2062fe44b2746263b13aea47d26eb399030de4cc5c416` |
| status after error | `033a8d46f0ba98ea507ba2d6a8b91f718c10c47446c791f981124e1c69f7fc1a` |
| pane identity capture | `f8e91a252f21cbdbf984af6bcb20919201ade9d62aff568d4a0d86b09a3fe16a` |

The NTM session was killed and a subsequent status returned `exists=false`.
The exact disposable control root was moved to the operating-system Trash
after its evidence digests were recorded; it is recoverable there and absent
from its original path. No disposable database was created because Stage B was
forbidden.

## 6. Classification and smallest next action

Stage A failed before the declared sealed output, so the governing matrix
requires `EXTERNAL_RUNTIME_BLOCKER` and forbids Stage B. The evidence narrows
the blocker from generic instability to a reproducible launch-environment
incompatibility: a standalone per-work-order output directory is not covered
by the repository trust declaration, so the interactive Codex trust gate
intercepts noninteractive NTM operation.

This does not prove that the Case A packet, prompt, materialised inputs,
collector, or canonical integration is defective; the control used none of
them. It also does not prove the external model service is unavailable.

The smallest repair surface for PRO to compile is the Codex launch/trust and
disposable working-directory boundary. A repair must preserve least privilege,
must not grant broad permanent trust or credentials, and must prove one
standalone control before another product replay. No such repair was made by
Packet 011.

## 7. Stage B, failures, and nonclaims

Stage B was **not run** because Stage A failed. Therefore there is no fresh
Packet 011 product episode, proposal, canonical V2 decision, wrong-source
block, filed-report replacement, candidate, calculation receipt, synthetic
disposition, restart projection, or correction record.

Packet 010's deterministic source-custody candidate remains accepted only with
the prior exact narrowing. Packet 011 does not advance Packet 009, direct
Excel, integration, verified V0, analyst validation, professional reliance,
harness promotion, security review, deployment, production readiness, or
client readiness.

Verdict: `EXTERNAL_RUNTIME_BLOCKER`.

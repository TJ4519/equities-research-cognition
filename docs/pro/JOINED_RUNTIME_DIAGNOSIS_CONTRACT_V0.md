# Joined Runtime Diagnosis Contract V0

Status: governing evidence contract for one bounded runtime diagnosis and exact replay.

Programme state: `REPAIRING`.

Recorded: 18 August 2026.

## Exact basis

- Repository: `TJ4519/equities-research-cognition`
- Product branch under diagnosis: `agent/case-a-source-custody-repair-v2`
- Packet 010 implementation: `7a400ae9ce6f5fff7df746908324f2c2ff5fb37b`
- Packet 010 evidence head: `a7df89f22f1783b529d9f31654234ed6de82eb62`
- Packet 010 receipt: `docs/pro/evidence/CASE_A_SOURCE_CUSTODY_REPAIR_RECEIPT.md`
- Controlling adjudication: `docs/pro/evidence/MILESTONE_2_PACKET_010_ADJUDICATION_RECEIPT.md`
- Failed live episode: `d0cc7295-d7ba-4edb-9f3f-2c06f276ae30`
- First work order: `7237d545-455e-442f-8a4d-34ba42f241a8`
- Successor work order: `bd56643c-cb26-4a89-82c5-4c20a1638303`
- Observed terminal runtime state: two NTM `AGENT_ERROR` events before sealed proposal output
- Canonical result: two retryable runtime outcomes; zero proposals, decisions, candidates, or calculation receipts

No product code, prompt, model, runtime adapter, timeout, or packet may be changed under this contract.

## Governing question

Did the two Packet 010 live attempts fail because the external Codex/NTM runtime was unavailable or unstable, or because the product's exact work-order packet, launch, materialisation, collection, or integration path caused the agent to fail before output?

The diagnosis must distinguish those causes before another product retry. “Agent error” and “send succeeded” are observations, not causal classifications.

## Why this gate precedes other work

The source-custody branch now passes its deterministic safety cases, but the commissioned product requires real NTM/Codex work to produce a typed proposal before the rest of the journey can occur. Classifier hygiene cannot create that proposal. More backend objects cannot create it. A redesigned interface cannot create it. The next material uncertainty is therefore the boundary between external runtime operation and product integration.

A blind third retry would add another trace without making failure debuggable.

## Diagnostic invariants

1. Preserve the two failed attempts and their canonical outcomes.
2. Use a fresh disposable PostgreSQL database and new NTM session for any replay.
3. Do not reuse a prior work order, output root, proposal, candidate, or receipt.
4. Do not change product code, prompts, models, tools, timeouts, settings, packet schemas, or network policy.
5. Use the same operator runtime identity and supported command boundary as Packet 010 unless the evidence proves that identity is unavailable.
6. Capture exact evidence before stopping or deleting disposable runtime state.
7. Do not infer success from a tracked send, pane creation, process existence, or partial file.
8. A product success requires sealed typed output, host custody, canonical state, and restart—not an agent transcript.

## Required evidence from the two failed attempts

Where still available, record for each work order:

- NTM version and commit;
- Codex CLI version;
- selected model and reasoning configuration;
- operating identity and authentication mode without exposing credentials;
- exact NTM session, pane, and process identifiers;
- exact allowlisted launch and send command shapes;
- process exit code, signal, or NTM terminal reason;
- pane stdout/stderr or equivalent bounded logs;
- timestamps for launch, readiness, send, first error, collection, and stop;
- exact work-order ID, digest, closure, protocol, network policy, and packet digest;
- required-read and materialised-input paths and SHA-256 values;
- filesystem ownership and permissions for workbench, input, and output roots;
- output-root contents before send, at error, and after collection attempt;
- any partial, temporary, or malformed file and its digest;
- canonical runtime events and outcome digests; and
- confirmation that no proposal or candidate authority was created.

If a required observation was not retained, state `NOT_RETAINED`; do not reconstruct it from memory.

## Comparison baseline

Compare the failed Packet 010 attempts with the most recent successful real Packet 008 episode on these dimensions only:

- NTM and Codex versions;
- model and runtime identity;
- launch/send command shapes;
- work-order protocol and network policy;
- packet size and required-read/input population;
- output contract and filesystem layout;
- readiness and polling sequence;
- process/pane terminal state; and
- sealed output population.

Do not treat the Packet 008 success as proof that Packet 010 must work. Use it to identify changed variables.

## Two-stage diagnostic experiment

### Stage A — same-environment runtime control

Run one disposable NTM/Codex control using the same runtime identity, CLI, model, NTM boundary, working-directory class, network policy, and output-root permissions as the product path.

The control instruction is deliberately small: read one exact local UTF-8 input file, copy a declared token into one declared JSON output file, and terminate. It must not use repository product code, search, browser access, or private data.

Capture the same process, pane, timing, exit, and output evidence required above.

### Stage B — exact current product replay

Run Stage B only if Stage A produces the declared sealed output.

Create one fresh synthetic Case A population on the exact Packet 010 implementation head and execute the ordinary product path without code or configuration changes. Record all canonical and runtime identities, including:

- owner, job, campaign, campaign director, episode;
- starting artifact ID and digest;
- both source artifact IDs, roles, campaigns, and digests;
- source-document and source-assertion IDs and digests;
- conceptual object, manifest, human authorities, work order, packet digest, and closure;
- NTM session, pane, runtime versions, send and terminal state;
- sealed output files and digests;
- proposal and canonical V2 decision;
- wrong-source block and unchanged-original fact;
- filed-report repair, replacement proposal, pass, candidate, and calculation receipt;
- synthetic disposition;
- fresh-process restart; and
- correction record.

Stage B succeeds only if the whole joined synthetic path reaches the correction record and the restarted authenticated projection can recover it from canonical state.

## Decision matrix

### `EXTERNAL_RUNTIME_BLOCKER`

Return this when Stage A fails before producing its declared output. Do not run Stage B. State the exact runtime failure and whether lawful operator action, service recovery, authentication, or environment repair is required.

### `PRODUCT_RUNTIME_DEFECT_IDENTIFIED`

Return this when Stage A succeeds but Stage B fails before sealed typed output, or when the failed-attempt evidence identifies an exact packet, materialisation, command, permissions, collection, or product integration defect. Do not patch it under this contract. Name the smallest repair surface and counterexample.

### `JOINED_REPLAY_PASS_FOR_INDEPENDENT_VERIFICATION`

Return this only when Stage A succeeds and Stage B completes the full joined Case A path on fresh canonical rows. This licenses a fresh independent verification request, not integration or verified V0.

### `INCONCLUSIVE`

Return this when retained evidence is insufficient to distinguish causes and the controlled experiments cannot run lawfully or reproducibly. Name the exact missing observation or authority.

## Stop conditions

Stop without product changes when:

- the branch or implementation head moved;
- the exact runtime identity cannot be used lawfully;
- the two failed attempt records contradict the supplied basis;
- a code, prompt, settings, timeout, NTM, model, or packet change appears necessary;
- protected data, permanent credentials, external account administration, material expenditure, or irreversible action is required; or
- Stage A fails.

## Claim ceiling

A successful diagnosis may classify the runtime/product boundary and may supply one fresh joined synthetic replay for independent verification.

It may not claim integration, reliability, verified V0, analyst validation, source entitlement, Excel compatibility, professional correctness, permission to rely, harness improvement, deployment, security review, production readiness, or client readiness.

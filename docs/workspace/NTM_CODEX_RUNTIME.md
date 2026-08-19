# NTM-managed Codex research runtime

Status: controlling runtime decision for the local research workspace.

## Rule

Codex research runs inside persistent sessions created and managed through NTM.

`codex exec` is not an authorised research runtime. The product must not introduce a one-shot Codex path as a shortcut, fallback, evaluator, replay mechanism, or implementation convenience.

The local `DirectProcessAdapter` belongs to deterministic conformance testing. It may run retained local fixtures and deterministic methods. It must not be used to launch Codex.

## Division of responsibility

```text
Codex session
    performs model-mediated research, planning, comparison, challenge,
    synthesis, calculation, and candidate artifact work

NTM
    creates, names, preserves, addresses, observes, and stops persistent
    Codex sessions and panes

local research service
    owns the professional commission, exact sources, assertions, evidence-use
    decisions, context populations, branch state, claims, artifacts, decisions,
    corrections, memory, and replay
```

NTM is not an optional operator display placed beside another Codex control plane. NTM is the session runtime used to instantiate and maintain Codex research workers.

Codex remains the reasoning system. NTM does not decide what the evidence means. The local service remains the authority system. NTM completion does not grant research authority.

## Persistent sessions and research branches

One research branch should bind to one persistent Codex session or pane when branch-local continuity matters.

A durable branch record should contain:

- branch identity;
- parent episode;
- exact commission and prior perspective;
- professional question;
- method and skill versions;
- allowed sources and tools;
- authority ceiling;
- current checkpoint;
- NTM session and pane identity;
- Codex model and launch configuration;
- sent instruction identities;
- received acknowledgements;
- produced claims and artifacts;
- unresolved questions;
- stop or continuation state; and
- later disposition.

The NTM session preserves live conversational and working context. The branch checkpoint preserves durable professional state.

A persistent session may disappear, become corrupt, or outlive its useful context. A fresh NTM-managed Codex session must be able to resume from the durable branch checkpoint without using the analyst as a message bus.

## Research topology

The system should create separate persistent Codex sessions only when the split earns its cost.

Useful reasons include:

- a branch needs a different evidence population;
- a challenge needs fresh context;
- an artifact worker needs different write authority;
- two investigations can proceed independently;
- a branch needs long-lived local context; or
- later comparison requires independently disposable work.

A possible episode may use:

```text
lead Codex session
    holds the confirmed commission and branch index

research Codex session
    investigates one question and preserves branch-local state

challenge Codex session
    receives a candidate and exact support through a fresh context

artifact Codex session
    works against one exact native artifact and permitted operation set
```

The topology remains contingent. Agent count does not establish evidence count.

## Context and source changes

The host constructs the starting context before sending work through NTM.

A research session may discover that it needs new evidence. The session must return a capture request or source candidate to the host. The host captures the source, issues source and assertion identities, applies the relevant evidence-use decision, and then sends a new instruction or context delta through NTM.

A Codex session may not cite a newly found URL as authoritative merely because the model read it. Host capture and admission remain required before the assertion can support a relied-upon result.

The persistent session may remember the discovery. The professional record should use the host-issued source and assertion identities.

## Checkpointing

A Codex research session should checkpoint after a consequential state change, before expected compaction, before operator interruption, and before branch completion.

A checkpoint should state:

- current candidate claims;
- support and contradiction relations;
- captured source and assertion identities;
- rival explanations;
- calculations and artifact proposals;
- unresolved professional questions;
- work already attempted;
- next discriminating action;
- reason to continue, stop, or refuse; and
- exact NTM session and pane identity.

The host stores the checkpoint. A prose pane summary is not sufficient.

## Dispatch and acknowledgement

The host sends exact instruction material through NTM to the bound Codex session.

The runtime record should preserve:

- NTM command and configuration identity;
- session and pane;
- exact instruction or packet digest;
- tracked-send response;
- semantic Codex acknowledgement tied to the branch and context;
- status observations;
- checkpoint submissions;
- stop or interruption events; and
- exact output custody.

A tracked send proves transport. A semantic acknowledgement proves that the Codex worker understood which branch and context it received. Neither proves useful research.

## Completion

NTM reporting `complete` does not by itself complete a research branch.

Branch completion requires:

- the expected semantic acknowledgement;
- the latest checkpoint;
- a typed candidate result or bounded refusal;
- exact output files where the method requires them;
- host validation of assertion-to-object support relations;
- preserved unresolved questions;
- a clean or explicitly interrupted NTM state; and
- host custody of the result population.

The result remains provisional until the relevant human or policy decision.

## Replay

Deterministic fixture replay may use the local conformance runner.

Model-mediated replay must use a fresh NTM-managed Codex session. The host should construct the historical context, create the new persistent session through NTM, send the replay commission, and compare the returned claims, support, contradictions, uncertainty, and artifact proposals with the historical result.

Exact prose equality is not required. Later evidence must not enter the replay context.

No `codex exec` path may be introduced for replay.

## Operator visibility

NTM and tmux preserve a valuable operator surface. The consultant can inspect live sessions, intervene when authorised, and diagnose context or tool problems.

An operator intervention should enter durable state when it changes the research. The intervention should record the actor, exact wording, branch, session, time, reason, and resulting checkpoint.

Invisible consultant repair must not be attributed to autonomous Codex work.

## Implications for the current V0

The deterministic local vertical proves host contracts only.

Its direct process adapter should be treated as a conformance runner for deterministic methods. It does not represent the Codex research architecture.

The next joined implementation should bind the new local authority objects to the existing NTM-managed persistent Codex sessions:

```text
confirmed commission
-> durable research branch
-> sealed starting context
-> NTM session and pane
-> persistent Codex research
-> host-mediated source additions
-> durable checkpoints
-> fresh NTM challenge session when warranted
-> typed result and artifact custody
-> analyst decision
-> NTM-managed re-derivation session
```

The work should strengthen NTM acknowledgement, checkpointing, completion evidence, and configuration isolation. It should not replace NTM with a second Codex runtime.
# NTM persistent research branch implementation

Status: active implementation plan.

The next software object is a durable research branch bound to one or more persistent NTM-managed Codex session attempts.

## Required software relations

```text
research episode
-> durable branch
-> NTM session attempt
-> exact dispatch
-> semantic acknowledgement
-> append-only checkpoints
-> host-mediated context additions
-> typed candidate or refusal
-> host validation and custody
-> human disposition
```

A fresh challenge or re-derivation creates another durable branch and another NTM-managed Codex session. It does not inherit the producing pane as its authority.

## Branch state

The branch is immutable in identity. State changes arrive as append-only events.

Required event kinds:

- branch created;
- NTM session bound;
- instruction dispatched;
- semantic acknowledgement accepted;
- checkpoint accepted;
- context addition dispatched;
- operator intervention recorded;
- NTM status observed;
- NTM completion observed;
- candidate accepted into custody;
- refusal accepted into custody;
- session attempt abandoned;
- branch resumed in a fresh NTM session;
- branch completed;
- branch stopped.

## Session attempt

One attempt records:

- branch;
- ordinal attempt number;
- NTM session name;
- pane index;
- model and role;
- exact NTM configuration digest;
- working directory;
- starting checkpoint;
- instruction digest;
- tracked-send receipt;
- status and completion observations; and
- stop reason.

The attempt is not the branch. A new attempt may resume the same branch from the latest accepted checkpoint.

## Semantic acknowledgement

The Codex session must return an acknowledgement tied to:

- branch id;
- context id and digest;
- session and pane;
- instruction digest;
- method and skill versions; and
- authority ceiling.

An NTM tracked-send response does not substitute for this acknowledgement.

## Checkpoint

A checkpoint should preserve:

- parent checkpoint digest;
- sequence number;
- current candidate claims;
- support and contradiction relations;
- captured source and assertion identities;
- rival explanations;
- calculations and artifact proposals;
- unresolved questions;
- work attempted;
- next discriminating action;
- reason to continue, stop, or refuse; and
- session and pane identity.

The host should reject missing parents, duplicate sequence numbers, changed branch identity, and references outside the current branch context.

## Context addition

A persistent Codex session may discover new evidence. The session submits a source candidate or capture request. The host captures and identifies the source, applies the evidence-use decision, creates a new immutable context addition, and sends its digest through NTM.

The session may remember a URL. A claim may use only the host-issued assertion identity and permitted relation.

## Completion

The host may complete a branch only after:

- semantic acknowledgement;
- at least one accepted checkpoint;
- a typed candidate or bounded refusal tied to the latest checkpoint;
- exact required artifacts;
- validation of assertion-to-professional-object relations;
- an NTM completion or explicit stop observation; and
- host custody of the result population.

NTM `complete` without those objects leaves the branch incomplete.

## Resumption

A missing or abandoned pane should create a fresh NTM session attempt. The resume instruction should contain the exact branch identity, starting context, latest checkpoint, unresolved questions, and authority ceiling.

The analyst should not restate the history.

## Tests

The first mechanical suite should prove:

- tracked send cannot complete a branch;
- NTM complete with an empty result cannot complete a branch;
- acknowledgement mismatch is rejected;
- checkpoint lineage is append-only;
- a fresh attempt resumes from the latest checkpoint;
- host-mediated context addition is required before a new assertion can support a claim;
- challenge and replay create fresh NTM sessions;
- result use remains separate from branch completion;
- direct process execution refuses any Codex executable; and
- no `codex exec` path exists.

The suite may use a scripted fake NTM endpoint. It proves host and NTM contracts, not useful Codex research.

## Live proof after the mechanical suite

A configured environment should then run one real NTM-managed Codex branch across several turns. The live receipt should preserve the exact NTM configuration, session and pane, instructions, acknowledgements, checkpoints, context additions, typed output, and operator interventions.

No completion claim may rely upon the scripted endpoint.
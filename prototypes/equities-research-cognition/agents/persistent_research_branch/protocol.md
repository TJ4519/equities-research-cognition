# Persistent Codex research branch

The host has bound this Codex session to one durable research branch. The NTM
session preserves live working context. The branch files and host objects
preserve professional state. Never treat the terminal transcript as the only
record of the work.

Read `attempt-manifest.json`, `branch.json`, every supplied input, every context
snapshot named by the latest instruction, and the latest inbox instruction
before acting. Verify the identities and digests stated in those files. Stop
when a required file is missing, changed, or inconsistent.

The branch question may be broad enough to require several turns. Work only
inside the named branch, method, evidence cutoff, permitted tools, and authority
ceiling. Do not broaden the commission. Do not decide that a result may be used.
Do not promote a correction into memory or a reusable method.

## Exact acknowledgement

Each inbox instruction names one required acknowledgement path. Write that
acknowledgement before relying on the instruction or its context. Use exactly:

```json
{
  "schema": "research-branch-acknowledgement/v1",
  "branch_id": "<exact branch id>",
  "binding_id": "<exact NTM binding id>",
  "instruction_id": "<exact instruction id>",
  "instruction_digest": "<exact message digest>",
  "context_ids": ["<exact context ids from this instruction>"],
  "authority_ceiling": "<exact branch authority ceiling>",
  "worker": {
    "provider": "codex",
    "model": "<exact bound model>",
    "role": "<exact bound role>"
  },
  "protocol_version": "ntm-codex-research-branch/v1"
}
```

A tracked NTM send proves transport. The acknowledgement states that this Codex
worker understood which branch, instruction, contexts, model, role, and
authority it received. An acknowledgement does not prove useful research.

## Evidence

Use host-issued source, assertion, professional-object, context, artifact, and
memory identifiers. Never manufacture an identifier from a URL or prose
citation.

An assertion may support only the professional objects and actions granted in
the acknowledged context. Equal text or equal numbers from different sources
remain different assertions.

The full document may be absent from a support context. Use the exact assertion
projection supplied by the host. Do not recover excluded passages through a
copy of the same document.

When the branch needs new evidence, write a source request beneath
`outbox/source-requests/`. Use:

```json
{
  "schema": "research-source-request/v1",
  "branch_id": "<exact branch id>",
  "binding_id": "<exact binding id>",
  "external_request_id": "<stable id chosen within this branch>",
  "request_kind": "search | url | local_path | licensed_connector",
  "locator": "<query, URL, path, or connector locator>",
  "source_class": "<requested class>",
  "purpose": "<professional purpose>",
  "rationale": "<why this source could change the branch>",
  "professional_object_ids": ["<host-issued object ids>"],
  "rights_needed": {}
}
```

A request grants no evidence authority. Wait for a later host instruction that
carries a captured and admitted context delta. A source read during discovery
cannot support a relied-upon claim until the host issues the assertion and
admits its exact relation.

## Claims

Each candidate claim must state:

- a stable claim id within the branch;
- the proposition;
- exact assertion-to-professional-object support relations;
- contradiction relations where relevant;
- unresolved uncertainty; and
- its scope.

Do not flatten conflicting management statements into one smooth narrative.
Do not present a derived value or analyst estimate as a directly sourced fact.
Do not infer a professional-object meaning and then use the same inference to
authorise the evidence route.

## Checkpoints

Write a checkpoint after a consequential change in the branch, before expected
context compaction, before an authorised operator interruption, when waiting for
new evidence or professional judgment, and before branch completion.

Write checkpoints beneath `outbox/checkpoints/` with the exact next sequence
and predecessor identity:

```json
{
  "schema": "research-branch-checkpoint/v1",
  "branch_id": "<exact branch id>",
  "binding_id": "<exact binding id>",
  "sequence": 1,
  "predecessor_id": null,
  "candidate_claims": [],
  "rivals": [],
  "source_request_ids": [],
  "artifact_proposals": [],
  "unresolved_questions": [],
  "next_action": "<next discriminating act or null>",
  "disposition": "continue | complete | refuse | blocked",
  "refusal": null
}
```

A checkpoint is the durable branch state. It should let a fresh NTM-managed
Codex session continue without the analyst carrying messages from the old pane.
Preserve support, contradiction, uncertainty, source requests, artifact work,
and questions that remain open. Do not reduce the state to a persuasive prose
summary.

A `complete` checkpoint must contain the branch’s final candidate claims or
artifact proposals and must not retain an unsatisfied source request. A
`refuse` checkpoint must name the reason.

## Artifacts

Write candidate artifact files beneath `outbox/artifacts/`. Never overwrite a
supplied source or prior professional artifact. The final result declares every
artifact by its path, kind, title, and media type. The host will hash and store
the exact bytes.

An artifact remains provisional. A download, a completed Codex turn, or an NTM
completion response does not grant permission to rely upon it.

## Final result

After writing a complete or refusing checkpoint, write `outbox/result.json`:

```json
{
  "schema": "research-branch-result/v1",
  "branch_id": "<exact branch id>",
  "binding_id": "<exact binding id>",
  "checkpoint_id": "<host-issued checkpoint id>",
  "summary": "<ordinary-language account of the branch result>",
  "claims": [],
  "artifacts": [],
  "memory_proposals": [],
  "unresolved_questions": [],
  "refusal": null
}
```

The host validates evidence relations and artifact population after NTM reports
completion. NTM completion alone cannot complete the branch.

A memory proposal may state a possible future lesson and its narrow scope. The
proposal remains model-authored. It cannot enter active memory without a
separate authorised decision.

## Persistent-session rules

Do not invoke `codex exec`. Do not start another Codex runtime. Separate research
branches, fresh challenge, artifact work, and re-derivation are created by the
host as NTM-managed persistent sessions.

An operator may steer this session. When the intervention changes the research,
preserve it in the next checkpoint. Do not hide consultant repair.

When the live session becomes unusable, checkpoint what remains valid and stop.
A new NTM-managed session will resume from the stored checkpoint.
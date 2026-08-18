# Agentic SDLC Applicability Memo

Status: bounded donor-pattern assessment. No finding in this memo changes the active product plan without a separate decision-ledger entry and build-contract revision.

Inspected donor: `leobeeson/agentic-sdlc` at commit `6767511ee3f053b866da59f78330f6a540d89bdf`.

The Agentic SDLC repository is a Claude Code software-development harness. Its durable artifacts, role contracts, run records, and session reconstitution address coordination and context recovery. They do not establish a sell-side research workflow, source admissibility, workbook correctness, analyst authority, or a product interface.

## Retain

### Rebuild from durable work rather than conversational history

The donor's `prime` skill reconstructs one initiative by loading its run record and exact output artifacts into a fresh main-agent context. This directly addresses a demonstrated project problem: product intent and repository truth have repeatedly been split across long ChatGPT and Codex sessions, leaving the user at risk of becoming the message bus.

Retain the principle that a fresh worker should receive an exact commit, a current semantic checkpoint, the active decision, the bounded work contract, and the durable evidence needed for that contract. Do not require the user to replay the conversation that produced them.

### Make the bounded task artifact the worker instruction

The donor treats a per-task artifact as both durable state and the next worker's prompt. The repository already implements a stronger form for runtime research through canonical `WorkOrder.packet` objects, exact required reads, input digests, output roots, and legal authority. Retain this pattern for Codex engineering work: one committed worker packet should state the base commit, objective, allowed files, prohibited substitutions, required evidence, tests, stop conditions, and completion ceiling.

The packet does not replace repository inspection. It constrains what the worker may do after inspection.

### Record why work ran, was skipped, or stopped

The donor run record makes dynamic composition legible by recording included and excluded stages, their rationale, degradation, outcomes, escalations, and human gates. The present repository preserves proposals, work orders, runtime events, artifacts, and dispositions, but it does not yet give a compact product-owner account of why a prospective build step was excluded or killed.

Retain an append-only decision and experiment chronology that records alternatives considered, the selected path, evidence, nonclaims, kill conditions, and rollback. This is especially useful when an attractive prompt rewrite, agent role, interface, or framework is deliberately not adopted.

### Separate deterministic rules from judgment

The donor states a sound division: a rule belongs in code when code can decide it; a rule remains with a role when it requires judgment. The current product thesis independently reaches the same boundary.

Retain that division, with stronger enforcement than the donor starter provides. Exact bytes, identity, permitted paths, document classes, target dimensions, arithmetic, legal transitions, and output populations belong to deterministic host software. Contested source meaning, assumptions, materiality, and permission to rely on an exact artifact remain analyst judgments.

## Adapt

### Generate reconstitution views from canonical state

The donor treats the filesystem artifact tree as the system of record. This repository already has a stronger canonical substrate in PostgreSQL and Git. Adapt the reconstitution mechanism as a generated or committed projection whose source authority remains explicit:

```text
exact Git commit
+ canonical database object identities and digests
+ committed PRO decisions and contracts
-> bounded semantic checkpoint for a fresh worker
```

The projection must identify its basis and become stale when that basis moves. A fresh worker must verify the branch and commit rather than accepting the prose as current truth.

### Distinguish an evolving job from a finalised episode

The donor separates an initiative from one run. A related distinction would repair a demonstrated campaign-lifecycle problem: Langfuse correlation currently finalises campaign custody, while the research model otherwise permits later work orders.

Adapt the distinction as a research-specific `job` versus `episode` boundary. A long-lived analyst job may contain multiple immutable execution episodes. Artifact collection and trace correlation can be final per episode without freezing the whole job. This is a candidate architecture consequence, not an automatic adoption; it should be introduced only when the selected product slice needs more than one episode.

### Convert semantic input declarations into hard and soft classes

The donor allows a missing semantic signal to be elicited, inferred, or defaulted. That is acceptable for some software-planning context and dangerous for source identity or financial-model targets.

Adapt declared inputs into three explicit classes:

- hard host fact: must exist as an exact host-issued object or the operation refuses;
- analyst-supplied judgment: must be attributed, scoped, and revisable;
- optional context: may be absent only through a named degraded path.

Document class, source bytes, target identity, entity, period, units, accounting basis, and scope cannot be silently inferred into authority.

### Replace provenance headers with immutable object relations

The donor appends provenance text to artifacts that may be overwritten in place. Adapt the human readability, not the storage model. Product records should use immutable versions, exact content digests, producer identities, parent relations, and scoped dispositions. A readable header or export may project those facts, but it must not be the only enforcement surface.

### Use recipes only for bounded engineering work

The donor's recipes can help a Codex coordinator choose the smallest engineering sequence and explain omissions. Adapt them as optional worker-packet templates for recurrent repository tasks such as capability spike, domain-contract implementation, service transition, interface integration, and live verification.

Do not turn recipes into an analyst workflow taxonomy. A real research job should compose around the objective, native artifacts, evidence, and consequential uncertainty rather than a fixed series of role names.

### Scope review to the named risk

The donor uses a risk classifier and up to ten fresh review agents. The useful part is risk-based selection and independent consolidation; the topology is excessive for this project by default.

Adapt review as one fresh context focused on a named failure, with additional independent reviewers only when their distinct inspection boundary can change the decision. Every review finding should bind an exact file, object, assertion, or test receipt. Model agreement remains non-evidence.

### Implement gates before relying on them

The donor explicitly defers much of its permission policy and pre-tool-use enforcement. Adapt only gates that are executable in the current host. A prompt-stated write fence, destructive-operation ban, or source policy is not a product control until host code blocks the invalid action and preserves the refusal evidence.

## Reject

### Reject the software-development stage taxonomy as product ontology

Requirements, architecture, planning, generation, testing, review, walkthrough, and reconciliation are useful software-delivery stages. They do not describe the analyst's native job and must not appear as the organising product model.

The same applies to the donor's closed intent and magnitude vocabulary. The practitioner evidence is too narrow to justify a universal sell-side task taxonomy, and the mature product must support evolving modelling and research work rather than force every objective through one recipe family.

### Reject the filesystem artifact bus as canonical product state

A directory tree addressed by constructed paths is weaker than the repository's existing database identities, ownership checks, exact bytes, append-only chronology, and legal transitions. It would create a second authority surface and make cross-user permissions, scoped use, dependency invalidation, and transactional correction harder.

Files may remain exports, worker inputs, native artifacts, and reconstitution projections. They must not replace canonical database state.

### Reject overwrite-in-place idempotency

The donor treats a valid file at a known path as evidence that a stage can be skipped and permits regeneration by overwriting the file while appending provenance. This conflicts with exact artifact versions, protected comparisons, and the need to reconstruct what downstream work relied on.

Regeneration should create a new immutable version or episode. Reuse should point to an exact prior object and explain why it remains valid.

### Reject inferred or defaulted authority facts

No agent may repair a missing source class, entity, reporting period, unit, accounting basis, scope, or target contract by inference and then use that inferred field to validate its own output. Missing hard facts must produce a refusal or an attributed analyst decision.

### Reject semi-hard orchestration for known invalid states

A model-guided recipe may choose useful work. It cannot enforce destructive-operation boundaries, source admissibility, output custody, dependency invalidation, or release authority. Those states require deterministic host gates.

### Reject a subagent-per-stage topology

The donor's agent catalogue and review fan-out are implementation choices for Claude Code. They provide no evidence that more contexts improve this research product. Roles should remain semantic protocols that may be realised by one or several model calls according to the task and evaluation evidence.

The analyst should never have to navigate an agent roster or visible process graph to understand their work.

### Reject deferred enforcement as an acceptable product claim

The donor is candid that many permission and tool gates are specified but not implemented. This is acceptable as a starter limitation and unacceptable as evidence that the corresponding control exists. The product may reuse the specification idea only after executable enforcement and hostile tests exist.

## Discriminating experiment

### Question

Can a compact, durable reconstitution packet let a fresh Codex worker continue the active build from exact repository truth without conversational history, product drift, or the user carrying messages?

### Baseline

A fresh worker receives the repository URL and a narrative request, then reconstructs purpose and current state from the root documentation and recent conversation supplied by the coordinator. Known risks are reopening settled discovery, treating the Casebook as product truth, activating dormant prompts, importing the manual Micron report, or choosing an easy mechanical task disconnected from the counterexample.

### Treatment

Use the committed PRO artifacts as a bounded engineering artifact bus for one worker only:

1. exact branch and base commit;
2. `PRO_CONSTITUTION.md`;
3. `REPOSITORY_GROUND.md`;
4. `PROMPT_AND_HARNESS_AUDIT.md`;
5. `CURRENT_SEMANTIC_CHECKPOINT.md`;
6. one active build contract; and
7. one task-specific worker packet.

The coordinating Codex agent opens a fresh worker with repository access and transmits only those references plus the task packet. The worker must independently verify the commit and inspected code before editing.

The first treatment task should be a bounded native-workbook capability spike because its outcome can kill or reshape the proposed product hypothesis before interface work.

### Expected evidence

The treatment succeeds only if the fresh worker:

- starts from the exact named commit;
- reconstructs the product and counterexample without the old conversation;
- touches only packet-authorised files;
- does not revive the Casebook, manual Micron attachment, dormant prompt suite, visible agent topology, or prompt-only source policy;
- produces the exact requested code, tests, command receipts, and nonclaims;
- stops rather than simulating unsupported recalculation or workbook preservation; and
- returns evidence that another reviewer can reconcile directly against Git and test output.

Compare with the baseline on wrong-direction edits, missing constraints, coordinator corrections, user relays, unnecessary files, and ability to reproduce the worker's conclusion.

### Kill condition

Reject the donor pattern if any of the following occurs:

- the checkpoint or packet becomes a competing authority that contradicts code or the exact Git commit;
- maintaining the projection requires copying facts manually from several places after each change;
- the worker still needs conversational history to identify the product centre or prohibited shortcuts;
- the packet encourages checklist completion without resolving the named uncertainty;
- the worker cannot state which facts it independently verified; or
- the extra artifact burden does not reduce wrong-direction work or reconciliation cost.

### Rollback

The experiment changes no analyst-facing product path and adopts no SDLC stage taxonomy. Rollback is deletion of any experiment-only template or generated projection. The committed constitution, repository ground, decision chronology, and build contract remain ordinary project governance artifacts, not an imported Agentic SDLC installation.

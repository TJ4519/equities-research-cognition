# Repository Ground

Status: inspected software ground for product and architecture decisions. This document describes the public repository at one exact commit; it is not a completion claim.

## Verified basis

The governing source is branch `agent/pro-responsibility-handoff` at commit `c1fc568424facbb5bb8e1b6369d30a1f380ae308`. The PRO working branch `agent/pro-grounding` was created directly from that commit. The first PRO change is `docs/pro/PRO_CONSTITUTION.md` at commit `c98ef7fa2ef23056cb1e9367ae0eaff656271f5f`.

Inspection covered the root commission and instructions, both route maps, package overview and discovery documents, Django settings and URL routes, campaign models, services, state validation, templates and migrations, NTM and Langfuse boundaries, review models and transitions, active role protocols, workbench protocols, the external-skill lock, dormant DeepResearch prompts, evidence notes, and the bound-job counterexample test.

The public repository has no GitHub Actions run for the verified handoff commit. The handoff reports 115 passing mechanical tests, but this surface did not independently rerun them: the local clone attempt could not resolve GitHub, and the test environment also requires PostgreSQL, Python 3.14, runtime configuration, pinned NTM/Codex binaries, Langfuse credentials, and exact external skill packages. The reported test result is therefore attributed validation, not a newly reproduced receipt.

## Executable topology

The repository contains two operationally separate product paths plus a dormant prompt suite.

### Owned modelling and research jobs

Django mounts authentication at `/login/` and `/logout/`, job work at `/campaigns/`, and the separate review product at `/`.

An authenticated POST to `/campaigns/` calls `create_owned_job`. It requires:

- a job title;
- issuer or security;
- named professional decision use;
- evidence cutoff;
- objective;
- run instruction;
- one starting artifact; and
- one or more uploaded source files.

Creation is atomic. It stores one director-owned `ResearchCampaign`, exact uploaded bytes as `ArtifactVersion` rows, one immutable `RunSpecVersion`, one director-authored `Proposal`, an approved disposition, and one `WorkOrder` using protocol `bound_work`. The run specification binds the objective, instruction, complete input manifest, and a candidate-or-refusal outcome contract. The work-order packet is deterministically derived from those records and has `provisional_only` authority.

The current job page then exposes separate actions rather than starting work during creation:

```text
create owned job
-> start work
-> inspect exact NTM readiness
-> send exact work-order packet
-> inspect completion
-> collect and validate exact outputs
-> optionally correlate stored output with Langfuse observations
```

At launch, the host revalidates the canonical packet and every required protocol, workbench, and external skill digest. It preflights the configured Langfuse project, prepares an empty output root, generates content-addressed Codex and NTM control files, and invokes only an allowlisted NTM command through `subprocess.run(shell=False)`.

The Codex launcher is pinned by absolute path and invokes the configured model with:

- `--sandbox workspace-write`;
- `--ask-for-approval never`;
- `--search`;
- `--cd <exact work-order output root>`; and
- fixed OpenTelemetry identity arguments.

The NTM adapter permits only exact spawn, add, status, tracked-send, completion-wait, and stop command shapes. Runtime events preserve the arguments, parsed provider response, success result, and canonical digest.

Before send, the host materialises exact database-held input bytes under a work-order-specific dispatch directory, verifies their digests and population, writes the canonical packet once, and sends its path through NTM with acknowledgement tracking. Completion is accepted only after a successful tracked send and a later exact completion response for the same target.

Collection renames the output directory to a sealed location, requires regular root-level files only, enforces byte limits, verifies the worker's artifact attestation against every output byte, validates protocol-specific required paths, and stores each result as an immutable `Artifact`. Bound work must produce exactly:

- `run-acknowledgement.json` matching the exact campaign, run specification, work order, and input population; and
- `outcome.json` containing either a non-empty provisional candidate object or a bounded refusal.

The host does not interpret the candidate object beyond that envelope.

Langfuse readback occurs after artifact custody. It verifies the configured project, requests the exact campaign session and time range, rejects unknown or missing work-order identities, requires one complete native trace and one root Codex turn per work order, and creates a `TraceLink` from that root to the stored primary artifact. Telemetry is therefore a post-hoc diagnostic join, not an input to candidate authority.

### Research programme and state path

The code also supports planner, research-worker, adversarial-review, synthesis, and machine-judgment protocols. This path is rendered for campaigns without a `RunSpecVersion`; the ordinary current job-creation form instead creates bound work and renders `job.html`.

Planner approval creates an exact work order with a frozen workbench catalogue, skill catalogue, and Research Frame skill selection. Planner output can produce a human-readable plan plus separately disposable proposals. A model-authored planner interpretation must be explicitly confirmed before its child routes are available.

A research-worker proposal must currently select exactly one workbench and exactly one reasoning operator. Accepted research output must contain a workbench result, a complete append-only research-state journal, and an exact epistemic delta. The host verifies state prefix preservation, internal references, cutoff dates, selected operator results, rival mechanisms, uncertainties, claims, claim ceiling history, route decision, and bounded decision consequence.

A candidate research-state transition may be accepted for continuation, challenged into a separate adversarial-review work order, or rejected. Follow-on research marked `continue` is blocked unless its proposal descends from a planner work order created from the exact accepted current transition. Director-requested planner re-entry from accepted state is implemented.

Accepted research state is authority to continue research. It is not accepted claim authority, artifact release, or permission to rely on a result.

### Separate blind-review path

The root review application is a second product path with its own models and chronology:

```text
admitted or fixture ResearchCase
-> assigned analyst queue
-> blind first-pass judgment locked to packet and rubric digests
-> lineage reveal
-> diagnosis and corrected judgment
-> three consequence decisions
```

The three consequence families can record a current correction, create a rubric or protected-evaluation candidate, and quarantine a proposed prompt, retrieval, or workflow change. Future proposals are database-constrained to remain `inactive_quarantined`.

This review path is not connected to the owned job's `ArtifactVersion`, `RunSpecVersion`, `WorkOrder`, candidate outcome, research-state transition, or named artifact use. A `CurrentCorrection` is free text attached to a review completion. It does not patch a workbook, update a campaign artifact, invalidate dependencies, recompute downstream values, or grant scoped authority.

## Current custody guarantees

The inspected code establishes the following mechanical facts for the exact paths described above:

- authenticated job ownership is enforced by querying campaigns with both campaign ID and `director=request.user`;
- starting artifacts and uploaded sources are stored as exact bytes with SHA-256 digests;
- run specifications, proposals, work orders, runtime events, artifacts, research-state transitions, dispositions, and trace links carry canonical identity relations;
- Django model managers reject update, delete, bulk update, and bulk create for append-only campaign facts;
- foreign keys use `PROTECT` across the principal chronology;
- database triggers reject update or delete for `ArtifactVersion`, `RunSpecVersion`, and bound `WorkOrder` history;
- work-order packets freeze exact role protocols, workbench protocols, input artifacts, selected external skill packages, output roots, and required output paths;
- installed external skills are recursively checked against an exact per-file lock before launch;
- NTM command construction and subprocess execution are allowlisted;
- output collection requires observed completion, an exact artifact population, byte-level attestation, and transactional storage;
- stored artifacts and input artifacts are retrievable after process restart with their SHA-256 identity; and
- Langfuse correlation must agree with the complete stored work-order population and one exact primary artifact per work order.

These guarantees establish identity, chronology, transport, and file custody. They do not establish professional truth.

## Immutability boundary

The public description should not say that every campaign fact is uniformly database-immutable.

All campaign models reject mutation through their Django model and queryset interfaces. PostgreSQL triggers in the public migrations additionally protect exact bound inputs, run specifications, and bound work orders from direct update or deletion. The public migrations do not install equivalent mutation triggers for every campaign table. Direct SQL protection is therefore narrower than ORM-level append-only behavior.

The review application also uses append-only model interfaces and database constraints for legal consequence combinations, but its public model definitions do not by themselves prove universal protection from privileged direct SQL mutation.

## Active cognition surface

The active host loads the thin protocols under `agents/`, not the richer files under `prompts/deepresearch/`.

Active role protocols are:

- `bound_work`;
- `planner`;
- `research_worker`;
- `adversarial_review`;
- `synthesis`; and
- `judgment`.

Active workbench registrations are:

- Comparable-State Reconstruction V0;
- Aggregate Driver Attribution V0;
- Expectation Surfaces V1; and
- Decision-Consequence Map V1.

The fourth workbench correctly refuses with `DECISION_AUTHORITY_UNAVAILABLE` because the current product cannot issue the required decision-contract binding or authoritative absence object.

Two external skills may be selected: Research Frame and Modes of Reasoning. Their source is intentionally absent from the public export. `skills/lock.json` preserves exact package manifests, and runtime verification can establish that the installed package matches. Public repository inspection alone cannot evaluate the skill content or its causal effect on research.

The DeepResearch prompt suite is a candidate treatment surface. Its README explicitly states that it is dormant and names host gaps including review-driven re-entry, user correction, post-synthesis review, operative claim authority, zero-operator worker approval, complete checkpoint validation, and technical isolation for machine judgment.

## Semantic ceiling

### Uploaded source custody is not source semantics

`ArtifactVersion` stores role, filename, media type, exact bytes, and digest. It does not store or verify:

- document class;
- issuer or legal entity;
- reporting period;
- metric definition;
- units or scale;
- accounting basis;
- consolidation, segment, geography, acquisition, or operating scope;
- publication authority; or
- an exact assertion locator extracted by machine-owned software.

The job form labels uploaded files as “Sources Codex may use,” but the generated Codex command unconditionally enables `--search`. The host therefore does not enforce an uploaded-source-only information boundary.

### Bound candidates are intentionally untyped

The bound outcome validator requires a candidate JSON object but does not require target identity, source identity, source locator, transformation, assumption, dependency, or proposed artifact operation. The test suite deliberately stores a candidate that proposes the right-looking consolidated GAAP revenue from `earnings_release_nonfiling`. Collection succeeds because the host correctly recognises only a byte-exact, acknowledged, provisional candidate. It does not detect the inadmissible source-to-target relation.

### Research receipts are worker declarations

The research-state validator requires each source receipt to contain name, kind, origin, URL or path, locator, dates, passage, and access state. It validates shape, cutoff, positive-versus-negative access consistency, and internal references. Those fields are written by the worker. The host does not join them to an exact uploaded `ArtifactVersion`, host-captured web response, machine-extracted passage, or independently established source class.

### Workbench prose exceeds host enforcement

Comparable-State V0 describes exact definition, scope, period, unit, bridge, residual, authority, and source-artifact custody. The active host validates a much smaller workbench result shape and selected internal references. The workbench protocol itself says no standalone validator is shipped. A `COMPARABLE` state is therefore a model-produced candidate under a narrative contract, not a machine-established admissibility result.

The same distinction applies to richer W2 and W3 requirements. Some arithmetic and lineage invariants are mechanically testable, but source meaning and professional interpretation remain model- or analyst-authored unless a host object and validator establish them.

## Native artifact ceiling

The current runtime treats supplied native artifacts as opaque unless the worker happens to have a capable tool. The bound protocol forbids claiming parsing, formula preservation, recalculation, adoption, or release merely because bytes were supplied. The Python dependency set contains Django and PostgreSQL support only; no spreadsheet parser or recalculation engine is declared.

The public code does not implement:

- workbook parsing into stable workbook, sheet, table, range, cell, formula, and named-range identities;
- formula-preserving workbook patching;
- supported spreadsheet recalculation;
- a calculation result or error receipt;
- source-to-cell or assumption-to-formula lineage;
- a dependency graph and invalidation cascade;
- competing candidate workbook branches;
- exact correction followed by recomputation;
- comparison of original and candidate workbooks; or
- a release artifact authorised for a named use.

Excel is present only as uploaded opaque bytes and a possible worker input. A page that displays a proposed value does not constitute model updating.

## Authority ceiling

The campaign path has director dispositions over proposals and research-state continuation. The review path has blind judgments and consequence records. Neither implements the mature authority relation:

```text
exact artifact version × named use × commission × scenario × release
-> Use | Reject | Amend
```

No model currently represents a use request, scoped permission to rely, release object, recalculated descendant, provisional descendant after invalidation, or mandatory re-disposition after a correction.

No automatic path turns a correction into an evaluation candidate tied to the exact owned job, applies one reversible workflow change, or compares later work under protected chronology.

## Interface ground

`job.html` is truthful but narrow. It shows objective, exact uploaded files and digests, authorised instruction, runtime controls, a raw provisional candidate or refusal, explicit nonclaims, and an operational record. It does not expose a native artifact operation, evidence-to-target fit, downstream consequences, correction, recomputation, or named use.

`casebook.html` is inherited counterexample material. It presents worker-authored source receipts and research-state objects as analyst-facing “New evidence,” “Working alternatives,” “Claim boundary,” and “Decision consequence” cards. It also renders the forbidden `Investment Casebook` eyebrow. Its richness comes from backend research-state vocabulary rather than a native analyst job. It should not govern the product form.

The separate blind-review pages are designed around research packets and lineage reveal, not ongoing model and research work.

## Evidence currently available

The strongest public counterexample is mechanical: `test_synthetic_wrong_source_candidate_survives_as_provisional_only` constructs exact workbook and source bytes, writes a candidate with the right number and an inadmissible `earnings_release_nonfiling` basis for a GAAP target, and verifies that the host stores and re-renders it only as provisional. This proves the custody ceiling and the missing semantic gate. It does not prove the live worker episode described in private history.

Historical live receipts are excluded from the public export. The public evidence note explicitly limits adversarial fixtures to deterministic package behavior and disclaims fresh campaign completion, research correctness, analyst usefulness, product fit, or improvement.

No material public Micron episode currently originates through login, canonical backend state, real NTM/Codex work, controlled failure, analyst decision, exact changed artifact, recalculation, and scoped release.

## Repository-ground conclusion

The reusable substrate is exact job ownership, byte custody, immutable run identity, bounded runtime control, provisional output custody, state lineage, and trace correlation. The missing product seam is not another prompt, agent, dashboard, or review card. It is a host-owned relation between an exact source assertion, an explicit target contract, a proposed native-artifact operation, the resulting dependency consequences, and scoped analyst authority.

The next product hypothesis must use that seam to complete one recognisable analyst job. It must not claim that existing campaign state, blind review, or workbook bytes already do so.

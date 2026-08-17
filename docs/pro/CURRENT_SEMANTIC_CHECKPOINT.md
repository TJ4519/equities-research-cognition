# Current Semantic Checkpoint

The project is now testing a governed model-change object whose spreadsheet surface is replaceable, rather than allowing one `.xlsx` fixture or calculation engine to define the product.

Status: active reconstitution point for the PRO owner and coordinating Codex agent. Git and repository code remain authoritative. Read the decision ledger and active contract amendment when any older artifact conflicts with this checkpoint.

Checkpoint date: 17 August 2026.

## Exact repository basis

- Repository: `TJ4519/equities-research-cognition`
- Governing handoff branch: `agent/pro-responsibility-handoff`
- Verified governing commit: `c1fc568424facbb5bb8e1b6369d30a1f380ae308`
- PRO working branch: `agent/pro-grounding`
- Workbook worker result: `agent/workbook-capability-spike` at `101b83272a473598069d4e14c02552cf48982c56`
- Workbook reconciliation merge: `3dc187ff47ba0d75eabf54be527bb527d049183f`
- Working-branch parent used for this checkpoint revision: `2ced6f62ce8ec33c08c4797a73217e7072720a36`

The workbook worker diff is now part of `agent/pro-grounding`. Its changed surfaces remain limited to experiment code, one synthetic `.xlsx` fixture, a narrow mechanical test, and the evidence receipt. No product model, service, prompt, runtime, source policy, UI, or dependency file changed.

## Read order

After verifying the current branch, read:

1. `docs/pro/PRO_CONSTITUTION.md`
2. `docs/pro/OPERATING_MODEL_SYNTHESIS.md`
3. `docs/pro/REPOSITORY_GROUND.md`
4. `docs/pro/PROMPT_AND_HARNESS_AUDIT.md`
5. `docs/pro/ACTIVE_BUILD_CONTRACT.md`
6. `docs/pro/ACTIVE_BUILD_CONTRACT_AMENDMENT_001.md`
7. `docs/pro/DECISION_LEDGER.jsonl`
8. `docs/pro/COUNTEREXAMPLE_REGISTER.md`
9. the worker packet for the active slice

Do not reconstruct the project from a completion summary when these exact artifacts are available.

## Product and business centre

Useful agent-assisted analyst methods invite more frequent use, more companies, more source retrievals, more transformations, and more downstream consumers. A plausible local error can therefore propagate farther, while manual reconstruction of every result can erase the leverage.

The business opportunity is to preserve agent leverage and analyst autonomy while making consequential support, transformations, assumptions, corrections, dependencies, and permission to rely on one exact artifact reconstructable.

The product centre is a governed model-change environment. It is not:

- Excel itself;
- an `.xlsx` patcher;
- the inherited Casebook;
- a provenance dashboard;
- a chat wrapper;
- a visible agent graph;
- a static spreadsheet review; or
- a thin control plane.

Excel is an economically important artifact surface. Desktop Excel, Excel for the Web, OOXML manipulation, and LibreOffice may each act as adapters or test surfaces. None supplies the professional conceptual model by itself.

## Conceptual-model requirement

A named range gives a target mechanical identity. It does not establish what that target means.

Before a model proposal may be admitted, the smallest supported conceptual slice must connect:

### Workbook structure and dependencies

- workbook, sheet, table, range, cell, formula, chart, and named-range identity;
- dependency edges and affected outputs;
- versions, byte digests, engine, warnings, and errors; and
- allowed operations and preservation checks.

### Economic entities and relationships

- issuer, security, group, segment, product, customer, geography, or channel where relevant;
- metric, period, unit, scale, accounting basis, and scope;
- operating or financial relationships represented by the model; and
- rival interpretations when observations do not identify one mechanism.

### Assumptions and methodologies

- reported fact, issuer recast, derived calculation, estimate, forecast, adjustment, analyst assumption, scenario, or sensitivity;
- transformation, bridge, allocation, residual, and normalization method;
- method version, rationale, uncertainty, and change condition; and
- distinction between disclosed arithmetic and analyst interpretation.

### Analyst-confirmed meaning and authority

- attributed confirmation of the target meaning;
- permitted source and method variants;
- evidence cutoff and named use;
- professional ambiguity and materiality requiring judgment;
- exact `USE | REJECT | AMEND` scope; and
- ancestor changes that invalidate descendants and require recomputation.

The representation must be bounded to one consequential object. It must not pretend to encode a universal ontology of sell-side research or an entire workbook before earning the need.

## First-vertical adjudication

Updating an existing workbook remains the best next falsification surface because it supplies:

- an exact before state;
- a bounded proposed delta;
- visible propagation through formulas and outputs;
- an exact correction;
- a recalculated descendant; and
- a measurable review burden.

It is not established as the best commercial proposition or the natural start of the analyst's work. Model building, model adjustments, earnings work, and ad hoc research begin from different states. The conceptual representation must make those beginnings expressible without changing the authority model.

The vertical now begins before patching: reconstruct a bounded conceptual slice, expose uncertainty, obtain attributed confirmation, then permit a proposal.

## Repository operating model

Django and PostgreSQL own authenticated jobs, exact inputs, immutable run specifications, proposals, human dispositions, work orders, runtime events, artifacts, research-state transitions, restart truth, and post-custody trace joins.

NTM supplies persistent session and pane lifecycle. The operator-installed Codex CLI supplies the subscribed external cognition runtime. The product does not call a model API directly.

The path remains:

```text
authenticated job
-> exact input and run specification
-> attributed proposal and approval
-> immutable work-order packet
-> frozen role, workbench and skill identities
-> allowlisted NTM/Codex launch
-> tracked exact dispatch
-> observed completion
-> sealed output and attestation
-> host validation and artifact custody
-> human disposition and restart retrieval
-> optional Langfuse diagnostic correlation
```

Planner, researcher, adversarial review, synthesis, and judgment are semantic roles, not mandatory visible agents. A context split must earn independence, context economy, different tools or permissions, independently disposable output, or measured parallelism. Pane count is not evidence count.

## Slice 0 result

Verdict: `PARTIAL`.

Observed on the worker environment:

- one synthetic `.xlsx` was generated and inspected through direct OOXML;
- `FY25_REVENUE_USDM` resolved to `Model!B5`;
- the target changed from `36,900` to `37,378` without altering the original;
- declared formulas, named target, formats, and style semantics survived;
- formula caches were invalidated rather than manually filled;
- `LibreOfficeDev 26.8.0.0.alpha0` recalculated the workbook non-interactively;
- growth became approximately `48.8511%`;
- the mechanical EV/revenue value became approximately `3.21044x`;
- an invalid formula became visibly detectable as `#NAME?`; and
- two clean runs produced the same semantic OOXML content apart from ZIP timestamps.

The worker recorded `PARTIAL` because `tools/classify_loc.py` attempts to decode the authorised binary test fixture as UTF-8. The narrow workbook tests passed, while the full adversarial suite ended with one architecture setup error from that same classifier path.

LibreOfficeDev is retained as a labelled calculation proxy. Its alpha status, production integration, Excel parity, and general workbook compatibility remain unresolved.

## New direct-surface evidence

Read-only inspection supplied by the user established only:

1. the desktop Chrome session is authenticated to Excel for the Web;
2. the surface exposes `Create blank workbook` and `Upload a file`; and
3. no cloud workbook was created, uploaded, opened, or changed during that inspection.

The following remain untested:

- reproducible Codex operation of a disposable workbook there;
- interactive recalculation behaviour;
- version or activity evidence;
- faithful `.xlsx` download and round trip;
- metadata and privacy consequences;
- supported automation;
- API authentication and consent;
- licensing and tenancy; and
- lawful commercial integration.

Human interactive access, reproducible worker operation, and commercial integration are separate claims.

## Governing method

Before engineering or preserving a proxy:

```text
inventory the real surfaces already available
-> test the least mediated surface with synthetic disposable data
-> record edit, calculation, export, provenance and cleanup
-> use a proxy only for capabilities the real surface cannot expose
-> label the remaining gap
```

The workbook spike did not follow this complete order because it inspected desktop executables but not the authenticated Excel web surface. The direct-surface test now controls the next action.

## Active work and ownership

### Active: Worker Packet 002

File: `docs/pro/worker-packets/002_EXCEL_WEB_ASSUMPTION_TEST.md`

Owner: coordinating browser-capable Codex worker.

PRO responsibility:

- define the exact test and evidence standard;
- preserve authority boundaries;
- reconcile the return;
- compare the direct surface with the LibreOffice proxy; and
- refuse inflated integration or product claims.

Worker responsibility:

- use only the committed synthetic mechanical workbook;
- create only plainly disposable isolated cloud artifacts;
- open, edit, observe calculation, inspect synthetic version history where available, download, compare, repeat, and clean up;
- avoid every existing personal or client workbook;
- capture no credentials, cookies, tokens, account administration, or API consent; and
- return the receipt directly to the PRO/coordinator channel.

User responsibility: none as a relay. The user has supplied bounded authority for synthetic disposable artifacts, not existing workbooks or account administration.

The PRO attempted its available connector path and found no installed Excel or OneDrive operation connector. This PRO surface cannot attach to the user's authenticated Chrome session. Execution therefore belongs to the coordinator/Codex under the committed packet rather than to the user.

### Queued: Worker Packet 003

File: `docs/pro/worker-packets/003_BINARY_FIXTURE_CLASSIFIER_EXTENSION.md`

Owner: one fresh Codex worker after Packet 002 returns.

Scope: classify a valid authorised `.xlsx` test fixture as binary test data with zero physical lines, while hostile binary content masquerading as text still fails. Rerun the unchanged workbook sequence and all mandatory checks.

A classifier pass upgrades repository integration only.

### PRO-owned pre-Slice 1 gate

Commit the smallest conceptual-model representation contract joining artifact structure, economic meaning, methodology, assumptions, analyst confirmation, source authority, and downstream consequences. Show how the same authority model can cover an existing-model update, an adjustment, and a model-building or earnings-derived addition.

No product implementation is authorised by this gate yet.

## Slice 1 status

Blocked.

Slice 1 requires a later explicit ledger entry after:

- Excel-for-the-Web assumption-test adjudication;
- classifier-extension reconciliation or an explicit waiver;
- a committed conceptual-model representation contract; and
- comparison of direct Excel, OOXML/LibreOffice proxy, and remaining adapter gaps.

A spreadsheet capability `PASS` cannot authorise Slice 1 by itself.

## Current authority boundary

The PRO may inspect the public repository, write durable artifacts, prepare bounded packets, create review branches, reconcile evidence, update the ledger, and kill inflated claims.

The PRO and workers may not contact analysts or clients, inspect private workbooks, expose personal account material, make investment judgments, deploy production, spend money, grant API consent, weaken security, or promote candidate research into institutional authority.

## Evidence ceiling

The strongest current claim is:

> On one observed worker environment, a bounded synthetic OOXML workbook can be patched and recalculated through a real LibreOfficeDev proxy with repeatable semantic results, while the direct authenticated Excel-for-the-Web surface, typical sell-side workbooks, conceptual-model understanding, source admission, product usefulness, and commercial integration remain unproved.

This is not a product demo.

## Next action

The coordinating Codex worker executes Worker Packet 002 against the current `agent/pro-grounding` packet commit and returns the exact evidence receipt without using the user as a relay. No classifier, source, model, prompt, runtime, or interface work begins before that return.
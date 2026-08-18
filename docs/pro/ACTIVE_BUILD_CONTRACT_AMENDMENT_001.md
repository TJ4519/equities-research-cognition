# Active Build Contract Amendment 001

Amendment to: `MU-MODEL-UPDATE-V0`

Recorded: 17 August 2026

Status: controlling amendment. The original `ACTIVE_BUILD_CONTRACT.md` remains in force except where this document changes its product centre, Slice 0 result, assumption-test order, and the conditions required before Slice 1.

## Governing correction

The experiment is not an `.xlsx` patching product. It is a governed model-change experiment in which a native spreadsheet is one artifact adapter.

The object under test is a bounded conceptual model change that connects:

1. workbook structure and dependencies;
2. economic entities, metrics, periods, units, basis, scope, and relationships;
3. reported facts, calculations, adjustments, estimates, assumptions, scenarios, and methodologies; and
4. analyst-confirmed meaning, admissible authority, materiality, amendment, and permission to rely for a named use.

A stable named range supplies mechanical identity only. It cannot establish what the target means, why the method is appropriate, or who may rely on the result.

## Product-hypothesis ruling

Updating an existing workbook remains the best next falsification surface because it supplies an exact before state, a bounded delta, visible propagation, correction, recalculation, and a descendant artifact. It is not yet established as:

- the best commercial proposition;
- the natural beginning of the analyst's workflow;
- an analyst-validated product vertical;
- an Excel-only product centre; or
- a substitute for model building, adjustments, earnings work, or ad hoc research.

The vertical must begin before patching. The system must reconstruct and expose a bounded conceptual slice, then obtain attributed human confirmation of the target meaning, methodology, and authority boundary before any model-change proposal can be admitted.

The revised cold question is:

> Can the system understand and confirm enough of one consequential model-change object to contain a plausible wrong proposal, produce a corrected recalculated descendant, and reduce review below manual reconstruction?

## Slice 0 reconciliation

Worker branch: `agent/workbook-capability-spike`

Worker result commit: `101b83272a473598069d4e14c02552cf48982c56`

PRO reconciliation merge: `3dc187ff47ba0d75eabf54be527bb527d049183f`

Verdict: `PARTIAL`.

Established mechanically on the observed worker environment:

- deterministic construction and direct OOXML inspection of one bounded synthetic workbook;
- one-cell patch through a workbook-defined name;
- original-byte preservation;
- preservation of declared formula strings, target identity, formats, and style semantics;
- cache invalidation without manually fabricating dependent values;
- non-interactive recalculation using `LibreOfficeDev 26.8.0.0.alpha0`;
- independent observation of changed dependent values;
- visible invalid-formula failure; and
- repeatable semantic output across two clean runs.

Unresolved:

- the mandatory LOC classifier decodes the authorised `.xlsx` fixture as UTF-8;
- the full adversarial suite therefore did not pass;
- the engine is an alpha development build supplied by the worker environment;
- production integration and Excel parity are unknown; and
- the synthetic workbook establishes no conceptual-model understanding or analyst usefulness.

LibreOfficeDev is retained as a labelled proxy for bounded calculation capability, not as the preferred artifact surface or production engine.

## Governing assumption-test method

Before engineering or preserving a proxy, enumerate and test the real surfaces already available to the user.

The required order is:

```text
real available surface
-> synthetic direct interaction
-> reproducible edit and recalculation evidence
-> round-trip export and independent inspection
-> provenance and cleanup evidence
-> proxy only for a capability the real surface could not expose
```

Observed direct evidence: the user's authenticated desktop Chrome session exposes Excel for the Web with `Create blank workbook` and `Upload a file`.

Not established:

- reproducible Codex operation of that authenticated surface;
- reliable workbook recalculation and round-trip fidelity under automation;
- supported backend or API integration;
- authentication, licensing, tenancy, consent, or commercial deployment; or
- any conceptual-model or product-form claim.

No existing personal workbook may be inspected, opened, altered, searched, shared, or used as evidence.

## Revised build order

### Slice 0A — Excel for the Web direct-surface assumption test

Status: authorised and active.

Owner: coordinating Codex worker, because this PRO surface cannot attach to or operate the user's authenticated desktop browser session. The PRO owns the packet, evidence standard, and later adjudication.

Authority is limited to:

- one synthetic, plainly disposable workbook;
- one isolated disposable cloud location or file name;
- upload or creation, interactive edit, calculation observation, download, and cleanup necessary for the test;
- no use of personal or client data;
- no inspection or alteration of existing workbooks;
- no sharing or permission changes;
- no API consent, token extraction, browser credential handling, or tenant administration; and
- no persistence after the test unless the evidence receipt records an explicit retention decision.

Exit: `PASS | PARTIAL | FAIL` receipt for interactive operation, recalculation, provenance, versioning where visible, round-trip export, independent OOXML inspection, repeatability, and cleanup. The result concerns the observed human/browser surface only. It cannot establish commercial integration.

### Slice 0B — Binary test-fixture classifier extension

Status: authorised but queued behind Slice 0A.

Owner: one fresh Codex worker on a separate branch.

Scope: classify the authorised binary workbook fixture without decoding it as UTF-8, add hostile regressions, rerun the unchanged workbook sequence and all mandatory checks. It may not change workbook mechanics, product code, prompts, runtime, source policy, or UI.

Exit: all mandatory checks pass or the repair returns a bounded failure. A pass upgrades only repository integration of the mechanical fixture.

### Pre-Slice 1 conceptual-model gate

Status: PRO-owned and active as product adjudication; no implementation authorised.

Before Slice 1, the PRO must commit the smallest representation contract that lets one workbook target connect to economic meaning, methodology, assumptions, analyst confirmation, source authority, and downstream dependency consequences without pretending to model a whole sell-side workbook.

The contract must show how the same model-change object can begin from:

- an existing-model update;
- a model adjustment or assumption change; and
- a model-building or earnings-derived addition.

This is required to show that the experiment tests a model-change proposition rather than one convenient cell-update script.

### Slice 1 — Source, assertion, workbook, conceptual target, and authority contracts

Status: blocked.

Slice 1 remains blocked until all of the following occur:

1. Slice 0A is adjudicated;
2. Slice 0B is reconciled or explicitly waived for a named reason;
3. the conceptual-model representation contract is committed;
4. the PRO compares the direct Excel surface, the OOXML/LibreOffice proxy, and any remaining adapter gaps; and
5. a new ledger entry explicitly authorises the revised Slice 1.

A mechanical spreadsheet `PASS` cannot satisfy these conditions by itself.

## Claim ceiling

The strongest current claim is:

> The repository can preserve a bounded synthetic OOXML patch and observe real recalculation through one LibreOfficeDev proxy in the worker environment, while the direct authenticated Excel-for-the-Web surface and the conceptual meaning of an analyst model target remain untested.

No current evidence establishes a product demo, typical sell-side workbook support, Excel parity, analyst usefulness, preferred product form, commercial integration, source admissibility, or cumulative learning.
# Worker Packet 002 — Excel for the Web Direct-Surface Assumption Test

Status: active. One coordinating Codex worker owns this packet.

Contract: `MU-MODEL-UPDATE-V0`, as amended by `ACTIVE_BUILD_CONTRACT_AMENDMENT_001.md`.

## Objective

Test the real spreadsheet surface already available to the user before preserving or extending a proxy.

The worker must establish exactly which of these operations are reproducible through the user's already-authenticated Excel-for-the-Web browser surface using one synthetic disposable workbook:

1. create an isolated disposable cloud location or upload one exact synthetic workbook;
2. open the workbook in Excel for the Web without touching any existing personal workbook;
3. navigate to and change one declared input value;
4. observe whether declared dependent formulas recalculate;
5. inspect what the surface exposes about versions, actor, time, or activity for this synthetic file;
6. download or export an `.xlsx` round trip;
7. inspect the downloaded bytes independently for target, formulas, named range, styles, values, errors, and package changes;
8. repeat the core sequence from a clean synthetic copy; and
9. delete or explicitly retain every created cloud artifact under a recorded cleanup decision.

A truthful `PASS`, `PARTIAL`, or `FAIL` is valid. The test must not infer backend/API integration from successful browser interaction.

## Why this test controls the next step

The prior workbook spike selected LibreOfficeDev after inspecting installed desktop executables. It did not test the authenticated Excel web surface already available to the user. That made the capability audit incomplete and risked allowing an automatable proxy to define the artifact strategy.

The governing order is now:

```text
real available surface
-> synthetic direct operation
-> recalculation and round-trip evidence
-> provenance and cleanup evidence
-> proxy only for a capability the real surface cannot expose
```

LibreOfficeDev remains useful proxy evidence. It must not be treated as preferred merely because its command line was available.

## Exact authority

The user has authorised executable project work limited to synthetic, plainly disposable cloud artifacts.

The worker may:

- create one plainly named disposable folder if isolation requires it;
- upload the committed synthetic workbook fixture or create an equivalent blank synthetic workbook;
- create at most two working copies plus one invalid-formula copy when needed for the declared tests;
- edit only those created synthetic files;
- download the resulting synthetic `.xlsx` files for local inspection;
- inspect version history or activity only for those created files;
- capture redacted evidence that contains no unrelated personal file, account, tenant, or contact information; and
- move created artifacts to the recycle bin or delete them after evidence capture.

The worker may not:

- inspect, open, search, preview, alter, download, rename, share, or infer content from any existing personal, client, or unrelated workbook;
- browse OneDrive or recent-file lists beyond what is unavoidable to reach the isolated synthetic artifact;
- change sharing, permissions, account settings, licensing, tenant settings, or integrations;
- extract cookies, tokens, credentials, API keys, session storage, or authentication material;
- grant Microsoft Graph or other API consent;
- use browser developer tools to capture secrets;
- claim that browser access establishes a supported commercial integration;
- leave a synthetic cloud artifact without an explicit retention or cleanup record; or
- use personal or protected data in labels, formulas, values, screenshots, or filenames.

Stop immediately if the only available route exposes or requires interaction with unrelated personal files, account administration, consent, or credentials.

## Ownership

- **PRO owner:** defines the test, evidence standard, claim ceiling, and later adjudication.
- **Coordinating Codex worker:** operates the authenticated browser surface, creates the synthetic files, performs the test, captures and sanitises evidence, commits the receipt, and returns exact observations.
- **User:** is not a relay. No user action is required unless the authenticated surface itself presents a human-only consent or destructive-action gate outside the authority above; in that case return a bounded blocker rather than asking the user to reconstruct the task.

This PRO surface cannot directly attach to or control the user's authenticated Chrome session. No installed connector available to the PRO exposes Excel or OneDrive operation. The worker therefore owns execution under this packet.

## Required grounding

Before operating the browser, verify the exact branch and read:

1. root `AGENTS.md`;
2. `PRO_RESPONSIBILITY_PROMPT.md`;
3. `DEMO_COMMISSION.md`;
4. `docs/pro/OPERATING_MODEL_SYNTHESIS.md`;
5. `docs/pro/ACTIVE_BUILD_CONTRACT_AMENDMENT_001.md`;
6. `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`;
7. `docs/pro/DECISION_LEDGER.jsonl`;
8. `docs/pro/evidence/WORKBOOK_CAPABILITY_SPIKE_RECEIPT.md`;
9. `docs/pro/worker-packets/001_WORKBOOK_CAPABILITY_SPIKE.md`; and
10. this packet.

Then verify that the only workbook selected for upload is the committed synthetic fixture:

`prototypes/equities-research-cognition/scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`

Record its exact pre-upload SHA-256. Do not substitute an existing cloud workbook.

## Synthetic workbook

The preferred input is the existing committed mechanical fixture. It contains:

### `Model`

- `B4 = 25111`;
- `B5 = 36900`;
- workbook-defined name `FY25_REVENUE_USDM -> Model!$B$5`; and
- `B6 = B5/B4-1`.

### `Valuation`

- `B4 = 120000`; and
- `B5 = B4/Model!B5`.

The target edit is:

`Model!B5: 36900 -> 37378`.

Expected independent arithmetic, used only for comparison rather than writing values:

- growth approximately `0.488511011110669`; and
- mechanical EV/revenue approximately `3.21044464658355`.

The workbook and all values are `MECHANICAL_REGRESSION_ONLY`. They are not Micron research, an analyst model, or a commercial artifact.

## Isolation and naming

Use names that make disposal obvious and contain no personal information, for example:

- folder: `DISPOSABLE_AI_EXCEL_TEST_2026-08-17`;
- baseline file: `synthetic-model-baseline.xlsx`;
- repeat file: `synthetic-model-repeat.xlsx`; and
- optional error file: `synthetic-model-invalid-formula.xlsx`.

Do not use company, client, analyst, account, or project names in cloud filenames.

Before creating anything, record the visible authenticated state only at the level necessary to establish that `Create blank workbook` and `Upload a file` are available. Do not record account identity, email, tenant, recent files, or unrelated filenames.

## Test A — Baseline upload and opening

1. Compute and record the local fixture digest.
2. Upload the exact fixture to the isolated disposable location.
3. Open it in Excel for the Web.
4. Confirm whether the following are visibly preserved:
   - sheet names;
   - labels and target value;
   - formula cells and displayed values;
   - number formats and visible style semantics;
   - workbook-defined name where the web surface exposes it; and
   - absence or presence of compatibility warnings.
5. Record the workbook's displayed formula text for `Model!B6` and `Valuation!B5` where the surface permits.
6. Record whether calculation mode or refresh state is visible. Do not change global account settings.

A missing UI for named ranges is not a failure by itself; the downloaded round trip must still be inspected independently.

## Test B — Interactive edit and recalculation

1. Edit only `Model!B5` from `36900` to `37378` through the ordinary workbook UI.
2. Do not type values into dependent cells.
3. Record whether `Model!B6` and `Valuation!B5` update automatically, require an explicit calculation action, remain stale, or produce an error.
4. Record the displayed before and after values and any visible calculation status.
5. Record whether the edit appears in version history or activity for this synthetic file, including the granularity of actor and timestamp exposed. Redact personal identity in public evidence.
6. Download an `.xlsx` copy after the edit.
7. Compute the downloaded SHA-256 and inspect it independently using the existing OOXML probe or a separate direct package inspection.

The independent inspection must report:

- target value;
- workbook-defined name and address;
- formula strings;
- cached or stored formula results where present;
- error values;
- relevant styles and number formats;
- package members changed from the committed fixture; and
- document or application metadata that may contain personal identity.

Do not commit a downloaded workbook that contains personal account metadata. Record its digest and a sanitised semantic manifest instead.

## Test C — Clean repeat

Repeat the core baseline, edit, calculation observation, download, and inspection sequence using a fresh synthetic copy.

Record:

- whether the same UI steps worked;
- whether dependent values changed identically;
- whether the downloaded semantic content matched;
- whether package bytes differed and why;
- any version-history or save-timing differences; and
- any intermittent browser, upload, calculation, or download failure.

One successful manual edit without a reproducible second run is `PARTIAL` at most.

## Test D — Visible formula failure

When the surface permits a safe disposable copy, replace `Model!B6` with an invalid formula such as `=NO_SUCH_FUNCTION(1)`.

Record whether Excel for the Web:

- rejects the formula at entry;
- accepts it and displays an error;
- translates the formula name;
- leaves stale output; or
- surfaces a compatibility warning.

Download and inspect the error copy when doing so does not expand the authority boundary. This test is optional only when the web surface or cleanup path makes it unsafe; the reason must be recorded.

## Provenance and observability questions

For the synthetic file only, establish what the human-facing surface makes reproducible:

- file creation or upload time;
- last modified time;
- actor identity granularity;
- version history entries;
- ability to restore or compare versions;
- whether edit history identifies the target change;
- whether calculation or save completion is explicit;
- download/export time and file naming; and
- whether downloaded metadata preserves or introduces account identity.

Do not infer machine-owned provenance merely because the UI displays activity. Distinguish visible user history from an API-grade immutable receipt.

## Round-trip comparison

Compare the committed fixture and each downloaded workbook at three levels:

1. **Byte level:** SHA-256 and ZIP member population.
2. **Workbook-semantic level:** sheets, names, targets, formulas, displayed or cached values, styles, number formats, errors, and declared dependencies.
3. **Metadata level:** creator, last-modified-by, application version, calculation properties, timestamps, relationship changes, and any account-derived information.

Classify every difference as:

- expected user edit;
- expected Excel normalisation;
- unexplained but harmless metadata;
- semantic preservation risk;
- privacy or provenance risk; or
- blocker.

## Cleanup

The default decision is to delete or move every created cloud artifact and disposable folder to the recycle bin after:

- required downloads are complete;
- digests and sanitised manifests are recorded; and
- any permitted redacted evidence is captured.

Record:

- exact cloud artifact count created;
- exact count deleted or retained;
- deletion or recycle-bin action observed;
- whether any copy remains in the cloud; and
- the reason and scope of any retention.

Do not permanently empty the user's recycle bin. Do not delete anything not created by this test.

## Owned repository files

The worker may create or modify only:

- `docs/pro/evidence/EXCEL_WEB_ASSUMPTION_TEST_RECEIPT.md`;
- an optional sanitised JSON manifest under `docs/pro/evidence/excel-web/` containing no personal, tenant, authentication, or service-issued identifiers; and
- no other file.

No workbook downloaded from the personal cloud account may be committed unless an independent inspection proves it contains no personal or tenant metadata and the PRO separately authorises publication. The default is not to commit it.

No product code, test code, prompt, protocol, source policy, runtime, dependency, fixture, or interface change is authorised.

## Required evidence receipt

Create `docs/pro/evidence/EXCEL_WEB_ASSUMPTION_TEST_RECEIPT.md` with:

1. **Verdict:** `PASS | PARTIAL | FAIL` for the direct human/browser surface.
2. **Exact basis:** repository branch and commit, browser and operating-system details available without exposing account identity, fixture digest, test time window.
3. **Authority and isolation:** created names, artifact count, prohibition compliance, and any stop condition.
4. **Observed access:** exact controls and route used, without credentials or unrelated files.
5. **Baseline opening:** visible fidelity and warnings.
6. **Interactive edit:** exact action and displayed before/after values.
7. **Recalculation:** automatic, explicit, stale, failed, or unknown; evidence and timing.
8. **Provenance surface:** versions, actor/time granularity, activity, and limitations.
9. **Round-trip export:** download route, digests, semantic and metadata comparison.
10. **Repeat run:** reproducibility and differences.
11. **Invalid-formula test:** result or bounded reason omitted.
12. **Cleanup:** created, deleted, retained, recycle-bin status, and remaining artifacts.
13. **Comparison with LibreOfficeDev:** capabilities observed directly, only through proxy, conflicting, or still absent.
14. **Commercial-integration nonclaims:** authentication, APIs, licensing, tenancy, automation, and fidelity gaps.
15. **Recommended PRO decision:** direct Excel surface, proxy, hybrid adapter, further test, or kill/narrow.

Every public screenshot or extracted manifest must be reviewed for personal identity and unrelated file exposure. When safe redaction is not possible, omit the screenshot and preserve a textual observation plus workbook digest instead.

## Verdict rules

### PASS

`PASS` means only that, in the observed authenticated browser environment, the synthetic workbook can be reproducibly opened, edited at the declared target, recalculated without dependent manual entry, downloaded twice, independently inspected with preserved declared semantics, and cleaned up with a complete receipt.

It does not establish automation or commercial integration.

### PARTIAL

Return `PARTIAL` when any required direct operation works but one or more of recalculation evidence, repeatability, provenance visibility, export, independent verification, metadata safety, or cleanup remains incomplete.

### FAIL

Return `FAIL` when the direct surface cannot safely operate the synthetic workbook under the declared authority, produces an unresolvable semantic round-trip loss, exposes unrelated personal material as a necessary step, or requires credentials, consent, administration, or unsupported automation outside this packet.

## Required return

Return directly to the PRO owner and coordinating thread:

- exact result commit;
- receipt path;
- verdict;
- exact synthetic cloud artifact count and cleanup result;
- workbook digests and sanitised semantic comparison;
- direct edit and recalculation observations;
- repeat result;
- provenance and metadata result;
- comparison with LibreOfficeDev;
- unresolved integration facts; and
- claim ceiling.

Do not begin the classifier extension, Slice 1, source work, product code, interface work, or API integration.
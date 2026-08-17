# Worker Packet 001 — Workbook Capability Spike

Status: active. One fresh Codex worker owns this packet. Do not parallelise overlapping implementation.

Contract slice: `MU-MODEL-UPDATE-V0 / Slice 0`.

Exact contract base commit: `b238ee2949f71ad04c74dac2700c7714e1018012` on `agent/pro-grounding`.

The commit carrying this packet is a documentation-only descendant of the contract base. The coordinating agent must create or point the worker at a dedicated branch from the packet-carrying commit and report that exact branch head with the return.

## Objective

Determine whether the current repository environment can truthfully support the native-workbook premise of the selected product hypothesis.

The spike must establish whether one bounded `.xlsx` workbook can be:

1. read without changing the original;
2. inspected for a stable named target, relevant formulas, styles, number formats, and dependencies;
3. copied and patched at exactly one allowed input cell;
4. passed through an independently observed supported calculation engine;
5. reopened after calculation;
6. verified to preserve the declared formula strings and named target;
7. verified to produce changed dependent cached values without manually writing them; and
8. reproduced with exact commands, versions, digests, and explicit limitations.

A truthful `PARTIAL` or `FAIL` is a valid result. A simulated or overstated `PASS` is not.

## Why this is first

The active product hypothesis is invalid if it can only show proposed spreadsheet changes while leaving the workbook opaque, formulas stale, or recalculation unobserved. Source models, agent protocols, deterministic admission, and interface work would all be premature until this native-artifact boundary is known.

This packet is also the discriminating Agentic SDLC reconstitution experiment. The worker receives durable repository artifacts rather than prior conversation. Its return must show whether those artifacts were sufficient to preserve product direction and avoid attractive but prohibited work.

## Required grounding

Before editing, verify the exact Git commit and read these files in order:

1. root `AGENTS.md`
2. `DEMO_COMMISSION.md`
3. root `ROUTE.md`
4. `prototypes/equities-research-cognition/AGENTS.md`
5. `prototypes/equities-research-cognition/ROUTE.md`
6. `prototypes/equities-research-cognition/DEPENDENCIES.md`
7. `docs/pro/CURRENT_SEMANTIC_CHECKPOINT.md`
8. `docs/pro/ACTIVE_BUILD_CONTRACT.md`, limited to the workbook contract, capability gate, Slice 0, acceptance tests, nonclaims, and rollback
9. `docs/pro/REPOSITORY_GROUND.md`, especially the native-artifact ceiling
10. `docs/pro/COUNTEREXAMPLE_REGISTER.md`, especially CE-003
11. `docs/pro/DECISION_LEDGER.jsonl`, especially decision `PRO-2026-08-17-007`
12. this packet

Then inspect the current package layout, `pyproject.toml`, existing adversarial-test conventions, and available host executables. Do not accept the packet's statement that no workbook support exists without checking the checkout.

In the evidence receipt, separate:

- facts independently verified from code or command output;
- constraints inherited from the active contract; and
- unresolved assumptions.

If HEAD is not the packet-carrying descendant of exact contract base `b238ee2949f71ad04c74dac2700c7714e1018012`, stop and return the actual branch and commit. Do not rebase, merge, or reinterpret a moved branch silently.

## Owned files

The worker may create or modify only these surfaces:

- `prototypes/equities-research-cognition/spikes/workbook_capability/**`
- `prototypes/equities-research-cognition/scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_workbook_capability_spike.py`
- `prototypes/equities-research-cognition/pyproject.toml`, only when a committed Python dependency is necessary for the evidenced spike
- `prototypes/equities-research-cognition/DEPENDENCIES.md`, only when `pyproject.toml` changes
- the package lock file, only if one already exists and dependency tooling updates it normally
- `docs/pro/evidence/WORKBOOK_CAPABILITY_SPIKE_RECEIPT.md`

A smaller diff is preferred. Do not create a general spreadsheet framework.

The fixture is explicitly `MECHANICAL_REGRESSION_ONLY`. It must not be placed under product data, rendered in the UI, or described as a live Micron artifact.

## Prohibited changes

Do not change:

- Django models, migrations, services, views, URLs, forms, templates, or settings;
- campaign or review state;
- `harness/ntm/adapter.py` or any runtime process boundary;
- Langfuse code;
- active or dormant prompts, protocols, workbenches, skills, or cognition locks;
- the Casebook;
- source-policy, admissibility, proposal, candidate, correction, or use-authority objects;
- product styling or analyst-facing UI;
- the manual Micron report or any private artifact; or
- existing security, ownership, append-only, or subprocess constraints.

Do not install a system package, start a paid service, provision external infrastructure, commit a binary supplied from private material, or modify host configuration without explicit outer-user authority.

The executable package instruction states that only `harness/ntm/adapter.py` may spawn host processes. Do not add Python `subprocess`, shell-out, or process-spawn code elsewhere. An external calculation engine may be invoked manually by the worker from the shell solely to establish the capability receipt. Production integration is a later architecture decision and remains out of scope.

Do not use browser automation or a desktop application by hand and then report an unreproducible result. Every engine interaction must be command- or API-reproducible and recorded.

## Dependency rule

The package currently declares only Django and Psycopg.

A committed Python dependency is permitted only when all of the following are recorded in the receipt and `DEPENDENCIES.md`:

- exact package and pin;
- narrow role in the spike;
- licence;
- source and maintenance status;
- Python 3.14 compatibility evidence;
- why the standard library is insufficient;
- whether it parses, writes, calculates, or merely serialises formulas;
- transitive-dependency consequence; and
- removal path if the spike fails.

Do not silently add several overlapping spreadsheet packages. Prefer one narrow parser/writer plus an independently observed calculation engine. If no credible dependency choice can be justified, return `FAIL` rather than broadening the stack casually.

Temporary uncommitted experiments are allowed during investigation. A `PASS` return must leave a reproducible declared environment. A `FAIL` return should remove exploratory dependencies that are not part of the evidence.

## Mechanical workbook fixture

Create one public, purpose-built `.xlsx` fixture at the authorised path. Its exact bytes and SHA-256 must be recorded.

The workbook must contain:

### Sheet `Model`

- `A4`: `FY2024 revenue`
- `B4`: numeric value `25111`
- `A5`: `FY2025 revenue`
- `B5`: numeric stale value `36900`
- workbook-defined name `FY25_REVENUE_USDM` referring exactly to `Model!$B$5`
- `A6`: `FY2025 revenue growth`
- `B6`: formula `=B5/B4-1`

### Sheet `Valuation`

- `A4`: `Enterprise value assumption`
- `B4`: numeric mechanical value `120000`
- `A5`: `EV / FY2025 revenue`
- `B5`: formula `=B4/Model!B5`

The target, formula cells, and their labels must have non-default but simple styles and explicit number formats so preservation can be checked. The fixture must contain no macros, external links, circular references, data tables, hidden external data, or volatile functions.

The fixture's valuation assumption is mechanical test data, not investment research.

Document how the fixture was generated. A library used to create and patch the fixture cannot be the sole verifier of its output. Use independent standard-library OOXML inspection or another genuinely independent method to verify the named range, raw formula text, worksheet targets, and relevant style identifiers.

Do not commit candidate output workbooks. Generate them under a temporary test or evidence directory that is ignored by Git.

## Required patch scenario

Starting from the exact fixture:

- resolve `FY25_REVENUE_USDM` to `Model!B5`;
- record the original target value `36900`;
- copy the workbook to a candidate path;
- set only the target input to numeric value `37378`;
- preserve the original fixture bytes exactly;
- preserve the formula text in `Model!B6` and `Valuation!B5`;
- preserve the named range and its target;
- preserve the relevant styles and number formats;
- run the supported calculation engine over a copy, never the original;
- reopen the recalculated output in a value-reading mode independent of hand-entered expected outputs; and
- record the before and after dependent values.

The expected mathematical results may be calculated independently as assertions, but they may not be written into the workbook as cached values by the spike code. The workbook engine must produce the cached formula results that the post-engine reader observes.

Opening and saving the file with a parser/writer is not recalculation.

## Calculation-engine investigation

Inspect the current environment for a credible calculation engine or API. Record every candidate considered and why it was selected, rejected, or unavailable.

A credible engine must:

- evaluate the fixture formulas rather than only preserve formula strings;
- expose an exact version;
- run through a reproducible non-interactive command or API;
- produce a workbook or calculation result that an independent reader can inspect;
- return a process or API result that can be captured;
- fail visibly on invalid formulas; and
- have a plausible later integration path that does not require unrecorded desktop actions.

Do not assume that LibreOffice, Excel, a Python formula library, or any other engine is installed or suitable. Verify it. Do not install a system engine under this packet.

Because product process spawning is out of scope, distinguish:

- engine capability demonstrated manually from the worker shell;
- parser and patch code that can be tested inside Python; and
- unresolved production integration into the repository's single process boundary.

A manual shell engine run can support `PASS` for environmental capability only when every required receipt exists. It does not authorise production process integration.

## Independent verification

The spike must not trust one library to create, patch, recalculate, and validate its own output.

At minimum, independently verify:

- original and candidate SHA-256;
- original bytes unchanged after every operation;
- workbook-defined name and exact address by reading OOXML package content;
- formula strings in original, patched, and recalculated packages;
- relevant style IDs and number-format references in OOXML;
- target value after patch;
- formula cached values after engine calculation through a value-reading path;
- no Excel error values in the declared target and dependency population; and
- no unexpected changed formula or target address.

If the selected tool rewrites broad workbook package metadata, record that separately from semantic preservation. Byte equality between input and candidate is neither expected nor sufficient.

## Repetition

Run the complete baseline-and-candidate sequence twice from clean temporary directories.

Record:

- whether input bytes and fixture digest are stable;
- candidate output digests per run;
- whether engine metadata makes byte output nondeterministic;
- semantic before and after values;
- formula and named-range preservation; and
- any difference between the two runs.

`PASS` requires repeatable semantic results. If byte-for-byte output differs, explain every observed source of difference or lower the result to `PARTIAL` when unexplained.

## Checks

Run the package's normal commands from `prototypes/equities-research-cognition` when the environment supports them:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
```

Also run the narrow workbook test directly and record the exact command.

Do not claim the full suite passed when PostgreSQL, Python 3.14, system binaries, credentials, or other required services are unavailable. Record exact blockers and the subset that ran.

Warnings promoted to errors must remain clean. A skipped workbook test is not a passing capability test.

## Required evidence receipt

Create `docs/pro/evidence/WORKBOOK_CAPABILITY_SPIKE_RECEIPT.md` with these sections:

1. **Verdict:** `PASS`, `PARTIAL`, or `FAIL`, followed by one exact sentence stating what was established.
2. **Exact basis:** repository, starting branch and commit, result commit, operating system, Python, uv, package, and engine versions.
3. **Independent repository verification:** facts checked from code rather than inherited from this packet.
4. **Fixture:** generation method, path, declared profile, SHA-256, and mechanical-only status.
5. **Strategy comparison:** parser/writer and engine candidates considered, evidence used, and reason for the chosen route.
6. **Commands:** exact commands in execution order, including engine invocation and return status.
7. **Before and after evidence:** target, formulas, named range, styles, number formats, dependent cached values, errors, and digests.
8. **Repeat run:** semantic and byte-level comparison.
9. **Checks:** every repository test or check attempted, with complete result or exact blocker.
10. **Boundary review:** confirmation that no product code, prompts, runtime spawn boundary, or UI changed.
11. **Unresolved integration work:** what a production workbook adapter would still require.
12. **Claim ceiling and nonclaims.**
13. **Reconstitution experiment:** whether the committed artifacts were sufficient; missing context; coordinator or user relays required; wrong-direction work avoided or encountered.
14. **Recommended PRO decision:** continue, narrow, choose another engine boundary, or kill the Excel-companion hypothesis.

Do not write “all tests pass” without the commands and outputs that support it.

## Verdict rules

### PASS

Return `PASS` only when:

- all fixture, patch, preservation, recalculation, independent-verification, and repetition requirements hold;
- the calculation engine is real, versioned, non-interactive, and reproducible in the observed environment;
- no formula cache was manually fabricated;
- no original byte was changed;
- no prohibited file changed;
- dependency changes are justified and pinned;
- narrow workbook tests pass without skip; and
- unresolved production integration is named without undermining the demonstrated environmental capability.

### PARTIAL

Return `PARTIAL` when parser, patch, or preservation works but any required recalculation, cached-value, independent-verification, repeatability, environment, or integration fact remains unresolved.

Examples include:

- a credible engine is unavailable in the current environment;
- the engine calculates but the output cannot be read independently;
- formula text is preserved but cached values remain stale;
- the parser loses a named range or relevant style;
- only manual desktop steps work;
- output changes are semantically correct but unexplained nondeterminism remains; or
- dependency support on Python 3.14 is uncertain.

### FAIL

Return `FAIL` when the bounded workbook profile cannot be parsed, patched, preserved, or calculated credibly, or when a valid result would require a prohibited shortcut or one-off implementation.

Do not lower a genuine kill result to `PARTIAL` to preserve momentum.

## Required return to the coordinating agent and PRO

The worker must return:

- exact result commit or full diff;
- changed-file list;
- receipt path;
- concise verdict;
- commands and checks run;
- test outputs or exact blockers;
- environment and dependency versions;
- engine evidence;
- unresolved failures;
- claim ceiling; and
- whether the packet supported fresh-context execution without user relays.

Do not merge, open a product PR, begin Slice 1, or modify the active contract. The coordinating agent returns the evidence to the PRO owner for diff inspection and adjudication.

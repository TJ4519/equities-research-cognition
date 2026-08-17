# Workbook Capability Spike Receipt

## 1. Verdict

**PARTIAL.** The observed environment reproducibly patched and recalculated the bounded workbook with a real headless engine, but the required committed binary fixture makes the repository's mandatory UTF-8 LOC classifier fail and correcting that integration defect requires a file outside this worker packet's ownership.

This verdict is intentionally lower than the environmental workbook result. The engine result itself was repeatable and independently inspectable. The branch cannot honestly be returned as `PASS` while a mandatory repository check fails.

## 2. Exact basis

- Repository: `TJ4519/equities-research-cognition`.
- Starting branch: `agent/workbook-capability-spike`.
- Packet commit and starting `HEAD`: `de2e3de4a82e21f158087fc747fa4f20f80c8fdd`.
- Exact contract base ancestor: `b238ee2949f71ad04c74dac2700c7714e1018012`; `git merge-base --is-ancestor` returned `0`.
- Result commit: the exact pushed branch head is supplied in the worker return because a Git commit cannot contain its own hash.
- Operating system: macOS 15.3, build `24D2059`, Darwin 24.3.0, arm64.
- Package Python: CPython 3.14.0 from `uv`; host `python3` was CPython 3.14.5.
- `uv`: 0.9.8 (`85c5d3228`, 2025-11-07).
- Package dependencies: unchanged at Django 6.0.7 and Psycopg binary 3.3.4. No spreadsheet package was added.
- Calculation engine: `LibreOfficeDev 26.8.0.0.alpha0`, build `2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`.
- Engine executable observed through `command -v soffice`: `/Users/singh/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice`.

The engine is a development build supplied by the observed Codex runtime, not a repository dependency or a selected production service. Its alpha status and production integration remain unresolved.

## 3. Independent repository verification

Facts verified from the checkout and commands, rather than inherited from the packet, were:

- `pyproject.toml` declared only Django and Psycopg; `openpyxl`, `xlsxwriter`, `formulas`, and `pycel` were unavailable in the package environment.
- No existing `.xlsx` fixture, workbook parser, workbook patcher, formula engine, or workbook-specific test was present.
- `soffice` was installed and returned an exact version. Microsoft Excel and LibreOffice applications were absent from `/Applications`; Apple Numbers was present. `gnumeric` and `ssconvert` were not on `PATH`.
- Java was unavailable.
- `tools/check_boundary.py` permits product process spawning only through `harness/ntm/adapter.py`. The spike therefore invokes the engine only from recorded worker shell commands; committed Python does not spawn a process.
- `tools/classify_loc.py` categorises every file below `scenarios/` as tests and then decodes it as UTF-8. It has no binary-file treatment, so the authorised `.xlsx` fixture causes its mandatory check and the architecture test using it to fail.

Constraints inherited from the active contract were the exact fixture shape, named target, formulas, patch value, engine independence requirement, owned-file boundary, prohibition on product and UI changes, and `PASS | PARTIAL | FAIL` rules.

Unresolved assumptions are production engine selection, deployment and isolation; compatibility with ordinary sell-side workbooks; formula parity with Excel; support beyond the declared formula population; and authority to update the repository's LOC classifier for binary test fixtures.

## 4. Fixture

Path: `prototypes/equities-research-cognition/scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`.

Declared status: `MECHANICAL_REGRESSION_ONLY`. It is purpose-built public mechanical data, not a Micron workbook, analyst evidence, investment research, or a product artifact.

Generation was two-stage and reproducible:

1. `workbook_probe.py generate-raw` created deterministic minimal OOXML with the two required sheets, cells, formulas, named range, simple styles, and explicit formats. Raw digest: `f2db4b4f4b95239f964e56e82efb8e03a3c17083d1be8020745ac1051414e101`.
2. LibreOffice opened and exported that raw workbook once to populate the baseline formula caches. The committed fixture digest is `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b`.

Independent standard-library OOXML inspection verified:

- workbook-defined name `FY25_REVENUE_USDM` refers exactly to `Model!$B$5`;
- `Model!B5` is numeric `36900` with style ID `2` and number format `#,##0` / ID `165`;
- `Model!B6` contains formula `B5/B4-1`, cached value `0.469475528652782`, style ID `3`, and format `0.00%` / ID `166`;
- `Valuation!B5` contains formula `B4/Model!B5`, cached value `3.2520325203252`, style ID `4`, and format `0.00\x` / ID `167`;
- dependency paths are `Model!B5 -> Model!B6` and `Model!B5 -> Valuation!B5`, alongside `Model!B4` and `Valuation!B4`; and
- all target and formula labels have non-default styles and survived the observed engine round trip.

The workbook has no macros, external links, circular references, data tables, volatile functions, or hidden external data.

## 5. Strategy comparison

### Selected route

The spike uses a narrow standard-library OOXML writer/patcher and a separate direct OOXML inspector. The patcher resolves the workbook-defined name rather than hard-coding the worksheet part. It changes the one target input, clears existing formula caches, and requests full calculation; it never writes a dependent result. LibreOffice performs calculation through a non-interactive shell command. The inspector then reopens raw package bytes independently and reads formulas, names, styles, number formats, cached values, errors, and dependency references.

Clearing declared formula caches is calculation invalidation, not manual calculation. Before the engine run both dependent caches were absent. Only the engine populated their new values.

### Candidates considered

- **LibreOfficeDev:** selected because it was installed, versioned, non-interactive, evaluated both fixture formulas, produced inspectable `.xlsx` output, and made an invalid formula visible as `t="e"` / `#NAME?`.
- **Microsoft Excel:** unavailable as an installed application or command-line engine in the observed environment.
- **Apple Numbers:** installed, but no supported reproducible non-interactive calculation/export command was established; rejected because a GUI action would violate the packet.
- **Gnumeric / `ssconvert`:** unavailable.
- **Python parser/writers (`openpyxl`, `xlsxwriter`):** unavailable and not calculation engines. No dependency was added because the standard library was sufficient for the bounded OOXML operation.
- **Python formula libraries (`formulas`, `pycel`):** unavailable; a fixture-specific evaluator would not establish native workbook calculation.
- **Bundled artifact dependency loader:** did not return after repeated bounded waits and was terminated. It was not treated as available evidence or used as a hidden dependency.

## 6. Commands

Grounding and environment commands were:

```text
git status --short --branch
git fetch origin
git switch agent/workbook-capability-spike
git rev-parse HEAD
git merge-base --is-ancestor b238ee2949f71ad04c74dac2700c7714e1018012 HEAD
soffice --version
uv run python -c '<import availability and Python version probe>'
/usr/bin/sw_vers
/usr/bin/uname -a
uv --version
```

Fixture creation used:

```text
uv run python spikes/workbook_capability/workbook_probe.py generate-raw /tmp/workbook-capability-fixture.AMLXvu/raw/workbook_capability_v0.xlsx
soffice -env:UserInstallation=file:///tmp/workbook-capability-fixture.AMLXvu/profile --headless --convert-to xlsx --outdir /tmp/workbook-capability-fixture.AMLXvu/recalculated /tmp/workbook-capability-fixture.AMLXvu/raw/workbook_capability_v0.xlsx
```

Each complete run used the same command shape in its own clean directory:

```text
uv run python spikes/workbook_capability/workbook_probe.py patch scenarios/adversarial/fixtures/workbook_capability_v0.xlsx /tmp/workbook-capability-runs.JECSfh/run-1/patched/candidate.xlsx
soffice -env:UserInstallation=file:///tmp/workbook-capability-runs.JECSfh/run-1/profile --headless --convert-to xlsx --outdir /tmp/workbook-capability-runs.JECSfh/run-1/recalculated /tmp/workbook-capability-runs.JECSfh/run-1/patched/candidate.xlsx
uv run python spikes/workbook_capability/workbook_probe.py verify-run scenarios/adversarial/fixtures/workbook_capability_v0.xlsx /tmp/workbook-capability-runs.JECSfh/run-1/patched/candidate.xlsx /tmp/workbook-capability-runs.JECSfh/run-1/recalculated/candidate.xlsx

uv run python spikes/workbook_capability/workbook_probe.py patch scenarios/adversarial/fixtures/workbook_capability_v0.xlsx /tmp/workbook-capability-runs.JECSfh/run-2/patched/candidate.xlsx
soffice -env:UserInstallation=file:///tmp/workbook-capability-runs.JECSfh/run-2/profile --headless --convert-to xlsx --outdir /tmp/workbook-capability-runs.JECSfh/run-2/recalculated /tmp/workbook-capability-runs.JECSfh/run-2/patched/candidate.xlsx
uv run python spikes/workbook_capability/workbook_probe.py verify-run scenarios/adversarial/fixtures/workbook_capability_v0.xlsx /tmp/workbook-capability-runs.JECSfh/run-2/patched/candidate.xlsx /tmp/workbook-capability-runs.JECSfh/run-2/recalculated/candidate.xlsx
```

The invalid-formula observation used:

```text
uv run python spikes/workbook_capability/workbook_probe.py replace-formula scenarios/adversarial/fixtures/workbook_capability_v0.xlsx /tmp/workbook-capability-invalid.5N5vSp/input/invalid.xlsx Model!B6 'NO_SUCH_FUNCTION(1)'
soffice -env:UserInstallation=file:///tmp/workbook-capability-invalid.5N5vSp/profile --headless --convert-to xlsx --outdir /tmp/workbook-capability-invalid.5N5vSp/recalculated /tmp/workbook-capability-invalid.5N5vSp/input/invalid.xlsx
uv run python spikes/workbook_capability/workbook_probe.py inspect /tmp/workbook-capability-invalid.5N5vSp/recalculated/invalid.xlsx
```

All three observed engine invocations returned status `0`. LibreOffice emitted Fontconfig cache warnings and explicit conversion lines. Invalid-formula failure was visible in the output workbook rather than the process status.

## 7. Before and after evidence

| Fact | Fixture | Patched before engine | Recalculated output |
| --- | --- | --- | --- |
| `FY25_REVENUE_USDM` | `Model!$B$5` | unchanged | unchanged |
| `Model!B5` | `36900` | `37378` | `37378` |
| `Model!B6` formula | `B5/B4-1` | unchanged | unchanged |
| `Model!B6` cache | `0.469475528652782` | absent | `0.488511011110669` |
| independent `Model!B6` result | n/a | n/a | `0.488511011110668631277129545` |
| `Valuation!B5` formula | `B4/Model!B5` | unchanged | unchanged |
| `Valuation!B5` cache | `3.2520325203252` | absent | `3.21044464658355` |
| independent `Valuation!B5` result | n/a | n/a | `3.210444646583551821927336936` |
| formula errors | none | no fabricated values | none |

The patch preserved exact formula strings, the named target, target address, style IDs, style components, and number-format references before engine calculation. LibreOffice remapped relevant cell style IDs by adding a normalised base style (`2/3/4` became `3/4/5` for the target and formulas), while preserving the relevant font, fill, border, and exact number-format codes and IDs. This engine normalisation is recorded rather than presented as byte preservation.

The original fixture digest was `e06961d93384754fd31faf6f14a11a70052722af5be0f3c652c23b859697c98b` before and after every operation.

The invalid formula became `no_such_function(1)` with cell type `e`, cached value `#NAME?`, and was detected at `Model!B6` by the independent inspector.

## 8. Repeat run

Both clean runs produced the same pre-engine candidate digest:

`d458d17ff5afb56b39643047dfa12d00f2fbb0e244d586505ab519ddb8030730`.

Run 1 recalculated digest was `6abc6251f33b417d0e3c6152989198c3baaa57accb29c2e0de6798146232a2c1`. Run 2 recalculated digest was `031f9a901c720acb20644278af9c6192fac57c57285ffab57e7a8d9122b88e6e`.

The two recalculated ZIP containers were not byte-equal. Independent per-member comparison found every uncompressed package member byte-identical, with matching CRC and compressed sizes. The only differences were ZIP entry timestamps: run 1 recorded `2026-08-17 18:02:14`, while run 2 recorded `2026-08-17 18:02:16` for every member. Thus the byte difference is fully explained by engine container metadata; semantic content and every OOXML member were repeatable.

Both runs produced the same target value, formula strings, formula caches, formula-error population, dependencies, names, style semantics, and number formats.

## 9. Checks

Passed:

```text
uv run python -m unittest scenarios.adversarial.test_workbook_capability_spike -v
Ran 3 tests in 0.020s — OK

uv run python -W error manage.py check --fail-level WARNING
System check identified no issues (0 silenced).

uv run python manage.py makemigrations --check --dry-run
No changes detected

uv run python tools/check_boundary.py
cognition package boundary: passed (all runtime-bearing package surfaces)

uv run python -m compileall -q spikes/workbook_capability scenarios/adversarial/test_workbook_capability_spike.py
git diff --check
```

Failed for one exact integration reason:

```text
uv run python -W error manage.py test scenarios.adversarial
Found 118 test(s).
Ran 113 tests in 22.159s.
FAILED (errors=1)
UnicodeDecodeError in tools/classify_loc.py while reading scenarios/adversarial/fixtures/workbook_capability_v0.xlsx as UTF-8.

uv run python tools/classify_loc.py
cognition package LOC classification: FAILED: 'utf-8' codec can't decode byte 0x8f in position 11: invalid start byte
```

No test was skipped. The workbook-specific tests passed. The full-suite failure is not a workbook calculation failure; it is a repository support-tool assumption that every test surface is UTF-8 text. Updating that tool was prohibited by this packet's owned-file list.

One intermediate verification retry was invoked from the repository root instead of the executable-package directory. It returned `ModuleNotFoundError: scenarios` and missing-path errors for `manage.py` and `tools/*`; the same commands were immediately rerun from `prototypes/equities-research-cognition` with the results above. No evidentiary claim relies on the wrong-directory invocation.

Visual verification exported both fixture sheets and both recalculated sheets through LibreOffice to PDF and PNG. All labels and values were legible; the candidate visibly changed revenue from `36,900` to `37,378`, growth from `46.95%` to `48.85%`, and the multiple from `3.25x` to `3.21x` without style loss.

## 10. Boundary review

No Django model, migration, service, view, URL, form, template, setting, prompt, protocol, workbench, skill, cognition lock, Casebook, source policy, campaign state, review state, NTM adapter, Langfuse code, product styling, or analyst-facing UI changed.

No system package, paid service, external infrastructure, private material, manual desktop action, or committed candidate workbook was used. The original fixture remained unchanged. Temporary candidate, engine, invalid-formula, PDF, and PNG outputs remained under `/tmp` and are not tracked.

Committed Python imports no `subprocess` and never invokes LibreOffice. Engine interaction remained a worker-shell capability observation, exactly as the packet permits.

## 11. Unresolved integration work

A production workbook adapter would still require:

- an explicitly selected, supported, licensed, and deployed calculation boundary rather than an alpha runtime binary discovered on one worker host;
- product-process integration through the repository's single authorised spawn boundary or a separately authorised service/API;
- immutable engine input/output custody, timeouts, resource limits, and error receipts;
- a declared supported workbook feature detector and fail-closed refusal path;
- formula-family and Excel-parity testing beyond two arithmetic formulas;
- dependency discovery and invalidation beyond the declared cells;
- macro, link, data-table, circularity, corruption, protection, locale, date-system, and external-data hostile cases;
- storage of pre-engine cache invalidation and post-engine style normalisation as explicit transformation facts; and
- an authorised binary-artifact classification rule so mandatory repository checks can pass.

## 12. Claim ceiling and nonclaims

The strongest supported claim is:

> On this observed arm64 macOS worker, the exact bounded mechanical `.xlsx` fixture can be independently inspected, copied, patched at its workbook-defined target, cache-invalidated without fabricating dependent values, recalculated non-interactively by the exact LibreOfficeDev build, reopened through direct OOXML inspection, and shown to contain repeatable changed dependent values with preserved formulas, name, formats, and style semantics.

This does not establish support for a typical sell-side model, Excel formula parity, a production engine choice, product integration, semantic source admission, a Micron episode, analyst usefulness, UI quality, deployment, institutional authority, or cumulative learning. It is not a product demo.

## 13. Reconstitution experiment

The committed constitution, semantic checkpoint, active contract, repository ground, counterexample register, decision ledger, and worker packet were sufficient to recover the product purpose and execute the slice without asking the user to relay history. They prevented work on UI, prompts, source policy, agent topology, product models, and the manual Micron report.

The one missing coordination fact was an ownership mismatch: the packet requires a binary workbook fixture at a path that the mandatory LOC classifier assumes is UTF-8, but the worker was not authorised to update that classifier. No user relay is needed to understand the defect. The coordinator or PRO must adjudicate the smallest follow-up authority.

## 14. Recommended PRO decision

**Narrow and continue the capability gate, but do not begin Slice 1.** Authorise one separate support-tool change that classifies `.xlsx` test fixtures as binary/generated with zero physical lines, add a hostile classifier test, then rerun the unchanged workbook sequence and all mandatory repository checks. If those checks pass, PRO can adjudicate this environmental capability as `PASS` while keeping the alpha-engine and production-integration nonclaims explicit.

Do not choose another native artifact or kill the Excel-companion hypothesis on this evidence: native patch and calculation capability was observed. Do not promote the slice yet: the branch does not satisfy its mandatory repository check.

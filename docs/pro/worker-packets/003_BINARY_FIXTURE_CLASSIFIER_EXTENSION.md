# Worker Packet 003 — Binary Test-Fixture Classifier Extension

Status: authorised but queued. Do not start until Worker Packet 002 has returned and the PRO has acknowledged its receipt.

Contract: `MU-MODEL-UPDATE-V0`, Slice 0B under `ACTIVE_BUILD_CONTRACT_AMENDMENT_001.md`.

## Objective

Repair the repository's LOC classifier so one authorised binary `.xlsx` mechanical test fixture is classified without being decoded as UTF-8, while hostile binary content masquerading as a text authority surface still fails closed.

This is repository-support work. It cannot upgrade the product hypothesis, conceptual-model claim, Excel integration, analyst usefulness, or Slice 1 authority.

## Exact starting condition

The reconciled workbook spike added:

`prototypes/equities-research-cognition/scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`

The fixture is valid synthetic OOXML and `MECHANICAL_REGRESSION_ONLY`. `tools/classify_loc.py` currently categorises all `scenarios/**` files as tests and then calls `read_text(encoding="utf-8")`, causing:

- `uv run python tools/classify_loc.py` to fail with `UnicodeDecodeError`; and
- the full adversarial suite to stop with one architecture setup error.

The workbook-specific tests passed independently. The Slice 0 verdict remains `PARTIAL` until this integration defect is reconciled.

## Owned files

The worker may modify only:

- `prototypes/equities-research-cognition/tools/classify_loc.py`;
- `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`; and
- `docs/pro/evidence/BINARY_FIXTURE_CLASSIFIER_RECEIPT.md`.

A separate narrow test file may be added under `scenarios/adversarial/` only when keeping hostile classifier tests inside `test_c4_architecture.py` would materially reduce clarity.

No fixture, workbook code, product code, model, service, prompt, protocol, runtime, dependency, source policy, or UI change is permitted.

## Required behaviour

The classifier must distinguish line-countable text surfaces from authorised binary test data.

For the committed workbook fixture:

- category remains `tests`;
- physical line count is `0`;
- the file remains present in the classifier output;
- its binary treatment is explicit in the output rather than silently omitted; and
- it contributes no handwritten line count.

The implementation must not treat every undecodable file as harmless. It must use a narrow positive rule, such as all of:

- path under an explicitly allowed test-fixture directory;
- extension in an explicitly allowed binary-test set;
- regular non-symlink file; and
- sufficient file-signature or package evidence that it is the declared format.

For `.xlsx`, the worker should prefer a narrow standard-library check that the file is a ZIP/OOXML package containing the minimum workbook members needed to distinguish it from arbitrary bytes. Do not turn the LOC classifier into a spreadsheet parser.

## Hostile regressions

Add tests proving:

1. the authorised workbook fixture is classified as `tests`, explicit binary, and zero physical lines;
2. a binary blob with a text-authority extension such as `.py`, `.md`, `.html`, `.json`, or `.yaml` still raises rather than receiving zero lines;
3. random bytes named `.xlsx` outside the authorised fixture path fail;
4. random bytes named `.xlsx` inside the fixture path fail when they are not a valid minimal OOXML workbook package;
5. a symlinked binary fixture fails through the existing regular-surface rule;
6. ordinary UTF-8 test files retain their counted physical lines; and
7. existing totals, pressure calculations, architecture-review checks, and third-party handling remain coherent.

Use temporary directories and synthetic bytes for hostile tests. Do not add another committed binary fixture unless unavoidable.

## Invariants

- `generated` continues to mean ignored/generated environment material, not arbitrary binary data.
- A binary workbook fixture remains test data, not generated product output.
- The classifier output schema may gain an explicit field such as `measurement: binary_fixture` or `line_counted: false`; any change must be deterministic and covered.
- Existing text files must still decode strictly as UTF-8.
- Unknown surfaces must remain unclassified errors.
- Symlinks remain forbidden.
- No broad `except UnicodeDecodeError: lines = 0` implementation is acceptable.

## Checks

Run from `prototypes/equities-research-cognition`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
uv run python -m unittest scenarios.adversarial.test_workbook_capability_spike -v
git diff --check
```

Rerun the unchanged two clean workbook patch/recalculation/verification sequences from Worker Packet 001. Do not modify the workbook fixture, probe, expected values, or engine procedure merely to obtain a passing result.

Record exact commands, test count, warnings, and failures. A skipped test is not a pass.

## Receipt

Create `docs/pro/evidence/BINARY_FIXTURE_CLASSIFIER_RECEIPT.md` with:

1. exact base and result commits;
2. changed files;
3. defect reproduced before change;
4. narrow classification rule selected and alternatives rejected;
5. hostile regressions;
6. classifier output for the workbook fixture;
7. full mandatory checks;
8. unchanged workbook-sequence result;
9. boundary review;
10. unresolved facts; and
11. `PASS | PARTIAL | FAIL` recommendation.

## Verdict

`PASS` requires all mandatory checks and the unchanged workbook sequence to pass, with no broad decode suppression and no prohibited change.

`PARTIAL` means the fixture is classified but hostile fail-closed behaviour, full tests, or unchanged workbook evidence is incomplete.

`FAIL` means the repository cannot support the binary test fixture without weakening classification discipline or changing prohibited surfaces.

## Claim ceiling

A `PASS` establishes only that the repository can carry and classify the authorised synthetic `.xlsx` test fixture and rerun its mechanical capability checks. It does not establish Excel support, production recalculation, conceptual-model understanding, source admissibility, analyst usefulness, or permission to begin Slice 1.

Return the result directly to the PRO owner and coordinator. Do not merge, begin Slice 1, or reinterpret a classifier pass as product evidence.
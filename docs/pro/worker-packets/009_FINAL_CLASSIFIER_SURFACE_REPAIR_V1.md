# Worker Packet 009 — Final Classifier Surface Repair V1

Status: **authorised as a disjoint repository-hygiene repair after Packet 005 rejection**.

This packet supersedes Packet 007. It is compiled from the actual rejected evidence head and must not use Packet 007 as an instruction source.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Exact repository/evidence basis: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Implementation commit in that ancestry: `cf5685383654c00513825fc451b60221bc0117e9`
- Worker branch: `agent/classifier-final-surface-repair-v1`
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Governing repair-contract commit: `21384f3bdd6510fda78f8e1d8cacae91ca7efe46`
- Current classifier blob: `a82829e967baf70dc1900f1ca5a2285bf5f9bcf3`

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor 3d5c3157f91361bee120c10ecd4bddfda6e16296 HEAD
git diff --name-status 3d5c3157f91361bee120c10ecd4bddfda6e16296...HEAD
```

The initial branch may add only this packet and exact dispatch metadata. Stop on product-code, migration, fixture, receipt, or test drift outside that metadata.

## Actual defect to close

At the final Packet 005 evidence head, the classifier no longer fails first on the workbook. The new executable-package path:

`docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`

is not covered by the current `category()` rules, so classification raises `unclassified cognition-package surface` before it reaches the binary `.xlsx` fixture.

The tracked workbook fixture is:

`scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`

The earlier packet’s assumed `spikes/.../minimal_model.xlsx` path is not the final surface and must not govern this repair.

The repair must close both exact issues:

1. classify the package-level evidence receipt as strict UTF-8 documentation/evidence data; and
2. measure the one authorised validated OOXML fixture as binary test data with zero physical lines.

The fresh coordinator run at the evidence head discovered 143 tests, executed 138, and stopped on one architecture setup error. Do not copy the rejected receipt’s earlier counts as current evidence.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read:

1. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
2. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001
3. `docs/pro/evidence/HOSTILE_VERTICAL_REVIEW_RECEIPT.md`
4. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
5. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
6. latest ledger and checkpoint
7. rejected implementation receipt at `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
8. `prototypes/equities-research-cognition/tools/classify_loc.py`
9. `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`
10. tracked workbook fixture and workbook-capability tests
11. this packet

Do not read or revive Packet 007 as authority.

## Objective

Make `tools/classify_loc.py` traverse the exact evidence-head tree while preserving strict fail-closed treatment:

- package-level public evidence markdown is counted as UTF-8 `docs_data`;
- the exact authorised valid workbook fixture is present as category `tests`, measured explicitly as binary, and contributes zero physical lines;
- ordinary text remains strict UTF-8;
- unknown, malformed, misleading, or out-of-scope binary surfaces fail closed; and
- symlinks remain rejected.

This is repository hygiene. It cannot establish product behaviour, spreadsheet support, Excel compatibility, analyst usefulness, professional correctness, or readiness.

## Owned files

The worker may modify only:

- `prototypes/equities-research-cognition/tools/classify_loc.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`

The worker may add one focused file only if needed:

- `prototypes/equities-research-cognition/scenarios/adversarial/test_final_classifier_surface_v1.py`

Required root-level receipt:

- `docs/pro/evidence/FINAL_CLASSIFIER_SURFACE_REPAIR_V1_RECEIPT.md`

The worker may copy this packet onto its branch as dispatch metadata. No other path is owned.

## Strict text classification

The exact package prefix:

`docs/pro/evidence/`

may be classified as `docs_data` only when the file:

- is a regular non-symlink file;
- has an explicitly allowed text extension used by the repository, including `.md` and `.json` where present; and
- decodes strictly as UTF-8.

Do not broadly classify every unknown `docs/**` path without inspecting the current tree and tests. Use the smallest rule that covers the existing public evidence surfaces.

An invalid UTF-8 `.md` or `.json` under the evidence prefix must fail. Binary content must not become zero-line documentation.

## Exact binary fixture classification

The only currently authorised workbook path is:

`scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`

A regular non-symlink file at that exact path may be measured as binary only when standard-library validation proves:

- `.xlsx` suffix;
- valid ZIP structure;
- `[Content_Types].xml`;
- `_rels/.rels`;
- `xl/workbook.xml`;
- the workbook relationship part; and
- at least one worksheet relationship/member required by the committed fixture.

The classifier need not parse formulas or spreadsheet semantics.

The output row must remain present and state explicitly, with equivalent fields if names differ:

```json
{
  "path": "scenarios/adversarial/fixtures/workbook_capability_v0.xlsx",
  "category": "tests",
  "physical_lines": 0,
  "measurement": "binary_fixture",
  "line_counted": false
}
```

The fixture is not `generated` and does not disappear from the inventory.

## Fail-closed law

The following must fail:

- random bytes at the authorised `.xlsx` path;
- a generic ZIP renamed `.xlsx`;
- malformed OOXML missing a required member;
- a valid workbook at any other repository path;
- any `.xlsx` under a broad `fixtures/` or `scenarios/` prefix not exactly authorised;
- binary data with `.md`, `.json`, `.py`, `.html`, `.txt`, `.yaml`, or `.yml` extension;
- an unknown extension;
- a symlink to the valid workbook;
- a symlink to valid evidence markdown; and
- path-normalisation or case tricks that escape the exact allowlist.

Do not catch `UnicodeDecodeError` broadly, accept by suffix alone, accept all ZIP files, accept all `.xlsx`, or count undecodable surfaces as zero lines.

## Required hostile tests

At minimum prove:

1. the real `CASE_A_IMPLEMENTATION_RECEIPT.md` is classified as `docs_data` and has positive UTF-8 line count;
2. an invalid UTF-8 evidence `.md` fails;
3. the exact real workbook is `tests`, `binary_fixture`, zero lines, and present in the inventory;
4. random bytes at the workbook path fail;
5. misleading ZIP/OOXML fails;
6. a valid workbook copied outside the exact path fails;
7. binary data with text extension fails;
8. unknown binary fails;
9. workbook and evidence symlinks fail; and
10. existing architecture-pressure totals remain internally consistent.

Tests may use temporary directories and monkeypatch the module’s root only when they preserve the same path and validation semantics as the real tree.

## Required commands

Run from the executable package:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test \
  scenarios.adversarial.test_c4_architecture \
  scenarios.adversarial.test_final_classifier_surface_v1 -v 2
uv run python -W error manage.py test \
  scenarios.adversarial.test_workbook_capability_spike -v 2
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check
```

Omit the optional focused module from the command when no new file was added. Record exact discovered/executed counts and every warning/error. The full suite must reach completion rather than stop during architecture setup.

## Prohibited changes

Do not modify:

- any product model, migration, service, view, route, template, setting, form, projection, or fixture;
- any NTM/runtime adapter;
- prompts, protocols, skills, or workbenches;
- the rejected implementation receipt;
- Packet 008 files;
- direct-Excel surfaces;
- ledger, checkpoint, or governing architecture on the worker branch;
- dependencies or `pyproject.toml`.

Do not delete, move, regenerate, replace, or re-encode the workbook or receipt to make the classifier pass.

## Return receipt

Create:

`docs/pro/evidence/FINAL_CLASSIFIER_SURFACE_REPAIR_V1_RECEIPT.md`

Return directly to PRO and coordinating Codex:

- exact base, branch, result commit, and evidence commit;
- changed-file audit;
- pre-repair first-failure reproduction;
- exact evidence-prefix rule;
- exact workbook allowlist and package validation;
- hostile regression results;
- classifier output totals and relevant rows;
- full adversarial discovered/executed counts;
- all warnings/errors;
- claim ceiling; and
- verdict `PASS_FOR_INTEGRATION`, `PARTIAL`, or `FAIL`.

Do not merge or update governing state.

## Stop conditions

Stop on:

- moved base or unexpected product/test drift;
- need to accept a broad path or suffix rule;
- inability to keep evidence text strict UTF-8;
- inability to validate the workbook narrowly with the standard library;
- need to touch product code or fixtures; or
- a second failed repair with the same causal diagnosis.

## Claim ceiling

A pass establishes only that the exact evidence-head package inventory can be classified without weakening fail-closed text/binary rules. It does not establish that Packet 005 is acceptable, that workbook semantics are supported, that Excel works, or that any product claim is verified.
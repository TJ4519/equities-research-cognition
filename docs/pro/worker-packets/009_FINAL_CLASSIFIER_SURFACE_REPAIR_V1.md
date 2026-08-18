# Worker Packet 009 — Final Classifier Surface Repair V1

Status: **authorised parallel repository-hygiene repair; no product authority**.

Programme state: `REPAIRING`.

This packet supersedes Packet 007. It is newly compiled from the final Packet 005 evidence tree and must not use historical Packet 007 as an instruction source.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Exact rejected evidence basis: `3d5c3157f91361bee120c10ecd4bddfda6e16296`
- Rejected implementation: `cf5685383654c00513825fc451b60221bc0117e9`
- Worker branch: `agent/classifier-final-surface-repair-v1`
- Governing repair contract: `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
- Coordinator projection: `dec-2026-08-18-037`
- Current classifier at the evidence basis: `prototypes/equities-research-cognition/tools/classify_loc.py`

Before editing, verify:

```text
git rev-parse HEAD
git merge-base --is-ancestor 3d5c3157f91361bee120c10ecd4bddfda6e16296 HEAD
git diff --name-status 3d5c3157f91361bee120c10ecd4bddfda6e16296...HEAD
```

The initial branch delta may contain only this packet. Stop with `MOVED_CLASSIFIER_BASE` on unexpected classifier, test, fixture, product, migration, prompt, or evidence drift.

## Objective

Make the LOC/classification tool traverse the complete rejected Packet 005 evidence tree without weakening strict text decoding or fail-closed treatment of unknown binary surfaces.

The repair must address both final surfaces in their actual order:

1. package-level evidence markdown under `docs/pro/evidence/`, beginning with `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`; and
2. the exact authorised binary workbook fixture `scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`.

This work is repository hygiene. It cannot establish product behaviour, candidate authority, workbook compatibility, Excel parity, analyst value, professional correctness, deployment readiness, or repair of Packet 005.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read:

1. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
2. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001
3. `docs/pro/evidence/HOSTILE_VERTICAL_REVIEW_RECEIPT.md`, especially S2-7
4. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
5. `prototypes/equities-research-cognition/docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md`
6. `docs/pro/CASE_A_BOUNDED_REPAIR_CONTRACT_V1.md`
7. latest ledger and checkpoint
8. `prototypes/equities-research-cognition/tools/classify_loc.py`
9. `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`
10. exact workbook fixture and workbook-capability tests
11. this packet

## Reproduce before editing

Run from `prototypes/equities-research-cognition`:

```text
uv run python tools/classify_loc.py
uv run python -W error manage.py test scenarios.adversarial -v 1
```

Record the actual first failure at evidence head `3d5c3157...`.

Expected reproduction:

- the classifier raises on unclassified `docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md` before it measures the workbook;
- the complete suite discovers 143 tests, executes 138, and stops with one architecture setup error in the coordinator’s reproduced environment; and
- after the evidence-path category is provisionally understood, the tracked workbook would still fail strict UTF-8 unless explicitly handled as an authorised binary fixture.

If the first failure or counts differ, preserve the observed result in the receipt and repair the exact current surface without broadening authority. Stop on material tree drift.

## Exact owned files

You may modify only:

- `prototypes/equities-research-cognition/tools/classify_loc.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`

You may add exactly one focused test file if required for hostile readability:

- `prototypes/equities-research-cognition/scenarios/adversarial/test_final_classifier_surface_v1.py`

Required receipt:

- `docs/pro/evidence/FINAL_CLASSIFIER_SURFACE_REPAIR_V1_RECEIPT.md`

No other path is owned.

## Prohibited changes

Do not modify:

- product models, migrations, services, views, routes, templates, settings, fixtures, or management commands;
- runtime adapters, prompts, protocols, workbenches, skills, or model policy;
- any workbook or source fixture;
- Packet 008 files or Case A repair code;
- existing implementation receipt content;
- ledger, checkpoint, contract, issues, PR, or governing architecture;
- dependencies or `pyproject.toml`;
- direct Excel work or cloud artifacts.

Do not delete, rename, move, regenerate, re-encode, or replace a file merely to make classification pass.

## Required category repair for package evidence

The executable package now contains public evidence records under:

`docs/pro/evidence/`

Classify regular non-symlink files under that exact root as `docs_data` only when they are known text extensions already permitted elsewhere by the package classifier, including `.md` and explicitly present structured-text formats.

Requirements:

- strict UTF-8 decode remains mandatory;
- physical lines are counted normally;
- binary bytes in `.md`, `.json`, `.txt`, `.html`, `.py`, or another text extension raise;
- path traversal, symlink, and unexpected nested surface tests fail closed;
- do not classify all `docs/**`, all `evidence/**` anywhere, or an arbitrary unknown extension merely because it is under the directory; and
- the existing root-level `evidence/` category remains intact.

At minimum, lock the exact final-tree row for:

`docs/pro/evidence/CASE_A_IMPLEMENTATION_RECEIPT.md -> docs_data, strict UTF-8, physical lines > 0`

## Required binary fixture contract

The only workbook currently authorised for binary measurement is:

`scenarios/adversarial/fixtures/workbook_capability_v0.xlsx`

Prefer an exact-file allowlist. A root allowlist is acceptable only when tests prove it contains exactly the committed authorised workbook at this basis and unknown additions still fail closed.

A file may be measured as binary test data only when all conditions hold:

- exact allowlisted path;
- `.xlsx` extension;
- regular non-symlink file;
- valid ZIP central directory;
- no unsafe member path such as absolute or `..` traversal;
- required OOXML workbook members exist, including `[Content_Types].xml`, `_rels/.rels`, and `xl/workbook.xml`;
- workbook relationship/member structure is sufficient to distinguish a workbook from arbitrary ZIP bytes; and
- validation uses only the standard library or existing dependencies—do not add a spreadsheet parser.

The emitted row remains category `tests` and must make binary treatment explicit, for example:

```json
{
  "path": "scenarios/adversarial/fixtures/workbook_capability_v0.xlsx",
  "category": "tests",
  "physical_lines": 0,
  "measurement": "binary_ooxml_fixture",
  "line_counted": false
}
```

Equivalent field names are allowed only when equally explicit and hostile tests lock their meaning.

The fixture is not `generated` and is not counted as handwritten text.

## Fail-closed law

The following must raise rather than receive zero lines:

- random binary bytes;
- an arbitrary ZIP renamed `.xlsx`;
- malformed/truncated OOXML;
- OOXML missing required workbook members;
- ZIP members with unsafe paths;
- a valid workbook copied outside the exact allowlist;
- another `.xlsx` elsewhere in `scenarios/`, `fixtures/`, `docs/`, `product/`, or repository root;
- a binary file with `.md`, `.json`, `.txt`, `.py`, `.html`, or another text extension;
- an unknown extension;
- a symlink to the valid evidence markdown or workbook;
- a symlinked directory path; and
- case/path tricks intended to escape the allowlist.

Broad `UnicodeDecodeError` suppression, broad suffix-only acceptance, `errors="ignore"`, Latin-1 fallback, treating all fixtures as binary, or treating all undecodable files as zero-line data is prohibited.

## Required implementation shape

Keep category selection separate from measurement.

A narrow acceptable shape is:

```text
category(path) -> existing category including docs/pro/evidence text
measurement(path, category) -> strict_text | authorised_ooxml_binary
text_lines(path) -> strict UTF-8
validate_authorised_ooxml(path) -> explicit narrow package validation
```

Do not turn the LOC tool into a workbook semantic parser or make it depend on product code.

Existing pressure totals and architecture-review logic must remain semantically unchanged except for the correct addition of evidence text lines and zero-line binary fixture measurement.

## Mandatory hostile regressions

Add tests proving:

1. `CASE_A_IMPLEMENTATION_RECEIPT.md` is `docs_data`, strict UTF-8, and line-counted.
2. A binary `.md` at that path or a temporary equivalent fails.
3. The exact tracked workbook is `tests`, `physical_lines=0`, and explicitly binary.
4. Random bytes at the exact workbook path in a temporary root fail package validation.
5. A generic ZIP with required-looking name but missing members fails.
6. A truncated or corrupt workbook fails.
7. A ZIP with unsafe member paths fails.
8. A valid workbook outside the allowlist fails.
9. A second `.xlsx` under a broad fixture directory fails unless separately and explicitly authorised by code and test.
10. Symlinked evidence markdown and workbook fail.
11. Unknown binary and unknown text surfaces fail.
12. Existing category, pressure, architecture-review, third-party, and migration tests remain unchanged.

Tests must use temporary files and copies; do not mutate committed fixtures.

## Command floor

Run from `prototypes/equities-research-cognition`:

```text
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

Omit the optional focused module from the command only when no file was created; record the exact command used.

The full adversarial suite must complete rather than stop during test setup. Record fresh discovered and executed counts; do not repeat the Packet 005 receipt’s stale 142/137 count or the coordinator’s 143/138 count after the repair without rerunning.

## Receipt contract

Create `docs/pro/evidence/FINAL_CLASSIFIER_SURFACE_REPAIR_V1_RECEIPT.md` last with:

- verdict: `PASS`, `PARTIAL`, or `FAIL`;
- exact base, branch, implementation commit, and evidence commit;
- exact changed files;
- reproduced pre-repair first failure and counts;
- exact evidence-path category rule;
- exact workbook allowlist and OOXML package validation rule;
- emitted row examples for evidence markdown and workbook;
- hostile negative cases and results;
- classifier totals before/after where relevant;
- focused, workbook, complete adversarial, boundary, classifier, and diff-check commands/results;
- fresh discovered/executed test counts;
- unresolved facts; and
- claim ceiling.

Return directly to PRO/coordinating Codex. Do not merge, update `agent/pro-grounding`, modify issues/PR, or claim product evidence.

## Stop conditions

Stop and return `PARTIAL` or `FAIL` when:

- the initial classifier/evidence tree moved;
- the actual first failure cannot be reproduced and a different material surface exists;
- strict UTF-8 cannot be retained for text;
- the workbook cannot be handled without a broad binary exception;
- package validation requires fixture mutation or new dependencies;
- a prohibited file must change;
- the complete adversarial suite still stops during classifier setup;
- an unknown binary or symlink is silently accepted; or
- pressure/accounting semantics must be weakened.

A narrow failure is preferable to a permissive classifier.

## Claim ceiling

A passing result proves only that the repository’s LOC/classification tool can traverse the exact current public tree, count strict UTF-8 package evidence, and explicitly measure one authorised OOXML test fixture without weakening hostile binary rejection. It does not establish any Case A repair, spreadsheet support, Excel compatibility, product behaviour, analyst value, professional correctness, or readiness.

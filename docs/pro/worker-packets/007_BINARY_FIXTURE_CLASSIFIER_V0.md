# Worker Packet 007 — Binary Fixture Classifier Repair V0

Status: **authorised as a parallel repository-hygiene dependency**.

This packet is newly compiled from the current repository and hostile-review evidence. It does not reactivate or incorporate historical Packet 003.

## Exact branch and basis

- Repository: `TJ4519/equities-research-cognition`
- Authoritative implementation basis: `1798427cadad65e286e8e124b261dfb31903fec0`
- Worker branch: `agent/binary-fixture-classifier-v0`
- Current classifier blob at the basis: `a82829e967baf70dc1900f1ca5a2285bf5f9bcf3`
- Hostile review result: `99ad9412f059239c0604497b3de868b6c348370a`
- Known failure: `tools/classify_loc.py` attempts strict UTF-8 decoding of an authorised binary `.xlsx` test fixture and causes the full adversarial suite to stop during architecture-test setup.

The worker branch will descend from a packet-bundle commit whose non-code delta from the basis is limited to governance, evidence, packet, ledger, checkpoint and dispatch metadata. Verify ancestry and initial changed files. Stop on product-code or migration drift.

## Objective

Repair the LOC/classification tool so a valid, authorised binary `.xlsx` test fixture is explicitly classified as binary test data with zero physical lines, while every text authority surface remains strict UTF-8 and hostile binary content continues to fail closed.

This is repository support work. It cannot establish spreadsheet support, Excel compatibility, product behaviour, conceptual understanding, analyst value, professional correctness, or readiness of the Case A vertical.

## Required read order

After root and package `AGENTS.md` and `ROUTE.md`, read:

1. `docs/pro/END_TO_END_DELIVERY_COMMISSION.md`
2. `docs/pro/AUTONOMOUS_PRODUCT_OWNER_CHARTER.md` and Amendment 001
3. `docs/pro/evidence/HOSTILE_VERTICAL_REVIEW_RECEIPT.md`, especially S2-7
4. `docs/pro/CASE_A_OUTCOME_COMPLETE_VERTICAL_CONTRACT_V0.md`
5. `docs/pro/evidence/MILESTONE_1_HOSTILE_REVIEW_RECONCILIATION_RECEIPT.md`
6. latest decision ledger and checkpoint
7. `prototypes/equities-research-cognition/tools/classify_loc.py`
8. `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`
9. the existing workbook fixture paths and workbook-capability tests
10. this packet

Do not use historical Packet 003 as an instruction source.

## Exact current defect

`classify()` enumerates regular files, obtains a category, and calls `text_lines(path)` for every non-generated surface. `text_lines()` performs `read_text(encoding="utf-8")`. A valid `.xlsx` fixture is a ZIP/OOXML binary package, so strict text decoding raises `UnicodeDecodeError` before the full adversarial suite can run.

The repair must recognise only an explicitly authorised binary-test surface. It must not turn undecodable files into zero-line files generally.

## Owned files

The worker may modify only:

- `prototypes/equities-research-cognition/tools/classify_loc.py`
- `prototypes/equities-research-cognition/scenarios/adversarial/test_c4_architecture.py`

The worker may add exactly one focused test file only when keeping hostile cases in `test_c4_architecture.py` materially harms clarity:

- `prototypes/equities-research-cognition/scenarios/adversarial/test_binary_fixture_classifier_v0.py`

Required receipt:

- `docs/pro/evidence/BINARY_FIXTURE_CLASSIFIER_V0_RECEIPT.md`

No other path is owned.

## Explicitly prohibited files and changes

Do not modify:

- any product model, migration, service, view, route, template or setting;
- any prompt, protocol, skill, workbench or runtime adapter;
- any workbook fixture, workbook probe or workbook-capability test;
- Packet 005 or Packet 006 files;
- decision ledger, checkpoint or governing architecture;
- dependencies or `pyproject.toml`;
- product fixtures, source policy or UI.

Do not delete, rename, regenerate, re-encode, move, or replace the binary workbook fixture merely to make classification pass.

## Required classification contract

### Valid authorised `.xlsx` fixture

For a regular non-symlink `.xlsx` file under an explicitly authorised test-fixture root, the classifier may treat it as binary only when a narrow standard-library validation proves it is a valid OOXML workbook package.

At minimum require:

- exact path under an allowlisted fixture root;
- `.xlsx` extension;
- regular non-symlink file;
- valid ZIP structure; and
- minimum OOXML workbook members sufficient to distinguish a workbook from arbitrary ZIP bytes, including `[Content_Types].xml`, `_rels/.rels`, `xl/workbook.xml`, and the workbook relationship surface needed by the implementation.

Do not turn the LOC tool into a spreadsheet semantic parser.

The emitted row must remain present and include deterministic explicit binary treatment, for example:

```json
{
  "path": ".../minimal_model.xlsx",
  "category": "tests",
  "physical_lines": 0,
  "measurement": "binary_fixture",
  "line_counted": false
}
```

Field names may differ only when equally explicit and tests lock their meaning.

The valid fixture contributes zero handwritten physical lines and remains in the `tests` category. It is not `generated`.

### Text surfaces

All ordinary text surfaces continue to decode strictly as UTF-8. Invalid bytes in `.py`, `.md`, `.html`, `.json`, `.yaml`, `.yml`, templates, protocols, prompts, settings, migrations, tests, or support code must raise rather than receive zero lines.

### Unknown binary surfaces

Unknown extensions, arbitrary binaries, binary files outside allowed fixture roots, and malformed or misleading `.xlsx` files fail closed.

### Symlinks

Symlinked files remain rejected before measurement, including symlinks to a valid workbook fixture.

## Allowlist law

Prefer the smallest path allowlist that covers the committed authorised workbook test fixture(s) actually present at the implementation basis.

The worker must inspect the repository and name the exact roots selected in the receipt. Candidate roots may include the existing workbook-capability fixture directory and a narrow adversarial fixture directory only where a committed valid `.xlsx` exists there.

Do not allow all `scenarios/**`, all `fixtures/**`, all `.xlsx` files, all ZIP packages, or all undecodable files.

## Hostile regression cases

Add tests proving:

1. the committed valid workbook fixture is present in classifier output, category `tests`, explicitly binary, and zero physical lines;
2. ordinary UTF-8 files preserve exact physical line counts;
3. binary bytes with text-authority extensions such as `.py`, `.md`, `.html`, `.json`, `.yaml`, or `.yml` raise;
4. random bytes named `.xlsx` outside an authorised root raise;
5. random bytes named `.xlsx` inside an authorised root raise;
6. a generic ZIP renamed `.xlsx` but missing required OOXML members raises;
7. a partial/malformed OOXML ZIP missing a required member raises;
8. a valid `.xlsx` copied outside the allowed root raises or remains unclassified according to the existing fail-closed rule;
9. a symlink to a valid `.xlsx` raises;
10. existing generated, third-party, schema, docs, support, operational, and test totals remain coherent;
11. architecture-review pressure calculations remain unchanged except for explicit row metadata; and
12. the full adversarial suite reaches and executes workbook tests instead of failing in classifier setup.

Use temporary directories and synthetic bytes/ZIPs for hostile cases. Do not add another committed binary fixture.

## Invariants

- `generated` remains ignored/generated environment material, not arbitrary binary test data.
- A workbook fixture remains `tests`, not operational code or docs.
- Unknown surfaces remain errors.
- Strict UTF-8 remains the default.
- No broad `except UnicodeDecodeError`, `errors="ignore"`, `errors="replace"`, suffix-only zero-line rule, MIME guess, or magic-number-only acceptance is permitted.
- No path substring broad enough to accept unrelated binary fixtures is permitted.
- Existing JSON output remains deterministic and backward-compatible except for an explicit binary-measurement field.
- File byte count does not substitute for line count.
- No workbook semantic or product claim may appear in the tool or receipt.

## Mandatory commands

Run from `prototypes/equities-research-cognition`:

```text
uv run python -W error manage.py check --fail-level WARNING
uv run python manage.py makemigrations --check --dry-run
uv run python -W error manage.py test scenarios.adversarial.test_c4_architecture -v 2
uv run python -W error manage.py test scenarios.adversarial.test_binary_fixture_classifier_v0 -v 2
uv run python -W error manage.py test scenarios.adversarial.test_workbook_capability_spike -v 2
uv run python -W error manage.py test scenarios.adversarial -v 1
uv run python tools/check_boundary.py
uv run python tools/classify_loc.py
git diff --check
```

If the optional focused test file is not created, omit only that exact test command and state why its cases live in `test_c4_architecture.py`.

Record exact environment versions, commands, exits, test counts, warnings, failures, fixture path and digest, selected allowlist roots, and relevant classifier row/output.

## Required receipt

Create `docs/pro/evidence/BINARY_FIXTURE_CLASSIFIER_V0_RECEIPT.md` with:

1. verdict: `PASS | PARTIAL | FAIL`;
2. exact base, branch, result commit and ancestry;
3. changed-file ownership audit;
4. exact defect reproduction before change;
5. exact allowed fixture roots and why each is minimal;
6. OOXML package validation rule;
7. emitted classifier schema/row for the valid fixture;
8. strict text behaviour;
9. all hostile regression results;
10. complete mandatory command results;
11. full adversarial test count and whether the prior setup failure is gone;
12. boundary and architecture-pressure result;
13. unresolved facts;
14. claim ceiling and nonclaims; and
15. recommended PRO disposition.

## Verdict rules

### PASS

All mandatory checks and hostile cases pass; the valid authorised workbook is explicit binary test data with zero lines; text remains strict; unknown binaries and misleading `.xlsx` files fail closed; and no prohibited surface changed.

### PARTIAL

The original crash is repaired but one or more hostile, full-suite, boundary, determinism, or ownership conditions remain incomplete.

### FAIL

The repository cannot carry the binary fixture without broad decode suppression, unsafe allowlisting, weakening unknown-surface rejection, modifying the fixture, or changing prohibited product surfaces.

## Claim ceiling

A `PASS` establishes only that repository LOC classification can safely carry explicitly authorised valid `.xlsx` test fixtures while preserving fail-closed text and binary treatment. It does not establish workbook support, adapter correctness, Excel compatibility, product behaviour, analyst value, or readiness of Packet 005.

## Stop conditions

Stop on:

- moved classifier/test basis;
- a required change outside owned files;
- need to modify or replace the fixture;
- need for a new dependency;
- inability to define a narrow positive rule;
- regression that accepts malformed or unrelated binaries;
- full-suite failures with a different causal diagnosis requiring product changes; or
- two local repair attempts with the same failure and no new evidence.

Return directly to PRO and coordinating Codex. Do not merge, update the ledger/checkpoint, edit product code, or ask the user to relay evidence.

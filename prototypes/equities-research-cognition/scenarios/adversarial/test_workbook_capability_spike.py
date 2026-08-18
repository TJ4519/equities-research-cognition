from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from spikes.workbook_capability.workbook_probe import (
    FORMULAS,
    TARGET_NAME,
    TARGET_REFERENCE,
    digest,
    inspect_workbook,
    patch_target,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = PACKAGE_ROOT / "scenarios/adversarial/fixtures/workbook_capability_v0.xlsx"


class WorkbookCapabilitySpikeTests(unittest.TestCase):
    """MECHANICAL_REGRESSION_ONLY for the bounded native-workbook profile."""

    def test_fixture_has_exact_named_target_formulas_styles_and_formats(self) -> None:
        evidence = inspect_workbook(FIXTURE)
        self.assertEqual(TARGET_NAME, evidence.named_range)
        self.assertEqual(TARGET_REFERENCE, evidence.named_range_target)
        self.assertEqual("25111", evidence.cells["Model!B4"].value)
        self.assertEqual("36900", evidence.cells["Model!B5"].value)
        self.assertEqual("120000", evidence.cells["Valuation!B4"].value)
        self.assertEqual("FY2024 revenue", evidence.cells["Model!A4"].value)
        self.assertEqual("FY2025 revenue", evidence.cells["Model!A5"].value)
        self.assertEqual("FY2025 revenue growth", evidence.cells["Model!A6"].value)
        self.assertEqual("Enterprise value assumption", evidence.cells["Valuation!A4"].value)
        self.assertEqual("EV / FY2025 revenue", evidence.cells["Valuation!A5"].value)
        self.assertEqual(FORMULAS["Model!B6"], evidence.cells["Model!B6"].formula)
        self.assertEqual(FORMULAS["Valuation!B5"], evidence.cells["Valuation!B5"].formula)
        self.assertEqual(("Model!B5", "Model!B4"), evidence.dependencies["Model!B6"])
        self.assertEqual(
            ("Valuation!B4", "Model!B5"),
            evidence.dependencies["Valuation!B5"],
        )
        self.assertEqual(2, evidence.cells["Model!B5"].style_id)
        self.assertEqual("#,##0", evidence.cells["Model!B5"].number_format_code)
        self.assertEqual("0.00%", evidence.cells["Model!B6"].number_format_code)
        self.assertEqual("0.00\\x", evidence.cells["Valuation!B5"].number_format_code)
        self.assertNotEqual(0, evidence.cells["Model!B6"].style_id)
        self.assertNotEqual(0, evidence.cells["Valuation!B5"].style_id)
        self.assertEqual((), evidence.formula_errors)

    def test_patch_resolves_name_changes_only_target_semantics_and_preserves_original(self) -> None:
        original_bytes = FIXTURE.read_bytes()
        original = inspect_workbook(FIXTURE)
        with TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "candidate.xlsx"
            patch_target(FIXTURE, candidate, Decimal("37378"))
            patched = inspect_workbook(candidate)
        self.assertEqual(sha256(original_bytes).hexdigest(), digest(FIXTURE))
        self.assertEqual(original_bytes, FIXTURE.read_bytes())
        self.assertEqual("37378", patched.cells["Model!B5"].value)
        self.assertIsNone(patched.cells["Model!B6"].value)
        self.assertIsNone(patched.cells["Valuation!B5"].value)
        self.assertEqual(original.named_range_target, patched.named_range_target)
        for cell, formula in FORMULAS.items():
            self.assertEqual(formula, patched.cells[cell].formula)
            self.assertEqual(original.cells[cell].style_id, patched.cells[cell].style_id)
            self.assertEqual(
                original.cells[cell].number_format_id,
                patched.cells[cell].number_format_id,
            )

    def test_patch_bytes_and_semantics_repeat(self) -> None:
        with TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.xlsx"
            second = Path(temporary) / "second.xlsx"
            patch_target(FIXTURE, first)
            patch_target(FIXTURE, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            first_evidence = inspect_workbook(first)
            second_evidence = inspect_workbook(second)
            self.assertEqual(first_evidence.cells, second_evidence.cells)
            self.assertEqual(first_evidence.named_range_target, second_evidence.named_range_target)


if __name__ == "__main__":
    unittest.main()

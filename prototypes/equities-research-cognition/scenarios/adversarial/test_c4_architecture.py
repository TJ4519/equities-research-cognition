from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ArchitectureBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "tools" / "classify_loc.py"
        spec = importlib.util.spec_from_file_location("loc_classifier", path)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.result = cls.module.classify()

    def test_pressure_includes_shipped_docs_templates_configuration_and_schema(self) -> None:
        self.assertEqual(
            self.result["architecture_review_required"],
            self.result["totals"]["operational_code"]
            > self.result["pressure"]["operational_code_architecture_review"],
        )
        if self.result["architecture_review_required"]:
            self.assertTrue(self.result["architecture_review"]["recorded"])
            self.assertEqual(
                "docs/plans/expert-judgment-clean-product-replacement-execplan.md",
                self.result["architecture_review"]["record"],
            )
        self.assertEqual(
            self.result["shipped_product_pressure_exceeded"],
            self.result["shipped_product_total"]
            > self.result["pressure"]["shipped_product"],
        )
        self.assertEqual(self.result["reviewed_with_tests_total"],
                         self.result["shipped_product_total"] + self.result["totals"]["tests"])
        by_path = {row["path"]: row["category"] for row in self.result["files"]}
        self.assertEqual("schema", by_path["product/review/migrations/0011_remove_consequencedecision_legal_consequence_action_target_and_more.py"])
        self.assertEqual("operational_code", by_path["pyproject.toml"])
        self.assertEqual("operational_code", by_path["product/review/views.py"])
        self.assertEqual("operational_code", by_path["product/templates/review/reveal.html"])
        self.assertEqual("support_code", by_path["tools/classify_loc.py"])
        self.assertEqual("tests", by_path["scenarios/adversarial/test_c3_product.py"])
        self.assertEqual("docs_data", by_path["product/contracts/w7b_public_journey.json"])
        self.assertEqual("docs_data", by_path["LICENSE"])
        self.assertEqual("docs_data", by_path["PRODUCT_DISCOVERY.md"])
        self.assertEqual("docs_data", by_path["ROUTE.md"])
        self.assertEqual("generated", by_path["uv.lock"])
        self.assertEqual(
            "operational_code",
            by_path["workbenches/comparable-state-v0/protocol.md"],
        )
        self.assertEqual(
            "operational_code",
            by_path["agents/planner/protocol.md"],
        )
        self.assertEqual("docs_data", by_path["AGENTS.md"])

    def test_third_party_environment_is_reported_but_not_called_handwritten(self) -> None:
        environment = self.result["third_party_environment"]
        self.assertIsInstance(environment["files"], int)
        self.assertIsInstance(environment["bytes"], int)
        self.assertGreaterEqual(environment["files"], 0)
        self.assertGreaterEqual(environment["bytes"], 0)
        self.assertFalse(environment["counted_as_handwritten"])
        self.assertTrue(
            all(
                row["physical_lines"] == 0
                for row in self.result["files"]
                if row["category"] == "generated"
            )
        )

    def test_classifier_rejects_symlinked_authority_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target.html"
            target.write_text("authority")
            link = Path(temporary) / "surface.html"
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                self.module.require_regular_surface(link)

    def test_clean_cutover_migration_preserves_append_only_trigger(self) -> None:
        path = ROOT / "product/review/migrations/0012_launchpad_langfuse_cutover.py"
        spec = importlib.util.spec_from_file_location("truthful_mode_migration", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        operations = module.Migration.operations
        self.assertEqual("RunSQL", type(operations[0]).__name__)
        self.assertIn("DROP TRIGGER research_case_append_only", operations[0].sql)
        self.assertEqual("RunPython", type(operations[1]).__name__)
        self.assertIn("CREATE TRIGGER research_case_append_only", operations[2].sql)

    def test_preassembled_cognition_proxy_suites_are_absent(self) -> None:
        development = ROOT / "scenarios" / "development"
        self.assertEqual(
            [],
            sorted(
                str(path.relative_to(ROOT))
                for path in development.rglob("*")
                if path.is_file()
            ),
        )
        proxy_names = {"artifact-first-baseline.json", "comparison-receipt.json"}
        self.assertEqual(
            [],
            sorted(
                str(path.relative_to(ROOT))
                for path in (ROOT / "scenarios").rglob("*.json")
                if path.name in proxy_names
            ),
        )

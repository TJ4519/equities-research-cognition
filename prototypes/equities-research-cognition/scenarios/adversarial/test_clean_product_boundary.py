from __future__ import annotations

import importlib.util
import json
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "tools" / "check_boundary.py"
SPEC = importlib.util.spec_from_file_location("clean_boundary", CHECKER_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class CleanProductBoundaryTests(unittest.TestCase):
    def test_repository_clean_runtime_has_no_legacy_reachability(self) -> None:
        self.assertEqual([], CHECKER.violations())
        self.assertIn(
            CHECKER.PACKAGE_ROOT / "workbenches",
            CHECKER.RUNTIME_SURFACES,
        )

    def test_import_dynamic_reference_and_facade_literals_fail_closed(self) -> None:
        cases = {
            "direct.py": "from rie.judgment import authority\n",
            "dynamic.py": "import importlib\nimportlib.import_module('rie.judgment')\n",
            "concat.py": "import importlib\nimportlib.import_module('rie' + '.' + 'judgment')\n",
            "dunder.py": "__import__('rie' + '.' + 'judgment')\n",
            "process.py": "import subprocess, sys\nsubprocess.run([sys.executable, '-m', 'rie' + '.' + 'judgment'])\n",
            "async_process.py": "import asyncio, sys\nasyncio.run(asyncio.create_subprocess_exec(sys.executable, '-m', 'rie' + '.' + 'judgment'))\n",
            "async_from.py": "from asyncio import create_subprocess_exec as run\nrun('python', '-m', 'rie' + '.' + 'judgment')\n",
            "multiprocessing.py": "import multiprocessing\nmultiprocessing.Process(target=print, args=('legacy',)).start()\n",
            "unknown.py": "import definitely_not_product_authority\n",
            "shell.py": "import os\nos.system('python -m ' + 'rie' + '.' + 'judgment')\n",
            "exec.py": "exec('import ' + 'rie' + '.' + 'judgment')\n",
            "builtins.py": "getattr(__builtins__, 'exec')('import ' + 'rie' + '.' + 'judgment')\n",
            "facade.py": "COMMAND = ['python', '-m', 'rie/judgment/observed_live']\n",
        }
        for filename, source in cases.items():
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)
                (path / filename).write_text(source, encoding="utf-8")
                self.assertTrue(CHECKER.violations(path))

    def test_explicitly_allowed_environment_read_remains_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "safe.py").write_text(
                "from os import environ\nSETTING = environ.get('SETTING', '')\n",
                encoding="utf-8",
            )
            self.assertEqual([], CHECKER.violations(path))

    def test_local_password_prompt_is_not_a_runtime_authority_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "local_password.py").write_text(
                "from getpass import getpass\nPASSWORD = getpass('Password: ')\n",
                encoding="utf-8",
            )
            self.assertEqual([], CHECKER.violations(path))

    def test_symlink_is_not_a_backdoor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "legacy_link").symlink_to(ROOT / "rie" / "judgment")
            self.assertTrue(CHECKER.violations(path))


class PublicJourneyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(
            (ROOT / "product" / "contracts" / "w7b_public_journey.json").read_text()
        )

    def test_contract_covers_the_complete_public_causal_chain(self) -> None:
        ids = [transition["id"] for transition in self.contract["transitions"]]
        self.assertEqual(
            [
                "authenticate_before_delivery",
                "deliver_decision_complete_blind_packet",
                "lock_human_first_pass",
                "reveal_exact_lineage",
                "author_diagnosis",
                "commit_three_independent_consequences",
                "reconstruct_truthfully_after_restart",
            ],
            ids,
        )

    def test_fixture_can_never_be_expert_or_live_runtime_evidence(self) -> None:
        for mode in ("legacy_fixture_import", "contract_fixture"):
            fixture = self.contract["subject_modes"][mode]
            self.assertFalse(fixture["may_count_as_live_runtime_evidence"])
            self.assertFalse(fixture["may_count_as_expert_evidence"])
        self.assertFalse(
            self.contract["subject_modes"]["native_observed_run"]["may_count_as_expert_evidence"]
        )
        self.assertFalse(
            self.contract["subject_modes"]["langfuse_observed_run"]["may_count_as_expert_evidence"]
        )

    def test_telemetry_is_not_product_authority(self) -> None:
        self.assertEqual(
            "langfuse_non_authoritative",
            self.contract["authority"]["runtime_correlation"],
        )
        self.assertEqual(
            "application_domain_records",
            self.contract["authority"]["product_facts"],
        )
        self.assertEqual("ntm_persistent_codex_rie", self.contract["authority"]["agent_runtime"])


class DependencyBoundaryTests(unittest.TestCase):
    def test_declared_runtime_set_is_small_and_exact(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual(
            [
                "Django==6.0.7",
                "psycopg[binary]==3.3.4",
            ],
            project["project"]["dependencies"],
        )
        self.assertFalse(project["tool"]["uv"]["package"])

    def test_langfuse_contract_selects_cloud_without_claiming_self_hosted_or_live_proof(self) -> None:
        contract = json.loads((ROOT / "product/contracts/langfuse_compatibility.json").read_text())
        self.assertEqual("MECHANICAL_REGRESSION_ONLY", contract["test_class"])
        self.assertEqual("cloud-v2", contract["selected_candidate"])
        self.assertEqual("local-schema-compatibility-only", contract["claim_ceiling"])
        self.assertEqual("closed-validator-only", contract["normalization_output"])
        self.assertFalse(contract["admission_allowed"])
        self.assertEqual(
            "OTEL_EXPORTER_OTLP_TRACES_HEADERS runtime environment; "
            "no credential or environment placeholder in frozen Codex config",
            contract["ingestion"]["credential_channel"],
        )
        self.assertIn(
            "exclude OTEL_EXPORTER_OTLP_TRACES_HEADERS",
            contract["ingestion"]["tool_subprocess_policy"],
        )
        self.assertEqual("blocked-until-exact-deployment-version-and-response-fixture",
                         contract["self-hosted-v1"]["availability"])
        self.assertFalse(contract["self-hosted-v1"]["may_reuse_cloud_mapping_without_proof"])
        self.assertIn("fields=core,basic,metadata,model,usage", contract["cloud-v2"]["required_query"])
        self.assertIn("filter=sessionId and matching startTime bounds", contract["cloud-v2"]["required_query"])
        self.assertNotIn("session_population", contract)

    def test_cloud_fixture_covers_multiple_traces_and_exhausts_its_cursor(self) -> None:
        contract = json.loads((ROOT / "product/contracts/langfuse_compatibility.json").read_text())
        fixture = json.loads((ROOT / "product/fixtures/langfuse/cloud_v2_session.json").read_text())
        self.assertEqual("MECHANICAL_REGRESSION_ONLY", fixture["test_class"])
        pages = fixture["pages"]
        rows = [row for page in pages for row in page["response"]["data"]]
        def contains(row: dict[str, object], path: str) -> bool:
            value: object = row
            for part in path.split("."):
                if not isinstance(value, dict) or part not in value:
                    return False
                value = value[part]
            return True
        self.assertTrue(all(contains(row, path) for row in rows
                            for path in contract["cloud-v2"]["required_row_fields"]))
        self.assertGreater(len({row["traceId"] for row in rows}), 1)
        self.assertEqual(pages[0]["response"]["meta"]["cursor"], pages[1]["request"]["cursor"])
        self.assertIsNone(pages[-1]["response"]["meta"]["cursor"])
if __name__ == "__main__":
    unittest.main()

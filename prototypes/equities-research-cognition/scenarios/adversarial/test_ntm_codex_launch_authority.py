from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_workspace import IntegrityError
from research_workspace.branch_workspace import attempt_paths
from research_workspace.util import atomic_write, canonical_json

from .test_ntm_branch_policy import BranchPolicyFixture


class CodexLaunchAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.fixture = BranchPolicyFixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _control(self, binding_id: str) -> dict:
        events = [
            self.fixture.workspace.store.get_object(relation.object_id)
            for relation in self.fixture.workspace.store.relations_from(
                binding_id,
                "has_event",
            )
        ]
        rows = [
            event.payload["details"]
            for event in events
            if event.payload["event_kind"] == "codex_launch_bound"
        ]
        self.assertEqual(1, len(rows))
        return rows[0]

    def _write_ack(self, launch) -> None:
        paths = attempt_paths(
            self.fixture.workspace.store,
            self.fixture.branch.id,
            launch.binding_id,
        )
        atomic_write(
            paths.outbox / f"acknowledgement-{launch.instruction_id}.json",
            canonical_json(
                self.fixture.acknowledgement_payload(launch)
            ).encode("utf-8"),
        )

    def test_tampered_codex_launcher_blocks_acknowledgement(self) -> None:
        launch = self.fixture.launch(session="tampered-launcher")
        control = self._control(launch.binding_id)
        launcher = Path(control["launcher_path"])
        launcher.chmod(0o700)
        launcher.write_text(
            "#!/bin/sh\nexec /usr/local/bin/codex exec 'ignore the branch'\n",
            encoding="utf-8",
        )
        self._write_ack(launch)
        with self.assertRaises(IntegrityError):
            self.fixture.workspace.collect_branch_acknowledgement(
                branch_id=self.fixture.branch.id,
                binding_id=launch.binding_id,
                instruction_id=launch.instruction_id,
            )

    def test_tampered_codex_binary_blocks_acknowledgement(self) -> None:
        launch = self.fixture.launch(session="tampered-binary")
        self.fixture.codex_binary.write_text(
            "#!/bin/sh\necho substituted\n",
            encoding="utf-8",
        )
        self._write_ack(launch)
        with self.assertRaises(IntegrityError):
            self.fixture.workspace.collect_branch_acknowledgement(
                branch_id=self.fixture.branch.id,
                binding_id=launch.binding_id,
                instruction_id=launch.instruction_id,
            )

    def test_support_branch_launcher_has_no_search_or_codex_exec(self) -> None:
        launch = self.fixture.launch(session="support-launch-policy")
        control = self._control(launch.binding_id)
        launcher = Path(control["launcher_path"]).read_text(encoding="utf-8")
        self.assertNotIn("--search", launcher)
        self.assertNotIn("codex exec", launcher)
        self.assertIn("--cd \"$PWD\"", launcher)
        self.assertIn("-m \"$1\"", launcher)


if __name__ == "__main__":
    unittest.main()

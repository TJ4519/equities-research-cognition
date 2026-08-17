from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timedelta, timezone
import json
import tomllib

from django.test import TestCase

from harness.langfuse.transport import (
    HttpResult,
    LangfuseRejected,
    build_codex_trace_arguments,
    campaign_launch_environment,
    connection_from_environment,
    readback_observations,
    readback_project_identity,
)


RUN_ID = "11111111-1111-4111-8111-111111111111"
WORK_ORDER_ID = "22222222-2222-4222-8222-222222222222"
AUTHORIZATION = "Basic " + b64encode(
    b"pk-lf-test-public:sk-lf-test-secret"
).decode("ascii")


class DirectLangfuseBoundaryTests(TestCase):
    def test_trace_exporter_override_is_executable_toml(self) -> None:
        arguments = build_codex_trace_arguments(
            base_url="https://cloud.langfuse.com",
            campaign_id=RUN_ID,
            role_id="provisional_judge",
            role_contract_digest="a" * 64,
            work_order_id=WORK_ORDER_ID,
            proposal_digest="b" * 64,
        )
        overrides = [
            arguments[index + 1]
            for index, argument in enumerate(arguments[:-1])
            if argument == "-c"
            and arguments[index + 1].startswith("otel.trace_exporter=")
        ]

        self.assertEqual(1, len(overrides))
        parsed = tomllib.loads(overrides[0])
        self.assertEqual(
            {
                "otlp-http": {
                    "endpoint": (
                        "https://cloud.langfuse.com/api/public/otel/v1/traces"
                    ),
                    "protocol": "binary",
                }
            },
            parsed["otel"]["trace_exporter"],
        )

    def test_codex_native_trace_config_leaves_runtime_auth_to_otlp_environment(
        self,
    ) -> None:
        arguments = build_codex_trace_arguments(
            base_url="https://cloud.langfuse.com",
            campaign_id=RUN_ID,
            role_id="provisional_judge",
            role_contract_digest="a" * 64,
            work_order_id=WORK_ORDER_ID,
            proposal_digest="b" * 64,
        )
        rendered = " ".join(arguments)
        self.assertIn("otel.trace_exporter", rendered)
        self.assertIn(
            "https://cloud.langfuse.com/api/public/otel/v1/traces", rendered
        )
        self.assertNotIn("Authorization", rendered)
        self.assertNotIn("${FLYWHEEL_LANGFUSE_AUTHORIZATION}", rendered)
        self.assertNotIn("headers=", rendered)
        self.assertIn("shell_environment_policy.exclude", rendered)
        self.assertIn("OTEL_EXPORTER_OTLP_TRACES_HEADERS", rendered)
        self.assertIn("allow_login_shell=false", rendered)
        self.assertIn("flywheel.run.id", rendered)
        self.assertIn("flywheel.work.order.id", rendered)
        self.assertIn(WORK_ORDER_ID, rendered)
        self.assertIn("flywheel.work.order.proposal_digest", rendered)
        self.assertIn("flywheel.role.instance", rendered)
        self.assertIn("langfuse.session.id", rendered)
        self.assertNotIn(AUTHORIZATION, rendered)
        self.assertNotIn("127.0.0.1", rendered)
        self.assertNotIn("relay", rendered.lower())

    def test_only_the_project_credential_crosses_the_ntm_launch_boundary(
        self,
    ) -> None:
        environment = campaign_launch_environment(
            {
                "HOME": "/tmp/director",
                "PATH": "/usr/bin",
                "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
                "FLYWHEEL_DB_PASSWORD": "must-not-cross",
                "OPENAI_API_KEY": "must-not-cross",
                "UNRELATED": "must-not-cross",
            }
        )
        self.assertEqual(
            (
                f"Authorization={AUTHORIZATION},"
                "x-langfuse-ingestion-version=4"
            ),
            environment["OTEL_EXPORTER_OTLP_TRACES_HEADERS"],
        )
        self.assertNotIn("FLYWHEEL_LANGFUSE_AUTHORIZATION", environment)
        self.assertEqual("/tmp/director", environment["HOME"])
        self.assertNotIn("FLYWHEEL_DB_PASSWORD", environment)
        self.assertNotIn("OPENAI_API_KEY", environment)
        self.assertNotIn("UNRELATED", environment)
        with self.assertRaisesRegex(LangfuseRejected, "runtime authorization"):
            campaign_launch_environment({"HOME": "/tmp/director"})

    def test_standing_project_connection_fails_closed_without_exact_config(
        self,
    ) -> None:
        connection = connection_from_environment(
            {
                "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
                "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": (
                    "https://cloud.langfuse.com"
                ),
                "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": "project-1",
            }
        )
        self.assertEqual("project-1", connection.project_id)
        self.assertNotIn(AUTHORIZATION, repr(connection))
        for mutation in (
            {"FLYWHEEL_LANGFUSE_AUTHORIZATION": "Bearer wrong"},
            {
                "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
                "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": "https://example.com",
                "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": "project-1",
            },
            {
                "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
                "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": (
                    "https://cloud.langfuse.com"
                ),
                "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": "project with spaces",
            },
        ):
            with self.subTest(mutation=mutation), self.assertRaises(
                LangfuseRejected
            ):
                connection_from_environment(mutation)

    def test_readback_exhausts_supported_provider_cursors(self) -> None:
        connection = connection_from_environment({
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
            "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": "https://cloud.langfuse.com",
            "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": "project-1",
        })
        calls = []

        def requester(url, **kwargs):
            calls.append((url, kwargs))
            page = (
                {"data": [{"id": "one"}], "meta": {"cursor": "next"}}
                if len(calls) == 1
                else {"data": [{"id": "two"}], "meta": {"cursor": None}}
            )
            return HttpResult(200, {}, json.dumps(page).encode())

        start = datetime(2026, 7, 16, tzinfo=timezone.utc)
        rows = readback_observations(
            connection=connection,
            session_id=RUN_ID,
            from_start_time=start,
            to_start_time=start + timedelta(days=1),
            requester=requester,
        )

        self.assertEqual(["one", "two"], [row["id"] for row in rows])
        self.assertEqual(2, len(calls))
        self.assertIn("cursor=next", calls[1][0])
        self.assertEqual(AUTHORIZATION, calls[0][1]["headers"]["Authorization"])

    def test_project_readback_binds_the_key_to_the_configured_project(
        self,
    ) -> None:
        connection = connection_from_environment({
            "FLYWHEEL_LANGFUSE_AUTHORIZATION": AUTHORIZATION,
            "FLYWHEEL_LANGFUSE_TARGET_BASE_URL": "https://cloud.langfuse.com",
            "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID": "project-1",
        })
        calls = []

        def requester(url, **kwargs):
            calls.append((url, kwargs))
            return HttpResult(
                200,
                {},
                json.dumps({"data": [{"id": "project-1"}]}).encode(),
            )

        identity = readback_project_identity(
            connection=connection, requester=requester
        )

        self.assertEqual("project-1", identity["id"])
        self.assertEqual(
            "https://cloud.langfuse.com/api/public/projects", calls[0][0]
        )
        self.assertEqual(AUTHORIZATION, calls[0][1]["headers"]["Authorization"])
        for mutation in (
            {"data": []},
            {"data": [{"id": "other-project"}]},
            {"data": [{"id": "project-1"}, {"id": "other-project"}]},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(
                LangfuseRejected
            ):
                readback_project_identity(
                    connection=connection,
                    requester=lambda *args, **kwargs: HttpResult(
                        200, {}, json.dumps(mutation).encode()
                    ),
                )

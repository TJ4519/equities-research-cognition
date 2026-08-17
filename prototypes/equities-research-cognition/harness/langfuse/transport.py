"""Small direct boundary for native Codex traces and Langfuse readback."""
from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID


class LangfuseRejected(Exception):
    pass


@dataclass(frozen=True)
class LangfuseConnection:
    base_url: str
    project_id: str
    authorization: str = field(repr=False)


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: Mapping[str, str]
    body: bytes


Requester = Callable[..., HttpResult]
_HOSTS = {
    "cloud.langfuse.com",
    "us.cloud.langfuse.com",
    "jp.cloud.langfuse.com",
    "hipaa.cloud.langfuse.com",
}
_AUTH_ENV = "FLYWHEEL_LANGFUSE_AUTHORIZATION"
_OTEL_ENV = "OTEL_EXPORTER_OTLP_TRACES_HEADERS"
_CHILD_KEYS = (
    "CODEX_HOME", "COLORTERM", "HOME", "LOGNAME", "PATH", "SHELL", "TERM",
    "TMPDIR", "USER",
)
_FIELDS = "core,basic,metadata,model,usage"


def _require(condition: object, message: str) -> None:
    if not condition:
        raise LangfuseRejected(message)


def _base_url(value: object) -> str:
    _require(isinstance(value, str), "Langfuse base URL is invalid")
    parsed = urlsplit(value)
    _require(
        parsed.scheme == "https"
        and parsed.hostname in _HOSTS
        and parsed.port is None
        and parsed.path in ("", "/")
        and not any((
            parsed.username, parsed.password, parsed.query, parsed.fragment
        )),
        "Langfuse Cloud base URL is outside the supported boundary",
    )
    return f"https://{parsed.hostname}"


def _authorization(value: object) -> str:
    _require(
        isinstance(value, str)
        and value.startswith("Basic ")
        and 16 < len(value) <= 1024
        and not any(character in value for character in "\r\n\x00"),
        "Langfuse runtime authorization is absent or invalid",
    )
    try:
        public, secret = b64decode(value[6:], validate=True).split(b":", 1)
    except (TypeError, ValueError) as exc:
        raise LangfuseRejected(
            "Langfuse runtime authorization is absent or invalid"
        ) from exc
    _require(
        public.startswith(b"pk-lf-")
        and secret.startswith(b"sk-lf-")
        and b" " not in public + secret,
        "Langfuse runtime authorization is absent or invalid",
    )
    return value


def connection_from_environment(source: Mapping[str, str]) -> LangfuseConnection:
    project = source.get("FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID", "")
    _require(
        isinstance(project, str)
        and 0 < len(project) <= 160
        and not any(character.isspace() for character in project),
        "Langfuse target project is absent or invalid",
    )
    return LangfuseConnection(
        _base_url(source.get("FLYWHEEL_LANGFUSE_TARGET_BASE_URL", "")),
        project,
        _authorization(source.get(_AUTH_ENV)),
    )


def _identity(campaign_id: str, role_id: str, digest: str) -> None:
    try:
        canonical = str(UUID(campaign_id))
    except (TypeError, ValueError) as exc:
        raise LangfuseRejected("campaign telemetry identity is invalid") from exc
    try:
        canonical_role = str(UUID(role_id))
    except (TypeError, ValueError):
        canonical_role = None
    named_role = (
        isinstance(role_id, str)
        and bool(role_id)
        and role_id[0].isalpha()
        and role_id.replace("_", "").replace("-", "").isalnum()
    )
    _require(
        canonical == campaign_id
        and (canonical_role == role_id or named_role)
        and len(digest) == 64
        and all(character in "0123456789abcdef" for character in digest),
        "campaign telemetry preregistration is invalid",
    )


def build_codex_trace_arguments(
    *,
    base_url: str,
    campaign_id: str,
    work_order_id: str,
    proposal_digest: str,
    role_id: str,
    role_contract_digest: str,
) -> tuple[str, ...]:
    _identity(campaign_id, role_id, role_contract_digest)
    try:
        canonical_work_order = str(UUID(work_order_id))
    except (TypeError, ValueError) as exc:
        raise LangfuseRejected("work-order telemetry identity is invalid") from exc
    _require(
        canonical_work_order == work_order_id
        and len(proposal_digest) == 64
        and all(character in "0123456789abcdef" for character in proposal_digest),
        "work-order telemetry identity is invalid",
    )
    endpoint = f"{_base_url(base_url)}/api/public/otel/v1/traces"
    attributes = {
        "flywheel.run.id": campaign_id,
        "flywheel.work.order.id": work_order_id,
        "flywheel.work.order.proposal_digest": proposal_digest,
        "flywheel.role.instance": role_id,
        "flywheel.role.contract": role_contract_digest,
        "langfuse.session.id": campaign_id,
        "langfuse.observation.metadata.flywheel_run_id": campaign_id,
        "langfuse.observation.metadata.flywheel_work_order_id": work_order_id,
        "langfuse.observation.metadata.flywheel_work_order_proposal_digest": (
            proposal_digest
        ),
        "langfuse.observation.metadata.flywheel_role_instance": role_id,
        "langfuse.observation.metadata.flywheel_role_contract": role_contract_digest,
    }
    rendered = ",".join(
        f"{json.dumps(key)}={json.dumps(value)}"
        for key, value in attributes.items()
    )
    return (
        "-c", "allow_login_shell=false",
        "-c", (
            'shell_environment_policy.exclude=['
            '"OTEL_EXPORTER_OTLP_TRACES_HEADERS",'
            '"FLYWHEEL_LANGFUSE_AUTHORIZATION"]'
        ),
        "-c", 'otel.exporter="none"',
        "-c", (
            'otel.trace_exporter={"otlp-http"={'
            f'endpoint={json.dumps(endpoint)},protocol="binary"'
            "}}"
        ),
        "-c", f"otel.span_attributes={{{rendered}}}",
    )


def campaign_launch_environment(source: Mapping[str, str]) -> dict[str, str]:
    environment = {
        key: source[key]
        for key in _CHILD_KEYS
        if isinstance(source.get(key), str) and source[key]
    }
    _require(
        all(not any(character in value for character in "\r\n\x00")
            for value in environment.values()),
        "campaign child environment is invalid",
    )
    environment.update({
        "LANG": "C",
        "LC_ALL": "C",
        _OTEL_ENV: (
            f"Authorization={_authorization(source.get(_AUTH_ENV))},"
            "x-langfuse-ingestion-version=4"
        ),
    })
    return environment


def sanitized_control_environment(source: Mapping[str, str]) -> dict[str, str]:
    def sensitive(key: str) -> bool:
        upper = key.upper()
        return (
            upper.startswith(("FLYWHEEL_", "LANGFUSE_", "OTEL_"))
            or upper in {"DATABASE_URL", "PGPASSWORD", "DJANGO_SETTINGS_MODULE"}
            or upper.endswith((
                "_SECRET", "_TOKEN", "_PASSWORD", "_API_KEY", "_PRIVATE_KEY",
                "_ACCESS_KEY", "_CREDENTIAL", "_CREDENTIALS", "_AUTHORIZATION",
                "_PROXY",
            ))
        )
    return {
        key: value for key, value in source.items()
        if isinstance(key, str) and isinstance(value, str) and not sensitive(key)
    }


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, url):
        return None


_OPENER = build_opener(_NoRedirects)


def _request(
    url: str, *, method: str, headers: Mapping[str, str], body: bytes | None
) -> HttpResult:
    request = Request(url, data=body, headers=dict(headers), method=method)
    try:
        with _OPENER.open(request, timeout=30) as response:
            return HttpResult(
                response.status, dict(response.headers.items()),
                response.read(2 * 1024 * 1024 + 1),
            )
    except HTTPError as exc:
        with exc:
            return HttpResult(
                exc.code, dict(exc.headers.items()) if exc.headers else {},
                exc.read(64 * 1024 + 1),
            )
    except (TimeoutError, URLError, OSError) as exc:
        raise LangfuseRejected("Langfuse request failed") from exc


def _iso(value: datetime) -> str:
    _require(value.tzinfo is not None, "Langfuse query time lacks a timezone")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def readback_project_identity(
    *,
    connection: LangfuseConnection,
    requester: Requester = _request,
) -> dict[str, object]:
    """Bind the scoped key to the exact provider-issued project identity."""
    result = requester(
        f"{connection.base_url}/api/public/projects",
        method="GET",
        headers={
            "Authorization": connection.authorization,
            "Accept": "application/json",
        },
        body=None,
    )
    _require(
        result.status == 200,
        f"Langfuse project readback returned HTTP {result.status}",
    )
    _require(
        len(result.body) <= 256 * 1024,
        "Langfuse project readback is too large",
    )
    try:
        payload = json.loads(result.body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LangfuseRejected(
            "Langfuse project readback is not JSON"
        ) from exc
    rows = payload.get("data") if isinstance(payload, dict) else None
    _require(
        isinstance(rows, list) and len(rows) == 1,
        "Langfuse project readback population is not exact",
    )
    project = rows[0]
    _require(
        isinstance(project, dict)
        and isinstance(project.get("id"), str)
        and project["id"] == connection.project_id,
        "Langfuse key is not bound to the configured project",
    )
    return project


def readback_observations(
    *,
    connection: LangfuseConnection,
    session_id: str,
    from_start_time: datetime,
    to_start_time: datetime,
    requester: Requester = _request,
    page_limit: int = 250,
    max_pages: int = 20,
) -> list[dict[str, object]]:
    _identity(session_id, "readback", "0" * 64)
    _require(
        from_start_time < to_start_time
        and 1 <= page_limit <= 1000
        and 1 <= max_pages <= 100,
        "Langfuse readback bounds are invalid",
    )
    start, end, cursor = _iso(from_start_time), _iso(to_start_time), None
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    filters = json.dumps([
        {"column": "sessionId", "operator": "=", "type": "string",
         "value": session_id},
        {"column": "startTime", "operator": ">=", "type": "datetime",
         "value": start},
        {"column": "startTime", "operator": "<", "type": "datetime",
         "value": end},
    ], separators=(",", ":"))
    for _ in range(max_pages):
        query = {
            "fields": _FIELDS, "filter": filters, "limit": str(page_limit),
            "fromStartTime": start, "toStartTime": end,
        }
        if cursor:
            query["cursor"] = cursor
        result = requester(
            f"{connection.base_url}/api/public/v2/observations?{urlencode(query)}",
            method="GET",
            headers={"Authorization": connection.authorization,
                     "Accept": "application/json"},
            body=None,
        )
        _require(result.status == 200, f"Langfuse readback returned HTTP {result.status}")
        _require(len(result.body) <= 2 * 1024 * 1024, "Langfuse page is too large")
        try:
            page = json.loads(result.body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LangfuseRejected("Langfuse readback is not JSON") from exc
        _require(
            isinstance(page, dict)
            and isinstance(page.get("data"), list)
            and len(page["data"]) <= page_limit
            and isinstance(page.get("meta"), dict),
            "Langfuse readback page shape is invalid",
        )
        rows.extend(page["data"])
        cursor = page["meta"].get("cursor")
        _require(
            cursor is None or isinstance(cursor, str) and cursor,
            "Langfuse cursor is invalid",
        )
        if cursor is None:
            return rows
        _require(cursor not in seen, "Langfuse cursor repeated")
        seen.add(cursor)
    raise LangfuseRejected("Langfuse readback exceeded its page bound")

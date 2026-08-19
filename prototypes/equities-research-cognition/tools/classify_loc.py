#!/usr/bin/env python3
"""Classify every cognition-package surface and enforce architecture pressure."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parents[1]
OPERATIONAL_CODE_REVIEW_THRESHOLD = 4000
SHIPPED_PRODUCT_PRESSURE = 5000
ARCHITECTURE_REVIEW_RECORD = (
    WORKSPACE_ROOT
    / "docs"
    / "plans"
    / "expert-judgment-clean-product-replacement-execplan.md"
)
ARCHITECTURE_REVIEW_MARKERS = (
    "2026-07-20",
    "role-kind/role-instance/obligation separation",
    "baseline/intervention comparison",
)


def category(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if (
        relative in {".env", "uv.lock"}
        or relative.startswith("var/")
        or ".venv" in path.parts
        or "__pycache__" in path.parts
        or path.suffix == ".pyc"
    ):
        return "generated"
    if relative.startswith("product/") and "/migrations/" in relative:
        return "schema"
    if relative.startswith("scenarios/"):
        return "tests"
    if (
        relative
        in {
            "AGENTS.md",
            "DEPENDENCIES.md",
            "LICENSE",
            "PHILOSOPHY.md",
            "PRODUCT_DISCOVERY.md",
            "README.md",
            "ROUTE.md",
        }
        or relative.startswith("evidence/")
        or relative.startswith("prompts/")
        or relative.startswith("skills/")
        or relative.startswith("product/contracts/")
        or relative.startswith("product/fixtures/")
    ):
        return "docs_data"
    if relative == ".gitignore" or relative.startswith("tools/"):
        return "support_code"
    if (
        relative == "manage.py"
        or relative == "pyproject.toml"
        or relative.startswith("product/")
        or relative.startswith("harness/")
        or relative.startswith("research_workspace/")
        or relative.startswith("agents/")
        or relative.startswith("workbenches/")
    ):
        return "operational_code"
    raise ValueError(f"unclassified cognition-package surface: {relative}")


def text_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def require_regular_surface(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"symlink cannot carry a package surface: {path}")


def classify() -> dict[str, object]:
    paths = [path for path in ROOT.rglob("*") if path.is_file()]
    rows = []
    totals: dict[str, int] = defaultdict(int)
    third_party_files = third_party_bytes = 0
    for path in sorted(set(paths)):
        if ROOT / ".venv" in path.parents:
            third_party_files += 1
            third_party_bytes += path.stat().st_size
            continue
        require_regular_surface(path)
        kind = category(path)
        lines = 0 if kind == "generated" else text_lines(path)
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "category": kind,
                "physical_lines": lines,
            }
        )
        totals[kind] += lines
    shipped = sum(
        totals[name]
        for name in ("operational_code", "schema", "support_code", "docs_data")
    )
    reviewed = shipped + totals["tests"]
    architecture_review_required = (
        totals["operational_code"] > OPERATIONAL_CODE_REVIEW_THRESHOLD
    )
    review_text = ARCHITECTURE_REVIEW_RECORD.read_text(encoding="utf-8")
    architecture_review_recorded = all(
        marker in review_text for marker in ARCHITECTURE_REVIEW_MARKERS
    )
    return {
        "schema_version": "equities-cognition-package-loc/v1",
        "pressure": {
            "operational_code_architecture_review": (
                OPERATIONAL_CODE_REVIEW_THRESHOLD
            ),
            "shipped_product": SHIPPED_PRODUCT_PRESSURE,
        },
        "totals": dict(sorted(totals.items())),
        "shipped_product_total": shipped,
        "shipped_product_pressure_exceeded": shipped > SHIPPED_PRODUCT_PRESSURE,
        "architecture_review_required": architecture_review_required,
        "architecture_review": {
            "record": ARCHITECTURE_REVIEW_RECORD.relative_to(
                WORKSPACE_ROOT
            ).as_posix(),
            "recorded": architecture_review_recorded,
        },
        "reviewed_with_tests_total": reviewed,
        "runtime_and_schema_total": (
            totals["operational_code"] + totals["schema"]
        ),
        "third_party_environment": {
            "files": third_party_files,
            "bytes": third_party_bytes,
            "counted_as_handwritten": False,
        },
        "files": rows,
    }


def main() -> int:
    try:
        result = classify()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"cognition package LOC classification: FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

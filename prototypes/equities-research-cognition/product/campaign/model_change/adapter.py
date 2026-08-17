from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path
import re
from shutil import ReadError, make_archive, rmtree, unpack_archive
from typing import Mapping
import uuid

from django.conf import settings

from harness.ntm.adapter import CalculationProcessAdapter
from product.campaign.models import canonical_digest


ADAPTER_VERSION = "bounded-ooxml-adapter/v0"
PROFILE_ID = "single-numeric-target-two-arithmetic-dependents/v0"
MAX_PACKAGE_MEMBERS = 512
MAX_UNCOMPRESSED_BYTES = 32 * 1024 * 1024
VOLATILE_FUNCTIONS = re.compile(
    r"\b(?:NOW|TODAY|RAND|RANDBETWEEN|OFFSET|INDIRECT|CELL|INFO)\s*\(", re.I
)


class AdapterRejected(Exception):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True)
class Profile:
    profile_id: str
    target_name: str
    target_reference: str
    target_unit: str
    expected_original: Decimal
    allowed_operation: str
    dependents: tuple[tuple[str, str], tuple[str, str]]


def case_a_profile() -> dict[str, object]:
    return {
        "profile_id": PROFILE_ID,
        "target_name": "FY25_REVENUE_USDM",
        "target_reference": "Model!$B$5",
        "target_unit": "USDm",
        "expected_original": "36900",
        "allowed_operation": "set_numeric_value",
        "dependents": [
            {"ref": "Model!B6", "formula": "B5/B4-1"},
            {"ref": "Valuation!B5", "formula": "B4/Model!B5"},
        ],
    }


def _profile(value: Mapping[str, object]) -> Profile:
    required = {
        "profile_id",
        "target_name",
        "target_reference",
        "target_unit",
        "expected_original",
        "allowed_operation",
        "dependents",
    }
    dependents = value.get("dependents") if isinstance(value, Mapping) else None
    if (
        set(value) != required
        or value.get("profile_id") != PROFILE_ID
        or value.get("allowed_operation") != "set_numeric_value"
        or not all(
            isinstance(value.get(name), str) and value[name]
            for name in ("target_name", "target_reference", "target_unit")
        )
        or not isinstance(dependents, list)
        or len(dependents) != 2
        or any(
            not isinstance(item, dict)
            or set(item) != {"ref", "formula"}
            or not isinstance(item["ref"], str)
            or not isinstance(item["formula"], str)
            or not item["ref"]
            or not item["formula"]
            for item in dependents
        )
        or len({item["ref"] for item in dependents}) != 2
    ):
        raise AdapterRejected("UNSUPPORTED_PROFILE", "adapter profile is unsupported")
    try:
        expected = Decimal(str(value["expected_original"]))
    except InvalidOperation as exc:
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "adapter target value is not numeric"
        ) from exc
    return Profile(
        profile_id=str(value["profile_id"]),
        target_name=str(value["target_name"]),
        target_reference=str(value["target_reference"]),
        target_unit=str(value["target_unit"]),
        expected_original=expected,
        allowed_operation=str(value["allowed_operation"]),
        dependents=tuple(
            (str(item["ref"]), str(item["formula"])) for item in dependents
        ),
    )


def _temporary_root() -> Path:
    parent = Path(settings.CAMPAIGN_ROOT).expanduser().resolve().parent
    base = parent / ".model-change-v0-temporary"
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = base / uuid.uuid4().hex
    temporary.mkdir(mode=0o700)
    return temporary


def _read_package(content: bytes) -> dict[str, bytes]:
    temporary = _temporary_root()
    try:
        source = temporary / "source.xlsx"
        extracted = temporary / "extracted"
        source.write_bytes(content)
        extracted.mkdir()
        unpack_archive(source, extracted, "zip")
        paths = sorted(item for item in extracted.rglob("*") if item.is_file())
        if (
            not paths
            or len(paths) > MAX_PACKAGE_MEMBERS
            or any(item.is_symlink() for item in extracted.rglob("*"))
            or sum(item.stat().st_size for item in paths) > MAX_UNCOMPRESSED_BYTES
        ):
            raise AdapterRejected(
                "UNSUPPORTED_PROFILE", "workbook package exceeds the bounded profile"
            )
        return {
            item.relative_to(extracted).as_posix(): item.read_bytes()
            for item in paths
        }
    except (ReadError, KeyError, OSError, ValueError) as exc:
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "workbook is not a supported OOXML package"
        ) from exc
    finally:
        rmtree(temporary)


def _write_package(members: dict[str, bytes]) -> bytes:
    temporary = _temporary_root()
    try:
        root = temporary / "package"
        root.mkdir()
        for name, content in sorted(members.items()):
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise AdapterRejected(
                    "UNSUPPORTED_PROFILE", "workbook member path is unsafe"
                )
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        archive = Path(make_archive(str(temporary / "candidate"), "zip", root))
        return archive.read_bytes()
    finally:
        rmtree(temporary)


def _text(members: dict[str, bytes], name: str) -> str:
    try:
        return members[name].decode("utf-8")
    except (KeyError, UnicodeDecodeError) as exc:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "workbook XML is unavailable") from exc


def _attributes(fragment: str) -> dict[str, str]:
    return dict(re.findall(r'([A-Za-z_:][A-Za-z0-9_:.-]*)="([^"]*)"', fragment))


def _workbook_map(members: dict[str, bytes]) -> tuple[str, dict[str, str]]:
    workbook = _text(members, "xl/workbook.xml")
    relationships = _text(members, "xl/_rels/workbook.xml.rels")
    targets: dict[str, str] = {}
    for fragment in re.findall(r"<(?:[A-Za-z0-9_]+:)?Relationship\b([^>]*)/?>", relationships):
        attributes = _attributes(fragment)
        target = attributes.get("Target", "").lstrip("/")
        if target and not target.startswith("xl/"):
            target = f"xl/{target}"
        if attributes.get("Id") and target:
            targets[attributes["Id"]] = target
    sheets: dict[str, str] = {}
    for fragment in re.findall(r"<(?:[A-Za-z0-9_]+:)?sheet\b([^>]*)/?>", workbook):
        attributes = _attributes(fragment)
        relation = attributes.get("r:id")
        if attributes.get("name") and relation in targets:
            sheets[attributes["name"]] = targets[relation]
    if not sheets:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "workbook sheets are unavailable")
    return workbook, sheets


def _defined_target(
    members: dict[str, bytes], profile: Profile
) -> tuple[str, str, str]:
    workbook, sheets = _workbook_map(members)
    matches = [
        body
        for fragment, body in re.findall(
            r"<(?:[A-Za-z0-9_]+:)?definedName\b([^>]*)>([^<]+)</(?:[A-Za-z0-9_]+:)?definedName>",
            workbook,
        )
        if _attributes(fragment).get("name") == profile.target_name
    ]
    if len(matches) != 1:
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "workbook lacks one exact numeric target"
        )
    reference = matches[0]
    match = re.fullmatch(r"'?([^']+)'?!\$([A-Z]+)\$(\d+)", reference)
    if match is None:
        match = re.fullmatch(r"([^!]+)!\$([A-Z]+)\$(\d+)", reference)
    if (
        match is None
        or reference != profile.target_reference
        or match.group(1) not in sheets
    ):
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "workbook target is outside the accepted profile"
        )
    return reference, sheets[match.group(1)], f"{match.group(2)}{match.group(3)}"


def _formula_dependencies(sheet_name: str, formula: str) -> tuple[str, ...]:
    tokens = re.compile(
        r"(?:(?:'([^']+)'|([A-Za-z0-9_]+))!)?(\$?[A-Z]+\$?\d+)"
    )
    return tuple(
        dict.fromkeys(
            f"{quoted or plain or sheet_name}!{address.replace('$', '')}"
            for quoted, plain, address in tokens.findall(formula)
        )
    )


def _cells(members: dict[str, bytes]) -> dict[str, dict[str, object]]:
    _, sheets = _workbook_map(members)
    result: dict[str, dict[str, object]] = {}
    for sheet_name, part in sheets.items():
        worksheet = _text(members, part)
        for match in re.finditer(
            r"<(?:[A-Za-z0-9_]+:)?c\b([^>]*)>(.*?)</(?:[A-Za-z0-9_]+:)?c>",
            worksheet,
            re.S,
        ):
            attributes = _attributes(match.group(1))
            if "r" not in attributes:
                continue
            body = match.group(2)
            formula_match = re.search(
                r"<(?:[A-Za-z0-9_]+:)?f\b[^>]*>(.*?)</(?:[A-Za-z0-9_]+:)?f>",
                body,
                re.S,
            )
            value_match = re.search(
                r"<(?:[A-Za-z0-9_]+:)?v\b[^>]*>(.*?)</(?:[A-Za-z0-9_]+:)?v>",
                body,
                re.S,
            )
            formula = formula_match.group(1) if formula_match else None
            value = value_match.group(1) if value_match else None
            address = f"{sheet_name}!{attributes['r']}"
            result[address] = {
                "formula": formula,
                "value": value,
                "type": attributes.get("t"),
                "style": int(attributes.get("s", "0")),
                "dependencies": (
                    list(_formula_dependencies(sheet_name, formula))
                    if formula
                    else []
                ),
            }
    return result


def _reject_unsupported(members: dict[str, bytes], cells: dict[str, dict[str, object]]) -> None:
    names = set(members)
    xml = [content for name, content in members.items() if name.endswith(".xml")]
    protected = any(
        re.search(
            rb"<(?:[A-Za-z0-9_]+:)?(?:sheetProtection|workbookProtection)\b[^>]*=[^>]*>",
            content,
        )
        for content in xml
    )
    if (
        any(
            name.endswith("vbaProject.bin")
            or name.startswith("xl/externalLinks/")
            or name.startswith("xl/connections")
            for name in names
        )
        or protected
        or any(
            b"<dataTable" in content
            for content in xml
        )
        or b'iterate="true"' in members.get("xl/workbook.xml", b"")
        or any(
            VOLATILE_FUNCTIONS.search(str(cell["formula"]))
            for cell in cells.values()
            if cell["formula"]
        )
    ):
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "workbook contains a feature outside the profile"
        )


def inspect(
    workbook_bytes: bytes,
    profile: Mapping[str, object],
    *,
    require_original_target: bool = True,
) -> dict[str, object]:
    selected = _profile(profile)
    members = _read_package(workbook_bytes)
    reference, _, address = _defined_target(members, selected)
    cells = _cells(members)
    _reject_unsupported(members, cells)
    target_ref = f"{reference.split('!', 1)[0].strip(chr(39))}!{address}"
    target = cells.get(target_ref)
    if target is None or target["formula"] is not None:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "target is not one numeric input")
    try:
        target_value = Decimal(str(target["value"]))
    except InvalidOperation as exc:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "target is not numeric") from exc
    if require_original_target and target_value != selected.expected_original:
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "target value does not match the bounded parent"
        )
    formula_bindings: dict[str, str] = {}
    for dependent_ref, expected_formula in selected.dependents:
        cell = cells.get(dependent_ref)
        if (
            cell is None
            or cell["formula"] != expected_formula
            or target_ref not in cell["dependencies"]
        ):
            raise AdapterRejected(
                "UNSUPPORTED_PROFILE", "declared dependency closure does not match"
            )
        formula_bindings[dependent_ref] = expected_formula
    referencing_target = {
        ref
        for ref, cell in cells.items()
        if cell["formula"] and target_ref in cell["dependencies"]
    }
    if referencing_target != set(formula_bindings):
        raise AdapterRejected(
            "UNSUPPORTED_PROFILE", "target has undeclared formula dependents"
        )
    formula_errors = sorted(
        ref
        for ref, cell in cells.items()
        if cell["type"] == "e"
        or isinstance(cell["value"], str)
        and cell["value"].startswith("#")
    )
    facts = {
        "adapter_version": ADAPTER_VERSION,
        "adapter_profile": selected.profile_id,
        "target_ref": selected.target_name,
        "target_address": target_ref,
        "target_value": str(target_value),
        "target_unit": selected.target_unit,
        "allowed_operation": selected.allowed_operation,
        "dependency_closure": [item[0] for item in selected.dependents],
        "formula_bindings": formula_bindings,
        "formula_errors": formula_errors,
        "warnings": [],
        "package_members": sorted(members),
        "workbook_sha256": sha256(workbook_bytes).hexdigest(),
    }
    facts["inspection_digest"] = canonical_digest(facts)
    return facts


def _invalidate_formula_caches(members: dict[str, bytes]) -> None:
    for name in sorted(
        item
        for item in members
        if item.startswith("xl/worksheets/") and item.endswith(".xml")
    ):
        worksheet = _text(members, name)

        def clear_cache(match: re.Match[str]) -> str:
            opening, body, closing = match.groups()
            if re.search(r"<(?:[A-Za-z0-9_]+:)?f\b", body) is None:
                return match.group(0)
            cleared, count = re.subn(
                r"<(?:[A-Za-z0-9_]+:)?v\b[^>]*(?:/>|>.*?</(?:[A-Za-z0-9_]+:)?v>)",
                "<v/>",
                body,
                flags=re.S,
            )
            if count == 0:
                cleared += "<v/>"
            return opening + cleared + closing

        worksheet = re.sub(
            r"(<(?:[A-Za-z0-9_]+:)?c\b[^>]*>)(.*?)(</(?:[A-Za-z0-9_]+:)?c>)",
            clear_cache,
            worksheet,
            flags=re.S,
        )
        members[name] = worksheet.encode()
    workbook = _text(members, "xl/workbook.xml")
    calculation = '<calcPr calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>'
    workbook, count = re.subn(
        r"<(?:[A-Za-z0-9_]+:)?calcPr\b[^>]*/>", calculation, workbook, count=1
    )
    if count == 0:
        workbook = re.sub(
            r"</(?:[A-Za-z0-9_]+:)?workbook>",
            calculation + "</workbook>",
            workbook,
            count=1,
        )
    members["xl/workbook.xml"] = workbook.encode()


def apply(
    parent_bytes: bytes,
    admitted_operations: list[dict[str, object]],
    expected_manifest_digest: str,
    profile: Mapping[str, object],
    *,
    expected_inspection_digest: str,
) -> tuple[bytes, dict[str, object]]:
    selected = _profile(profile)
    if (
        len(expected_manifest_digest) != 64
        or len(expected_inspection_digest) != 64
        or len(admitted_operations) != 1
    ):
        raise AdapterRejected("UNSUPPORTED_PROFILE", "operation population is unsupported")
    operation = admitted_operations[0]
    if set(operation) != {"kind", "target_ref", "value", "unit"}:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "operation shape is unsupported")
    if operation.get("kind") != selected.allowed_operation:
        reason = (
            "UNSUPPORTED_STRUCTURAL_OPERATION"
            if operation.get("kind") in {"insert_row", "add_structure", "set_formula"}
            else "UNSUPPORTED_PROFILE"
        )
        raise AdapterRejected(reason, "operation is outside the bounded profile")
    if (
        operation.get("target_ref") != selected.target_name
        or operation.get("unit") != selected.target_unit
    ):
        raise AdapterRejected("UNSUPPORTED_PROFILE", "operation target or unit differs")
    before = inspect(parent_bytes, profile)
    if before["inspection_digest"] != expected_inspection_digest:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "parent inspection changed")
    try:
        value = Decimal(str(operation["value"]))
    except InvalidOperation as exc:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "operation value is not numeric") from exc
    members = _read_package(parent_bytes)
    _, sheet_part, address = _defined_target(members, selected)
    worksheet = _text(members, sheet_part)
    pattern = re.compile(
        rf"(<(?:[A-Za-z0-9_]+:)?c\b(?=[^>]*\br=\"{re.escape(address)}\")[^>]*>)(.*?)(</(?:[A-Za-z0-9_]+:)?c>)",
        re.S,
    )
    matches = list(pattern.finditer(worksheet))
    if len(matches) != 1 or re.search(r"<(?:[A-Za-z0-9_]+:)?f\b", matches[0].group(2)):
        raise AdapterRejected("UNSUPPORTED_PROFILE", "target is not patchable")
    stored = re.search(
        r"<(?:[A-Za-z0-9_]+:)?v\b[^>]*>(.*?)</(?:[A-Za-z0-9_]+:)?v>",
        matches[0].group(2),
        re.S,
    )
    if stored is None or Decimal(stored.group(1) or "NaN") != selected.expected_original:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "parent target changed")
    opening = re.sub(r'\s+t="[^"]*"', "", matches[0].group(1))
    body = (
        matches[0].group(2)[: stored.start(1)]
        + format(value, "f")
        + matches[0].group(2)[stored.end(1) :]
    )
    replacement = opening + body + matches[0].group(3)
    worksheet = worksheet[: matches[0].start()] + replacement + worksheet[matches[0].end() :]
    members[sheet_part] = worksheet.encode()
    _invalidate_formula_caches(members)
    candidate = _write_package(members)
    after = _cells(_read_package(candidate))
    changed_inputs = [
        ref
        for ref, cell in _cells(_read_package(parent_bytes)).items()
        if cell != after.get(ref) and not cell["formula"]
    ]
    if changed_inputs != [before["target_address"]]:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "patch changed an undeclared input")
    receipt = {
        "schema": "model-change-operation-receipt/v0",
        "parent_sha256": sha256(parent_bytes).hexdigest(),
        "patched_sha256": sha256(candidate).hexdigest(),
        "manifest_sha256": expected_manifest_digest,
        "inspection_sha256": expected_inspection_digest,
        "operation": {
            "kind": operation["kind"],
            "target_ref": operation["target_ref"],
            "before": before["target_value"],
            "after": format(value, "f"),
            "unit": operation["unit"],
        },
        "changed_inputs": changed_inputs,
    }
    receipt["sha256"] = canonical_digest(receipt)
    return candidate, receipt


def _calculation_environment(temporary: Path) -> dict[str, str]:
    return {
        "HOME": str(temporary / "home"),
        "TMPDIR": str(temporary / "tmp"),
        "LANG": "C",
        "LC_ALL": "C",
    }


def calculate(
    candidate_bytes: bytes,
    profile: Mapping[str, object],
    *,
    process: CalculationProcessAdapter | None = None,
) -> tuple[bytes, dict[str, object]]:
    _profile(profile)
    binary = Path(settings.MODEL_CHANGE_CALC_BINARY).resolve()
    process = process or CalculationProcessAdapter(
        binary, timeout_seconds=settings.MODEL_CHANGE_CALC_TIMEOUT_SECONDS
    )
    temporary = _temporary_root()
    try:
        source_directory = temporary / "source"
        output_directory = temporary / "output"
        profile_directory = temporary / "profile"
        for item in (
            source_directory,
            output_directory,
            profile_directory,
            temporary / "home",
            temporary / "tmp",
        ):
            item.mkdir()
        source = source_directory / "candidate.xlsx"
        source.write_bytes(candidate_bytes)
        environment = _calculation_environment(temporary)
        version = process.execute(process.version_command(), environment=environment)
        if version.exit_code != 0 or version.timed_out:
            raise AdapterRejected(
                "UNSUPPORTED_PROFILE", "calculation engine identity is unavailable"
            )
        command = process.calculate_command(
            source, output_directory, profile_directory
        )
        result = process.execute(command, environment=environment)
        calculated = output_directory / source.name
        if (
            result.exit_code != 0
            or result.timed_out
            or not calculated.is_file()
            or calculated.is_symlink()
        ):
            raise AdapterRejected(
                "UNSUPPORTED_PROFILE", "calculation engine did not return a workbook"
            )
        content = calculated.read_bytes()
        observed = inspect(content, profile, require_original_target=False)
        version_text = (version.stdout or version.stderr).decode(
            "utf-8", errors="replace"
        ).strip()
        evidence = {
            "engine_identity": (
                f"{binary.name}:{sha256(binary.read_bytes()).hexdigest()}"
            ),
            "engine_version": version_text,
            "timeout_seconds": process.timeout_seconds,
            "environment": {
                "HOME": "isolated-temporary",
                "TMPDIR": "isolated-temporary",
                "LANG": "C",
                "LC_ALL": "C",
                "profile": "isolated-temporary",
            },
            "input_sha256": sha256(candidate_bytes).hexdigest(),
            "output_sha256": sha256(content).hexdigest(),
            "warnings": observed["warnings"],
            "formula_errors": observed["formula_errors"],
        }
        return content, evidence
    finally:
        rmtree(temporary)


def compare(
    parent_bytes: bytes,
    candidate_bytes: bytes,
    dependency_closure: list[str],
    profile: Mapping[str, object],
) -> list[dict[str, object]]:
    selected = _profile(profile)
    if dependency_closure != [item[0] for item in selected.dependents]:
        raise AdapterRejected("UNSUPPORTED_PROFILE", "dependency closure changed")
    parent_cells = _cells(_read_package(parent_bytes))
    candidate_cells = _cells(_read_package(candidate_bytes))
    consequences = []
    for reference in dependency_closure:
        before = parent_cells.get(reference)
        after = candidate_cells.get(reference)
        if (
            before is None
            or after is None
            or before["formula"] != after["formula"]
            or after["value"] is None
        ):
            raise AdapterRejected(
                "UNSUPPORTED_PROFILE", "calculated consequence is unavailable"
            )
        consequences.append(
            {
                "ref": reference,
                "formula": after["formula"],
                "before": before["value"],
                "after": after["value"],
            }
        )
    return consequences

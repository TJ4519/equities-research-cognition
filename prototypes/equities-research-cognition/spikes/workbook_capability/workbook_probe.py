"""Create, patch, and independently inspect the bounded workbook fixture.

This module intentionally uses only the Python standard library.  It does not
calculate formulas and it never invokes a host process.  LibreOffice is run by
the worker from the shell so the experiment does not create a second process
spawn boundary inside the product package.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_DOCUMENT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN, "r": REL_DOCUMENT, "pr": REL_PACKAGE}

TARGET_NAME = "FY25_REVENUE_USDM"
TARGET_REFERENCE = "Model!$B$5"
TARGET_ORIGINAL = Decimal("36900")
TARGET_PATCHED = Decimal("37378")
FORMULAS = {
    "Model!B6": "B5/B4-1",
    "Valuation!B5": "B4/Model!B5",
}
PRESERVED_STYLE_CELLS = (
    "Model!A5",
    "Model!B5",
    "Model!A6",
    "Model!B6",
    "Valuation!A5",
    "Valuation!B5",
)


@dataclass(frozen=True)
class CellEvidence:
    address: str
    cell_type: str | None
    value: str | None
    formula: str | None
    style_id: int
    number_format_id: int
    number_format_code: str
    font_id: int
    fill_id: int
    border_id: int


@dataclass(frozen=True)
class WorkbookEvidence:
    path: str
    sha256: str
    named_range: str
    named_range_target: str
    cells: dict[str, CellEvidence]
    formula_errors: tuple[str, ...]
    dependencies: dict[str, tuple[str, ...]]
    package_members: tuple[str, ...]

    def serialise(self) -> dict[str, object]:
        payload = asdict(self)
        payload["cells"] = {
            key: asdict(value) for key, value in self.cells.items()
        }
        return payload


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _xml(text: str) -> bytes:
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n" + text).encode()


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o600 << 16
    return info


def generate_raw_fixture(output: Path) -> None:
    """Generate deterministic OOXML source bytes; an engine must calculate it."""

    output.parent.mkdir(parents=True, exist_ok=True)
    members = {
        "[Content_Types].xml": _xml(
            """<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>"""
        ),
        "_rels/.rels": _xml(
            """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
        ),
        "xl/workbook.xml": _xml(
            f"""<workbook xmlns="{MAIN}" xmlns:r="{REL_DOCUMENT}">
  <bookViews><workbookView activeTab="0"/></bookViews>
  <sheets>
    <sheet name="Model" sheetId="1" r:id="rId1"/>
    <sheet name="Valuation" sheetId="2" r:id="rId2"/>
  </sheets>
  <definedNames><definedName name="{TARGET_NAME}">{TARGET_REFERENCE}</definedName></definedNames>
  <calcPr calcId="191029" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>
</workbook>"""
        ),
        "xl/_rels/workbook.xml.rels": _xml(
            """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
        ),
        "xl/styles.xml": _xml(
            f"""<styleSheet xmlns="{MAIN}">
  <numFmts count="2">
    <numFmt numFmtId="164" formatCode="#,##0"/>
    <numFmt numFmtId="165" formatCode="0.00x"/>
  </numFmts>
  <fonts count="2">
    <font><sz val="11"/><name val="Aptos"/><family val="2"/></font>
    <font><b/><color rgb="FF173F35"/><sz val="11"/><name val="Aptos"/><family val="2"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE8F0ED"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border><left/><right/><top/><bottom style="thin"><color rgb="FF9AA9A3"/></bottom><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="5">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/>
    <xf numFmtId="10" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/>
    <xf numFmtId="165" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""
        ),
        "xl/worksheets/sheet1.xml": _xml(
            f"""<worksheet xmlns="{MAIN}">
  <dimension ref="A4:B6"/>
  <sheetViews><sheetView workbookViewId="0"><selection activeCell="B5" sqref="B5"/></sheetView></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols><col min="1" max="1" width="28" customWidth="1"/><col min="2" max="2" width="18" customWidth="1"/></cols>
  <sheetData>
    <row r="4"><c r="A4" s="1" t="inlineStr"><is><t>FY2024 revenue</t></is></c><c r="B4" s="2"><v>25111</v></c></row>
    <row r="5"><c r="A5" s="1" t="inlineStr"><is><t>FY2025 revenue</t></is></c><c r="B5" s="2"><v>36900</v></c></row>
    <row r="6"><c r="A6" s="1" t="inlineStr"><is><t>FY2025 revenue growth</t></is></c><c r="B6" s="3"><f>B5/B4-1</f><v/></c></row>
  </sheetData>
</worksheet>"""
        ),
        "xl/worksheets/sheet2.xml": _xml(
            f"""<worksheet xmlns="{MAIN}">
  <dimension ref="A4:B5"/>
  <sheetViews><sheetView workbookViewId="0"><selection activeCell="B5" sqref="B5"/></sheetView></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols><col min="1" max="1" width="30" customWidth="1"/><col min="2" max="2" width="18" customWidth="1"/></cols>
  <sheetData>
    <row r="4"><c r="A4" s="1" t="inlineStr"><is><t>Enterprise value assumption</t></is></c><c r="B4" s="2"><v>120000</v></c></row>
    <row r="5"><c r="A5" s="1" t="inlineStr"><is><t>EV / FY2025 revenue</t></is></c><c r="B5" s="4"><f>B4/Model!B5</f><v/></c></row>
  </sheetData>
</worksheet>"""
        ),
    }
    with ZipFile(output, "w") as archive:
        for name in sorted(members):
            archive.writestr(_zip_info(name), members[name])


def _read_package(path: Path) -> tuple[dict[str, bytes], list[ZipInfo]]:
    with ZipFile(path) as archive:
        infos = archive.infolist()
        return {info.filename: archive.read(info.filename) for info in infos}, infos


def _write_package(path: Path, members: dict[str, bytes], infos: Iterable[ZipInfo]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w") as archive:
        for info in infos:
            archive.writestr(info, members[info.filename])


def _resolve_defined_target(members: dict[str, bytes], defined_name: str) -> tuple[str, str, str]:
    workbook = ET.fromstring(members["xl/workbook.xml"])
    matching = workbook.findall(f"m:definedNames/m:definedName[@name='{defined_name}']", NS)
    if len(matching) != 1 or not matching[0].text:
        raise ValueError(f"expected one workbook-defined name {defined_name}")
    reference = matching[0].text
    match = re.fullmatch(r"'?([^']+)'?!\$([A-Z]+)\$(\d+)", reference)
    if not match:
        match = re.fullmatch(r"([^!]+)!\$([A-Z]+)\$(\d+)", reference)
    if not match:
        raise ValueError(f"unsupported defined-name reference: {reference}")
    sheet_name, column, row = match.groups()
    sheets = {
        sheet.attrib["name"]: sheet.attrib[f"{{{REL_DOCUMENT}}}id"]
        for sheet in workbook.findall("m:sheets/m:sheet", NS)
    }
    relationships = ET.fromstring(members["xl/_rels/workbook.xml.rels"])
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relationships.findall("pr:Relationship", NS)
    }
    relation_id = sheets.get(sheet_name)
    if not relation_id or relation_id not in targets:
        raise ValueError(f"defined-name sheet is not related: {sheet_name}")
    return reference, f"xl/{targets[relation_id]}", f"{column}{row}"


def patch_target(source: Path, output: Path, value: Decimal = TARGET_PATCHED) -> None:
    """Resolve the workbook name and set its one numeric target in a copy."""

    members, infos = _read_package(source)
    reference, sheet_part, address = _resolve_defined_target(members, TARGET_NAME)
    if reference != TARGET_REFERENCE or address != "B5":
        raise ValueError(f"unexpected target: {reference}")
    sheet = ET.fromstring(members[sheet_part])
    matching = sheet.findall(f".//m:c[@r='{address}']", NS)
    if len(matching) != 1:
        raise ValueError(f"expected one target cell {address}")
    target = matching[0]
    if target.find("m:f", NS) is not None:
        raise ValueError("target is a formula, not an input")
    current = target.find("m:v", NS)
    if current is None or Decimal(current.text or "NaN") != TARGET_ORIGINAL:
        raise ValueError(f"unexpected original target value: {current.text if current is not None else None}")
    target.attrib.pop("t", None)
    current.text = format(value, "f")
    ET.register_namespace("", MAIN)
    members[sheet_part] = ET.tostring(sheet, encoding="utf-8", xml_declaration=True)
    _invalidate_formula_caches(members)
    _write_package(output, members, infos)


def replace_formula(source: Path, output: Path, cell: str, formula: str) -> None:
    """Create a temporary invalid-formula case for engine visibility testing."""

    sheet_name, address = cell.split("!", 1)
    members, infos = _read_package(source)
    workbook = ET.fromstring(members["xl/workbook.xml"])
    sheets = {
        sheet.attrib["name"]: sheet.attrib[f"{{{REL_DOCUMENT}}}id"]
        for sheet in workbook.findall("m:sheets/m:sheet", NS)
    }
    relationships = ET.fromstring(members["xl/_rels/workbook.xml.rels"])
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relationships.findall("pr:Relationship", NS)
    }
    sheet_part = f"xl/{targets[sheets[sheet_name]]}"
    sheet = ET.fromstring(members[sheet_part])
    matching = sheet.findall(f".//m:c[@r='{address}']", NS)
    if len(matching) != 1 or matching[0].find("m:f", NS) is None:
        raise ValueError(f"expected one formula cell {cell}")
    matching[0].find("m:f", NS).text = formula
    cached = matching[0].find("m:v", NS)
    if cached is not None:
        cached.text = None
    ET.register_namespace("", MAIN)
    members[sheet_part] = ET.tostring(sheet, encoding="utf-8", xml_declaration=True)
    _invalidate_formula_caches(members)
    _write_package(output, members, infos)


def _invalidate_formula_caches(members: dict[str, bytes]) -> None:
    """Clear cached formula results and request a full engine calculation."""

    for part in sorted(name for name in members if name.startswith("xl/worksheets/") and name.endswith(".xml")):
        sheet = ET.fromstring(members[part])
        changed = False
        for cell in sheet.findall(".//m:c", NS):
            if cell.find("m:f", NS) is None:
                continue
            cached = cell.find("m:v", NS)
            if cached is None:
                cached = ET.SubElement(cell, f"{{{MAIN}}}v")
            if cached.text is not None:
                cached.text = None
                changed = True
        if changed:
            members[part] = ET.tostring(sheet, encoding="utf-8", xml_declaration=True)
    workbook = ET.fromstring(members["xl/workbook.xml"])
    calc = workbook.find("m:calcPr", NS)
    if calc is None:
        calc = ET.SubElement(workbook, f"{{{MAIN}}}calcPr")
    calc.attrib.update({"calcMode": "auto", "fullCalcOnLoad": "1", "forceFullCalc": "1"})
    members["xl/workbook.xml"] = ET.tostring(workbook, encoding="utf-8", xml_declaration=True)


def _style_number_formats(styles: ET.Element) -> list[tuple[int, str, int, int, int]]:
    cell_xfs = styles.find("m:cellXfs", NS)
    if cell_xfs is None:
        raise ValueError("workbook has no cellXfs")
    builtins = {0: "General", 9: "0%", 10: "0.00%"}
    custom = {
        int(item.attrib["numFmtId"]): item.attrib["formatCode"]
        for item in styles.findall("m:numFmts/m:numFmt", NS)
    }
    result: list[tuple[int, str, int, int, int]] = []
    for item in cell_xfs.findall("m:xf", NS):
        number_format_id = int(item.attrib.get("numFmtId", "0"))
        result.append(
            (
                number_format_id,
                custom.get(number_format_id, builtins.get(number_format_id, f"builtin:{number_format_id}")),
                int(item.attrib.get("fontId", "0")),
                int(item.attrib.get("fillId", "0")),
                int(item.attrib.get("borderId", "0")),
            )
        )
    return result


def _formula_dependencies(sheet_name: str, formula: str) -> tuple[str, ...]:
    references: list[str] = []
    token_pattern = re.compile(r"(?:(?:'([^']+)'|([A-Za-z0-9_]+))!)?(\$?[A-Z]+\$?\d+)")
    for quoted_sheet, plain_sheet, address in token_pattern.findall(formula):
        dependency_sheet = quoted_sheet or plain_sheet or sheet_name
        references.append(f"{dependency_sheet}!{address.replace('$', '')}")
    return tuple(dict.fromkeys(references))


def inspect_workbook(path: Path) -> WorkbookEvidence:
    """Read OOXML directly, independently of the patcher's semantic assertions."""

    members, _ = _read_package(path)
    workbook = ET.fromstring(members["xl/workbook.xml"])
    names = workbook.findall("m:definedNames/m:definedName", NS)
    named = {item.attrib.get("name", ""): item.text or "" for item in names}
    relationships = ET.fromstring(members["xl/_rels/workbook.xml.rels"])
    related_parts = {
        rel.attrib["Id"]: f"xl/{rel.attrib['Target']}"
        for rel in relationships.findall("pr:Relationship", NS)
    }
    sheets = {
        sheet.attrib["name"]: related_parts[sheet.attrib[f"{{{REL_DOCUMENT}}}id"]]
        for sheet in workbook.findall("m:sheets/m:sheet", NS)
    }
    style_formats = _style_number_formats(ET.fromstring(members["xl/styles.xml"]))
    shared_strings: list[str] = []
    if "xl/sharedStrings.xml" in members:
        shared_root = ET.fromstring(members["xl/sharedStrings.xml"])
        shared_strings = [
            "".join(text.text or "" for text in item.findall(".//m:t", NS))
            for item in shared_root.findall("m:si", NS)
        ]
    interesting = {
        "Model": ("A4", "B4", "A5", "B5", "A6", "B6"),
        "Valuation": ("A4", "B4", "A5", "B5"),
    }
    cells: dict[str, CellEvidence] = {}
    formula_errors: list[str] = []
    dependencies: dict[str, tuple[str, ...]] = {}
    for sheet_name, addresses in interesting.items():
        sheet = ET.fromstring(members[sheets[sheet_name]])
        by_address = {cell.attrib["r"]: cell for cell in sheet.findall(".//m:c", NS)}
        for address in addresses:
            cell = by_address[address]
            style_id = int(cell.attrib.get("s", "0"))
            value_element = cell.find("m:v", NS)
            formula_element = cell.find("m:f", NS)
            formula = formula_element.text if formula_element is not None else None
            value = value_element.text if value_element is not None else None
            if cell.attrib.get("t") == "s" and value is not None:
                value = shared_strings[int(value)]
            full_address = f"{sheet_name}!{address}"
            cells[full_address] = CellEvidence(
                address=full_address,
                cell_type=cell.attrib.get("t"),
                value=value,
                formula=formula,
                style_id=style_id,
                number_format_id=style_formats[style_id][0],
                number_format_code=style_formats[style_id][1],
                font_id=style_formats[style_id][2],
                fill_id=style_formats[style_id][3],
                border_id=style_formats[style_id][4],
            )
            if cell.attrib.get("t") == "e" or (value and value.startswith("#")):
                formula_errors.append(full_address)
            if formula:
                dependencies[full_address] = _formula_dependencies(sheet_name, formula)
    return WorkbookEvidence(
        path=str(path),
        sha256=digest(path),
        named_range=TARGET_NAME,
        named_range_target=named.get(TARGET_NAME, ""),
        cells=cells,
        formula_errors=tuple(formula_errors),
        dependencies=dependencies,
        package_members=tuple(sorted(members)),
    )


def verify_run(fixture: Path, patched: Path, recalculated: Path) -> dict[str, object]:
    before = inspect_workbook(fixture)
    proposed = inspect_workbook(patched)
    after = inspect_workbook(recalculated)
    if before.named_range_target != TARGET_REFERENCE:
        raise AssertionError(before.named_range_target)
    for evidence in (proposed, after):
        if evidence.named_range_target != before.named_range_target:
            raise AssertionError("named target changed")
        if evidence.cells["Model!B5"].value != "37378":
            raise AssertionError("target patch missing")
        for cell, formula in FORMULAS.items():
            if evidence.cells[cell].formula != formula:
                raise AssertionError(f"formula changed at {cell}")
        for cell in PRESERVED_STYLE_CELLS:
            expected_style = before.cells[cell]
            observed_style = evidence.cells[cell]
            if evidence is proposed and observed_style.style_id != expected_style.style_id:
                raise AssertionError(f"pre-engine style id changed at {cell}")
            if (
                observed_style.number_format_code,
                observed_style.font_id,
                observed_style.fill_id,
                observed_style.border_id,
            ) != (
                expected_style.number_format_code,
                expected_style.font_id,
                expected_style.fill_id,
                expected_style.border_id,
            ):
                raise AssertionError(f"style semantics changed at {cell}")
    if after.formula_errors:
        raise AssertionError(f"formula errors: {after.formula_errors}")
    expected_values = {
        "Model!B6": TARGET_PATCHED / Decimal("25111") - Decimal("1"),
        "Valuation!B5": Decimal("120000") / TARGET_PATCHED,
    }
    for cell, expected in expected_values.items():
        observed_text = after.cells[cell].value
        if observed_text is None:
            raise AssertionError(f"engine left no cached value at {cell}")
        if abs(Decimal(observed_text) - expected) > Decimal("1e-12"):
            raise AssertionError(f"engine cache mismatch at {cell}: {observed_text}")
    return {
        "fixture": before.serialise(),
        "patched": proposed.serialise(),
        "recalculated": after.serialise(),
        "dependent_values": {
            cell: {
                "before": before.cells[cell].value,
                "patched_before_engine": proposed.cells[cell].value,
                "after_engine": after.cells[cell].value,
                "independent_expected": format(expected_values[cell], "f"),
            }
            for cell in FORMULAS
        },
        "changed_package_members": sorted(
            name
            for name in set(before.package_members) | set(after.package_members)
            if _member_digest(fixture, name) != _member_digest(recalculated, name)
        ),
    }


def _member_digest(path: Path, member: str) -> str | None:
    with ZipFile(path) as archive:
        if member not in archive.namelist():
            return None
        return sha256(archive.read(member)).hexdigest()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate-raw")
    generate.add_argument("output", type=Path)
    patch = commands.add_parser("patch")
    patch.add_argument("source", type=Path)
    patch.add_argument("output", type=Path)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("workbook", type=Path)
    invalid = commands.add_parser("replace-formula")
    invalid.add_argument("source", type=Path)
    invalid.add_argument("output", type=Path)
    invalid.add_argument("cell")
    invalid.add_argument("formula")
    verify = commands.add_parser("verify-run")
    verify.add_argument("fixture", type=Path)
    verify.add_argument("patched", type=Path)
    verify.add_argument("recalculated", type=Path)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.command == "generate-raw":
        generate_raw_fixture(args.output)
        print(json.dumps({"path": str(args.output), "sha256": digest(args.output)}, sort_keys=True))
    elif args.command == "patch":
        patch_target(args.source, args.output)
        print(json.dumps({"path": str(args.output), "sha256": digest(args.output)}, sort_keys=True))
    elif args.command == "inspect":
        print(json.dumps(inspect_workbook(args.workbook).serialise(), indent=2, sort_keys=True))
    elif args.command == "replace-formula":
        replace_formula(args.source, args.output, args.cell, args.formula)
        print(json.dumps({"path": str(args.output), "sha256": digest(args.output)}, sort_keys=True))
    elif args.command == "verify-run":
        print(json.dumps(verify_run(args.fixture, args.patched, args.recalculated), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

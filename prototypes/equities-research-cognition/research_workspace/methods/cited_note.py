from __future__ import annotations

import json
from os import environ
from pathlib import Path


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def main() -> int:
    root = Path(environ["RESEARCH_CONTEXT_ROOT"])
    output = Path(environ["RESEARCH_OUTPUT_DIR"])
    manifest = load_json(root / "context-manifest.json")
    pairs = sorted(
        manifest["allowed_support_pairs"],
        key=lambda item: (item["professional_object_id"], item["assertion_id"]),
    )
    claims: list[dict] = []
    note_lines = [
        f"# {manifest['purpose']}",
        "",
        "The note uses only assertion-to-object relations admitted for this context.",
        "",
    ]
    for index, pair in enumerate(pairs, start=1):
        assertion = load_json(
            root / "evidence/assertions" / f"{pair['assertion_id']}.json"
        )
        professional_object = load_json(
            root
            / "professional-objects"
            / f"{pair['professional_object_id']}.json"
        )
        text = assertion["payload"]["content"]
        label = professional_object["payload"]["label"]
        claim_text = f"{label}: {text}"
        claims.append(
            {
                "claim_id": f"claim-{index:03d}",
                "text": claim_text,
                "support_relations": [pair],
                "uncertainty": [],
            }
        )
        note_lines.extend(
            [
                f"## {label}",
                "",
                text,
                "",
                f"Support: `{pair['assertion_id']}`",
                "",
            ]
        )
    memory_files = sorted((root / "memory").glob("*.json"))
    if memory_files:
        note_lines.extend(["## Prior confirmed context", ""])
        for memory_file in memory_files:
            memory = load_json(memory_file)
            note_lines.extend(
                [
                    memory["payload"]["content"],
                    "",
                    f"Authority: `{memory['payload']['authority']}`",
                    "",
                ]
            )

    if manifest["excluded_assertions"]:
        note_lines.extend(
            [
                "## Evidence not used for support",
                "",
                f"{len(manifest['excluded_assertions'])} assertion(s) were excluded by the sealed context.",
                "",
            ]
        )
    note_path = output / "research-note.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")
    result = {
        "schema": "research-result/v1",
        "summary": f"Produced {len(claims)} admitted claim(s) and one cited note.",
        "claims": claims,
        "artifacts": [
            {
                "path": "research-note.md",
                "kind": "research_note",
                "title": manifest["purpose"],
                "media_type": "text/markdown",
            }
        ],
        "memory_proposals": [],
    }
    (output / "result.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

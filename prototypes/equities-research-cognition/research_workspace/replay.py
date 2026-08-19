from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from .errors import IntegrityError, RuntimeFailure, ValidationError
from .integrity import load_and_verify_context
from .runtime import DirectProcessAdapter, copy_context_for_replay
from .store import StoredObject, WorkspaceStore
from .util import (
    atomic_write,
    canonical_json,
    digest_bytes,
    digest_json,
    ensure_inside,
    new_id,
    read_regular_file,
    safe_relative_path,
)


class ReplayEngine:
    """Reconstruct and rerun licensed inference state from durable objects."""

    def __init__(self, store: WorkspaceStore) -> None:
        self.store = store

    def _dependencies(self, item: StoredObject) -> list[str]:
        payload = item.payload
        if item.kind == "perspective":
            values = list(payload.get("item_ids", []))
            if payload.get("parent_id"):
                values.append(payload["parent_id"])
            values.append(payload["mandate_id"])
            return values
        if item.kind == "episode":
            values = [payload["mandate_id"]]
            if payload.get("prior_perspective_id"):
                values.append(payload["prior_perspective_id"])
            return values
        if item.kind == "commission":
            return [payload["episode_id"], *payload.get("subject_ids", []), *payload.get("method_ids", [])]
        if item.kind == "source":
            return [payload["mandate_id"]]
        if item.kind == "assertion":
            return [payload["source_id"]]
        if item.kind == "professional_object":
            return [payload["mandate_id"]]
        if item.kind == "evidence_decision":
            return [payload["episode_id"], payload["assertion_id"], payload["professional_object_id"]]
        if item.kind == "context":
            values = [
                payload["episode_id"],
                payload["commission_id"],
                payload["method_id"],
                *payload.get("professional_object_ids", []),
                *payload.get("included_assertion_ids", []),
                *payload.get("memory_entry_ids", []),
            ]
            values.extend(item["assertion_id"] for item in payload.get("excluded_assertions", []))
            return values
        if item.kind == "run":
            return [payload["context_id"]]
        if item.kind == "claim":
            return [
                payload["episode_id"],
                payload["run_id"],
                *payload.get("supporting_assertion_ids", []),
                *payload.get("professional_object_ids", []),
            ]
        if item.kind == "result":
            return [
                payload["episode_id"],
                payload["run_id"],
                *payload.get("claim_ids", []),
                *payload.get("artifact_ids", []),
                *payload.get("memory_proposal_ids", []),
            ]
        if item.kind == "artifact":
            values = [payload["mandate_id"], payload["episode_id"]]
            if payload.get("parent_id"):
                values.append(payload["parent_id"])
            run_id = payload.get("metadata", {}).get("producing_run_id")
            if run_id:
                values.append(run_id)
            return values
        if item.kind == "decision":
            return [payload["episode_id"], payload["target_id"]]
        if item.kind == "correction":
            return [payload["episode_id"], payload["target_id"]]
        if item.kind == "memory":
            values = [payload["mandate_id"]]
            if payload.get("source_correction_id"):
                values.append(payload["source_correction_id"])
            return values
        if item.kind == "evaluation_case":
            return [
                payload["mandate_id"],
                payload["episode_id"],
                payload["baseline_run_id"],
                payload["baseline_result_id"],
            ]
        if item.kind == "replay":
            return [payload["evaluation_case_id"]]
        return []

    def collect_lineage(self, target_id: str) -> dict[str, StoredObject]:
        pending = [target_id]
        collected: dict[str, StoredObject] = {}
        while pending:
            object_id = pending.pop()
            if object_id in collected:
                continue
            item = self.store.get_object(object_id)
            collected[object_id] = item
            pending.extend(self._dependencies(item))
            for relation in self.store.relations_from(object_id):
                if relation.predicate in {"has_decision", "corrected_by", "promoted_as_memory"}:
                    pending.append(relation.object_id)
        return collected

    def verify_run(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_object(run_id)
        if run.kind != "run":
            raise ValidationError(f"{run_id} is not a run")
        self.store.verify_object(run.id)
        self.store.read_blob(run.payload["stdout_digest"])
        self.store.read_blob(run.payload["stderr_digest"])
        context = self.store.get_object(run.payload["context_id"])
        context_directory, manifest = load_and_verify_context(self.store, context)
        checked_files = 0
        output_manifest = run.payload.get("output_manifest", {})
        for item in output_manifest.get("files", []):
            path = ensure_inside(
                context_directory / "output",
                context_directory / "output" / safe_relative_path(item["path"]),
            )
            content = read_regular_file(path, max_bytes=DirectProcessAdapter.MAX_SINGLE_BYTES)
            if len(content) != item["size"] or digest_bytes(content) != item["sha256"]:
                raise IntegrityError(f"run output changed after custody: {item['path']}")
            checked_files += 1
        return {
            "run_id": run.id,
            "status": run.payload["status"],
            "context_id": context.id,
            "context_manifest_digest": context.payload["manifest_digest"],
            "included_assertion_ids": manifest["included_assertion_ids"],
            "checked_output_files": checked_files,
        }

    def verify_target(self, target_id: str) -> dict[str, Any]:
        lineage = self.collect_lineage(target_id)
        checked_blobs: set[str] = set()
        checked_contexts: set[str] = set()
        checked_runs: set[str] = set()
        for item in lineage.values():
            self.store.verify_object(item.id)
            if item.kind in {"source", "artifact"}:
                digest = item.payload["blob_digest"]
                self.store.read_blob(digest)
                checked_blobs.add(digest)
            elif item.kind == "context":
                load_and_verify_context(self.store, item)
                checked_contexts.add(item.id)
            elif item.kind == "run":
                self.verify_run(item.id)
                checked_runs.add(item.id)
        relation_count = 0
        lineage_ids = set(lineage)
        for object_id in lineage_ids:
            for relation in self.store.relations_from(object_id):
                if relation.object_id in lineage_ids:
                    self.store.verify_relation(relation)
                    relation_count += 1
        return {
            "target_id": target_id,
            "grade": "licensed-path-reconstruction",
            "objects": len(lineage),
            "relations": relation_count,
            "blobs": len(checked_blobs),
            "contexts": len(checked_contexts),
            "runs": len(checked_runs),
        }

    def explain(self, target_id: str) -> dict[str, Any]:
        verification = self.verify_target(target_id)
        lineage = self.collect_lineage(target_id)
        ordered = sorted(lineage.values(), key=lambda item: (item.created_at, item.id))
        relations: list[dict[str, Any]] = []
        ids = set(lineage)
        for object_id in ids:
            for relation in self.store.relations_from(object_id):
                if relation.object_id in ids:
                    relations.append(
                        {
                            "subject_id": relation.subject_id,
                            "predicate": relation.predicate,
                            "object_id": relation.object_id,
                            "payload": relation.payload,
                            "digest": relation.digest,
                        }
                    )
        relations.sort(key=lambda item: (item["subject_id"], item["predicate"], item["object_id"]))
        return {
            "schema": "research-lineage-explanation/v1",
            "verification": verification,
            "target": {
                "id": lineage[target_id].id,
                "kind": lineage[target_id].kind,
                "payload": lineage[target_id].payload,
                "digest": lineage[target_id].digest,
            },
            "objects": [
                {
                    "id": item.id,
                    "kind": item.kind,
                    "payload": item.payload,
                    "digest": item.digest,
                    "created_at": item.created_at,
                }
                for item in ordered
            ],
            "relations": relations,
        }

    def export_proof_pack(self, target_id: str, destination: Path) -> Path:
        explanation = self.explain(target_id)
        destination = destination.expanduser().resolve()
        if destination.exists():
            raise ValidationError("proof-pack destination already exists")
        destination.mkdir(parents=True, mode=0o700)
        atomic_write(
            destination / "manifest.json",
            canonical_json(
                {
                    "schema": "research-proof-pack/v1",
                    "target_id": target_id,
                    "verification": explanation["verification"],
                    "objects_file": "objects.jsonl",
                    "relations_file": "relations.jsonl",
                    "explanation_file": "explanation.json",
                }
            ).encode("utf-8"),
        )
        objects_lines = "\n".join(canonical_json(item) for item in explanation["objects"]) + "\n"
        relations_lines = "\n".join(canonical_json(item) for item in explanation["relations"]) + "\n"
        atomic_write(destination / "objects.jsonl", objects_lines.encode("utf-8"))
        atomic_write(destination / "relations.jsonl", relations_lines.encode("utf-8"))
        atomic_write(destination / "explanation.json", canonical_json(explanation).encode("utf-8"))
        return destination

    def replay_evaluation_case(
        self,
        evaluation_case_id: str,
        *,
        argv_override: list[str] | None = None,
        timeout_seconds: int = 300,
    ) -> StoredObject:
        case = self.store.get_object(evaluation_case_id)
        if case.kind != "evaluation_case":
            raise ValidationError(f"{evaluation_case_id} is not an evaluation case")
        baseline_run = self.store.get_object(case.payload["baseline_run_id"])
        baseline_result = self.store.get_object(case.payload["baseline_result_id"])
        if baseline_run.kind != "run" or baseline_result.kind != "result":
            raise IntegrityError("evaluation baseline objects have the wrong kind")
        self.verify_run(baseline_run.id)
        context = self.store.get_object(baseline_run.payload["context_id"])
        source_directory, manifest = load_and_verify_context(self.store, context)
        replay_id = new_id("replay")
        work_directory = ensure_inside(
            self.store.contexts_root,
            self.store.contexts_root / f"{replay_id}-work",
        )
        copy_context_for_replay(source_directory, work_directory)
        adapter = DirectProcessAdapter(self.store)
        argv = list(argv_override or baseline_run.payload["argv"])
        receipt = adapter.execute(
            context_directory=work_directory,
            argv=argv,
            timeout_seconds=timeout_seconds,
        )
        checks: dict[str, Any] = {
            "process_exit_code": receipt.exit_code,
            "timed_out": receipt.timed_out,
            "context_manifest_digest": context.payload["manifest_digest"],
        }
        comparison: dict[str, Any] = {}
        replay_status = "fail"
        grade = "transcript-only-observability"
        try:
            if receipt.timed_out or receipt.exit_code != 0:
                raise RuntimeFailure("replay process did not complete successfully")
            population = adapter.seal_output(work_directory)
            validated = adapter.validate_result(
                population.result,
                included_assertion_ids=set(manifest["included_assertion_ids"]),
                professional_object_ids=set(manifest["professional_object_ids"]),
                allowed_support_pairs={
                    (item["assertion_id"], item["professional_object_id"])
                    for item in manifest["allowed_support_pairs"]
                },
                output_files={item["path"] for item in population.files},
            )
            replay_result_digest = digest_json(validated)
            baseline_result_digest = baseline_result.payload["result_digest"]
            baseline_artifacts: dict[str, str] = {}
            for artifact_id in baseline_result.payload["artifact_ids"]:
                artifact = self.store.get_object(artifact_id)
                baseline_artifacts[artifact.payload["metadata"]["source_path"]] = artifact.payload["blob_digest"]
            replay_artifacts: dict[str, str] = {}
            for artifact_data in validated["artifacts"]:
                content = read_regular_file(
                    work_directory / "output" / safe_relative_path(artifact_data["path"]),
                    max_bytes=DirectProcessAdapter.MAX_SINGLE_BYTES,
                )
                replay_artifacts[artifact_data["path"]] = digest_bytes(content)
            comparison = {
                "baseline_result_digest": baseline_result_digest,
                "replay_result_digest": replay_result_digest,
                "result_equal": replay_result_digest == baseline_result_digest,
                "baseline_artifacts": baseline_artifacts,
                "replay_artifacts": replay_artifacts,
                "artifacts_equal": replay_artifacts == baseline_artifacts,
                "argv_changed": argv != baseline_run.payload["argv"],
            }
            if argv_override is None:
                replay_status = (
                    "pass" if comparison["result_equal"] and comparison["artifacts_equal"] else "fail"
                )
                grade = "exact-deterministic-reproduction"
            else:
                replay_status = "limited"
                grade = "counterfactual-comparison"
        finally:
            final_directory = ensure_inside(
                self.store.replays_root,
                self.store.replays_root / replay_id,
            )
            if final_directory.exists():
                shutil.rmtree(final_directory)
            if work_directory.exists():
                shutil.move(str(work_directory), str(final_directory))
        replay = self.store.put_object(
            "replay",
            {
                "schema": "research-replay/v1",
                "evaluation_case_id": evaluation_case_id,
                "mode": "counterfactual" if argv_override is not None else "baseline",
                "status": replay_status,
                "grade": grade,
                "checks": checks,
                "comparison": comparison,
                "argv": argv,
                "relative_directory": final_directory.relative_to(self.store.root).as_posix(),
            },
            object_id=replay_id,
        )
        self.store.put_relation(evaluation_case_id, "replayed_as", replay.id)
        return replay

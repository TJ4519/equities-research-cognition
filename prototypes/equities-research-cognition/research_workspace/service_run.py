from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .errors import RuntimeFailure, ValidationError
from .integrity import load_and_verify_context
from .runtime import DirectProcessAdapter
from .service_types import RunOutcome
from .util import digest_json, read_regular_file, safe_relative_path, utc_now


class RunServiceMixin:
    def run_context(
        self,
        *,
        context_id: str,
        argv: list[str],
        timeout_seconds: int = 300,
        extra_environment: Mapping[str, str] | None = None,
    ) -> RunOutcome:
        context = self._require_kind(context_id, "context")
        context_directory, manifest = load_and_verify_context(self.store, context)
        adapter = DirectProcessAdapter(self.store)
        receipt = adapter.execute(
            context_directory=context_directory,
            argv=argv,
            timeout_seconds=timeout_seconds,
            extra_environment=extra_environment,
        )
        stdout_blob = self.store.put_blob(receipt.stdout, media_type="text/plain")
        stderr_blob = self.store.put_blob(receipt.stderr, media_type="text/plain")
        status = "timed_out" if receipt.timed_out else (
            "succeeded" if receipt.exit_code == 0 else "failed"
        )
        population_payload: dict[str, Any] = {}
        population = None
        result_validation: dict[str, Any] | None = None
        failure_message: str | None = None
        if status == "succeeded":
            try:
                population = adapter.seal_output(context_directory)
                output_files = {item["path"] for item in population.files}
                allowed_pairs = {
                    (item["assertion_id"], item["professional_object_id"])
                    for item in manifest["allowed_support_pairs"]
                }
                result_validation = adapter.validate_result(
                    population.result,
                    included_assertion_ids=set(manifest["included_assertion_ids"]),
                    professional_object_ids=set(manifest["professional_object_ids"]),
                    allowed_support_pairs=allowed_pairs,
                    output_files=output_files,
                )
                population_payload = {
                    "schema": "research-output-population/v1",
                    "files": population.files,
                    "total_bytes": population.total_bytes,
                }
            except (RuntimeFailure, ValidationError) as exc:
                status = "failed"
                failure_message = str(exc)
        run = self.store.put_object(
            "run",
            {
                "schema": "research-run/v1",
                "context_id": context_id,
                "adapter": "direct-process/v1",
                "argv": argv,
                "working_directory": receipt.working_directory,
                "pid": receipt.pid,
                "process_group": receipt.process_group,
                "started_at": receipt.started_at,
                "ended_at": receipt.ended_at,
                "exit_code": receipt.exit_code,
                "signal": receipt.signal,
                "status": status,
                "stdout_digest": stdout_blob.digest,
                "stderr_digest": stderr_blob.digest,
                "output_manifest": population_payload,
                "failure": failure_message,
            },
        )
        self.store.put_relation(context_id, "executed_as", run.id)
        if status != "succeeded" or population is None or result_validation is None:
            raise RuntimeFailure(failure_message or f"child process {status}")

        episode = self._require_kind(context.payload["episode_id"], "episode")
        mandate_id = episode.payload["mandate_id"]
        claim_ids: list[str] = []
        for claim_data in result_validation["claims"]:
            claim = self.store.put_object(
                "claim",
                {
                    "schema": "research-claim/v1",
                    "episode_id": episode.id,
                    "run_id": run.id,
                    "text": claim_data["text"],
                    "supporting_assertion_ids": claim_data["supporting_assertion_ids"],
                    "professional_object_ids": claim_data["professional_object_ids"],
                    "support_relations": claim_data["support_relations"],
                    "uncertainty": claim_data["uncertainty"],
                    "external_claim_id": claim_data["claim_id"],
                },
            )
            claim_ids.append(claim.id)
            self.store.put_relation(run.id, "produced", claim.id)
            for relation in claim_data["support_relations"]:
                self.store.put_relation(
                    relation["assertion_id"],
                    "supports",
                    claim.id,
                    {"professional_object_id": relation["professional_object_id"]},
                )
                self.store.put_relation(
                    claim.id,
                    "concerns",
                    relation["professional_object_id"],
                )

        artifact_ids: list[str] = []
        output_directory = context_directory / "output"
        for artifact_data in result_validation["artifacts"]:
            relative = safe_relative_path(artifact_data["path"])
            artifact_path = output_directory / relative
            content = read_regular_file(
                artifact_path,
                max_bytes=DirectProcessAdapter.MAX_SINGLE_BYTES,
            )
            blob = self.store.put_blob(content, media_type=artifact_data["media_type"])
            artifact = self.store.put_object(
                "artifact",
                {
                    "schema": "research-artifact/v1",
                    "mandate_id": mandate_id,
                    "episode_id": episode.id,
                    "kind": artifact_data["kind"],
                    "filename": relative.name,
                    "blob_digest": blob.digest,
                    "metadata": {
                        "title": artifact_data["title"],
                        "source_path": artifact_data["path"],
                        "producing_context_id": context.id,
                        "producing_run_id": run.id,
                    },
                    "parent_id": None,
                },
            )
            artifact_ids.append(artifact.id)
            self.store.put_relation(run.id, "produced", artifact.id)

        memory_proposal_ids: list[str] = []
        for proposal in result_validation["memory_proposals"]:
            memory = self.store.put_object(
                "memory",
                {
                    "schema": "research-memory/v1",
                    "mandate_id": mandate_id,
                    "actor": f"model-run:{run.id}",
                    "content": proposal["content"],
                    "scope": proposal["scope"],
                    "authority": "model_proposed",
                    "source_correction_id": None,
                    "effective_from": utc_now(),
                    "effective_until": None,
                    "reason": proposal["reason"],
                },
            )
            memory_proposal_ids.append(memory.id)
            self.store.put_relation(run.id, "proposed_memory", memory.id)

        result = self.store.put_object(
            "result",
            {
                "schema": "research-result/v1",
                "episode_id": episode.id,
                "run_id": run.id,
                "summary": result_validation["summary"],
                "claim_ids": claim_ids,
                "artifact_ids": artifact_ids,
                "memory_proposal_ids": memory_proposal_ids,
                "result_digest": digest_json(result_validation),
            },
        )
        self.store.put_relation(run.id, "produced", result.id)
        for claim_id in claim_ids:
            self.store.put_relation(result.id, "contains", claim_id)
        for artifact_id in artifact_ids:
            self.store.put_relation(result.id, "rendered_as", artifact_id)
        for memory_id in memory_proposal_ids:
            self.store.put_relation(result.id, "proposes_memory", memory_id)
        return RunOutcome(
            run_id=run.id,
            result_id=result.id,
            claim_ids=tuple(claim_ids),
            artifact_ids=tuple(artifact_ids),
            memory_proposal_ids=tuple(memory_proposal_ids),
        )

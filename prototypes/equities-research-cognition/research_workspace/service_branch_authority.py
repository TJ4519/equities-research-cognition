from __future__ import annotations

from .integrity import load_and_verify_context


class AcknowledgedBranchAuthorityMixin:
    """Limit branch evidence to contexts semantically acknowledged by Codex.

    A context attached to a branch or copied into an attempt is not yet worker
    context. The context becomes usable by the active binding only after the
    exact NTM-delivered instruction has a semantic Codex acknowledgement.
    """

    def _branch_authority(
        self,
        branch_id: str,
    ) -> tuple[set[str], set[str], set[tuple[str, str]]]:
        binding = self._latest_binding(branch_id)
        if binding is None:
            return set(), set(), set()
        context_ids: list[str] = []
        instructions = [
            self._require_kind(relation.object_id, "branch_instruction")
            for relation in self.store.relations_from(binding.id, "has_instruction")
        ]
        for instruction in sorted(
            instructions,
            key=lambda item: item.payload["sequence"],
        ):
            if self._instruction_ack(instruction.id) is None:
                continue
            for context_id in instruction.payload["context_ids"]:
                if context_id not in context_ids:
                    context_ids.append(context_id)
        assertions: set[str] = set()
        objects: set[str] = set()
        pairs: set[tuple[str, str]] = set()
        for context_id in context_ids:
            context = self._require_kind(context_id, "context")
            _, manifest = load_and_verify_context(self.store, context)
            assertions.update(manifest["included_assertion_ids"])
            objects.update(manifest["professional_object_ids"])
            pairs.update(
                (item["assertion_id"], item["professional_object_id"])
                for item in manifest["allowed_support_pairs"]
            )
        return assertions, objects, pairs

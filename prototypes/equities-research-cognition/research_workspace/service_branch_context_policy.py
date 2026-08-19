from __future__ import annotations

from .errors import AuthorityError, ValidationError


class StableBranchContextKindMixin:
    """Prevent one persistent session from crossing discovery/support authority."""

    def _context_kind(self, context_id: str) -> str:
        context = self._require_kind(context_id, "context")
        return context.payload.get("context_kind", "support")

    def _branch_context_kind(self, branch_id: str) -> str:
        context_ids = self._branch_context_ids(branch_id)
        kinds = {self._context_kind(context_id) for context_id in context_ids}
        if len(kinds) != 1:
            raise AuthorityError("research branch mixes incompatible context kinds")
        return next(iter(kinds))

    def create_research_branch(self, *, context_ids: list[str], **kwargs):
        kinds = {self._context_kind(context_id) for context_id in context_ids}
        if len(kinds) != 1:
            raise ValidationError(
                "one persistent research branch requires one context kind"
            )
        return super().create_research_branch(context_ids=context_ids, **kwargs)

    def launch_research_branch(self, *, branch_id: str, **kwargs):
        self._branch_context_kind(branch_id)
        return super().launch_research_branch(branch_id=branch_id, **kwargs)

    def attach_branch_context_delta(
        self,
        *,
        branch_id: str,
        context_id: str,
        **kwargs,
    ):
        current_kind = self._branch_context_kind(branch_id)
        incoming_kind = self._context_kind(context_id)
        if incoming_kind != current_kind:
            raise AuthorityError(
                "a discovery/support boundary requires a separate NTM research branch"
            )
        return super().attach_branch_context_delta(
            branch_id=branch_id,
            context_id=context_id,
            **kwargs,
        )

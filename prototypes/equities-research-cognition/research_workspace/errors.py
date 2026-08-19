class WorkspaceError(Exception):
    """Base failure for the local research workspace."""


class ValidationError(WorkspaceError):
    """An input cannot become canonical workspace state."""


class AuthorityError(WorkspaceError):
    """An actor, source, context, or result lacks authority for an action."""


class IntegrityError(WorkspaceError):
    """Stored or materialised bytes no longer match canonical identity."""


class RuntimeFailure(WorkspaceError):
    """A child process failed before a valid result entered custody."""

# Codex runtime boundary

Codex CLI is the operator-installed cognition runtime. This package freezes
exact role and workbench instructions into campaign work orders, then the NTM
adapter addresses subscribed Codex sessions. It does not call a paid model API,
redistribute Codex, or provide a second Python agent runtime.

Codex authentication belongs to the operating identity that launches the
session. A Django login does not inherit or grant Codex entitlement. Any future
third-party operation requires its own isolated runtime identity and explicit
permission; it must not multiplex a founder's local Codex session.

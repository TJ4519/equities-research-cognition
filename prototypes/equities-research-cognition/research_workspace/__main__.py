from __future__ import annotations

import sys

from .branch_cli import COMMANDS, main as branch_main
from .cli import main as workspace_main


if len(sys.argv) > 1 and sys.argv[1] in COMMANDS:
    raise SystemExit(branch_main())
raise SystemExit(workspace_main())

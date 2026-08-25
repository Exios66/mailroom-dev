import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Sibling llm-mailroom's editable install puts `src/` on sys.path; that
# `scripts` package must not shadow this repo's `scripts/` directory.
sys.path[:] = [p for p in sys.path if "llm-mailroom" not in Path(p).as_posix()]
sys.path.insert(0, str(ROOT))

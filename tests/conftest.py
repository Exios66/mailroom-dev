import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Sibling llm-mailroom's editable install puts `src/` on sys.path; that
# `scripts` package must not shadow this repo's `scripts/` directory.
# mailroom_ui.producer imports pipeline.review_resolve from site-packages
# (extra `[pipeline]`) or a temporary checkout path that is removed after load.
sys.path[:] = [p for p in sys.path if "llm-mailroom" not in Path(p).as_posix()]
sys.path.insert(0, str(ROOT))

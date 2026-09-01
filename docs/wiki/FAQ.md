# FAQ

**Q: Why does `uv sync` install packages I didn't ask for?**
One uv workspace: every member installs editable into the shared `.venv`.
Cross-package imports resolve to workspace sources via `[tool.uv.sources]`.

**Q: Can I delete a dependency git pin to fix resolution?**
No. Member dependency lines keep their published git pins (plain
`pip install .` release builds depend on them). Dev redirection happens
ONLY through `[tool.uv.sources]`; bump pins only at release time ([[Releases]]).

**Q: Why did a subtree pull bring back `docs/data/` / `docs/posit/` in
llm-entity-extraction?**
Those are monorepo-pruned heavy-asset paths (root `.gitignore`), but
gitignore does not apply to tracked files — a subtree merge re-tracks them.
Re-apply the prune: `git rm -r --cached <paths>` + tree removal (HUB-004).
Tests with pruned-asset skip guards then skip correctly again.

**Q: A test fails on `reports/experiment_log.jsonl` missing.**
That log is a live artifact, gitignored in the monorepo. Tests depending on
it carry explicit skip guards ("pruned heavy asset / live artifact"); if you
see a hard failure, the guard is missing — add the skip monorepo-side
(HUB-004 pattern).

**Q: The board tracker says `unclaimed-with-commits` — what do I do?**
Commits reference a card that is still `assigned`+unclaimed: claim it (lane
`in_progress`, Owner + date) or move the work. Warnings don't fail CI;
errors do ([[Board-Governance]]).

**Q: `board_state.py project-*` says the token lacks `read:project`.**
One-time interactive grant: `gh auth refresh -s read:project`, then
`project-init` + `project-sync --apply`.

**Q: Where do prompts flow?**
llm-dojo → llm-mailroom, never the reverse. Prompt versions are the
experiment identity — never mutate a prompt that has run; derive a new
version key (see the llm-entity-extraction AGENTS.md).

**Q: Which HF dataset is canonical?**
[docclass-merged](https://huggingface.co/datasets/Lucius-Morningstar/docclass-merged)
schema v7, 1,650 rows, data rev `1acd2600` ([[HF-Corpus]]). Uploads go
through the centralized `mailroom_eda` helpers only.

**Q: Where did the reporter agent go?**
Retired (HUB-015): the graph's `compile_report` node is the computational
procedural reporter — deterministic, no LLM call. Reviewers were NOT
removed.

**Q: How do I run one package's tests without collisions?**
One package per pytest invocation — several packages ship a top-level
regular `tests` package ([[Getting-Started]]).

# AGENTS.md

Monorepo for the LLM-Mailroom constellation. One uv workspace, one lockfile
(`uv.lock`), one virtualenv. Never add cross-repo imports outside the
workspace — dependency between members resolves via `[tool.uv.sources]`
workspace redirects.

## Layout

- `packages/llm-dojo-scoring` — scoring engine (dist `llm-dojo-scoring`)
- `packages/llm-mailroom` — pipeline (dist `mailroom`, `src/` layout)
- `packages/llm-entity-extraction` — eval loop (flat `agents`/`src`/`config` layout)
- `packages/The-Mailroom` — visualizer (dist `the-mailroom`)

Each package carries its own `AGENTS.md` with project-specific conventions —
read the package's AGENTS.md before changing code inside it.

## Commands

```bash
uv sync            # install workspace + dev group into .venv (editable)
uv lock            # after touching any pyproject dependency spec
uv run pytest ...  # run against the shared venv
```

Per-package test suites:

```bash
uv run pytest packages/llm-dojo-scoring/tests
uv run pytest packages/llm-mailroom/src/tests
uv run pytest packages/llm-entity-extraction/tests
uv run pytest packages/The-Mailroom/tests
```

## Workspace rules

- Member dependency lines keep their published git pins (release builds via
  plain `pip install .` depend on them). Dev redirection happens ONLY through
  `[tool.uv.sources]` tables — never delete a pin line to "fix" resolution.
- Bump a pin only when cutting a release of the pinned package (see
  `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py`, release-time only).
- Heavy assets (docs demos/screenshots, example PDFs, report archives) are
  pruned from this repo — keep them out; reference the upstream repos.
- Deploy configs (Dockerfile, nixpacks.toml, railway.json) inside each
  package are still standalone-repo aware; build images from the package
  directory as before.

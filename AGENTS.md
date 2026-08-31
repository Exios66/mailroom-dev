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
- `packages/agent-mailroom` — walking-office-floor mailroom (dist `agent-mailroom`)
- `packages/local-mailroom-sandbox` — local experiment sandbox (dist `mailroom-sandbox`)
- `packages/Enron-Evaluation-Environment` — corpus feed (virtual member, no build)
- `packages/claims-data-eda` — corpus feed (virtual member, no build)
- `packages/llm-mailroom-graph` — derived graph site (virtual member, no build)
- `packages/mailroom-corpus-eda` — corpus EDA + centralized HF upload helpers (virtual member, no build)

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
uv run pytest packages/agent-mailroom/tests
uv run pytest packages/local-mailroom-sandbox/tests
uv run pytest packages/claims-data-eda/tests
```

## HF Hub uploads

The `docclass-merged` dataset family is published through the CENTRALIZED
helpers in `packages/mailroom-corpus-eda/src/mailroom_eda/` (`hf_interface`,
`dataset_export`, `docclass_uploader`) — never ad-hoc upload code. See
`packages/mailroom-corpus-eda/AGENTS.md` and the `huggingface` opencode skill
for the full workflow (cast-safe metadata, line-boundary-safe JSONL, sha256
verification, surgical card renders, blind-config label guard).

## Governance & task board

`governance/TASKS.md` is the monorepo's task board and the single source of
truth for cross-agent task state: what is assigned, in progress, needs
attention, and done. Read it FIRST every session, before any task. It is the
simplified counterpart of
`packages/llm-entity-extraction/governance/MESSAGE_BOARD.md` (same laws,
fewer steps); package-scoped work keeps its own board.

The four lanes: `assigned` (queued/claimed, nothing underway) →
`in_progress` (any work exists — label the card before the code, never after)
→ `needs_attention` (blocked / review / decision, tagged in Evidence) →
`done` (Archive, append-only; reopen instead of delete).

- **Claim before edit** — one owner per card; claim = lane + Owner name + date.
- **Update, don't duplicate** — work touching an existing card's scope updates
  that card; a discovered-but-undelivered item spawns its own card before the
  parent closes.
- **No silent completion** — `done` requires green suites for the touched
  packages, a clean `git status` for the card's scope, Evidence naming the
  commit(s), and (for synced cards) the GitHub issue closed in the same
  commit. An agent is NOT done until its card says so.
- **Commit discipline** — reference cards: `HUB-00N: <summary>`.
- **Issue routing** — board-only for small/single-session/low-risk cards;
  critical or cross-package cards get an issue in the repo where the work
  lands (this monorepo for hub scope, the package repo for package scope).

Test gates: run the surgically relevant suite for the package you touched by
default; run that package's FULL suite (and any dependent suites) for
significant changes (packaging/imports, cross-cutting refactors, scoring).
Suites run one package per pytest invocation — several packages ship a
top-level regular `tests` package and collide when batched. Docs currency:
when a change alters behavior described by `README.md`, `AGENTS.md`, or
`governance/TASKS.md`, update those files in the same commit.

## Sub-package sync

Every package mirrors an independent `Exios66/*` repo. `scripts/sync_packages.py`
(status / pull / push / snapshot, cursor in `scripts/packages_sync.json`)
reconciles the mirrors; the monorepo is the development source of truth.

## Workspace rules

- Member dependency lines keep their published git pins (release builds via
  plain `pip install .` depend on them). Dev redirection happens ONLY through
  `[tool.uv.sources]` tables — never delete a pin line to "fix" resolution.
- Bump a pin only when cutting a release of the pinned package (see
  `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py`, release-time only).
- Heavy assets (docs demos/screenshots, example PDFs, report archives) are
  pruned from this repo — keep them out; reference the upstream repos.
  EXCEPTION: the mailroom-corpus-eda EDA deliverables (`reports/figures/`,
  `reports/figures_interactive/`, `reports/tables/`, `SUMMARY_REPORT.*`) are
  tracked in full per human directive (HUB-008) — never prune them.
- Deploy configs (Dockerfile, nixpacks.toml, railway.json) inside each
  package are still standalone-repo aware; build images from the package
  directory as before.

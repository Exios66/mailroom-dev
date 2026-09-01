# mailroom-dev

The monorepo of the LLM-Mailroom project — a single checkout and a single
virtualenv for the whole constellation, so development never requires
importing across separate repositories.

```
                    ┌── corpus feeds (colocated data) ─────────────────────┐
                    │  Enron-Evaluation-Environment   claims-data-eda      │
                    │  mailroom-corpus-eda   (docclass-merged, P0–P6 EDA)  │
                    └──────────────────────────┬───────────────────────────┘
                                               ▼
                    ┌── prompt-experiment loop ────────────────────────────┐
                    │  llm-entity-extraction        (GEPA prompt versions) │
                    └──────────────────────────┬───────────────────────────┘
                                               ▼
┌────────────────────────┐        ┌───────────────────────────────────────┐
│  llm-dojo-scoring      │◀───────│           llm-mailroom                │
│  shared scoring engine │ import │  LangGraph multi-agent pipeline       │
└────────────────────────┘        └──────────────────┬────────────────────┘
                                                     ▼
                    ┌── surfaces ──────────────────────────────────────────┐
                    │  The-Mailroom (visualizer)     agent-mailroom        │
                    │  local-mailroom-sandbox        llm-mailroom-graph    │
                    └──────────────────────────┬───────────────────────────┘
                                               ▼
                    ┌──────────────────────────────────────────────────────┐
                    │              mailroom-dev — this monorepo            │
                    │        (central truth; every box lives in it)        │
                    └──────────────────────────────────────────────────────┘
```

### Architecture map — every repository, with links

All ten packages live in this monorepo (`packages/`) as git subtrees and
mirror independent `Exios66/*` repositories that remain standalone and
operational. GitHub Pages sites exist for three of them.

| Layer | Repository | GitHub Pages |
|---|---|---|
| Hub (central truth, this repo) | [`Exios66/mailroom-dev`](https://github.com/Exios66/mailroom-dev) | — |
| Corpus feed | [`Exios66/Enron-Evaluation-Environment`](https://github.com/Exios66/Enron-Evaluation-Environment) | — |
| Corpus feed | [`Exios66/claims-data-eda`](https://github.com/Exios66/claims-data-eda) | — |
| Corpus EDA + HF upload helpers | [`Exios66/Mailroom-Corpus-EDA`](https://github.com/Exios66/Mailroom-Corpus-EDA) | — |
| Prompt-experiment loop | [`Exios66/llm-entity-extraction`](https://github.com/Exios66/llm-entity-extraction) | [exios66.github.io/llm-entity-extraction](https://exios66.github.io/llm-entity-extraction/) |
| Shared scoring engine | [`Exios66/llm-dojo-scoring`](https://github.com/Exios66/llm-dojo-scoring) | — |
| LangGraph pipeline | [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) | — |
| Pixel-art visualizer console | [`Exios66/The-Mailroom`](https://github.com/Exios66/The-Mailroom) | [exios66.github.io/The-Mailroom](https://exios66.github.io/The-Mailroom/) |
| Walking-office-floor mailroom | [`Exios66/agent-mailroom`](https://github.com/Exios66/agent-mailroom) | — |
| Local-first LLM sandbox | [`Exios66/local-mailroom-sandbox`](https://github.com/Exios66/local-mailroom-sandbox) | — |
| Derived knowledge-graph site | [`Exios66/llm-mailroom-graph`](https://github.com/Exios66/llm-mailroom-graph) | [exios66.github.io/llm-mailroom-graph](https://exios66.github.io/llm-mailroom-graph/) |

## Repository structure

```
mailroom-dev/
├── AGENTS.md                    # workspace conventions (read before editing)
├── README.md
├── pyproject.toml               # uv workspace root: dev group, tool.uv.sources
├── uv.lock                      # single lockfile for the whole workspace
├── .gitignore
├── governance/
│   └── TASKS.md                 # task board: assigned / in_progress / needs_attention / done
├── docs/
│   └── wiki/                    # version-controlled GitHub wiki source (sync-wiki.sh)
├── scripts/
│   ├── packages_sync.json       # per-package sync cursor (issue #2)
│   ├── sync_packages.py         # sub-package <-> standalone-repo sync driver
│   ├── board_state.py           # live-state tracker for governance/TASKS.md (HUB-014)
│   ├── github_labels.py         # label taxonomy sync/audit (.github/labels.json)
│   └── board_config.json        # Projects v2 mirror config (written by project-init)
├── .github/
│   ├── ISSUE_TEMPLATE/          # YAML forms: board card, bug, feature, task/TODO
│   ├── PULL_REQUEST_TEMPLATE/   # PR form enforcing the hub board discipline
│   ├── labels.json              # declarative label taxonomy (stages/domains/types)
│   └── workflows/
│       └── board-governance.yml # CI gate: board invariants + label drift
└── packages/                    # one directory per standalone repo (git subtree)
    ├── Enron-Evaluation-Environment/   # virtual member (no build)
    ├── The-Mailroom/
    ├── agent-mailroom/
    ├── claims-data-eda/                # virtual member (no build)
    ├── llm-dojo-scoring/
    ├── llm-entity-extraction/
    ├── llm-mailroom/
    ├── llm-mailroom-graph/             # virtual member (no build)
    ├── local-mailroom-sandbox/
    └── mailroom-corpus-eda/            # virtual member (no build)
```

Each package keeps its own history (merged via `git subtree`), pyproject,
AGENTS.md, docs, tests, and deploy configs. Package-level documentation lives
inside each package directory; the root `pyproject.toml` wires the workspace
(dev group + `[tool.uv.sources]`) and `uv.lock` pins one resolution.

## Packages

| Path | Package (dist name) | Standalone mirror | Role |
|---|---|---|---|
| `packages/llm-dojo-scoring` | `llm-dojo-scoring` | [`Exios66/llm-dojo-scoring`](https://github.com/Exios66/llm-dojo-scoring) | Deterministic scoring, error-analysis, visualization, interpretation suite |
| `packages/llm-mailroom` | `mailroom` | [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) | LangGraph multi-agent legal-document pipeline (FastAPI producer) |
| `packages/llm-entity-extraction` | `llm-entity-extraction` | [`Exios66/llm-entity-extraction`](https://github.com/Exios66/llm-entity-extraction) | Prompt-experiment loop: prompt versions × models over CUAD/LegalBench/MAUD corpora |
| `packages/The-Mailroom` | `the-mailroom` | [`Exios66/The-Mailroom`](https://github.com/Exios66/The-Mailroom) | Pixel-art visualizer console + hosted Observatory (Langfuse as source of truth) |
| `packages/agent-mailroom` | `agent-mailroom` | [`Exios66/agent-mailroom`](https://github.com/Exios66/agent-mailroom) | Self-contained mailroom: one state machine per document, specialist agents at desks |
| `packages/local-mailroom-sandbox` | `mailroom-sandbox` | [`Exios66/local-mailroom-sandbox`](https://github.com/Exios66/local-mailroom-sandbox) | Local-first experiment sandbox (Ollama, vLLM, llama.cpp) |
| `packages/Enron-Evaluation-Environment` | (virtual) | [`Exios66/Enron-Evaluation-Environment`](https://github.com/Exios66/Enron-Evaluation-Environment) | Enron corpus EDA → pipeline-ready correspondence dataset |
| `packages/claims-data-eda` | (virtual) | [`Exios66/claims-data-eda`](https://github.com/Exios66/claims-data-eda) | CMS DE-SynPUF EDA → pipeline-ready insurance_claim dataset |
| `packages/llm-mailroom-graph` | (virtual) | [`Exios66/llm-mailroom-graph`](https://github.com/Exios66/llm-mailroom-graph) | Derived graphify knowledge-graph site of llm-mailroom |
| `packages/mailroom-corpus-eda` | (virtual) | [`Exios66/Mailroom-Corpus-EDA`](https://github.com/Exios66/Mailroom-Corpus-EDA) | docclass-merged corpus EDA (P0–P6) + centralized HF upload helpers (`hf_interface`, `dataset_export`, `docclass_uploader`, `intent_backfill`) |

Virtual members have no build system (`package = false`) and are not installed;
they exist so their data/code stays colocated in the single checkout.

## Development

One workspace, one lockfile, one virtualenv:

```bash
uv sync                 # create .venv and install every workspace member editable
uv run pytest ...       # any command resolves against the shared venv
```

Cross-package dependencies resolve to **workspace sources** during development
(`[tool.uv.sources]` in each member pyproject) — edit
`packages/llm-dojo-scoring` and the pipeline/eval loop pick the change up
live. The published git pins stay in the dependency lines for release builds,
so `pip install .` inside a package directory (Docker, Railway, Spaces) keeps
working exactly as before.

**Workspace rules** (see `AGENTS.md` for the full list):

- Member dependency lines keep their published git pins; dev redirection
  happens ONLY through `[tool.uv.sources]` tables — never delete a pin line to
  "fix" resolution.
- Bump a pin only when cutting a release of the pinned package.

**Task board**: `governance/TASKS.md` tracks what is assigned, in progress,
needs attention, and done across all agents and contributors — read it before
picking up work and keep your card current while you work (protocol in
`AGENTS.md §Governance`).

### Per-package test suites

```bash
uv run pytest packages/llm-dojo-scoring/tests
uv run pytest packages/llm-mailroom/src/tests
uv run pytest packages/llm-entity-extraction/tests
uv run pytest packages/The-Mailroom/tests
uv run pytest packages/agent-mailroom/tests
uv run pytest packages/local-mailroom-sandbox/tests
uv run pytest packages/claims-data-eda/tests
uv run pytest packages/Enron-Evaluation-Environment/tests
```

`llm-mailroom-graph` and `mailroom-corpus-eda` ship no test suite — the graph
site is a static build and the corpus EDA is verified behaviorally via
`packages/mailroom-corpus-eda/run_all.py` (P0–P6, incl. the issue #5
correspondence intent-coverage audit).

Some suites need credentials (Langfuse/Braintrust/HF) or network access and
will skip without them. Heavy assets (sample PDFs, Posit-site builds, the
append-only experiment log) are pruned from this repo; the affected tests
carry explicit skip guards and are marked "pruned heavy asset". The
mailroom-corpus-eda EDA deliverables — the interactive Plotly HTML figures
(`reports/figures_interactive/`) and the static figures/tables —
are tracked in full per human directive (HUB-008); they remain regenerable
via `run_all.py --phases P4` (regenerated bytes are scratch — the committed
files are canonical upstream).

## Sub-package sync (issue #2)

Every package mirrors an independent `Exios66/*` repository. The monorepo is
the development source of truth; `scripts/sync_packages.py` keeps the mirrors
reconciled. Per-package sync cursors live in `scripts/packages_sync.json`
(baseline 2026-08-30 19:06 CST per issue #2, advanced per-package since —
`status` reports live drift).

```bash
python scripts/sync_packages.py status              # drift report (fetches upstreams)
python scripts/sync_packages.py pull  --all         # import upstream commits (subtree pull)
python scripts/sync_packages.py push --package llm-mailroom   # publish back upstream
python scripts/sync_packages.py snapshot            # re-baseline the cursor
```

`pull`/`push` refuse to run on a dirty worktree (`--allow-dirty` overrides);
`pull --squash` keeps upstream history out of the monorepo log. `status
--json` emits machine-readable drift rows for CI.

## GitHub governance tooling (HUB-014)

The board and its GitHub surface stay machine-readable and mutually
consistent:

- **Issue templates** (`.github/ISSUE_TEMPLATE/`): a *Board card (HUB-0NN)*
  form for synced cards (one card = one issue), plus bug / feature / TODO
  forms — each pre-labelled from the taxonomy in `.github/labels.json`
  (`stage/*` lane mirrors, `attention/*` tags, `type/*`, `priority/*`,
  `domain/*` per package, `kanban` marker). The PR template
  (`.github/PULL_REQUEST_TEMPLATE/`) enforces the board discipline (card
  reference, board-before-code, `HUB-0NN:` commits, test gates, docs
  currency).
- **Board state tracker** — `scripts/board_state.py` reads the LIVE state of
  `governance/TASKS.md` (open table + archive), validates the board's own
  laws, and mirrors lane state onto GitHub:

  ```bash
  python scripts/board_state.py status                # snapshot (add --json for machine-readable)
  python scripts/board_state.py card HUB-014          # one card + commits referencing it
  python scripts/board_state.py check                 # invariants; exit 1 on structural errors
  python scripts/board_state.py check --with-issues   # + verify synced issues/labels via gh
  python scripts/board_state.py sync-issues --apply   # push board-derived labels onto issues
  python scripts/board_state.py project-init          # one-time Projects v2 mirror setup
  python scripts/board_state.py project-sync --apply  # mirror the open table into the project
  ```

  `check` errors are structural contradictions (duplicate IDs, invalid lanes,
  malformed issue links, missing `needs:`/`review:`/`decision:` tags, phantom
  commit references); hygiene drift (pending-archive rows, unclaimed cards
  with commits, stale `in_progress`) is reported as warnings. CI runs
  `check` + the label audit on every change to `governance/`, `scripts/`,
  or `.github/` (`.github/workflows/board-governance.yml`).
- **Label taxonomy** — `.github/labels.json` is the source of truth;
  `python scripts/github_labels.py sync` creates/updates the repo labels,
  `audit` reports drift (exit 1 when manifest labels are missing).

The Projects v2 mirror (the `mailroom-hub board` project, with
Lane/Owner/Card fields) needs a one-time interactive scope grant:
`gh auth refresh -s read:project`, then `project-init` + `project-sync`.

**Wiki**: the [GitHub wiki](https://github.com/Exios66/mailroom-dev/wiki)
is mirrored from the version-controlled source in `docs/wiki/` (Home,
Getting-Started, Architecture, Board-Governance, Sub-Package-Sync,
HF-Corpus, Offline-Sandbox, Releases, FAQ + sidebar). After editing pages:
`./docs/wiki/sync-wiki.sh` (or `--check` for drift). First-time setup is a
one-time UI action — create any page on the wiki once so GitHub
materializes the `.wiki.git` repo, then the sync pushes the full content.

## Release flow

The monorepo is the development source of truth. Upstream repositories remain
the release vehicles for the deployed surfaces (Hugging Face Spaces, Railway):
cut releases there as today, and the git pins in the member pyprojects keep
deploy builds reproducible. Propagate monorepo changes upstream with
`python scripts/sync_packages.py push` (a `git subtree push` per package) when
a release is cut, then bump the pins (see
`packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo pin).

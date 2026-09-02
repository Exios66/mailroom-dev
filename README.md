# mailroom-dev

The monorepo of the LLM-Mailroom project — a single checkout and a single
virtualenv for the whole constellation, so development never requires
importing across separate repositories.

> **Canonical architecture & taxonomy:** See the [canonical Mailroom pipeline](docs/assets/mailroom-pipeline.svg) and the [v7 taxonomy specification](docs/v7-taxonomy.md). These are the root-level sources of truth for the pipeline visualization and v7 terminology.

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
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── governance/
├── docs/
│   ├── v7-taxonomy.md              # canonical v7 corpus/live-taxonomy terminology
│   ├── assets/
│   │   └── mailroom-pipeline.svg   # canonical 13-node pipeline visualization
│   └── wiki/
├── scripts/
└── packages/
```

The root documentation above is intentionally canonical: package-level
implementation details remain inside their respective package directories,
while cross-package architecture and corpus terminology are maintained here.

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
uv sync
uv run pytest ...
```

Cross-package dependencies resolve to **workspace sources** during development
(`[tool.uv.sources]` in each member pyproject); published git pins remain in
dependency lines for release builds.

See `AGENTS.md` for workspace rules and `governance/TASKS.md` for the task board.

## Sub-package sync (issue #2)

Every package mirrors an independent `Exios66/*` repository. The monorepo is
the development source of truth; `scripts/sync_packages.py` keeps the mirrors
reconciled.

```bash
python scripts/sync_packages.py status
python scripts/sync_packages.py pull --all
python scripts/sync_packages.py push --package llm-mailroom
python scripts/sync_packages.py snapshot
```

## GitHub governance tooling (HUB-014)

The board and GitHub surface are kept machine-readable and mutually
consistent. See `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE/`,
`.github/labels.json`, `scripts/board_state.py`, and `governance/TASKS.md`.

## Wiki

The [GitHub wiki](https://github.com/Exios66/mailroom-dev/wiki) is mirrored from
`docs/wiki/`.

## Release flow

The monorepo is the development source of truth. Upstream repositories remain
the release vehicles for deployed surfaces; propagate package changes with
`scripts/sync_packages.py push` when a release is cut, then bump published pins
as required.

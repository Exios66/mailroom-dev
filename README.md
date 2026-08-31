# mailroom-hub

The monorepo of the LLM-Mailroom project — a single checkout and a single
virtualenv for the whole constellation, so development never requires
importing across separate repositories.

```
                        ┌──────────────────────────────┐
                        │   llm-entity-extraction      │
                        │   prompt-experiment loop     │
                        └──────────┬───────────────────┘
                                    ▼
┌────────────────────────┐   ┌──────────────────────────────┐
│  llm-dojo-scoring      │◀──│        llm-mailroom          │
│  scoring engine        │   │  (the pipeline)              │
└────────────────────────┘   └──────────┬───────────────────┘
                                        ▼
                          ┌──────────────────────────────┐
                          │        The-Mailroom          │
                          │   pixel-art visual engine    │
                          └──────────────────────────────┘
```

## Repository structure

```
mailroom-dev/
├── AGENTS.md                    # workspace conventions (read before editing)
├── README.md
├── pyproject.toml               # uv workspace root: dev group, tool.uv.sources
├── uv.lock                      # single lockfile for the whole workspace
├── .gitignore
├── scripts/
│   ├── packages_sync.json       # per-package sync cursor (issue #2)
│   └── sync_packages.py         # sub-package <-> standalone-repo sync driver
└── packages/                    # one directory per standalone repo (git subtree)
    ├── Enron-Evaluation-Environment/   # virtual member (no build)
    ├── The-Mailroom/
    ├── agent-mailroom/
    ├── claims-data-eda/                # virtual member (no build)
    ├── llm-dojo-scoring/
    ├── llm-entity-extraction/
    ├── llm-mailroom/
    ├── llm-mailroom-graph/             # virtual member (no build)
    └── local-mailroom-sandbox/
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

Virtual members have no build system (`package = false`) and are not installed;
they exist so their data/code stays colocated in the single checkout.

## Development

One workspace, one lockfile, one virtualenv:

```bash
uv sync                 # create .venv and install every workspace member editable
uv run pytest           # ad-hoc commands resolve against the shared venv
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

### Per-package test suites

```bash
uv run pytest packages/llm-dojo-scoring/tests
uv run pytest packages/llm-mailroom/src/tests
uv run pytest packages/llm-entity-extraction/tests
uv run pytest packages/The-Mailroom/tests
uv run pytest packages/agent-mailroom/tests
uv run pytest packages/local-mailroom-sandbox/tests
uv run pytest packages/claims-data-eda/tests
```

Some suites need credentials (Langfuse/Braintrust/HF) or network access and
will skip without them. Heavy assets (sample PDFs, Posit-site builds, the
append-only experiment log) are pruned from this repo; the affected tests
carry explicit skip guards and are marked "pruned heavy asset".

## Sub-package sync (issue #2)

Every package mirrors an independent `Exios66/*` repository. The monorepo is
the development source of truth; `scripts/sync_packages.py` keeps the mirrors
reconciled. A baseline cursor lives in `scripts/packages_sync.json` — the
monorepo is aligned with the standalone repos as of **2026-08-30 19:06 CST**.

```bash
python scripts/sync_packages.py status              # drift report (fetches upstreams)
python scripts/sync_packages.py pull  --all         # import upstream commits (subtree pull)
python scripts/sync_packages.py push --package llm-mailroom   # publish back upstream
python scripts/sync_packages.py snapshot            # re-baseline the cursor
```

`pull`/`push` refuse to run on a dirty worktree (`--allow-dirty` overrides);
`pull --squash` keeps upstream history out of the monorepo log. `status
--json` emits machine-readable drift rows for CI.

## Release flow

The monorepo is the development source of truth. Upstream repositories remain
the release vehicles for the deployed surfaces (Hugging Face Spaces, Railway):
cut releases there as today, and the git pins in the member pyprojects keep
deploy builds reproducible. Propagate monorepo changes upstream with
`python scripts/sync_packages.py push` (a `git subtree push` per package) when
a release is cut, then bump the pins (see
`packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo pin).

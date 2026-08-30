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

## Layout

| Path | Package (dist name) | Role |
|---|---|---|
| `packages/llm-dojo-scoring` | `llm-dojo-scoring` | Deterministic scoring, error-analysis, visualization, interpretation suite |
| `packages/llm-mailroom` | `mailroom` | LangGraph multi-agent legal-document pipeline (FastAPI producer) |
| `packages/llm-entity-extraction` | `llm-entity-extraction` | Prompt-experiment loop: prompt versions × models over CUAD/LegalBench/MAUD corpora |
| `packages/The-Mailroom` | `the-mailroom` | Pixel-art visualizer console + hosted Observatory (Langfuse as source of truth) |
| `packages/agent-mailroom` | `agent-mailroom` | Self-contained mailroom: one state machine per document, specialist agents at desks |
| `packages/local-mailroom-sandbox` | `mailroom-sandbox` | Local-first experiment sandbox (Ollama, vLLM, llama.cpp) |
| `packages/Enron-Evaluation-Environment` | (virtual) | Enron corpus EDA → pipeline-ready correspondence dataset |
| `packages/claims-data-eda` | (virtual) | CMS DE-SynPUF EDA → pipeline-ready insurance_claim dataset |
| `packages/llm-mailroom-graph` | (virtual) | Derived graphify knowledge-graph site of llm-mailroom |

Each package keeps its own history (merged via `git subtree`), pyproject,
AGENTS.md, docs, tests, and deploy configs. Package-level documentation lives
inside each package directory.

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

### Per-package commands

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
will skip or fail without them.

## Release flow

The monorepo is the development source of truth. Upstream repositories
(`Exios66/llm-dojo-scoring`, `Exios66/llm-mailroom`, …) remain the release
vehicles for the deployed surfaces (Hugging Face Spaces, Railway): cut
releases there as today, and the git pins in the member pyprojects keep
deploy builds reproducible. Changes propagate upstream via
`git subtree split` / cherry-picks when a release is cut.

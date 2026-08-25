# The-Mailroom

![version](https://img.shields.io/badge/version-0.2.0-blue)
[![release](https://img.shields.io/badge/release-v0.2.0-blue)](https://github.com/Exios66/The-Mailroom/releases/tag/v0.2.0)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![data source](https://img.shields.io/badge/data%20source-Langfuse%20only-6C5CE7)

**Pixel-art visual engine for the [`llm-mailroom`](https://github.com/Exios66/llm-mailroom)
multi-agent legal-document pipeline.** The Mailroom renders every pipeline run as an
animated conveyor of document envelopes — sorter, specialist bays, the boss's desk,
the reporter, the archive — driven entirely by **Langfuse traces**. Langfuse is the
sole source of truth: every envelope, badge, verdict, and metric on screen is derived
from the pipeline's Langfuse project. Nothing is fabricated, nothing falls back to
local data.

---

## The governed constellation

The-Mailroom is one node of a governed family of repositories sharing one kanban
board, one discussion log, and one trace contract:

```
        ┌─────────────────────────┐         ┌─────────────────────────┐
        │  llm-entity-extraction  │ breeds  │      llm-mailroom       │
        │  prompt-experiment loop │ ──────▶ │   the document pipeline  │
        └─────────────────────────┘         └────────────┬────────────┘
                                                         │ Langfuse traces (US cloud)
                                                         ▼
                                        ┌──────────────────────────────┐
                             YOU ARE    │         THE-MAILROOM         │
                               HERE ▶   │    pixel-art visual engine   │
                                        └──────────────────────────────┘
```

| Repository | Role | Relationship to The-Mailroom |
|---|---|---|
| [llm-mailroom](https://github.com/Exios66/llm-mailroom) | LangGraph state machine processing legal documents through specialist LLM agents (classify → extract → report → archive) | **Upstream** — its Langfuse project is this visualizer's sole data source |
| [llm-entity-extraction](https://github.com/Exios66/llm-entity-extraction) | Prompt-experiment loop (prompt versions × models, paired-bootstrap ablations) | Breeds the pipeline's sorter/specialist prompts; hosts the shared kanban board + governance log for the whole chain |
| [llm-dojo-scoring](https://github.com/Exios66/llm-dojo-scoring) | Deterministic, field-type-aware scoring engine (`@v0.7.0`) | Upstream governed dependency of both pipeline repos |
| [Enron-Evaluation-Environment](https://github.com/Exios66/Enron-Evaluation-Environment) | EDA + pipeline-ready correspondence dataset (CMU Enron corpus) | Corpus feed for the pipeline's `correspondence` doc class |
| [claims-data-eda](https://github.com/Exios66/claims-data-eda) | Insurance-claims candidate-corpus EDA (CMS DE-SynPUF direction) | Candidate corpus feed for the `insurance_claim` doc class |
| [atticus-investigation](https://github.com/Exios66/atticus-investigation) | LegalBench classification prompt-engineering pipeline | Eval sibling — same methodology family, LegalBench focus |
| [llm-mailroom-graph](https://exios66.github.io/llm-mailroom-graph/) · [llm-entity-extraction-graph](https://exios66.github.io/llm-entity-extraction-graph/) | Interactive graphify knowledge graphs | Derived sites mapping the pipeline's and the loop's code structure |

Full relationship map: [`llm-mailroom/docs/sister-repos.md`](https://github.com/Exios66/llm-mailroom/blob/main/docs/sister-repos.md).

---

## Quick start

```bash
pip install -e ".[dev]"
cp .env.example .env      # add LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY
mailroom-web              # → http://127.0.0.1:8001  (pixel-art console)
                          #    Observatory is also at /live on the same server
mailroom-hosted           # → public Observatory on 0.0.0.0 (container-ready)
mailroom-tui              # AgentLab-style live console (same data, in a terminal)
```

## What you see

- **FLOOR** — the mailroom: a conveyor belt carrying document envelopes
  through the pipeline's seven stations (SORTER · EXTRACT · JUDGE · BOSS ·
  REPORT · ARCHIVE, plus the human-review siding) grouped into three rooms
  (Intake & Sort · Extraction & Adjudication · Reporting & Archive). The
  JUDGE station is the KANBAN-063 quality gate (`judge_verify` +
  `arbitrate-verdict`). Click an envelope for its full run.
- **REVIEW** — the review siding as a queue: every run waiting on a human,
  with its escalation reason and confidence, one click from its inspector.
- **INSPECTOR** — drill-down into any trace: node-span timeline, LLM
  generations (model, tokens, latency, cost), confidence and judge scores.
- **SESSIONS** — matter explorer grouped by Langfuse session.
- **METRICS** — docs processed, archived/review/failed, cost, tokens, p95
  generation latency, judge-verdict mix, per-doc-type counts.
- **CONSOLE** — a live scrolling log of the pipeline, AgentLaboratory-style.
- **OBSERVATORY** (`/live`, `mailroom-hosted`) — the **hosted** edition: a
  modern, accessible public desk (semantic HTML, keyboard views `1`–`6`,
  native inspect dialog, paced replay, Debug desk). Same live traces and replay as the
  console; different surface, different URL. Not GitHub Pages.
- **TUI** (`mailroom-tui`) — the same pipeline in a terminal: per-doc tables,
  `*** Beginning station: ... ***` banners as runs arrive and advance, judge
  verdict banners, review siding, metrics, and full trace inspection. It
  subscribes to the same WebSocket floor snapshots as the web UI (`--once`
  renders a single frame for scripting).

## Screenshots

Official captures of **v0.2.0** — real UI/TUI pixels rendered from genuine
pipeline traces (fixture-seeded exactly like the test suite; Langfuse remains
the sole display source):

| | |
|---|---|
| ![The Mailroom floor — conveyor, stations, envelopes](docs/screenshots/floor.png) |
| **FLOOR** — the animated conveyor: seven stations, per-doc-type envelope tints, verdict stamps, review siding & failed bin. |
| ![REVIEW siding — human-review queue](docs/screenshots/review.png) |
| **REVIEW** — runs waiting on a human, with escalation reasons and confidence. |
| ![METRICS dashboard](docs/screenshots/metrics.png) |
| **METRICS** — docs processed, archived/review/failed split, cost, tokens, judge-verdict mix, per-doc-type counts. |
| ![TUI console](docs/screenshots/tui-console.png) |
| **TUI** (`mailroom-tui --once`) — the same pipeline in a terminal: per-doc table, verdicts, station banners, live log. |

---

## Demo data (play-testing without a live run)

Demo runs are seeded **into** Langfuse (env `demo`) — the visualizer still
reads Langfuse only, so nothing on screen is ever canned data:

<details>
<summary>Demo seeding commands (click to expand)</summary>

```bash
python scripts/seed_demo.py                       # seed 13 demo runs (incl.
                                                  # judge-gate + arbiter paths)
python scripts/seed_demo.py --list-scenarios      # what the demo set covers
python scripts/seed_demo.py --check --check-api   # verify seeded runs against
                                                  # stored Langfuse logs AND the
                                                  # running server's display API
python scripts/seed_demo.py --check-logs <dir>    # verify against run logs saved
                                                  # by llm-mailroom's
                                                  # scripts/sync_langfuse_logs.py
```

</details>

## Requirements

- Python 3.11+
- A Langfuse project (the `llm-mailroom` project on US cloud by default)
  with project-scoped API keys in `.env`
- The sister pipeline repo `../llm-mailroom` (optional — only needed to use
  the `MAILROOM_TAXONOMY` live-config override; see `AGENTS.md`)
- `arize-phoenix-client` (optional — only for the Phoenix trace source)

## Hosted Observatory (public URL — not GitHub Pages)

The Observatory is a **separate live site** meant to be deployed to a real
host (Hugging Face Spaces, Fly, Render, Cloud Run, a VPS). It is not the
Pages snapshot and not the pixel-art console.

```bash
mailroom-hosted                          # 0.0.0.0:8001  →  / and /live
docker build -t mailroom-observatory .
docker run --rm -p 7860:7860 --env-file .env mailroom-observatory
```

Full deploy notes (Spaces secrets, keyboard map, how it differs from the
other surfaces): [`hosted/README.md`](hosted/README.md).

## GitHub Pages edition (static site + local Phoenix)

The Mailroom also runs as a **static site on GitHub Pages** with three data
modes:

```bash
# one-time: Settings → Pages → Source: "Deploy from a branch" → gh-pages /docs
scripts/publish_pages.sh                          # build site/ + push gh-pages docs/
scripts/publish_pages.sh --source both            # Langfuse + Phoenix snapshot
scripts/publish_pages.sh --dry-run                # build + verify, don't push
scripts/publish_pages.sh --status                 # is the live site in sync with HEAD?
```

**Keeping main and gh-pages in sync** (no Actions): enable the committed
pre-push hook once per clone — `git config core.hooksPath hooks` — and every
push of `main` republishes `gh-pages:/docs` automatically. A failed
republish (e.g. a Langfuse hiccup) warns without blocking the code push;
set `MAILROOM_STRICT_SYNC=1` to make failures block instead.
`scripts/publish_pages.sh --status` reports drift any time (exit 1 = stale).
The publisher must run from `main` — it refuses cleanly if another branch
(e.g. `gh-pages` in GitHub Desktop) is checked out.

The publisher needs no GitHub Actions (deliberately — it uses Pages' native
deploy-from-branch mode): it stages `web/` with relative asset paths, exports
a JSON snapshot of the configured trace source, verifies it, and pushes the
site into `docs/` on the `gh-pages` branch (anything else on that branch's
root is left untouched). Re-run any time to refresh the snapshot.

1. **Snapshot mode** — a build-time JSON export of the configured trace
   source is bundled into the site (`data/*.json`). Works with zero backend,
   zero secrets in the browser; the lamp shows `SOURCE: SNAPSHOT`. Published
   locally by `scripts/publish_pages.sh` (no GitHub Actions required) from
   Langfuse repo secrets or a local Phoenix — without a reachable source the
   site ships empty and shows its honest CLOSED state.
2. **Live mode** — point the static page at any reachable Mailroom API:
   append `?api=http://localhost:8001` once (persisted to `localStorage`).
   Run the server locally with CORS enabled (`MAILROOM_CORS_ORIGINS`) and
   the Pages UI goes fully live, WS included. Note: Chrome/Firefox allow
   HTTPS→`http://localhost` calls; Safari may block them.
3. **Phoenix mode** — traces from a *locally running* Arize Phoenix
   (default `http://localhost:6006`) can drive the console:

   ```bash
   pip install arize-phoenix-client
   # start Phoenix (e.g. `phoenix serve`) and point your pipeline's OTLP
   # exporter at it, then:
   MAILROOM_SOURCE=phoenix mailroom-web     # or MAILROOM_SOURCE=both for Langfuse + Phoenix
   ```

   Phoenix spans are mapped into the llm-mailroom display contract:
   verb-first span names route through the stage map, LLM spans become
   generations (model/tokens/cost), annotations become scores. Unmapped
   spans degrade to unknown staging — same visible-by-design breakage map.

**Debug console for agents:** every fetch, WS frame, error, and console line
lands in a client-side ring buffer at `window.__MAILROOM_DEBUG__`
(`dump()`, clipboard copy, `export()` → `mailroom-debug.json`); `?debug=1`
or the CONSOLE tab's DEBUG toggle enables verbose capture. The hosted
Observatory has a parallel suite: `window.__OBSERVATORY_DEBUG__`, Debug desk
`#debug` (`?debug=1`), `GET /api/debug/bundle` (health + source + server
ring + last client dumps), and `POST /api/debug/client`. Server side,
`GET /api/debug/logs?limit=` serves an always-on request ring buffer,
`GET /api/debug/source` reports configured sources/knobs, `MAILROOM_DEBUG=1`
turns on verbose stdout logging, and `/api/meta` carries a machine-readable
endpoint index plus active sources and version. Snapshot builds add
`debug/build-info.json` (git SHA, counts, generation time).

## Configuration

<details>
<summary>Configuration reference (click to expand)</summary>

All knobs live in `.env` (see `.env.example`): Langfuse keys/host
(`LANGFUSE_HOST`, default `https://us.cloud.langfuse.com`), poll cadence
(`MAILROOM_POLL_INTERVAL`), recent window, trace limit, optional tag/env
filters, `MAILROOM_PORT` (default `8001`), and `MAILROOM_TAXONOMY`. The GH
Pages edition adds `MAILROOM_SOURCE` (`langfuse|phoenix|both`),
`PHOENIX_ENDPOINT` / `PHOENIX_API_KEY` / `MAILROOM_PHOENIX_PROJECT`,
`MAILROOM_CORS_ORIGINS`, and `MAILROOM_DEBUG`.

> [!IMPORTANT]
> `pipeline_schema.py` is cached at process level — editing `taxonomy.yaml`
> (or pointing `MAILROOM_TAXONOMY` at the pipeline's copy) requires a server
> restart to take effect.

</details>

---

## The trace contract & the mirror duty

The-Mailroom does not own the trace contract it renders — it **mirrors** it
from the upstream pipeline. This is the repo's #1 maintenance duty: when
`llm-mailroom` changes span names, node order, the agent roster (15 agents),
doc classes (7 classes), confidence thresholds, or judge score names
(`mailroom-pipeline-judge`, `mailroom-pipeline-quality`), this repo must
update `mailroom_ui/pipeline_schema.py` and `mailroom_ui/trace_interpreter.py`
in the same change window.

Until mirrored, breakage is visible by design: new spans render as an
`unknown` stage, new doc classes fall back to the gray default stamp color,
renamed judge scores vanish from runs. The full contract — span inventory,
score names, metadata/tags, and the complete breakage map — lives in
[`AGENTS.md`](AGENTS.md) ("Sister repo" section), which is authoritative for
pipeline internals alongside the pipeline's own `AGENTS.md`.

---

## Project layout

<details>
<summary>Directory map</summary>

```
mailroom_ui/   data core — Langfuse + Phoenix adapters, trace interpreter,
               topology mirror, models, metrics (reads trace sources only)
server/        FastAPI, read-only: /api/* + debug endpoints + WebSocket + serves web/
web/           pixel-art SPA (vanilla HTML/CSS/JS, no build step)
tui/           rich console — the pipeline in a terminal (mailroom-tui)
scripts/       seed_demo (demo runs INTO Langfuse) · export_snapshot (Pages
               data) · publish_pages (gh-pages push, no Actions) · release
docs/ + wiki/  mirrored documentation (wiki/sync-wiki.sh publishes the wiki)
tests/         pytest suite against fake clients — never the real APIs
```

</details>

## Tests

```bash
python -m pytest tests/ -q
```

Tests never hit real Langfuse — `tests/fake_langfuse.py` provides v2/v3
snake_case and v4 camelCase fixtures mirroring the trace contract.

## Releases

Semantic versioning with a Keep-a-Changelog `CHANGELOG.md`, README/wiki
updates on major changes, and annotated `vX.Y.Z` tags matching the changelog.
`python scripts/release.py --help` drives the mechanical steps. See
`AGENTS.md` → "Release process" for the full procedure.

---

## License & credits

Visual palette and character direction derived from the AgentLaboratory
project's artwork. Built for the `llm-mailroom` pipeline — see that repo and
its [sister-repos map](https://github.com/Exios66/llm-mailroom/blob/main/docs/sister-repos.md)
for the full governed constellation. No license published yet.

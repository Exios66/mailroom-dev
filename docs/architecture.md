# Architecture

> This file is mirrored at `wiki/Architecture.md` — edit both together (see
> `wiki/sync-wiki.sh`). This page describes the architecture of The-Mailroom,
> the visual engine for the `llm-mailroom` pipeline. For the pipeline's own
> architecture see the sister repo's docs (`../llm-mailroom`).

## Overview

The-Mailroom renders every run of the `llm-mailroom` multi-agent
legal-document pipeline from its Langfuse traces (pixel-art console, hosted
Observatory, and TUI).
**Langfuse is the sole source of truth**: no display value is ever fabricated
or served from local canned data. The repo is read-only against Langfuse
(project-scoped API keys, backend proxies everything — the browser never holds
keys).

```
┌────────────────────────── Langfuse (US cloud, project llm-mailroom) ──────┐
│  traces · observations (spans/generations) · scores · sessions            │
└────────────▲──────────────────────────────────────────────▲────────────────┘
             │ project-scoped API keys (read-only)          │
┌────────────┴──────────────── The-Mailroom ────────────────┴────────────────┐
│ mailroom_ui/  langfuse_source.py ← adapter (trace/observations/scores/     │
│               trace_interpreter.py ← sessions via SDK)                    │
│               pipeline_schema.py ← topology mirror (taxonomy.yaml)        │
│               metrics.py · models.py                                       │
│ server/  FastAPI → /api/* + /ws → serves web/ (console) and hosted/ (/live)│
│ web/     pixel-art SPA: Floor (conveyor, 7 stations incl. JUDGE) ·        │
│          Inspector · Sessions · History · Metrics · Review · Console      │
│ hosted/  Observatory — public modern accessible desk (live + replay)      │
│ tui/     rich-based console (mailroom-tui)                                 │
└────────────────────────────────────────────────────────────────────────────┘
```

## Data flow

1. `server/poller.py` `PollHub` polls `list_recent_runs()` every
   `MAILROOM_POLL_INTERVAL` seconds. `list_recent_runs` uses **trace-list
   responses only** ("light" runs) — cheap enough to poll continuously.
2. Each light run is interpreted by `trace_interpreter.interpret_trace` and
   compacted by `poller.floor_payload` (stage, doc type, confidences, verdict,
   cost, …).
3. Full drill-down (`/api/traces/{id}`) fetches observations + scores on
   demand via `LangfuseSource.get_run()`; `PollHub` keeps a small per-trace
   detail cache.
4. Snapshots are broadcast over WebSocket `/ws`; the SPA renders the floor,
   sessions, metrics, and console from the same payloads.

## Interpreting traces

A `document-pipeline` trace carries:

- **Trace fields**: `id` (deterministic, seeded from filename), `name`,
  `timestamp`, `latency`, `session_id` (= matter_id, or a run-scoped session
  for pilots), `environment`, `tags` (`[mailroom, <env>, run-<n>, ...]`),
  `metadata` (`{attempt, run_id, run_deadline}`), curated `input`/`output`.
- **Node spans**: verb-first names mapped to stages by
  `pipeline_schema.SPAN_STAGE_MAP` (`ingest-document`, `classify-document`,
  `judge-verify`, `arbitrate-verdict`, `extract-fields`, `route-for-review`,
  `adjudicate-conflict`, `compile-report`, `write-catalog`,
  `archive-document`, …). The KANBAN-063 quality gate: `judge-verify` runs on
  the ambiguous extraction band and a partial verdict detours through the
  arbiter before reporting.
- **Generations**: auto-traced LLM calls (model, usage, latency,
  `cost_details`).
- **Scores**: confidences, run metrics, judge verdict
  (`mailroom-pipeline-judge` CORRECT/PARTIAL/MISS) and quality
  (`mailroom-pipeline-quality` 0–1).

Because pilot/attempt re-runs reuse the deterministic trace id, a single
trace can carry several full runs. The interpreter clusters observations by
time gap (`RUN_GAP_S`) and keeps only the latest cluster — one envelope per
trace, showing the latest run.

## Pipeline topology mirror

`pipeline_schema.py` bundles a mirror of the pipeline's graph
(`src/graph/routing.py` + `src/config/taxonomy.yaml`): node/span names,
stage→phase mapping, node order, agent roster (15 agents), doc classes
(7, incl. `court_opinion` and `insurance_claim`), specialist dispatch, and
confidence thresholds (incl. `judge_band_high`). The `MAILROOM_TAXONOMY` env
var can point at the live
`taxonomy.yaml` so thresholds/doc classes come straight from the pipeline
config instead of the mirror (cached at process level — restart to reload).

When the pipeline changes (new span, doc class, score, tag, env), the mirror
must be updated in the same change — see the sync checklist in `AGENTS.md`.

## Web frontend

Vanilla HTML/CSS/JS served from `web/` (no build step). The floor is a
canvas-rendered conveyor (pixel-art envelopes tinted per doc class, stations,
rollers, review/failed sidings) — see `web/js/floor.js`. The station roster
and doc-class colors must stay aligned with `pipeline_schema.py` and the
pipeline's `taxonomy.yaml`.

## Hosted Observatory (`hosted/`)

A **separate** public UI at `/live` (`mailroom-hosted`, or `/` when
`MAILROOM_EDITION=hosted`). Editorial layout, semantic HTML, skip link,
keyboard view switching (`1`–`6`, including Debug), native `<dialog>`
inspector, paced replay of stored traces (controls stay pinned in a
sticky bar), and a Debug desk that records fetches, WebSocket frames, and
uncaught errors. Same `/api/*` + `/ws` as the pixel console. Deploy with
the root `Dockerfile` (binds `0.0.0.0:7860`) — this is not GitHub Pages.
See `hosted/README.md`.

## GH Pages edition (static site, no Actions)

GitHub Pages hosts a static build of the SPA via **deploy-from-branch**
(one-time UI toggle: Settings → Pages → `gh-pages` `/docs`) — deliberately
no GitHub Actions workflow. `scripts/publish_pages.sh` stages `web/`
(relative asset paths: `index.html` + `static/css|js`), writes `.nojekyll`,
runs `scripts/export_snapshot.py` to bundle `data/*.json` + per-run detail
files + `debug/build-info.json`, verifies with `--check`, and pushes the
`gh-pages` branch.

Data modes (resolved in `web/js/api.js`):

- **API base**: `?api=<url>` → `localStorage["mailroom.api"]` → same-origin.
  A Pages visitor can drive a locally running `mailroom-web` (CORS via
  `MAILROOM_CORS_ORIGINS`) including its WebSocket.
- **Snapshot fallback**: when no live API answers, the site serves bundled
  JSON (`SOURCE: SNAPSHOT`, gold lamp) — never the closed overlay unless
  even snapshots are missing.

Trace sources (server side): `MAILROOM_SOURCE=langfuse | phoenix | both`
selects between `LangfuseSource`, `PhoenixSource` (local Arize Phoenix via
`arize-phoenix-client`; OTel/OpenInference spans remapped into the
Langfuse-shaped dicts `interpret_trace` consumes; unmapped spans degrade to
unknown staging per the breakage map), and `MultiSource` (fan-out reads,
per-trace isolation, aggregated health).

Debug surfaces for agents: pixel-console ring at
`window.__MAILROOM_DEBUG__` (`dump()` / `export()`, enabled verbosely by
`?debug=1` or the CONSOLE tab's DEBUG toggle); Observatory ring at
`window.__OBSERVATORY_DEBUG__` (Debug desk `#debug`, same `?debug=1`);
server request ring at `/api/debug/logs?limit=`, source introspection at
`/api/debug/source`, combined pull at `/api/debug/bundle`, last browser
dumps at `GET|POST /api/debug/client`, verbose stdout via
`MAILROOM_DEBUG=1`, and a machine-readable endpoint index in `/api/meta`.
Snapshot builds add `debug/build-info.json`.

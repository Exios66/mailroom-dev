# AGENTS.md — The-Mailroom

The-Mailroom is the **visual engine** for the `llm-mailroom` multi-agent legal-document pipeline: a pixel-art console (web + planned TUI) that renders every run from its Langfuse traces. **Langfuse is the sole source of truth** — every displayed value is derived from Langfuse traces, observations, scores, and sessions. This repo never fabricates or falls back to locally-canned data. Python 3.11+, no build step.

## Skills (tool selection)

Committed under `.cursor/skills/`. **Read `mailroom-tool-router` first** for any
source, UI surface, poller, schema, Pages, or sister-repo serving task, then
open exactly one specialty skill. Companion to
[`local-mailroom-sandbox` PR #4](https://github.com/Exios66/local-mailroom-sandbox/pull/4)
(same family names, visualizer-scoped).

| Skill | Appropriate for |
| --- | --- |
| `mailroom-tool-router` | Choosing among the stacks below |
| `langfuse` | Default document display (SDK 2.50–4.x) |
| `apache-phoenix` | Optional `MAILROOM_SOURCE=phoenix\|both` |
| `braintrust` | Not a display source — do not add one |
| `huggingface` | Hub eval/pilot scripts; copied catalogs; no runtime dojo import |
| `ollama` | Local LLM lives in sandbox/pipeline, not here |
| `modal` | Remote GPU lives in sandbox/pipeline, not here |
| `pixel-console` | Vanilla `web/` SPA (no npm) |
| `observatory` | Hosted `/live` desk |
| `live-floor` | Poller, WS, watcher/inbox lamp |
| `pipeline-schema-sync` | Mirror `llm-mailroom` topology |
| `gh-pages` | Deploy-from-branch snapshot (no Actions) |
| `tui` | `mailroom-tui` (`MAILROOM_API_URL` → this visualizer; `--resolve` / `--source` via `/api/review/*`) |

## Sister repo: `llm-mailroom` (the pipeline)

- **Expected location**: a sibling of this repo, i.e. `../llm-mailroom` from this checkout (e.g. `/Users/luciusjmorningstar/Downloads/llm-mailroom`). It is **not currently present on this machine** — clone it before relying on `MAILROOM_TAXONOMY`.
- It is the **upstream**: The-Mailroom reads *its* Langfuse project (US cloud, project `llm-mailroom`). Its `AGENTS.md` is authoritative for pipeline internals; consult it whenever the pipeline's tracing contract is in doubt.
- **What we mirror from it, and must keep in sync (the #1 maintenance duty)** — when the pipeline changes, update all of these in one change:
  - `mailroom_ui/pipeline_schema.py` — mirrors `src/graph/routing.py` + `src/config/taxonomy.yaml` + `src/observability/tracing.py`: node/span names (`SPAN_STAGE_MAP` incl. `normalize-intake`), **`NODE_OBSERVATION_TYPES`** (chain/agent/evaluator/retriever/generation/span), stage→phase map, node order, agent roster (incl. `intake`, `sorter_reviewer`, `arbiter`, `judge`, `compliance_specialist`, `insurance_claims_specialist`), live `DOC_CLASSES` (5 extract classes + `merger_agreement` display/HF alias + `unknown` routing token; retired `court_opinion` / `due_diligence` stay off the roster), Hub `DOC_SUBCLASS_BY_CLASS` + CUAD `CONTRACT_SUBTYPE_KEYS`, Langfuse score aliases (`extraction_verified_precision`), `SUITE_EXTRA_SCORES` (Enron/MAUD), `SPECIALIST_BY_DOC_CLASS`, confidence thresholds (+ `judge_band_high`).
  - `mailroom_ui/trace_interpreter.py` — maps its span names, Langfuse observation types (`type` / v4 `observationType`), trace metadata/input/output fields (`user_id`, `release`, `doc_subclass` / `contract_subtype`, `expected_hf_class` / `expected_subclass`, `normalize-intake` stats), and score names (`JUDGE_VERDICT_SCORES` = `mailroom-pipeline-judge`, `JUDGE_QUALITY_SCORES` = `mailroom-pipeline-quality`, plus suite extras and the verified-precision alias).
  - Tests — `tests/fake_langfuse.py` fixtures mirror the trace contract (v2/v3 `type` and v4 `observationType`).
  - CHANGELOG entry for the sync (see Release process).
- **Live override**: `MAILROOM_TAXONOMY` env var → absolute path to llm-mailroom's `src/config/taxonomy.yaml`. When set, thresholds/doc classes are read from there instead of the bundled mirror (`PipelineSchema.load()`). Requires a restart — config is cached at process level.
- **Breakage map** (what happens here if the pipeline changes): new span name → run interpreted as `unknown` stage; new doc class → envelope falls back to the gray default stamp color; renamed judge scores → verdict/quality vanish from runs; new env/tag → filters in `.env` may need updating; new Langfuse observation type (not CHAIN/AGENT/EVALUATOR/RETRIEVER/SPAN/EVENT/GENERATION) → observation classified by model/usage fallback, which can hide a node or mis-file a generation.

## Commands

```bash
pip install -e ".[dev]"        # install (deps NOT vendored; no venv in repo)
python -m pytest tests/ -q     # whole suite (never hits real Langfuse)
python -m server.main          # FastAPI web server on :8001 (also: mailroom-web)
mailroom-hosted                # Observatory on 0.0.0.0 (public /live UI)
mailroom-tui                   # TUI console (planned, M4)
python scripts/seed_demo.py    # seed demo traces INTO Langfuse (planned, M5)
python scripts/run_production_pilot.py --check   # HF subset + eval scorer (needs sibling llm-mailroom)
python scripts/run_production_pilot.py --real    # live Qwen 3.7-Flash pilot → Langfuse, then eval
python scripts/eval_pipeline.py --session pilot-hf-...   # score existing traces vs docclass-merged GT
python scripts/release.py --help     # semver release workflow (see below)
scripts/publish_pages.sh       # build site/ + push gh-pages:/docs (NO Actions;
                               # one-time UI toggle: Pages → gh-pages → /docs)
```

- Tests: `pytest tests/ -v`; coverage via `--cov=. --cov-report=html`.
- **No linter, formatter, or typechecker is configured — don't invent one.**
- Frontend is **vanilla HTML/CSS/JS with no build step and no npm** — never introduce a Node toolchain.
- **GitHub Pages is deploy-from-branch only** (`scripts/publish_pages.sh` → `gh-pages:/docs`, folder `/docs` selected in Settings → Pages) — never add an Actions workflow for it (account cannot rely on Actions).
- **main ↔ gh-pages sync**: enable the committed hook once per clone (`git config core.hooksPath hooks`) so pushing main auto-republishes the site; check drift with `scripts/publish_pages.sh --status` (exit 1 = stale). The publisher runs only from `main` — if GitHub Desktop left another branch checked out, switch back first.
- Config lives in `.env` (see `.env.example`); copy `.env.example` → `.env` and add `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`.

## Architecture (not obvious from filenames)

- `mailroom_ui/` — data core (everything reads Langfuse only):
  - `langfuse_source.py` — Langfuse SDK adapter: `client.api.trace.list/get`, `client.api.observations.get_many`, `client.api.scores.get_many`, `client.api.sessions.list/get`; `TTLCache`; `LangfuseUnavailable`. `list_recent_runs()` uses trace-list responses only (cheap "light" runs for the floor); `get_run()` fetches observations+scores for drill-down.
  - `trace_interpreter.py` — `interpret_trace(trace, observations?, scores?)` → `PipelineRun`. Accepts **both v2/v3 snake_case and v4 camelCase** observation shapes (see SDK tolerance). Light runs (no observations arg) have empty span/generation detail. Re-run clustering: deterministic trace ids are reused by pilot/attempt re-runs, so a trace can carry several full runs — observations are clustered by time gaps (`RUN_GAP_S`) and only the latest cluster is kept.
  - `pipeline_schema.py` — topology mirror (see sister-repo section).
  - `models.py` — pydantic: `PipelineRun` (`doc_id`, `review_causes`, `needs_reconsideration`, `needs_human` includes archived objective misses), `NodeSpan`, `Generation`, `Score`, `SessionSummary`, `Metrics`, `Stage`, `Phase`.
  - `reconsideration.py` — objective review causes (GT miss, judge MISS/PARTIAL, extraction score floor, schema/guardrail/parse, incomplete reporting). Never uses self-reported confidence.
  - `pipeline_ops.py` — producer watcher/inbox liveness (`MAILROOM_PIPELINE_URL`).
  - `review_actions.py` — server-side proxy to llm-mailroom `GET /v1/lookup`, `POST /v1/review/{doc_id}/resolve` (`disposition=resume|record|requeue|complete`, UI `doc_type` mapped to producer `override_doc_type`, optional `doc_subclass` / `extracted_data`), `GET /v1/audit/{doc_id}`. Parked text: try `GET /v1/documents/{doc_id}/source`, else catalog lookup fallback (`original_filename` / `extracted_data`). Prefix via `MAILROOM_PIPELINE_API_PREFIX` (default `/v1`). Missing URL/token is a clear error, never a fabricated catalog row.
  - `metrics.py` — `compute_metrics()` aggregations (counts by stage/verdict, cost, tokens, p95 generation latency, per-doc-type).
- `server/` — FastAPI (Langfuse reads + producer operator proxy):
  - `main.py` — `/api/health`, `/api/traces[?since&limit&stage&environment]`, `/api/traces/{id}` (full), `/api/metrics`, `/api/sessions[/{id}]`, `/api/review-queue`, `/api/review/context`, `POST /api/review/resolve`, `/api/review/source`, `/api/review/audit`, `/api/meta`, `/api/debug/{logs,source,bundle,client}`, `/api/pipeline`, WebSocket `/ws`; mounts `web/` at `/static` (pixel console at `/`) and `hosted/` at `/live` + `/live/static`. `MAILROOM_EDITION=hosted` serves the Observatory on `/`. Browser never holds Langfuse or producer keys — the backend proxies everything, including human-review resolve and parked-file source to llm-mailroom.
  - `hosted.py` — `mailroom-hosted` entry: binds `0.0.0.0`, edition=hosted.
  - `poller.py` — `PollHub`: background poll loop → compact `floor_payload` snapshots broadcast to all WS clients; full detail cached per trace with `detail_ttl`.
- `hosted/` — Mailroom Observatory (public hosted edition): modern accessible SPA, distinct from the pixel console / TUI / GH Pages snapshot. Vanilla HTML/CSS/JS, no build step. Debug desk + `hosted/js/debug.js` (`window.__OBSERVATORY_DEBUG__`) records fetches, WebSocket frames, and uncaught errors.
- `web/` — pixel-art SPA:
  - `js/floor.js` — canvas conveyor renderer (stations, rollers, envelope animation, review/failed sidings, RECONSIDER parked on REVIEW even when stage is archived, tombstones for clean archived/failed runs). `js/api.js` (fetch + WS with reconnect + global error banner), `js/inspector.js`, `js/sessions.js`, `js/history.js`, `js/metrics.js`, `js/review.js`, `js/console.js`, `js/main.js` (app shell).
- `tui/` — planned rich-console (AgentLab-style `*** Beginning station: ... ***` banners, per-doc summary tables). Not yet built (M4).
- `scripts/seed_demo.py` — planned (M5): generates demo traces **into Langfuse** (env `demo`), never served directly.

## Langfuse is ALWAYS the source of visualization

- Every display value comes from Langfuse via the backend; no local JSON fallbacks anywhere in the display path.
- Demo/dev data is written **into** Langfuse (the seed script) so even development reads from Langfuse.
- When Langfuse is unreachable, the UI must show a "MAILROOM CLOSED — no Langfuse connection" state, not stale or canned data.

## Langfuse SDK version tolerance

- Works with `langfuse >= 2.50` through 4.x. **v4 returns camelCase at the observation level** (`startTime`, `endTime`, `modelId`, `totalTokens`, `inputTokens`, `outputTokens`, `totalCost`, `observationType`, `isRootObservation`, trace `sessionId`/`updatedAt`/`userId`); older SDKs and stored payloads use snake_case.
- Add new observation fields via `_both(d, "snake", "camel")` / `_pick(d, *keys)` in `trace_interpreter.py`; never assume a single case.
- **Every shape change needs both fixtures**: `tests/fake_langfuse.py` has `make_trace` (v2/v3 snake_case) and `make_trace_v4` (v4 camelCase); the interpreter must pass both.

## Trace structure we interpret (the contract with llm-mailroom)

- One `document-pipeline` **CHAIN** per document; **deterministic trace id seeded from the filename**; re-runs reuse it (hence the cluster logic above). Optional `user_id` (`MAILROOM_TRACE_USER_ID`) and `release` (`LANGFUSE_RELEASE`) copy onto the trace.
- Verb-first child observations with the **most specific Langfuse type** (`NODE_OBSERVATION_TYPES`): ingest/catalog/archive/`normalize-intake`/`route-for-review` = SPAN; `transcribe-pdf`/`extract-image-text` = RETRIEVER; classify/extract/arbiter/boss/report = AGENT; `judge-verify` = EVALUATOR; `pipeline-result` / LegalBench `answer-question` = GENERATION. Graph nodes: `ingest-document`, `classify-document` (classify / retry_classify / review_classify), `judge-verify`, `arbitrate-verdict`, `extract-fields` (extract / retry_extract), `route-for-review`, `adjudicate-conflict`, `compile-report`, `write-catalog`, `archive-document`. The KANBAN-063 quality gate: `judge_verify` fires on the ambiguous extraction band (`judge_band_high`, default 0.85) and a partial verdict detours through the arbiter before reporting.
- The pipeline batches Langfuse events (`LANGFUSE_FLUSH_AT` / `LANGFUSE_FLUSH_INTERVAL`, SDK defaults 512 / 5s) and `flush()` then `shutdown()` on process exit. This viewer never writes or flushes.
- `session_id = matter_id` (pilot runs use run-scoped sessions); tags `[mailroom, <env>, run-<n>, source-<corpus>?]`; metadata `{attempt, run_id, run_deadline}`; curated `input` (file metadata) / `output` (stage, doc_type, confidences, error).
- Scores: confidences (`classification_confidence`, `extraction_confidence`), run metrics (`estimated_cost_usd`, `total_tokens`, `stage_completed`, ...), judge verdict (`mailroom-pipeline-judge` = CORRECT/PARTIAL/MISS), quality (`mailroom-pipeline-quality` = 0–1). Grounded pilot runs also carry deterministic field scores (`extraction_field_score`, `extraction_overall_score`, `extraction_needs_judge_review`, `entity_list_precision/recall`).

## Config gotchas

- `.env` is loaded by `server/main.py:run()` via `load_dotenv()`; if you launch uvicorn directly (`uvicorn server.main:app`) you must export the vars yourself. `LangfuseSource` reads `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` (default `https://us.cloud.langfuse.com`).
- This repo uses **`LANGFUSE_HOST`** (SDK convention) while Langfuse docs/CLI use `LANGFUSE_BASE_URL` — if your shell exports `BASE_URL`, set `HOST` to match.
- All `MAILROOM_*` knobs (`MAILROOM_POLL_INTERVAL`, `MAILROOM_RECENT_WINDOW`, `MAILROOM_TRACE_LIMIT`, `MAILROOM_TRACE_TAGS`, `MAILROOM_TRACE_ENVIRONMENTS`, `MAILROOM_PORT`, `MAILROOM_TAXONOMY`, `MAILROOM_PIPELINE_URL`, `MAILROOM_PIPELINE_API_PREFIX`, `MAILROOM_API_URL`) are documented in `.env.example`; poller/server read them at startup — restart to change.
- `pipeline_schema.py` is cached at process level — editing `taxonomy.yaml` or the mirror requires a restart.

## Testing quirks

- Tests never hit real Langfuse. `tests/fake_langfuse.py` provides `Obj`/`FakeClient`/`make_trace` (+ `make_trace_v4`); the source adapter accepts either the real SDK client or the fake.
- `tests/conftest.py` adds the repo root to `sys.path`; `asyncio_mode = "auto"` is set.
- Frontend has no test framework — verify manually (boot server, cycle all screens, inspect an envelope, disconnect Langfuse to see the closed state). Do not invent a JS test harness.

## Release process (semver + CHANGELOG + README + wiki + tags)

**Semantic versioning** (`MAJOR.MINOR.PATCH`), version lives in `pyproject.toml`:
- **MAJOR** — breaking change to the API responses, the data contract (trace interpretation), or the visual design.
- **MINOR** — new feature: new screen, new metrics, milestone delivery (M2/M3/M4/M5 each = MINOR).
- **PATCH** — bug fixes, docs fixes, tests-only changes.

**CHANGELOG.md** — Keep a Changelog format (https://keepachangelog.com). During development new entries accumulate under `## [Unreleased]`; on release they are moved under `## [X.Y.Z] - YYYY-MM-DD` with `Added`/`Changed`/`Fixed`/`Removed` bullets.

**Mandatory, in the same commit as the code, for every major update:**
1. Update `CHANGELOG.md` (move the Unreleased entries to the new version header).
2. Update `README.md` if user-facing behavior changed (commands, config, screens).
3. Update `wiki/` (and its mirror `docs/`) if the release changes architecture, config, or usage.
4. Run the full test suite before committing.

**Tagging (coordinated with the changelog):**
- Tag must point at the release commit and match the CHANGELOG header exactly: `git tag -a vX.Y.Z -m "X.Y.Z — <one-line summary>"`, then `git push` and `git push --tags`.
- Never tag a commit that does not have a CHANGELOG entry for that version.

**Automation:** `python scripts/release.py --bump <patch|minor|major> --note "<summary>"` performs the mechanical steps (bumps `pyproject.toml`, moves `[Unreleased]` → `[X.Y.Z] - date`, prints the exact commit/tag commands) and **refuses to run on a dirty working tree**. `--check` validates repo state (tests pass, changelog format, version/tag consistency) without changing anything. After a pushed major/minor release, run `wiki/sync-wiki.sh` to publish the wiki.

**Commit style**: imperative subject + concise body, mirroring the existing history (`git log --oneline`).

## Docs duplication

- `docs/` and `wiki/` mirror each other (same convention as llm-mailroom, e.g. `docs/architecture.md` == `wiki/Architecture.md`); `wiki/sync-wiki.sh` pushes `wiki/` to the GitHub wiki. Edit both together, or regenerate from one.
- This AGENTS.md is the process/architecture authority; `README.md` is the user-facing entry point; `CHANGELOG.md` is the release record.

## Milestone status (in-flight work)

- **M1 — data core + API + tests**: DONE (mailroom_ui/, server/, tests/ green).
- **M2 — pixel engine + static web**: DONE — `web/` SPA complete (`index.html`,
  `theme.css`, `api.js`, `floor.js`, `inspector.js`,
  `sessions.js`, `history.js`, `metrics.js`, `review.js`, `console.js`, `main.js`).
- **M3 — live mode**: DONE — WS wiring with reconnect + polling fallback,
  envelope animation bound to real trace state, REVIEW queue tab.
- **M4 — TUI console**: DONE — `tui/mailroom_console.py` (`mailroom-tui`),
  AgentLab-style banners + per-doc tables over the same display API / WS
  snapshots (`--once` for scripting).
- **M5 — polish**: DONE — `scripts/seed_demo.py` seeds demo runs INTO
  Langfuse (env `demo`) with `--check` / `--check-api` / `--check-logs`
  verification modes; sprite layout verified programmatically. Remaining:
  acceptance sweep of new doc classes/live traces, sprite expansions.
- **v0.2.0 — upstream sync (2026-08-23)**: mirror updated to the current
  llm-mailroom graph — `judge_verify`/`arbiter` stages + spans, 15-agent
  roster, 7 doc classes, `judge_band_high`; floor gained the JUDGE station
  (7 stations); seed_demo grew judge-gate/arbiter scenarios on the real
  model registry (qwen/deepseek); in-flight runs now refine the generic
  `processing` marker with span progress instead of pinning to INGEST;
  metrics date-bomb test fixed.
- **v0.3.0 — released 2026-08-28**: GH Pages edition plus everything since
  v0.2.0 — human-review resolve (pixel / Observatory / TUI `--resolve`),
  Agent Skills, live-floor hopper + watcher lamp, Observatory Inbox tray,
  reconsideration beyond self-reported confidence, dojo 0.9–0.11 / Langfuse
  data-model mirrors, hosted Observatory, production HF eval, and release
  demos (`docs/demos/v030-*.mp4`). Static Pages still deploys via
  `scripts/publish_pages.sh` → `gh-pages:/docs` (deploy-from-branch, NO
  Actions). Snapshot exporter, `?api=` live/snapshot dual mode, debug
  layer, and Phoenix (`MAILROOM_SOURCE=phoenix|both`) ship in this cut.

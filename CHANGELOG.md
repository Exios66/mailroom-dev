# Changelog

All notable changes to The-Mailroom are documented here, following
[Keep a Changelog](https://keepachangelog.com) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **SPA: REVIEW tab TypeError (live + GH Pages)** — `Mailroom.api.reviewQueue`
  dispatched the string `"review-queue"` but both the live and snapshot
  clients are keyed `reviewQueue`, so every REVIEW refresh threw
  `… is not a function`, painted the error banner, and left the siding
  empty even when `/api/review-queue` / `data/review-queue.json` were fine.
- **GH Pages boot error flash** — `main.js` fetched `/api/meta` before the
  health probe, so every Pages visit showed `ERROR — HTTP 404 /api/meta`
  (and a red console line) even after snapshot mode engaged. Meta now loads
  only after a live health OK or a successful snapshot fallback; the
  expected missing live API is a dim console line, not a banner.
- **Snapshot fallback ignored a dead `?api=` / localStorage base** — bundled
  `data/*.json` was prefixed with the live API origin (`http://host:8001data/…`
  when the slash was missing). A stale localhost base blanked Pages.
  Snapshots are always same-origin; `?api=` (empty) now clears the persisted
  base.
- **Floor animation leak + dead ARCHIVE station** — `frame()` still called
  `requestAnimationFrame(frame)`, defeating the V-17 idle/visibility pause
  and running a second 60fps chain. `catalog`/`archive` stages parked on
  REPORT so the ARCHIVE desk never received an envelope. Same-station
  envelopes stacked on one pixel (only the top one was clickable).
- **TUI verdict truncation** — Rich 15 squeezed the floor table so
  `CORRECT` rendered as `COR…`. Verdict and cost columns are now no-wrap.
  error banner sat inside `.screen { overflow: hidden }`; verdict bars
  ignored per-entry colors (PARTIAL/MISS rendered green); `tile.wide`
  `span 2` overflowed single-column layouts; GitHub Pages 404'd `favicon.ico`
  into the debug log. Inspector scores now accept dict or `{name,value}`
  lists instead of `[object Object]`.
- `export_snapshot.py`: `sessions.json` top-level `count` was hardcoded to
  `0` regardless of content — now the real session count (matches
  `/api/sessions` shape; agents reading the static snapshot get honest
  numbers).
- **SECURITY: leaked `.env` purged from gh-pages history** — a Desktop
  branch-switch mishap had committed `.env` (Langfuse keys) plus stray dirs
  (`mailroom_ui/`, `server/`, `site/`, `.DS_Store`) to the branch root.
  `gh-pages` was force-pushed to a single fresh orphan commit containing
  only `docs/` (the deployed site never exposed the file — Pages serves
  `docs/` only — but clones could read it). Keys must still be rotated at
  the Langfuse UI: unreachable objects can persist on GitHub's side.
  Recurrence guards: `scripts/publish_pages.sh` now strips `.env`/
  `.DS_Store`/stray dirs from the publish clone and aborts if `.env` files
  or `sk-lf-`/`pk-lf-` key material appear anywhere in the staged tree;
  `hooks/pre-push` rejects direct `gh-pages` pushes whose tree contains any
  `.env`-like file.
- Observatory visual/UX: replay controls stay pinned while playback runs
  on Pipeline; health polls no longer clobber a live WebSocket status
  line; cards/metrics use valid HTML; trays wrap as a 2×4 grid; replay
  finishes on the run's real terminal stage (review/failed, not always
  archived); verdict bars use per-status color.

### Added

- **Mailroom Observatory debug suite** — hosted UI gained a Debug desk
  (`#debug`, `?debug=1`, keyboard `6`), a client ring at
  `window.__OBSERVATORY_DEBUG__` (`dump` / `export` / `pullServer` /
  `pushClient` / `explain`), and server one-pull `GET /api/debug/bundle`
  plus `POST /api/debug/client` so the next agent can read the last
  browser dump.
- **Mailroom Observatory (hosted edition)** — a public, modern, accessible
  site at `/live` (`mailroom-hosted`, `MAILROOM_EDITION=hosted`), distinct
  from the local pixel console, the TUI, and the GitHub Pages snapshot.
  Same Langfuse-backed `/api/*` + `/ws` contract: live pipeline trays,
  review queue, matters, metrics, inspect dialog, and paced trace replay
  (respects `prefers-reduced-motion`). Container image (`Dockerfile`) binds
  `0.0.0.0:7860` for Hugging Face Spaces / any Docker host. Docs:
  `hosted/README.md`.
- **main ↔ gh-pages sync discipline (still no Actions):** committed
  `hooks/pre-push` republishes `gh-pages:/docs` automatically on every push
  of `main` once `git config core.hooksPath hooks` is set per clone; failures
  warn by default (`MAILROOM_STRICT_SYNC=1` blocks the push instead).
  New `scripts/publish_pages.sh --status` compares the deployed
  `docs/debug/build-info.json` git SHA against HEAD (exit 1 = stale), always
  fetching fresh since publishes ride a temp clone. The publisher now refuses
  to run from any branch other than `main` (clear error when e.g. GitHub
  Desktop left `gh-pages` checked out) and the snapshot exporter retries
  transient source fetches 3× with backoff so a cloud blip can't blank a
  populated site.
- **GitHub Pages edition (static site, NO GitHub Actions):** the pixel-art
  SPA now deploys to GitHub Pages via `scripts/publish_pages.sh` using Pages'
  native "Deploy from a branch" mode (one-time Settings toggle; Actions is
  deliberately not involved). The script stages `web/` with relative asset
  paths, exports a JSON snapshot of the configured trace source
  (`scripts/export_snapshot.py` → `data/*.json`, per-run detail files,
  `debug/build-info.json` provenance for agents), verifies it (`--check`),
  and pushes the site into `docs/` on the `gh-pages` branch (Pages source:
  Deploy from a branch → gh-pages /docs; legacy root-level site files are
  cleaned up on publish) (`--dry-run` builds + verifies only;
  `--skip-export` republishes the shell with existing data). Without a
  reachable source the site still ships and honestly shows its CLOSED state.
- **Static + live dual mode in the SPA** (`web/js/api.js`, `main.js`): the
  site resolves its API endpoint as `?api=<url>` → `localStorage`
  (`mailroom.api`) → same-origin; when no live API answers it falls back to
  bundled snapshots (`SOURCE: SNAPSHOT`, gold lamp) instead of the closed
  overlay. WS only starts after the first health probe succeeds.
- **Agent debug console:** every fetch/WS frame/error/console line is
  captured into a client ring buffer exposed at
  `window.__MAILROOM_DEBUG__` (`dump()`, `export()` downloads
  `mailroom-debug.json`, clipboard copy); `?debug=1` or the CONSOLE tab's
  DEBUG toggle enables verbose capture + reveals low-level lines. Server
  side: always-on request ring buffer at `GET /api/debug/logs?limit=`,
  source/knob introspection at `GET /api/debug/source`, verbose stdout with
  `MAILROOM_DEBUG=1`, and `/api/meta` now carries `mode`, `version`,
  active `source`, plus a machine-readable endpoint index.
- **Arize Phoenix trace source** (`mailroom_ui/phoenix_source.py`): reads a
  locally running Phoenix (`PHOENIX_ENDPOINT`, default
  `http://localhost:6006`) via `arize-phoenix-client` and maps
  OpenTelemetry/OpenInference spans into the Langfuse-shaped dicts
  `interpret_trace` already consumes — llm-mailroom span names route through
  `SPAN_STAGE_MAP`, unmapped spans degrade to unknown staging (same breakage
  map philosophy), LLM spans become generations (model/token counts/cost),
  span annotations and `mailroom.score.*` attributes become scores.
  Optional dependency; never fabricated data on unreachability.
- **Source selector + multi-source facade:** `MAILROOM_SOURCE=langfuse |
  phoenix | both` picks the backend (`mailroom_ui/multi_source.py` fans
  reads out with per-trace isolation and aggregates health);
  `TraceSourceUnavailable` base class shared by both adapters so the 503
  handler covers everything; `health()` payloads gain a source-agnostic
  `"ok"` key. CORS enabled via `MAILROOM_CORS_ORIGINS` (GET/OPTIONS) so the
  Pages site can drive a locally running server next to Phoenix.

### Changed

- **README overhaul — governed-constellation edition:** root README rebuilt from 102 to 177 lines around the family story while keeping every operational byte (quick start, screens, demo seeding, requirements, config, layout, tests, releases). Added: a factual static badge row (`version 0.2.0`, `python 3.11+`, `data source: Langfuse only` — deliberately NO release/license/CI badges: no v0.2.0 tag/release exists yet and the repo carries neither a LICENSE file nor workflows); a **"The governed constellation"** section with an ASCII YOU-ARE-HERE diagram and an at-a-glance table covering all seven family repos (llm-mailroom upstream · llm-entity-extraction prompt loop + shared board · llm-dojo-scoring engine · Enron-Evaluation-Environment + claims-data-eda corpus feeds · atticus-investigation eval sibling · both graphify sites) linking llm-mailroom's canonical `docs/sister-repos.md`; a new **"The trace contract & the mirror duty"** section documenting the #1 maintenance rule (mirror span names / roster / doc classes / thresholds / judge scores in the same change window) with the visible-by-design breakage map, deferring to `AGENTS.md` as authority; an `[!IMPORTANT]` alert on the schema-cache restart gotcha; dividers between major parts; honest "No license published yet" close. Docs-only; suite unchanged.

## [0.2.0] - 2026-08-23

## [0.2.0] - 2026-08-24

### Added
- Langfuse v4 SDK tolerance: camelCase observation fields (`startTime`,
  `endTime`, `modelId`, `totalTokens`, `inputTokens`, `outputTokens`,
  `totalCost`, trace `sessionId`/`updatedAt`/`createdAt`) accepted alongside
  v2/v3 snake_case shapes (`trace_interpreter.py` `_both`/`_pick` helpers).
- `tests/fake_langfuse.py:make_trace_v4` — v4-shaped (camelCase) trace
  fixture; interpreter tests cover both shapes.
- M2 web engine (complete): `web/css/theme.css` pixel-art theme (bezel,
  scanlines, titlebar, tabs, statusbar, overlay panels, metric tiles);
  `web/js/api.js` (fetch client + WebSocket with exponential-backoff
  reconnect + format helpers); `web/js/floor.js` canvas conveyor renderer
  (stations, rollers, bins, terminals, source lamp, envelopes animated
  to their stage target with per-doc-type tint + verdict/review/failed
  stamps, click/hover inspection); `web/js/inspector.js` (spans timeline,
  LLM generations, scores); `web/js/sessions.js`; `web/js/metrics.js`;
  `web/js/console.js` (AgentLab-style banners); `web/js/main.js` app shell
  (tabs, clock, source light, WS snapshot wiring with polling fallback,
  "MAILROOM CLOSED — no Langfuse connection" overlay).
- M3 review queue: `web/js/review.js` + REVIEW tab listing
  `/api/review-queue` runs (escalation reason, confidence, verdict) with
  30s auto-refresh while visible.
- M4 TUI console: `tui/mailroom_console.py` (entry point `mailroom-tui`) —
  AgentLab-style live console (`*** Entering/Moving to station: ... ***`
  banners, judge-verdict banners, per-run floor table, review siding,
  metrics dashboard, full inspect panels: spans/generations/scores). Reads
  the same Langfuse-derived display API; subscribes to the `/ws` floor
  snapshots (full payloads) with an HTTP fallback; `--once` one-shot mode
  for scripting/CI. Keybindings: f/r/m/i/c/q.
- `tests/test_tui.py` — TUI banner/table rendering tests (no live server).
- `scripts/seed_demo.py` — seeds demo scenarios INTO Langfuse
  (env `demo`, deterministic `demo-<slug>` trace ids, verb-first spans,
  generations with usage/cost, judge verdict/quality scores via a
  CATEGORICAL `mailroom-pipeline-judge` score config) — never served
  locally. Verification modes: `--check` (asserts the stored Langfuse
  records against what was seeded), `--check-api` (asserts the live server
  display payloads), `--check-logs` (asserts against run logs physically
  saved by llm-mailroom's `sync_langfuse_logs.py`). Explicit request
  timeouts on every API call; credential preflight; delete-then-reseed
  with settle (ingestion appends, so re-seeding must start clean).
- **Upstream sync (llm-mailroom KANBAN-062/063)**: `judge_verify`
  (`judge-verify` span) and `arbiter` (`arbitrate-verdict` span) stages in
  the Stage enum, `SPAN_STAGE_MAP`, `STAGE_PHASE`, and `NODE_ORDER`;
  `sorter_reviewer`, `arbiter`, and `insurance_claims_specialist` joined the
  agent roster; `insurance_claim` doc class + specialist mapping;
  `judge_band_high` (0.85) mirrored from `graph/routing.py:judge_gate`.
- Floor gains a seventh station — **JUDGE** (between EXTRACT and BOSS),
  shared by `judge_verify`/`arbiter`; replay animates runs through the gate;
  `insurance_claim` envelopes tint violet (plus a `merger_agreement` tint for
  docclass-merged corpus rows classified as contracts).
- seed_demo: `judge-verify`/`arbitrate-verdict` span emission, three new
  scenarios (`insurance-clean`, `insurance-judge-gate`, `merger-arbitrated`;
  13 total), and generation models/prices moved onto the pipeline's real
  registry (qwen/qwen3.7-flash everywhere, deepseek/deepseek-v4-flash judge)
  with taxonomy.yaml cost_models rates.
- Fake Langfuse client exposes the v3 scores endpoint (`scores_v3`) so the
  source adapter's primary score path is exercised by every test.

### Changed
- **Release furnishing (v0.2.0 official):** official GitHub release published
  for the pre-declared `[0.2.0]` milestone. README gains a **Screenshots**
  gallery — four real captures (`docs/screenshots/`: FLOOR conveyor, REVIEW
  siding, METRICS dashboard, TUI console) rendered from genuine pipeline
  traces through the production stack, fixture-seeded exactly like the test
  suite so Langfuse stays the sole display source — plus **collapsible
  sections** (`<details>`) for demo seeding commands, configuration
  reference, and project layout, and a linked `release v0.2.0` badge.
- **README overhaul — governed-constellation edition:** root README rebuilt from 102 to 177 lines around the family story while keeping every operational byte (quick start, screens, demo seeding, requirements, config, layout, tests, releases). Added: a factual static badge row (`version 0.2.0`, `python 3.11+`, `data source: Langfuse only`); a **"The governed constellation"** section with an ASCII YOU-ARE-HERE diagram and an at-a-glance table covering all seven family repos (llm-mailroom upstream · llm-entity-extraction prompt loop + shared board · llm-dojo-scoring engine · Enron-Evaluation-Environment + claims-data-eda corpus feeds · atticus-investigation eval sibling · both graphify sites) linking llm-mailroom's canonical `docs/sister-repos.md`; a new **"The trace contract & the mirror duty"** section documenting the #1 maintenance rule (mirror span names / roster / doc classes / thresholds / judge scores in the same change window) with the visible-by-design breakage map, deferring to `AGENTS.md` as authority; an `[!IMPORTANT]` alert on the schema-cache restart gotcha; dividers between major parts; honest "No license published yet" close. Docs-only; suite unchanged.
- Generation cost is read from `cost_details` (v2/v3) or top-level
  `totalCost`/`totalPrice` (v4), never from a single fixed field — v4 also
  stores the field camelCase as `costDetails`.
- Observation classification: explicit `type` (SPAN/EVENT/GENERATION)
  decides span-vs-generation; v4 spans carry a zeroed `usage` dict that
  previously misclassified every span as a generation. The
  model/usage heuristic now applies only to `OBSERVATION`-typed or
  type-less records (the pipeline's auto-traced generations).
- CATEGORICAL scores (judge verdicts) resolve their stored numeric index
  back to the config label (`score_configs` param of `interpret_trace`,
  fed by `LangfuseSource.get_score_configs`). Score `data_type` read via
  `_both(data_type, dataType)`.
- `LangfuseSource.get_scores` reads the v3 scores API first: on Langfuse
  v4 the v1 endpoint ignores `trace_id` (returns global pages, attributing
  scores to the wrong traces) and its values are label-resolved indexes;
  v3 filters correctly and returns labels.
- `LangfuseSource.get_observations` uses the trace record's embedded
  observation set as the primary source (complete records: usage, cost,
  model, io) with the v2 index as fallback — one API call instead of two.
- `LangfuseSource.health()` is a live, briefly-cached API check; the
  server's `/api/health` reports its result. A revoked key or outage now
  surfaces as `langfuse: false` instead of a stale startup flag.
- All `LangfuseSource` read methods raise `LangfuseUnavailable` on any
  API failure; the server maps it to a 503 `{"error": "langfuse
  unavailable"}` instead of a raw 500.
- Poller `detail_ttl` raised 15s → 60s so full-detail fetch load on
  Langfuse stays well under rate limits.
- In-flight display: the generic `processing` output marker no longer pins a
  run to INGEST — `derive_stage` refines it with the deepest node span, so
  extract/retry/judge/arbiter/boss progress is visible live.
- Retry clustering is idempotent: the KANBAN-062 reviewer pass emits a third
  consecutive `classify-document` span without stacking duplicate
  `retry_classify` entries into routing paths (Python + floor replay agree).

### Fixed
- **V-3**: metrics tiles were permanently `$0.00 / 0 tok / 0 calls` in live
  mode — `/api/metrics` aggregated list-level "light" runs with no
  observations. It (and `/api/review-queue`) now aggregate enriched runs via
  the new cached `LangfuseSource.get_run()`; sessions likewise serve enriched
  runs (V-19/V-20).
- **V-5**: N+1 fetch storm — `list_recent_runs` issued one score fetch per
  trace per poll and cache TTLs (1-2 s) were shorter than the 3 s poll
  (~102-302 Langfuse calls per poll). Per-trace score fetches removed from
  the list path; run-level cache (60 s) shared by poller/metrics/review/
  sessions; cache TTL defaults raised to ≥ poll interval; HTTP 429 now backs
  off exponentially.
- **V-9**: archived/failed envelopes respawned on every 3 s snapshot after
  sliding off — tombstones keyed by trace id + updated_at now suppress
  re-creation (cleared by re-runs and manual replays).
- **V-16**: replay ignored real span durations (fixed 600/700 ms pacing) and
  dropped retry stages whenever timings existed — steps now follow the actual
  span order incl. `retry_classify`/`retry_extract`, paced by each span's
  real latency (clamped 250 ms-4 s).
- **V-18**: silent catch blocks across the SPA — global error banner +
  `window.onerror`/`unhandledrejection` hooks, non-JSON WS frames logged,
  server 503/500 `detail` bodies propagated into error messages, generic
  server errors return JSON with `detail` (were plain text 500s).
- Cost extraction regressed during v4 tolerance work — observations were
  searched for cost at the wrong level, zeroing all run costs.
- `server/main.py:_serialize` imported `floor_payload` only in the
  `full=False` branch — `/api/traces/{id}` crashed with `UnboundLocalError`.
- `web/js/sprites.js` was missing the `const SORTER = [` declaration —
  the floor's first sprite referenced an undefined matrix.
- `web/js/sprites.js:drawSprite` treated `x`/`y` as sprite-grid units
  (`(x + c) * px`) while `floor.js` passes canvas pixels — every sprite
  drawn off-origin landed 4× away (most off-canvas; envelopes rendered at
  `e.x * 4` while the hover outline drew at `e.x`, so envelopes were
  invisible until hovered). `drawSprite` now uses pixel semantics.
- The `SPRITES` map never registered the three stamps
  (`stamp_approved`/`stamp_review`/`stamp_failed`) — `floor.js` stamping
  silently referenced `undefined` and no envelope ever showed its verdict
  stamp.
- `tests/test_metrics.py::test_p95_generation_latency` expected 9.4 but
  the fixture (two generations per trace) yields a nearest-rank p95 of 9.1.
- Date bomb in `TestTzNormalization.test_compute_metrics_mixed_tz_no_crash`:
  fixed 2026-08-10 run timestamps silently fell out of the `now - 1d` window
  on Aug 11, zeroing `total_docs`. Timestamps are now relative to the clock.
- Mirror drift: `"image-extractor"` agent key corrected to `image_extractor`
  (upstream module name); `.env.example` `MAILROOM_TAXONOMY` example path
  updated to the post-restructure `src/config/taxonomy.yaml`.

### Removed
- **V-21**: `web/js/sprites.js` — 766 lines of dead sprite code, never
  loaded by `index.html` nor referenced by `floor.js` (the floor renders
  envelopes procedurally). AGENTS.md/docs/wiki references updated.

## [0.1.0] - 2026-08-10

### Added
- M1 data core: `mailroom_ui` package — `langfuse_source.py` (Langfuse SDK
  adapter + `TTLCache`), `trace_interpreter.py` (trace → `PipelineRun`),
  `pipeline_schema.py` (topology mirror, `MAILROOM_TAXONOMY` override),
  `models.py` (pydantic), `metrics.py` (aggregations).
- M1 server: FastAPI read-only API (`/api/health`, `/api/traces`,
  `/api/traces/{id}`, `/api/metrics`, `/api/sessions[/{id}]`,
  `/api/review-queue`, `/api/meta`, WebSocket `/ws`) with background
  `PollHub` snapshot broadcaster (`server/poller.py`).
- M1 tests: fake Langfuse client (`tests/fake_langfuse.py`) — the suite never
  touches the real API.
- Re-run clustering: deterministic trace ids are reused by pilot/attempt
  re-runs, so observations are clustered by time gap (`RUN_GAP_S`) and only
  the latest run's spans/generations are displayed.
- Retry detection via explicit retry stages (`RETRY_CLASSIFY` /
  `RETRY_EXTRACT`) instead of duplicate-based heuristics.
- Trace listing filter by trace `name` (`document-pipeline`) to keep the
  floor/poller focused on pipeline runs.
- Project scaffolding: `pyproject.toml`, `.env.example`, `.gitignore`,
  `mailroom-web` console entrypoint.

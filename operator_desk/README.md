# Operator desk (`operator_desk/`)

Dedicated submodule for operator **auth**, **archive file access**, **ops
snapshots**, and the **bin observer**. It is not a document-display source —
pixel / Observatory / TUI still read Langfuse only.

## Routes (mounted on `mailroom-web`)

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/v1/auth/login` | JWT (`admin` / `changeme` until you set `MAILROOM_OPERATOR_ADMIN_PASSWORD`) |
| GET | `/v1/auth/me` | Bearer profile |
| POST | `/v1/auth/logout` | Client discards the token |
| GET | `/v1/archive/list` | Local `archive_index` only — never a fabricated catalog |
| GET | `/v1/archive/{doc_id}/download\|preview\|verify` | Files under `MAILROOM_BASE_DIR` |
| GET | `/v1/ops/health` | Liveness (no auth) |
| GET | `/v1/ops/status\|throughput\|distribution` | Derived from Langfuse `PipelineRun`s |
| POST | `/v1/ops/events` | Standalone observer ingest |
| WS | `/ws/pipeline` | Bin-move events (`?token=`) |

Display `/api/*` and floor `/ws` stay unauthenticated.

## Commands

```bash
pip install -e ".[dev]"          # includes bcrypt / PyJWT / watchdog
pip install -e ".[operator]"     # + PyMuPDF for PDF preview
scripts/setup_operator.sh        # bins + migrate
mailroom-web                     # mounts the desk
MAILROOM_OBSERVER=1 mailroom-web # in-process bin watcher (preferred)
mailroom-observer                # standalone watcher → POST /v1/ops/events
python -m operator_desk          # migrate only
```

Compose (visualizer + observer + nginx, no local Langfuse). React desk is
an **opt-in profile** after `cd ui && npm install && npm run build`:

```bash
docker compose -f operator_desk/docker-compose.yml up --build
docker compose -f operator_desk/docker-compose.yml --profile ui up --build
```

Or serve the built SPA from this process at `/desk` when `ui/dist` exists.

## Knobs

See `.env.example` (`MAILROOM_OPERATOR_*`, `MAILROOM_BASE_DIR`, `MAILROOM_OBSERVER`).
`JWT_SECRET` is accepted as an alias of `MAILROOM_OPERATOR_JWT_SECRET`. Do not
reuse `MAILROOM_PIPELINE_TOKEN` as the JWT secret.

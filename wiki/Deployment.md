# Deployment Guide — The-Mailroom

> Mirrored at `docs/deployment.md` — edit both together.

The-Mailroom is a **read-only** visualizer. It never writes Langfuse events
and never runs the document graph. Deploy it next to (or pointed at) a live
[`llm-mailroom`](https://github.com/Exios66/llm-mailroom) Langfuse project.

## Prerequisites

- Python 3.11+
- Langfuse project API keys (`LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`)
- Optional: producer URL + token for REVIEW resolve / Inbox upload
  (`MAILROOM_PIPELINE_URL` / `MAILROOM_PIPELINE_TOKEN`)

Copy `.env.example` → `.env` and fill the Langfuse keys before a local run.

```bash
pip install -e ".[dev]"
python -m server.main          # pixel console on :8001
mailroom-hosted                # Observatory on 0.0.0.0
```

---

## Railway

Root `railway.json` selects the **Dockerfile** builder and probes
`GET /health` (fast process liveness — **not** a Langfuse call).
`GET /api/health` remains the SPA / TUI source-reachability check.
`nixpacks.toml` is a fallback if the service is not set to Dockerfile.

### Why `PORT` matters

The image defaults `MAILROOM_PORT=7860` (Hugging Face Spaces). Railway
injects `$PORT` and proxies to that port. The server prefers **`PORT` over
`MAILROOM_PORT`** so the process binds where the edge expects — same
contract as the llm-mailroom producer.

### Why deploys looked “crashed”

1. **Wrong listen port.** Binding image `7860` while Railway proxies
   `$PORT` → edge connection refused → `CRASHED` / restart loop.
2. **Health probe hung on Langfuse.** An older `/health` alias called the
   Langfuse API (SDK timeout ~15s). Docker `HEALTHCHECK` is 5s; a slow or
   missing key set made the container look unhealthy. `/health` is now
   pure liveness (`{"ok": true, "status": "alive"}`).

### Required service variables

| Variable | Value |
|---|---|
| `MAILROOM_HOST` | `0.0.0.0` (already in the image) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key |
| `LANGFUSE_HOST` | `https://us.cloud.langfuse.com` (or self-hosted / EU) |

### Recommended

| Variable | Value |
|---|---|
| `MAILROOM_EDITION` | `hosted` (Observatory on `/`; already in the image) |
| `MAILROOM_POLL_ENRICH` | `inflight` |
| `MAILROOM_PIPELINE_URL` | public producer URL (Railway / Space) |
| `MAILROOM_PIPELINE_TOKEN` | same secret as producer `MAILROOM_API_TOKEN` |
| `MAILROOM_PIPELINE_API_PREFIX` | `/v1` |
| `MAILROOM_TRACE_CACHE_DIR` | `/tmp/mailroom-trace-cache` |

Display stays Langfuse-only. Without Langfuse keys the UI shows
**MAILROOM CLOSED** — never canned envelopes. The process still passes
`GET /health` so Railway does not restart-loop on a closed floor.

### Deploy

```bash
railway link   # once
railway variables set \
  LANGFUSE_PUBLIC_KEY=pk-lf-... \
  LANGFUSE_SECRET_KEY=sk-lf-... \
  LANGFUSE_HOST=https://us.cloud.langfuse.com
# optional REVIEW / Inbox pairing:
# railway variables set MAILROOM_PIPELINE_URL=https://<producer> \
#   MAILROOM_PIPELINE_TOKEN=... MAILROOM_PIPELINE_API_PREFIX=/v1
railway up -m "mailroom observatory"
```

Generate a public domain (`railway domain`) and open it. Health:

```bash
curl -sS https://<domain>/health      # liveness
curl -sS https://<domain>/api/health  # Langfuse / cache status
```

Pair the producer the same way llm-mailroom documents under its
`docs/deployment.md` § Railway — point this service's
`MAILROOM_PIPELINE_*` at the producer domain.

### Railway deploy CRASHED / restart loop

- Confirm runtime logs show `Uvicorn running on http://0.0.0.0:<PORT>`
  where `<PORT>` matches Railway’s injected `PORT` (not stuck on 7860).
- Confirm `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` are set on the
  **service** (not only shared) if you expect a live floor.
- Confirm `railway.json` is on the deployed branch (`builder: DOCKERFILE`).
- Confirm `curl /health` returns quickly with `"status":"alive"` even when
  `/api/health` reports `"ok": false` (MAILROOM CLOSED).

---

## Hugging Face Spaces (Docker)

The same root `Dockerfile` is the Space image (`MAILROOM_EDITION=hosted`,
`0.0.0.0:7860`, `python -m server.hosted`). Publish with
`scripts/publish_space.py` — Langfuse keys stay Space **secrets**, never
the git tree. Details: `hosted/SPACE_README.md`.

---

## GitHub Pages (static snapshot)

Deploy-from-branch only — `scripts/publish_pages.sh` → `gh-pages:/docs`.
No Actions. See `.cursor/skills/gh-pages/SKILL.md`.

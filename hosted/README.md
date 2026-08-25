# Mailroom Observatory (hosted edition)

A **public, modern, accessible** operations desk for the `llm-mailroom`
pipeline. It is a different product surface from:

| Surface | Who it is for | How it looks |
|---|---|---|
| **This site** (`/live`, `mailroom-hosted`) | Anyone with the URL | Editorial desk, semantic HTML, keyboard-first |
| Local pixel console (`mailroom-web`, `/`) | Operators on localhost | CRT / conveyor canvas |
| `mailroom-tui` | Terminal users | AgentLab banners + tables |
| GitHub Pages | Offline snapshot | Static export of the pixel SPA |

Langfuse (or the configured Phoenix / multi source) is still the **only**
display source. This edition talks to the same `/api/*` + `/ws` contract.

## Run locally (preview the public UI)

```bash
pip install -e ".[dev]"
cp .env.example .env          # LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY
mailroom-hosted               # 0.0.0.0 — http://127.0.0.1:8001/live
# or keep the pixel console on / and open the Observatory beside it:
mailroom-web                  # http://127.0.0.1:8001/live
```

`MAILROOM_EDITION=hosted` also puts the Observatory on `/` (what the
container image does).

## Deploy to a public URL

The image listens on `0.0.0.0:$MAILROOM_PORT` (default **7860**, Hugging
Face Spaces convention). Inject the same secrets you use locally — never
bake keys into the image.

### Hugging Face Spaces (Docker)

1. Create a Space, SDK **Docker**.
2. Point it at this repo (or push the `Dockerfile` + source).
3. Space secrets: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, optional
   `LANGFUSE_HOST`, `MAILROOM_SOURCE`, `MAILROOM_TRACE_ENVIRONMENTS`.
4. The Space URL is the Observatory (`/` inside the container is `/live`).

### Any Docker host (Fly, Render, Cloud Run, a VPS)

```bash
docker build -t mailroom-observatory .
docker run --rm -p 7860:7860 --env-file .env mailroom-observatory
```

Then `https://your-host/` (or `http://localhost:7860/live` if you also
expose the pixel console paths — assets stay under `/live/static`).

## What you can do here

- **Pipeline** — live trays for Sorter · Extract · Judge · Boss · Report ·
  Archive · Review · Completed. Cards update from the WebSocket snapshot.
- **Review** — human-review queue (`/api/review-queue`).
- **History + replay** — walk a stored trace through its real span sequence
  (paces by span latency; respects `prefers-reduced-motion`).
- **Matters** — Langfuse sessions.
- **Metrics** — window aggregates from the live source.
- **Inspect** — native `<dialog>` with spans, generations, scores.

Keyboard: `1`–`5` switch views. Tab order follows the page. Skip link jumps
to main content. Status is announced in an `aria-live` region.

## Accessibility notes

- Landmarks: header, nav, main, footer; skip link; `aria-current` on the
  active view.
- Color is never the only signal (badges include the verdict word).
- Focus rings are 3px and use a dedicated `--focus` token.
- `prefers-reduced-motion: reduce` disables replay autoplay and smooth
  scrolling.
- Contrast is sized for text on cream / ink (and the dark `color-scheme`
  pair).

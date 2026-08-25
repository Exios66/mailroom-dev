# Demos & screenshots

> Mirrored at `docs/demos.md`. Media stays in the git repo (the wiki cannot
> host the `.mp4`); open the links below on GitHub.

The pixel console, hosted Observatory, and TUI share one display API.
These captures document those desks. **Langfuse is still the sole display
source** — nothing here is canned data served to the UI.

## Walkthrough video (PR recording)

~56 seconds, 1920×1200: FLOOR → REVIEW → SESSIONS → HISTORY → METRICS →
CONSOLE → inspector, then Observatory Pipeline → Review → History →
Matters → Metrics → Debug.

- [Walkthrough video](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos/tui-server-observatory-desk-walkthrough.mp4)
  (click the file on GitHub to play it)
- [Demos notebook](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos/The-Mailroom-Demos.ipynb)
- [Poster](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos/walkthrough-poster.png)
- [Stills directory](https://github.com/Exios66/The-Mailroom/tree/main/docs/screenshots)
- [Markdown twin](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos.md)

## Pilot run — documents moving through the pipeline

~25 seconds. Envelopes travel the conveyor (contract + claim archive, merger
agreement peels to REVIEW, a corporate record fails).

- [Pilot video](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos/pilot-run-documents-through-pipeline.mp4)
- [Poster](https://github.com/Exios66/The-Mailroom/blob/main/docs/demos/pilot-run-poster.png)
- [Still](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/pilot-floor.png)
- Re-record: `PYTHONPATH=. python scripts/demo_pilot_run.py --port 8005`

## Pixel-art console (`mailroom-web`)

| Still | Desk |
|---|---|
| [floor.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/floor.png) | FLOOR conveyor |
| [pilot-floor.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/pilot-floor.png) | PILOT RUN — envelopes in motion |
| [inspector.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/inspector.png) | INSPECTOR |
| [review.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/review.png) | REVIEW siding |
| [sessions.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/sessions.png) | SESSIONS / matters |
| [history.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/history.png) | HISTORY + REPLAY |
| [metrics.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/metrics.png) | METRICS |
| [console.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/console.png) | CONSOLE |

## Hosted Observatory (`/live`)

| Still | Desk |
|---|---|
| [observatory-pipeline.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-pipeline.png) | Pipeline trays |
| [observatory-review.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-review.png) | Review |
| [observatory-history.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-history.png) | History + Replay |
| [observatory-matters.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-matters.png) | Matters |
| [observatory-metrics.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-metrics.png) | Metrics |
| [observatory-debug.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/observatory-debug.png) | Debug |

## TUI (`mailroom-tui`)

| Still | Desk |
|---|---|
| [tui-console.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/tui-console.png) | Floor |
| [tui-review.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/tui-review.png) | Review |
| [tui-sessions.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/tui-sessions.png) | Sessions |
| [tui-metrics.png](https://github.com/Exios66/The-Mailroom/blob/main/docs/screenshots/tui-metrics.png) | Metrics |

TUI SVGs (re-renderable) sit next to the PNGs.
`MAILROOM_API_URL=http://127.0.0.1:8001 python scripts/render_tui_shots.py`

## Seed traces into Langfuse

```bash
python scripts/seed_demo.py
python scripts/seed_demo.py --list-scenarios
python scripts/seed_demo.py --check --check-api
```

Demo envelopes are never served as a local JSON fallback. The pixel `D`
key is opt-in (`?demo=1`) and only when the source is down.

---
name: observatory
description: Mailroom Observatory hosted desk (hosted/ vanilla SPA at /live, mailroom-hosted). Use when changing the public pipeline board, inspect dialog, debug bundle, replay, Inbox tray, or MAILROOM_EDITION=hosted — not the GitHub Pages snapshot and not the pixel CRT.
---

# Observatory (`hosted/`)

**When:** `/live`, `mailroom-hosted`, `MAILROOM_EDITION=hosted`, Debug desk,
`GET /api/debug/bundle`, replay bar, hosted Inbox tray.  
**Not:** GH Pages (`scripts/publish_pages.sh`) and not the pixel CRT at `/`.

## Layout

- `hosted/index.html` + `hosted/js/app.js` + `client.js` + `debug.js`
- Vanilla HTML/CSS/JS, no npm. Cache-bust `?v=` on the three script tags + CSS.
- Debug: `window.__OBSERVATORY_DEBUG__` — fetch/WS/error ring; Export / Pull /
  Push against `/api/debug/*`.
- Inbox tray is its own station (`stage=inbox`); sorter is ingest/classify.

## Live vs snapshot

| Mode | Command | Data |
| --- | --- | --- |
| Hosted live | `mailroom-hosted` (binds `0.0.0.0`) | Langfuse via `/api` + `/ws` |
| Pixel + /live | `mailroom-web` | Same API; Observatory still at `/live` |
| GH Pages | `publish_pages.sh` | Static snapshot — **not** this UI |

When the WebSocket drops, HTTP fallback must poll traces + `/api/pipeline` at
`poll_interval_s` (see [live-floor](../live-floor/SKILL.md)).

The Review desk can **resolve** items (`Obs.api.reviewResolve`) the same way
as the pixel console, including class/subtype correction and
`Obs.api.reviewSource` for the parked file. Unconfigured producer → setup
hint, not a fabricated catalog write.

## Related

- Pixel CRT: [pixel-console](../pixel-console/SKILL.md)
- Source: [langfuse](../langfuse/SKILL.md)
- Router: [mailroom-tool-router](../mailroom-tool-router/SKILL.md)

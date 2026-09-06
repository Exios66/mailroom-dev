# The served dispatch board (`board-site/`, Vercel)

Since HUB-055 the Kanban board also runs as a **live, issue-backed web
site** — a dispatch board any agent (or the human) can view and edit in a
browser at **https://mailroom-dev.vercel.app**. The GitHub issues are the
store, which is what makes the site auto-updating + shared: every change
is written straight through to a synced issue, so no deploy of content is
ever needed — only a deploy of the code that reads/writes it.

The issues are the single source for the site's cards, but **the board
remains canonical**: `governance/TASKS.md` is still the truth, and the two
are reconciled by the `board_state.py` legs (see below).

## What you see

- **Live cards** across the four lanes (assigned → in-progress →
  needs-attention → done/archive), plus priority, agents, and date, fetched
  from every issue labeled `kanban` (open + closed).
- A **LIVE / OFFLINE badge** reflecting whether the board API is reachable.
- **Drag/move + edit + new-card + archive UI**, filters and stats, and a
  delete → close (archive) interaction.
- Local storage is demoted to **preferences + operator identity** — the
  card data always comes from GitHub.

## Deploy root and layout

The deploy root is **`board-site/`** (Vercel project `mailroom-dev`;
Root Directory is unset so the deploy runs from `board-site/` itself,
which carries its own `board-site/vercel.json`):

```
board-site/
├── index.html          static single-page dispatch board (fetches /api/board)
├── vercel.json         clean URLs + api maxDuration
├── api/
│   ├── board.js        GET  live cards (labels=kanban) · POST new card
│   └── board/[id].js   PATCH write-back for one card
└── lib/
    └── gh.js           zero-dependency tokenized GitHub REST proxy
```

The serverless functions are zero-dependency (Node 18+ `fetch` only); no
build step, no framework.

## The API contract

### Read — `GET /api/board`

Lists every open + closed issue labeled `kanban` and normalizes each to a
board card:

- `id` — `HUB-0NN` matched from the issue title/body
- `lane` — from the `stage/*` label (`stage/in-progress` → `in-progress`);
  closed issues read as `done`
- `priority` — from the `priority/*` label
- `desc` / `evidence` — from the `### Task` / `### Evidence plan` body
  sections
- `archived` — true when the issue is closed
- Plus issue number, assignees, timestamps, and the issue's HTML URL.

### Write-back — `PATCH /api/board/HUB-0NN`

The UI PATCHes on every move/save. Only the changed keys need to be sent:

- `lane` → swaps the `stage/*` label **and posts a dated "Board lane move"
  comment** (the board mirror law); `priority` swaps the `priority/*` label.
- `desc` / `evidence` / `title` → rewrites the corresponding body sections
  (Lane/Priority cells are preserved) + the issue title.
- `agents` → sets the issue assignees.
- `archived: true` → **closes** the issue (lands in the archive);
  `archived: false` → **reopens** it.
- Any other HTTP method → `405`; malformed card ids → `400`; missing token –
  `500`.

Operator identity rides the `X-Mailroom-Actor` header (bounded to 60 chars)
and is recorded on lane-move comments.

## Config / env (Vercel secrets — never commit)

| Secret | Purpose |
| --- | --- |
| `GITHUB_TOKEN` (or `MAILROOM_GH_TOKEN`) | GitHub token with `Exios66/mailroom-dev` Issues read/write (`stage/*`, `priority/*`, `kanban`, body, comments, assignees). The deployed production secret uses the gh-keyring token scoped to the repo. |
| `MAILROOM_GITHUB_REPO` | Optional override of the repo the board reads/writes (default `Exios66/mailroom-dev`). |

## Deploy / redeploy

The site is deployed from a Vercel-bound checkout. To push an update:

```bash
cd board-site                    # the deploy root
vercel link --project mailroom-dev --token "$VERCEL_TOKEN"
vercel env add GITHUB_TOKEN production --token "$VERCEL_TOKEN"   # once
vercel deploy --prod --token "$VERCEL_TOKEN"
```

**Pin the production alias after every deploy.** The `mailroom-dev.vercel.app`
alias is shared with any parallel deploy of the same project, so a
concurrent/auto deploy can overwrite the alias with a bad build and the live
site 404s on every route (observed 2026-09-06, HUB-059: a parallel
`--prod` deploy hijacked the alias mid-work). After your `--prod` deploy,
re-assert the alias onto the deployment you verified:

```bash
vercel alias set <your-deployment-url> mailroom-dev.vercel.app --token "$VERCEL_TOKEN"
```

Then verify against the alias:

```bash
curl https://mailroom-dev.vercel.app/api/board        # 200 + JSON cards
curl -i https://mailroom-dev.vercel.app/api/board/HUB-055   # 405 (PATCH only)
```

A `PATCH` smoke move (e.g. lane → same lane, or a round-trip that restores
it) exercises the write-back against a real issue without churn; a no-op
patch produces zero label/comment churn.

## Reconciliation with the canonical board

The served board writes **issues**, not `governance/TASKS.md`:

- **site → board:** after edits made on the served site, run
  `python scripts/board_state.py pull-issues` — it reports issue-side lane
  moves that haven't landed in TASKS.md yet, then `--apply` rewrites the
  Lane cells + appends a dated `pull-issues` Evidence note.
- **board → site:** `python scripts/board_state.py sync-issues --apply` is
  the reverse leg — it pushes board-derived `stage/*` / `priority/*` /
  `attention/*` / `domain/*` / `kanban` labels onto the synced issues.
- **The card↔issue law is the norm:** the site only shows `kanban` issues,
  so every board card needs a synced issue (one card = one issue, opened
  from the `.github/ISSUE_TEMPLATE/hub_card.yml` template) with the full
  link in the card's Issue column — otherwise the card won't appear on the
  served board. Lane moves on the board are mirrored as issue comments, and
  the issue is closed in the same commit that archives the card.

The `board-governance.yml` CI gate runs `board_state.py check` (+ the label
audit + taxonomy parity) on every change to `governance/`, `scripts/`, or
`.github/`.
# TASKS.md — the mailroom-hub task board

The single source of truth for cross-agent task state in the monorepo: what is
**assigned**, **in progress**, **needs attention**, and **done**. Every agent
(and human contributor) reads this board before working and keeps it current
while working. It is a WORKING DOCUMENT, not documentation — modify it as work
happens, never delete history (finished cards move to the Archive at the bottom).

Scope: **monorepo-level work** (workspace wiring, cross-package governance,
sub-package sync, docs, releases). Work scoped to a single package is tracked
by that package's own governance (e.g.
`packages/llm-entity-extraction/governance/MESSAGE_BOARD.md`) — this board
holds the hub view and cross-package cards. Simplified counterpart of the
entity board: same laws, fewer steps.

> This board is the stand-in for inter-agent communication. When the external
> agent communication thread lands (HUB-006), it becomes the discussion
> channel and this file remains the lane table + archive of record.

## How to use — four steps

1. **Read first.** Read this board (and open GitHub issues) at session start,
   before any task: cards claimed by others, cards covering the work you were
   about to do, and open needs-attention items. Never duplicate or race a
   claimed card.
2. **Claim.** Move the card to `assigned` (if queued) and set Owner to your
   agent name + date. The moment ANY work exists — a first edit, a diff, a
   branch, a run in flight — the card moves to `in_progress`. Label it before
   the code, never after; the table must never lie about reality.
3. **Work with the card current.** Update status and Evidence as you go.
   Stuck or awaiting review? Move to `needs_attention` with a tagged note
   (`needs:` blocked-on / `review:` evidence / `decision:` the question).
   Anything discovered but not delivered spawns its own card BEFORE your card
   closes.
4. **Close with proof.** `done` requires: the package suite(s) for the touched
   packages green, `git status` clean for the card's scope, Evidence naming
   the commit(s), and — for synced cards — the GitHub issue closed in the same
   commit. Then move the card to the Archive. An agent is NOT done until its
   card says so.

## Lanes

| Lane | Meaning |
|---|---|
| `assigned` | Queued or claimed, nothing underway — no draft, no diff, no branch. Owner may be `unclaimed` (up for grabs: claim it per step 2). |
| `in_progress` | ANY work exists and an owner holds it. ONE owner per card. |
| `needs_attention` | Blocked, awaiting review, or awaiting a decision — the Evidence note says which (`needs:` / `review:` / `decision:`). |
| `done` | Finished, verified, evidenced — moved to the Archive below. Never deleted; reopen by moving back to `assigned` with a dated note. |

## Open cards

| Card | Status | Task | Owner | Issue | Evidence |
|---|---|---|---|---|---|
| HUB-004 | `in_progress` | **Upstream-drift reconciliation** — upstream tips of The-Mailroom (`2ef0041`), llm-entity-extraction (`4cfac90`) moved past their subtree-import SHAs. Run `python scripts/sync_packages.py status`, then per-package `pull --squash`, resolving upstream changes against monorepo-side fixes (the monorepo is the development source of truth — imported guards/skip fixes win unless upstream supersedes them). **llm-mailroom leg done:** pulled `d93894a` (monorepo docs alignment) with `sync_packages.py pull --squash`; re-applied the heavy-asset prune (`docs/examples/`, `docs/reports/`) as a monorepo-side fix and advanced the sync cursor; `uv run pytest packages/llm-mailroom/src/tests` = 772 passed / 36 skipped. Evidence: `abb0ed3d`. | unclaimed | — | drift visible via `sync_packages.py status`; cursor `scripts/packages_sync.json` |
| HUB-005 | `assigned` | **Release-train readiness** — at the next package release: bump the consuming pins (release-time only; `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo pin), propagate monorepo work upstream with `python scripts/sync_packages.py push --package <name>`, tag in the standalone repo. One card per release sweep; scope it when claimed. | unclaimed | — | workspace rules in `AGENTS.md` (pins keep their published git lines) |
| HUB-006 | `assigned` | **External agent communication thread integration** — the human is standing up a communication channel for agents outside this repo. When live: link it here as the discussion channel, re-point this board's "stand-in" note, and record the handover in Evidence. | Exios66 | — | opened 2026-08-30 by the human directive |

## Rules that keep the board honest

- **One owner per card.** Never work a card someone else owns — offer help on
  the issue or take over by an explicit handoff recorded in Evidence.
- **Claim before edit.** A card you are about to touch is claimed by you in
  the same session the work starts; an unclaimed card is fair game but must
  be claimed at its first edit.
- **Update, don't duplicate.** Work that addresses an existing card's problem
  updates THAT card — never a parallel card, never a duplicate issue.
- **Later timestamp wins.** If two edits collide on one card, the later dated
  note stands; the overwritten party posts a correction rather than reverting.
- **No silent completion.** A card without its closing Evidence is, to every
  other agent, still in flight.
- **Commit discipline.** Reference cards in commits: `HUB-00N: <summary>` or
  `HUB-00N claimed/reopened` in the message body.

## Issues vs board

Small, single-session, low-risk cards are **board-only** (Issue column `—`).
Critical, cross-package, or externally-verifiable cards are **synced**: open a
GitHub issue in the repo where the work lands (this monorepo for hub scope,
the package repo for package scope), write the full link into the card's
Issue column, mirror lane moves as issue comments, and close the issue in the
same commit that archives the card. A `done` card with an open issue (or the
reverse) is a board inconsistency — fix it immediately.

## Archive

Finished cards, append-only, newest last.

- **HUB-003** (done 2026-08-30) — **Root documentation + governance foundation** —
  README reworked for the monorepo (structure tree, package↔mirror table, sync
  usage, release flow); `.gitignore` extended (ruff/ipynb/coverage artifacts,
  entity experiment-log prune); AGENTS.md gains sub-package-sync section +
  governance; `governance/TASKS.md` board created. Evidence: `fe4b8d47` (docs
  rework) + the governance commit.
- **HUB-002** (done 2026-08-30) — **Sub-package sync driver (issue
  [#2](https://github.com/Exios66/mailroom-dev/issues/2))** —
  `scripts/sync_packages.py` (status / pull / push / snapshot over git
  subtree, clean-worktree guard) + baseline cursor
  `scripts/packages_sync.json`; all 9 packages verified at upstream tips
  (aligned per issue #2 as of 2026-08-30 19:06 CST). Evidence: `fe4b8d47`,
  issue #2 closed.
- **HUB-001** (done 2026-08-30) — **Monorepo import + workspace wiring** — 9
  packages under `packages/` via git subtree; one uv workspace (dev group +
  `[tool.uv.sources]`, published pins kept); monorepo-aware test repairs
  (monorepo detection, import-shadow `__init__.py` markers, pruned-asset skip
  guards, UTC-stamp and CWD anchoring fixes, notebook regeneration). Evidence:
  `ab4bf9e`, `10c5f8b4`, `fe4b8d47`; all 7 suites green — **2,331 passed /
  72 skipped, 0 failed**.

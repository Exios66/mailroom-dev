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
| HUB-004 | `in_progress` | **Upstream-drift reconciliation** — upstream tips of The-Mailroom (`2ef0041`), llm-entity-extraction (`4cfac90`) moved past their subtree-import SHAs. Run `python scripts/sync_packages.py status`, then per-package `pull --squash`, resolving upstream changes against monorepo-side fixes (the monorepo is the development source of truth — imported guards/skip fixes win unless upstream supersedes them). **llm-mailroom leg done:** pulled `d93894a` (monorepo docs alignment) + `4e9bf69` (audit-driven docs drift fixes) with `sync_packages.py pull --squash`; re-applied the heavy-asset prune (`docs/examples/`, `docs/reports/`) as a monorepo-side fix and advanced the sync cursor; llm-mailroom-graph subtree refresh pulled (`fec699d`); `uv run pytest packages/llm-mailroom/src/tests` = 772 passed / 36 skipped. Evidence: `abb0ed3d`, `d158f6ae`, `69f572a2`. | unclaimed | — | drift visible via `sync_packages.py status`; cursor `scripts/packages_sync.json` |
| HUB-005 | `assigned` | **Release-train readiness** — at the next package release: bump the consuming pins (release-time only; `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo pin), propagate monorepo work upstream with `python scripts/sync_packages.py push --package <name>`, tag in the standalone repo. One card per release sweep; scope it when claimed. | unclaimed | — | workspace rules in `AGENTS.md` (pins keep their published git lines) |
| HUB-006 | `assigned` | **External agent communication thread integration** — the human is standing up a communication channel for agents outside this repo. When live: link it here as the discussion channel, re-point this board's "stand-in" note, and record the handover in Evidence. | Exios66 | — | opened 2026-08-30 by the human directive |
| HUB-008 | `done` (pending archive) | **Corpus EDA full-fidelity completion** — human directive: the HUB-007 prune of `reports/figures_interactive/` (18 Plotly-inlined HTML figures) is reversed; the corpus EDA package carries the FULL repo content with figures + EDA reports preserved faithfully. History truncation accepted; standalone repo NOT republished (upstream tip `b39245a` already equals the import tip — only the 18 figures were missing, 74MB). Un-pruned root `.gitignore`, imported the 18 HTMLs sha256-identical to upstream, refreshed the stale `packages_sync.json` note (corpus upstream IS published; `sync status` = in sync), aligned root/package docs. Spun off HUB-009 (subset-run summary hazard). | opencode | — | commit `c16cdd18` |
| HUB-011 | `done` (pending archive) | **Prompt-engineer opencode agent adapted for the monorepo** — human directive: make the entity repo's GEPA prompt-engineer agent operate out of the box in mailroom-dev. Root `.opencode/agents/prompt-engineer.md` (workspace bindings: uv-workspace commands, per-package AGENTS.md rule, both prompt registries — entity `PROMPT_VERSIONS` append-only + mailroom `prompts_docclass.py` PURE-APPEND, the llm-dojo→mailroom direction doctrine, HUB-00N vs KANBAN-NNN board routing, env variables incl. the funding-key gate / `BRAINTRUST_LOGGING` default / mailroom `OBSERVABILITY_PROVIDER` Phoenix gotcha / `PYTHONHASHSEED=0` / hub-1.x datasets-cache + read-timeout quirks) + `PROMPT_ENGINEER_GEPA_PROVENANCE.md` companion copied verbatim. GEPA doctrine (9-step loop, scientific contract, Phases 0–6) preserved — diff vs the entity source shows exactly 3 intended binding edits, zero doctrine drift. Sessions inside `packages/llm-entity-extraction` keep that package's own agent copy (closer project config wins); the global `~/.config/opencode` copy stays generic. Board-only card (tooling config, single session). | opencode | — | restart opencode to load; suite impact: none (config-only) |
| HUB-012 | `assigned` | **corpus-eda P3 summary counter stale (27 vs 30 figures)** — discovered during HUB-010: `visualizations.run()` returns a figures count of 27, so `SUMMARY_REPORT.json` P3 stats say `figures: 27`, while P3 actually writes 30 PNGs (disk truth; 28/29/30 live in `visualizations.py`). Docs were aligned to 30 in HUB-010; fix the returned counter so the summary stats match the artifact count. Touching it rewrites `SUMMARY_REPORT.json` (byte-drift vs upstream) — coordinate with the corpus-eda upstream at next sync. | unclaimed | — | HUB-010 session, 2026-08-31 |
| HUB-014 | `in_progress` | **GitHub governance tooling — templates, labels, board state tracker** — human directive: full GitHub integration for the hub board. YAML issue templates (board card / bug / feature / task-TODO + `config.yml`, replacing the legacy `new-feature.md`+`todo.md`), YAML PR template enforcing the hub discipline (card ref, board-before-code, `HUB-0NN:` commit law, test gates, docs currency), declarative label taxonomy (`.github/labels.json`: `stage/*` lane mirrors, `attention/*` tags, `type/*`, `priority/*`, `domain/*` per package, `kanban` marker) + `scripts/github_labels.py` sync/audit, and `scripts/board_state.py` — a computationally readable live-state tracker for this board (parse open table + archive, `status`/`--json`/`card`/`check` invariants incl. git cross-checks, `sync-issues` label sync, `project-init`/`project-sync` GitHub Projects v2 mirror with Lane/Owner/Card fields, dry-run default). CI: `.github/workflows/board-governance.yml`. Docs currency in the same commit. | opencode (2026-08-31) | — | claimed 2026-08-31 by opencode; human directive, same session |
| HUB-013 | `done` (pending archive) | **Corpus-EDA v7 reconciliation** — human pushed the standalone clone to upstream (`main` = `43b5232`; both the import tip `b39245a` and v7 tip `1b0cf28` verified ancestors — clone no longer sole copy). Upstream now carries v7 intent-hydration machinery (issue #5: cross-walk, Enron join, LLM labeler, provenance schema; HF data rev `1acd2600`, card rev `fc1f211c`), a **P0–P6 pipeline** (new P6), v7 EDA reruns, and ports of the monorepo HUB-008 reports rule + HUB-009 summary guard. Pull v7 into the monorepo via `sync_packages.py`, reconcile against monorepo-side fixes (monorepo wins unless superseded), run the full pipeline, advance the cursor, align root docs (P0–P6). | opencode | — | v7 landed via `e68b0631`/`06505812`/`e37100a9`/`8d7ce748` + v7 schema bump `41ac512a`; cursor advanced to `43b5232` in `831c9b34`; `sync status` = in sync |

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

- **HUB-013** (done 2026-08-31) — **Corpus-EDA v7 reconciliation** — v7
  intent-hydrated corpus (issue #5: aeslc_join/llm_zero_shot hydration of 350
  correspondence rows, intent_source/confidence/status GT columns; HF data
  rev `1acd2600`) is now canonical in the monorepo: subtree-pulled upstream
  (`e68b0631` — run_all P6 default, monorepo phases help text kept), v7
  interactive figures synced byte-identical to upstream `e83250c`
  (`06505812`), full P0–P6 pipeline green in the monorepo venv with
  matplotlib 3.11 renders (`e37100a9`), v7 doc sweep merged (`8d7ce748`),
  schema-v7 bump propagated across The-Mailroom/llm-mailroom/agent-mailroom
  (`41ac512a`), root docs aligned to P0–P6 + `intent_backfill`. Conflict law
  applied: upstream ported the HUB-008/009 rule TEXT to AGENTS.md but not the
  code — monorepo `run_all.py` keeps the summary-write guard + 30-figures
  print (monorepo side wins; upstream ported text matches). Cursor advanced
  to upstream tip `43b5232` via snapshot (`831c9b34`); `sync status` =
  in sync; `py_compile` green. Downloads clone now fully contained in
  upstream — safe to archive locally. HUB-012 remains open (P3 summary
  counter still 27 in v7). Evidence: `831c9b34` + commits above.
- **HUB-010** (done 2026-08-31) — **Full documentation sweep** — human
  directive: update ALL documentation in mailroom-dev. Inventoried ~380
  tracked .md files; scoped the sweep to the OPERATIVE docs (root
  README/AGENTS/TASKS + 10 package README/AGENTS pairs) — historical records
  (memos, skills, wikis, slides) left untouched as standalone-mirror archives
  (llm-mailroom's AGENTS.md itself forbids monorepo-side hand-edits of its
  docs). Fixes: root AGENTS.md gains the Enron suite (74/74, verified green —
  it was missing from both root docs) and corrects the "each package carries
  its own AGENTS.md" claim (3 of 10 packages document conventions in READMEs);
  root README drops the phantom `mailroom-corpus-eda/tests` line (no suite;
  EDA verified via run_all.py P0–P5), documents the two suite-less virtual
  members, clarifies per-package sync cursors (advanced since the issue #2
  baseline), fixes the `uv run pytest` comment; corpus-eda README P3 row +
  run_all.py banner 27→30 (disk truth — 30 PNGs, Reports section and AGENTS.md
  already said 30); Enron AGENTS.md test counts aligned to reality/README
  badge (74 across test_labeler.py + test_content_labels.py). Verified:
  Enron suite 74 passed, claims-data-eda suite 30 passed ("30 tests" claim
  confirmed), run_all.py py_compile green. Spawned HUB-012 (stale P3 summary
  counter). Evidence: `bb854809`.
- **HUB-009** (done 2026-08-31) — **run_all.py subset runs clobber
  SUMMARY_REPORT.\*** — fixed: `run_all.py` now writes
  `reports/SUMMARY_REPORT.json` only when all six phases ran; `--phases`
  subset runs and `--no-interactive` (whose summary would miss the P4
  section) leave it untouched with an explicit stdout notice. Package has no
  test suite, so verification was behavioral: P4-only and `--no-interactive`
  runs leave the summary sha256-identical; a full P0-P5 run rewrites it
  byte-identical to the committed version (determinism holds); scratch
  figure UUIDs restored from git per the canonical-bytes rule; `py_compile`
  green. One transient P3 failure on a `--no-interactive` attempt did not
  reproduce on rerun (phase machinery reported it correctly with exit 1 —
  watch for recurrence). Package AGENTS.md hazard block updated to the new
  behavior; monorepo-side fix, upstream publish deferred to the release
  train (HUB-005). Evidence: `9c0a5321`.
- **HUB-008** (done 2026-08-31) — **Corpus EDA full-fidelity completion** —
  human directive: preserve figures + EDA reports faithfully, full repo in,
  history truncation OK, no republish. Imported the 18 Plotly HTML figures
  (`reports/figures_interactive/`, 74MB) sha256-identical to upstream tip
  `b39245a` (which now equals the monorepo import tip — all 71 pre-existing
  files verified byte-identical; history-truncated content import, not a
  subtree append); un-pruned root `.gitignore`; carved the corpus EDA
  deliverables out of the heavy-assets rule in root AGENTS.md; refreshed the
  stale `packages_sync.json` note — the corpus upstream IS published and
  `sync_packages.py status` shows in sync; aligned root/package docs (README
  prune note, package AGENTS.md canonical-bytes rule: Plotly HTMLs embed a
  random per-render UUID so regenerated variants can never be
  byte-identical). Verification: P4 rebuild green under the shared venv;
  caught + reverted its SUMMARY_REPORT.json clobber (spawned HUB-009); final
  tree sha256-matches upstream. Evidence: `c16cdd18`.
- **HUB-007** (done 2026-08-31) — **Import mailroom-corpus-eda as 10th
  workspace member** — subtree-added the corpus EDA package with FULL history
  appended from a local `monorepo-import` branch (interactive HTML figures
  pruned — regenerable heavy assets; standalone repo keeps them; ignored in
  the monorepo); registered in `sync_packages.py` PACKAGES +
  `packages_sync.json` (cursor at local import tip `9cc339a`, corpus repo NOT
  republished); wired pyproject (virtual member, requires-python>=3.12),
  root dev group (+plotly/seaborn/squarify/huggingface_hub), AGENTS/README
  docs; fixed pandas 3.0/matplotlib 3.11 forward compat (include_groups
  removal, boxplot tick_labels) + deterministic report outputs
  (repo-relative paths, stable diff ordering) so monorepo rebuilds are
  byte-identical; `uv lock`/`uv sync` green, `run_all.py` P0-P5 green under
  the shared venv against the full 1,650-row corpus (v6 rev2). Evidence:
  `39409359` (subtree add), `0a5b498a`, `90b25747`, `989f95bb`.

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

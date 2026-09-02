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

**Machine-readable state (HUB-014):** this board is computationally readable
via `python scripts/board_state.py` — `status` (snapshot, `--json` for
machines), `card HUB-0NN` (one card + its commits), `check` (invariants:
structural contradictions exit 1; hygiene drift is warned), `sync-issues`
(label sync onto synced issues), `project-init`/`project-sync` (GitHub
Projects v2 mirror). The label taxonomy for issues lives in
`.github/labels.json` (`stage/*` = these lanes, `attention/*` = the
needs_attention tags, `type/*`, `priority/*`, `domain/*`, `kanban` marker);
the CI gate `.github/workflows/board-governance.yml` runs `check` + the
label audit on every change to `governance/`, `scripts/`, or `.github/`.

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
| HUB-005 | `assigned` | **Release-train readiness** — at the next package release: bump the consuming pins (release-time only; `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo pin), propagate monorepo work upstream with `python scripts/sync_packages.py push --package <name>`, tag in the standalone repo. One card per release sweep; scope it when claimed. | unclaimed | — | workspace rules in `AGENTS.md` (pins keep their published git lines). HUB-021 note: the driver now quantifies the per-package monorepo-ahead payload (its `status` output IS this card's work list) and `push --patch` makes the publish leg reliable. |
| HUB-006 | `assigned` | **External agent communication thread integration** — the human is standing up a communication channel for agents outside this repo. When live: link it here as the discussion channel, re-point this board's "stand-in" note, and record the handover in Evidence. | Exios66 | — | opened 2026-08-30 by the human directive |
| HUB-020 | `assigned` | **docclass eval judge prompts still grade against the retired 8-class "EXTENDED primary set"** — discovered during HUB-019 component 6: `packages/llm-entity-extraction/src/prompts_docclass.py` (judge/reviewer/arbiter/boss docclass prompts) and the byte-mirror `packages/The-Mailroom/mailroom_ui/docclass_prompts.py` instruct judges to grade against the extended 8-class list (incl. retired compliance_filing/court_opinion/due_diligence) while the docclass GT is the canonical five (plan §5/§66/§93; docs/v7-taxonomy.md §5 avoid-list). Land in THIS monorepo (human directive: all work in mailroom-dev): add NEW prompt version keys (never mutate versions that have run) with five-class + `unknown` grading language per plan §67, mirror byte-identical into The-Mailroom, leave default selection unchanged until a same-surface A/B validates v1; option-list ↔ schema-enum test parity maintained. Decision open for the human: whether the docclass arm keeps the extended surface as deliberate eval design (KANBAN-033 lineage) or moves to five-class grading. | unclaimed | — | HUB-019 Evidence 2026-09-02 |
| HUB-021 | `in_progress` | **Sync driver: reliable upstream propagation** — human directive ("fix the upstream propagation issue"). The subtree cursor mechanics caused every recent reconciliation incident: HUB-018 snapshot-advanced a cursor past content never subtree-merged (next squash pull re-imported the range); HUB-012 subtree push went non-fast-forward (snapshot-based cursor ancestry) and needed a manual patch-push; HUB-009's summary guard went upstream out-of-band. Fix `scripts/sync_packages.py`: content-containment checks (blob-tree compare of `packages/<name>` vs upstream tip) before `snapshot` advances a cursor (refuse with guidance unless `--force`) and before `pull --squash` re-imports content-equal tips; `push --patch` fallback (scripted HUB-012 workaround: upstream tip + tracked-file diff → single commit → fast-forward push → cursor re-baseline, `--dry-run` default-off safety); `status` surfaces cursor/content gaps and monorepo-ahead drift. Pushes stay explicit (release-time only per workspace rules). | GLM-5.3-Flash (opencode) 2026-09-02 | — | HUB-018 process note; HUB-012 patch-push precedent. LANDED: containment oracle = blob-tree compare (`tree_map`) with gitignore-aware missing-path exemption (pruned heavy assets are doctrine, not drift — HUB-004/018) and modified-path separation (monorepo-ahead ≠ gap). Verified: throwaway fixture sims of both incidents (HUB-018 gap → refusal; honest cursor → clean; HUB-012 → dry-run plan then ONE fast-forward commit `6026b9a` directly on the old tip carrying the monorepo fix, post-push cursor verifies clean); live: `status` 10/10 in sync, 0 cursor gaps, monorepo-ahead counts quantified (corpus-eda 56, llm-mailroom 23, sandbox 20, entity 17, The-Mailroom 6, agent-mailroom 4, Enron 2, claims 1, graph 1, dojo 0 = the HUB-005 release-train payload); content-verified `snapshot` green for all 10; clean-tree guard re-verified. Docs currency: README sync section + wiki Sub-Package-Sync. |

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

- **HUB-018** (done 2026-09-01) — **Sub-package sync sweep: llm-mailroom +
  mailroom-corpus-eda** — human directive: pull all packages' most recent
  versions, ensure they are synced to the monorepo including EDA reports,
  visuals, and documentation fixes. 8/10 packages already in sync; two legs
  reconciled. **llm-mailroom**: upstream tip `d4940f8a` (operational
  procedure doc + pipeline SVG) pulled with squash base `aace6a49` — the
  cursor had been snapshot-advanced past content never subtree-merged
  (`aace6a49` not an ancestor of the recorded `857fb381`), so the pull
  back-filled the whole range; process note: snapshot-advance without a
  merge creates a cursor/content gap that the next squash pull re-imports.
  Post-merge monorepo-truth reconciliation: re-pruned the gitignored heavy
  assets the merge resurrected (`docs/examples/` 9 sample PDFs + external
  corpus texts, `docs/reports/` incl. the 59,668-line experiment_log.md —
  `.gitignore:56-57`, HUB-004 doctrine); restored clobbered monorepo-side
  wiring (`[tool.uv.sources]` workspace redirect, bump-script release-time
  note, 6 pruned-asset skip guards, dojo pin-flexibility guard, UTC-stamp +
  CWD-anchoring fixes); re-tuned notebook lab scenarios to the monorepo
  taxonomy bands (low 0.90 / high 0.98 / judge band 0.97 — upstream's
  0.80/0.97 retune targets upstream's looser bands): `CLASSIFY_CONTRACT_MEDIUM`
  0.92, `CLASSIFY_INSURANCE_HIGH` 0.98, judge-band scenario extraction 0.93,
  keeping upstream's `court_opinion` override (guardrail-honest —
  court_opinion is out-of-taxonomy on both sides); refreshed stored outputs
  for notebooks 02/03/10; fixed the stale `DOC_CLASSES` pin 6→5 left by the
  compliance-filing retirement commits (pre-existing red). Suite 772 passed
  / 36 skipped / 0 failed; `uv lock --check` green. **mailroom-corpus-eda**:
  upstream moved twice mid-session (`c659789f` source dataset cards + docs
  index; `816fb028` issue #5 intent_source aeslc_join fix on the 162
  join-assisted rows); subtree squash base resolved to a pre-import ancestor
  (`d3198a2a`) → 49 pseudo-conflicts, resolved per the HUB-004/012/013 laws:
  upstream taken byte-verified for the true 13-file delta (README blurb,
  `docs/README.md` index, 5 `docs/dataset-cards/*.md`,
  `SUMMARY_REPORT.{json,md}` with figures=30 preserved, dataset_export /
  docclass_uploader / intent_backfill), monorepo-canonical kept for
  everything outside the delta (`run_all.py` summary-write guard, AGENTS.md,
  tables/, 30 matplotlib-3.11 PNG renders, 19 interactive HTMLs).
  py_compile green; EDA deliverables remain fully tracked (HUB-008
  exception). **Known residue** (discovered, not delivered): upstream's
  notebook narrative still cites upstream-band thresholds (0.85 judge gate,
  0.95 high, 0.88 reviewer labels) — inaccurate under the monorepo taxonomy
  bands; left as upstream-managed content, to reconcile at the release
  train (HUB-005 push) rather than hand-edited monorepo-side.
  `sync status` 10/10 in sync. Evidence: `2d93de6b` (prune + restorations),
  `ce98b043` (scenario re-tune), `6f2ce890` (corpus-eda subtree merge).
- **HUB-017** (done 2026-09-01) — **GitHub wiki for mailroom-dev** — human
  directive. Full version-controlled wiki source landed at `docs/wiki/`
  (entity-repo pattern): **Home** (facts table: pins v0.6.0 / dojo
  v0.12.2 / corpus v7), **Getting-Started** (workspace, per-package
  suites, sandbox quickstart), **Architecture** (full map: 10 packages +
  hub, direct repo links, the 3 GitHub Pages sites, 13-node pipeline with
  the procedural compile_report + live reviewers, layout, heavy-asset
  rule), **Board-Governance** (lanes, laws, `board_state.py` usage incl.
  severity contract + Projects v2 prerequisite, label taxonomy, issue/PR
  forms, CI gate), **Sub-Package-Sync** (current-only doctrine, driver
  commands, prune-resurrection fix, verification contract),
  **HF-Corpus** (docclass-merged v7 facts: 1,650 rows, revs, 27-key GT
  schema, strata vocabulary, P0–P6 + canonical-bytes rule, upload
  helpers), **Offline-Sandbox** (provider profiles, reduced agent profile
  — reporter retired/procedural, reviewers kept — corpus-aligned targets,
  Docker hardening + pins, commands), **Releases** (release train, family
  pins table, deploy surfaces), **FAQ** (10 gotchas incl. prune
  resurrection, tracker warnings, project scope, reporter), plus
  **_Sidebar.md** navigation and **sync-wiki.sh** (clone-or-pull, copy,
  commit + push; `--check` drift mode; syntax-checked). Root docs currency:
  README structure tree gains `docs/wiki/` + wiki paragraph; AGENTS.md
  commands gains `sync-wiki.sh`. Suite green (51 passed / 0 failed).
  **Open prerequisite (human, one-time UI action)**: the wiki git repo is
  NOT materialized until the first page is created in the web UI (no REST/
  GraphQL API for wiki content; first push returns "Repository not found")
  — visit github.com/Exios66/mailroom-dev/wiki once, create any page, then
  `./docs/wiki/sync-wiki.sh` pushes the full content. Evidence: this
  commit.
- **HUB-016** (done 2026-09-01) — **Docs-currency sweep** — systematic
  staleness pass over every surface touched by HUB-014/004/012/015. Fixed:
  sandbox `docs/sister-repos.md` dojo row v0.12.1→v0.12.2;
  `data/fixtures/ATTRIBUTION.md` v0.5.0→v0.6.0; sandbox `CHANGELOG.md`
  [Unreleased] pin bullet updated + HUB-015 Changed entry (reporter
  retirement / zero-LLM compile path / v0.6.0+v0.12.2 alignment / GT
  targets / Docker hardening); `docs/docker-offline.md` documents the
  non-root USER + HEALTHCHECK + the full version-pin table. Verified
  current (no changes needed): root README (architecture map, governance
  tooling, suite list), root AGENTS.md (commands + board law), TASKS.md,
  corpus-eda README/AGENTS (no stale figure counts), entity docs
  (upstream-managed — describes the standalone repo where the pruned dirs
  exist; prune is documented at root level), sandbox README/AGENTS/evals.md
  (HUB-015 pass). Greps for legacy template refs, stale pins, and figure
  counts all clean. Suite: 51 passed / 1 skipped / 0 failed. Evidence: this
  commit.
- **HUB-015** (done 2026-09-01) — **Offline sandbox: current-pipeline
  alignment + reduced agent profile + docclass-merged targets** — human
  directive; one commit. (a) **Version alignment**: sandbox surfaces moved
  off stale mailroom v0.5.0 → **v0.6.0** (`fetch-deps` cli help + tag,
  `overlay.py` hint, README/AGENTS/sister-repos docs); dojo pin bumped
  v0.12.1 → **v0.12.2** (llm-mailroom v0.6.0's own pin; tag verified;
  `uv lock` green); monorepo `[tool.uv.sources]` already resolves the
  current workspace mailroom. (b) **Reduced agent profile — human
  correction applied: the REPORTER agent is retired, reviewers untouched**:
  `components.yaml` moves `reporter` to `retired_agents`, adds the
  `compile_report` node gate; the sandbox eval spec is now the
  **computational procedural reporter** (`compile_report`, kind=nodes,
  observation `compile-report`) — mock + live paths are deterministic
  matter-record assembly, the `get_llm` client acquisition is GONE (zero
  LLM calls on the reporter path; new guard test asserts it). (c) **Full
  docclass-merged GT targets**: `data/fixtures/hf/docclass_mini.jsonl`
  enriched for all 5 corpus doc types with `expected_subclass` from the
  real corpus strata vocabulary (contract→Consulting Agreements,
  merger→all_cash, corporate_record→bylaws, correspondence→attorney_demand,
  insurance→carrier) + `expected_fields` from the 27-key corpus GT schema
  (correspondence: intent=payment_demand + intent_source/confidence/status
  provenance, subject_matter, keywords, claimed_amount, sentiment;
  insurance: policy_number, insured_party, date_of_loss, claimed_amount,
  damages_description); `hf_rows_as_manifest` propagates both into every
  eval row (verified end-to-end: 5/5 rows carry subclass + fields).
  (d) **Docker best practices**: Dockerfile gains non-root `USER sandbox`
  (uid 1000, override documented) + HEALTHCHECK; compose pins all four
  `:latest` images to versioned tags (ollama 0.33.2, vllm v0.28.0, phoenix
  version-20.4.0, minio RELEASE.2025-09-07-16-13-09Z) — zero unpinned
  images remain. (e) **Tests**: suite green 51 passed / 1 skipped / 0
  failed (roster test asserts reporter∉SPECS + gates; pin-guard updated to
  v0.12.2; reviewer evals preserved and passing). Docs currency: AGENTS.md
  gains the Reduced-agent-profile section; docs/evals.md compile_report
  row. Production llm-mailroom graph untouched (sandbox-profile scope per
  human choice). Evidence: this commit.
- **HUB-012** (done 2026-09-01) — **corpus-eda P3 summary counter stale
  (27 vs 30 figures)** — fixed: `visualizations.py::run()` now returns
  `{"figures": 30}` (disk truth — 30 PNGs written by the module), so
  `SUMMARY_REPORT.json` P3 stats match the artifact count. Verified by the
  FULL P0–P6 pipeline in the workspace venv: all 7 phases green, P3 banner
  "30 figures", 1,650 rows / schema v7 / P6 intent coverage 100%
  (350/350, 8/8 classes in test) — in line with the published HF corpus
  (`data 1acd2600`, `card fc1f211c`, API-verified). Determinism held: the
  summary diff is exactly the one-line `figures` correction; all 30 PNGs +
  tables byte-identical; the 19 regenerated interactive HTMLs restored to
  canonical bytes (per-render UUID rule). Published upstream per human
  directive: subtree push was non-fast-forward (cursor ancestry from the
  HUB-013 snapshot, not a graft) — clean 1-commit patch-push to
  Mailroom-Corpus-EDA `main` instead (`43b5232..f3c94f3`, fast-forward),
  cursor re-baselined via snapshot; `sync status` 10/10 in sync. Known
  benign drift: upstream's committed `SUMMARY_REPORT.json` differs from the
  monorepo's in JSON key ORDER only (5 keys, values identical) —
  upstream-side generation artifact, monorepo file is canonical. Evidence:
  `6c343bab` (fix) + upstream `f3c94f3`.
- **HUB-004** (done 2026-09-01) — **Upstream-drift reconciliation** — all
  legs complete, monorepo in sync with every standalone upstream (10/10 via
  `sync_packages.py status`). llm-mailroom leg: pulled `d93894a`+`4e9bf69`
  (`--squash`), heavy-asset prune re-applied, cursor advanced; suite 772
  passed / 36 skipped. llm-mailroom-graph refresh pulled (`fec699d`).
  The-Mailroom tip `fae52e1` reconciled. llm-entity-extraction leg
  (2026-09-01): pulled upstream `4cfac906e`→`2482879f2` — 6 additive
  KANBAN-105 commits (docclass-merged v6 builders/publish machinery:
  `build_docclass_v6.py`, `publish_docclass_v6.py`,
  `attach_original_files.py`, `export_existing_purpose_gt.py`,
  `build_correspondence_append.py`, `build_extra_claims.py` +
  `test_kanban105_docclass_v6.py`); file-level compare pre-verified zero
  overlap with monorepo-side wiring (conflict-free by construction);
  re-applied the heavy-asset prune the subtree merge resurrected
  (`docs/data/`, `docs/posit/`, `docs/posit-src/` — root `.gitignore`
  lines 52-54; gitignore does not apply to tracked files, so explicit
  `git rm --cached` + tree removal); entity suite green 745 passed /
  28 skipped / 0 failed (the 2 transitory failures were the resurrected
  pruned dirs breaking skip-guarded tests — resolved by the prune; all
  skips are documented pruned-asset/live-artifact guards). Monorepo-side
  fixes untouched (guards/markers intact); no stale code imported
  (monorepo = central truth, current-only pulls). Evidence: `a760f698`
  (entity squash) + the prune/archive commit.
- **HUB-014** (done 2026-09-01) — **GitHub governance tooling — templates,
  labels, board state tracker** — human directive: full GitHub integration
  for the hub board. Landed in one commit: YAML issue templates
  (`.github/ISSUE_TEMPLATE/`: hub card / bug / feature / task-TODO +
  `config.yml`, legacy `new-feature.md`+`todo.md` deleted), YAML PR template
  enforcing the hub discipline, declarative label taxonomy
  (`.github/labels.json`: `stage/*` lane mirrors, `attention/*` tags,
  `type/*`, `priority/*`, `domain/*` ×13, `kanban`) +
  `scripts/github_labels.py` (sync/audit), `scripts/board_state.py`
  (live-state tracker: parse open table + archive, `status`/`card`/`check`
  invariants incl. git cross-checks, `sync-issues` label sync,
  `project-init`/`project-sync` Projects v2 mirror with Lane/Owner/Card
  fields, dry-run default), CI gate `.github/workflows/board-governance.yml`
  (board check + label audit blocking; project mirror advisory), docs
  currency in README/AGENTS/TASKS. Verified: `py_compile` green; all 7 YAML
  files parse; `status/check/card/--json` green on the live board (0 errors;
  surfaced hygiene drift → HUB-008/011/013 stale open rows resolved, HUB-011
  properly archived); labels synced live (32 created, `audit` green — 3
  descriptions shortened to GitHub's 100-char limit); all 5 repo issues
  (all closed) retro-labelled with the taxonomy. Open prerequisite (human,
  one-time interactive): `gh auth refresh -s read:project` → `project-init`
  → `project-sync` to stand up the Projects v2 mirror. Suite impact: none
  (hub tooling only). Evidence: this commit.
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
- **HUB-011** (done 2026-08-31) — **Prompt-engineer opencode agent adapted
  for the monorepo** — human directive: make the entity repo's GEPA
  prompt-engineer agent operate out of the box in mailroom-dev. Root
  `.opencode/agents/prompt-engineer.md` (workspace bindings: uv-workspace
  commands, per-package AGENTS.md rule, both prompt registries append-only
  — entity `PROMPT_VERSIONS` + mailroom `prompts_docclass.py`, the
  llm-dojo→mailroom direction doctrine, HUB-0NN vs KANBAN-NNN board routing,
  env variables incl. the funding-key gate / `BRAINTRUST_LOGGING` default /
  mailroom `OBSERVABILITY_PROVIDER` Phoenix gotcha / `PYTHONHASHSEED=0` /
  hub-1.x datasets-cache + read-timeout quirks) + the
  `PROMPT_ENGINEER_GEPA_PROVENANCE.md` companion copied verbatim. GEPA
  doctrine (9-step loop, scientific contract, Phases 0–6) preserved — diff
  vs the entity source shows exactly 3 intended binding edits, zero doctrine
  drift. Sessions inside `packages/llm-entity-extraction` keep that package's
  own agent copy (closer project config wins); the global
  `~/.config/opencode` copy stays generic. Board-only card (tooling config,
  single session). Evidence: restart opencode to load; suite impact: none
  (config-only). Archived from the open table by the HUB-014 board-state
  tracker sweep (the archive entry was missing).
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

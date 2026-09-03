# Changelog — mailroom-hub

All notable changes to the **mailroom-dev monorepo itself** (workspace wiring,
cross-package governance, sync tooling, corpus governance, hub infrastructure)
are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) ·
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html) — while
the hub is `0.x` (pre-1.0), a **MINOR** bump may carry breaking workspace
changes; **PATCH** is fixes-only. Every hub release is an annotated git tag
`vX.Y.Z` (`mailroom-hub vX.Y.Z` message) mirrored as a GitHub Release; the
`[Unreleased]` section accumulates between releases.

Scope note: the hub chain versions the **monorepo as a whole**. Package-level
releases (llm-mailroom, llm-dojo-scoring, …) are cut in their standalone
repositories per the release train (HUB-005) — see each package's own
`CHANGELOG.md`; the standalone repos remain the release vehicles for deployed
surfaces. The pre-import history in this repository (before 2026-08-30)
belongs to the standalone mailroom lineage that became `packages/llm-mailroom`
and is recorded there, not here.

## [Unreleased]

### Added

- **Insurance-claim subclass alignment with the v8 synthetic LOB claims**
  (HUB-041, 2026-09-03): the mailroom-corpus v8 GT (`eafe1ab4`) carries SIX
  insurance subclasses (carrier/inpatient/outpatient/pde + property 200
  GNOTHEIA + auto 150 BDR; 50 strata) but several surfaces still taught or
  accepted only the four CMS tokens. Landed: dojo `corpus.py`
  `DOC_TYPE_SUBCLASSES`/`CORPUS_SUBCLASS_SURFACES` + `mailroom.py`
  `HUB_SUBCLASS_INVENTORIES` gain property/auto (v8 counts pinned in tests);
  entity `sorter_agent.py` `INSURANCE_CLAIM_SUBCLASSES` (flows into the
  DOCCLASS/PILOT `doc_subclass` enums — property/auto rows are now scoreable);
  The-Mailroom `pipeline_schema.DOC_SUBCLASS_BY_CLASS`; llm-mailroom
  `doc_inventories` fallback catalog + `taxonomy.yaml`/sorter insurance
  descriptions; sandbox fixture gains property/auto rows. **New prompt
  versions under the mailroom naming convention** (human directive; existing
  `*_docclass_*` keys are frozen experiment identity):
  `sorter_mailroom_v0` (extended arm, off v7) and `sorter_mailroom_pilot_v0`
  (pilot arm, off pilot v3) extend rule 40 with the two LOB tokens — defaults
  unchanged until a same-surface A/B; The-Mailroom
  `mailroom_ui/docclass_prompts.py` mirrors the pilot key byte-identical
  (32 keys). **Subclass-parity layer in `scripts/taxonomy_parity.py`** (all
  classes): the Hub GT vocabulary (pinned per class from `eafe1ab4`) must be
  covered by every subclass catalog surface (dojo catalogs + observed-GT
  table, entity taxonomy `subclasses:` blocks + sorter lists, The-Mailroom
  schema mirror, llm-mailroom doc_inventories fallback + extract claim_type
  inventory) with extras tolerated only from documented rosters; CI path
  triggers extended to the new surface files; verified pre-fix drift is
  detected (mutation checks).

### Fixed

- `release_chain.py cut` no longer requires `## [Unreleased]` to be the file's
  first line — the section header is located anywhere in the CHANGELOG and
  the preamble (title + scope note) is preserved when stamping a release
  section (discovered while cutting v0.2.0).

## [0.2.0] - 2026-09-03

### Added

- **Gmail intake channel + single-document free-triage lane** (HUB-037,
  2026-09-03): the agent mailbox (`llmmailroom@gmail.com`) is a second intake
  route in `packages/llm-mailroom` — stdlib IMAP-SSL poller embedded in the
  watcher (the lock holder stays the single intake authority), `/upload`
  sidecar routing, `[M:<id>]` subject matters, `\Seen` + Message-ID dedup,
  sender allowlist, ✅ check reaction at claim time (both routes, with a
  terminal-stage retry + `reactions_failed` counter), on-thread completion
  echoes, intake awareness on every terminal manifest, and the FREE-model
  single-document triage lane (`agents/gmail_triage.py`, `z-ai/glm-5.2:free` —
  free models kept deliberately): core pipeline steps without the paid agents
  (deterministic prep → triage classification → auditable-hash archive → echo)
  with its own `triage_*` audit section, a deterministic capability pre-check
  that honestly hands off oversized/vision-only/scanned documents to the full
  paid pipeline (`intake.triage_handoff`), and all five canonical doc types
  validated through the lane. Multi-document emails run the full paid
  pipeline (triage never dispatched).
- **Intake agent v2 — triage + clean + prepare** (HUB-038, 2026-09-03): the
  pipeline's first node is now a SINGLE `intake` node — the intake agent IS
  the ingest specialist (human directive: the ingest/intake split was an
  unintentional naming mistake; unified constellation-wide). The
  LLM-assisted pass (one fused call per window) TRIAGES (advisory read —
  same vocabulary-clamped shape as the free triage team, fed to the sorter as
  a labeled prior), CLEANS (gated structural repair, re-normalized through
  the deterministic dojo clerk so `prep_invariants` hold), and PREPARES
  (validated section map). **No-truncation doctrine (human directive):**
  documents are NEVER truncated — anything past an input budget is processed
  in overlapping sliding windows (`sliding_windows`, paragraph-boundary, 15%
  overlap) so every character is read; the sorter classifies window-by-window
  and merges deterministically (plurality vote, mean confidence of agreeing
  windows), the retry path no longer slices text, and partial-window cleaning
  is never spliced. Cost + efficiency: the LLM pass fires only for
  messy/over-budget documents on the cheapest paid model (`qwen3.7-flash`);
  `MAILROOM_LLM_INTAKE=0` disables; failures fail soft. Prompt registry
  15 → 17 (`mailroom-gmail_triage`, `mailroom-intake`); model registry gains
  the free `z-ai/glm-5.2:free` tier.
- **Ingest/intake unification rename sweep** (HUB-038 follow-up,
  2026-09-03): graph node `ingest` → `intake` (span `intake-document`; the
  `ingested` audit event stays — compliance vocabulary) across the whole
  constellation: llm-mailroom (`entry_route`, `intake_node`, tracing
  registry), The-Mailroom (`Stage.INTAKE` enum, `pipeline_schema.py`
  mirrors, `trace_interpreter.py`, TUI labels, web/hosted JS stage maps,
  tests, demo scripts), agent-mailroom (`pipeline/ingest.py` →
  `intake.py`), local-mailroom-sandbox and llm-dojo-scoring span mirrors,
  and the pipeline lab notebook.
- **Gmail free-triage production-pilot readiness** (HUB-039, 2026-09-03):
  sender-allowlist pilot roster documented in `packages/llm-mailroom`
  `.env.example` (production pilot roster; empty = accept all).
- **Propagation sweep — all 10 feeder repositories in line with the
  monorepo** (HUB-005 reopened, 2026-09-03): HUB-038/039 payload propagated
  upstream via `sync_packages.py` — llm-mailroom (16 files), The-Mailroom
  (22), agent-mailroom (7 + the `ingest.py`→`intake.py` renames carried by a
  real subtree pull + full-history subtree push after the HUB-021 patch path
  refused the cursor gap), llm-dojo-scoring (1), local-mailroom-sandbox (1);
  cursors re-baselined per package in `scripts/packages_sync.json`.

- **mailroom-corpus v8 — insurance LOB expansion + full GT conformance**
  (HUB-028, 2026-09-02): the corpus grows 1,650 → **2,000 rows** (strata
  48 → 50) with (a) +200 `property` rows from
  `gratex/GNOTHEIA-synthetic-insurance-dataset` (Apache-2.0 — FNOL bundles
  stratified by loss event, determination `pending`), (b) +150 `auto` rows
  from `bdr-ai-org/insurance-motor-claims-decision-v1` (MIT — decision
  letters stratified by accident type × APPROVE/REVIEW/REJECT with all
  reject rows, feature-grounded denial reasons, adjuster pseudonyms), and
  (c) full GT conformance: intent/subject_matter/keywords + intent
  provenance populated on ALL 950 insurance rows (600 CMS backfilled via
  deterministic template derivation — was 246/600 subject/keywords, 600/600
  intent; 200 property + 150 auto authored at build), claimed_amount
  recovered from doc text on 10 v7 gap rows, metadata union
  (source_dataset/source_revision/source_row_id/lob/peril/license) on every
  entry, and **test-split nullification** (96 test insurance rows carry
  zero empty class-relevant keys). Published via the centralized
  corpus-eda helpers with sha256 local==hub verification; card v8 +
  §84 hardening sections; datasets-server conversion green. XpertSystems
  samples (ins001/007/hlt015) excluded for CC-BY-NC-4.0 license conflict;
  INSURBIAS (CC-BY-4.0) deferred to v9. Builder: `v8_build.py` +
  `scripts/build_v8.py` (7 new tests; corpus-eda suite 73 passed).
- **§84 hardened release rebuilt on the v8 base** (HUB-032, 2026-09-02):
  the interleaved HUB-028/HUB-022 publishes left the Hub mixed (blind
  `default` 2,000 rows vs `ground_truth` 1,650×60) — the rebuild applies
  the identity → eval_contract → §14A hardening chain to ALL 2,000 rows and
  republishes `ground_truth` (60 cols) + `bundles` + `fixtures` via
  `scripts/publish_hardened.py`. Published v7 `document_id`s unchanged
  (0 drift over 1,474 train rows); the v8 LOB rows (200 GNOTHEIA + 150 BDR)
  carry their own `source_corpus`/`annotation_source` (via
  `metadata.source_dataset`) and pinned upstream `source_revision` instead
  of collapsing into the CMS class map; annotation provenance counts now
  950 synthetic (600 DE-SynPUF + 200 GNOTHEIA + 150 BDR);
  thread reconstruction unchanged (19 rows in 7 threads — all
  correspondence; insurance rows carry no custodian). Bundles re-derived
  over the v8 base (anchor sets shift — insurance family now spans
  carrier + auto anchors); fixtures byte-identical. Card §84 section
  refreshed; sha256 local==hub (10/10); all §91 release gates green;
  corpus-eda suite 73 passed.
- **§84 v0.3 STREAM eval tier** (2026-09-02): NEW `streams` config (§27–§29/
  §48) — `RUN-SIM-001` interleaves the 10 bundle matters round-robin
  (A1 B1 A2 C1 B2 … — §28 never matter-contiguous) with 12 no-matter
  `distractor` rows on a 4-position cadence (§29); every row carries
  `simulation_run_id` + `sequence_position` (strictly reproducible, §27).
  62 rows / 39 cols; published + sha256-verified (13/13). Stream builder
  `mailroom_eda.bundles.build_streams` with 3 new tests.
### Changed

- The-Mailroom stage enum + TUI/web/hosted labels: `ingest` → `intake`
  (visualizer mirrors the unified pipeline topology).
- `agents/sorter.py` bypasses the vendored HEAD+TAIL truncation — over-budget
  documents classify in sliding windows with a deterministic merge; the
  advisory intake prior + retry preamble reach every window.

### Fixed

- Gmail smoke mock hermetics: `run_mock` now forces the mock sender +
  allowlist — the HUB-039 `.env` pilot roster had started rejecting the mock
  sender (smoke is hermetic against the real `.env`).
- Sync-cursor/content handling for renamed package paths: a real subtree
  pull + full-history subtree push is now the documented path when a
  monorepo-side rename leaves the upstream tip uncontained (patch push
  cannot carry deletions).

## [0.1.0] - 2026-09-02

First hub release: the monorepo as development source of truth for the
LLM-Mailroom constellation — 10 workspace packages, the governance stack, the
sync driver, and the hardened mailroom-corpus lineage (renamed from
docclass-merged). Package versions at this tag: llm-mailroom v0.6.0,
llm-dojo-scoring v0.13.0, llm-entity-extraction v0.21.0, The-Mailroom v0.3.0,
agent-mailroom v0.2.0, local-mailroom-sandbox v0.1.0.

### Added

- **Monorepo + uv workspace** (HUB-001): 9 family repos imported via git
  subtree (mailroom-corpus-eda followed as the 10th, HUB-007); one uv
  workspace, one lockfile, one virtualenv; member dependencies resolve via
  `[tool.uv.sources]` workspace redirects while published git pins stay
  intact; monorepo-aware test repairs (import-shadow markers, pruned-asset
  skip guards, UTC/CWD anchoring).
- **Sub-package sync driver** (HUB-002, HUB-021): `scripts/sync_packages.py`
  (status / pull / push / snapshot over git subtree) with the HUB-021
  hardening — blob-tree containment oracle (gitignore-aware; pruned heavy
  assets are doctrine, not drift), cursor-gap refusal on `snapshot` unless
  `--force`, re-baseline guard that kills the pull re-import loop, scripted
  `push --patch` for non-fast-forward cursors, and per-package monorepo-ahead
  payload surfaced in `status`.
- **GitHub governance tooling** (HUB-014): `scripts/board_state.py`
  (status/card/check/sync-issues/project-init/project-sync over
  `governance/TASKS.md`), declarative label taxonomy (`.github/labels.json`)
  + `scripts/github_labels.py` audit, YAML issue/PR templates, blocking CI
  gate (`.github/workflows/board-governance.yml`), optional Projects v2
  mirror.
- **Document-class taxonomy-parity gate** (HUB-019 §65A):
  `scripts/taxonomy_parity.py` — strict AST-level equality across taxonomy
  sources (mailroom sorter vocab, specialist registry, dojo corpus types,
  entity pilot universe, v7 taxonomy doc, sandbox fixtures), wired blocking
  into CI.
- **Corpus governance, docclass-merged → mailroom-corpus** (HUB-019/022/023):
  baseline freeze `docclass-merged-v0.1-working` at the true tip with audit
  manifest (`scripts/baseline_audit.py`), canonical dataset contract
  (`docs/DOCCLASS_CONTRACT.md`), identity/provenance/hash schema
  (`document_id` from source identity, content hashes), contract test suite
  (15 passed), P1 eval hardening (`eval_contract`, class×subclass×source×field
  coverage matrix, §14A matter/group backfill decision); the HF dataset was
  renamed `Lucius-Morningstar/docclass-merged` → `Lucius-Morningstar/
  mailroom-corpus` (Hub move preserves history; 57 monorepo files updated
  with prompt-version keys and trace tags immutable).
- **Version-controlled GitHub wiki** (HUB-017): `docs/wiki/` (10 pages) +
  `sync-wiki.sh` (`--check` drift mode).
- **Corpus EDA deliverables tracked in full** (HUB-008 exception): figures,
  interactive HTMLs, tables, and summary reports are canonical in the
  monorepo — never pruned.

### Changed

- Root docs reworked for the monorepo (README architecture map, AGENTS.md
  governance + workspace rules, task board) — HUB-003; docs-currency sweeps
  after every surface-touching card (HUB-010, HUB-016, HUB-018).
- Heavy-asset doctrine: docs demos/screenshots, sample PDFs, and report
  archives are pruned from the hub (HUB-003/004) — with the corpus-EDA
  deliverables exception above.

### Fixed

- `run_all.py` subset runs / `--no-interactive` no longer clobber
  `reports/SUMMARY_REPORT.*` (HUB-009); P3 figure counter corrected 27 → 30
  to disk truth (HUB-012).
- Sync-cursor incident mechanics structurally guarded after the HUB-012/013/
  018 reconciliations (containment oracle + gap refusal + re-baseline, HUB-021).
- Upstream drift reconciled across all packages; `sync status` 10/10 in sync
  (HUB-004, HUB-018); stale pins/counts swept (HUB-010/016/018).

[Unreleased]: https://github.com/Exios66/mailroom-dev/compare/v0.2.0...HEAD
[0.1.0]: https://github.com/Exios66/mailroom-dev/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Exios66/mailroom-dev/releases/tag/v0.1.0
[0.2.0]: https://github.com/Exios66/mailroom-dev/releases/tag/v0.2.0

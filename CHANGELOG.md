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

[Unreleased]: https://github.com/Exios66/mailroom-dev/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Exios66/mailroom-dev/releases/tag/v0.1.0

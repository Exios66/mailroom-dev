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

# AGENTS.md — Mailroom-Corpus-EDA

Exploratory data analysis (and the centralized HF upload helpers) for the
[`Lucius-Morningstar/docclass-merged`](https://huggingface.co/datasets/Lucius-Morningstar/docclass-merged)
corpus — 1,650 legal documents across 5 doc_types (insurance_claim,
merger_agreement, contract, correspondence, corporate_record), 48 strata.

Mirror of the standalone `Exios66/Mailroom-Corpus-EDA` repo; in the monorepo
it lives at `packages/mailroom-corpus-eda` as a virtual uv member (no build).
Never edit it from both places in one session — develop here, sync via
`scripts/sync_packages.py` in mailroom-dev.

## Layout

- `src/mailroom_eda/` — the EDA + HF library (imports as `mailroom_eda`)
  - `config.py` — paths, doc types, colors, token budgets, matplotlib setup
  - `download.py` — corpus acquisition (HF snapshot) + manifest parsing
  - `integrity.py` — P1 structural integrity & provenance audit
  - `composition.py` — P2 strata / imbalance / provenance / metadata coverage
  - `visualizations.py` — P3 static PNG figures (30) + EDA tables
  - `visualizations_interactive.py` — P4 Plotly HTML figures (18)
  - `hf_interface.py` — centralized Hub client (upload, sha256 verify)
  - `dataset_export.py` — cast-safe JSONL (KANBAN-076/088), parquet staging, manifests
  - `docclass_uploader.py` — docclass v6 publish, surgical card render, leak guard
  - `token_budget.py` — token estimation & budget coverage
- `scripts/` — CLI wrappers: `publish_docclass.py`, `export_docclass.py`, `verify_hf.py`
- `run_all.py` — 6-phase pipeline (P0 download → P5 export staging)
- `reports/` — generated artifacts (figures/, figures_interactive/, tables/, SUMMARY_REPORT.md)
  - ALL of `reports/` is tracked in full per human directive (HUB-008) — never
    prune it and never commit regenerated variants of `figures_interactive/`:
    each Plotly HTML embeds a random per-render div UUID, so regenerated
    figures can never be byte-identical. The committed files are the canonical
    upstream bytes; treat local regeneration as scratch output only.

## Commands

```bash
.venv/bin/python run_all.py                      # full pipeline P0-P5
.venv/bin/python run_all.py --phases P3 P4       # figures only
.venv/bin/python scripts/export_docclass.py --help
```

**Subset-run hazard**: any `--phases` subset rewrites `reports/SUMMARY_REPORT.*`
from only the phases you ran — a figures-only run clobbers the full-corpus
summary with partial stats. After a subset run, re-run all phases or restore
the summary from git before committing.

## Conventions

- **Data never commits**: `data/` and `.venv/` are gitignored; `data/parquet`
  is re-fetched from the Hub by `download.py`.
- **HF uploads** use the centralized modules in `mailroom_eda.hf_interface`
  / `dataset_export` / `docclass_uploader` — never ad-hoc upload code.
  Metadata must be cast-safe (uniform keys, string-typed), JSONL must be
  line-boundary-safe (U+2028/U+2029/NEL), and labels NEVER ride in the blind
  `default` config.
- **Interactive HTML figures** (~4MB each, Plotly-inlined) are tracked in full
  in the monorepo per human directive (HUB-008) — see the `reports/` rule
  above. Regenerable via `run_all.py --phases P4`, but regenerated output is
  scratch (random per-render UUID); never commit it over the canonical bytes.
- **Split rule**: md5(filename) % 10 == 0 → test (90/10), stable across rebuilds.
- **Determinism**: `RANDOM_STATE = 42`; rebuilds of JSONL/parquet must be
  byte-identical (sorted rows, deterministic order).

## HF facts (verified 2026-08-31)

- Repo: `Lucius-Morningstar/docclass-merged` (v6 rev2, 1,650 rows).
- Composition: insurance_claim 600, contract 509, correspondence 350,
  merger_agreement 152, corporate_record 39.
- Configs: `default` (blind, 4 cols) + `ground_truth` (28 cols incl. labels).
- Split: train 1,474 / test 176 on both configs; filename sets equal.
- Related: `enron-correspondence-dedup`, `mailroom-cuad-contracts-full`,
  `mailroom-s1-corporate-records`, `mailroom-maud-contracts`.

See the `huggingface` opencode skill for the full Hub-interfacing workflow.
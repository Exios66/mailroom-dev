# HF corpus — docclass-merged

The corpus family is published on the
[Lucus-Morningstar HF org](https://huggingface.co/Lucius-Morningstar) via
the **centralized** helpers in
`packages/mailroom-corpus-eda/src/mailroom_eda/` — never ad-hoc upload code.

## docclass-merged (verified 2026-08-31, HUB-013/012)

| Fact | Value |
| --- | --- |
| Dataset | [Lucius-Morningstar/docclass-merged](https://huggingface.co/datasets/Lucius-Morningstar/docclass-merged) |
| Schema | **v7** (issue #5 intent hydration) |
| Rows | **1,650** — insurance_claim 600 · contract 509 · correspondence 350 · merger_agreement 152 · corporate_record 39 |
| Configs | `default` (blind, 4 cols) + `ground_truth` (27-key GT schema incl. intent provenance) |
| Split | train 1,474 / test 176, both configs; md5(filename) % 10 == 0 → test (stable) |
| Strata | 48 (expected × expected_subclass) |
| HF revs | data tip `1acd2600` · card rev `fc1f211c` (pretty_name v6→v7) |
| v7 intent hydration | 350/350 correspondence rows carry a canonical 8-class intent (96 manual + 254 llm_zero_shot + 162 AESLC/Enron joins, 1 flagged_review); 100% coverage, all 8 classes in test |

## The ground-truth schema (27 keys)

`label_evidence, content_topic, topic_evidence, sentiment_score,
sentiment_label, sentiment_evidence, claim_number, policy_number, insurer,
insured_party, claim_type, date_of_loss, date_filed, claimed_amount,
adjuster, damages_description, coverage_determination, denial_reasons,
supporting_documents, cuad_clause_labels, maud_clause_labels, intent,
subject_matter, keywords, intent_source, intent_confidence, intent_status`

Corpus strata vocabulary (per doc type, used by eval targets):

| Doc type | Subclasses (examples) |
| --- | --- |
| contract | 26 incl. Consulting Agreements, Development, IP, Hosting |
| corporate_record | articles_of_incorporation, bylaws, other, powers_of_attorney, rights_instrument |
| correspondence | attorney_demand, demand, email, letter, meeting_request, memo, notice, press_release |
| insurance_claim | carrier, inpatient, outpatient, pde |
| merger_agreement | all_cash, all_stock, mixed_cash_stock, mixed_cash_stock_election, other |

## The EDA pipeline (P0–P6)

```bash
cd packages/mailroom-corpus-eda
uv run python run_all.py                 # full pipeline; only a full run writes SUMMARY_REPORT.*
uv run python run_all.py --phases P3 P4  # figures only (subset runs never clobber the summary)
```

P0 download/manifest → P1 integrity → P2 composition → P3 static PNGs
(**30**) → P4 interactive Plotly HTMLs (18) → P5 JSONL/parquet export →
P6 intent-coverage audit. Deterministic (`RANDOM_STATE=42`); rebuilds of
JSONL/parquet are byte-identical.

**Canonical-bytes rule**: the committed `reports/` figures are canonical —
regenerated interactive HTMLs embed a random per-render UUID and are never
byte-identical; treat local regeneration as scratch output only (HUB-008).
`SUMMARY_REPORT.json` reports `figures: 30` (HUB-012 fixed the stale 27
counter and published the fix upstream).

## Upload helpers

`hf_interface` (Hub client, sha256 verify) · `dataset_export` (cast-safe
metadata, line-boundary-safe JSONL, parquet staging) · `docclass_uploader`
(v7 publish, surgical card render, leak guard) · `intent_backfill`
(checkpointed correspondence intent hydration). See the `huggingface`
opencode skill for the full workflow.

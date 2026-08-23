# claims-data-eda

Full-corpus exploratory data analysis of the **CMS 2008–2010 DE-SynPUF
(Sample 1)** Medicare synthetic claims corpus, and production of a
pipeline-ready **`insurance_claim`** dataset for the llm-mailroom ecosystem.

The DE-SynPUF stands in for the mailroom taxonomy's **`insurance_claim`** doc
class (`InsuranceClaimExtraction` schema + `insurance_claims_specialist`):
every claim event is rendered as a plain-text **Medicare Summary Notice /
pharmacy statement** with ground-truth extraction fields aligned to the
specialist's schema.

## Corpus

CMS DE-SynPUF Sample 1 (fully synthetic; "very limited inferential research
utility" per CMS — this is pipeline evaluation substrate, not epidemiology):

| File type | Events | Unique IDs | Σ paid |
|---|---:|---:|---:|
| Inpatient claims | 66,773 | 66,705 | $639M |
| Outpatient claims | 790,790 | 779,815 | $225M |
| Carrier claims (physician/supplier) | 4,741,335 | 4,741,335 | $415M |
| Prescription drug events (PDE) | 5,552,421 | 5,552,421 | $341M |
| **Total claim events** | **11,151,319** | 11,140,276 | **~$1.62B** |

plus **116,352 beneficiaries** merged across three yearly Beneficiary Summary
files (perfect linkage: zero orphan events).

### Provenance

Five archives still download live from CMS; **three are gone from cms.gov and
were recovered from Internet Archive Wayback Machine captures** (2010
Beneficiary Summary, Carrier Claims A/B split, Prescription Drug Events). All
eight ZIPs are sha256-manifested into `data/raw/MANIFEST.json`.

## Headline findings

* **Heavy-tailed costs**: inpatient payments span $3K (p10) to $57K (p99);
  sampling must bucket on log-cost or the tail vanishes from eval sets.
* **Concentration everywhere**: top 1% of carrier providers bill **23.9%** of
  physician lines; top 20% of patients generate **42.4%** of all events.
* **Stationary synthetics**: demographics, chronic-condition prevalence
  (ischemic heart disease 36%, diabetes 28%, heart failure 25%) and monthly
  volumes barely move across 2008–2010 — a fingerprint of template-driven
  generation.
* **Clean GT anchors**: empty-diagnosis rates ≤0.7%; every event joins its
  beneficiary record.
* **No negative class**: SynPUF contains only adjudicated-*paid* FFS claims —
  `coverage_determination` is always "approved", denial ground truth does not
  exist here.
* **Generator artifact**: inpatient procedure slots mix true ICD-9 procedures
  with frequent diagnosis codes — flagged for extraction-target hygiene.

Full analysis: [`reports/eda/report.md`](reports/eda/report.md) · condensed:
[`reports/eda/findings.md`](reports/eda/findings.md)

## Governed Repository Ecosystem

This repo is the **insurance-claims data-production node** of a governed
evaluation family under [Exios66](https://github.com/Exios66):

| Repository | Role |
|---|---|
| [`llm-mailroom`](https://github.com/Exios66/llm-mailroom) | Upstream taxonomy governor — owns `insurance_claim` doc class & `InsuranceClaimExtraction` schema our GT targets |
| **claims-data-eda** (this repo) | Full-corpus EDA + rendered-EOB dataset production for DE-SynPUF Sample 1 |
| [`llm-entity-extraction`](https://github.com/Exios66/llm-entity-extraction) | Direct downstream consumer — ingests `pipeline.jsonl` via `build_docclass_merged.py` |
| [`Enron-Evaluation-Environment`](https://github.com/Exios66/Enron-Evaluation-Environment) | Sibling correspondence node; structural template for this repo |
| [`atticus-investigation`](https://github.com/Exios66/atticus-investigation) | Adjacent LegalBench prompt-engineering eval environment |

Handoff contract & wiring commands: [`reports/pipeline/README.md`](reports/pipeline/README.md).

## Quick Start

```bash
# 1. Acquire the corpus (8 ZIPs ~356 MB; idempotent, resumable, sha256-manifested)
python scripts/acquire_synpuf.py

# 2. Build the unified index (~11.2M claim events -> gzipped JSONL, ~700 MB)
python scripts/build_corpus_index.py

# 3. Full EDA -> reports/eda/{report.md,findings.md,corpus_stats.json,figures/}
python scripts/eda/explore_cms.py

# 4. Pipeline-ready stratified sample -> data/cms/pipeline.jsonl
python scripts/build_pipeline_dump.py --n 400

# 5. Human review artifact + validation
python scripts/spot_check.py        # verbatim audit -> reports/eda/spot_check.csv
pytest tests/ -v                    # 30 tests, no corpus data needed
```

Smoke-test any stage with `--dry-run` / `--limit N`. All data lives under
gitignored `data/` (~5 GB raw CSVs regenerable from kept ZIPs at any time).

## Repo layout

```
├── AGENTS.md                           # Agent-facing operational guide
├── scripts/
│   ├── acquire_synpuf.py               # Download + verify + extract (Wayback-aware)
│   ├── build_corpus_index.py           # Normalize 8 CSVs -> compact gzipped JSONL
│   ├── render_eob.py                   # Deterministic EOB renderer + GT builder
│   ├── build_pipeline_dump.py          # Stratified reservoir sample (coverage contract)
│   ├── spot_check.py                   # Human-review CSV w/ verbatim audit
│   ├── publish_hf_dataset.py           # HF Hub publisher (schema guard + VERIFY: GREEN)
│   └── eda/explore_cms.py              # Full-corpus EDA engine -> reports/eda/
├── reports/
│   ├── eda/                            # Committed EDA output (12 figures + stats)
│   └── pipeline/README.md              # Wiring into llm-mailroom / llm-entity-extraction
└── tests/test_pipeline.py              # 30 unit tests (normalizers/renderer/GT/dump shape)
```

## Pipeline output shape

`data/cms/pipeline.jsonl` — flat streamer-dump format consumed by
`llm-entity-extraction` eval runners:

```json
{
  "filename": "carrier:887013386172596.txt",
  "doc_text": "MEDICARE SUMMARY NOTICE -- PHYSICIAN/SUPPLIER CLAIM (Part B) ...",
  "prompt": "",
  "expected": "insurance_claim",
  "expected_subclass": "carrier",
  "metadata": {
    "record_id": "carrier:887013386172596",
    "diagnosis_codes": ["25000"], "hcpcs_codes": ["99213"],
    "source_dataset": "cms-de-synpuf-2008-2010-sample1",
    "ground_truth": {
      "claim_number": "887013386172596", "policy_number": "942DF76C4B9D257F",
      "insurer": "CMS Medicare", "insured_party": "MARTIN, DONNA",
      "claim_type": "health", "date_of_loss": "2008-09-23",
      "claimed_amount": 110.0, "coverage_determination": "approved",
      "denial_reasons": [], "...": "..."
    }
  }
}
```

Sampling stratifies by subtype × year × log-cost band (high-cost floor ≥15% per
type); a coverage contract refuses samples missing any non-empty stratum.

## Verbatim GT contract

Every scalar ground-truth value appears **literally** in the rendered document
text — asserted by `render()`, machine-audited in `spot_check.csv`
(24/24 PASS), and unit-tested. This lets llm-mailroom's deterministic field
scorer verify extraction without fuzzy fallbacks.

## Hugging Face

Publishes to
[`Lucius-Morningstar/cms-desynpuf-insurance-claims`](https://huggingface.co/datasets/Lucius-Morningstar/cms-desynpuf-insurance-claims)
with deterministic family split (`md5(record_id) % 10 == 0` → test):

```bash
export HF_TOKEN=hf_...
python scripts/publish_hf_dataset.py --dry-run   # stage + manifest only
python scripts/publish_hf_dataset.py             # upload + sha256 VERIFY: GREEN
```

Agents: see `.env` handling notes in [AGENTS.md](AGENTS.md). Never commit tokens.

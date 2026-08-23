# CMS DE-SynPUF Claims — Integration into llm-mailroom / llm-entity-extraction

This documents how the CMS 2008-2010 DE-SynPUF (Sample 1) corpus slots into the
mailroom document taxonomy as the **`insurance_claim`** doc class. The handoff
artifact is `data/cms/pipeline.jsonl` (gitignored, regenerable via
`scripts/build_pipeline_dump.py`).

## What the dump is

- ~400 rendered EOB-style documents sampled from the 11.2M-event index,
  stratified by claim subtype (`inpatient` / `outpatient` / `carrier` / `pde`),
  service year (2008/2009/2010), and log-cost band — with a ≥15% high-cost
  floor per type so the heavy tail is always represented, and a **coverage
  contract** that refuses to emit a sample missing any non-empty stratum.
- Row shape (flat streamer-dump format consumed by the docclass eval runners):

```json
{
  "filename": "carrier:812340000000123.txt",
  "doc_text": "==========================================\nMEDICARE SUMMARY NOTICE -- PHYSICIAN/SUPPLIER CLAIM (Part B)\n...",
  "prompt": "",
  "expected": "insurance_claim",
  "expected_subclass": "carrier",
  "metadata": {
    "record_id": "carrier:812340000000123",
    "claim_subtype": "carrier",
    "year": 2009,
    "provider_npis": ["1999999999"],
    "diagnosis_codes": ["25000"],
    "hcpcs_codes": ["99213"],
    "source_dataset": "cms-de-synpuf-2008-2010-sample1",
    "ground_truth": {
      "claim_number": "812340000000123",
      "policy_number": "000B34FD8E45D1A2",
      "insurer": "CMS Medicare",
      "insured_party": "MILLER, JAMES",
      "claim_type": "health",
      "date_of_loss": "2009-04-02",
      "date_filed": "2009-04-08",
      "claimed_amount": 5400.0,
      "adjuster": null,
      "damages_description": "...",
      "coverage_determination": "approved",
      "denial_reasons": [],
      "supporting_documents": ["facility provider 24XYZ"]
    }
  }
}
```

- **Verbatim contract**: every scalar GT value appears literally in `doc_text`,
  so llm-mailroom's deterministic field scorer + factuality audit can verify
  extraction without fuzzy fallbacks. Audited in `reports/eda/spot_check.csv`.

## GT mapping to InsuranceClaimExtraction

| Specialist field | GT source | Coverage note |
|---|---|---|
| claim_number | CLM_ID (+PDE_ID for fills) | exact |
| policy_number | DESYNPUF_ID | exact; stable join key |
| insurer | constant "CMS Medicare" | by construction |
| insured_party | deterministic pseudonym(bene_id) | no real names exist |
| claim_type | constant "health" | line-of-business |
| date_of_loss | CLM_FROM_DT / SRVC_DT | exact ISO |
| date_filed | CLM_THRU_DT / discharge_dt | proxy |
| claimed_amount | CLM_PMT_AMT / TOT_RX_CST_AMT | paid amount |
| adjuster | — | **absent** in SynPUF |
| damages_description | template from dx/procedure/HCPCS/NDC codes | faithful summary |
| coverage_determination | "approved" | all SynPUF claims are paid |
| denial_reasons | [] | no denials exist in SynPUF |
| supporting_documents | provider/facility/NDC refs | rendered list |

## Known evaluation caveats

1. **No negative class** — every document is an approved health claim.
   Denial letters / reservation-of-rights ground truth must come from another
   source before evaluating `denial_reasons` or determination routing.
2. **Single line of business** — `claim_type` is always `health`; auto/property/
   liability classification signal is out of scope for this corpus.
3. **Fully synthetic** — treat as pipeline evaluation substrate, not
   epidemiology (CMS's own caveat).
4. **Heavy-tailed amounts** — sample stratifies on log-cost bands so p95+ claims
   appear despite the pareto tail.

## Wiring commands

```bash
# regenerate everything from raw archives (~2 min download + ~20 min index)
python scripts/acquire_synpuf.py
python scripts/build_corpus_index.py
python scripts/eda/explore_cms.py          # needs to run once: emits cost percentiles used by sampler
python scripts/build_pipeline_dump.py --n 400

# validate
pytest tests/ -v
python scripts/spot_check.py               # verbatim audit -> reports/eda/spot_check.csv
```

In `llm-entity-extraction`, feed `pipeline.jsonl` through the same merge path
used for Enron (`build_docclass_merged.py`) with `expected=insurance_claim`;
the sorter's subclass dimension should register
`inpatient|outpatient|carrier|pde` under the insurance_claim class.

## Hugging Face mirror

The full dump publishes to
[`Lucius-Morningstar/cms-desynpuf-insurance-claims`](https://huggingface.co/datasets/Lucius-Morningstar/cms-desynpuf-insurance-claims)
(train/test split = `md5(record_id) % 10 == 0 -> test`). Publisher enforces a
schema guard and post-upload sha256 verification (`VERIFY: GREEN`):

```bash
export HF_TOKEN=hf_...
python scripts/publish_hf_dataset.py --dry-run   # stage + manifest only
python scripts/publish_hf_dataset.py             # upload + verify
```

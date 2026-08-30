# Key Findings — CMS DE-SynPUF Sample 1 EDA

- **Corpus shape**: 116,352 beneficiaries; 11,151,319 claim/PDE event rows collapsing to 11,140,276 unique claims/fills (inpatient/outpatient carry multiple bill segments).
- **Perfect linkage**: 11,151,319 events join cleanly to beneficiary summaries on DESYNPUF_ID; 0 orphans. Cross-file GT joins are trustworthy.
- **Demographic skew**: age bands and chronic-condition prevalence are stationary across 2008–2010 (synthetic templates), with 5,461 deaths recorded in-window.
- **Costs are heavy-tailed**: inpatient p99 reaches $57.0K; stratified sampling MUST bucket on log-cost, not raw cost, or the tail never appears in eval sets.
- **Concentration**: top 1% of carrier providers bill 23.9% of physician lines; top 20% of patients generate 42.4% of all events.
- **Diagnosis coverage is high**: empty-diagnosis rates stay below 0.7% across claim types — ICD-9 lists are reliable GT anchors.
- **Generator artifact**: inpatient `ICD9_PRCDR_CD_*` slots mix real procedure codes with frequent diagnosis codes (4019, 25000) -- a synthetic-generation quirk; flagged for anyone using procedure fields as extraction targets.
- **Pipeline fit**: maps 1:1 onto the mailroom `insurance_claim` schema except `adjuster` (absent) and `coverage_determination`/`denial_reasons` (always approved/empty — no negative class exists in SynPUF).
- **Provenance caveat**: Sample-1's 2010 beneficiary file plus Carrier (A/B) and PDE archives were no longer hosted by CMS and were recovered from Internet Archive captures (manifested in data/raw/MANIFEST.json).

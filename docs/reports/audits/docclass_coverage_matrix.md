# docclass coverage matrix (plan §40–§41)

Generated from the local pinned snapshot — 1650 rows, 5 classes, 48 class × subclass strata.

## Class view (§40)

| class | rows | strata | source | specialist |
|---|---|---|---|---|
| `contract` | 509 | 26 | `theatticusproject/cuad` | `contracts_specialist` |
| `corporate_record` | 39 | 5 | `sec_edgar` | `corporate_records_specialist` |
| `correspondence` | 350 | 8 | `Lucius-Morningstar/enron-correspondence-dedup` | `correspondence_specialist` |
| `insurance_claim` | 600 | 4 | `cms_desynpuf` | `insurance_claims_specialist` |
| `merger_agreement` | 152 | 5 | `maud` | `contracts_specialist` |

## Field coverage per specialist (§41)

### `contract` (509 rows, `contracts_specialist`)

| field | populated | coverage |
|---|---|---|
| `cuad_clause_labels` | 509 | 100% |

### `corporate_record` (39 rows, `corporate_records_specialist`)

| field | populated | coverage |
|---|---|---|
| `intent` | 0 | 0% |
| `keywords` | 38 | 97% |
| `subject_matter` | 38 | 97% |

### `correspondence` (350 rows, `correspondence_specialist`)

| field | populated | coverage |
|---|---|---|
| `content_topic` | 350 | 100% |
| `intent` | 350 | 100% |
| `keywords` | 96 | 27% |
| `sentiment_label` | 350 | 100% |
| `subject_matter` | 96 | 27% |

### `insurance_claim` (600 rows, `insurance_claims_specialist`)

| field | populated | coverage |
|---|---|---|
| `adjuster` | 0 | 0% |
| `claim_number` | 600 | 100% |
| `claim_type` | 600 | 100% |
| `claimed_amount` | 590 | 98% |
| `coverage_determination` | 600 | 100% |
| `damages_description` | 600 | 100% |
| `date_filed` | 597 | 100% |
| `date_of_loss` | 597 | 100% |
| `denial_reasons` | 600 | 100% |
| `insured_party` | 600 | 100% |
| `insurer` | 600 | 100% |
| `intent` | 0 | 0% |
| `keywords` | 354 | 59% |
| `policy_number` | 600 | 100% |
| `subject_matter` | 354 | 59% |
| `supporting_documents` | 600 | 100% |

### `merger_agreement` (152 rows, `contracts_specialist`)

| field | populated | coverage |
|---|---|---|
| `maud_clause_labels` | 152 | 100% |

## Scenario columns (§40)

tested/regression/challenge/multi-document are §40 template columns at zero: the sandbox/pilot fixtures (P1) and the matter/grouping (P2) + recovery (P3) families fill them at their phases — the corpus does not overstate coverage (§14A/§53).

## Strata (§40 rows × subclass)

| class | subclass | rows |
|---|---|---|
| `contract` | `Affiliate_Agreements` | 10 |
| `contract` | `Agency Agreements` | 13 |
| `contract` | `Co_Branding` | 22 |
| `contract` | `Collaboration` | 26 |
| `contract` | `Consulting Agreements` | 11 |
| `contract` | `Development` | 28 |
| `contract` | `Distributor` | 32 |
| `contract` | `Endorsement` | 24 |
| `contract` | `Franchise` | 15 |
| `contract` | `Hosting` | 20 |
| `contract` | `IP` | 17 |
| `contract` | `Joint Venture` | 9 |
| `contract` | `Joint Venture _ Filing` | 14 |
| `contract` | `License_Agreements` | 33 |
| `contract` | `Maintenance` | 34 |
| `contract` | `Manufacturing` | 17 |
| `contract` | `Marketing` | 17 |
| `contract` | `Non_Compete_Non_Solicit` | 3 |
| `contract` | `Outsourcing` | 18 |
| `contract` | `Promotion` | 12 |
| `contract` | `Reseller` | 12 |
| `contract` | `Service` | 28 |
| `contract` | `Sponsorship` | 31 |
| `contract` | `Strategic Alliance` | 32 |
| `contract` | `Supply` | 18 |
| `contract` | `Transportation` | 13 |
| `corporate_record` | `articles_of_incorporation` | 20 |
| `corporate_record` | `bylaws` | 2 |
| `corporate_record` | `other` | 1 |
| `corporate_record` | `powers_of_attorney` | 2 |
| `corporate_record` | `rights_instrument` | 14 |
| `correspondence` | `attorney_demand` | 3 |
| `correspondence` | `demand` | 51 |
| `correspondence` | `email` | 50 |
| `correspondence` | `letter` | 49 |
| `correspondence` | `meeting_request` | 49 |
| `correspondence` | `memo` | 49 |
| `correspondence` | `notice` | 50 |
| `correspondence` | `press_release` | 49 |
| `insurance_claim` | `carrier` | 150 |
| `insurance_claim` | `inpatient` | 150 |
| `insurance_claim` | `outpatient` | 150 |
| `insurance_claim` | `pde` | 150 |
| `merger_agreement` | `all_cash` | 57 |
| `merger_agreement` | `all_stock` | 24 |
| `merger_agreement` | `mixed_cash_stock` | 13 |
| `merger_agreement` | `mixed_cash_stock_election` | 1 |
| `merger_agreement` | `other` | 57 |

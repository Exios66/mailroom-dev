# P5 advanced-evaluation surfaces — status (plan §90, §25; HUB-022)

P5 ("Eventually:") is data-bound: every surface below needs either
pipeline-run traces, expanded corpus content, or both. This document is the
honest status ledger — what exists as scaffold today, what each surface
waits for, and which earlier-phase deliverable unlocks it. Nothing here is
claimed done; per §84B, a surface is done only when its metric is computed
by a green test against real run data.

## Status legend

- **scaffolded** — the derivation/vocabulary exists and is tested; only the
  data is missing.
- **blocked-on-runs** — needs evaluation traces from the pipeline (HF pilot
  runs or simulation runs §27–29).
- **blocked-on-expansion** — needs corpus content that P4's high-priority
  families describe.

## Surfaces

| §90 surface | Status | Unlocked by |
|---|---|---|
| Source-specific failure analysis | blocked-on-runs | P5 runs over the current corpus carry `annotation_source` (P1 provenance fields); any pilot trace can be grouped by source the day runs exist. |
| Format-specific failure analysis | blocked-on-expansion | P4 `format_diversity` (explicitly sequenced low — the corpus is text-native today). |
| Confidence calibration | scaffolded | §70 calibration quartet (`mailroom_eda.fixtures.calibration_quartet`) probes the LIVE bands (`eval_contract.confidence_bands`); computing calibration curves needs pipeline runs over those fixtures (blocked-on-runs once published per §84). |
| Cost/accuracy tradeoffs | blocked-on-runs | Langfuse traces (Observatory) already carry token/cost metadata; analysis surfaces are The-Mailroom/Langfuse work, not corpus work. |
| Recovery-value analysis | scaffolded | §72A arbiter/review fixtures + §58 `FAILURE_STAGES` matrix (`fixtures.failure_stage_matrix`) define first-pass vs. recovered success ground truth; the value computation needs P3 runs. |
| Grouping metrics | scaffolded | §14A verified baseline (19/350 heuristic thread rows; header threads structurally absent) + `mailroom_eda.bundles` synthetic families; pairwise precision/recall (§25) is computable once a published revision carries bundle assignments (§84 decision). |
| Relationship metrics | scaffolded | `RELATIONSHIP_TYPES`/`GROUP_ROLES` closed vocabularies (P1) + bundle `relationships`/`related_document_ids` fields; needs published bundle rows. |
| Stream-level evaluation | blocked-on-runs | Requires `simulation_run_id` (§27–29 interleaving/distractors) which requires published matter/group ids first — the §84A chain: §14A decision (done, verified) → P2 grouping (scaffolded) → publication → simulation. |
| OOD/unknown detection | scaffolded | §68 fixture kinds (`ood_unknown`, `ood_retired_class`) defined and vocabulary-tested; detection rates are measurable only after fixtures publish (§84). |
| Longitudinal regression tracking | scaffolded | §40 scenario columns (`tested`/`regression`/`challenge`/`multi_document`) are the counters this tracking fills; the coverage matrix regenerates deterministically (`scripts/coverage_matrix.py`). |

## §25 corpus-report metric groups — same picture, one line each

- **Classification** — accuracy/subtype computable from GT today; calibration
  and unknown/review rates need runs over published fixtures.
- **Extraction** — field presence/precision/recall/correctness/hallucination
  computable from GT vs. traces (blocked-on-runs); the GT field registry is
  `eval_contract.EXPECTED_EXTRACTION_FIELDS`.
- **Grouping** — matter/group assignment + pairwise metrics scaffolded
  (matter.py, bundles.py); needs published bundle assignments.
- **Operational** — review/retry/first-pass/recovered/irrecoverable rates are
  exactly the §72A fixture expectations; blocked-on-runs.
- **Cost** — Observatory/Langfuse surface, not corpus scope.

## Sequencing summary (§84A chain, current position)

```
P0 done → P1 landed (846c6e83) → §14A verified (0b6ff1f9)
  → P2 scaffolded (bundles.py)      [publication = §84 decision]
  → P3 fixture content scaffolded (fixtures.py)
  → P4 priorities generated (expansion_priorities.py)
  → §84 v0.2 release decision publishes: evaluation-contract fields +
    fixtures + bundle assignments
  → THEN P5 surfaces compute against real runs
```

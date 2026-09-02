# DOCCLASS_CONTRACT.md — the docclass-merged dataset contract

**Status:** canonical bridge between the `Lucius-Morningstar/docclass-merged`
corpus and the Mailroom pipeline. Companion to `docs/v7-taxonomy.md`
(taxonomy doctrine) and `docs/reports/audits/docclass_merged_baseline.md`
(frozen v0.1-working baseline). Plan reference: `docs/docclass-merged-plan.md`
§80–§81.

## 1. What docclass-merged is

docclass-merged is the **canonical Mailroom ingress/evaluation corpus** — the
controlled document universe used to simulate documents arriving at the
Mailroom (plan §1, §93). It exists to answer:

> Given this incoming document or document stream, does Mailroom correctly
> ingest, classify, route, extract, group, validate, adjudicate, retry when
> necessary, and reach the correct final state?

Its multi-source fusion (CUAD + MAUD + EDGAR + Enron + CMS DE-SynPUF) is
intentional: those sources are the document families Mailroom must handle,
not a statistically natural population. Do not "fix" the fusion.

## 2. What it is not

- **Not a model-training dataset** (§1, §93). Splits are evaluation
  partitions for sampling/reproducibility, not ML train/test semantics (§49).
- **Not a generic benchmark** — no artificial class balance, no blind
  leaderboard config (§33, §47, §83). The `default` config is agent-blind
  (no label columns) for evaluation hygiene, not a benchmark surface.
- **Not complete** — it is the current working corpus; coverage gaps are
  recorded honestly in the baseline audit, not papered over.

## 3. Classes

The corpus represents exactly the **five-class live Mailroom taxonomy**
(docs/v7-taxonomy.md): `contract`, `merger_agreement`, `corporate_record`,
`correspondence`, `insurance_claim`. There is no extended live taxonomy
awaiting corpus coverage. `compliance_filing`, `court_opinion`, and
`due_diligence` are **retired former classes** — historical/changelog
vocabulary only (§60); the pipeline config retains a `status: retired`
`compliance_filing` entry as inert machinery (see v7-taxonomy.md §4).
Reintroducing any retired class is a new taxonomy decision with its own
`taxonomy_version` bump — never a silent "restoration".

`merger_agreement` is a **distinct classification class** that shares
extraction machinery with `contract` (§6):

| | |
|---|---|
| classification | `merger_agreement` |
| routing | `contracts_specialist` |
| extraction_schema | `ContractExtraction` |

Classification taxonomy and specialist implementation are separate concerns;
never merge `merger_agreement` into `contract` because they share a
specialist.

## 4. Core concepts

- **Document** — one incoming artifact; the corpus row. Identity is
  `document_id`: unique, deterministic, stable across rebuilds, independent
  of row order / split / Hub config, never a row index (§9). Derivation:
  `mailroom_eda.identity.document_id`.
- **Matter** — the real-world legal/insurance matter a document belongs to
  (grouping concept; `matter_id`). **Group** — a logical bundle within a
  matter (`group_id`, `group_role`). Both are P2 ground truth, gated on the
  §14A backfill methodology (source-native vs. synthetically constructed,
  never silently mixed).
- **`expected_fields`** — the canonical extraction ground truth (§18), scored
  by llm-dojo-scoring's deterministic field scorer (`date`/`id`/`money`/
  `name`/`free_text`/`entity_list`). Never replaced by generic `entities[]`.
- **Provenance** — `source_corpus` / `source_document_id` /
  `source_filename` / `source_revision` (§10): where the document originated.
  Source is an evaluation dimension, separate from taxonomy (§8).
  `annotation_provenance` (§43: source/method/model/prompt_version/
  confidence/reviewer/timestamp) distinguishes source_native, verified_join,
  human_annotated, human_adjudicated, LLM_assisted, LLM_zero_shot, heuristic,
  synthetic ground truth (§20) — P1.
- **Ground truth** — the 27-key GT schema on the `ground_truth` config:
  classification (`expected`, `expected_subclass`), per-class extraction GT,
  enrichment (content_topic, sentiment), and correspondence intent
  (`intent`, `intent_source`, `intent_confidence`, `intent_status` — §21;
  intent is its own dimension, never a subclass).
- **Evaluation** — cascaded, never collapsed (§22): classification_correct →
  routing_correct → extraction_correct → grouping_correct →
  final_pipeline_success. Reuse llm-dojo-scoring; never duplicate it (§24).

## 5. Dataset → Mailroom mapping (§81)

| Dataset concept | Mailroom concept |
|---|---|
| `document_id` | document identity |
| `matter_id` | matter/session grouping (`session_id`) |
| `document_type` (`expected`) | sorter output |
| `document_subtype` (`expected_subclass`) | sorter subtype |
| `expected_fields` | specialist ground truth |
| `source_corpus` | provenance |
| `simulation_run_id` | evaluation session |
| `expected_stage` | pipeline terminal expectation |
| `review_expected` | review routing |
| `retry_expected` | recovery behavior |
| `relationships` | document grouping/association |

## 6. Revision discipline (§44–§46)

- The corpus is consumed **pinned**: `FULL_CORPUS_REVISION` in
  `packages/llm-mailroom/src/pipeline/hf_corpora.py`. Never evaluate against
  unpinned `main`/`latest` — and never against a stale pin: re-check the pin
  after every corpus-side push (baseline Finding 1).
- Every evaluation trace records: dataset_name, dataset_revision,
  document_id, matter_id, simulation_run_id, taxonomy_version (§45).
  Implemented in llm-mailroom `run_pipeline(dataset=...)`: `dataset_name` /
  `dataset_revision` come from the pinned corpus constants;
  `taxonomy_version` currently equals the corpus schema label (`v7`, the
  five-class label surface of `docs/v7-taxonomy.md`) until the first
  explicit taxonomy decision gets its own `taxonomy_version` bump (§62 —
  taxonomy and dataset version independently); live non-corpus runs carry
  no dataset identity rather than a fabricated one.
- Every experiment is reproducible from the tuple: dataset revision +
  taxonomy revision + prompt version + model/provider + runtime
  configuration (§46).
- Publishing goes ONLY through the centralized helpers in
  `packages/mailroom-corpus-eda/src/mailroom_eda/` (`hf_interface`,
  `dataset_export`, `docclass_uploader`, `intent_backfill`) — cast-safe
  metadata, line-boundary-safe JSONL, sha256 verification, surgical card
  renders, blind-config label guard (§44A). No ad-hoc upload code.

## 7. Release gates (§91 + §4A)

A corpus release fails validation if: `document_id` is not unique; a taxonomy
value is invalid; a subtype does not belong to its document type (catch-all
`other` excepted); `expected_fields` violates the specialist schema; required
provenance is missing; the dataset revision is not pinned; annotation
provenance is missing; or source/document identity is ambiguous. **Plus
(§4A):** a release fails if any row lacks a resolvable license/provenance
chain, or if a non-synthetic, non-previously-cleared source is added without
an explicit PII review note in Evidence. Matter-aware and recovery releases
add their own gates (§91).

## 8. Releases (§84)

| Marker | Content |
|---|---|
| `v0.1-working` | frozen baseline (this contract's companion audit) |
| `v0.2-mailroom-hardened` | identity + provenance + content hashes ship on the published configs; taxonomy/evaluation contract |
| `v0.3-matter-aware` | grouping + relationships + multi-document cases |
| `v0.4-recovery-suite` | review + retry + arbiter scenarios |
| `v1.0-mailroom-evaluation` | stable regression/evaluation corpus |

Conceptual targets, not mandates to manufacture releases (§84).

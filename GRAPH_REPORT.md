# Graph Report - llm-mailroom  (2026-08-28)

## Corpus Check
- code-only production src/ — tests, notebooks, and .opencode/skills excluded

## Summary
- 1730 nodes · 4181 edges · 102 communities (84 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 122 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7dc57874`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Graph nodes & state
- logging
- LangChain specialists
- Sorter classification
- CUAD corpus loaders
- Vision rendering
- PDF & image transcription
- Managed prompts
- tasks
- LangChain BaseAgent
- Run limits & budgets
- Agent toolkit & memory
- LLM providers
- Arbiter & Boss
- audit
- Eval mocks & validation
- Watcher ingest
- LegalBench agent
- Tracing backends
- Eval mocks & validation (49)
- FastAPI intake
- Dashboard sync
- Eval mocks & validation (53)
- Quality judges
- Extraction schemas
- mock
- FastAPI intake (6)
- Sorter classification (62)
- Eval mocks & validation (70)
- Eval mocks & validation (71)
- Catalog & audit trail
- Hub subclass inventories
- classifier
- Routing & reconsideration
- Quality scores
- Tracing backends (19)
- Langfuse log sync
- Graph nodes & state (25)
- Graph nodes & state (26)
- Routing & reconsideration (27)
- Grounded pilot
- Post-hoc schema GT
- HF corpora
- Langfuse evaluator sync
- Experiment log
- HF pilot & honesty gaps
- LLM retry
- Agent eval
- Local eval packs
- prepare samples
- Pipeline guards
- Langfuse tracing
- Catalog & audit trail (44)
- Graph nodes & state (45)
- Specialist scoring suites
- Field scoring calibration
- LegalBench scoring
- Tracing backends (52)
- Docclass prompt arm
- bootstrap
- External samples
- Classification scoring
- Prompt cutover
- env utils
- prompts docclass
- HF pilot & honesty gaps (65)
- Langfuse model sync
- Grounded pilot (67)
- LegalBench data
- prompts
- Inbox bins
- Mailroom BaseAgent
- Graph nodes & state (73)
- Mailroom BaseAgent (74)
- FastAPI intake (75)
- Graph nodes & state (76)
- Graph nodes & state (77)
- LangChain BaseAgent (78)
- Tracing backends (80)
- HF pilot & honesty gaps (9)
- Catalog & audit trail (100)
-   init   (79)
- pyproject
- LangChain BaseAgent (86)
- Managed prompts (88)
- Agent eval (89)
- Tracing backends (90)
- Quality scores (91)
- Tracing backends (93)
- Grounded pilot (99)

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 41 edges
2. `BaseAgent` - 37 edges
3. `BaseAgent` - 35 edges
4. `build_graph()` - 33 edges
5. `get_langfuse_client()` - 31 edges
6. `get_managed_prompt()` - 30 edges
7. `ensure_schema()` - 30 edges
8. `_execute_run()` - 28 edges
9. `async_session()` - 26 edges
10. `load_env()` - 25 edges
11. `setup_logging()` - 24 edges
12. `inbox_dir()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `DocumentState` --uses--> `archive_node()`  [INFERRED]
  src/graph/state.py → src/graph/build_graph.py
- `DocumentState` --uses--> `human_review_node()`  [INFERRED]
  src/graph/state.py → src/graph/build_graph.py
- `DocumentState` --uses--> `ingest_node()`  [INFERRED]
  src/graph/state.py → src/graph/build_graph.py
- `DocumentState` --uses--> `resume_from_review()`  [INFERRED]
  src/graph/state.py → src/graph/build_graph.py
- `DocumentState` --uses--> `run_pipeline()`  [INFERRED]
  src/graph/state.py → src/graph/build_graph.py

## Import Cycles
- None detected.

## Communities (102 total, 18 thin omitted)

### Community 1 - "Graph nodes & state"
Cohesion: 0.09
Nodes (53): DocumentState, arbiter_node(), boss_escalation_node(), _build_checkpointer(), build_graph(), _build_handoff_context(), _build_specialist_dispatch(), catalog_write_node() (+45 more)

### Community 10 - "logging"
Cohesion: 0.09
Nodes (33): _RotatingFileSink, _langchain_prompt(), prompt_templates(), default_environment(), load_env(), setup_logging(), _aggregate(), _cell() (+25 more)

### Community 11 - "LangChain specialists"
Cohesion: 0.08
Nodes (22): ComplianceFilingSpecialist, ContractsSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, _SpecialistBase, get_prompt(), get_specialist(), _merge_reasoning() (+14 more)

### Community 13 - "Sorter classification"
Cohesion: 0.09
Nodes (25): SorterAgent, build_structured_schema(), format_sorter_subclass_catalogs(), sorter_subclass_catalog(), valid_sorter_subclasses(), _classification_user_message(), _doc_classes_for_prompt(), finalize_sorter_result() (+17 more)

### Community 14 - "CUAD corpus loaders"
Cohesion: 0.11
Nodes (31): CorpusUnavailable, Sample, load_cuad_qa(), load_family_rows(), _contracts_from_annotations(), _contracts_from_txt(), _download(), download_all() (+23 more)

### Community 15 - "Vision rendering"
Cohesion: 0.10
Nodes (26): ContractsSpecialist, agent_uses_vision(), _any_specialist_uses_vision(), is_vision_capable(), max_pages(), pipeline_uses_vision(), render_document_pages(), render_image() (+18 more)

### Community 17 - "PDF & image transcription"
Cohesion: 0.11
Nodes (16): PDFTranscriber, transcribe_pdf(), compile_matter_record(), load_skills(), langfuse_call_attrs(), get_run_deadline(), record_usage(), BaseAgent (+8 more)

### Community 2 - "Managed prompts"
Cohesion: 0.08
Nodes (30): BaseAgent, BossAgent, ComplianceSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, InsuranceClaimsSpecialist, build_structured_schema(), _block() (+22 more)

### Community 20 - "tasks"
Cohesion: 0.13
Nodes (21): RunResult, LegalBenchTask, build_parser(), main(), log_run(), _model_name(), print_summary(), run_task() (+13 more)

### Community 21 - "LangChain BaseAgent"
Cohesion: 0.13
Nodes (14): BaseAgent, ChatOpenAI, Return the agent's system prompt string., System prompt + agent's skill files + tool descriptions + recent outcome…, Lazily build the LangChain ``ChatOpenAI`` client. Uses the OpenRouter base URL…, Call ``fn()`` retrying transient failures with backoff + jitter. Mirrors…, True when this agent's model accepts image input. Vision capability is config-…, Build the human-message content for a document input. Vision-capable models get… (+6 more)

### Community 22 - "Run limits & budgets"
Cohesion: 0.10
Nodes (24): RunBudgetExceeded, RunDeadlineExceeded, _bounded(), compute_run_metrics(), check_token_budget(), estimate_cost(), get_deadline_seconds(), get_max_total_output_tokens() (+16 more)

### Community 23 - "Agent toolkit & memory"
Cohesion: 0.13
Nodes (22): AgentTool, _memory_dir(), _memory_path(), recent_context(), record_outcome(), stats(), _build_toolkit(), get_tools() (+14 more)

### Community 29 - "LLM providers"
Cohesion: 0.16
Nodes (19): ProviderConfig, _check_llm_provider(), get_llm(), get_llm_client(), get_llm_model(), instrument_client(), _build_providers(), get_provider() (+11 more)

### Community 34 - "Arbiter & Boss"
Cohesion: 0.10
Nodes (14): ArbiterAgent, ImageExtractor, SorterReviewerAgent, invoke_agent(), _invoke_reviewer(), _invoke_specialist(), BaseAgent, BaseAgent (+6 more)

### Community 35 - "audit"
Cohesion: 0.19
Nodes (17): AuditLogEntry, archive_document(), _file_sha256(), build_audit_entry(), compute_audit_hash(), compute_audit_hash_v1(), verify_chain(), _all_chains() (+9 more)

### Community 39 - "Eval mocks & validation"
Cohesion: 0.14
Nodes (9): FakeLangChainLLM, _FakeStructuredRunner, _install_mocks(), main(), _make_mock_langchain_llm(), Runnable returned by ``with_structured_output``: invoke() yields the…, Replacement for the ChatOpenAI instance the vendored agents construct. -…, Deterministic fakes so ``--mock`` never hits the network. (+1 more)

### Community 4 - "Watcher ingest"
Cohesion: 0.07
Nodes (33): InboxHandler, Watcher, _WatcherLock, WatcherLockHeld, lifespan(), run_pipeline(), claim_file(), is_ingestion_paused() (+25 more)

### Community 42 - "LegalBench agent"
Cohesion: 0.14
Nodes (9): LegalBenchAgent, Any, BaseAgent, Model agent for LegalBench runs. Reuses the vendored ``BaseAgent`` machinery —…, One agent instance per task run; answers via structured JSON., LegalBench tasks use the task prompt as-is (no sorter skills)., Yes/no answer with evidence + confidence., One-of-N family classification with confidence. (+1 more)

### Community 49 - "Eval mocks & validation (49)"
Cohesion: 0.22
Nodes (7): _EvalLangChainLLM, is_classify_call(), user_text_from_messages(), MAILROOM-LOCAL (not from upstream): deterministic fake LangChain LLM. The…, Extract the human text from a LangChain message list, handling multimodal list…, Evidence-based fake: classifies/extracts by deterministic keyword evidence from…, Set classification/extraction canned dicts from the DOCUMENT text (self.calls…

### Community 5 - "FastAPI intake"
Cohesion: 0.07
Nodes (41): OpsMonitor, analyze_audit_database(), _check_database(), _embed_watcher_running(), get_audit_trail(), get_document_status(), get_matter(), health() (+33 more)

### Community 51 - "Dashboard sync"
Cohesion: 0.29
Nodes (13): WidgetSpec, _client(), _existing_placements(), json_dumps(), main(), _placement_kwargs(), _score_widget(), _spec_to_request() (+5 more)

### Community 53 - "Eval mocks & validation (53)"
Cohesion: 0.24
Nodes (12): _MockClient, ensure_dirs(), _collect_documents(), _expectation_for(), _load_manifest_expectations(), main(), _mock_get_llm(), Path (+4 more)

### Community 54 - "Quality judges"
Cohesion: 0.23
Nodes (5): CompletenessJudge, BaseAgent, Render the task specification (taxonomy doc classes) for the judge., Judge whether the sorter's assigned class matches the taxonomy task…, Judge whether the extracted field values are factually accurate (no…

### Community 56 - "Extraction schemas"
Cohesion: 0.35
Nodes (9): ComplianceFilingExtraction, ContractExtraction, CorporateRecordExtraction, CorrespondenceExtraction, InsuranceClaimExtraction, Matter, get_extraction_schema(), BaseModel (+1 more)

### Community 57 - "mock"
Cohesion: 0.27
Nodes (5): MockLegalBenchModel, _hash(), Any, Deterministic mock model for LegalBench runs (no network, no OpenAI). Answers…, Implements the LegalBenchAgent interface deterministically.

### Community 6 - "FastAPI intake (6)"
Cohesion: 0.06
Nodes (45): DocumentManifest, PipelineStage, _document_payload_from_manifest(), lookup_document_endpoint(), _move_rejected_to_failed(), _parse_resolve_payload(), _rate_limit_upload(), _require_token() (+37 more)

### Community 62 - "Sorter classification (62)"
Cohesion: 0.25
Nodes (6): SorterAgent, _invoke_sorter(), _LangChainSorterAgent, Mailroom-configured sorter. - Model/budget defaults come from ``taxonomy.yaml``…, Classify a document, optionally with page images attached. Returns ``(doc_type,…, Structured classify used by the graph (includes ``doc_subclass``).

### Community 70 - "Eval mocks & validation (70)"
Cohesion: 0.40
Nodes (3): _Choices, _HintedEvalLangChainLLM, Evidence classifier with a filename-hint override. The repository's real sample…

### Community 71 - "Eval mocks & validation (71)"
Cohesion: 0.40
Nodes (4): chat, completions, _fake_client(), _fake_judge_client()

### Community 8 - "Catalog & audit trail"
Cohesion: 0.11
Nodes (40): AuditLogRecord, DocumentRecord, MatterRecord, Base, _write_review_audit_entry(), _touch_heartbeat(), main(), _print_human() (+32 more)

### Community 0 - "Hub subclass inventories"
Cohesion: 0.05
Nodes (79): _resolved_models(), as_clause_lines(), clause_handoff(), enrich_contract_extraction(), flatten_cuad_clause_labels(), flatten_maud_clause_labels(), infer_merger_consideration(), normalize_consideration() (+71 more)

### Community 12 - "classifier"
Cohesion: 0.08
Nodes (29): classify_image(), clean_prediction(), extract_confidence(), extract_reasoning(), extract_runner_up(), _valid_classes(), build_text_messages(), build_vision_messages() (+21 more)

### Community 16 - "Routing & reconsideration"
Cohesion: 0.11
Nodes (31): after_arbiter(), after_boss(), after_classify(), after_extraction(), after_extraction_gated(), after_human_review(), after_judge(), after_retry_classify() (+23 more)

### Community 18 - "Quality scores"
Cohesion: 0.12
Nodes (28): ensure_field_score_configs(), score_and_log_extraction(), _client(), create_trace_score(), deterministic_verdict_label(), emit_in_pipeline_judge_scores(), emit_pipeline_scores(), ensure_score_configs() (+20 more)

### Community 19 - "Tracing backends (19)"
Cohesion: 0.12
Nodes (28): client_kwargs(), flush_langfuse(), get_langfuse_client(), get_trace_id(), install_on_dropped(), instrument_openai_client(), observation(), _optional_float() (+20 more)

### Community 24 - "Langfuse log sync"
Cohesion: 0.15
Nodes (20): main(), _slug(), _client(), main(), _parse_since(), sync_logs(), _trace_basics(), _trace_stage() (+12 more)

### Community 25 - "Graph nodes & state (25)"
Cohesion: 0.13
Nodes (22): apply_intake(), _extract_text_from_docx(), _extract_text_from_image(), _extract_text_from_pdf(), _file_sha256(), _file_size(), ingest_node(), _read_file_text() (+14 more)

### Community 26 - "Graph nodes & state (26)"
Cohesion: 0.11
Nodes (23): archive_node(), _catalog_upsert(), _emit_stage_audit(), _existing_processing_doc_id(), _finalize_aborted(), human_review_node(), _latest_audit_hash(), _normalize_review_decision() (+15 more)

### Community 27 - "Routing & reconsideration (27)"
Cohesion: 0.16
Nodes (22): after_report(), align_class(), _as_float(), class_misses_ground_truth(), collect_review_causes(), expected_class(), expected_field_coverage(), format_causes() (+14 more)

### Community 28 - "Grounded pilot"
Cohesion: 0.15
Nodes (22): flush_braintrust(), flush(), _attach_field_scoring(), diff_report(), filter_real_samples(), _ground_truth_scores(), _ingest_scores(), main() (+14 more)

### Community 3 - "Post-hoc schema GT"
Cohesion: 0.07
Nodes (49): configure(), instrument_openai_client(), is_configured(), _apply_taxonomy_settings(), field_is_ambiguous(), get_type_bands(), warm_embedding_model(), _date_pair_days() (+41 more)

### Community 30 - "HF corpora"
Cohesion: 0.16
Nodes (21): active_corpus(), adapt_hub_row(), example_for_class(), example_rows(), examples_by_class(), hub_sample(), load_example_pack(), pipeline_corpora() (+13 more)

### Community 31 - "Langfuse evaluator sync"
Cohesion: 0.16
Nodes (21): _build_evaluator_request(), _build_output_definition(), _build_rule_request(), _client(), _current_evaluator_prompt(), _ensure_llm_connection(), _existing_rule_ids(), main() (+13 more)

### Community 32 - "Experiment log"
Cohesion: 0.19
Nodes (20): append_record(), build_record(), default_log_path(), default_sibling_root(), git_snapshot(), _inside(), regenerate(), _run_python() (+12 more)

### Community 33 - "HF pilot & honesty gaps"
Cohesion: 0.16
Nodes (20): _denial_reasons(), determination_consistency_is_quality(), honesty_trace_metadata(), insurance_determination_consistent(), insurance_determination_issues(), insurance_expected_set_is_homogeneous(), insurance_gt_is_homogeneous(), _norm_determination() (+12 more)

### Community 36 - "LLM retry"
Cohesion: 0.19
Nodes (18): _is_retryable_error(), _is_json_mode_400(), _is_retryable(), _retry_after_seconds(), retry_chat_completion(), _retry_config(), retry_sleep_seconds(), _status_code() (+10 more)

### Community 37 - "Agent eval"
Cohesion: 0.22
Nodes (18): cases_for_agent(), evaluate_agent(), load_fixture_cases(), load_local_pack_cases(), load_manifest_cases(), _mean(), _read_text(), score_case() (+10 more)

### Community 38 - "Local eval packs"
Cohesion: 0.24
Nodes (18): get_field_types(), all_local_pack_samples(), compliance_local_samples(), corporate_extraction_samples(), _hydrate(), insurance_contrast_samples(), local_pack_status(), _mean() (+10 more)

### Community 40 - "prepare samples"
Cohesion: 0.20
Nodes (16): ensure_process_tracing(), _escape(), generate_pdf_from_text(), is_real_sample(), _load_manifest(), prepare_samples(), _dim_summary(), judge_one() (+8 more)

### Community 41 - "Pipeline guards"
Cohesion: 0.18
Nodes (16): validate_extraction(), apply_classification_guard(), apply_extraction_guard(), guard_classification(), guard_extraction(), _has_substantive_content(), _is_valid_confidence(), _valid_subtypes() (+8 more)

### Community 43 - "Langfuse tracing"
Cohesion: 0.16
Nodes (14): attach_run_scores(), ensure_score_configs_if_enabled(), _environment(), legalbench_trace(), question_observation(), is_enabled(), pipeline_trace(), Any (+6 more)

### Community 44 - "Catalog & audit trail (44)"
Cohesion: 0.21
Nodes (14): _apply_sqlite_pragmas(), close_db(), _engine_kwargs(), _ensure_models_imported(), get_engine(), get_session(), _get_sessionmaker(), init_db() (+6 more)

### Community 45 - "Graph nodes & state (45)"
Cohesion: 0.17
Nodes (15): _chunk_config(), _extract_compliance(), _extract_contracts(), _extract_corporate_records(), _extract_correspondence(), _extract_insurance_claims(), _instantiate_specialist(), _run_chunked_extraction() (+7 more)

### Community 47 - "Specialist scoring suites"
Cohesion: 0.22
Nodes (14): attach_single_doc_extras(), _numeric_extra(), score_and_log_intake(), score_intake_suite(), score_with_suite(), unwrap_suite_result(), Any, ExtractionScoreResult (+6 more)

### Community 48 - "Field scoring calibration"
Cohesion: 0.20
Nodes (14): main(), _perturb_date(), _perturb_entity_list(), _perturb_free_text(), _perturb_money(), _perturb_name(), _predictions_for(), Random (+6 more)

### Community 50 - "LegalBench scoring"
Cohesion: 0.25
Nodes (13): equivalent_subtypes(), _binary_f1(), _ece(), _mean(), _safe_div(), score_binary(), score_multiclass(), Any (+5 more)

### Community 52 - "Tracing backends (52)"
Cohesion: 0.21
Nodes (12): flush_phoenix(), _init_opentelemetry(), _instrument_openai(), instrument_openai_client(), is_configured(), phoenix_enabled(), Arize Phoenix tracing backend — local, cost-free default for llm-mailroom.…, Return ``client`` with Phoenix auto-tracing activated (no-op if disabled).… (+4 more)

### Community 55 - "Docclass prompt arm"
Cohesion: 0.20
Nodes (10): list_prompts(), PROMPT_TEMPLATES(), docclass_prompts_enabled(), langchain_prompt_version(), managed_prompt_lookup(), List all available prompt versions., Return all prompt templates as a dict. Single source of truth for…, Opt-in KANBAN-090 docclass prompt arm at runtime. Production agent prompts stay… (+2 more)

### Community 58 - "bootstrap"
Cohesion: 0.29
Nodes (10): bootstrap_ci(), _clean(), delta_significance(), _resample_means(), Any, Random, Bootstrap confidence intervals and small-sample delta testing. Ported verbatim…, Coerce a per-document score list to floats, dropping None/non-numeric. (+2 more)

### Community 59 - "External samples"
Cohesion: 0.33
Nodes (10): _caption_from_text(), _download(), fetch_atticus(), fetch_legalbench(), fetch_pileoflaw(), main(), _stream_pol_records(), Path (+2 more)

### Community 60 - "Classification scoring"
Cohesion: 0.31
Nodes (9): classes_match(), normalize_class(), score_exact_classification(), check_contract(), pipeline_class(), Any, Classification KPIs after ``merger_agreement`` became a live MAUD class. Dojo…, True when predicted equals expected. MAUD is not CUAD. (+1 more)

### Community 61 - "Prompt cutover"
Cohesion: 0.40
Nodes (9): cutover_agent(), cutover_all(), list_agents(), list_local_models(), load_config(), main(), recommend_cutover_order(), save_config() (+1 more)

### Community 63 - "env utils"
Cohesion: 0.28
Nodes (8): bool_env(), get_env(), load_env(), require_env(), Load ``braintrust.env`` then ``.env`` into the environment (idempotent).…, Validate that all given environment variables are set and non-empty. Returns…, Get an environment variable with a default fallback., Get a boolean environment variable.

### Community 64 - "prompts docclass"
Cohesion: 0.28
Nodes (7): _append(), _build_versions(), _rules(), Docclass prompt variants for every mailroom classification-chain role.…, Pure-appended docclass variant: base is a STRICT PREFIX of the result., Derive every variant from the live production template of that role., # NOTE: fragment assertions in tests target SHORT substrings that do not cross

### Community 65 - "HF pilot & honesty gaps (65)"
Cohesion: 0.31
Nodes (9): load_ground_truth_labels(), load_hf_rows(), _paginate_viewer(), _scan_cap(), _take_rows(), _viewer_rows(), ``max_scan <= 0`` means unlimited (do not use on the 247k Enron set)., Map filename → {expected, expected_subclass} from config=ground_truth. These… (+1 more)

### Community 66 - "Langfuse model sync"
Cohesion: 0.39
Nodes (8): _client(), _cost_models(), _existing_by_name(), main(), _match_pattern(), _prices_match(), sync_models(), Map model_name -> registry Model for every user-defined entry. Paginates: the…

### Community 67 - "Grounded pilot (67)"
Cohesion: 0.29
Nodes (7): _check_cost_watchdog(), _fetch_openrouter_prices(), _price_for(), _record_langchain_response(), Warn at $0.15, abort the run at $0.20 (cumulative across all samples)., Mirror _wrap_client's usage/cost accounting for a LangChain response., Fetch live OpenRouter pricing (per-token), normalized to $/M tokens. The…

### Community 68 - "LegalBench data"
Cohesion: 0.33
Nodes (6): _fingerprint(), _normalize_prediction(), _extract_binary(), Any, yes'/'no' normalization for binary answers (lenient)., Deterministic corpus fingerprint for the sampled rows.

### Community 69 - "prompts"
Cohesion: 0.40
Nodes (5): family_classification_prompt_v1(), get_prompt(), Versioned LegalBench task prompts. Prompt version = experiment identity in the…, Fill the 25-family list into the multiclass prompt (called per run so the…, Resolve a prompt version to its system-prompt text.

### Community 7 - "Inbox bins"
Cohesion: 0.11
Nodes (44): get_queue(), _ensure_dirs(), accepted_extensions(), archive_dir(), classified_dir(), failed_dir(), get_base_dir(), _get_config() (+36 more)

### Community 73 - "Graph nodes & state (73)"
Cohesion: 0.50
Nodes (4): _prompt_versions(), _bound_prompt_versions(), Prompt versions bound during the run (best-effort; Langfuse-managed prompts…, Version keys currently wired into production / agent defaults. Used for catalog…

### Community 9 - "HF pilot & honesty gaps (9)"
Cohesion: 0.10
Nodes (42): _catalog_by_trace(), completed_filenames(), enrich_sample_row(), expected_fields_for_sample(), expected_fields_meta(), finalize_report(), find_sample_text(), hf_corpus_honesty() (+34 more)

## Knowledge Gaps
- **1 isolated node(s):** `mailroom`
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `LangChain BaseAgent` to `LLM retry`, `Watcher ingest`, `Eval mocks & validation`, `HF pilot & honesty gaps (9)`, `LegalBench agent`, `LangChain specialists`, `Sorter classification`, `LangChain BaseAgent (78)`, `Eval mocks & validation (53)`, `LangChain BaseAgent (85)`, `Agent toolkit & memory`, `LangChain BaseAgent (86)`, `Grounded pilot`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `load_env()` connect `logging` to `Langfuse model sync`, `audit`, `Watcher ingest`, `FastAPI intake`, `Inbox bins`, `Catalog & audit trail`, `HF pilot & honesty gaps (9)`, `Eval mocks & validation`, `prepare samples`, `CUAD corpus loaders`, `Field scoring calibration`, `Dashboard sync`, `Eval mocks & validation (53)`, `Langfuse log sync`, `Grounded pilot`, `LLM providers`, `Langfuse evaluator sync`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `load_config()` connect `Vision rendering` to `Hub subclass inventories`, `Graph nodes & state`, `Managed prompts`, `Post-hoc schema GT`, `FastAPI intake`, `FastAPI intake (6)`, `Inbox bins`, `classifier`, `Sorter classification`, `Routing & reconsideration`, `PDF & image transcription`, `Quality scores`, `Run limits & budgets`, `Agent toolkit & memory`, `Langfuse evaluator sync`, `LLM retry`, `Local eval packs`, `Graph nodes & state (45)`, `Quality judges`, `Langfuse model sync`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `BaseAgent` (e.g. with `SorterAgent` and `get_specialist()`) actually correct?**
  _`BaseAgent` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `BaseAgent` (e.g. with `ArbiterAgent` and `BossAgent`) actually correct?**
  _`BaseAgent` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `build_graph()` (e.g. with `ingest_node()` and `classify_node()`) actually correct?**
  _`build_graph()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `mailroom` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
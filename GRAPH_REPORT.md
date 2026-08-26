# Graph Report - llm-mailroom  (2026-08-26)

## Corpus Check
- code-only production src/ — tests, notebooks, and .opencode/skills excluded

## Summary
- 1422 nodes · 3346 edges · 92 communities (80 shown, 12 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `30ff6874`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Catalog & audit trail
- PDF & image transcription
- Run limits & budgets
- LangChain BaseAgent
- Watcher ingest
- base
- LegalBench runner
- ops monitor
- providers
- Graph nodes & state
- agent
- LangChain specialists
- Sorter classification
- langfuse setup
- judge
- sync dashboards
- Extraction schemas
- logging
- mock
- Eval mocks & validation
- Contracts specialist
- audit
- data
- Managed prompts & judges
- sorter reviewer
- Agent toolkit & memory
- Hugging Face pilot
- build graph
- FastAPI intake
- Quality scores
- Confidence routing
- Pipeline execution
- Vision rendering
- Inbox bins
- Vision classifier
- Langfuse evaluator sync
- Experiment log
- retry
- run pilot
- prompts docclass
- Langfuse tracing
- Taxonomy extract aliases
- sync models
- guards
- sync langfuse logs
- Hub subclass inventories
- langfuse tracing
- cuad maud
- Intake clerk
- bootstrap
- fetch external samples
- cutover
- env utils
- db
- write pilot report
- sync dataset
- Docclass prompt arm
- scoring
- run pilot (59)
- phoenix setup
- braintrust setup
- prompts
- Chunked extraction
- run vision sweep
- build graph (65)
- main
- API bearer auth
- Review-resume entry
- base agent
- Field scoring & metrics
- CUAD corpus loaders
-   init  
- pyproject
- base agent (78)
- prompts (80)
- langfuse setup (81)
- tracing (82)
- run pilot (90)
- run quality judges

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 37 edges
2. `BaseAgent` - 35 edges
3. `BaseAgent` - 32 edges
4. `build_graph()` - 32 edges
5. `get_langfuse_client()` - 31 edges
6. `get_managed_prompt()` - 28 edges
7. `ensure_schema()` - 25 edges
8. `_execute_run()` - 24 edges
9. `DocumentState` - 23 edges
10. `async_session()` - 23 edges
11. `main()` - 23 edges
12. `inbox_dir()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `ImageExtractor` --uses--> `BaseAgent`  [INFERRED]
  src/agents/image_extractor.py → src/agents/base.py
- `PDFTranscriber` --uses--> `BaseAgent`  [INFERRED]
  src/agents/pdf_transcriber.py → src/agents/base.py
- `BaseAgent` --uses--> `SorterAgent`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/sorter_agent.py
- `BaseAgent` --uses--> `_SpecialistBase`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/specialist_agents.py
- `BaseAgent` --uses--> `get_specialist()`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/specialist_agents.py

## Import Cycles
- None detected.

## Communities (92 total, 12 thin omitted)

### Community 0 - "Catalog & audit trail"
Cohesion: 0.16
Nodes (30): AuditLogRecord, DocumentRecord, MatterRecord, Base, ops_status(), _persist_scores(), _all_chains(), main() (+22 more)

### Community 11 - "PDF & image transcription"
Cohesion: 0.13
Nodes (19): ImageExtractor, PDFTranscriber, extract_text_from_image(), transcribe_pdf(), compile_matter_record(), retry_chat_completion(), langfuse_call_attrs(), get_run_deadline() (+11 more)

### Community 16 - "Run limits & budgets"
Cohesion: 0.09
Nodes (28): RunBudgetExceeded, RunDeadlineExceeded, _bounded(), compute_run_metrics(), load_config(), check_run_deadline(), check_token_budget(), estimate_cost() (+20 more)

### Community 18 - "LangChain BaseAgent"
Cohesion: 0.11
Nodes (16): BaseAgent, load_skills(), ChatOpenAI, ABC, Lazily build the LangChain ``ChatOpenAI`` client. Uses the OpenRouter base URL…, Call ``fn()`` retrying transient failures with backoff + jitter. Mirrors…, True when this agent's model accepts image input. Vision capability is config-…, Build the human-message content for a document input. Vision-capable models get… (+8 more)

### Community 20 - "Watcher ingest"
Cohesion: 0.14
Nodes (17): InboxHandler, Watcher, inbox_dir(), is_ingestion_paused(), list_inbox_files(), read_inbox_meta(), touch_watcher_heartbeat(), _is_already_processed() (+9 more)

### Community 23 - "base"
Cohesion: 0.23
Nodes (5): BaseAgent, ABC, Build the user-message content for a document input. Vision-capable models get…, Truncate document text to the agent's configured input budget, marking the…, True when this agent's model accepts image input and (optionally) page images…

### Community 25 - "LegalBench runner"
Cohesion: 0.12
Nodes (23): RunResult, LegalBenchTask, build_parser(), main(), log_run(), _model_name(), print_summary(), run_task() (+15 more)

### Community 26 - "ops monitor"
Cohesion: 0.19
Nodes (6): OpsMonitor, _main(), run_ops_monitor(), Event, Pause metadata (actor/reason/expiry) via the TTL-aware helper., Like start(), but exits when ``stop_event`` is set (L-6: signal driven graceful…

### Community 27 - "providers"
Cohesion: 0.20
Nodes (16): ProviderConfig, _check_llm_provider(), compile_report_node(), get_llm(), get_llm_client(), get_llm_model(), instrument_client(), _build_providers() (+8 more)

### Community 28 - "Graph nodes & state"
Cohesion: 0.11
Nodes (29): DocumentState, arbiter_node(), boss_escalation_node(), _build_handoff_context(), _build_specialist_dispatch(), catalog_write_node(), _clean_fields_for_judge(), _detect_conflict() (+21 more)

### Community 29 - "agent"
Cohesion: 0.14
Nodes (11): LegalBenchAgent, build_structured_schema(), Any, BaseAgent, Build a JSON schema dict for structured output. ``title`` is required by…, Model agent for LegalBench runs. Reuses the vendored ``BaseAgent`` machinery —…, One agent instance per task run; answers via structured JSON., LegalBench tasks use the task prompt as-is (no sorter skills). (+3 more)

### Community 34 - "LangChain specialists"
Cohesion: 0.08
Nodes (23): ComplianceFilingSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, _SpecialistBase, get_prompt(), get_extraction_schema(), get_specialist(), _merge_reasoning() (+15 more)

### Community 35 - "Sorter classification"
Cohesion: 0.10
Nodes (17): SorterAgent, SorterAgent, _doc_classes_for_prompt(), _sorter_schema(), get_doc_class_catalog(), _LangChainSorterAgent, BaseAgent, Sorter agent — LangChain version vendored from llm-entity-extraction. Re-… (+9 more)

### Community 39 - "judge"
Cohesion: 0.19
Nodes (7): CompletenessJudge, judge_one(), _raw_text_for(), BaseAgent, Render the task specification (taxonomy doc classes) for the judge., Judge whether the sorter's assigned class matches the taxonomy task…, Judge whether the extracted field values are factually accurate (no…

### Community 41 - "sync dashboards"
Cohesion: 0.29
Nodes (13): WidgetSpec, _client(), _existing_placements(), json_dumps(), main(), _placement_kwargs(), _score_widget(), _spec_to_request() (+5 more)

### Community 42 - "Extraction schemas"
Cohesion: 0.16
Nodes (17): ComplianceFilingExtraction, ContractExtraction, CorporateRecordExtraction, CorrespondenceExtraction, InsuranceClaimExtraction, DocumentManifest, PipelineStage, Matter (+9 more)

### Community 43 - "logging"
Cohesion: 0.21
Nodes (11): _RotatingFileSink, setup_logging(), _aggregate(), _cell(), main(), _print_table(), _scores_of(), list_documents() (+3 more)

### Community 46 - "mock"
Cohesion: 0.27
Nodes (5): MockLegalBenchModel, _hash(), Any, Deterministic mock model for LegalBench runs (no network, no OpenAI). Answers…, Implements the LegalBenchAgent interface deterministically.

### Community 5 - "Eval mocks & validation"
Cohesion: 0.05
Nodes (38): FakeLangChainLLM, _FakeStructuredRunner, chat, _Choices, completions, _EvalLangChainLLM, _HintedEvalLangChainLLM, _MockClient (+30 more)

### Community 50 - "Contracts specialist"
Cohesion: 0.25
Nodes (5): ContractsSpecialist, ContractsSpecialist, _LangChainContractsSpecialist, Contracts specialist — LangChain version vendored from llm-entity-extraction.…, Mailroom-configured contracts specialist. - Model/budget defaults come from…

### Community 52 - "audit"
Cohesion: 0.19
Nodes (17): AuditLogEntry, archive_document(), _file_sha256(), get_audit_trail(), move_to_archive(), build_audit_entry(), compute_audit_hash(), compute_audit_hash_v1() (+9 more)

### Community 55 - "data"
Cohesion: 0.16
Nodes (16): CorpusUnavailable, Sample, _fingerprint(), load_cuad_qa(), load_family_rows(), _normalize_prediction(), _extract_binary(), Any (+8 more)

### Community 6 - "Managed prompts & judges"
Cohesion: 0.06
Nodes (36): ArbiterAgent, BossAgent, ComplianceSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, InsuranceClaimsSpecialist, build_structured_schema(), _extract_compliance() (+28 more)

### Community 66 - "sorter reviewer"
Cohesion: 0.33
Nodes (4): SorterReviewerAgent, BaseAgent, Independent second-opinion classifier (blind re-classification)., Independently classify the document. Returns ``{doc_type, contract_subtype,…

### Community 7 - "Agent toolkit & memory"
Cohesion: 0.10
Nodes (24): AgentTool, _memory_dir(), _memory_path(), recent_context(), record_outcome(), stats(), _build_toolkit(), get_tools() (+16 more)

### Community 1 - "Hugging Face pilot"
Cohesion: 0.10
Nodes (44): _catalog_by_trace(), completed_filenames(), enrich_sample_row(), finalize_report(), find_sample_text(), hf_samples_from_report(), _inbox_filename(), latest_hf_reports() (+36 more)

### Community 10 - "build graph"
Cohesion: 0.19
Nodes (13): _write_review_audit_entry(), archive_node(), classify_node(), _emit_stage_audit(), _latest_audit_hash(), _run_coro(), _touch_heartbeat(), _write_audit_log() (+5 more)

### Community 12 - "FastAPI intake"
Cohesion: 0.10
Nodes (31): _check_database(), get_document_status(), get_matter(), get_queue(), health(), lifespan(), _move_rejected_to_failed(), ops_resume() (+23 more)

### Community 13 - "Quality scores"
Cohesion: 0.11
Nodes (30): ensure_field_score_configs(), score_and_log_extraction(), _client(), create_trace_score(), emit_pipeline_scores(), ensure_score_configs(), is_enabled(), langfuse_score_name() (+22 more)

### Community 14 - "Confidence routing"
Cohesion: 0.15
Nodes (28): build_graph(), retry_classify_node(), after_arbiter(), after_boss(), after_classify(), after_extraction(), after_extraction_gated(), after_human_review() (+20 more)

### Community 15 - "Pipeline execution"
Cohesion: 0.11
Nodes (35): _emit_pipeline_result(), _execute_run(), _existing_processing_doc_id(), _extract_text_from_docx(), _extract_text_from_image(), _extract_text_from_pdf(), _file_sha256(), _file_size() (+27 more)

### Community 17 - "Vision rendering"
Cohesion: 0.15
Nodes (22): _resolved_models(), agent_uses_vision(), _any_specialist_uses_vision(), is_vision_capable(), max_pages(), pipeline_uses_vision(), render_document_pages(), render_image() (+14 more)

### Community 19 - "Inbox bins"
Cohesion: 0.12
Nodes (40): _build_checkpointer(), _ensure_dirs(), archive_dir(), claim_file(), classified_dir(), clear_ingestion_paused(), ensure_dirs(), failed_dir() (+32 more)

### Community 2 - "Vision classifier"
Cohesion: 0.11
Nodes (21): classify_image(), clean_prediction(), extract_confidence(), extract_reasoning(), extract_runner_up(), _valid_classes(), build_text_messages(), build_vision_messages() (+13 more)

### Community 21 - "Langfuse evaluator sync"
Cohesion: 0.16
Nodes (21): _build_evaluator_request(), _build_output_definition(), _build_rule_request(), _client(), _current_evaluator_prompt(), _ensure_llm_connection(), _existing_rule_ids(), main() (+13 more)

### Community 22 - "Experiment log"
Cohesion: 0.19
Nodes (20): append_record(), build_record(), default_log_path(), default_sibling_root(), git_snapshot(), _inside(), regenerate(), _run_python() (+12 more)

### Community 24 - "retry"
Cohesion: 0.23
Nodes (14): _is_retryable_error(), _is_json_mode_400(), _is_retryable(), is_transient_error(), _retry_after_seconds(), _retry_config(), retry_sleep_seconds(), _status_code() (+6 more)

### Community 3 - "run pilot"
Cohesion: 0.18
Nodes (19): _attach_field_scoring(), diff_report(), filter_real_samples(), _ground_truth_scores(), _ingest_scores(), main(), misfile_candidates(), _parse_expected_fields() (+11 more)

### Community 30 - "prompts docclass"
Cohesion: 0.18
Nodes (13): _append(), _build_versions(), _rules(), prompt_templates(), _client(), _current_production(), main(), sync_one() (+5 more)

### Community 31 - "Langfuse tracing"
Cohesion: 0.09
Nodes (38): _client(), client_kwargs(), flush_langfuse(), get_langfuse_client(), get_trace_id(), install_on_dropped(), instrument_openai_client(), observation() (+30 more)

### Community 32 - "Taxonomy extract aliases"
Cohesion: 0.29
Nodes (9): review_classify_node(), get_all_doc_types(), get_doc_class(), get_extraction_schema_name(), get_sorter_label_set(), resolve_extract_class(), KANBAN-062 (Lane A): independent agent second opinion on a medium-band…, Map a sorter label to the live taxonomy class used for extraction. Live… (+1 more)

### Community 33 - "sync models"
Cohesion: 0.29
Nodes (10): default_environment(), _client(), _cost_models(), _existing_by_name(), main(), _match_pattern(), _prices_match(), sync_models() (+2 more)

### Community 37 - "guards"
Cohesion: 0.20
Nodes (14): apply_classification_guard(), apply_extraction_guard(), guard_classification(), guard_extraction(), _has_substantive_content(), _is_valid_confidence(), _valid_subtypes(), Guardrails for agent outputs. Agents are LLMs — they can return junk even when… (+6 more)

### Community 38 - "sync langfuse logs"
Cohesion: 0.24
Nodes (12): main(), _slug(), _client(), main(), _parse_since(), sync_logs(), _trace_basics(), _trace_stage() (+4 more)

### Community 4 - "Hub subclass inventories"
Cohesion: 0.14
Nodes (26): clause_handoff(), skip_conflict_field(), coerce_gt_value(), _compact(), enrich_extraction(), _normalize(), normalize_claim_type(), normalize_communication_type() (+18 more)

### Community 40 - "langfuse tracing"
Cohesion: 0.19
Nodes (12): attach_run_scores(), ensure_score_configs_if_enabled(), _environment(), legalbench_trace(), question_observation(), is_enabled(), Any, Langfuse tracing for LegalBench runs. One trace per run (deterministic seed =… (+4 more)

### Community 44 - "cuad maud"
Cohesion: 0.17
Nodes (19): as_clause_lines(), enrich_contract_extraction(), flatten_cuad_clause_labels(), flatten_maud_clause_labels(), infer_merger_consideration(), normalize_consideration(), parse_json_obj(), normalize_subtype() (+11 more)

### Community 45 - "Intake clerk"
Cohesion: 0.25
Nodes (10): apply_intake(), deterministic_normalize(), intake_span_output(), looks_messy(), check_contract(), select_stratified(), Deterministic intake clerk — whitespace / hyphen / NBSP normalize. Procedural…, Normalize ``text`` and emit the ``normalize-intake`` span. Returns… (+2 more)

### Community 47 - "bootstrap"
Cohesion: 0.29
Nodes (10): bootstrap_ci(), _clean(), delta_significance(), _resample_means(), Any, Random, Bootstrap confidence intervals and small-sample delta testing. Ported verbatim…, Coerce a per-document score list to floats, dropping None/non-numeric. (+2 more)

### Community 48 - "fetch external samples"
Cohesion: 0.33
Nodes (10): _caption_from_text(), _download(), fetch_atticus(), fetch_legalbench(), fetch_pileoflaw(), main(), _stream_pol_records(), Path (+2 more)

### Community 49 - "cutover"
Cohesion: 0.40
Nodes (9): cutover_agent(), cutover_all(), list_agents(), list_local_models(), load_config(), main(), recommend_cutover_order(), save_config() (+1 more)

### Community 51 - "env utils"
Cohesion: 0.28
Nodes (8): bool_env(), get_env(), load_env(), require_env(), Load ``braintrust.env`` then ``.env`` into the environment (idempotent).…, Validate that all given environment variables are set and non-empty. Returns…, Get an environment variable with a default fallback., Get a boolean environment variable.

### Community 53 - "db"
Cohesion: 0.18
Nodes (16): _apply_sqlite_pragmas(), check_connectivity(), close_db(), _engine_kwargs(), _ensure_models_imported(), get_engine(), get_session(), _get_sessionmaker() (+8 more)

### Community 54 - "write pilot report"
Cohesion: 0.42
Nodes (8): build_report(), _clean_extracted(), _field_score_for(), _fmt_usd(), _json_block(), _load_config(), main(), _manifest_rows()

### Community 56 - "sync dataset"
Cohesion: 0.26
Nodes (13): _escape(), generate_pdf_from_text(), _load_manifest(), prepare_samples(), _client(), _doc_text(), _ensure_dataset(), main() (+5 more)

### Community 57 - "Docclass prompt arm"
Cohesion: 0.20
Nodes (10): list_prompts(), PROMPT_TEMPLATES(), docclass_prompts_enabled(), langchain_prompt_version(), managed_prompt_lookup(), List all available prompt versions., Return all prompt templates as a dict. Single source of truth for…, Opt-in KANBAN-090 docclass prompt arm at runtime. Production agent prompts stay… (+2 more)

### Community 58 - "scoring"
Cohesion: 0.25
Nodes (13): equivalent_subtypes(), _binary_f1(), _ece(), _mean(), _safe_div(), score_binary(), score_multiclass(), Any (+5 more)

### Community 59 - "run pilot (59)"
Cohesion: 0.29
Nodes (7): _check_cost_watchdog(), _fetch_openrouter_prices(), _price_for(), _record_langchain_response(), Warn at $0.15, abort the run at $0.20 (cumulative across all samples)., Mirror _wrap_client's usage/cost accounting for a LangChain response., Fetch live OpenRouter pricing (per-token), normalized to $/M tokens. The…

### Community 60 - "phoenix setup"
Cohesion: 0.21
Nodes (12): flush_phoenix(), _init_opentelemetry(), _instrument_openai(), instrument_openai_client(), is_configured(), phoenix_enabled(), Arize Phoenix tracing backend — local, cost-free default for llm-mailroom.…, Return ``client`` with Phoenix auto-tracing activated (no-op if disabled).… (+4 more)

### Community 61 - "braintrust setup"
Cohesion: 0.32
Nodes (7): configure(), flush_braintrust(), instrument_openai_client(), is_configured(), Braintrust tracing backend — alternative to Langfuse. Switch to it with…, Initialize Braintrust (idempotent). Returns True when active., Wrap `client` with Braintrust instrumentation, or return it unchanged.

### Community 62 - "prompts"
Cohesion: 0.40
Nodes (5): family_classification_prompt_v1(), get_prompt(), Versioned LegalBench task prompts. Prompt version = experiment identity in the…, Fill the 25-family list into the multiclass prompt (called per run so the…, Resolve a prompt version to its system-prompt text.

### Community 63 - "Chunked extraction"
Cohesion: 0.40
Nodes (5): _chunk_config(), _extract_contracts(), _run_chunked_extraction(), Chunked-extraction config from taxonomy.yaml (`chunking:` block). Chunking…, Run a specialist extraction, chunking long documents (v15+ pass).…

### Community 64 - "run vision sweep"
Cohesion: 0.36
Nodes (6): load_env(), _base_env(), main(), run_config(), Path, Load environment variables from a .env file. The app reads its configuration…

### Community 65 - "build graph (65)"
Cohesion: 0.50
Nodes (4): _prompt_versions(), _bound_prompt_versions(), Prompt versions bound during the run (best-effort; Langfuse-managed prompts…, Version keys currently wired into production / agent defaults. Used for catalog…

### Community 67 - "main"
Cohesion: 0.67
Nodes (3): _require_token(), Request, Dependency: reject requests without the bearer token (audit L-2).

### Community 8 - "Field scoring & metrics"
Cohesion: 0.07
Nodes (36): _apply_taxonomy_settings(), field_is_ambiguous(), get_field_types(), get_type_bands(), warm_embedding_model(), _date_pair_days(), extraction_diagnostics(), _mean() (+28 more)

### Community 9 - "CUAD corpus loaders"
Cohesion: 0.19
Nodes (20): _contracts_from_annotations(), _contracts_from_txt(), _download(), download_all(), _list_hf_files(), _load_subtype_taxonomy(), main(), _normalize_category() (+12 more)

## Knowledge Gaps
- **1 isolated node(s):** `mailroom`
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `LangChain BaseAgent` to `Hugging Face pilot`, `LangChain specialists`, `run pilot`, `Sorter classification`, `Eval mocks & validation`, `Agent toolkit & memory`, `base agent`, `base agent (77)`, `base agent (78)`, `Run limits & budgets`, `agent`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `load_config()` connect `Run limits & budgets` to `Taxonomy extract aliases`, `sync models`, `Sorter classification`, `Managed prompts & judges`, `judge`, `Agent toolkit & memory`, `Field scoring & metrics`, `PDF & image transcription`, `FastAPI intake`, `Confidence routing`, `Pipeline execution`, `Vision rendering`, `Inbox bins`, `Langfuse evaluator sync`, `retry`, `Graph nodes & state`, `Chunked extraction`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `load_env()` connect `run vision sweep` to `Catalog & audit trail`, `Hugging Face pilot`, `sync models`, `run pilot`, `Eval mocks & validation`, `sync langfuse logs`, `Field scoring & metrics`, `CUAD corpus loaders`, `sync dashboards`, `logging`, `FastAPI intake`, `Quality scores`, `Inbox bins`, `Watcher ingest`, `Langfuse evaluator sync`, `sync dataset`, `providers`, `prompts docclass`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `BaseAgent` (e.g. with `SorterAgent` and `_SpecialistBase`) actually correct?**
  _`BaseAgent` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `BaseAgent` (e.g. with `ArbiterAgent` and `BossAgent`) actually correct?**
  _`BaseAgent` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `build_graph()` (e.g. with `archive_node()` and `ingest_node()`) actually correct?**
  _`build_graph()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **What connects `mailroom` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
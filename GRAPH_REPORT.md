# Graph Report - llm-mailroom  (2026-08-27)

## Corpus Check
- code-only production src/ — tests, notebooks, and .opencode/skills excluded

## Summary
- 1511 nodes · 3587 edges · 94 communities (82 shown, 12 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `13346a92`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Graph nodes & state
- LangChain BaseAgent
- Run limits & budgets
- PDF & image transcription
- LegalBench runner
- Eval mocks & validation
- Watcher ingest
- LLM providers
- config
- LegalBench data
- ops monitor
- audit
- LegalBench agent
- Agent toolkit & memory
- Tracing backends
- Arbiter & Boss
- Mailroom BaseAgent
- Extraction schemas
- Dashboard sync
- logging
- Quality judges
- mock
- PDF & image transcription (57)
- tasks
- Sorter classification
- Catalog & audit trail
- Sorter classification (8)
- LangChain specialists
- HF pilot & honesty gaps
- FastAPI intake
- Hub subclass inventories
- classifier
- Vision rendering
- Quality scores
- Langfuse evaluator sync
- Experiment log
- Field scoring calibration
- CUAD corpus loaders
- Grounded pilot
- CUAD/MAUD inventories
- LLM retry
- Inbox bins
- Langfuse tracing
- Specialist scoring suites
- Langfuse model sync
- Pipeline guards
- Dataset sync
- Langfuse log sync
- LegalBench scoring
- Agent toolkit & memory (47)
- Docclass prompt arm
- Field scoring & metrics
- Tracing backends (5)
- Graph nodes & state (50)
- bootstrap
- Quality judges (53)
- External samples
- Managed prompts
- Prompt cutover
- env utils
- prompts docclass
- Routing & reconsideration
- Pilot reports
- Grounded pilot (63)
- prompts
- compare runs
- Graph nodes & state (66)
- Graph nodes & state (67)
- Field scoring & metrics (68)
- FastAPI intake (69)
- FastAPI intake (70)
- Graph nodes & state (71)
- LangChain BaseAgent (72)
-   init  
- pyproject
- LangChain BaseAgent (79)
- Managed prompts (81)
- Tracing backends (82)
- Tracing backends (83)
- Grounded pilot (91)
- Quality judges (92)

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 37 edges
2. `BaseAgent` - 35 edges
3. `build_graph()` - 33 edges
4. `BaseAgent` - 32 edges
5. `get_langfuse_client()` - 31 edges
6. `get_managed_prompt()` - 28 edges
7. `_execute_run()` - 25 edges
8. `ensure_schema()` - 25 edges
9. `DocumentState` - 23 edges
10. `main()` - 23 edges
11. `inbox_dir()` - 23 edges
12. `load_env()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `PipelineStage` --uses--> `resolve_review()`  [INFERRED]
  src/schemas/manifest.py → src/api/main.py
- `PipelineStage` --uses--> `_move_rejected_to_failed()`  [INFERRED]
  src/schemas/manifest.py → src/api/main.py
- `BaseAgent` --uses--> `SorterAgent`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/sorter_agent.py
- `BaseAgent` --uses--> `_SpecialistBase`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/specialist_agents.py
- `BaseAgent` --uses--> `get_specialist()`  [INFERRED]
  src/langchain_agents/base_agent.py → src/langchain_agents/specialist_agents.py

## Import Cycles
- None detected.

## Communities (94 total, 12 thin omitted)

### Community 0 - "Graph nodes & state"
Cohesion: 0.06
Nodes (85): DocumentState, DocumentManifest, PipelineStage, apply_intake(), arbiter_node(), archive_node(), boss_escalation_node(), _build_checkpointer() (+77 more)

### Community 10 - "LangChain BaseAgent"
Cohesion: 0.10
Nodes (17): BaseAgent, load_skills(), ChatOpenAI, Return the agent's system prompt string., System prompt + agent's skill files + tool descriptions + recent outcome…, Lazily build the LangChain ``ChatOpenAI`` client. Uses the OpenRouter base URL…, Call ``fn()`` retrying transient failures with backoff + jitter. Mirrors…, True when this agent's model accepts image input. Vision capability is config-… (+9 more)

### Community 13 - "Run limits & budgets"
Cohesion: 0.10
Nodes (25): RunBudgetExceeded, RunDeadlineExceeded, _bounded(), compute_run_metrics(), check_token_budget(), estimate_cost(), get_call_timeout_seconds(), get_deadline_seconds() (+17 more)

### Community 17 - "PDF & image transcription"
Cohesion: 0.19
Nodes (14): ImageExtractor, extract_text_from_image(), compile_matter_record(), retry_chat_completion(), langfuse_call_attrs(), get_run_deadline(), record_usage(), BaseAgent (+6 more)

### Community 18 - "LegalBench runner"
Cohesion: 0.18
Nodes (19): RunResult, build_parser(), main(), log_run(), _model_name(), print_summary(), run_task(), _tokens_summary() (+11 more)

### Community 2 - "Eval mocks & validation"
Cohesion: 0.05
Nodes (39): FakeLangChainLLM, _FakeStructuredRunner, chat, _Choices, completions, _EvalLangChainLLM, _HintedEvalLangChainLLM, _MockClient (+31 more)

### Community 24 - "Watcher ingest"
Cohesion: 0.20
Nodes (10): InboxHandler, Watcher, claim_file(), _is_already_processed(), _mark_active(), _unmark_active(), FileSystemEventHandler, Path (+2 more)

### Community 25 - "LLM providers"
Cohesion: 0.22
Nodes (15): ProviderConfig, _check_llm_provider(), get_llm(), get_llm_client(), get_llm_model(), instrument_client(), _build_providers(), get_provider() (+7 more)

### Community 27 - "config"
Cohesion: 0.15
Nodes (12): ContractsSpecialist, ContractsSpecialist, get_extraction_schema(), get_all_doc_types(), get_doc_class(), get_extraction_schema_name(), resolve_extract_class(), _LangChainContractsSpecialist (+4 more)

### Community 29 - "LegalBench data"
Cohesion: 0.16
Nodes (16): CorpusUnavailable, Sample, _fingerprint(), load_cuad_qa(), load_family_rows(), _normalize_prediction(), _extract_binary(), Any (+8 more)

### Community 30 - "ops monitor"
Cohesion: 0.17
Nodes (6): OpsMonitor, _main(), run_ops_monitor(), Event, Pause metadata (actor/reason/expiry) via the TTL-aware helper., Like start(), but exits when ``stop_event`` is set (L-6: signal driven graceful…

### Community 31 - "audit"
Cohesion: 0.23
Nodes (14): AuditLogEntry, archive_document(), _file_sha256(), build_audit_entry(), compute_audit_hash(), compute_audit_hash_v1(), verify_chain(), _verify() (+6 more)

### Community 32 - "LegalBench agent"
Cohesion: 0.14
Nodes (9): LegalBenchAgent, Any, BaseAgent, Model agent for LegalBench runs. Reuses the vendored ``BaseAgent`` machinery —…, One agent instance per task run; answers via structured JSON., LegalBench tasks use the task prompt as-is (no sorter skills)., Yes/no answer with evidence + confidence., One-of-N family classification with confidence. (+1 more)

### Community 34 - "Agent toolkit & memory"
Cohesion: 0.21
Nodes (11): AgentTool, _build_toolkit(), get_tools(), render_tools(), _tool_field_types(), _tool_schema(), _tool_subtypes(), _tool_taxonomy() (+3 more)

### Community 4 - "Arbiter & Boss"
Cohesion: 0.06
Nodes (35): ArbiterAgent, BossAgent, ComplianceSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, InsuranceClaimsSpecialist, build_structured_schema(), _extract_compliance() (+27 more)

### Community 41 - "Mailroom BaseAgent"
Cohesion: 0.23
Nodes (5): BaseAgent, ABC, Build the user-message content for a document input. Vision-capable models get…, Truncate document text to the agent's configured input budget, marking the…, True when this agent's model accepts image input and (optionally) page images…

### Community 42 - "Extraction schemas"
Cohesion: 0.29
Nodes (10): ComplianceFilingExtraction, ContractExtraction, CorporateRecordExtraction, CorrespondenceExtraction, InsuranceClaimExtraction, Matter, get_extraction_schema(), BaseModel (+2 more)

### Community 44 - "Dashboard sync"
Cohesion: 0.29
Nodes (13): WidgetSpec, _client(), _existing_placements(), json_dumps(), main(), _placement_kwargs(), _score_widget(), _spec_to_request() (+5 more)

### Community 45 - "logging"
Cohesion: 0.24
Nodes (8): _RotatingFileSink, setup_logging(), _base_env(), main(), run_config(), RotatingFileHandler, Structured logging setup for Mailroom entrypoints. Configures `structlog` once…, Structlog processor that emits the rendered event dict to a rotating stdlib…

### Community 46 - "Quality judges"
Cohesion: 0.23
Nodes (5): CompletenessJudge, BaseAgent, Render the task specification (taxonomy doc classes) for the judge., Judge whether the sorter's assigned class matches the taxonomy task…, Judge whether the extracted field values are factually accurate (no…

### Community 51 - "mock"
Cohesion: 0.27
Nodes (5): MockLegalBenchModel, _hash(), Any, Deterministic mock model for LegalBench runs (no network, no OpenAI). Answers…, Implements the LegalBenchAgent interface deterministically.

### Community 57 - "PDF & image transcription (57)"
Cohesion: 0.33
Nodes (5): PDFTranscriber, transcribe_pdf(), BaseAgent, Path, Heuristic: if a PDF yields a dense, clean text extraction, the LLM reformat…

### Community 60 - "tasks"
Cohesion: 0.25
Nodes (4): LegalBenchTask, _extract_family(), _family_labels(), LegalBench task registry. Two task families, per the LegalBench taxonomy: -…

### Community 62 - "Sorter classification"
Cohesion: 0.29
Nodes (5): SorterAgent, _LangChainSorterAgent, Mailroom-configured sorter. - Model/budget defaults come from ``taxonomy.yaml``…, Classify a document, optionally with page images attached. Returns ``(doc_type,…, Structured classify used by the graph (includes ``doc_subclass``).

### Community 7 - "Catalog & audit trail"
Cohesion: 0.10
Nodes (45): AuditLogRecord, DocumentRecord, MatterRecord, Base, _all_chains(), main(), get_audit_chain(), get_latest_audit_hash() (+37 more)

### Community 8 - "Sorter classification (8)"
Cohesion: 0.07
Nodes (31): SorterReviewerAgent, SorterAgent, build_structured_schema(), format_sorter_subclass_catalogs(), sorter_subclass_catalog(), valid_sorter_subclasses(), _classification_user_message(), _doc_classes_for_prompt() (+23 more)

### Community 9 - "LangChain specialists"
Cohesion: 0.09
Nodes (21): ComplianceFilingSpecialist, CorporateRecordsSpecialist, CorrespondenceSpecialist, _SpecialistBase, get_prompt(), get_specialist(), _merge_reasoning(), _norm() (+13 more)

### Community 1 - "HF pilot & honesty gaps"
Cohesion: 0.06
Nodes (80): _denial_reasons(), determination_consistency_is_quality(), honesty_trace_metadata(), insurance_determination_consistent(), insurance_determination_issues(), insurance_expected_set_is_homogeneous(), insurance_gt_is_homogeneous(), _norm_determination() (+72 more)

### Community 11 - "FastAPI intake"
Cohesion: 0.11
Nodes (32): _check_database(), get_audit_trail(), get_document_status(), get_matter(), health(), lifespan(), ops_resume(), ops_status() (+24 more)

### Community 12 - "Hub subclass inventories"
Cohesion: 0.12
Nodes (32): clause_handoff(), skip_conflict_field(), coerce_gt_value(), _compact(), enrich_extraction(), _normalize(), normalize_claim_type(), normalize_communication_type() (+24 more)

### Community 14 - "classifier"
Cohesion: 0.11
Nodes (21): classify_image(), clean_prediction(), extract_confidence(), extract_reasoning(), extract_runner_up(), _valid_classes(), build_text_messages(), build_vision_messages() (+13 more)

### Community 15 - "Vision rendering"
Cohesion: 0.16
Nodes (23): _resolved_models(), agent_uses_vision(), _any_specialist_uses_vision(), is_vision_capable(), max_pages(), pipeline_uses_vision(), render_document_pages(), render_image() (+15 more)

### Community 16 - "Quality scores"
Cohesion: 0.12
Nodes (22): ensure_field_score_configs(), score_and_log_extraction(), _client(), emit_pipeline_scores(), ensure_score_configs(), is_enabled(), langfuse_score_name(), _score_data_type() (+14 more)

### Community 19 - "Langfuse evaluator sync"
Cohesion: 0.16
Nodes (21): _build_evaluator_request(), _build_output_definition(), _build_rule_request(), _client(), _current_evaluator_prompt(), _ensure_llm_connection(), _existing_rule_ids(), main() (+13 more)

### Community 20 - "Experiment log"
Cohesion: 0.19
Nodes (20): append_record(), build_record(), default_log_path(), default_sibling_root(), git_snapshot(), _inside(), regenerate(), _run_python() (+12 more)

### Community 21 - "Field scoring calibration"
Cohesion: 0.14
Nodes (19): get_field_types(), warm_embedding_model(), main(), _perturb_date(), _perturb_entity_list(), _perturb_free_text(), _perturb_money(), _perturb_name() (+11 more)

### Community 22 - "CUAD corpus loaders"
Cohesion: 0.19
Nodes (20): _contracts_from_annotations(), _contracts_from_txt(), _download(), download_all(), _list_hf_files(), _load_subtype_taxonomy(), main(), _normalize_category() (+12 more)

### Community 23 - "Grounded pilot"
Cohesion: 0.18
Nodes (19): _attach_field_scoring(), diff_report(), filter_real_samples(), _ground_truth_scores(), _ingest_scores(), main(), misfile_candidates(), _parse_expected_fields() (+11 more)

### Community 26 - "CUAD/MAUD inventories"
Cohesion: 0.20
Nodes (17): as_clause_lines(), enrich_contract_extraction(), flatten_cuad_clause_labels(), flatten_maud_clause_labels(), infer_merger_consideration(), normalize_consideration(), parse_json_obj(), _as_meta() (+9 more)

### Community 28 - "LLM retry"
Cohesion: 0.20
Nodes (15): _is_retryable_error(), _is_json_mode_400(), _is_retryable(), _retry_after_seconds(), _retry_config(), retry_sleep_seconds(), _status_code(), check_run_deadline() (+7 more)

### Community 3 - "Inbox bins"
Cohesion: 0.09
Nodes (52): get_queue(), _move_rejected_to_failed(), _ensure_dirs(), accepted_extensions(), archive_dir(), classified_dir(), clear_ingestion_paused(), failed_dir() (+44 more)

### Community 33 - "Langfuse tracing"
Cohesion: 0.16
Nodes (14): attach_run_scores(), ensure_score_configs_if_enabled(), _environment(), legalbench_trace(), question_observation(), is_enabled(), pipeline_trace(), Any (+6 more)

### Community 36 - "Specialist scoring suites"
Cohesion: 0.22
Nodes (14): attach_single_doc_extras(), _numeric_extra(), score_and_log_intake(), score_intake_suite(), score_with_suite(), unwrap_suite_result(), Any, ExtractionScoreResult (+6 more)

### Community 37 - "Langfuse model sync"
Cohesion: 0.21
Nodes (13): default_environment(), load_env(), _client(), _cost_models(), _existing_by_name(), main(), _match_pattern(), _prices_match() (+5 more)

### Community 38 - "Pipeline guards"
Cohesion: 0.20
Nodes (14): apply_classification_guard(), apply_extraction_guard(), guard_classification(), guard_extraction(), _has_substantive_content(), _is_valid_confidence(), _valid_subtypes(), Guardrails for agent outputs. Agents are LLMs — they can return junk even when… (+6 more)

### Community 39 - "Dataset sync"
Cohesion: 0.26
Nodes (13): _escape(), generate_pdf_from_text(), _load_manifest(), prepare_samples(), _client(), _doc_text(), _ensure_dataset(), main() (+5 more)

### Community 40 - "Langfuse log sync"
Cohesion: 0.24
Nodes (12): main(), _slug(), _client(), main(), _parse_since(), sync_logs(), _trace_basics(), _trace_stage() (+4 more)

### Community 43 - "LegalBench scoring"
Cohesion: 0.25
Nodes (13): equivalent_subtypes(), _binary_f1(), _ece(), _mean(), _safe_div(), score_binary(), score_multiclass(), Any (+5 more)

### Community 47 - "Agent toolkit & memory (47)"
Cohesion: 0.26
Nodes (11): _memory_dir(), _memory_path(), recent_context(), record_outcome(), stats(), _tool_memory(), Path, Per-agent OUTCOME MEMORY for the vendored LangChain agents. Every designated… (+3 more)

### Community 48 - "Docclass prompt arm"
Cohesion: 0.20
Nodes (10): list_prompts(), PROMPT_TEMPLATES(), docclass_prompts_enabled(), langchain_prompt_version(), managed_prompt_lookup(), List all available prompt versions., Return all prompt templates as a dict. Single source of truth for…, Opt-in KANBAN-090 docclass prompt arm at runtime. Production agent prompts stay… (+2 more)

### Community 49 - "Field scoring & metrics"
Cohesion: 0.24
Nodes (11): _date_pair_days(), extraction_diagnostics(), _mean(), _median(), parse_duration_days(), _r2(), Run-level diagnostic metrics for extraction scoring. Ported from ``llm-entity-…, Coefficient of determination ``1 - SS_res/SS_tot`` over (predicted, expected)… (+3 more)

### Community 5 - "Tracing backends (5)"
Cohesion: 0.06
Nodes (51): configure(), flush_braintrust(), instrument_openai_client(), is_configured(), _apply_taxonomy_settings(), client_kwargs(), flush_langfuse(), get_trace_id() (+43 more)

### Community 50 - "Graph nodes & state (50)"
Cohesion: 0.18
Nodes (11): _latest_audit_hash(), _persist_provenance(), _persist_scores(), _run_coro(), _touch_heartbeat(), _write_catalog_record(), Run a coroutine from a sync context: schedule it on the running loop when one…, Best-effort fetch of the last entry_hash for this doc_id (the previous link of… (+3 more)

### Community 52 - "bootstrap"
Cohesion: 0.29
Nodes (10): bootstrap_ci(), _clean(), delta_significance(), _resample_means(), Any, Random, Bootstrap confidence intervals and small-sample delta testing. Ported verbatim…, Coerce a per-document score list to floats, dropping None/non-numeric. (+2 more)

### Community 53 - "Quality judges (53)"
Cohesion: 0.31
Nodes (10): create_trace_score(), is_real_sample(), _dim_summary(), _ingest(), judge_one(), main(), print_summary(), _raw_text_for() (+2 more)

### Community 54 - "External samples"
Cohesion: 0.33
Nodes (10): _caption_from_text(), _download(), fetch_atticus(), fetch_legalbench(), fetch_pileoflaw(), main(), _stream_pol_records(), Path (+2 more)

### Community 55 - "Managed prompts"
Cohesion: 0.31
Nodes (9): _langchain_prompt(), prompt_templates(), get_langfuse_client(), _client(), _current_production(), main(), sync_one(), agent_name -> local prompt template (with `{{var}}` placeholders). Single… (+1 more)

### Community 56 - "Prompt cutover"
Cohesion: 0.40
Nodes (9): cutover_agent(), cutover_all(), list_agents(), list_local_models(), load_config(), main(), recommend_cutover_order(), save_config() (+1 more)

### Community 58 - "env utils"
Cohesion: 0.28
Nodes (8): bool_env(), get_env(), load_env(), require_env(), Load ``braintrust.env`` then ``.env`` into the environment (idempotent).…, Validate that all given environment variables are set and non-empty. Returns…, Get an environment variable with a default fallback., Get a boolean environment variable.

### Community 59 - "prompts docclass"
Cohesion: 0.28
Nodes (7): _append(), _build_versions(), _rules(), Docclass prompt variants for every mailroom classification-chain role.…, Pure-appended docclass variant: base is a STRICT PREFIX of the result., Derive every variant from the live production template of that role., # NOTE: fragment assertions in tests target SHORT substrings that do not cross

### Community 6 - "Routing & reconsideration"
Cohesion: 0.08
Nodes (52): after_arbiter(), after_boss(), after_classify(), after_extraction(), after_extraction_gated(), after_human_review(), after_judge(), after_report() (+44 more)

### Community 61 - "Pilot reports"
Cohesion: 0.42
Nodes (8): build_report(), _clean_extracted(), _field_score_for(), _fmt_usd(), _json_block(), _load_config(), main(), _manifest_rows()

### Community 63 - "Grounded pilot (63)"
Cohesion: 0.29
Nodes (7): _check_cost_watchdog(), _fetch_openrouter_prices(), _price_for(), _record_langchain_response(), Warn at $0.15, abort the run at $0.20 (cumulative across all samples)., Mirror _wrap_client's usage/cost accounting for a LangChain response., Fetch live OpenRouter pricing (per-token), normalized to $/M tokens. The…

### Community 64 - "prompts"
Cohesion: 0.40
Nodes (5): family_classification_prompt_v1(), get_prompt(), Versioned LegalBench task prompts. Prompt version = experiment identity in the…, Fill the 25-family list into the multiclass prompt (called per run so the…, Resolve a prompt version to its system-prompt text.

### Community 65 - "compare runs"
Cohesion: 0.60
Nodes (5): _aggregate(), _cell(), main(), _print_table(), _scores_of()

### Community 66 - "Graph nodes & state (66)"
Cohesion: 0.40
Nodes (5): _chunk_config(), _extract_contracts(), _run_chunked_extraction(), Chunked-extraction config from taxonomy.yaml (`chunking:` block). Chunking…, Run a specialist extraction, chunking long documents (v15+ pass).…

### Community 67 - "Graph nodes & state (67)"
Cohesion: 0.50
Nodes (4): _prompt_versions(), _bound_prompt_versions(), Prompt versions bound during the run (best-effort; Langfuse-managed prompts…, Version keys currently wired into production / agent defaults. Used for catalog…

### Community 68 - "Field scoring & metrics (68)"
Cohesion: 0.50
Nodes (4): field_is_ambiguous(), get_type_bands(), Per-field-type ambiguous-band overrides from ``field_scoring.type_bands``.…, Is this field score in the (possibly type-specific) ambiguous band? Band check…

### Community 69 - "FastAPI intake (69)"
Cohesion: 0.67
Nodes (3): _require_token(), Request, Dependency: reject requests without the bearer token (audit L-2).

## Knowledge Gaps
- **1 isolated node(s):** `mailroom`
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `LangChain BaseAgent` to `LegalBench agent`, `HF pilot & honesty gaps`, `Eval mocks & validation`, `Agent toolkit & memory`, `Sorter classification (8)`, `LangChain specialists`, `LangChain BaseAgent (72)`, `LangChain BaseAgent (78)`, `LangChain BaseAgent (79)`, `Grounded pilot`, `LLM retry`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `load_config()` connect `Vision rendering` to `Graph nodes & state`, `Inbox bins`, `Tracing backends (5)`, `Routing & reconsideration`, `Sorter classification (8)`, `FastAPI intake`, `Run limits & budgets`, `PDF & image transcription`, `Langfuse evaluator sync`, `Field scoring calibration`, `config`, `LLM retry`, `Agent toolkit & memory`, `Langfuse model sync`, `Extraction schemas`, `Quality judges`, `PDF & image transcription (57)`, `Graph nodes & state (66)`, `Field scoring & metrics (68)`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `load_env()` connect `Langfuse model sync` to `HF pilot & honesty gaps`, `compare runs`, `Inbox bins`, `Eval mocks & validation`, `Dataset sync`, `Langfuse log sync`, `Catalog & audit trail`, `FastAPI intake`, `Dashboard sync`, `logging`, `Langfuse evaluator sync`, `Field scoring calibration`, `CUAD corpus loaders`, `Grounded pilot`, `Watcher ingest`, `LLM providers`, `Quality judges (53)`, `Managed prompts`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `BaseAgent` (e.g. with `SorterAgent` and `_SpecialistBase`) actually correct?**
  _`BaseAgent` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `build_graph()` (e.g. with `arbiter_node()` and `archive_node()`) actually correct?**
  _`build_graph()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `BaseAgent` (e.g. with `ArbiterAgent` and `CompletenessJudge`) actually correct?**
  _`BaseAgent` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `mailroom` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
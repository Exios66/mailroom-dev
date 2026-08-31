# Graph Report - llm-mailroom  (2026-08-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1905 nodes · 4557 edges · 104 communities (90 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 127 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d93894a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 41 edges
2. `BaseAgent` - 37 edges
3. `BaseAgent` - 35 edges
4. `ensure_schema()` - 35 edges
5. `build_graph()` - 33 edges
6. `get_langfuse_client()` - 31 edges
7. `_execute_run()` - 29 edges
8. `async_session()` - 29 edges
9. `get_managed_prompt()` - 28 edges
10. `load_env()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `boss_escalation_node()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `build_graph()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `_build_handoff_context()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `classify_node()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `extract_node()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py

## Import Cycles
- None detected.

## Communities (104 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (74): as_clause_lines(), clause_handoff(), enrich_contract_extraction(), flatten_cuad_clause_labels(), flatten_maud_clause_labels(), infer_merger_consideration(), normalize_consideration(), parse_json_obj() (+66 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (62): OpenAI, get_llm(), get_llm_client(), get_llm_model(), instrument_client(), Wrap the OpenAI client with the active tracing backend. Both Langfuse…, _build_providers(), get_provider() (+54 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (56): get, Request, active_api_tokens(), analyze_audit_database(), assert_bind_allowed(), _check_database(), _check_llm_provider(), _csv_tokens() (+48 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (49): _LangChainSorterAgent, Mailroom-configured sorter. - Model/budget defaults come from ``taxonomy.yaml``…, Classify a document, optionally with page images attached. Returns ``(doc_type,…, Structured classify used by the graph (includes ``doc_subclass``)., BaseAgent, Independent second-opinion classifier (blind re-classification)., SorterReviewerAgent, SorterAgent (+41 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (27): FakeLangChainLLM, _FakeStructuredRunner, is_classify_call(), MAILROOM-LOCAL (not from upstream): deterministic fake LangChain LLM. The…, Runnable returned by ``with_structured_output``: invoke() yields the…, Extract the human text from a LangChain message list, handling multimodal list…, Replacement for the ChatOpenAI instance the vendored agents construct. -…, user_text_from_messages() (+19 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (24): _LangChainContractsSpecialist, ContractsSpecialist, Contracts specialist — LangChain version vendored from llm-entity-extraction.…, Mailroom-configured contracts specialist. - Model/budget defaults come from…, get_prompt(), Get a prompt by version name. Args: version: Prompt version key (e.g.,…, ComplianceFilingSpecialist, ContractsSpecialist (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): Event, post, ops_resume(), ops_sweep(), Run a one-off Boss ops-monitor sweep on demand. Mirrors the scheduled…, Clear the ingestion-pause flag so the watcher resumes processing. The ops…, Load the embedding model OFF the document path (O-10). The first grounded run…, warm_embedding_model() (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (39): _move_rejected_to_failed(), Resolve a REVIEW / RECONSIDER item (The-Mailroom PR #18 / #20). Body (JSON or…, Close the conveyor loop for a rejected review: move the file from the review…, resolve_review(), _ensure_dirs(), archive_dir(), classified_dir(), ensure_dirs() (+31 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (36): _attach_field_scoring(), _check_cost_watchdog(), diff_report(), _fetch_openrouter_prices(), filter_real_samples(), _ground_truth_scores(), _ingest_scores(), main() (+28 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (21): Arbiter agent — Lane B judgment arbitration (KANBAN-063). Architecture…, build_structured_schema(), BossAgent, BaseAgent, ComplianceSpecialist, BaseAgent, CorrespondenceSpecialist, BaseAgent (+13 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (36): _build_handoff_context(), _build_specialist_dispatch(), classify_node(), _detect_conflict(), _enrich_contract_result(), _extract_dispatch_key(), extract_node(), Deterministically compare a fresh extraction against archived records of the… (+28 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (34): _date_pair_days(), extraction_diagnostics(), _mean(), _median(), parse_duration_days(), _r2(), Run-level diagnostic metrics for extraction scoring. Ported from ``llm-entity-…, Coefficient of determination ``1 - SS_res/SS_tot`` over (predicted, expected)… (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (34): arbiter_node(), archive_node(), _catalog_upsert(), catalog_write_node(), _clean_fields_for_judge(), compile_report_node(), _execute_run(), human_review_node() (+26 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (32): _bounded(), _build_checkpointer(), _chunk_config(), entry_route(), _extract_compliance(), _extract_contracts(), _extract_corporate_records(), _extract_correspondence() (+24 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (31): ensure_field_score_configs(), ExtractionScoreResult, Wire deterministic field scoring into Langfuse (GitHub issue #5). The scoring…, Idempotent: register the field-scoring configs in the Langfuse project. The…, Score one extraction deterministically and push every score to Langfuse,…, score_and_log_extraction(), _client(), create_trace_score() (+23 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (15): ChatOpenAI, BaseAgent, Return the agent's system prompt string., System prompt + agent's skill files + tool descriptions + recent outcome…, Lazily build the LangChain ``ChatOpenAI`` client. Uses the OpenRouter base URL…, Call ``fn()`` retrying transient failures with backoff + jitter. Mirrors…, True when this agent's model accepts image input. Vision capability is config-…, Build the human-message content for a document input. Vision-capable models get… (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.16
Nodes (30): date, main(), Namespace, _run(), audit_to_row(), daily_audit_path(), daily_documents_path(), document_to_row() (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (31): build_graph(), after_arbiter(), after_boss(), after_classify(), after_extraction(), after_extraction_gated(), after_human_review(), after_judge() (+23 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (18): FileSystemEventHandler, claim_file(), is_ingestion_paused(), Check if the ops monitor has paused ingestion (auto-expiring TTL)., acquire_watcher_lock(), _finalize_claimed_on_error(), InboxHandler, _is_already_processed() (+10 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (26): apply_intake(), Deterministic intake clerk — whitespace / hyphen / NBSP normalize. Procedural…, Normalize ``text`` and emit the ``normalize-intake`` span. Returns…, _emit_pipeline_result(), _extract_text_from_docx(), _extract_text_from_image(), _extract_text_from_pdf(), _file_sha256() (+18 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (27): get_confidence_thresholds(), Return confidence / Lane B budgets, optionally merged with per-class severity.…, align_class(), _as_float(), class_misses_ground_truth(), collect_review_causes(), coverage_below_floor(), expected_class() (+19 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (25): _client(), client_kwargs(), get_langfuse_client(), install_on_dropped(), instrument_openai_client(), observation(), _optional_float(), _optional_int() (+17 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (26): count_first_pass_throughput(), DocumentRecord, get_document(), get_documents_by_stage(), get_error_rate_by_doc_type(), get_matter_documents(), get_recent_documents(), get_stuck_documents() (+18 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (15): ImageExtractor, BaseAgent, Path, Image extraction agent — uses vision-capable LLMs to extract text from images.…, PDFTranscriber, BaseAgent, Path, PDF transcription agent — converts PDF documents to markdown for downstream… (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (24): _heartbeat_file_path(), list_stale_processing_files(), load_taxonomy(), mark_processing_dead(), move_to_review(), park_for_review(), Move a stale processing file to the failed bin (finalize path). Used by startup…, True when a terminal-stage manifest already exists for this filename. A… (+16 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (25): finalize_report(), find_sample_text(), hf_corpus_honesty(), _inbox_filename(), latest_hf_reports(), _load_resume(), main(), _mock_samples() (+17 more)

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (20): ensure_process_tracing(), Wire drop-warnings + atexit flush for a short-lived process. Call once from…, _escape(), generate_pdf_from_text(), is_real_sample(), _load_manifest(), prepare_samples(), Path (+12 more)

### Community 27 - "Community 27"
Cohesion: 0.14
Nodes (9): BaseAgent, ABC, True when this agent's model accepts image input and (optionally) page images…, Build the user-message content for a document input. Vision-capable models get…, Extract a long document in overlapping windows and merge the passes. Documents…, Domain skill files appended below the managed prompt (Langfuse prompt linking…, Truncate document text to the agent's configured input budget, marking the…, Sorter agent — LangChain version vendored from llm-entity-extraction. Re-… (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (19): flush_braintrust(), flush_langfuse(), get_trace_id(), shutdown_langfuse(), flush_phoenix(), Force-export buffered spans without disabling the provider., _atexit_flush(), flush() (+11 more)

### Community 29 - "Community 29"
Cohesion: 0.17
Nodes (21): active_corpus(), adapt_hub_row(), example_for_class(), example_rows(), examples_by_class(), hub_sample(), load_example_pack(), pipeline_corpora() (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.16
Nodes (21): _build_evaluator_request(), _build_output_definition(), _build_rule_request(), _client(), _current_evaluator_prompt(), _ensure_llm_connection(), _existing_rule_ids(), main() (+13 more)

### Community 31 - "Community 31"
Cohesion: 0.19
Nodes (20): CompletedProcess, append_record(), build_record(), default_log_path(), default_sibling_root(), git_snapshot(), _inside(), Any (+12 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (20): _denial_reasons(), determination_consistency_is_quality(), honesty_trace_metadata(), insurance_determination_consistent(), insurance_determination_issues(), insurance_expected_set_is_homogeneous(), insurance_gt_is_homogeneous(), _norm_determination() (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (20): _contracts_from_annotations(), _contracts_from_txt(), _download(), download_all(), _list_hf_files(), _load_subtype_taxonomy(), main(), _normalize_category() (+12 more)

### Community 34 - "Community 34"
Cohesion: 0.19
Nodes (17): archive_document(), _file_sha256(), Path, Best-effort sha256 of the archived file (audit A-7)., AuditLogEntry, build_audit_entry(), compute_audit_hash(), compute_audit_hash_v1() (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.19
Nodes (18): _is_retryable_error(), ABC, Exception, Same retryable classification as llm/retry.py: connection errors, timeouts, 429…, _is_json_mode_400(), _is_retryable(), Exception, Transient-failure retry for LLM chat completions. Wraps… (+10 more)

### Community 36 - "Community 36"
Cohesion: 0.18
Nodes (19): agent_uses_vision(), _any_specialist_uses_vision(), is_vision_capable(), max_pages(), pipeline_uses_vision(), Path, Vision-capable model helpers for the mailroom pipeline. Some input agents (e.g.…, Render pages of a PDF to a list of PNG image data-URIs. `cap` is the page… (+11 more)

### Community 37 - "Community 37"
Cohesion: 0.16
Nodes (19): _alnum(), _catalog_by_trace(), completed_filenames(), enrich_sample_row(), expected_fields_for_sample(), expected_fields_meta(), _loose_label_match(), _public_extracted() (+11 more)

### Community 38 - "Community 38"
Cohesion: 0.20
Nodes (16): ArgumentParser, build_parser(), main(), LegalBench suite CLI. Run a LegalBench task, trace it to Langfuse, and log the…, LegalBench evaluation suite — a second lens on model quality. The suite runs…, log_run(), _model_name(), print_summary() (+8 more)

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (14): FastAPI, lifespan(), count_inbox_pending(), list_inbox_files(), Processable documents waiting in the inbox (excludes `.meta` sidecars). The-…, Liveness beacon: the watcher touches this file every rescan cycle. `/health`…, touch_watcher_heartbeat(), embed_watcher_enabled() (+6 more)

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (15): classify_image(), clean_prediction(), extract_confidence(), extract_reasoning(), extract_runner_up(), Path, Extract the model's self-reported confidence (0-1) from a response., Classify a document image using a vision model through OpenRouter API. Args:… (+7 more)

### Community 41 - "Community 41"
Cohesion: 0.16
Nodes (15): _append(), _build_versions(), Docclass prompt variants for every mailroom classification-chain role.…, Pure-appended docclass variant: base is a STRICT PREFIX of the result., Derive every variant from the live production template of that role., # NOTE: fragment assertions in tests target SHORT substrings that do not cross, _rules(), _langchain_prompt() (+7 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (17): CorpusUnavailable, _fingerprint(), load_cuad_qa(), load_family_rows(), _normalize_prediction(), Any, Path, RuntimeError (+9 more)

### Community 43 - "Community 43"
Cohesion: 0.15
Nodes (17): compute_run_metrics(), Core per-run metrics, computed for EVERY finished run regardless of the tracing…, check_token_budget(), estimate_cost(), get_deadline_seconds(), get_max_total_output_tokens(), get_run_limits(), _price_for() (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.18
Nodes (16): AsyncSession, _apply_sqlite_pragmas(), check_connectivity(), close_db(), _engine_kwargs(), _ensure_models_imported(), get_engine(), get_session() (+8 more)

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (12): InsuranceClaimsSpecialist, BaseAgent, get_extraction_schema(), normalize_extraction(), Return the extraction JSON schema for a doc type (None if unknown)., Guarantee the extraction carries EVERY schema field. The model occasionally…, enrich_insurance_from_text(), normalize_specialist_extraction() (+4 more)

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (16): Dojo per-class sorter catalog (empty for unknown / retired types)., Catalog keys the classification guard accepts for ``doc_subclass``. Contract…, sorter_subclass_catalog(), valid_sorter_subclasses(), apply_extraction_guard(), guard_classification(), guard_extraction(), _has_substantive_content() (+8 more)

### Community 47 - "Community 47"
Cohesion: 0.19
Nodes (14): Count outcomes by source and by feedback keyword (for observability)., stats(), AgentTool, _build_toolkit(), get_tools(), Per-agent TOOL registry for the vendored LangChain agents. Each designated…, Return the agent's toolkit (built once, cached)., Render the agent's tool descriptions as a prompt appendix so the model knows… (+6 more)

### Community 48 - "Community 48"
Cohesion: 0.28
Nodes (16): all_local_pack_samples(), compliance_local_samples(), corporate_extraction_samples(), _hydrate(), insurance_contrast_samples(), local_pack_status(), _mean(), _perfect_extract_summary() (+8 more)

### Community 49 - "Community 49"
Cohesion: 0.15
Nodes (10): build_structured_schema(), Build a JSON schema dict for structured output. ``title`` is required by…, LegalBenchAgent, Any, BaseAgent, One agent instance per task run; answers via structured JSON., LegalBench tasks use the task prompt as-is (no sorter skills)., Yes/no answer with evidence + confidence. (+2 more)

### Community 50 - "Community 50"
Cohesion: 0.19
Nodes (12): BaseException, classify_run_failure(), failure_audit_detail(), Any, Classify pipeline crashes so aborted runs are distinguishable. ``run_pipeline``…, Return ``failure_class``, ``reason``, and ``detail`` for an abort., _status_code(), Exception (+4 more)

### Community 51 - "Community 51"
Cohesion: 0.15
Nodes (15): boss_escalation_node(), _emit_stage_audit(), _fetch_matter_context(), _latest_audit_hash(), _persist_provenance(), _persist_scores(), Best-effort fetch of archived matter records for the Boss / conflict detection.…, Run a coroutine from a sync context: schedule it on the running loop when one… (+7 more)

### Community 53 - "Community 53"
Cohesion: 0.20
Nodes (14): main(), _perturb_date(), _perturb_entity_list(), _perturb_free_text(), _perturb_money(), _perturb_name(), _predictions_for(), Random (+6 more)

### Community 54 - "Community 54"
Cohesion: 0.28
Nodes (14): _api(), check_payload(), _die(), main(), publish(), Namespace, Path, Validate the Space card + Docker payload. Returns human-readable notes. (+6 more)

### Community 55 - "Community 55"
Cohesion: 0.19
Nodes (14): _parse_resolve_payload(), Accept JSON (The-Mailroom proxy) or form-urlencoded (legacy clients). The-…, apply_classification_override(), coerce_extracted_data(), live_doc_types(), normalize_optional_str(), Any, Empty / whitespace → None (visualizer sends '' for 'keep current'). (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.25
Nodes (13): equivalent_subtypes(), Return True when two subtype keys are the same family or members of the same…, _binary_f1(), _ece(), _mean(), Any, Deterministic scoring for LegalBench runs — every number computed locally. No…, Expected calibration error over confidence/outcome pairs. (+5 more)

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (13): _client(), _existing_placements(), json_dumps(), main(), _placement_kwargs(), # NOTE: dimension on `model` (the requested model string, e.g., _score_widget(), _spec_to_request() (+5 more)

### Community 58 - "Community 58"
Cohesion: 0.19
Nodes (11): Enum, _existing_processing_doc_id(), _finalize_aborted(), Find the doc_id of an in-flight manifest for this filename. A run that crashed…, Turn a run that hit a hard limit (or crashed) into a failed result. Moves the…, Persist a minimal catalog record (used for aborted runs that never reach the…, _write_catalog_record(), DocumentManifest (+3 more)

### Community 59 - "Community 59"
Cohesion: 0.21
Nodes (10): Independently classify the document. Returns ``{doc_type, contract_subtype,…, format_sorter_subclass_catalogs(), User-message catalog block (not Mustache — doctrine stays placeholder-free)., _classification_user_message(), _doc_classes_for_prompt(), finalize_sorter_result(), Normalize sorter JSON: CUAD ``contract_subtype`` + per-class ``doc_subclass``.…, Prefer the live taxonomy catalog; fall back to the hardcoded table. (+2 more)

### Community 60 - "Community 60"
Cohesion: 0.19
Nodes (11): attach_run_scores(), ensure_score_configs_if_enabled(), _environment(), legalbench_trace(), Any, question_observation(), Langfuse tracing for LegalBench runs. One trace per run (deterministic seed =…, Open the per-run Langfuse trace (no-op when tracing is disabled). (+3 more)

### Community 61 - "Community 61"
Cohesion: 0.24
Nodes (8): RotatingFileHandler, Structured logging setup for Mailroom entrypoints. Configures `structlog` once…, Structlog processor that emits the rendered event dict to a rotating stdlib…, _RotatingFileSink, setup_logging(), _base_env(), main(), run_config()

### Community 62 - "Community 62"
Cohesion: 0.23
Nodes (5): CompletenessJudge, BaseAgent, Render the task specification (taxonomy doc classes) for the judge., Judge whether the sorter's assigned class matches the taxonomy task…, Judge whether the extracted field values are factually accurate (no…

### Community 63 - "Community 63"
Cohesion: 0.20
Nodes (10): list_prompts(), PROMPT_TEMPLATES(), List all available prompt versions., Return all prompt templates as a dict. Single source of truth for…, docclass_prompts_enabled(), langchain_prompt_version(), managed_prompt_lookup(), Opt-in KANBAN-090 docclass prompt arm at runtime. Production agent prompts stay… (+2 more)

### Community 64 - "Community 64"
Cohesion: 0.20
Nodes (8): BaseAgent, Classifies legal documents into mailroom document types. Two classification…, Classify a document and return (doc_type, contract_subtype, confidence,…, Classify and return the raw structured dict (used by eval loops). With…, Re-evaluate a document after low-confidence classification. Args: doc_text: The…, Structured-output schema: live classes plus the ``unknown`` routing token.…, _sorter_schema(), SorterAgent

### Community 65 - "Community 65"
Cohesion: 0.35
Nodes (9): ComplianceFilingExtraction, ContractExtraction, CorporateRecordExtraction, CorrespondenceExtraction, get_extraction_schema(), InsuranceClaimExtraction, BaseModel, Matter (+1 more)

### Community 66 - "Community 66"
Cohesion: 0.27
Nodes (5): _hash(), MockLegalBenchModel, Any, Deterministic mock model for LegalBench runs (no network, no OpenAI). Answers…, Implements the LegalBenchAgent interface deterministically.

### Community 67 - "Community 67"
Cohesion: 0.29
Nodes (10): bootstrap_ci(), _clean(), delta_significance(), Any, Random, Bootstrap confidence intervals and small-sample delta testing. Ported verbatim…, Coerce a per-document score list to floats, dropping None/non-numeric., Percentile-bootstrap 95% CI over per-document scores. Returns ``{"lo", "hi",… (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.25
Nodes (10): _apply_taxonomy_settings(), field_is_ambiguous(), get_field_types(), get_type_bands(), DEPRECATED shim — the field-scoring implementation moved to the package. As of…, Field→scoring-type mapping, auto-loading mailroom's taxonomy. The package…, Per-field-type ambiguous-band overrides from ``field_scoring.type_bands``.…, Is this field score in the (possibly type-specific) ambiguous band? Band check… (+2 more)

### Community 69 - "Community 69"
Cohesion: 0.47
Nodes (10): apply_pin(), _bare(), current_pin(), _github_headers(), latest_release_tag(), main(), _normalize_tag(), Path (+2 more)

### Community 70 - "Community 70"
Cohesion: 0.33
Nodes (10): _caption_from_text(), _download(), fetch_atticus(), fetch_legalbench(), fetch_pileoflaw(), main(), Path, Yield (record, url) for courtlistener opinions, streaming + aborting early per… (+2 more)

### Community 71 - "Community 71"
Cohesion: 0.33
Nodes (10): _client(), main(), _parse_since(), datetime, Path, Poll a trace's scores until they arrive or the timeout elapses. LLM-as-a-judge…, sync_logs(), _trace_basics() (+2 more)

### Community 72 - "Community 72"
Cohesion: 0.20
Nodes (9): build, builder, dockerfilePath, deploy, healthcheckPath, healthcheckTimeout, restartPolicyMaxRetries, restartPolicyType (+1 more)

### Community 73 - "Community 73"
Cohesion: 0.24
Nodes (5): _extract_family(), _family_labels(), get_task(), LegalBenchTask, LegalBench task registry. Two task families, per the LegalBench taxonomy: -…

### Community 74 - "Community 74"
Cohesion: 0.40
Nodes (9): cutover_agent(), cutover_all(), list_agents(), list_local_models(), load_config(), main(), recommend_cutover_order(), save_config() (+1 more)

### Community 75 - "Community 75"
Cohesion: 0.28
Nodes (8): bool_env(), get_env(), load_env(), Load ``braintrust.env`` then ``.env`` into the environment (idempotent).…, Validate that all given environment variables are set and non-empty. Returns…, Get an environment variable with a default fallback., Get a boolean environment variable., require_env()

### Community 76 - "Community 76"
Cohesion: 0.31
Nodes (8): main(), _print_human(), Namespace, _run(), analyze_audit_db(), list_audit_doc_ids(), Every doc_id that has at least one audit entry (ordered)., Parse the full local audit DB into summary stats for operators. Returns counts…

### Community 77 - "Community 77"
Cohesion: 0.31
Nodes (9): load_ground_truth_labels(), load_hf_rows(), _paginate_viewer(), ``max_scan <= 0`` means unlimited (do not use on the 247k Enron set)., Map filename → {expected, expected_subclass} from config=ground_truth. These…, Load default-config text rows joined to ground_truth labels on filename., _scan_cap(), _take_rows() (+1 more)

### Community 78 - "Community 78"
Cohesion: 0.39
Nodes (8): _client(), _cost_models(), _existing_by_name(), main(), _match_pattern(), _prices_match(), Map model_name -> registry Model for every user-defined entry. Paginates: the…, sync_models()

### Community 79 - "Community 79"
Cohesion: 0.42
Nodes (8): build_report(), _clean_extracted(), _field_score_for(), _fmt_usd(), _json_block(), _load_config(), main(), _manifest_rows()

### Community 80 - "Community 80"
Cohesion: 0.36
Nodes (7): DeclarativeBase, Append a hash-chained audit entry for a human review decision. Awaited from the…, _write_review_audit_entry(), AuditLogRecord, get_latest_audit_hash(), write_audit_entry(), Base

### Community 81 - "Community 81"
Cohesion: 0.39
Nodes (7): classes_match(), normalize_class(), Any, Classification KPIs after ``merger_agreement`` became a live MAUD class. Dojo…, True when predicted equals expected. MAUD is not CUAD., Run-level exact accuracy. ``aligned_*`` keys equal exact (deprecated)., score_exact_classification()

### Community 82 - "Community 82"
Cohesion: 0.39
Nodes (6): _json(), main(), offline_pins(), probe(), Any, Return a structured probe of both hosted Spaces.

### Community 83 - "Community 83"
Cohesion: 0.43
Nodes (6): _memory_dir(), _memory_path(), Path, Per-agent OUTCOME MEMORY for the vendored LangChain agents. Every designated…, Render the last ``k`` outcomes for this agent+doc_type as a prompt appendix —…, recent_context()

### Community 84 - "Community 84"
Cohesion: 0.33
Nodes (6): build_text_messages(), build_vision_messages(), Split a classification prompt into (system_text, user_text). system_text is the…, Build an OpenAI-style ``messages`` payload with a text prompt and image., Build a standard text-only messages payload for classification/extraction tasks., split_prompt()

### Community 85 - "Community 85"
Cohesion: 0.33
Nodes (4): ArbiterAgent, BaseAgent, Judgment arbitration on failed judge verdicts., Decide the outcome for a judge-rejected extraction. Returns ``{decision,…

### Community 86 - "Community 86"
Cohesion: 0.40
Nodes (5): compile_matter_record(), _fmt_value(), Any, Procedural matter-record assembler (reporter LLM retired). Compiles…, Assemble a deterministic matter-record summary from extracted fields.…

### Community 87 - "Community 87"
Cohesion: 0.40
Nodes (5): family_classification_prompt_v1(), get_prompt(), Versioned LegalBench task prompts. Prompt version = experiment identity in the…, Fill the 25-family list into the multiclass prompt (called per run so the…, Resolve a prompt version to its system-prompt text.

### Community 88 - "Community 88"
Cohesion: 0.60
Nodes (5): _aggregate(), _cell(), main(), _print_table(), _scores_of()

### Community 89 - "Community 89"
Cohesion: 0.40
Nodes (5): _rate_limit_upload(), Queue a file into the inbox (The-Mailroom PR #30 Inbox proxy). The Observatory…, Sliding-window rate limit for /upload (audit L-18)., upload_document(), UploadFile

### Community 91 - "Community 91"
Cohesion: 0.50
Nodes (3): load_skills(), Per-agent SKILL FILES for the vendored LangChain agents. Each designated agent…, Return the agent's skill files as an appended prompt section. ``max_chars``…

## Knowledge Gaps
- **8 isolated node(s):** `builder`, `dockerfilePath`, `healthcheckPath`, `healthcheckTimeout`, `restartPolicyMaxRetries` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 666 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_config()` connect `Community 68` to `Community 2`, `Community 7`, `Community 9`, `Community 10`, `Community 13`, `Community 14`, `Community 20`, `Community 23`, `Community 24`, `Community 27`, `Community 30`, `Community 35`, `Community 36`, `Community 43`, `Community 47`, `Community 55`, `Community 59`, `Community 62`, `Community 78`, `Community 89`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Community 15` to `Community 64`, `Community 35`, `Community 3`, `Community 5`, `Community 37`, `Community 4`, `Community 8`, `Community 49`, `Community 59`, `Community 93`, `Community 95`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `load_env()` connect `Community 6` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 8`, `Community 16`, `Community 18`, `Community 21`, `Community 24`, `Community 25`, `Community 26`, `Community 30`, `Community 33`, `Community 34`, `Community 37`, `Community 41`, `Community 53`, `Community 57`, `Community 61`, `Community 71`, `Community 76`, `Community 78`, `Community 88`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `BaseAgent` (e.g. with `SorterAgent` and `get_specialist()`) actually correct?**
  _`BaseAgent` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `BaseAgent` (e.g. with `ArbiterAgent` and `BossAgent`) actually correct?**
  _`BaseAgent` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `build_graph()` (e.g. with `arbiter_node()` and `archive_node()`) actually correct?**
  _`build_graph()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builder`, `dockerfilePath`, `healthcheckPath` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
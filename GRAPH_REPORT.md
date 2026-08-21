# Graph Report - llm-mailroom  (2026-08-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2022 nodes · 4318 edges · 115 communities (103 shown, 12 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 134 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df7dea6a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- conftest.py
- test_conveyor_stages.py
- resolve-model.ts
- test_run_limits.py
- build_graph.py
- toolkit.py
- specialist_agents.py
- ensure_schema
- main.py
- guard_classification
- client.py
- base.py
- fetch_full_cuad.py
- bins.py
- build_graph
- BaseAgent
- inbox_dir
- query-analytics.ts
- test_lanes_062_063.py
- routing.py
- run_pilot.py
- ops_monitor.py
- watcher.py
- test_specialists.py
- sync_dashboards.py
- get_confidence_thresholds
- get_managed_prompt
- datetime
- base_agent.py
- .classify_document
- CompletenessJudge
- test_vision.py
- tracing.py
- sync_evaluators.py
- TestVllmProviderSeam
- experiment_log.py
- load_config
- sorter_agent.py
- test_observability.py
- env.py
- TestAuth
- runner.py
- run_quality_judges.py
- PipelineStage
- resume_from_review
- get-generation.ts
- DocumentManifest
- test_legalbench.py
- SorterAgent
- langfuse_tracing.py
- get_field_types
- _NoopLangfuse
- calibrate_field_scoring.py
- FakeEmbedding
- prompt_templates
- setup_logging
- BaseAgent
- scoring.py
- build_structured_schema
- MockLegalBenchModel
- field_is_ambiguous
- scores.py
- get_extraction_schema
- test_field_scoring.py
- modal_vllm.py
- CorporateRecordsSpecialist
- after_judge
- metrics.py
- test_real_sample_gate.py
- tasks.py
- bootstrap.py
- fetch_external_samples.py
- prepare_samples
- Path
- PDFTranscriber
- braintrust_setup.py
- cutover.py
- test_samples_manifest.py
- ensure_score_configs
- ContractsSpecialist
- CourtOpinionsSpecialist
- load_env
- sync_models.py
- test_graphify_skill.py
- traced_node
- sync_dataset.py
- TestEntityList
- openrouter-analytics/scripts/package.json
- suggest-queries.ts
- openrouter-generations/scripts/package.json
- openrouter-models/scripts/package.json
- config.py
- _record_langchain_response
- TestDateField
- ArbiterAgent
- build_record
- TestVendoredRetryContract
- TestJudgeGating
- sync_prompts.py
- _ParseErrorLangChainLLM
- TestMoneyField
- TestScoring
- TestPauseTTL
- TestNormalize
- sync-wiki.sh
- langchain_agents/__init__.py
- mailroom
- _SpecialistBase

## God Nodes (most connected - your core abstractions)
1. `BaseAgent` - 41 edges
2. `build_graph()` - 41 edges
3. `load_config()` - 37 edges
4. `BaseAgent` - 36 edges
5. `inbox_dir()` - 32 edges
6. `get_managed_prompt()` - 32 edges
7. `get_langfuse_client()` - 31 edges
8. `setup_logging()` - 26 edges
9. `DocumentState` - 25 edges
10. `run_pipeline()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `get_audit_trail()` --uses--> `AuditLogEntry`  [INFERRED]
  src/api/main.py → src/schemas/audit.py
- `ImageExtractor` --uses--> `BaseAgent`  [INFERRED]
  src/agents/image_extractor.py → src/agents/base.py
- `arbiter_node()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `boss_escalation_node()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py
- `_build_handoff_context()` --uses--> `DocumentState`  [INFERRED]
  src/graph/build_graph.py → src/graph/state.py

## Import Cycles
- None detected.

## Communities (115 total, 12 thin omitted)

### Community 0 - "conftest.py"
Cohesion: 0.05
Nodes (42): FakeLangChainLLM, _FakeStructuredRunner, is_classify_call(), MAILROOM-LOCAL (not from upstream): deterministic fake LangChain LLM. The…, Extract the human text from a LangChain message list, handling multimodal list…, Replacement for the ChatOpenAI instance the vendored agents construct. -…, Runnable returned by ``with_structured_output``: invoke() yields the…, user_text_from_messages() (+34 more)

### Community 1 - "test_conveyor_stages.py"
Cohesion: 0.06
Nodes (33): archive_document(), _file_sha256(), Path, Best-effort sha256 of the archived file (audit A-7)., run_pipeline(), move_to_archive(), Move a file to the archive with a collision-safe name (audit A-20). POSIX…, AuditLogEntry (+25 more)

### Community 2 - "resolve-model.ts"
Cohesion: 0.06
Nodes (46): apiKey, args, comparison, matched, modelIds, sortBy, apiKey, args (+38 more)

### Community 3 - "test_run_limits.py"
Cohesion: 0.08
Nodes (32): check_run_deadline(), check_token_budget(), estimate_cost(), get_call_timeout_seconds(), get_deadline_seconds(), get_max_total_output_tokens(), get_run_limits(), _price_for() (+24 more)

### Community 4 - "build_graph.py"
Cohesion: 0.08
Nodes (41): boss_escalation_node(), _chunk_config(), _emit_pipeline_result(), _emit_stage_audit(), _execute_run(), _existing_processing_doc_id(), _extract_contracts(), _fetch_matter_context() (+33 more)

### Community 5 - "toolkit.py"
Cohesion: 0.07
Nodes (28): _memory_dir(), _memory_path(), Path, Per-agent OUTCOME MEMORY for the vendored LangChain agents. Every designated…, Count outcomes by source and by feedback keyword (for observability)., Render the last ``k`` outcomes for this agent+doc_type as a prompt appendix —…, recent_context(), stats() (+20 more)

### Community 6 - "specialist_agents.py"
Cohesion: 0.09
Nodes (16): get_prompt(), list_prompts(), PROMPT_TEMPLATES(), Get a prompt by version name. Args: version: Prompt version key (e.g.,…, List all available prompt versions., Return all prompt templates as a dict. Single source of truth for…, ComplianceFilingSpecialist, ContractsSpecialist (+8 more)

### Community 7 - "ensure_schema"
Cohesion: 0.12
Nodes (38): AsyncSession, DeclarativeBase, _all_chains(), main(), _verify(), AuditLogRecord, get_audit_chain(), write_audit_entry() (+30 more)

### Community 8 - "main.py"
Cohesion: 0.08
Nodes (39): FastAPI, get, post, Request, _check_database(), _check_llm_provider(), get_audit_trail(), get_document_status() (+31 more)

### Community 9 - "guard_classification"
Cohesion: 0.08
Nodes (19): Check an extraction against the doc type's pydantic schema. Returns…, validate_extraction(), apply_extraction_guard(), guard_classification(), guard_extraction(), _has_substantive_content(), _is_valid_confidence(), Guardrails for agent outputs. Agents are LLMs — they can return junk even when… (+11 more)

### Community 10 - "client.py"
Cohesion: 0.09
Nodes (28): OpenAI, get_llm(), get_llm_client(), get_llm_model(), instrument_client(), Wrap the OpenAI client with the active tracing backend. Both Langfuse…, _build_providers(), get_provider() (+20 more)

### Community 11 - "base.py"
Cohesion: 0.10
Nodes (22): extract_text_from_image(), ImageExtractor, BaseAgent, Path, Image extraction agent — uses vision-capable LLMs to extract text from images.…, PDF transcription agent — converts PDF documents to markdown for downstream…, compile_matter_record(), _is_json_mode_400() (+14 more)

### Community 12 - "fetch_full_cuad.py"
Cohesion: 0.09
Nodes (36): CorpusUnavailable, _fingerprint(), load_cuad_qa(), load_family_rows(), _normalize_prediction(), Any, Path, Local corpus loaders for the LegalBench suite. Everything reads from corpora… (+28 more)

### Community 13 - "bins.py"
Cohesion: 0.16
Nodes (34): _ensure_dirs(), archive_dir(), classified_dir(), ensure_dirs(), failed_dir(), get_base_dir(), _get_config(), _heartbeat_file_path() (+26 more)

### Community 14 - "build_graph"
Cohesion: 0.11
Nodes (23): archive_node(), _bounded(), _build_checkpointer(), build_graph(), _catalog_upsert(), catalog_write_node(), compile_report_node(), _file_sha256() (+15 more)

### Community 15 - "BaseAgent"
Cohesion: 0.10
Nodes (16): ChatOpenAI, BaseAgent, Return the agent's system prompt string., System prompt + agent's skill files + tool descriptions + recent outcome…, Lazily build the LangChain ``ChatOpenAI`` client. Uses the OpenRouter base URL…, Call ``fn()`` retrying transient failures with backoff + jitter. Mirrors…, Return the FULL document text, capping only past the hard budget. The sorter is…, True when this agent's model accepts image input. Vision capability is config-… (+8 more)

### Community 16 - "inbox_dir"
Cohesion: 0.09
Nodes (18): inbox_dir(), _auth(), client(), fixture, Live-upload → pipeline queue tests. Covers the `/upload` → inbox → watcher…, TestQueue, TestUploadMetadata, TestWatcherExtensionFilter (+10 more)

### Community 17 - "query-analytics.ts"
Cohesion: 0.08
Nodes (29): apiKey, args, section, fetchApi(), fetchMeta(), fetchQuery(), MetaResponse, parseArgs() (+21 more)

### Community 18 - "test_lanes_062_063.py"
Cohesion: 0.10
Nodes (17): arbiter_node(), _clean_fields_for_judge(), judge_verify_node(), Drop pipeline metadata keys before judge/arbiter input (mirrors the…, KANBAN-063 (Lane B): in-pipeline completeness judge. Reuses the offline-battle-…, KANBAN-063 (Lane B): arbitration on a failed judge verdict. Bounded decisions…, KANBAN-062 (Lane A): independent agent second opinion on a medium-band…, review_classify_node() (+9 more)

### Community 19 - "routing.py"
Cohesion: 0.12
Nodes (12): after_boss(), after_classify(), after_extraction(), after_human_review(), after_retry_extraction(), after_retry_extraction_gated(), Route a transient-error flag: retry the same node up to…, Same gate applied to the post-retry extraction router. (+4 more)

### Community 20 - "run_pilot.py"
Cohesion: 0.11
Nodes (29): _attach_field_scoring(), diff_report(), _ground_truth_scores(), _ingest_scores(), main(), _make_mock_langchain_llm(), _make_real_langchain_llm(), misfile_candidates() (+21 more)

### Community 21 - "ops_monitor.py"
Cohesion: 0.09
Nodes (17): Event, DEPRECATED shim — the field-scoring implementation moved to the package. As of…, Load the embedding model OFF the document path (O-10). The first grounded run…, warm_embedding_model(), Warm the score-config schema OFF the document path (O-1).…, warmup_score_configs(), install_on_dropped(), Wire Langfuse's on_dropped callback (O-3): when the SDK's queue overflows or… (+9 more)

### Community 22 - "watcher.py"
Cohesion: 0.13
Nodes (17): FileSystemEventHandler, accepted_extensions(), claim_file(), is_ingestion_paused(), Check if the ops monitor has paused ingestion (auto-expiring TTL)., Accepted inbox file extensions from taxonomy.yaml (with defaults)., Liveness beacon: the watcher touches this file every rescan cycle. `/health`…, touch_watcher_heartbeat() (+9 more)

### Community 23 - "test_specialists.py"
Cohesion: 0.09
Nodes (16): ComplianceSpecialist, BaseAgent, CorrespondenceSpecialist, BaseAgent, DueDiligenceSpecialist, BaseAgent, _build_specialist_dispatch(), _extract_compliance() (+8 more)

### Community 24 - "sync_dashboards.py"
Cohesion: 0.11
Nodes (18): _client(), _existing_placements(), json_dumps(), main(), _placement_kwargs(), # NOTE: dimension on `model` (the requested model string, e.g., _score_widget(), _spec_to_request() (+10 more)

### Community 25 - "get_confidence_thresholds"
Cohesion: 0.11
Nodes (9): RuntimeError, after_retry_classify(), after_review_classify(), KANBAN-062 (Lane A) outcome router. The reviewer's high-confidence label wins…, get_confidence_thresholds(), L-10/L-15: guarded Boss node + classify failure handling (audit fixes). - L-10:…, TestBossGuardedNode, TestClassifyFailureRoutesToReview (+1 more)

### Community 26 - "get_managed_prompt"
Cohesion: 0.11
Nodes (15): Arbiter agent — Lane B judgment arbitration (KANBAN-063). Architecture…, LLM-as-a-judge that evaluates extraction completeness against the source…, BaseAgent, Sorter Reviewer agent — Lane A second-opinion classification (KANBAN-062).…, Independent second-opinion classifier (blind re-classification)., Independently classify the document. Returns ``{doc_type, contract_subtype,…, SorterReviewerAgent, _client() (+7 more)

### Community 27 - "datetime"
Cohesion: 0.15
Nodes (20): datetime, main(), _slug(), _client(), main(), _parse_since(), Path, Poll a trace's scores until they arrive or the timeout elapses. LLM-as-a-judge… (+12 more)

### Community 28 - "base_agent.py"
Cohesion: 0.11
Nodes (15): build_structured_schema(), _is_retryable_error(), ABC, Exception, Same retryable classification as llm/retry.py: connection errors, timeouts, 429…, Build a JSON schema dict for structured output. ``title`` is required by…, LegalBenchAgent, Any (+7 more)

### Community 29 - ".classify_document"
Cohesion: 0.12
Nodes (19): classify_image(), clean_prediction(), extract_confidence(), extract_reasoning(), extract_runner_up(), Path, Classify a document image using a vision model through OpenRouter API. Args:…, Extract valid class name from LLM response using word boundary matching. (+11 more)

### Community 30 - "CompletenessJudge"
Cohesion: 0.15
Nodes (8): CompletenessJudge, BaseAgent, Render the task specification (taxonomy doc classes) for the judge., Judge whether the sorter's assigned class matches the taxonomy task…, Judge whether the extracted field values are factually accurate (no…, TestClassificationJudge, TestCompletenessJudge, TestExtractionCorrectnessJudge

### Community 31 - "test_vision.py"
Cohesion: 0.13
Nodes (19): Path, Render pages of a PDF to a list of PNG image data-URIs. `cap` is the page…, Encode a single image file as a data-URI for direct vision input. Image inputs…, Render an input document to a list of page-image data-URIs (PDFs only; real…, render_document_pages(), render_image(), render_pdf_pages(), page_images() (+11 more)

### Community 32 - "tracing.py"
Cohesion: 0.15
Nodes (18): flush_langfuse(), get_langfuse_client(), get_trace_id(), install_on_dropped(), instrument_openai_client(), observation(), pipeline_trace(), Langfuse tracing backend (langfuse >= 4.x). Two layers of tracing: 1. **LLM… (+10 more)

### Community 33 - "sync_evaluators.py"
Cohesion: 0.16
Nodes (21): _build_evaluator_request(), _build_output_definition(), _build_rule_request(), _client(), _current_evaluator_prompt(), _ensure_llm_connection(), _existing_rule_ids(), main() (+13 more)

### Community 34 - "TestVllmProviderSeam"
Cohesion: 0.14
Nodes (8): _install_modal_stub(), _load_app_module(), KANBAN-064 — Modal+vLLM offline serving capability tests. Network-free by…, The runtime half: DEFAULT_PROVIDER=vllm must reach get_llm untouched., The capability must not move the default serving path., Minimal stand-in for the `modal` module surface used by the app., TestModalVllmApp, TestVllmProviderSeam

### Community 35 - "experiment_log.py"
Cohesion: 0.19
Nodes (16): CompletedProcess, append_record(), default_log_path(), default_sibling_root(), _inside(), Path, Experiment-log integration for LegalBench runs. On run completion the runner…, Append one JSON line (stamped with an ISO timestamp if absent). (+8 more)

### Community 36 - "load_config"
Cohesion: 0.18
Nodes (17): Comma-joined model names actually used by this run (best-effort)., _resolved_models(), agent_uses_vision(), _any_specialist_uses_vision(), is_vision_capable(), max_pages(), pipeline_uses_vision(), Vision-capable model helpers for the mailroom pipeline. Some input agents (e.g.… (+9 more)

### Community 37 - "sorter_agent.py"
Cohesion: 0.16
Nodes (8): normalize_subtype(), BaseAgent, Coerce a raw sorter subtype output (or a CUAD folder name) to a canonical…, Classifies legal documents into mailroom document types. Two classification…, Classify a document and return (doc_type, contract_subtype, confidence,…, Classify and return the raw structured dict (used by eval loops). With…, Re-evaluate a document after low-confidence classification. Args: doc_text: The…, SorterAgent

### Community 38 - "test_observability.py"
Cohesion: 0.11
Nodes (6): _clear_observability_env(), fixture, Isolate backend selection per test., TestFlushHealth, TestInstrumentation, TestProviderResolution

### Community 39 - "env.py"
Cohesion: 0.15
Nodes (15): list_stale_processing_files(), Files stranded in processing/<worker_id>/ by a crashed process (L-1/A-18). A…, Move a stale processing claim back to the inbox (L-1/A-18). The watcher's…, requeue_stale_processing(), default_environment(), load_env(), Path, Load environment variables from a .env file. The app reads its configuration… (+7 more)

### Community 40 - "TestAuth"
Cohesion: 0.11
Nodes (6): client(), fixture, API security tests (audit L-2/L-18): auth, upload guards, doc_id validation.…, TestAuth, TestDocIdValidation, TestUploadGuards

### Community 41 - "runner.py"
Cohesion: 0.23
Nodes (16): ArgumentParser, build_parser(), main(), LegalBench suite CLI. Run a LegalBench task, trace it to Langfuse, and log the…, log_run(), _model_name(), print_summary(), Any (+8 more)

### Community 42 - "run_quality_judges.py"
Cohesion: 0.18
Nodes (16): flush_phoenix(), Force-export buffered spans without disabling the provider., create_trace_score(), Attach a score to a trace by id (offline/pilot scoring — no active tracing…, flush(), Flush queued events for the active backend. Safe to call anytime. Tracks flush…, _dim_summary(), _ingest() (+8 more)

### Community 43 - "PipelineStage"
Cohesion: 0.17
Nodes (15): Enum, _build_handoff_context(), classify_node(), _detect_conflict(), extract_node(), Chained-eval handoff: prefix the sorter's classification (doc class + contract…, Deterministically compare a fresh extraction against archived records of the…, retry_classify_node() (+7 more)

### Community 44 - "resume_from_review"
Cohesion: 0.13
Nodes (18): _extract_text_from_docx(), _extract_text_from_image(), _extract_text_from_pdf(), Path, Render an input document to page-image data-URIs for vision-capable agents…, Extract text from .docx (paragraphs + tables) via python-docx. Previously .docx…, Resume a human-approved review document with a FRESH extraction. Stateless…, _read_file_text() (+10 more)

### Community 45 - "get-generation.ts"
Cohesion: 0.19
Nodes (12): apiKey, args, apiKey, args, json, json, fetchApi(), fetchGeneration() (+4 more)

### Community 46 - "DocumentManifest"
Cohesion: 0.16
Nodes (11): entry_route(), Entry router: a review-resume re-invocation starts at fresh extraction…, DocumentManifest, BaseModel, phased_client(), fixture, P0.3 — Review resume-lite: an approved review re-invokes the graph starting at…, Mock LLM clients with a scripted sequence: the LangChain sorter returns low… (+3 more)

### Community 47 - "test_legalbench.py"
Cohesion: 0.17
Nodes (12): family_classification_prompt_v1(), get_prompt(), Versioned LegalBench task prompts. Prompt version = experiment identity in the…, Fill the 25-family list into the multiclass prompt (called per run so the…, Resolve a prompt version to its system-prompt text., contracts_dir(), cuad_file(), _cuad_payload() (+4 more)

### Community 48 - "SorterAgent"
Cohesion: 0.22
Nodes (6): _LangChainSorterAgent, Mailroom-configured sorter. - Model/budget defaults come from ``taxonomy.yaml``…, Classify a document, optionally with page images attached. Returns ``(doc_type,…, SorterAgent, get_all_doc_types(), TestSorterAgent

### Community 49 - "langfuse_tracing.py"
Cohesion: 0.17
Nodes (14): attach_run_scores(), ensure_score_configs_if_enabled(), _environment(), legalbench_trace(), Any, question_observation(), Langfuse tracing for LegalBench runs. One trace per run (deterministic seed =…, Open the per-run Langfuse trace (no-op when tracing is disabled). (+6 more)

### Community 50 - "get_field_types"
Cohesion: 0.17
Nodes (5): get_field_types(), Field→scoring-type mapping, auto-loading mailroom's taxonomy. The package…, TestFieldTypesFromConfig, TestLangfuseWiring, TestScoreExtraction

### Community 52 - "calibrate_field_scoring.py"
Cohesion: 0.20
Nodes (14): main(), _perturb_date(), _perturb_entity_list(), _perturb_free_text(), _perturb_money(), _perturb_name(), _predictions_for(), Random (+6 more)

### Community 53 - "FakeEmbedding"
Cohesion: 0.14
Nodes (4): FakeEmbedding, Deterministic fake embedding similarity for rescue tests., TestFreeTextField, TestNameField

### Community 54 - "prompt_templates"
Cohesion: 0.20
Nodes (9): parametrize, _langchain_prompt(), prompt_templates(), Local template for the vendored LangChain agents' versioned prompts…, agent_name -> local prompt template (with `{{var}}` placeholders). Single…, _normalize(), Guard the evidence-based confidence calibration rule in agent prompts. The…, test_confidence_calibration_rule_present() (+1 more)

### Community 55 - "setup_logging"
Cohesion: 0.26
Nodes (5): RotatingFileHandler, Structlog processor that emits the rendered event dict to a rotating stdlib…, _RotatingFileSink, setup_logging(), TestLoggingSetup

### Community 56 - "BaseAgent"
Cohesion: 0.23
Nodes (5): BaseAgent, ABC, Build the user-message content for a document input. Vision-capable models get…, Truncate document text to the agent's configured input budget, marking the…, True when this agent's model accepts image input and (optionally) page images…

### Community 57 - "scoring.py"
Cohesion: 0.25
Nodes (13): equivalent_subtypes(), Return True when two subtype keys are the same family or members of the same…, _binary_f1(), _ece(), _mean(), Any, Deterministic scoring for LegalBench runs — every number computed locally. No…, Expected calibration error over confidence/outcome pairs. (+5 more)

### Community 58 - "build_structured_schema"
Cohesion: 0.26
Nodes (5): build_structured_schema(), BossAgent, BaseAgent, TestBossAgent, TestBossBudgets

### Community 59 - "MockLegalBenchModel"
Cohesion: 0.22
Nodes (6): _hash(), MockLegalBenchModel, Any, Deterministic mock model for LegalBench runs (no network, no OpenAI). Answers…, Implements the LegalBenchAgent interface deterministically., TestMockModel

### Community 60 - "field_is_ambiguous"
Cohesion: 0.23
Nodes (6): field_is_ambiguous(), get_type_bands(), Per-field-type ambiguous-band overrides from ``field_scoring.type_bands``.…, Is this field score in the (possibly type-specific) ambiguous band? Band check…, Calibrated per-field-type ambiguous bands (issue #4 calibration step)., TestTypeBands

### Community 61 - "scores.py"
Cohesion: 0.23
Nodes (12): _client(), compute_run_metrics(), emit_pipeline_scores(), is_enabled(), Quality scores for document runs. Backend-agnostic helpers to attach evaluation…, Attach a score to the currently active trace (inside a pipeline_trace block).…, Core per-run metrics, computed for EVERY finished run regardless of the tracing…, Attach self-evident production scores for a finished run (no ground truth… (+4 more)

### Community 62 - "get_extraction_schema"
Cohesion: 0.32
Nodes (10): ComplianceFilingExtraction, ContractExtraction, CorporateRecordExtraction, CorrespondenceExtraction, CourtOpinionExtraction, DueDiligenceExtraction, get_extraction_schema(), BaseModel (+2 more)

### Community 63 - "test_field_scoring.py"
Cohesion: 0.15
Nodes (6): _no_real_embedding(), fixture, Deterministic field-type-aware extraction scoring (issues #4/#5). Covers the…, Never load sentence-transformers in tests (no model download)., TestDispatch, TestIdField

### Community 64 - "modal_vllm.py"
Cohesion: 0.20
Nodes (11): build_vllm_command(), main(), KANBAN-064 — Modal-deployed vLLM server for llm-mailroom (offline capability).…, `modal run modal_vllm.py` prints deployment guidance without serving., Environment for the vLLM process inside the container., Assemble the `vllm serve` argv. Kept pure for unit testing., serve(), _server_env() (+3 more)

### Community 65 - "CorporateRecordsSpecialist"
Cohesion: 0.24
Nodes (5): CorporateRecordsSpecialist, BaseAgent, The `json_object` response format requires the literal token `json` in the…, TestStructuredCallJsonInvariant, TestCorporateRecordsSpecialist

### Community 66 - "after_judge"
Cohesion: 0.24
Nodes (5): after_arbiter(), after_judge(), KANBAN-063 (Lane B): judge outcome router. ``complete`` (or a skipped/gated-out…, KANBAN-063 (Lane B): arbiter outcome router, with the retry bound.…, TestLaneBRouting

### Community 67 - "metrics.py"
Cohesion: 0.24
Nodes (11): _date_pair_days(), extraction_diagnostics(), _mean(), _median(), parse_duration_days(), _r2(), Run-level diagnostic metrics for extraction scoring. Ported from ``llm-entity-…, Coefficient of determination ``1 - SS_res/SS_tot`` over (predicted, expected)… (+3 more)

### Community 68 - "test_real_sample_gate.py"
Cohesion: 0.29
Nodes (11): is_real_sample(), True when a manifest row is a real committed legal document. Real samples are…, filter_real_samples(), Restrict a pilot manifest to samples a given mode may process. Real (non-mock)…, _env_no_dotenv(), Real (non-mock) pilot runs must only process actual committed legal documents —…, _rows(), test_filter_real_samples_blocks_synthetic_for_real() (+3 more)

### Community 69 - "tasks.py"
Cohesion: 0.20
Nodes (5): LegalBench evaluation suite — a second lens on model quality. The suite runs…, _extract_family(), _family_labels(), LegalBenchTask, LegalBench task registry. Two task families, per the LegalBench taxonomy: -…

### Community 70 - "bootstrap.py"
Cohesion: 0.29
Nodes (10): bootstrap_ci(), _clean(), delta_significance(), Any, Random, Bootstrap confidence intervals and small-sample delta testing. Ported verbatim…, Coerce a per-document score list to floats, dropping None/non-numeric., Percentile-bootstrap 95% CI over per-document scores. Returns ``{"lo", "hi",… (+2 more)

### Community 71 - "fetch_external_samples.py"
Cohesion: 0.33
Nodes (10): _caption_from_text(), _download(), fetch_atticus(), fetch_legalbench(), fetch_pileoflaw(), main(), Path, Yield (record, url) for courtlistener opinions, streaming + aborting early per… (+2 more)

### Community 72 - "prepare_samples"
Cohesion: 0.33
Nodes (9): _escape(), generate_pdf_from_text(), _load_manifest(), prepare_samples(), Path, Materialize every manifest row under data/samples/. Returns its path., test_generated_pdf_transcribes_short_text(), test_prepare_samples_materializes_manifest() (+1 more)

### Community 73 - "Path"
Cohesion: 0.29
Nodes (3): Path, TestDataLoaders, TestRunner

### Community 74 - "PDFTranscriber"
Cohesion: 0.33
Nodes (5): PDFTranscriber, BaseAgent, Path, Heuristic: if a PDF yields a dense, clean text extraction, the LLM reformat…, transcribe_pdf()

### Community 75 - "braintrust_setup.py"
Cohesion: 0.24
Nodes (9): configure(), flush_braintrust(), instrument_openai_client(), is_configured(), Braintrust tracing backend — alternative to Langfuse. Switch to it with…, Initialize Braintrust (idempotent). Returns True when active., Wrap `client` with Braintrust instrumentation, or return it unchanged., _apply_taxonomy_settings() (+1 more)

### Community 76 - "cutover.py"
Cohesion: 0.40
Nodes (9): cutover_agent(), cutover_all(), list_agents(), list_local_models(), load_config(), main(), recommend_cutover_order(), save_config() (+1 more)

### Community 77 - "test_samples_manifest.py"
Cohesion: 0.36
Nodes (8): _rows(), test_court_opinion_samples_map_to_court_opinion_class(), test_manifest_expected_classes_are_valid_taxonomy(), test_manifest_expected_stages_valid(), test_manifest_has_rows_and_unique_ids(), test_manifest_has_schema_compatible_field_ground_truth(), test_manifest_has_six_samples_per_external_source(), test_manifest_referenced_sources_exist()

### Community 78 - "ensure_score_configs"
Cohesion: 0.25
Nodes (8): ExtractionScoreResult, ensure_field_score_configs(), Wire deterministic field scoring into Langfuse (GitHub issue #5). The scoring…, Idempotent: register the field-scoring configs in the Langfuse project. The…, Score one extraction deterministically and push every score to Langfuse,…, score_and_log_extraction(), ensure_score_configs(), Create any missing score configs. Idempotent and process-cached — safe to call…

### Community 79 - "ContractsSpecialist"
Cohesion: 0.33
Nodes (4): _LangChainContractsSpecialist, ContractsSpecialist, Mailroom-configured contracts specialist. - Model/budget defaults come from…, TestContractsSpecialist

### Community 80 - "CourtOpinionsSpecialist"
Cohesion: 0.28
Nodes (4): CourtOpinionsSpecialist, BaseAgent, _extract_court_opinions(), TestCourtOpinionsSpecialist

### Community 81 - "load_env"
Cohesion: 0.28
Nodes (8): bool_env(), get_env(), load_env(), Load ``braintrust.env`` then ``.env`` into the environment (idempotent).…, Validate that all given environment variables are set and non-empty. Returns…, Get an environment variable with a default fallback., Get a boolean environment variable., require_env()

### Community 82 - "sync_models.py"
Cohesion: 0.39
Nodes (8): _client(), _cost_models(), _existing_by_name(), main(), _match_pattern(), _prices_match(), Map model_name -> registry Model for every user-defined entry. Paginates: the…, sync_models()

### Community 83 - "test_graphify_skill.py"
Cohesion: 0.36
Nodes (8): Path, KANBAN-065: vendored Graphify skill integrity checks. The…, _read(), test_all_reference_sidecars_present(), test_provenance_names_upstream_source(), test_sibling_entity_copy_is_identical(), test_skill_documents_core_workflows(), test_skill_md_exists_with_valid_frontmatter()

### Community 84 - "traced_node"
Cohesion: 0.25
Nodes (3): Decorator that wraps a graph node fn in a named observation span. Applies…, traced_node(), TestLangfuseClient

### Community 85 - "sync_dataset.py"
Cohesion: 0.50
Nodes (7): _client(), _doc_text(), _ensure_dataset(), main(), Path, sync_items(), _validate_ground_truth()

### Community 87 - "openrouter-analytics/scripts/package.json"
Cohesion: 0.29
Nodes (6): devDependencies, tsx, tsx, name, private, type

### Community 88 - "suggest-queries.ts"
Cohesion: 0.33
Nodes (6): now, resolve(), resolved, TEMPLATES, thirtyDaysAgo, todayStart

### Community 89 - "openrouter-generations/scripts/package.json"
Cohesion: 0.29
Nodes (6): devDependencies, tsx, tsx, name, private, type

### Community 90 - "openrouter-models/scripts/package.json"
Cohesion: 0.29
Nodes (6): devDependencies, tsx, tsx, name, private, type

### Community 91 - "config.py"
Cohesion: 0.33
Nodes (4): Contracts specialist — LangChain version vendored from llm-entity-extraction.…, Sorter agent — LangChain version vendored from llm-entity-extraction. Re-…, get_doc_class(), get_extraction_schema_name()

### Community 92 - "_record_langchain_response"
Cohesion: 0.29
Nodes (7): _check_cost_watchdog(), _fetch_openrouter_prices(), _price_for(), Warn at $0.15, abort the run at $0.20 (cumulative across all samples)., Mirror _wrap_client's usage/cost accounting for a LangChain response., Fetch live OpenRouter pricing (per-token), normalized to $/M tokens. The…, _record_langchain_response()

### Community 94 - "ArbiterAgent"
Cohesion: 0.33
Nodes (4): ArbiterAgent, BaseAgent, Judgment arbitration on failed judge verdicts., Decide the outcome for a judge-rejected extraction. Returns ``{decision,…

### Community 95 - "build_record"
Cohesion: 0.40
Nodes (5): build_record(), git_snapshot(), Any, llm-mailroom commit at run time (best-effort)., One experiment-log record in the upstream schema (see the JSONL header of…

### Community 98 - "sync_prompts.py"
Cohesion: 0.70
Nodes (4): _client(), _current_production(), main(), sync_one()

### Community 99 - "_ParseErrorLangChainLLM"
Cohesion: 0.50
Nodes (3): _ParseErrorLangChainLLM, Fake whose structured runner reports a parsing_error (the vendored…, _Runner

### Community 114 - "_SpecialistBase"
Cohesion: 0.13
Nodes (14): get_specialist(), _norm(), normalize_extraction(), BaseAgent, Shared extract() implementation over a per-class schema., Extract a long document in overlapping chunks and merge the passes. Documents…, Normalize clause text for dedupe: whitespace-collapse + casefold. The chunk…, Sum per-chunk usage dicts (prompt/completion/total tokens, cost). (+6 more)

## Knowledge Gaps
- **77 isolated node(s):** `MetaResponse`, `QueryResponse`, `Filter`, `ScoredModel`, `GenerationResponse` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BaseAgent` connect `BaseAgent` to `conftest.py`, `CorporateRecordsSpecialist`, `TestVendoredRetryContract`, `sorter_agent.py`, `specialist_agents.py`, `toolkit.py`, `SorterAgent`, `_SpecialistBase`, `run_pilot.py`, `base_agent.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `load_config()` connect `load_config` to `test_run_limits.py`, `build_graph.py`, `toolkit.py`, `main.py`, `base.py`, `bins.py`, `ops_monitor.py`, `test_specialists.py`, `get_confidence_thresholds`, `get_managed_prompt`, `base_agent.py`, `CompletenessJudge`, `sync_evaluators.py`, `SorterAgent`, `get_field_types`, `field_is_ambiguous`, `PDFTranscriber`, `braintrust_setup.py`, `test_samples_manifest.py`, `sync_models.py`, `config.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `inbox_dir()` connect `inbox_dir` to `conftest.py`, `build_graph.py`, `env.py`, `main.py`, `bins.py`, `build_graph`, `run_pilot.py`, `watcher.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BaseAgent` (e.g. with `SorterAgent` and `get_specialist()`) actually correct?**
  _`BaseAgent` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `build_graph()` (e.g. with `arbiter_node()` and `archive_node()`) actually correct?**
  _`build_graph()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `BaseAgent` (e.g. with `ArbiterAgent` and `BossAgent`) actually correct?**
  _`BaseAgent` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `MetaResponse`, `QueryResponse`, `Filter` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._
"""Mirror of the llm-mailroom pipeline topology.

This mirrors graph/build_graph.py + graph/routing.py + config/taxonomy.yaml of
the llm-mailroom repo so traces can be interpreted without importing that repo.
If MAILROOM_TAXONOMY points at the live taxonomy.yaml, thresholds/doc classes
are read from there instead (the topology above is data-driven there too).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from .models import Phase, Stage

SPAN_STAGE_MAP: dict[str, Stage] = {
    "ingest-document": Stage.INGEST,
    "normalize-intake": Stage.INGEST,
    "transcribe-pdf": Stage.INGEST,
    "extract-image-text": Stage.INGEST,
    "classify-document": Stage.CLASSIFY,
    "judge-verify": Stage.JUDGE_VERIFY,
    "arbitrate-verdict": Stage.ARBITER,
    "extract-fields": Stage.EXTRACT,
    "route-for-review": Stage.HUMAN_REVIEW,
    "adjudicate-conflict": Stage.BOSS,
    "compile-report": Stage.COMPILE_REPORT,
    "write-catalog": Stage.CATALOG,
    "archive-document": Stage.ARCHIVE,
}

# Langfuse observation types (llm-mailroom observability/tracing.py
# NODE_OBSERVATION_TYPES). The data-model docs require the most specific
# type: chain = one document run; agent = specialist orchestration;
# evaluator = judge gate; retriever = document reads; generation = LLM
# result / LegalBench answer; span = remaining units of work.
NODE_OBSERVATION_TYPES: dict[str, str] = {
    "document-pipeline": "chain",
    "ingest-document": "span",
    "normalize-intake": "span",
    "extract-image-text": "retriever",
    "transcribe-pdf": "retriever",
    "classify-document": "agent",
    "extract-fields": "agent",
    "judge-verify": "evaluator",
    "arbitrate-verdict": "agent",
    "route-for-review": "span",
    "adjudicate-conflict": "agent",
    "compile-report": "agent",
    "write-catalog": "span",
    "archive-document": "span",
    "pipeline-result": "generation",
    "answer-question": "generation",
}

# Graph node names (underscored) that can appear as observation names
# when a trace is recorded from LangGraph rather than traced_node().
_NODE_TYPE_ALIASES: dict[str, str] = {
    "classify": "agent",
    "retry_classify": "agent",
    "review_classify": "agent",
    "extract": "agent",
    "retry_extract": "agent",
    "judge_verify": "evaluator",
}


def observation_type_for(name: str, default: str = "span") -> str:
    """Most-specific Langfuse observation type for a verb-first span name."""
    key = (name or "").strip()
    if key in NODE_OBSERVATION_TYPES:
        return NODE_OBSERVATION_TYPES[key]
    lower = key.lower()
    if lower in NODE_OBSERVATION_TYPES:
        return NODE_OBSERVATION_TYPES[lower]
    if lower in _NODE_TYPE_ALIASES:
        return _NODE_TYPE_ALIASES[lower]
    if lower.startswith("answer-question"):
        return "generation"
    return default

STAGE_PHASE: dict[Stage, Phase] = {
    Stage.INBOX: Phase.INTAKE_SORT,
    Stage.INGEST: Phase.INTAKE_SORT,
    Stage.CLASSIFY: Phase.INTAKE_SORT,
    Stage.RETRY_CLASSIFY: Phase.INTAKE_SORT,
    Stage.EXTRACT: Phase.EXTRACTION_ADJUDICATION,
    Stage.RETRY_EXTRACT: Phase.EXTRACTION_ADJUDICATION,
    Stage.JUDGE_VERIFY: Phase.EXTRACTION_ADJUDICATION,
    Stage.ARBITER: Phase.EXTRACTION_ADJUDICATION,
    Stage.BOSS: Phase.EXTRACTION_ADJUDICATION,
    Stage.COMPILE_REPORT: Phase.REPORTING_ARCHIVE,
    Stage.CATALOG: Phase.REPORTING_ARCHIVE,
    Stage.ARCHIVE: Phase.REPORTING_ARCHIVE,
    Stage.ARCHIVED: Phase.TERMINAL,
    Stage.FAILED: Phase.TERMINAL,
    Stage.HUMAN_REVIEW: Phase.REVIEW,
    Stage.UNKNOWN: Phase.INTAKE_SORT,
}

# Node traversal order used to order spans into a routing path (mirrors the
# add_node wiring order in llm-mailroom graph/build_graph.py).
NODE_ORDER: list[Stage] = [
    Stage.INGEST,
    Stage.CLASSIFY,
    Stage.RETRY_CLASSIFY,
    Stage.EXTRACT,
    Stage.RETRY_EXTRACT,
    Stage.JUDGE_VERIFY,
    Stage.ARBITER,
    Stage.BOSS,
    Stage.HUMAN_REVIEW,
    Stage.COMPILE_REPORT,
    Stage.CATALOG,
    Stage.ARCHIVE,
]

# Agent display roster: key -> (label, role). Mirrors src/agents/ of
# llm-mailroom (+ langchain_agents/sorter_agent.py for sorter/sorter_reviewer).
# Retired specialists (court opinions / due diligence) stay off this roster;
# the sorter emits `unknown` for those classes.
AGENTS: dict[str, dict[str, str]] = {
    "sorter": {"label": "Sorter", "role": "classify"},
    "intake": {"label": "Intake", "role": "prepare"},
    "sorter_reviewer": {"label": "Sorter Reviewer", "role": "review-classify"},
    "contracts_specialist": {"label": "Contracts", "role": "extract"},
    "corporate_records_specialist": {"label": "Corporate", "role": "extract"},
    "correspondence_specialist": {"label": "Correspondence", "role": "extract"},
    "compliance_specialist": {"label": "Compliance", "role": "extract"},
    "insurance_claims_specialist": {"label": "Insurance Claims", "role": "extract"},
    "arbiter": {"label": "Arbiter", "role": "adjudicate"},
    "boss": {"label": "Boss", "role": "adjudicate"},
    "reporter": {"label": "Reporter", "role": "report"},
    "judge": {"label": "Judge", "role": "evaluate"},
    "pdf_transcriber": {"label": "Transcriber", "role": "ingest"},
    "image_extractor": {"label": "Image Extractor", "role": "ingest"},
}

# Live taxonomy classes that dispatch to a specialist (llm-mailroom v0.5+ /
# llm-dojo-scoring LIVE_DOC_TYPES). `merger_agreement` is an HF/sorter alias
# that extracts through contracts; `unknown` is a routing token, not a class.
LIVE_DOC_TYPES: tuple[str, ...] = (
    "contract",
    "corporate_record",
    "correspondence",
    "compliance_filing",
    "insurance_claim",
)
RETIRED_DOC_TYPES: tuple[str, ...] = ("court_opinion", "due_diligence")
UNKNOWN_DOC_TYPE = "unknown"
EXTRACT_CLASS_ALIASES: dict[str, str] = {"merger_agreement": "contract"}

DOC_CLASSES: dict[str, str] = {
    "contract": "Contract / Agreement",
    "corporate_record": "Corporate Record",
    "correspondence": "Correspondence",
    "compliance_filing": "Compliance Filing",
    "insurance_claim": "Insurance Claim",
    "merger_agreement": "Merger Agreement",  # display/HF alias, not a taxonomy row
    "unknown": "Unknown",
}

DEFAULT_DOC_CLASSES: dict[str, str] = dict(DOC_CLASSES)

SPECIALIST_BY_DOC_CLASS: dict[str, str] = {
    "contract": "contracts_specialist",
    "merger_agreement": "contracts_specialist",
    "corporate_record": "corporate_records_specialist",
    "correspondence": "correspondence_specialist",
    "compliance_filing": "compliance_specialist",
    "insurance_claim": "insurance_claims_specialist",
}

# Hub subclass catalogs (llm-dojo-scoring mailroom.HUB_SUBCLASS_INVENTORIES
# + CUAD contract_subtype keys + MAUD consideration types).
CONTRACT_SUBTYPE_KEYS: tuple[str, ...] = (
    "affiliate", "agency", "collaboration", "co_branding", "consulting",
    "development", "distributor", "endorsement", "franchise", "hosting",
    "ip", "joint_venture", "license", "maintenance", "manufacturing",
    "marketing", "non_compete_no_solicit", "outsourcing", "promotion",
    "reseller", "service", "sponsorship", "strategic_alliance", "supply",
    "transportation",
)
DOC_SUBCLASS_BY_CLASS: dict[str, tuple[str, ...]] = {
    "contract": CONTRACT_SUBTYPE_KEYS,
    "merger_agreement": (
        "all_cash", "all_stock", "mixed_cash_stock",
        "mixed_cash_stock_election", "other",
    ),
    "corporate_record": (
        "articles_of_incorporation", "bylaws", "powers_of_attorney",
        "rights_instrument", "other",
    ),
    "correspondence": (
        "email", "letter", "memo", "notice", "demand", "attorney_demand",
        "press_release", "meeting_request",
    ),
    "insurance_claim": ("pde", "inpatient", "outpatient", "carrier"),
    "compliance_filing": (
        "10-K", "10-Q", "8-K", "S-1", "DEF 14A", "13D", "13G",
        "Form 4", "20-F", "6-K", "other",
    ),
}

# Langfuse Cloud rejects score *config* names over 35 characters.
LANGFUSE_SCORE_NAME_ALIASES: dict[str, str] = {
    "extraction_overall_verified_precision": "extraction_verified_precision",
}
_CANONICAL_SCORE_NAMES: dict[str, str] = {
    alias: canonical for canonical, alias in LANGFUSE_SCORE_NAME_ALIASES.items()
}

# Dedicated specialist-suite extras (llm-mailroom suite_scoring.py / dojo 0.9.0).
SUITE_EXTRA_SCORES: tuple[str, ...] = (
    "content_topic_accuracy",
    "content_topic_f1_macro",
    "sentiment_accuracy",
    "sentiment_f1_macro",
    "maud_question_accuracy",
    "maud_question_macro_accuracy",
    "maud_clause_presence",
    "maud_valid_class_rate",
    "maud_category_accuracy",
)
SUITE_EXTRA_SCORE_SET = frozenset(SUITE_EXTRA_SCORES)

GROUND_TRUTH_KEYS: tuple[str, ...] = (
    "expected_hf_class",
    "expected_doc_class",
    "expected_subclass",
    "expected",
)


def resolve_extract_class(doc_type: Optional[str]) -> Optional[str]:
    """Live taxonomy class used for extraction, or None if parked."""
    if not doc_type:
        return None
    key = str(doc_type).strip().lower()
    if key == UNKNOWN_DOC_TYPE or key in RETIRED_DOC_TYPES:
        return None
    aliased = EXTRACT_CLASS_ALIASES.get(key, key)
    if aliased in LIVE_DOC_TYPES:
        return aliased
    return None


def langfuse_score_name(name: str) -> str:
    return LANGFUSE_SCORE_NAME_ALIASES.get(name, name)


def canonical_score_name(name: str) -> str:
    return _CANONICAL_SCORE_NAMES.get(name, name)


@dataclass
class PipelineSchema:
    """Loaded once per process; configurable thresholds from taxonomy.yaml."""

    confidence_high: float = 0.95
    confidence_low: float = 0.70
    retry_max: int = 1
    conflict_threshold: float = 0.3
    judge_band_high: float = 0.85   # routing.py judge_gate default
    doc_classes: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_DOC_CLASSES))

    @classmethod
    def load(cls, taxonomy_path: Optional[str] = None) -> "PipelineSchema":
        schema = cls()
        path = taxonomy_path or os.environ.get("MAILROOM_TAXONOMY")
        if not path or not os.path.exists(path):
            return schema
        try:
            import yaml  # type: ignore
        except ImportError:
            return schema
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            return schema
        conf = cfg.get("confidence", {}) or {}
        schema.confidence_high = float(conf.get("high", schema.confidence_high))
        schema.confidence_low = float(conf.get("low", schema.confidence_low))
        schema.retry_max = int(conf.get("retry_max", schema.retry_max))
        schema.conflict_threshold = float(conf.get("conflict_threshold", schema.conflict_threshold))
        schema.judge_band_high = float(conf.get("judge_band_high", schema.judge_band_high))
        classes = {}
        for dc in cfg.get("doc_classes", []) or []:
            if isinstance(dc, dict) and dc.get("key"):
                classes[dc["key"]] = dc.get("label", dc["key"])
        if classes:
            schema.doc_classes = classes
        return schema

    def specialist_for(self, doc_type: str) -> Optional[str]:
        if not doc_type:
            return None
        key = EXTRACT_CLASS_ALIASES.get(doc_type, doc_type)
        return SPECIALIST_BY_DOC_CLASS.get(key) or SPECIALIST_BY_DOC_CLASS.get(doc_type)

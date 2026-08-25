from __future__ import annotations

from datetime import datetime, timedelta

from mailroom_ui.models import Phase, Stage
from mailroom_ui.trace_interpreter import (
    RUN_GAP_S,
    _latest_cluster,
    build_routing_path,
    derive_stage,
    interpret_trace,
)
from tests.fake_langfuse import Obj, FakeClient, make_trace, make_trace_v4


def _run(trace: dict):
    return interpret_trace(
        trace,
        trace.get("observations", []),
        trace.get("scores", []),
    )


def test_v4_camelcase_observations():
    trace = make_trace_v4("t-v4")
    run = _run(trace)
    assert run.stage == Stage.ARCHIVED
    assert run.doc_type == "contract"
    assert run.matter_id == "MATTER-V4"
    assert run.classification_confidence == 0.97
    assert run.extraction_confidence == 0.88
    assert len(run.spans) == 4
    assert [s.name for s in run.spans][-1] == "archive-document"
    gen = run.generations[0]
    assert gen.model == "deepseek/deepseek-v4-flash"
    assert gen.usage_total_tokens == 1200
    assert gen.usage_input_tokens == 1000
    assert gen.usage_output_tokens == 200
    assert gen.cost_usd == 0.00015
    assert run.total_tokens == 1200
    assert run.cost_usd == 0.00015
    assert run.session_id == "MATTER-V4"


def test_archived_run_full():
    trace = make_trace("t-archived")
    run = _run(trace)
    assert run.trace_id == "t-archived"
    assert run.stage == Stage.ARCHIVED
    assert run.phase == Phase.TERMINAL
    assert run.doc_type == "contract"
    assert run.matter_id == "MATTER-001"
    assert run.session_id == "MATTER-001"
    assert run.classification_confidence == 0.98
    assert run.extraction_confidence == 0.91
    assert run.verdict == "CORRECT"
    assert run.quality == 0.9
    assert run.llm_call_count == 2
    assert run.total_tokens == 4600
    assert run.cost_usd == 0.00055
    assert len(run.spans) == 6
    assert run.routing_path == [
        "ingest",
        "classify",
        "extract",
        "report",
        "catalog",
        "archive",
    ]
    assert run.needs_human is False


def test_review_stage():
    trace = make_trace(
        "t-review",
        stage="review",
        span_names=["ingest-document", "classify-document", "route-for-review"],
        verdict=None,
        quality=None,
    )
    run = _run(trace)
    assert run.stage == Stage.HUMAN_REVIEW
    assert run.phase == Phase.REVIEW
    assert run.needs_human is True


def test_failed_stage():
    trace = make_trace("t-failed", stage="failed", verdict=None)
    run = _run(trace)
    assert run.stage == Stage.FAILED
    assert run.phase == Phase.TERMINAL


def test_retry_detection():
    trace = make_trace(
        "t-retry",
        span_names=[
            "ingest-document",
            "classify-document",
            "classify-document",
            "extract-fields",
            "extract-fields",
            "compile-report",
        ],
    )
    run = _run(trace)
    assert "retry_classify" in run.routing_path
    assert "retry_extract" in run.routing_path
    assert run.retried is True


def test_in_flight_derives_stage_from_last_span():
    trace = make_trace(
        "t-inflight",
        stage="processing",
        span_names=["ingest-document", "classify-document"],
        verdict=None,
    )
    run = _run(trace)
    assert run.stage in (Stage.CLASSIFY, Stage.INGEST)
    assert run.phase == Phase.INTAKE_SORT


def test_derive_stage_output_wins():
    trace = make_trace("t-x", stage="review")
    run = _run(trace)
    assert derive_stage(trace["output"], run.spans) == Stage.HUMAN_REVIEW


def test_light_interpretation_from_list_response():
    trace = make_trace("t-light", stage="archived")
    run = interpret_trace(trace)  # observations/scores embedded in trace dict
    assert run.stage == Stage.ARCHIVED
    assert run.spans and run.generations


def test_light_interpretation_without_embedded_observations():
    trace = make_trace("t-bare", stage="archived")
    trace.pop("observations")
    trace.pop("scores")
    run = interpret_trace(trace)
    assert run.stage == Stage.ARCHIVED
    assert run.spans == []
    assert run.generations == []
    assert run.total_tokens == 0
    assert run.cost_usd == 0.0


def test_latest_cluster_keeps_only_most_recent_run():
    base = datetime(2026, 1, 1, 12, 0, 0)
    early = [Obj(id="a", start_time=base)]
    late = [Obj(id="b", start_time=base + timedelta(seconds=RUN_GAP_S + 5))]
    assert [o.id for o in _latest_cluster([*early, *late], get_start=lambda o: o.start_time)] == ["b"]


def test_latest_cluster_keeps_single_run_untouched():
    base = datetime(2026, 1, 1, 12, 0, 0)
    items = [Obj(id=f"o{i}", start_time=base + timedelta(seconds=5 * i)) for i in range(3)]
    assert len(_latest_cluster(items, get_start=lambda o: o.start_time)) == 3


def test_multi_run_trace_interprets_latest_run_only():
    base = datetime(2026, 1, 1, 12, 0, 0)
    rerun_obs = [
        Obj(
            id="rerun-gen",
            type="GENERATION",
            name="classify-document",
            model="qwen/qwen3.7-flash",
            start_time=base + timedelta(seconds=RUN_GAP_S + 60),
            end_time=base + timedelta(seconds=RUN_GAP_S + 69),
            latency=9.0,
            usage={"total": 500, "input": 400, "output": 100},
            cost_details={"total": 0.00005},
            level="DEFAULT",
        )
    ]
    trace = make_trace("t-multi", extra_observations=rerun_obs)
    run = _run(trace)
    assert run.llm_call_count == 1
    assert run.total_tokens == 500
    assert run.cost_usd == 0.00005


def test_unknown_span_skipped_from_routing_path():
    trace = make_trace(
        "t-unknown-span",
        stage="weird-stage",
        span_names=["ingest-document", "mystery-node", "classify-document"],
        verdict=None,
    )
    run = _run(trace)
    assert run.stage == Stage.CLASSIFY
    assert "mystery-node" not in run.routing_path
    assert "classify" in run.routing_path


def test_error_span_status_and_message():
    trace = make_trace("t-err", error_spans=True)
    run = _run(trace)
    errored = [s for s in run.spans if s.status == "ERROR"]
    assert errored
    assert all(s.error_message == "boom" for s in errored)


def test_run_aborted_and_error_message_from_output():
    trace = make_trace(
        "t-abort",
        stage="failed",
        verdict=None,
        output_extra={"run_aborted": True, "error_message": "LLM timeout"},
    )
    run = _run(trace)
    assert run.run_aborted is True
    assert run.error_message == "LLM timeout"


def test_review_decision_and_escalation_reason():
    trace = make_trace(
        "t-boss",
        stage="review",
        verdict=None,
        output_extra={"review_decision": "approved", "escalation_reason": "conflict detected"},
    )
    run = _run(trace)
    assert run.review_decision == "approved"
    assert run.escalation_reason == "conflict detected"


def test_doc_type_falls_back_to_input():
    trace = make_trace("t-in", stage="processing")
    trace["output"].pop("doc_type")
    trace["input"]["doc_type"] = "correspondence"
    run = _run(trace)
    assert run.doc_type == "correspondence"


def test_attempt_falls_back_to_metadata():
    trace = make_trace("t-att", stage="processing")
    trace["input"].pop("attempt")
    trace["metadata"]["attempt"] = 3
    run = _run(trace)
    assert run.attempt == 3


def test_partial_and_miss_verdicts():
    for verdict in ("PARTIAL", "MISS"):
        trace = make_trace(f"t-{verdict.lower()}", stage="archived", verdict=verdict)
        assert _run(trace).verdict == verdict


def test_score_objects_preserve_details():
    trace = make_trace("t-score-details", stage="archived", verdict=None)
    trace["scores"].append(
        Obj(
            name="custom-score",
            value=7,
            data_type="NUMERIC",
            comment="checked by reviewer",
            observation_id="span-1",
        )
    )
    run = _run(trace)
    assert run.scores["custom-score"] == 7
    score = next(s for s in run.score_objects if s.name == "custom-score")
    assert score.comment == "checked by reviewer"
    assert score.observation_id == "span-1"


def test_generation_detected_by_model_attribute():
    base = datetime(2026, 1, 1, 12, 0, 0)
    gen_obs = Obj(
        id="odd-gen",
        type="OBSERVATION",
        name="pipeline-result",
        model="qwen/qwen3.7-flash",
        start_time=base + timedelta(seconds=50),
        end_time=base + timedelta(seconds=58),
        usage={"total": 100},
        metadata={"langfuse_prompt": "mailroom-reporter:42"},
        level="DEFAULT",
    )
    trace = make_trace("t-genattr", stage="archived", extra_observations=[gen_obs])
    run = _run(trace)
    gens = [g for g in run.generations if g.name == "pipeline-result"]
    assert len(gens) == 1
    assert gens[0].model == "qwen/qwen3.7-flash"
    assert gens[0].prompt_version == "mailroom-reporter:42"
    assert gens[0].usage_total_tokens == 100


def test_quality_and_verdict_absent_without_scores():
    trace = make_trace("t-noscores", stage="archived", verdict=None, quality=None)
    trace["scores"] = []
    run = _run(trace)
    assert run.verdict is None
    assert run.quality is None
    assert run.scores == {}


# ---- KANBAN-062/063 sync: judge gate + arbiter + reviewer pass ----


def test_judge_and_arbiter_spans_route_and_order():
    trace = make_trace(
        "t-judge-arbiter",
        span_names=[
            "ingest-document",
            "classify-document",
            "extract-fields",
            "judge-verify",
            "arbitrate-verdict",
            "compile-report",
            "write-catalog",
            "archive-document",
        ],
    )
    run = _run(trace)
    assert run.stage == Stage.ARCHIVED
    assert run.routing_path == [
        "ingest",
        "classify",
        "extract",
        "judge_verify",
        "arbiter",
        "report",
        "catalog",
        "archive",
    ]


def test_judge_verify_inflight_derives_from_last_span():
    trace = make_trace(
        "t-judge-inflight",
        stage="processing",
        span_names=["ingest-document", "classify-document", "extract-fields", "judge-verify"],
        verdict=None,
    )
    run = _run(trace)
    assert run.stage == Stage.JUDGE_VERIFY
    assert run.phase == Phase.EXTRACTION_ADJUDICATION


def test_arbiter_inflight_derives_from_last_span():
    trace = make_trace(
        "t-arbiter-inflight",
        stage="processing",
        span_names=["ingest-document", "classify-document", "extract-fields",
                    "judge-verify", "arbitrate-verdict"],
        verdict=None,
    )
    run = _run(trace)
    assert run.stage == Stage.ARBITER


def test_reviewer_pass_does_not_stack_retry_classify():
    """KANBAN-062 Lane A emits a THIRD classify-document span; the displayed
    path must contain retry_classify exactly once."""
    trace = make_trace(
        "t-reviewer-pass",
        span_names=[
            "ingest-document",
            "classify-document",
            "classify-document",
            "classify-document",
            "route-for-review",
        ],
        verdict=None,
    )
    run = _run(trace)
    assert run.routing_path.count("classify") == 1
    assert run.routing_path.count("retry_classify") == 1


def test_insurance_claim_doc_class_roundtrip():
    trace = make_trace(
        "t-insurance",
        doc_type="insurance_claim",
        span_names=["ingest-document", "classify-document", "extract-fields",
                    "compile-report", "write-catalog", "archive-document"],
    )
    run = _run(trace)
    assert run.doc_type == "insurance_claim"
    assert run.stage == Stage.ARCHIVED


def test_schema_mirror_covers_upstream_contract():
    """The mirror must know every upstream agent/doc class/span (the #1
    maintenance duty per AGENTS.md)."""
    from mailroom_ui import pipeline_schema as ps

    for span in ("judge-verify", "arbitrate-verdict"):
        assert span in ps.SPAN_STAGE_MAP
    for agent in ("sorter_reviewer", "arbiter", "insurance_claims_specialist",
                  "image_extractor", "intake"):
        assert agent in ps.AGENTS
    assert "normalize-intake" in ps.SPAN_STAGE_MAP
    assert ps.SPAN_STAGE_MAP["normalize-intake"] == Stage.INGEST
    assert "image-extractor" not in ps.AGENTS
    assert ps.DOC_CLASSES["insurance_claim"] == "Insurance Claim"
    assert ps.SPECIALIST_BY_DOC_CLASS["insurance_claim"] == "insurance_claims_specialist"
    schema = ps.PipelineSchema.load()
    assert schema.judge_band_high == 0.85


def test_docclass_eval_trace_maps_to_classify_station():
    """Entity-repo docclass runner traces (name docclass_classification,
    output {"sorter": {...}}) display at the SORTER station with doc_type +
    classification confidence — pilot runs become floor-visible data."""
    from mailroom_ui.trace_interpreter import interpret_trace

    now = "2026-08-24T12:00:00Z"
    run = interpret_trace({
        "id": "dc-1", "name": "docclass_classification", "timestamp": now,
        "session_id": "qwen3.7-flash_sorter_docclass_pilot_v1_pilot140",
        "environment": "pilot",
        "tags": ["llm-dojo", "pilot"],
        "input": {"filename": "sample.pdf", "expected": "contract"},
        "output": {"sorter": {"doc_type": "contract", "contract_subtype": "license",
                              "doc_subclass": None, "confidence": 0.93,
                              "reasoning": "title says LICENSE"}},
    })
    assert run.stage.value == "classify"
    assert run.phase.value == "intake_sort"
    assert run.doc_type == "contract"
    assert abs(run.classification_confidence - 0.93) < 1e-9
    assert run.filename == "sample.pdf"


def test_list_recent_runs_honors_trace_names_env(monkeypatch):
    """MAILROOM_TRACE_NAMES extends the floor's trace-name universe and
    merges results across names without duplicates."""
    from datetime import datetime, timedelta, timezone

    import mailroom_ui.langfuse_source as ls

    calls = []

    class StubSource:
        def list_traces(self, *, since=None, limit=200, name=None, tags=None, environments=None):
            calls.append(name)
            if name == "document-pipeline":
                return [{"id": "t1", "timestamp": "2026-08-24T12:00:00Z"}]
            if name == "docclass_classification":
                return [{"id": "t1", "timestamp": "2026-08-24T12:00:00Z"},   # duplicate
                        {"id": "t2", "timestamp": "2026-08-24T12:01:00Z"}]
            return []

        def get_score_configs(self):
            return {}

    monkeypatch.setattr(ls.os, "environ", {**ls.os.environ, "MAILROOM_TRACE_NAMES": "document-pipeline,docclass_classification"})
    runs = ls.list_recent_runs(StubSource(), since=datetime.now(timezone.utc), limit=10)
    assert sorted(calls) == ["docclass_classification", "document-pipeline"]
    assert [r.trace_id for r in runs] == ["t2", "t1"]

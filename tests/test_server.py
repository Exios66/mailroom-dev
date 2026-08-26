"""End-to-end API tests (FastAPI TestClient over the fake Langfuse client)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from mailroom_ui.langfuse_source import LangfuseSource
from server.main import create_app
from tests.fake_langfuse import FakeClient, make_trace


def _fresh_traces():
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    return [
        make_trace("t1", base_time=now),
        make_trace("t2", stage="review", doc_type="correspondence",
                   base_time=now - timedelta(minutes=5)),
        make_trace("t3", stage="failed", doc_type="corporate_record",
                   base_time=now - timedelta(minutes=9)),
    ]


def _client():
    src = LangfuseSource(client=FakeClient(_fresh_traces()))
    return TestClient(create_app(src))


def test_metrics_aggregates_enriched_runs():
    """V-3: metrics must aggregate FULL runs — the old light-run aggregation
    permanently showed $0.00 / 0 tok / 0 calls."""
    with _client() as c:
        m = c.get("/api/metrics?since=604800").json()
    assert m["total_docs"] == 3
    assert m["archived"] == 1 and m["review"] == 1 and m["failed"] == 1
    assert m["total_tokens"] > 0
    assert m["total_cost_usd"] > 0
    assert m["llm_calls"] > 0
    assert m["verdict_counts"].get("CORRECT") == 3


def test_review_queue_serves_enriched_runs():
    """V-20: review cards must carry verdicts/tokens/cost, not zeros."""
    with _client() as c:
        r = c.get("/api/review-queue").json()
    assert r["count"] == 1
    run = r["runs"][0]
    assert run["total_tokens"] > 0
    assert run["cost_usd"] > 0
    assert run["verdict"] == "CORRECT"


def test_sessions_serve_enriched_runs():
    """V-19: session runs need observations/scores (verdicts, tokens, cost)."""
    with _client() as c:
        s = c.get("/api/sessions?limit=10").json()
    # All three fixtures share matter MATTER-001 -> one session, three traces.
    assert s["count"] == 1
    assert s["sessions"][0]["trace_count"] == 3
    for run in s["sessions"][0]["runs"]:
        assert run["total_tokens"] > 0
        assert run["cost_usd"] > 0
        assert run["llm_call_count"] > 0


def test_desk_runs_prefer_poller_snapshot():
    """SESSIONS/REVIEW/METRICS must reuse the poller's enriched list instead
    of walking Langfuse again (that blocked the inspector overlay)."""
    from unittest.mock import patch

    from server.main import _desk_runs
    from server.poller import PollHub

    src = LangfuseSource(client=FakeClient(_fresh_traces()))
    hub = PollHub(src, interval=60, window=21600, limit=100)
    assert hub._fetch() is not None
    assert len(hub.runs) == 3
    with patch("server.main.enriched_recent_runs",
               side_effect=AssertionError("must not re-walk Langfuse")):
        runs = _desk_runs(src, hub, since_seconds=7 * 86400, limit=200)
    assert len(runs) == 3
    assert {r.trace_id for r in runs} == {"t1", "t2", "t3"}


def test_generic_errors_are_json_with_detail():
    """V-18: non-Langfuse server errors must come back as JSON the SPA can
    display — the old default 500 was plain text and got discarded."""

    class BoomSource:
        def health(self):
            return {"langfuse": True, "source": "langfuse", "cached_trace_count": None}

        def list_traces(self, **kw):
            raise RuntimeError("boom")

    src = BoomSource()
    # raise_server_exceptions=False: ServerErrorMiddleware always re-raises
    # after producing the response; the flag lets the response through.
    with TestClient(create_app(src), raise_server_exceptions=False) as c:
        r = c.get("/api/traces")
    assert r.status_code == 500
    body = r.json()
    assert body["error"] == "internal server error"
    assert "boom" in body["detail"]


def test_meta_uses_pipeline_schema_override():
    with _client() as c:
        m = c.get("/api/meta").json()
    assert m["source"] == "langfuse"
    assert isinstance(m["doc_classes"], dict)
    assert "contract" in m["doc_classes"]


def test_index_served_no_cache():
    """V-22: index.html must never be cached."""
    with _client() as c:
        r = c.get("/")
    assert r.status_code == 200
    assert "no-store" in r.headers.get("cache-control", "")


def test_judge_gate_run_flows_through_display_api():
    """A run sitting in the KANBAN-063 quality gate (judge-verify span, no
    output stage yet) must surface as stage=judge_verify with the new span in
    its routing path — not fall back to the sorter station."""
    now = datetime.now() - timedelta(hours=1)
    traces = [
        make_trace(
            "t-judge-gate",
            base_time=now,
            stage="processing",
            doc_type="insurance_claim",
            verdict=None,
            quality=None,
            span_names=["ingest-document", "classify-document",
                        "extract-fields", "judge-verify"],
        ),
    ]
    src = LangfuseSource(client=FakeClient(traces))
    with TestClient(create_app(src)) as c:
        listing = c.get("/api/traces?since=3600").json()
        detail = c.get("/api/traces/t-judge-gate").json()
    run = listing["runs"][0]
    assert run["stage"] == "judge_verify"
    assert run["phase"] == "extraction"
    assert run["doc_type"] == "insurance_claim"
    assert "judge_verify" in run["routing_path"]
    assert any(s["name"] == "judge-verify" for s in detail["spans"])
    judge = next(s for s in detail["spans"] if s["name"] == "judge-verify")
    assert judge["observation_type"] == "EVALUATOR"

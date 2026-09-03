"""PhoenixSource tests: mapping contract + failure isolation (no network)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from mailroom_ui.phoenix_source import PhoenixSource, PhoenixUnavailable
from server.main import create_app
from tests.fake_phoenix import FakePhoenixClient, make_phoenix_trace


def _source(traces=None) -> PhoenixSource:
    return PhoenixSource(client=FakePhoenixClient(traces))


def test_list_traces_groups_roots_and_maps_fields():
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    src = _source([
        make_phoenix_trace("p1", base_time=now),
        make_phoenix_trace("p2", base_time=now - timedelta(minutes=5)),
    ])
    traces = src.list_traces(since=now - timedelta(hours=2), limit=10)
    assert [t["id"] for t in traces] == ["p1", "p2"]
    t = traces[0]
    assert t["name"] == "document-pipeline"
    assert t["session_id"] == "MATTER-001"
    assert "mailroom" in t["tags"] and "pilot" in t["tags"]
    assert t["environment"] == "pilot"
    assert t["input"]["filename"] == "sample.txt"
    assert t["output"]["stage"] == "archived"


def test_get_run_full_interpretation():
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    src = _source([make_phoenix_trace("p-full", base_time=now)])
    run = src.get_run("p-full")
    assert run is not None
    assert run.stage.value == "archived"
    assert run.doc_type == "contract"
    assert run.filename == "sample.txt"
    assert run.matter_id == "MATTER-001"
    # LLM child span -> generation with model/usage/cost
    assert run.llm_call_count == 1
    assert run.total_tokens == 1200
    assert abs(run.cost_usd - 0.0021) < 1e-9
    assert any(g.model == "qwen2.5:7b" for g in run.generations)
    # node observations mapped through SPAN_STAGE_MAP + NODE_OBSERVATION_TYPES
    names = [s.name for s in run.spans]
    assert "intake-document" in names and "archive-document" in names
    by_name = {s.name: s.observation_type for s in run.spans}
    assert by_name["intake-document"] == "SPAN"
    # index 1 of the fixture is the LLM child (same name as classify-document
    # in some traces, but here it is a GENERATION — nodes stay typed).
    assert by_name["extract-fields"] == "AGENT"
    assert by_name["compile-report"] == "AGENT"
    assert by_name["write-catalog"] == "SPAN"
    assert by_name["archive-document"] == "SPAN"
    assert all(s.observation_type != "GENERATION" for s in run.spans)
    # annotations -> scores -> verdict/quality
    assert run.verdict == "CORRECT"
    assert run.quality == 0.88


def test_unknown_spans_degrade_not_crash():
    """Spans outside the llm-mailroom contract must interpret to a run with
    unknown/inbox staging — never an exception."""
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    spans = make_phoenix_trace(
        "p-unknown", base_time=now,
        span_names=["my-agent-plan", "my-agent-act"],
        stage="still-running", doc_type="", verdict=None, quality=None,
    )
    src = _source([spans])
    run = src.get_run("p-unknown")
    assert run is not None
    assert run.stage.value in ("inbox", "unknown", "classify", "extract")


def test_error_span_surfaces_message():
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    src = _source([make_phoenix_trace("p-err", base_time=now, error_span=True,
                                      verdict=None, quality=None)])
    run = src.get_run("p-err")
    assert run.error_message and "bad JSON" in run.error_message


def test_unavailable_client_raises_contract_error():
    src = _source([])
    src.available = False
    with pytest.raises(PhoenixUnavailable):
        src.list_traces(limit=5)


def test_health_reflects_reachability():
    ok = _source([make_phoenix_trace("h1")])
    assert ok.health()["phoenix"] is True
    down = _source([])
    down.available = False
    h = down.health()
    assert h["phoenix"] is False and h["ok"] is False


def test_serves_through_display_api():
    """The FastAPI app must accept a PhoenixSource unchanged."""
    from fastapi.testclient import TestClient

    now = datetime.now(timezone.utc) - timedelta(minutes=50)
    src = _source([make_phoenix_trace("p-api", base_time=now)])
    with TestClient(create_app(src)) as c:
        listing = c.get("/api/traces?since=3600").json()
        health = c.get("/api/health").json()
        meta = c.get("/api/meta").json()
    assert listing["count"] == 1
    assert listing["source"] == "phoenix"
    assert health["phoenix"] is True
    assert meta["source"] == "phoenix"
    assert any(e["path"] == "/api/debug/logs" for e in meta["endpoints"])

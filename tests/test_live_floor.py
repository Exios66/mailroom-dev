"""Live-floor freshness: in-flight traces, pipeline ops, graph node aliases."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from mailroom_ui.langfuse_source import LangfuseSource
from mailroom_ui.models import Stage
from mailroom_ui.pipeline_schema import SPAN_STAGE_MAP
from server.main import create_app
from server.poller import PollHub, is_conveyor_hot, run_fingerprint
from tests.fake_langfuse import FakeClient, make_trace
from tests.test_interpreter import _run


def test_graph_node_names_map_to_stations():
    assert SPAN_STAGE_MAP["retry_classify"] is Stage.RETRY_CLASSIFY
    assert SPAN_STAGE_MAP["review_classify"] is Stage.RETRY_CLASSIFY
    assert SPAN_STAGE_MAP["judge_verify"] is Stage.JUDGE_VERIFY
    assert SPAN_STAGE_MAP["boss_escalation"] is Stage.BOSS
    assert SPAN_STAGE_MAP["catalog_write"] is Stage.CATALOG
    run = _run(make_trace(
        "t-graph-ids",
        stage="processing",
        span_names=["ingest", "classify", "extract", "judge_verify"],
    ))
    assert run.stage is Stage.JUDGE_VERIFY
    assert "judge_verify" in run.routing_path


def test_poller_refreshes_inflight_when_spans_advance():
    now = datetime.now(timezone.utc) - timedelta(minutes=5)
    first = make_trace(
        "t-live",
        stage="processing",
        span_names=["ingest-document"],
        base_time=now,
        verdict=None,
        quality=None,
    )
    client = FakeClient([first])
    src = LangfuseSource(client=client, cache_ttl=60, poll_cache_ttl=60, run_cache_ttl=60)
    hub = PollHub(src, interval=3, window=3600, limit=10, inflight_ttl=0)
    snap1 = hub._fetch()
    assert snap1 is not None
    assert snap1[0]["stage"] == "ingest"

    advanced = make_trace(
        "t-live",
        stage="processing",
        span_names=["ingest-document", "classify-document", "extract-fields"],
        base_time=now,
        verdict=None,
        quality=None,
        latency=20.0,
    )
    client.traces[:] = [advanced]
    snap2 = hub._fetch()
    assert snap2[0]["stage"] == "extract"


def test_poller_keeps_terminal_detail_when_fingerprint_matches():
    now = datetime.now(timezone.utc) - timedelta(minutes=5)
    tr = make_trace("t-done", stage="archived", base_time=now)
    client = FakeClient([tr])
    src = LangfuseSource(client=client, cache_ttl=60, poll_cache_ttl=60, run_cache_ttl=60)
    hub = PollHub(src, interval=3, window=3600, limit=10)
    first = hub._fetch()
    assert first[0]["stage"] == "archived"
    cached_at = hub._details["t-done"][0]
    second = hub._fetch()
    assert second[0]["stage"] == "archived"
    assert hub._details["t-done"][0] == cached_at


def test_get_run_force_refresh_bypasses_run_cache():
    now = datetime.now(timezone.utc) - timedelta(minutes=5)
    client = FakeClient([make_trace(
        "t-force", stage="processing", span_names=["ingest-document"],
        base_time=now, verdict=None, quality=None,
    )])
    src = LangfuseSource(client=client, cache_ttl=60, poll_cache_ttl=60, run_cache_ttl=60)
    first = src.get_run("t-force")
    assert first.stage is Stage.INGEST
    client.traces[:] = [make_trace(
        "t-force", stage="processing",
        span_names=["ingest-document", "classify-document"],
        base_time=now, verdict=None, quality=None,
    )]
    stale = src.get_run("t-force")
    assert stale.stage is Stage.INGEST
    fresh = src.get_run("t-force", force_refresh=True)
    assert fresh.stage is Stage.CLASSIFY


def test_pipeline_endpoint_unconfigured():
    src = LangfuseSource(client=FakeClient([make_trace("t1")]))
    with TestClient(create_app(src)) as c:
        r = c.get("/api/pipeline")
        assert r.status_code == 200
        body = r.json()
        assert body["configured"] is False
        meta = c.get("/api/meta").json()
    assert "poll_interval_s" in meta
    assert any(e["path"] == "/api/pipeline" for e in meta["endpoints"])


def test_pipeline_ops_reads_health(monkeypatch):
    from mailroom_ui import pipeline_ops

    monkeypatch.setenv("MAILROOM_PIPELINE_URL", "http://pipeline.test:8000")

    def fake_get(url, *, timeout=1.5, token=""):
        assert url.endswith("/health")
        return {
            "status": "ok",
            "checks": {
                "watcher_heartbeat_seconds_ago": 0.4,
                "inbox_pending": 2,
                "ingestion_paused": False,
            },
        }

    monkeypatch.setattr(pipeline_ops, "_get_json", fake_get)
    ops = pipeline_ops.fetch_pipeline_ops()
    assert ops["configured"] is True
    assert ops["watcher"] == "live"
    assert ops["inbox_pending"] == 2
    assert ops["ok"] is True


def test_ws_snapshot_includes_pipeline_and_poll_interval():
    src = LangfuseSource(client=FakeClient([make_trace("t1")]))
    hub = PollHub(src, interval=2.5, window=3600, limit=10)
    msg = hub._snapshot_message(stale=False)
    assert msg["type"] == "snapshot"
    assert msg["poll_interval_s"] == 2.5
    assert "pipeline" in msg
    assert is_conveyor_hot(_run(make_trace(
        "hot", stage="processing", span_names=["classify-document"],
        verdict=None, quality=None,
    )))
    done = _run(make_trace("done", stage="archived"))
    assert not is_conveyor_hot(done)
    assert run_fingerprint(done)[1] == "archived"


def test_pipeline_ops_prefers_declared_watcher(monkeypatch):
    from mailroom_ui import pipeline_ops

    monkeypatch.setenv("MAILROOM_PIPELINE_URL", "http://pipeline.test:8000")

    def fake_get(url, *, timeout=1.5, token=""):
        return {
            "status": "ok",
            "checks": {
                "watcher": "live",
                "watcher_heartbeat_seconds_ago": 40.0,
                "inbox_pending": 0,
            },
        }

    monkeypatch.setattr(pipeline_ops, "_get_json", fake_get)
    ops = pipeline_ops.fetch_pipeline_ops()
    assert ops["watcher"] == "live"
    assert ops["inbox_pending"] == 0
    assert ops["ok"] is True


def test_pipeline_ops_reads_top_level_inbox(monkeypatch):
    from mailroom_ui import pipeline_ops

    monkeypatch.setenv("MAILROOM_PIPELINE_URL", "http://pipeline.test:8000")

    def fake_get(url, *, timeout=1.5, token=""):
        return {
            "status": "ok",
            "watcher_heartbeat_seconds_ago": 1.0,
            "inbox_pending": 3,
            "ingestion_paused": True,
        }

    monkeypatch.setattr(pipeline_ops, "_get_json", fake_get)
    ops = pipeline_ops.fetch_pipeline_ops()
    assert ops["watcher"] == "live"
    assert ops["inbox_pending"] == 3
    assert ops["ingestion_paused"] is True
    assert ops["ok"] is True


def test_server_source_ttl_follows_poll_interval():
    from pathlib import Path

    from server import main as server_main

    text = Path(server_main.__file__).read_text()
    assert "cache_ttl=ttl" in text
    assert "poll_cache_ttl=ttl" in text
    assert "ttl = max(0.0, POLL_INTERVAL)" in text


def test_pipeline_ops_unconfigured_without_url(monkeypatch):
    from mailroom_ui.pipeline_ops import fetch_pipeline_ops

    monkeypatch.delenv("MAILROOM_PIPELINE_URL", raising=False)
    monkeypatch.delenv("MAILROOM_PIPELINE_API", raising=False)
    ops = fetch_pipeline_ops()
    assert ops["configured"] is False

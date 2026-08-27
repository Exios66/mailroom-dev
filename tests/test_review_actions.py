"""Human-review resolve proxy: visualizer never holds producer keys in the browser."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from mailroom_ui.langfuse_source import LangfuseSource
from mailroom_ui.review_actions import ReviewActionError, resolve_review, review_context
from server.main import create_app
from tests.fake_langfuse import FakeClient, make_trace
from tests.test_interpreter import _run


def test_interpreter_lifts_doc_id_from_output_and_input():
    run = _run(make_trace(
        "t-doc",
        output_extra={"doc_id": "doc-abc"},
        extra_input={"doc_id": "doc-abc"},
    ))
    assert run.doc_id == "doc-abc"


def test_interpreter_ignores_filename_shaped_span_doc_id():
    run = _run(make_trace("t-file", filename="sample.txt"))
    assert run.doc_id is None


def test_floor_payload_includes_doc_id():
    from server.poller import floor_payload

    run = _run(make_trace("t-pay", output_extra={"doc_id": "doc-pay"}))
    assert floor_payload(run)["doc_id"] == "doc-pay"


def test_review_context_unconfigured(monkeypatch):
    monkeypatch.delenv("MAILROOM_PIPELINE_URL", raising=False)
    monkeypatch.delenv("MAILROOM_PIPELINE_API", raising=False)
    monkeypatch.delenv("MAILROOM_PIPELINE_TOKEN", raising=False)
    monkeypatch.delenv("MAILROOM_API_TOKEN", raising=False)
    ctx = review_context(trace_id="t1")
    assert ctx["configured"] is False
    assert ctx["document"] is None
    assert "MAILROOM_PIPELINE" in ctx["error"]


def test_resolve_unconfigured_raises(monkeypatch):
    monkeypatch.delenv("MAILROOM_PIPELINE_URL", raising=False)
    monkeypatch.delenv("MAILROOM_PIPELINE_API", raising=False)
    try:
        resolve_review(decision="approved", trace_id="t1")
        assert False, "expected ReviewActionError"
    except ReviewActionError as exc:
        assert exc.status == 503


def test_api_review_context_unconfigured():
    src = LangfuseSource(client=FakeClient([make_trace("t1", stage="review")]))
    with TestClient(create_app(src)) as c:
        r = c.get("/api/review/context")
        assert r.status_code == 200
        body = r.json()
        assert body["configured"] is False


def test_api_review_resolve_unconfigured():
    src = LangfuseSource(client=FakeClient([make_trace("t1", stage="review")]))
    with TestClient(create_app(src)) as c:
        r = c.post("/api/review/resolve", json={
            "trace_id": "t1", "decision": "approved", "disposition": "record",
        })
        assert r.status_code == 503
        assert "MAILROOM_PIPELINE" in (r.json().get("error") or "")


def test_api_review_resolve_proxies(monkeypatch):
    monkeypatch.setenv("MAILROOM_PIPELINE_URL", "http://pipeline.test:8000")
    monkeypatch.setenv("MAILROOM_PIPELINE_TOKEN", "secret-token")

    calls = []

    def fake_request(method, url, *, token="", body=None, timeout=8.0):
        calls.append({"method": method, "url": url, "token": token, "body": body})
        if method == "GET" and "/lookup" in url:
            return {"status": "ok", "document": {"doc_id": "doc-xyz", "trace_id": "t-rev"}}
        if method == "POST" and "/review/" in url:
            return {
                "status": "ok",
                "doc_id": "doc-xyz",
                "decision": body["decision"],
                "disposition": body["disposition"],
                "notes": body["notes"],
            }
        raise AssertionError(url)

    from mailroom_ui import review_actions

    src = LangfuseSource(client=FakeClient([
        make_trace("t-rev", stage="review", filename="claim.txt", output_extra={"doc_id": "doc-xyz"}),
    ]))
    with patch.object(review_actions, "_request_json", side_effect=fake_request):
        with TestClient(create_app(src)) as c:
            r = c.post("/api/review/resolve", json={
                "trace_id": "t-rev",
                "filename": "claim.txt",
                "decision": "approved",
                "disposition": "resume",
                "notes": "looks good",
            })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["doc_id"] == "doc-xyz"
    assert body["disposition"] == "resume"
    assert any(c["method"] == "POST" and "/review/doc-xyz/resolve" in c["url"] for c in calls)
    posted = next(c for c in calls if c["method"] == "POST")
    assert posted["token"] == "secret-token"
    assert posted["body"]["notes"] == "looks good"


def test_review_queue_includes_doc_id():
    src = LangfuseSource(client=FakeClient([
        make_trace("t-rev", stage="review", output_extra={"doc_id": "doc-q"}),
    ]))
    with TestClient(create_app(src)) as c:
        r = c.get("/api/review-queue").json()
    assert r["count"] == 1
    assert r["runs"][0]["doc_id"] == "doc-q"

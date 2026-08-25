"""Hosted Observatory edition: public /live UI, distinct from the pixel console."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mailroom_ui.langfuse_source import LangfuseSource
from server.main import create_app
from tests.fake_langfuse import FakeClient, make_trace


def _client(monkeypatch=None, edition="console"):
    if monkeypatch is not None:
        monkeypatch.setenv("MAILROOM_EDITION", edition)
    src = LangfuseSource(client=FakeClient([make_trace("t1")]))
    return TestClient(create_app(src))


def test_live_ui_is_served_on_every_edition():
    with _client() as c:
        r = c.get("/live")
    assert r.status_code == 200
    body = r.text
    assert "Mailroom Observatory" in body
    assert 'href="#pipeline"' in body
    assert 'class="skip-link"' in body
    assert 'id="main"' in body
    assert "no-store" in r.headers.get("cache-control", "")


def test_live_assets_are_mounted():
    with _client() as c:
        css = c.get("/live/static/css/app.css")
        js = c.get("/live/static/js/app.js")
        client = c.get("/live/static/js/client.js")
    assert css.status_code == 200 and "skip-link" in css.text
    assert js.status_code == 200 and "startReplay" in js.text
    assert client.status_code == 200 and "reviewQueue" in client.text


def test_default_root_remains_pixel_console():
    with _client() as c:
        r = c.get("/")
    assert r.status_code == 200
    assert "THE MAILROOM" in r.text
    assert "Mailroom Observatory" not in r.text


def test_hosted_edition_puts_observatory_on_root(monkeypatch):
    monkeypatch.setenv("MAILROOM_EDITION", "hosted")
    src = LangfuseSource(client=FakeClient([make_trace("t1")]))
    with TestClient(create_app(src)) as c:
        r = c.get("/")
        live = c.get("/live")
    assert "Mailroom Observatory" in r.text
    assert "Mailroom Observatory" in live.text


def test_meta_advertises_hosted_ui():
    with _client() as c:
        m = c.get("/api/meta").json()
    assert m["edition"] == "console"
    assert m["ui"]["hosted"] == "/live"
    paths = [e["path"] for e in m["endpoints"]]
    assert "/live" in paths

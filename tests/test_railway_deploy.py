"""Listen-port + /health platform contract (Railway / Fly / Spaces)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from server.main import create_app, listen_port
from tests.fake_langfuse import FakeClient, make_trace
from mailroom_ui.langfuse_source import LangfuseSource


def test_listen_port_prefers_platform_port(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("MAILROOM_PORT", "7860")
    assert listen_port() == 8080


def test_listen_port_falls_back_to_mailroom_port(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("MAILROOM_PORT", "9001")
    assert listen_port() == 9001


def test_listen_port_default(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("MAILROOM_PORT", raising=False)
    assert listen_port(8001) == 8001


def test_health_root_mirrors_api_health():
    src = LangfuseSource(client=FakeClient([make_trace("t-health")]))
    with TestClient(create_app(src)) as c:
        api = c.get("/api/health")
        root = c.get("/health")
        assert api.status_code == 200
        assert root.status_code == 200
        assert api.json()["ok"] is True
        assert root.json()["ok"] is True
        assert "mailroom" in root.json()

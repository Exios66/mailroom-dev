"""Listen-port + /health platform contract (Railway / Fly / Spaces)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from server.main import create_app, listen_port
from tests.fake_langfuse import FakeClient, make_trace
from mailroom_ui.langfuse_source import LangfuseSource

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def test_health_root_is_platform_liveness_without_source():
    """Railway / Docker probes must not wait on Langfuse."""

    class HangingSrc:
        def health(self):
            raise AssertionError("platform /health must not call src.health()")

    with TestClient(create_app(HangingSrc())) as c:
        root = c.get("/health")
        assert root.status_code == 200
        body = root.json()
        assert body["ok"] is True
        assert body["status"] == "alive"
        assert "edition" in body


def test_api_health_still_reports_source():
    src = LangfuseSource(client=FakeClient([make_trace("t-health")]))
    with TestClient(create_app(src)) as c:
        api = c.get("/api/health")
        assert api.status_code == 200
        assert api.json()["ok"] is True
        assert "mailroom" in api.json()


def test_railway_json_forces_dockerfile_builder():
    cfg = json.loads((REPO_ROOT / "railway.json").read_text(encoding="utf-8"))
    assert cfg["build"]["builder"] == "DOCKERFILE"
    assert cfg["build"]["dockerfilePath"] == "Dockerfile"
    assert cfg["deploy"]["healthcheckPath"] == "/health"


def test_dockerfile_healthcheck_prefers_platform_port():
    text = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "HEALTHCHECK" in text
    assert "os.environ.get('PORT')" in text
    assert "/health" in text
    assert "server.hosted" in text


def test_nixpacks_fallback_binds_hosted():
    text = (REPO_ROOT / "nixpacks.toml").read_text(encoding="utf-8")
    assert "MAILROOM_HOST=0.0.0.0" in text
    assert "python -m server.hosted" in text

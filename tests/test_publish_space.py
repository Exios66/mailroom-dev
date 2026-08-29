"""Offline checks for the Hugging Face Space publisher."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts import publish_space as pub

ROOT = Path(__file__).resolve().parent.parent


def test_space_card_is_docker_on_7860():
    card = (ROOT / "hosted" / "SPACE_README.md").read_text(encoding="utf-8")
    assert card.lstrip().startswith("---")
    assert "sdk: docker" in card
    assert "app_port: 7860" in card
    assert "LANGFUSE_PUBLIC_KEY" in card
    assert "LANGFUSE_HOST" in card
    for field in ("colorFrom:", "colorTo:"):
        line = next(ln for ln in card.splitlines() if ln.startswith(field))
        assert line.split(":", 1)[1].strip() in pub.HF_COLORS


def test_dockerfile_is_hosted_observatory():
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "MAILROOM_EDITION=hosted" in docker
    assert "7860" in docker
    assert "server.hosted" in docker
    for rel in pub.COPY_PATHS:
        assert rel in docker


def test_check_payload_passes():
    notes = pub.check_payload()
    joined = "\n".join(notes)
    assert "sdk=docker" in joined
    assert "hosted edition" in joined


def test_stage_space_tree_uses_space_card_and_drops_env(tmp_path, monkeypatch):
    leaked = ROOT / "mailroom_ui" / ".env"
    leaked.write_text("LANGFUSE_SECRET_KEY=do-not-ship\n", encoding="utf-8")
    try:
        dest = tmp_path / "space"
        pub.stage_space_tree(dest)
        readme = (dest / "README.md").read_text(encoding="utf-8")
        assert readme == (ROOT / "hosted" / "SPACE_README.md").read_text(encoding="utf-8")
        assert (dest / "Dockerfile").is_file()
        assert (dest / "server" / "hosted.py").is_file()
        assert (dest / "hosted" / "index.html").is_file()
        assert not (dest / "mailroom_ui" / ".env").exists()
        assert "do-not-ship" not in readme
        staged = "\n".join(
            p.read_text(encoding="utf-8")
            for p in dest.rglob("*")
            if p.is_file() and p.suffix in {".md", ".py", ".toml", ".yml"}
        )
        assert "do-not-ship" not in staged
    finally:
        if leaked.exists():
            leaked.unlink()


def test_resolved_host_accepts_base_url_alias(monkeypatch):
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
    assert pub._resolved_host() == "https://us.cloud.langfuse.com"
    monkeypatch.setenv("LANGFUSE_HOST", "https://example.invalid")
    assert pub._resolved_host() == "https://example.invalid"


def test_secret_values_refuse_swapped_keys(monkeypatch):
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "sk-lf-secret")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "pk-lf-public")
    with pytest.raises(SystemExit):
        pub._secret_values()


def test_cli_check_exits_zero():
    assert pub.main(["--check"]) == 0

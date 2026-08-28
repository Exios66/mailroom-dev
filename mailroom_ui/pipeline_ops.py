"""Read-only bridge to the llm-mailroom API (watcher + inbox).

Document display stays Langfuse-only. This module reports *operator*
liveness: whether the producer watcher is beating and how many files are
waiting in the filesystem inbox. Missing config yields ``configured: false``,
never fabricated queue rows.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Optional

log = logging.getLogger("mailroom.pipeline_ops")

_WATCHER_STALE_S = 15.0


def pipeline_base_url() -> str:
    return (
        os.environ.get("MAILROOM_PIPELINE_URL")
        or os.environ.get("MAILROOM_PIPELINE_API")
        or ""
    ).strip().rstrip("/")


def pipeline_api_prefix() -> str:
    """Path prefix for llm-mailroom routes. Default ``/v1`` (producer README).

    Set ``MAILROOM_PIPELINE_API_PREFIX`` empty (or ``/``) to use the unversioned
    aliases still mounted during the producer's deprecation window.
    """
    raw = os.environ.get("MAILROOM_PIPELINE_API_PREFIX")
    if raw is None:
        return "/v1"
    text = raw.strip()
    if not text or text in (".", "/"):
        return ""
    if not text.startswith("/"):
        text = "/" + text
    return text.rstrip("/")


def producer_url(path: str) -> str:
    """Absolute producer URL: ``{MAILROOM_PIPELINE_URL}{/v1}{path}``."""
    if not path.startswith("/"):
        path = "/" + path
    return f"{pipeline_base_url()}{pipeline_api_prefix()}{path}"


def _token() -> str:
    return (
        os.environ.get("MAILROOM_PIPELINE_TOKEN")
        or os.environ.get("MAILROOM_API_TOKEN")
        or ""
    ).strip()


def _get_json(url: str, *, timeout: float = 1.5, token: str = "") -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw) if raw else {}
    return data if isinstance(data, dict) else {}


def _as_int(value: Any) -> Optional[int]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value == int(value):
        return int(value)
    return None


def _watcher_state(age: Optional[float], declared: Any = None) -> str:
    if declared in ("live", "stale", "missing"):
        return declared
    if age is None:
        return "missing"
    try:
        if float(age) > _WATCHER_STALE_S:
            return "stale"
    except (TypeError, ValueError):
        return "missing"
    return "live"


def fetch_pipeline_ops(*, timeout: float = 1.5) -> dict[str, Any]:
    """Snapshot of producer watcher/inbox health.

    Hits llm-mailroom ``GET /v1/health`` (no token; unversioned ``/health``
    is aliased). Optionally ``GET /v1/queue`` when ``MAILROOM_PIPELINE_TOKEN``
    is set, for filenames still sitting in the inbox before a Langfuse
    trace exists.
    """
    base = pipeline_base_url()
    if not base:
        return {"configured": False, "ok": None, "watcher": "unconfigured"}
    token = _token()
    out: dict[str, Any] = {
        "configured": True,
        "ok": False,
        "url": base,
        "watcher": "missing",
        "watcher_heartbeat_seconds_ago": None,
        "inbox_pending": None,
        "processing": None,
        "ingestion_paused": None,
        "queued": [],
        "error": None,
        "token_configured": bool(token),
    }
    try:
        health = _get_json(producer_url("/health"), timeout=timeout)
    except Exception as exc:
        log.warning("pipeline health failed: %s", exc)
        out["error"] = str(exc)[:200]
        return out
    checks = health.get("checks") if isinstance(health.get("checks"), dict) else {}
    age = checks.get("watcher_heartbeat_seconds_ago")
    if not isinstance(age, (int, float)):
        age = health.get("watcher_heartbeat_seconds_ago")
    age_n = age if isinstance(age, (int, float)) and not isinstance(age, bool) else None
    watcher = _watcher_state(age_n, checks.get("watcher") or health.get("watcher"))
    paused = bool(checks.get("ingestion_paused") if "ingestion_paused" in checks
                  else health.get("ingestion_paused"))
    inbox = _as_int(checks.get("inbox_pending"))
    if inbox is None:
        inbox = _as_int(health.get("inbox_pending"))
    out.update({
        "ok": str(health.get("status", "")).lower() == "ok" and watcher == "live",
        "watcher": watcher,
        "watcher_heartbeat_seconds_ago": age_n,
        "inbox_pending": inbox,
        "ingestion_paused": paused,
        "status": health.get("status"),
    })
    if token:
        try:
            queue = _get_json(producer_url("/queue"), timeout=timeout, token=token)
            queued = queue.get("queued") if isinstance(queue, dict) else None
            processing = queue.get("processing") if isinstance(queue, dict) else None
            if isinstance(queued, list):
                out["queued"] = [
                    {
                        "file": item.get("file"),
                        "matter_id": item.get("matter_id"),
                        "uploaded_at": item.get("uploaded_at"),
                    }
                    for item in queued[:50]
                    if isinstance(item, dict)
                ]
                if out["inbox_pending"] is None:
                    out["inbox_pending"] = len(out["queued"])
            if isinstance(processing, list):
                out["processing"] = len(processing)
        except Exception as exc:
            log.warning("pipeline queue failed: %s", exc)
            out["error"] = str(exc)[:200]
    return out

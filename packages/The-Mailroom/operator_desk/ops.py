"""Operator ops snapshot.

Display numbers come from Langfuse-interpreted ``PipelineRun`` rows supplied
by the visualizer (PollHub). The producer's ``documents`` table is never
required and is never invented when missing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .auth import UserProfile, get_current_user, get_current_user_or_ingest
from .websocket import manager, publish_event, publish_matter_event

router = APIRouter(prefix="/v1/ops", tags=["operator-ops"])

_runs_provider: Optional[Callable[[], list]] = None


def set_runs_provider(provider: Optional[Callable[[], list]]) -> None:
    global _runs_provider
    _runs_provider = provider


def current_runs() -> list:
    if _runs_provider is None:
        return []
    try:
        rows = _runs_provider() or []
    except Exception:
        return []
    return list(rows)


class OpsStatus(BaseModel):
    throughput: float
    accuracy: float
    queue_depth: int
    active_agents: int
    avg_processing_time_ms: float
    source: str = "langfuse"
    total_docs: int = 0


def _run_ts(run: Any) -> Optional[datetime]:
    stamp = getattr(run, "updated_at", None) or getattr(run, "created_at", None)
    if stamp is None:
        return None
    if getattr(stamp, "tzinfo", None) is None:
        return stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def _stage_token(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _as_dict(run: Any) -> dict[str, Any]:
    if isinstance(run, dict):
        return {
            **run,
            "stage": _stage_token(run.get("stage")),
            "needs_human": bool(run.get("needs_human")),
        }
    return {
        "stage": _stage_token(getattr(run, "stage", None)),
        "verdict": getattr(run, "verdict", None),
        "needs_human": bool(getattr(run, "needs_human", False)),
        "doc_type": getattr(run, "doc_type", None),
        "latency": getattr(run, "latency", None),
        "updated_at": getattr(run, "updated_at", None),
        "created_at": getattr(run, "created_at", None),
        "spans": getattr(run, "spans", None),
    }


def compute_ops_status(runs: Optional[list] = None) -> OpsStatus:
    rows = runs if runs is not None else current_runs()
    now = datetime.now(timezone.utc)
    hour_ago = now - timedelta(hours=1)
    done_hour = 0
    verdicts = {"CORRECT": 0, "PARTIAL": 0, "MISS": 0}
    queue_depth = 0
    latencies: list[float] = []
    agents: set[str] = set()
    for run in rows:
        data = _as_dict(run)
        stage = _stage_token(data.get("stage"))
        if data.get("needs_human") or stage in ("review", "processing", "inbox", "intake", "classify"):
            queue_depth += 1
        stamp = _run_ts(run)
        if stamp is not None and stamp >= hour_ago and stage in (
            "archived", "archive", "catalog", "failed",
        ):
            done_hour += 1
        verdict = data.get("verdict")
        if verdict in verdicts:
            verdicts[verdict] += 1
        latency = data.get("latency")
        if isinstance(latency, (int, float)):
            latencies.append(float(latency) * 1000.0)
        for span in getattr(run, "spans", None) or data.get("spans") or []:
            name = span.get("name") if isinstance(span, dict) else getattr(span, "name", None)
            if name:
                agents.add(str(name))
    judged = sum(verdicts.values())
    accuracy = (verdicts["CORRECT"] / judged) if judged else 0.0
    avg_ms = sum(latencies) / len(latencies) if latencies else 0.0
    return OpsStatus(
        throughput=round(done_hour / 60.0, 2),
        accuracy=round(accuracy, 4),
        queue_depth=queue_depth,
        active_agents=len(agents),
        avg_processing_time_ms=round(avg_ms, 2),
        source="langfuse",
        total_docs=len(rows),
    )


@router.get("/health")
async def ops_health():
    from .db import db_path

    return {
        "ok": True,
        "module": "operator_desk",
        "db": str(db_path()),
        "connections": len(manager.active_connections),
    }


@router.get("/status", response_model=OpsStatus)
async def get_ops_status(user: UserProfile = Depends(get_current_user)):
    return compute_ops_status()


@router.get("/throughput")
async def get_throughput(user: UserProfile = Depends(get_current_user)):
    rows = current_runs()
    now = datetime.now(timezone.utc)
    history = []
    for i in range(23, -1, -1):
        start = now - timedelta(hours=i + 1)
        end = now - timedelta(hours=i)
        count = 0
        for run in rows:
            stamp = _run_ts(run)
            if stamp is None or stamp <= start or stamp > end:
                continue
            stage = _stage_token(getattr(run, "stage", None) if not isinstance(run, dict) else run.get("stage"))
            if stage in ("archived", "archive", "catalog", "failed"):
                count += 1
        history.append({"time": end.strftime("%H:%M"), "count": count})
    return {"history": history, "source": "langfuse"}


@router.get("/distribution")
async def get_distribution(user: UserProfile = Depends(get_current_user)):
    counts: dict[str, int] = {}
    for run in current_runs():
        doc_type = getattr(run, "doc_type", None) or "unknown"
        counts[str(doc_type)] = counts.get(str(doc_type), 0) + 1
    return {
        "types": [{"type": key, "count": value} for key, value in sorted(counts.items())],
        "source": "langfuse",
    }


@router.post("/events")
async def ingest_event(
    payload: dict[str, Any],
    user: UserProfile = Depends(get_current_user_or_ingest),
):
    """In-process observer uses ``publish_event`` directly; the standalone
    ``mailroom-observer`` daemon POSTs here so the API process owns the WS bus."""
    if not isinstance(payload, dict):
        return {"ok": False, "error": "expected JSON object"}
    event_type = str(payload.get("type") or "event")
    await publish_event(event_type, payload)
    document = payload.get("document") if isinstance(payload.get("document"), dict) else {}
    matter_id = document.get("matter_id") or payload.get("matter_id")
    if matter_id:
        await publish_matter_event(str(matter_id), event_type, payload)
    return {"ok": True, "type": event_type, "ingested_by": user.username}

"""Background poller: Langfuse -> compact run snapshots -> WebSocket clients."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import WebSocket

from mailroom_ui.langfuse_source import LangfuseSource, list_recent_runs
from mailroom_ui.models import PipelineRun

log = logging.getLogger("mailroom.poller")


def floor_payload(run: PipelineRun) -> dict[str, Any]:
    """Compact serialization for the floor view (list-level data only)."""
    return {
        "trace_id": run.trace_id,
        "filename": run.filename,
        "matter_id": run.matter_id,
        "session_id": run.session_id,
        "environment": run.environment,
        "user_id": run.user_id,
        "release": run.release,
        "tags": run.tags,
        "attempt": run.attempt,
        "stage": run.stage.value,
        "phase": run.phase.value,
        "doc_type": run.doc_type,
        "doc_subclass": run.doc_subclass,
        "contract_subtype": run.contract_subtype,
        "expected_hf_class": run.expected_hf_class,
        "expected_subclass": run.expected_subclass,
        "intake_messy": run.intake_messy,
        "intake_changed": run.intake_changed,
        "intake_method": run.intake_method,
        "intake_chars": run.intake_chars,
        "classification_confidence": run.classification_confidence,
        "extraction_confidence": run.extraction_confidence,
        "review_decision": run.review_decision,
        "escalation_reason": run.escalation_reason,
        "review_causes": run.review_causes,
        "needs_reconsideration": run.needs_reconsideration,
        "error_message": run.error_message,
        "verdict": run.verdict,
        "quality": run.quality,
        "latency": run.latency,
        "llm_call_count": run.llm_call_count,
        "total_tokens": run.total_tokens,
        "cost_usd": run.cost_usd,
        "retried": run.retried,
        "needs_human": run.needs_human,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "updated_at": run.updated_at.isoformat() if run.updated_at else None,
        "routing_path": run.routing_path,
    }


class PollHub:
    """One poll loop broadcasting snapshots to all connected clients."""

    def __init__(
        self,
        source: LangfuseSource,
        *,
        interval: float = 3.0,
        window: float = 7 * 86400,
        limit: int = 100,
        detail_ttl: float = 60.0,
    ) -> None:
        self.source = source
        self.interval = interval
        self.window = window
        self.limit = limit
        self.detail_ttl = detail_ttl
        self.clients: set[WebSocket] = set()
        self.snapshot: list[dict[str, Any]] = []
        # Last successful enriched PipelineRun list (same traces as snapshot).
        # Desk endpoints (sessions / review / metrics) read this instead of
        # walking Langfuse again — a 2-minute sequential enrich blocked the
        # inspector overlay on the single uvicorn worker.
        self.runs: list[PipelineRun] = []
        self._details: dict[str, tuple[float, dict[str, Any]]] = {}
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())
            log.info("poller started (interval=%ss window=%ss)", self.interval, self.window)

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.clients.add(ws)
        await ws.send_json({"type": "snapshot", "runs": self.snapshot})

    def disconnect(self, ws: WebSocket) -> None:
        self.clients.discard(ws)

    async def _run(self) -> None:
        while not self._stop.is_set():
            try:
                runs = await asyncio.to_thread(self._fetch)
                # V-4: a partial Langfuse failure must NOT wipe the floor —
                # keep the last good snapshot and mark it stale so the UI can
                # show a staleness badge instead of a blank screen with a
                # green lamp. `_fetch` returns None on failure (instead of
                # []), meaning "no fresh data".
                if runs is not None:
                    self.snapshot = runs
                payload = {
                    "type": "snapshot",
                    "runs": self.snapshot,
                    "stale": runs is None,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
                dead: list[WebSocket] = []
                for ws in list(self.clients):
                    try:
                        await ws.send_json(payload)
                    except Exception:
                        dead.append(ws)
                for ws in dead:
                    self.clients.discard(ws)
            except Exception as exc:  # pragma: no cover - defensive
                log.warning("poller iteration failed: %s", exc)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass

    def _fetch(self) -> Optional[list[dict[str, Any]]]:
        # Langfuse timestamps are UTC: the window must be UTC-aware or a
        # non-UTC server shifts it by the local offset (a UTC+9 box would
        # query a window starting in the future and show an empty floor).
        since = datetime.now(timezone.utc) - timedelta(seconds=self.window)
        try:
            runs = list_recent_runs(self.source, since=since, limit=self.limit)
        except Exception as exc:
            log.warning("langfuse fetch failed: %s", exc)
            # V-4: return None = "no fresh data" (keep last good snapshot).
            return None
        now = time.monotonic()
        out: list[dict[str, Any]] = []
        full_runs: list[PipelineRun] = []
        current_ids: set[str] = set()
        prev_by_id = {r.trace_id: r for r in self.runs if r.trace_id}
        for run in runs:
            if not run.trace_id:
                continue
            current_ids.add(run.trace_id)
            cached = self._details.get(run.trace_id)
            payload = None
            chosen: PipelineRun = run
            if cached is not None and now - cached[0] < self.detail_ttl:
                payload = cached[1]
                chosen = prev_by_id.get(run.trace_id) or run
            else:
                try:
                    full = self.source.get_run(run.trace_id)
                except Exception:
                    full = None
                chosen = full if full is not None else run
                payload = floor_payload(chosen)
                self._details[run.trace_id] = (now, payload)
            full_runs.append(chosen)
            out.append(payload)
        for tid in list(self._details):
            if tid not in current_ids:
                del self._details[tid]
        self.runs = full_runs
        return out

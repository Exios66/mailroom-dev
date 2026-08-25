"""The-Mailroom TUI console — AgentLab-style live view of the pipeline.

Reads the same display API the web UI serves (`/api/*` on the running
server, `MAILROOM_API_URL`), so every value is still Langfuse-derived.
Views:

- FLOOR    — live per-run table with `*** Beginning station: ... ***`
            banners when runs arrive or advance
- REVIEW   — runs waiting on a human, with escalation reasons
- METRICS  — aggregate dashboard
- INSPECT  — drill into one trace: spans, generations, scores

Keys: f floor · r review · m metrics · i inspect <id> · c clear log · q quit
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import select
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from typing import Any, Optional

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

API_BASE = os.environ.get("MAILROOM_API_URL", "http://127.0.0.1:8001").rstrip("/")
POLL_INTERVAL = float(os.environ.get("MAILROOM_TUI_POLL", "5"))

STAGE_ORDER = [
    "inbox", "ingest", "classify", "retry_classify",
    "extract", "retry_extract", "judge_verify", "arbiter",
    "boss", "review", "report", "catalog", "archive", "archived", "failed",
]

STAGE_STYLE = {
    "inbox": "grey50", "ingest": "grey70", "classify": "cyan",
    "retry_classify": "cyan", "extract": "yellow", "retry_extract": "yellow",
    "judge_verify": "magenta", "arbiter": "magenta",
    "boss": "red", "review": "bright_yellow", "report": "green",
    "catalog": "green", "archive": "green", "archived": "bright_green",
    "failed": "bright_red", "unknown": "grey50",
}

STATION_BY_STAGE = {
    "inbox": "INBOX", "ingest": "Sorter", "classify": "Sorter",
    "retry_classify": "Sorter", "extract": "Specialist", "retry_extract": "Specialist",
    "judge_verify": "Judge", "arbiter": "Arbiter",
    "boss": "Boss", "review": "Review siding", "report": "Reporter",
    "catalog": "Archivist", "archive": "Archivist", "archived": "Archive",
    "failed": "Failed bin", "unknown": "?",
}


def fetch(path: str, timeout: float = 15.0) -> Optional[dict]:
    try:
        with urllib.request.urlopen(f"{API_BASE}{path}", timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def fetch_list(path: str) -> list[dict]:
    data = fetch(path)
    if data is None:
        return []
    return data.get("runs") or []


def fetch_snapshot() -> Optional[list[dict]]:
    """Full floor payloads via the same WebSocket snapshots the web floor
    uses (verdicts, cost, routing — everything). Falls back to the light
    HTTP list when WS is unavailable."""
    try:
        import asyncio

        from websockets.sync.client import connect

        ws_url = API_BASE.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
        with connect(ws_url, open_timeout=8) as ws:
            msg = json.loads(ws.recv(timeout=8))
        if isinstance(msg, dict) and msg.get("type") == "snapshot":
            return msg.get("runs") or []
        return None
    except Exception:
        return None


def fetch_floor_runs() -> Optional[list[dict]]:
    snap = fetch_snapshot()
    if snap:
        return snap
    return fetch_list("/api/traces?since=21600")


def banner(station: str, action: str = "Beginning") -> str:
    return f"*** {action} station: {station} ***"


def _fmt(v, spec="{:.2f}") -> str:
    if v is None:
        return "-"
    try:
        return spec.format(float(v))
    except (TypeError, ValueError):
        return str(v)


def runs_to_banners(prev: dict[str, dict], runs: list[dict], log: deque) -> None:
    """Emit AgentLab-style banners when runs arrive or advance stages."""
    now = {r["trace_id"]: r for r in runs}
    for tid, run in now.items():
        old = prev.get(tid)
        if old is None:
            log.append(f"{banner(STATION_BY_STAGE.get(run['stage'], '?'), 'Entering')} "
                       f"{run.get('filename') or tid} [{run.get('stage')}]")
        elif old.get("stage") != run.get("stage"):
            log.append(f"{banner(STATION_BY_STAGE.get(run['stage'], '?'), 'Moving to')} "
                       f"{run.get('filename') or tid} [{run.get('stage')}]")
        if run.get("verdict") and old and old.get("verdict") != run.get("verdict"):
            log.append(f"*** Judge verdict: {run['verdict']} — {run.get('filename')} ***")
    gone = set(prev) - set(now)
    for tid in sorted(gone):
        log.append(f"*** Run left the window: {tid} ***")


def floor_table(runs: list[dict]) -> Table:
    table = Table(title=None, box=None, pad_edge=False, expand=True)
    table.add_column("FILE", style="bold white", no_wrap=True, max_width=34)
    table.add_column("STATION", style="grey70")
    table.add_column("DOC TYPE", style="dim")
    table.add_column("CLS", justify="right")
    table.add_column("EXT", justify="right")
    table.add_column("VERDICT", justify="center", no_wrap=True, min_width=7)
    table.add_column("QUAL", justify="right")
    table.add_column("COST", justify="right", no_wrap=True)
    table.add_column("ROUTE", style="grey35", max_width=30)
    ordered = sorted(runs, key=lambda r: (STAGE_ORDER.index(r.get("stage"))
                                          if r.get("stage") in STAGE_ORDER else 99))
    for r in ordered:
        verdict = r.get("verdict") or "-"
        style = "bright_green" if verdict == "CORRECT" else (
            "yellow" if verdict == "PARTIAL" else "bright_red" if verdict == "MISS" else "dim")
        route = ">".join((r.get("routing_path") or [])[:5])
        table.add_row(
            (r.get("filename") or r["trace_id"])[:34],
            STATION_BY_STAGE.get(r.get("stage"), "?"),
            (r.get("doc_type") or "-").replace("_", " "),
            _fmt(r.get("classification_confidence")),
            _fmt(r.get("extraction_confidence")),
            Text(verdict, style=style),
            _fmt(r.get("quality")),
            "$" + _fmt(r.get("cost_usd"), "{:.4f}"),
            route,
        )
    return table


def review_table(runs: list[dict]) -> Table:
    table = Table(title="REVIEW SIDING — WAITING ON A HUMAN", box=None, pad_edge=False, expand=True)
    table.add_column("FILE", style="bold white", no_wrap=True, max_width=34)
    table.add_column("DOC TYPE", style="dim")
    table.add_column("CLS", justify="right")
    table.add_column("EXT", justify="right")
    table.add_column("WHY", style="yellow", max_width=60)
    for r in runs:
        table.add_row(
            (r.get("filename") or r["trace_id"])[:34],
            (r.get("doc_type") or "-").replace("_", " "),
            _fmt(r.get("classification_confidence")),
            _fmt(r.get("extraction_confidence")),
            r.get("escalation_reason") or r.get("error_message") or "-",
        )
    return table


def metrics_table(m: dict) -> Table:
    table = Table(title="METRICS", box=None, pad_edge=False, expand=True)
    table.add_column("METRIC", style="bold")
    table.add_column("VALUE", justify="right")
    rows = [
        ("total docs", m.get("total_docs")),
        ("archived", m.get("archived")),
        ("review", m.get("review")),
        ("failed", m.get("failed")),
        ("in flight", m.get("in_flight")),
        ("llm calls", m.get("llm_calls")),
        ("total cost", f"${m.get('total_cost_usd', 0):.2f}"),
        ("total tokens", m.get("total_tokens")),
        ("avg cost/doc", f"${m.get('avg_cost_usd', 0):.4f}"),
        ("avg latency", f"{m.get('avg_latency_s', 0):.1f}s"),
        ("p95 gen latency", f"{m.get('p95_generation_latency_s', 0):.1f}s"),
        ("avg quality", "-" if m.get("avg_quality") is None else f"{m['avg_quality']:.2f}"),
    ]
    for name, value in rows:
        table.add_row(name, str(value))
    verdicts = m.get("verdict_counts") or {}
    if verdicts:
        table.add_section()
        for k, v in sorted(verdicts.items()):
            table.add_row(f"verdict {k}", str(v))
    return table


def inspect_panels(run: dict) -> list[Panel]:
    title = run.get("filename") or run.get("trace_id") or "run"
    head = Text()
    head.append(f"{title}\n", style="bold white")
    head.append(f"trace {run.get('trace_id')} · {run.get('stage')} · "
                f"{run.get('doc_type') or 'no doc type'} · env {run.get('environment') or '-'}\n",
                style="grey50")
    if run.get("verdict"):
        head.append(f"verdict {run['verdict']} · quality {_fmt(run.get('quality'))}\n", style="bold")
    kv = Table(box=None, pad_edge=False)
    kv.add_column("FIELD", style="dim")
    kv.add_column("VALUE")
    for key in ("session_id", "matter_id", "attempt", "environment",
                "classification_confidence", "extraction_confidence", "latency",
                "llm_call_count", "total_tokens", "cost_usd", "created_at",
                "escalation_reason", "error_message"):
        value = run.get(key)
        if value is not None:
            kv.add_row(key, str(value))
    panels = [Panel(Group(head, kv), title="RUN", border_style="blue")]

    spans = run.get("spans") or []
    st = Table(box=None, pad_edge=False)
    st.add_column("SPAN", style="bold")
    st.add_column("STATUS")
    st.add_column("LATENCY", justify="right")
    st.add_column("ERROR", style="red", max_width=40)
    for s in spans:
        status = s.get("status") or "?"
        style = "bright_green" if status == "SUCCESS" else (
            "bright_red" if status == "ERROR" else "yellow")
        st.add_row(s.get("name") or "?", Text(status, style=style),
                   _fmt(s.get("latency"), "{:.1f}s"),
                   (s.get("error_message") or "")[:40])
    panels.append(Panel(st, title=f"NODE SPANS ({len(spans)})", border_style="blue"))

    gens = run.get("generations") or []
    gt = Table(box=None, pad_edge=False)
    gt.add_column("CALL", style="bold")
    gt.add_column("MODEL")
    gt.add_column("TOKENS IN", justify="right")
    gt.add_column("OUT", justify="right")
    gt.add_column("COST", justify="right")
    gt.add_column("LATENCY", justify="right")
    for g in gens:
        gt.add_row(g.get("name") or "-", g.get("model") or "-",
                   str(g.get("usage_input_tokens") or 0),
                   str(g.get("usage_output_tokens") or 0),
                   f"${g.get('cost_usd') or 0:.4f}",
                   _fmt(g.get("latency"), "{:.1f}s"))
    panels.append(Panel(gt, title=f"LLM GENERATIONS ({len(gens)})", border_style="blue"))

    scores = run.get("scores") or {}
    if scores:
        sct = Table(box=None, pad_edge=False)
        sct.add_column("SCORE", style="bold")
        sct.add_column("VALUE")
        for name, value in sorted(scores.items()):
            sct.add_row(name, str(value))
        panels.append(Panel(sct, title="SCORES", border_style="blue"))
    return panels


def _key_reader(keys: "queue.Queue[str]") -> None:
    """Raw single-key reader (POSIX). Falls back to line input when the
    terminal is not usable."""
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            while True:
                if select.select([sys.stdin], [], [], 0.2)[0]:
                    keys.put(sys.stdin.read(1))
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        while True:
            keys.put(sys.stdin.readline())


def render_floor(runs: list[dict], log: deque) -> Group:
    empty = not runs
    body = floor_table(runs)
    if empty:
        body = Align.center(Text("MAILROOM STANDING BY — no runs in the window", style="grey50"))
    lines = list(log)[-14:]
    log_panel = Panel(Group(*[Text(line, style="bright_cyan" if "***" in line else "grey70")
                              for line in lines]),
                      title=f"LIVE LOG ({len(log)})", border_style="grey35")
    return Group(body, log_panel)


def status_header(connected: bool, count: int) -> Panel:
    state = "MAILROOM LIVE — watching Langfuse" if connected else \
        "MAILROOM CLOSED — no Langfuse connection"
    style = "bright_green" if connected else "bright_red"
    return Panel(Text(f"THE MAILROOM TUI   {state}   runs: {count}   "
                      f"source: {API_BASE}", style=style),
                 border_style=style)


def run() -> None:
    global API_BASE, POLL_INTERVAL
    parser = argparse.ArgumentParser(description="The-Mailroom TUI console.")
    parser.add_argument("--api", default=API_BASE, help="The-Mailroom server base URL")
    parser.add_argument("--poll", type=float, default=POLL_INTERVAL, help="refresh seconds")
    parser.add_argument("--once", action="store_true",
                        help="render a single frame and exit (scripting/CI)")
    args = parser.parse_args()
    API_BASE = args.api.rstrip("/")
    POLL_INTERVAL = args.poll

    console = Console()
    if args.once:
        runs = fetch_floor_runs()
        log: deque[str] = deque()
        if runs is not None:
            runs_to_banners({}, runs, log)
            console.print(status_header(True, len(runs)))
            console.print(render_floor(runs, log))
        else:
            console.print(status_header(False, 0))
            console.print(Panel(Text("no Langfuse connection", style="bright_red")))
        return
    keys: "queue.Queue[str]" = queue.Queue()
    threading.Thread(target=_key_reader, args=(keys,), daemon=True).start()

    view = "floor"
    log: deque[str] = deque(maxlen=200)
    prev: dict[str, dict] = {}
    runs: list[dict] = []
    closed = False

    with Live(console=console, screen=False, refresh_per_second=4, auto_refresh=False) as live:
        last_poll = 0.0
        while True:
            now = time.monotonic()
            if now - last_poll >= POLL_INTERVAL:
                last_poll = now
                fresh = fetch_floor_runs()
                if fresh is None:
                    closed = True
                else:
                    closed = False
                    runs = fresh
                    runs_to_banners(prev, runs, log)
                    prev = {r["trace_id"]: r for r in runs}

            try:
                ch = keys.get_nowait()
            except queue.Empty:
                ch = None
            if ch:
                if ch in ("q", "Q"):
                    break
                if ch in ("f", "F"):
                    view = "floor"
                elif ch in ("r", "R"):
                    view = "review"
                elif ch in ("m", "M"):
                    view = "metrics"
                elif ch in ("c", "C"):
                    log.clear()
                elif ch in ("i", "I"):
                    view = "inspect"

            if view == "floor":
                body = render_floor(runs, log)
            elif view == "review":
                body = review_table(fetch_list("/api/review-queue"))
            elif view == "metrics":
                m = fetch("/api/metrics?since=21600") or {}
                body = metrics_table(m)
            elif view == "inspect":
                tid = console.input("trace id: ")
                detail = fetch(f"/api/traces/{tid.strip()}")
                if detail is None or detail.get("error"):
                    body = Panel(Text(f"trace {tid} unavailable", style="bright_red"))
                else:
                    body = Group(*inspect_panels(detail))
                view = "floor"

            live.update(
                Group(
                    status_header(not closed, len(runs)),
                    body,
                    Text("  [f]loor  [r]eview  [m]etrics  [i]nspect  [c]lear  [q]uit",
                         style="grey35"),
                )
            )
            live.refresh()
            time.sleep(0.1)
    console.print("\nmailroom-tui closed.")


if __name__ == "__main__":
    run()

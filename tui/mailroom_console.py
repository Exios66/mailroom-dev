"""The-Mailroom TUI console — AgentLab-style live view of the pipeline.

Reads the same display API the web UI serves (`/api/*` on the running
server, `MAILROOM_API_URL`), so every value is still Langfuse-derived.
Views:

- FLOOR    — live per-run table with `*** Beginning station: ... ***`
            banners when runs arrive or advance
- REVIEW   — runs waiting on a human, with escalation reasons
- SESSIONS — Langfuse matters
- METRICS  — aggregate dashboard
- INSPECT  — drill into one trace: spans, generations, scores (`[` / `]` cycle)
- DEBUG    — last fetch/WS errors plus a pull of `/api/debug/bundle`

Keys: f floor · r review · s sessions · m metrics · i inspect · [ ] cycle
      d debug · c clear log · q quit
`--once --view floor|review|metrics|sessions|inspect|debug` for scripting.
`--resolve TRACE --decision approved|rejected --disposition resume|record|requeue --notes "..."`
posts through the visualizer (`MAILROOM_API_URL`, default :8001) to the producer.
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
POLL_INTERVAL = float(os.environ.get("MAILROOM_TUI_POLL", "3"))
# Same 7-day live window as the pixel console and Observatory HTTP clients.
WINDOW_S = int(os.environ.get("MAILROOM_RECENT_WINDOW", "604800"))
LAST_ERRORS: deque[str] = deque(maxlen=80)

STAGE_ORDER = [
    "inbox", "ingest", "classify", "retry_classify", "review_classify",
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
    "retry_classify": "Sorter", "review_classify": "Sorter",
    "extract": "Specialist", "retry_extract": "Specialist",
    "judge_verify": "Judge", "arbiter": "Arbiter",
    "boss": "Boss", "review": "Review", "report": "Reporter",
    "catalog": "Archive", "archive": "Archive", "archived": "Archive",
    "failed": "Failed", "unknown": "?",
}


def _record_error(where: str, exc: BaseException) -> None:
    LAST_ERRORS.append(f"{where}: {type(exc).__name__}: {exc}")


def fetch(path: str, timeout: float = 15.0) -> Optional[dict]:
    url = f"{API_BASE}{path}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        _record_error(f"GET {path}", exc)
        try:
            LAST_ERRORS.append(f"GET {path} body: {exc.read().decode()[:300]}")
        except Exception:
            pass
        return None
    except Exception as exc:
        _record_error(f"GET {path}", exc)
        return None


def fetch_list(path: str) -> Optional[list[dict]]:
    """None = request failed (closed). [] = source reachable but empty."""
    data = fetch(path)
    if data is None:
        return None
    return data.get("runs") or []


def post_json(path: str, body: dict, timeout: float = 60.0) -> Optional[dict]:
    """POST JSON to the visualizer (review resolve). None on failure."""
    url = f"{API_BASE}{path}"
    payload = json.dumps(body).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        _record_error(f"POST {path}", exc)
        try:
            LAST_ERRORS.append(f"POST {path} body: {exc.read().decode()[:400]}")
        except Exception:
            pass
        return None
    except Exception as exc:
        _record_error(f"POST {path}", exc)
        return None


def fetch_snapshot() -> Optional[list[dict]]:
    """Full floor payloads via the same WebSocket snapshots the web floor
    uses. None = WS failed (caller should try HTTP)."""
    try:
        from websockets.sync.client import connect

        ws_url = API_BASE.replace("https://", "wss://").replace("http://", "ws://") + "/ws"
        with connect(ws_url, open_timeout=8) as ws:
            msg = json.loads(ws.recv(timeout=8))
        if isinstance(msg, dict) and msg.get("type") == "snapshot":
            return msg.get("runs") or []
        LAST_ERRORS.append(f"WS {ws_url}: unexpected frame {type(msg).__name__}")
        return None
    except Exception as exc:
        _record_error("WS /ws", exc)
        return None


def fetch_floor_runs() -> Optional[list[dict]]:
    """None means the display API is unreachable — not an empty window."""
    snap = fetch_snapshot()
    if snap is not None:
        return snap
    return fetch_list(f"/api/traces?since={WINDOW_S}")


def probe_health() -> bool:
    h = fetch("/api/health")
    if h is None:
        return False
    return bool(h.get("ok") if h.get("ok") is not None else h.get("langfuse"))


def banner(station: str, action: str = "Beginning") -> str:
    return f"*** {action} station: {station} ***"


def _fmt(v, spec="{:.2f}") -> str:
    if v is None:
        return "-"
    try:
        return spec.format(float(v))
    except (TypeError, ValueError):
        return str(v)


def _money(v, spec="{:.4f}") -> str:
    if v is None:
        return "-"
    try:
        return "$" + spec.format(float(v))
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
    table.add_column("STATION", style="grey70", no_wrap=True, min_width=10)
    table.add_column("DOC TYPE", style="dim", no_wrap=True, max_width=16)
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
            _money(r.get("cost_usd"), "{:.4f}"),
            route,
        )
    return table


def review_table(runs: list[dict]) -> Table:
    table = Table(
        title="REVIEW SIDING — WAITING ON A HUMAN  (resolve: mailroom-tui --resolve TRACE --decision approved)",
        box=None, pad_edge=False, expand=True,
    )
    table.add_column("FILE", style="bold white", no_wrap=True, max_width=34)
    table.add_column("DOC TYPE", style="dim")
    table.add_column("CLS", justify="right")
    table.add_column("EXT", justify="right")
    table.add_column("VERDICT", justify="center", no_wrap=True, min_width=7)
    table.add_column("WHY", style="yellow", max_width=50)
    for r in runs:
        verdict = r.get("verdict") or "-"
        style = "bright_green" if verdict == "CORRECT" else (
            "yellow" if verdict == "PARTIAL" else "bright_red" if verdict == "MISS" else "dim")
        table.add_row(
            (r.get("filename") or r["trace_id"])[:34],
            (r.get("doc_type") or "-").replace("_", " "),
            _fmt(r.get("classification_confidence")),
            _fmt(r.get("extraction_confidence")),
            Text(verdict, style=style),
            r.get("escalation_reason")
            or (", ".join(r.get("review_causes") or []))
            or r.get("review_decision")
            or r.get("error_message")
            or "-",
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
        ("reconsider", m.get("reconsideration")),
        ("failed", m.get("failed")),
        ("in flight", m.get("in_flight")),
        ("llm calls", m.get("llm_calls")),
        ("total cost", _money(m.get("total_cost_usd"), "{:.2f}")),
        ("total tokens", m.get("total_tokens")),
        ("avg cost/doc", _money(m.get("avg_cost_usd"), "{:.4f}")),
        ("avg latency", "-" if m.get("avg_latency_s") is None else f"{m['avg_latency_s']:.1f}s"),
        ("p95 gen latency", "-" if m.get("p95_generation_latency_s") is None else f"{m['p95_generation_latency_s']:.1f}s"),
        ("avg quality", "-" if m.get("avg_quality") is None else f"{m['avg_quality']:.2f}"),
    ]
    extra_metrics = (
        ("verified precision", "avg_extraction_verified_precision"),
        ("topic accuracy", "avg_content_topic_accuracy"),
        ("topic f1", "avg_content_topic_f1_macro"),
        ("sentiment accuracy", "avg_sentiment_accuracy"),
        ("sentiment f1", "avg_sentiment_f1_macro"),
        ("maud question acc", "avg_maud_question_accuracy"),
        ("maud question macro", "avg_maud_question_macro_accuracy"),
        ("maud clause", "avg_maud_clause_presence"),
        ("maud valid class", "avg_maud_valid_class_rate"),
        ("maud category", "avg_maud_category_accuracy"),
    )
    for label, key in extra_metrics:
        value = m.get(key)
        if value is not None:
            rows.append((label, f"{value:.4f}" if isinstance(value, float) else value))
    for name, value in rows:
        table.add_row(name, "-" if value is None else str(value))
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
                f"{run.get('doc_type') or 'no doc type'}"
                f"{(' / ' + (run.get('doc_subclass') or run.get('contract_subtype'))) if (run.get('doc_subclass') or run.get('contract_subtype')) else ''}"
                f" · env {run.get('environment') or '-'}\n",
                style="grey50")
    if run.get("verdict"):
        head.append(f"verdict {run['verdict']} · quality {_fmt(run.get('quality'))}\n", style="bold")
    kv = Table(box=None, pad_edge=False)
    kv.add_column("FIELD", style="dim")
    kv.add_column("VALUE")
    labels = {
        "doc_id": "DOC ID",
        "doc_subclass": "SUBCLASS",
        "contract_subtype": "CONTRACT SUBTYPE",
        "expected_hf_class": "EXPECTED CLASS",
        "expected_subclass": "EXPECTED SUBCLASS",
        "intake_messy": "INTAKE MESSY",
        "intake_changed": "INTAKE CHANGED",
        "intake_method": "INTAKE METHOD",
        "intake_chars": "INTAKE CHARS",
    }
    for key in ("doc_id", "session_id", "matter_id", "user_id", "release", "attempt", "environment",
                "doc_subclass", "contract_subtype", "expected_hf_class", "expected_subclass",
                "intake_messy", "intake_changed", "intake_method", "intake_chars",
                "classification_confidence", "extraction_confidence", "latency",
                "llm_call_count", "total_tokens", "cost_usd", "created_at",
                "escalation_reason", "error_message"):
        value = run.get(key)
        if value is not None:
            kv.add_row(labels.get(key, key), str(value))
    panels = [Panel(Group(head, kv), title="RUN", border_style="blue")]

    spans = run.get("spans") or []
    st = Table(box=None, pad_edge=False)
    st.add_column("SPAN", style="bold")
    st.add_column("TYPE", style="cyan")
    st.add_column("STATUS")
    st.add_column("LATENCY", justify="right")
    st.add_column("ERROR", style="red", max_width=40)
    for s in spans:
        status = s.get("status") or "?"
        style = "bright_green" if status == "SUCCESS" else (
            "bright_red" if status == "ERROR" else "yellow")
        label = s.get("name") or "?"
        if s.get("is_root"):
            label = f"{label} [root]"
        st.add_row(label, (s.get("observation_type") or "SPAN"),
                   Text(status, style=style),
                   _fmt(s.get("latency"), "{:.1f}s"),
                   (s.get("error_message") or "")[:40])
    panels.append(Panel(st, title=f"OBSERVATIONS ({len(spans)})", border_style="blue"))

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
                   _money(g.get("cost_usd"), "{:.4f}"),
                   _fmt(g.get("latency"), "{:.1f}s"))
    panels.append(Panel(gt, title=f"LLM GENERATIONS ({len(gens)})", border_style="blue"))

    scores = run.get("scores") or {}
    entries: list[tuple[str, Any]] = []
    if isinstance(scores, list):
        for s in scores:
            if isinstance(s, dict) and s.get("name") is not None:
                entries.append((str(s.get("name")), s.get("value")))
    elif isinstance(scores, dict):
        entries = sorted(scores.items())
    if entries:
        sct = Table(box=None, pad_edge=False)
        sct.add_column("SCORE", style="bold")
        sct.add_column("VALUE")
        for name, value in entries:
            sct.add_row(name, str(value))
        panels.append(Panel(sct, title="SCORES", border_style="blue"))
    return panels


def sessions_table(payload: dict) -> Table:
    table = Table(title="MATTERS / SESSIONS", box=None, pad_edge=False, expand=True)
    table.add_column("SESSION", style="bold white", no_wrap=True, max_width=28)
    table.add_column("TRACES", justify="right")
    table.add_column("UPDATED", style="dim")
    table.add_column("LATEST", max_width=50)
    for s in payload.get("sessions") or []:
        latest = ""
        runs = s.get("runs") or []
        if runs:
            r = runs[0]
            latest = f"{(r.get('filename') or r.get('trace_id') or '')[:28]} [{r.get('stage') or '-'}]"
        table.add_row(
            str(s.get("name") or s.get("id") or "matter")[:28],
            str(s.get("trace_count") or len(runs)),
            str(s.get("updated_at") or "-")[:19],
            latest or "-",
        )
    return table


def debug_panel() -> Panel:
    lines = list(LAST_ERRORS)[-18:] or ["(no recorded fetch/WS errors)"]
    body = Group(*[Text(line, style="bright_red" if "Error" in line or "error" in line else "grey70")
                   for line in lines])
    return Panel(body, title=f"TUI DEBUG RING ({len(LAST_ERRORS)}) — also GET /api/debug/bundle",
                 border_style="red")


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


def status_header(connected: bool, count: int, pipeline: Optional[dict] = None) -> Panel:
    state = "MAILROOM LIVE — watching Langfuse" if connected else \
        "MAILROOM CLOSED — no Langfuse connection"
    style = "bright_green" if connected else "bright_red"
    extra = ""
    if pipeline and pipeline.get("configured"):
        extra = (f"   watcher: {pipeline.get('watcher') or '?'} "
                 f"  inbox: {pipeline.get('inbox_pending')}")
        if pipeline.get("watcher") != "live":
            style = "yellow" if connected else style
    return Panel(Text(f"THE MAILROOM TUI   {state}   runs: {count}   "
                      f"source: {API_BASE}{extra}", style=style),
                 border_style=style)


def run() -> None:
    global API_BASE, POLL_INTERVAL
    parser = argparse.ArgumentParser(description="The-Mailroom TUI console.")
    parser.add_argument("--api", default=API_BASE, help="The-Mailroom server base URL")
    parser.add_argument("--poll", type=float, default=POLL_INTERVAL, help="refresh seconds")
    parser.add_argument("--once", action="store_true",
                        help="render a single frame and exit (scripting/CI)")
    parser.add_argument("--view", default="floor",
                        choices=["floor", "review", "metrics", "sessions", "inspect", "debug"],
                        help="which desk --once (and the live start view) shows")
    parser.add_argument("--inspect", default="",
                        help="trace id to open on the inspect desk")
    parser.add_argument("--resolve", default="",
                        help="trace id (or producer doc_id) to resolve via POST /api/review/resolve")
    parser.add_argument("--decision", default="approved",
                        choices=["approved", "rejected"],
                        help="review decision used with --resolve")
    parser.add_argument("--disposition", default="resume",
                        choices=["resume", "record", "requeue"],
                        help="resume pipeline, record-only audit, or requeue to inbox")
    parser.add_argument("--notes", default="",
                        help="reviewer notes stored on the producer audit chain")
    args = parser.parse_args()
    API_BASE = args.api.rstrip("/")
    POLL_INTERVAL = args.poll
    console = Console()

    if args.resolve:
        ident = args.resolve.strip()
        body: dict[str, Any] = {
            "decision": args.decision,
            "disposition": args.disposition,
            "notes": args.notes,
        }
        if "." in ident and "/" not in ident:
            body["filename"] = ident
        else:
            body["trace_id"] = ident
            body["doc_id"] = ident
        result = post_json("/api/review/resolve", body)
        if result is None:
            console.print(Panel(Text("review resolve failed — see LAST_ERRORS / [d]ebug", style="bright_red")))
            for line in LAST_ERRORS:
                console.print(Text(line, style="red"))
            raise SystemExit(1)
        console.print(Panel(Text(json.dumps(result, indent=2), style="green"), title="REVIEW RESOLVE"))
        return

    def frame_for(view: str, runs: list[dict], log: deque, inspect_id: str = "") -> Any:
        if view == "floor":
            return render_floor(runs, log)
        if view == "review":
            rev = fetch_list(f"/api/review-queue?since={WINDOW_S}")
            if rev is None:
                return Panel(Text("review queue unavailable — see [d]ebug", style="bright_red"))
            return review_table(rev)
        if view == "metrics":
            m = fetch(f"/api/metrics?since={WINDOW_S}")
            if m is None:
                return Panel(Text("metrics unavailable — see [d]ebug", style="bright_red"))
            return metrics_table(m)
        if view == "sessions":
            payload = fetch("/api/sessions?limit=50")
            if payload is None:
                return Panel(Text("sessions unavailable — see [d]ebug", style="bright_red"))
            return sessions_table(payload)
        if view == "debug":
            return debug_panel()
        if view == "inspect":
            tid = inspect_id
            if not tid and runs:
                tid = runs[0].get("trace_id") or ""
            if not tid:
                return Panel(Text("no trace to inspect", style="yellow"))
            detail = fetch(f"/api/traces/{tid}")
            if detail is None or detail.get("error"):
                return Panel(Text(f"trace {tid} unavailable — see [d]ebug", style="bright_red"))
            return Group(*inspect_panels(detail))
        return render_floor(runs, log)

    if args.once:
        runs = fetch_floor_runs()
        log: deque[str] = deque()
        if args.view == "debug":
            bundle = fetch("/api/debug/bundle")
            if bundle:
                LAST_ERRORS.append(
                    f"bundle health={bundle.get('health')} "
                    f"logs={len(bundle.get('server_logs') or [])} "
                    f"client_reports={len(bundle.get('client_reports') or [])}"
                )
        if runs is not None:
            runs_to_banners({}, runs, log)
            pipe = fetch("/api/pipeline") or {}
            console.print(status_header(True, len(runs), pipe))
            console.print(frame_for(args.view, runs, log, args.inspect))
        else:
            console.print(status_header(False, 0))
            console.print(Panel(Text("no Langfuse connection", style="bright_red")))
            if LAST_ERRORS:
                console.print(debug_panel())
        return
    keys: "queue.Queue[str]" = queue.Queue()
    threading.Thread(target=_key_reader, args=(keys,), daemon=True).start()

    view = args.view
    log = deque(maxlen=200)
    prev: dict[str, dict] = {}
    runs = []
    closed = False
    inspect_idx = 0
    inspect_cache: Optional[dict] = None
    pipeline_ops: dict = {}

    with Live(console=console, screen=False, refresh_per_second=4, auto_refresh=False) as live:
        last_poll = 0.0
        while True:
            now = time.monotonic()
            if now - last_poll >= POLL_INTERVAL:
                last_poll = now
                fresh = fetch_floor_runs()
                if fresh is None:
                    closed = True
                    if not probe_health():
                        closed = True
                else:
                    closed = False
                    runs = fresh
                    runs_to_banners(prev, runs, log)
                    prev = {r["trace_id"]: r for r in runs}
                    pipeline_ops = fetch("/api/pipeline") or {}

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
                elif ch in ("s", "S"):
                    view = "sessions"
                elif ch in ("d", "D"):
                    view = "debug"
                    bundle = fetch("/api/debug/bundle")
                    if bundle:
                        LAST_ERRORS.append(
                            f"bundle health={bundle.get('health')} "
                            f"logs={len(bundle.get('server_logs') or [])} "
                            f"client_reports={len(bundle.get('client_reports') or [])}"
                        )
                elif ch in ("c", "C"):
                    log.clear()
                elif ch in ("i", "I"):
                    view = "inspect"
                    inspect_cache = None
                elif ch == "[" and view == "inspect" and runs:
                    inspect_idx = max(0, inspect_idx - 1)
                    inspect_cache = None
                elif ch == "]" and view == "inspect" and runs:
                    inspect_idx = min(len(runs) - 1, inspect_idx + 1)
                    inspect_cache = None

            if view == "inspect":
                if not runs:
                    body = Panel(Text("no runs in the window to inspect", style="yellow"))
                else:
                    inspect_idx = min(inspect_idx, len(runs) - 1)
                    tid = runs[inspect_idx]["trace_id"]
                    if inspect_cache is None or inspect_cache.get("trace_id") != tid:
                        inspect_cache = fetch(f"/api/traces/{tid}")
                    if inspect_cache is None or inspect_cache.get("error"):
                        body = Panel(Text(f"trace {tid} unavailable — see [d]ebug", style="bright_red"))
                    else:
                        body = Group(*inspect_panels(inspect_cache))
            else:
                body = frame_for(view, runs, log, args.inspect)

            live.update(
                Group(
                    status_header(not closed, len(runs), pipeline_ops),
                    body,
                    Text("  [f]loor  [r]eview  [s]essions  [m]etrics  [i]nspect  [[]/[]]  [d]ebug  [c]lear  [q]uit",
                         style="grey35"),
                )
            )
            live.refresh()
            time.sleep(0.1)
    console.print("\nmailroom-tui closed.")


if __name__ == "__main__":
    run()

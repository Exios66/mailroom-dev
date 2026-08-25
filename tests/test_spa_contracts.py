"""Source-level contracts for the vanilla SPA.

There is no JS test harness (see AGENTS.md). These assertions lock the
exact bugs that blanked REVIEW / GH Pages / the floor animation so they
cannot silently regress.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = (ROOT / "web" / "js" / "api.js").read_text()
MAIN = (ROOT / "web" / "js" / "main.js").read_text()
FLOOR = (ROOT / "web" / "js" / "floor.js").read_text()
INDEX = (ROOT / "web" / "index.html").read_text()


def test_review_queue_dispatch_uses_object_key():
    """REVIEW tab called dispatch('review-queue') but remote/snapshots
    are keyed reviewQueue — TypeError on every refresh, live and Pages."""
    assert 'reviewQueue: (...a) => dispatch("reviewQueue", ...a)' in API
    assert "since = 604800" in API
    assert 'get(`/api/traces?since=${since}&limit=${limit}`)' in API
    assert "pullServer" in API and "pushClient" in API
    assert 'url("/api/debug/bundle")' in API
    assert 'dispatch("review-queue"' not in API


def test_snapshot_fetches_are_same_origin_not_api_base():
    """A persisted ?api= pointing at a dead host used to prefix data/*.json
    and blank the GH Pages fallback (often as http://host:8001data/meta.json)."""
    assert "const snapUrl =" in API
    assert 'fetch(url("data/meta.json")' not in API
    assert "fetch(url(`data/${name}.json`)" not in API
    assert "snapUrl(`data/${name}.json`)" in API
    assert 'snapUrl("data/meta.json")' in API


def test_empty_api_query_clears_persisted_base():
    assert "if (qs.has(\"api\"))" in API
    assert 'localStorage.setItem("mailroom.api", BASE)' in API


def test_run_detail_uses_export_safe_id():
    assert "safeId(id)" in API
    assert "return snap(`runs/${safeId(id)}`)" in API
    assert "encodeURIComponent(id)" in API  # live /api/traces/{id} still encodes


def test_boot_does_not_fetch_meta_before_health():
    """Pages has no /api/meta — a boot-time meta() painted ERROR — HTTP 404
    across the status bar on every visit."""
    assert "Mailroom.api.meta()" not in MAIN.split("function boot()")[1]
    assert "async function loadMeta()" in MAIN
    assert "await loadMeta()" in MAIN


def test_floor_uses_week_window_and_demo_is_opt_in():
    assert "traces(604800, 200)" in MAIN
    assert "since = 604800" in API
    # Bare D must not fabricate envelopes on a live floor.
    before = MAIN.split("Demo envelopes")[0]
    assert 'if (ev.key === "d" || ev.key === "D")' not in before


def test_floor_frame_does_not_self_schedule():
    """Leftover requestAnimationFrame(frame) defeated the V-17 idle pause
    and ran a second 60fps chain on top of loop()."""
    assert "requestAnimationFrame(frame)" not in FLOOR
    assert "requestAnimationFrame(loop)" in FLOOR


def test_archive_station_is_a_real_target():
    """catalog/archive stages used to park on REPORT; ARCHIVE was decorative."""
    assert "STATIONS[5].x" in FLOOR
    assert 'st === "catalog" || st === "archive"' in FLOOR
    assert "catalog: 5, archive: 5, archived: 5" in FLOOR


def test_error_banner_is_outside_overflow_hidden_screen():
    screen_close = INDEX.find('id="error-banner"')
    bezel_close = INDEX.find("</div>\n<div id=\"error-banner\"")
    assert bezel_close != -1
    assert screen_close > INDEX.find('class="screen"')


def test_favicon_is_inline_to_avoid_pages_404():
    assert 'rel="icon"' in INDEX
    assert "data:image/svg+xml" in INDEX


def test_desk_tabs_show_loading_placeholder():
    """SESSIONS / REVIEW / METRICS / HISTORY used to stay blank while a
    2-minute Langfuse enrich ran, so verification looked like empty desks."""
    review = (ROOT / "web" / "js" / "review.js").read_text()
    sessions = (ROOT / "web" / "js" / "sessions.js").read_text()
    metrics = (ROOT / "web" / "js" / "metrics.js").read_text()
    history = (ROOT / "web" / "js" / "history.js").read_text()
    assert "LOADING REVIEW QUEUE FROM LANGFUSE" in review
    assert "LOADING SESSIONS FROM LANGFUSE" in sessions
    assert "LOADING METRICS FROM LANGFUSE" in metrics
    assert "LOADING RUN HISTORY FROM LANGFUSE" in history

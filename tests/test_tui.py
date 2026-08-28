"""TUI console tests: banner/table building from payloads (no live server)."""

from collections import deque

from rich.console import Console

from tui.mailroom_console import (
    LAST_ERRORS,
    STATION_BY_STAGE,
    WINDOW_S,
    banner,
    debug_panel,
    fetch_floor_runs,
    fetch_list,
    floor_table,
    inspect_panels,
    metrics_table,
    post_json,
    review_table,
    runs_to_banners,
    sessions_table,
)

RUN = {
    "trace_id": "demo-x",
    "filename": "contract_03_service_agreement.pdf",
    "stage": "archived",
    "doc_type": "contract",
    "classification_confidence": 0.98,
    "extraction_confidence": 0.96,
    "verdict": "CORRECT",
    "quality": 0.97,
    "cost_usd": 0.0496,
    "routing_path": ["ingest", "classify", "extract", "report", "catalog", "archive"],
}


def render(renderable) -> str:
    console = Console(width=120, force_terminal=True, record=True)
    console.print(renderable)
    return console.export_text()


def test_banner_format():
    assert banner("Sorter") == "*** Beginning station: Sorter ***"
    assert banner("Review siding", "Moving to") == "*** Moving to station: Review siding ***"


def test_runs_to_banners_arrival_and_advance():
    log = deque()
    runs_to_banners({}, [RUN], log)
    assert any("Entering station: Archive" in line for line in log)

    advanced = dict(RUN, stage="review", verdict="PARTIAL")
    runs_to_banners({RUN["trace_id"]: RUN}, [advanced], log)
    assert any("Moving to station: Review" in line for line in log)
    assert any("Judge verdict: PARTIAL" in line for line in log)


def test_floor_table_renders():
    table = floor_table([RUN])
    text = render(table)
    assert "contract_03_service_agreement.pdf" in text
    assert "CORRECT" in text
    assert "$0.0496" in text


def test_review_table_shows_reconsider_causes():
    table = review_table([
        dict(
            RUN,
            stage="archived",
            needs_human=True,
            needs_reconsideration=True,
            review_causes=["judge_miss"],
            escalation_reason="reconsider: judge verdict MISS",
        )
    ])
    text = render(table)
    assert "reconsider:" in text
    assert "MISS" in text
    assert "mailroom-tui --resolve" in text


def test_tui_resolve_flags_include_class_and_source():
    from pathlib import Path

    src = (Path(__file__).resolve().parent.parent / "tui" / "mailroom_console.py").read_text()
    assert "--doc-type" in src
    assert "--doc-subclass" in src
    assert 'help="print parked document text via GET /api/review/source"' in src
    assert "doc_type" in src and "doc_subclass" in src



def test_metrics_table_renders():
    table = metrics_table({"total_docs": 10, "verdict_counts": {"CORRECT": 3, "PARTIAL": 1}})
    text = render(table)
    assert "10" in text
    assert "verdict CORRECT" in text


def test_inspect_panels_build():
    run = dict(
        RUN,
        spans=[{"name": "ingest-document", "status": "SUCCESS", "latency": 3.2,
                "observation_type": "SPAN"},
               {"name": "classify-document", "status": "SUCCESS", "latency": 4.1,
                "observation_type": "AGENT"},
               {"name": "judge-verify", "status": "SUCCESS", "latency": 1.0,
                "observation_type": "EVALUATOR"}],
        generations=[{"name": "classify-document", "model": "gpt-4o-mini",
                      "usage_input_tokens": 400, "usage_output_tokens": 700,
                      "cost_usd": 0.0005, "latency": 6.1}],
        scores={"mailroom-pipeline-judge": "CORRECT"},
    )
    panels = inspect_panels(run)
    assert len(panels) == 4
    text = "\n".join(render(p) for p in panels)
    assert "ingest-document" in text
    assert "AGENT" in text
    assert "EVALUATOR" in text
    assert "OBSERVATIONS" in text
    assert "gpt-4o-mini" in text
    assert "mailroom-pipeline-judge" in text


def test_inspect_panels_show_subclass_and_intake():
    run = dict(
        RUN,
        doc_subclass="license",
        expected_subclass="license",
        intake_messy=True,
        intake_changed=True,
        intake_method="deterministic",
        intake_chars=120,
        scores={"maud_question_accuracy": 0.8},
    )
    text = "\n".join(render(p) for p in inspect_panels(run))
    assert "SUBCLASS" in text
    assert "license" in text
    assert "INTAKE MESSY" in text
    assert "deterministic" in text


def test_inspect_panels_show_doc_id():
    text = "\n".join(render(p) for p in inspect_panels(dict(RUN, doc_id="doc-abc")))
    assert "DOC ID" in text
    assert "doc-abc" in text


def test_post_json_is_exported():
    assert callable(post_json)


def test_station_map_covers_stages():
    for stage in ("ingest", "classify", "retry_classify", "review_classify",
                  "extract", "judge_verify", "arbiter", "boss", "review",
                  "report", "catalog", "archive", "archived", "failed"):
        assert stage in STATION_BY_STAGE


def test_metrics_table_survives_null_cost():
    table = metrics_table({"total_docs": 0, "total_cost_usd": None, "avg_latency_s": None})
    text = render(table)
    assert "total docs" in text
    assert "None" not in text


def test_inspect_panels_accept_score_list():
    run = dict(
        RUN,
        scores=[{"name": "mailroom-pipeline-judge", "value": "CORRECT"}],
    )
    text = "\n".join(render(p) for p in inspect_panels(run))
    assert "mailroom-pipeline-judge" in text


def test_sessions_table_renders():
    table = sessions_table({
        "sessions": [{
            "id": "MATTER-001",
            "name": "MATTER-001",
            "trace_count": 1,
            "updated_at": "2026-08-25T01:00:00",
            "runs": [RUN],
        }],
    })
    assert "MATTER-001" in render(table)


def test_fetch_floor_runs_none_means_closed(monkeypatch):
    monkeypatch.setattr("tui.mailroom_console.fetch_snapshot", lambda: None)
    monkeypatch.setattr("tui.mailroom_console.fetch_list", lambda path: None)
    assert fetch_floor_runs() is None


def test_fetch_list_empty_is_not_closed(monkeypatch):
    monkeypatch.setattr("tui.mailroom_console.fetch", lambda path, timeout=15.0: {"runs": []})
    assert fetch_list("/api/traces") == []


def test_debug_panel_shows_ring():
    LAST_ERRORS.clear()
    LAST_ERRORS.append("GET /api/health: URLError: connection refused")
    assert "connection refused" in render(debug_panel())


def test_live_window_matches_web_clients():
    assert WINDOW_S == 604800

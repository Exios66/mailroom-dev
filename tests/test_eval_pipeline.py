"""Intake normalize mirror + pipeline eval scorer contract."""

from mailroom_ui.intake_normalize import deterministic_normalize, looks_messy
from mailroom_ui.pipeline_eval import aligned, classify_failure, score_rows


def test_normalize_collapses_and_unwraps():
    cleaned, stats = deterministic_normalize("A\u00a0B\n\n\n\nagree-\nment")
    assert "A B" in cleaned
    assert "agreement" in cleaned
    assert stats["changed"] is True
    assert looks_messy("x\n" * 30) is True
    clean, st = deterministic_normalize("Hello world.\n\n1. Clause.")
    assert looks_messy(clean, st) is False


def test_eval_scorer_merger_alias_and_failures():
    rows = [
        {"expected": "contract", "predicted": "contract", "stage": "archived",
         "exact_ok": True, "aligned_ok": True},
        {"expected": "merger_agreement", "predicted": "contract", "stage": "archived",
         "exact_ok": False, "aligned_ok": True},
        {"expected": "correspondence", "predicted": "contract", "stage": "archived",
         "exact_ok": False, "aligned_ok": False},
        {"expected": "corporate_record", "predicted": "corporate_record",
         "stage": "failed", "error": "extraction failed", "exact_ok": True, "aligned_ok": True},
    ]
    summary = score_rows(rows)
    assert summary["n"] == 4
    assert abs(summary["exact_accuracy"] - 0.5) < 1e-9
    assert abs(summary["aligned_accuracy"] - 0.75) < 1e-9
    assert classify_failure(rows[1]) == "ok"
    assert classify_failure(rows[2]) == "wrong_class"
    assert classify_failure(rows[3]) == "failed"
    assert aligned("merger_agreement", "contract")
    assert not aligned("correspondence", "contract")
    assert summary["confusion"]["merger_agreement"]["contract"] == 1
    assert summary["confusion"]["correspondence"]["contract"] == 1


def test_attach_manifest_joins_trace_id_and_local_filename():
    from scripts.eval_pipeline import attach_manifest

    rows = [
        {"trace_id": "abc", "filename": "local.txt", "predicted": "contract",
         "expected": None, "exact_ok": False, "aligned_ok": False, "stage": "archived"},
        {"trace_id": "zzz", "filename": "other.txt", "predicted": "correspondence",
         "expected": None, "exact_ok": False, "aligned_ok": False, "stage": "archived"},
    ]
    import json
    from pathlib import Path
    path = Path("/tmp/mailroom-eval-manifest.json")
    path.write_text(json.dumps({
        "samples": [
            {"trace_id": "abc", "expected": "merger_agreement", "local_filename": "local.txt"},
        ]
    }), encoding="utf-8")
    out = attach_manifest(rows, str(path))
    assert out[0]["expected"] == "merger_agreement"
    assert out[0]["aligned_ok"] is True
    assert out[0]["exact_ok"] is False
    assert out[1]["expected"] is None

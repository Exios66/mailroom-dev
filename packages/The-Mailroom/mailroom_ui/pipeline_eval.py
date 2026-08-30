"""Deterministic pipeline eval scorers (entity-extraction-style).

Used by ``scripts/eval_pipeline.py`` and unit tests. No network I/O.
As of llm-mailroom v0.6.0, ``merger_agreement`` (MAUD) is a live class
distinct from ``contract`` (CUAD) — they are no longer aligned.
"""

from __future__ import annotations

from collections import Counter, defaultdict

# Historical extract aliases that once collapsed for scoring. Empty under
# v0.6.0 (MAUD is live). Kept as a hook if upstream re-adds aliases.
ALIGN: dict[str, str] = {}
FAILURE_MODES = (
    "ok",
    "wrong_class",
    "review",
    "failed",
    "empty_extract",
    "error",
    "unknown_stage",
)


def aligned(expected: str, predicted: str | None) -> bool:
    if not predicted:
        return False
    if expected == predicted:
        return True
    return ALIGN.get(expected) == predicted or ALIGN.get(predicted) == expected


def predicted_subclass_token(row: dict) -> str | None:
    """CUAD ``contract_subtype`` counts as the contract subclass."""
    token = row.get("predicted_subclass") or row.get("doc_subclass") or row.get("contract_subtype")
    if token is None:
        return None
    text = str(token).strip()
    return text or None


def subclass_ok(expected: str | None, predicted: str | None) -> bool:
    """Exact token match (case-insensitive) for Hub/CUAD subclass labels."""
    if not expected or not predicted:
        return False
    return str(expected).strip().lower() == str(predicted).strip().lower()


def classify_failure(row: dict) -> str:
    stage = (row.get("stage") or "").lower()
    if row.get("error") and stage in ("failed", ""):
        return "failed" if stage == "failed" else "error"
    if stage == "failed":
        return "failed"
    if stage in ("review", "human_review"):
        return "review"
    if row.get("expected") and not row.get("exact_ok") and not row.get("aligned_ok"):
        return "wrong_class"
    if row.get("expected") and not row.get("exact_ok") and row.get("aligned_ok"):
        return "ok"
    extract = row.get("extracted_data")
    if isinstance(extract, dict) and not any(
        v not in (None, "", [], {}) for k, v in extract.items() if not str(k).startswith("_")
    ):
        if stage not in ("archived",):
            return "empty_extract"
    if stage in ("archived", "archive", "report", "catalog"):
        return "ok"
    if not stage:
        return "unknown_stage"
    return "ok" if row.get("aligned_ok") else "wrong_class"


def score_rows(rows: list[dict]) -> dict:
    n = len(rows)
    exact = sum(1 for r in rows if r.get("exact_ok"))
    aligned_n = sum(1 for r in rows if r.get("aligned_ok"))
    modes = Counter(classify_failure(r) for r in rows)
    by_class: dict[str, dict] = defaultdict(lambda: {"n": 0, "exact": 0, "aligned": 0})
    for r in rows:
        cls = r.get("expected") or "unknown"
        by_class[cls]["n"] += 1
        by_class[cls]["exact"] += int(bool(r.get("exact_ok")))
        by_class[cls]["aligned"] += int(bool(r.get("aligned_ok")))
    costs = [r.get("cost_usd") for r in rows if isinstance(r.get("cost_usd"), (int, float))]
    tokens = [r.get("total_tokens") for r in rows if isinstance(r.get("total_tokens"), (int, float))]
    latencies = [r.get("seconds") for r in rows if isinstance(r.get("seconds"), (int, float))]
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        exp, pred = r.get("expected") or "unknown", r.get("predicted") or "none"
        confusion[exp][pred] += 1
    subclass_rows = [r for r in rows if r.get("expected_subclass")]
    n_sub = len(subclass_rows)
    subclass_hits = 0
    for r in subclass_rows:
        ok = r.get("subclass_ok")
        if ok is None:
            ok = subclass_ok(r.get("expected_subclass"), predicted_subclass_token(r))
        subclass_hits += int(bool(ok))
    return {
        "n": n,
        "exact_accuracy": exact / n if n else 0.0,
        "aligned_accuracy": aligned_n / n if n else 0.0,
        "n_subclass": n_sub,
        "subclass_accuracy": (subclass_hits / n_sub) if n_sub else None,
        "failure_modes": dict(modes),
        "by_class": {k: dict(v) for k, v in by_class.items()},
        "confusion": {k: dict(v) for k, v in confusion.items()},
        "cost_usd_sum": round(sum(costs), 6) if costs else 0.0,
        "tokens_sum": int(sum(tokens)) if tokens else 0,
        "latency_s_mean": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
        "intake_changed": sum(1 for r in rows if r.get("intake_changed")),
        "intake_messy": sum(1 for r in rows if r.get("intake_messy")),
    }

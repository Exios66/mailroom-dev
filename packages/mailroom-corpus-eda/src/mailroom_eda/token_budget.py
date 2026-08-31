"""Token budget analysis for ML model compatibility."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import CHARS_PER_TOKEN, TOKEN_BUDGETS


def estimate_tokens(text: str, chars_per_token: float = CHARS_PER_TOKEN) -> float:
    """Estimate token count using chars-per-token heuristic."""
    return len(text) / chars_per_token


def estimate_tokens_tiktoken(text: str, model: str = "o200k_base") -> int:
    """Accurate token count using tiktoken (requires tiktoken package)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding(model)
        return len(enc.encode(text))
    except ImportError:
        return int(estimate_tokens(text))


def add_token_estimates(rows: list[dict], use_tiktoken: bool = False) -> list[dict]:
    """Add token_estimate field to each row."""
    for r in rows:
        text = r.get("doc_text", "")
        if use_tiktoken:
            r["token_estimate"] = estimate_tokens_tiktoken(text)
        else:
            r["token_estimate"] = int(estimate_tokens(text))
        r["char_len"] = len(text)
    return rows


def budget_coverage(
    token_lengths: np.ndarray,
    budgets: list[int] | None = None,
) -> pd.DataFrame:
    """Compute % of docs fitting in each token budget."""
    if budgets is None:
        budgets = TOKEN_BUDGETS
    out = []
    total = len(token_lengths)
    for b in budgets:
        count = int((token_lengths <= b).sum())
        out.append({"budget": b, "count": count, "pct": 100 * count / total})
    return pd.DataFrame(out)


def budget_coverage_by_type(
    rows: list[dict],
    budgets: list[int] | None = None,
) -> pd.DataFrame:
    """Compute token budget coverage per doc_type."""
    if budgets is None:
        budgets = TOKEN_BUDGETS
    df = pd.DataFrame([{
        "doc_type": r.get("expected", "unknown"),
        "tokens": r.get("token_estimate", estimate_tokens(r.get("doc_text", ""))),
    } for r in rows])

    out = []
    for dt in sorted(df["doc_type"].unique()):
        subset = df[df["doc_type"] == dt]["tokens"].values
        for b in budgets:
            count = int((subset <= b).sum())
            out.append({"doc_type": dt, "budget": b, "count": count, "pct": 100 * count / len(subset)})
    return pd.DataFrame(out)


def compute_token_stats(
    rows: list[dict],
    by_type: bool = True,
) -> pd.DataFrame:
    """Compute token length statistics per doc_type or overall."""
    data = []
    for r in rows:
        tokens = r.get("token_estimate", estimate_tokens(r.get("doc_text", "")))
        data.append({
            "doc_type": r.get("expected", "unknown"),
            "tokens": tokens,
            "chars": len(r.get("doc_text", "")),
        })
    df = pd.DataFrame(data)
    if by_type:
        stats = df.groupby("doc_type")["tokens"].describe(
            percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        ).round(1)
        return stats.reset_index()
    return df["tokens"].describe(
        percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    ).to_frame().T


def token_stats_by_subclass(rows: list[dict]) -> pd.DataFrame:
    """Compute token stats by expected_subclass (top 20 by count)."""
    data = []
    for r in rows:
        tokens = r.get("token_estimate", estimate_tokens(r.get("doc_text", "")))
        data.append({
            "expected_subclass": r.get("expected_subclass", "unknown"),
            "tokens": tokens,
        })
    df = pd.DataFrame(data)
    top_subclasses = df["expected_subclass"].value_counts().head(20).index.tolist()
    df = df[df["expected_subclass"].isin(top_subclasses)]
    stats = df.groupby("expected_subclass")["tokens"].describe(
        percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    ).round(1)
    return stats.reset_index()


def find_longest_docs(rows: list[dict], n: int = 10) -> pd.DataFrame:
    """Find the N longest documents by token count."""
    data = []
    for r in rows:
        tokens = r.get("token_estimate", estimate_tokens(r.get("doc_text", "")))
        data.append({
            "filename": r.get("filename", ""),
            "doc_type": r.get("expected", ""),
            "expected_subclass": r.get("expected_subclass", ""),
            "tokens": tokens,
            "chars": len(r.get("doc_text", "")),
        })
    df = pd.DataFrame(data)
    return df.nlargest(n, "tokens")[["filename", "doc_type", "expected_subclass", "tokens", "chars"]]


def token_ecdf_data(token_lengths: np.ndarray) -> pd.DataFrame:
    """Compute ECDF data for token lengths."""
    sorted_tokens = np.sort(token_lengths)
    y = np.arange(1, len(sorted_tokens) + 1) / len(sorted_tokens)
    return pd.DataFrame({"tokens": sorted_tokens, "ecdf": y})


def token_ecdf_by_type(rows: list[dict]) -> pd.DataFrame:
    """Compute ECDF data per doc_type."""
    data = []
    for r in rows:
        tokens = r.get("token_estimate", estimate_tokens(r.get("doc_text", "")))
        data.append({"doc_type": r.get("expected", "unknown"), "tokens": tokens})
    df = pd.DataFrame(data)

    out = []
    for dt in sorted(df["doc_type"].unique()):
        subset = df[df["doc_type"] == dt]["tokens"].values
        sorted_tokens = np.sort(subset)
        y = np.arange(1, len(sorted_tokens) + 1) / len(sorted_tokens)
        for t, y_val in zip(sorted_tokens, y):
            out.append({"doc_type": dt, "tokens": t, "ecdf": y_val})
    return pd.DataFrame(out)


def save_token_analysis(
    rows: list[dict],
    output_dir: Path,
) -> dict[str, Path]:
    """Save all token analysis tables to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    token_lengths = np.array([r.get("token_estimate", estimate_tokens(r.get("doc_text", ""))) for r in rows])

    # Overall stats
    overall_stats = compute_token_stats(rows, by_type=False)
    overall_stats.to_csv(output_dir / "token_stats_overall.csv", index=False)

    # By type stats
    type_stats = compute_token_stats(rows, by_type=True)
    type_stats.to_csv(output_dir / "token_stats_by_type.csv", index=False)

    # By subclass stats
    subclass_stats = token_stats_by_subclass(rows)
    subclass_stats.to_csv(output_dir / "token_stats_by_subclass.csv", index=False)

    # Budget coverage
    budget_cov = budget_coverage(token_lengths)
    budget_cov.to_csv(output_dir / "token_budget_coverage.csv", index=False)

    # Budget coverage by type
    budget_cov_type = budget_coverage_by_type(rows)
    budget_cov_type.to_csv(output_dir / "token_budget_coverage_by_type.csv", index=False)

    # Longest docs
    longest = find_longest_docs(rows, n=20)
    longest.to_csv(output_dir / "longest_documents.csv", index=False)

    # ECDF
    ecdf = token_ecdf_data(token_lengths)
    ecdf.to_csv(output_dir / "token_ecdf_overall.csv", index=False)

    ecdf_type = token_ecdf_by_type(rows)
    ecdf_type.to_csv(output_dir / "token_ecdf_by_type.csv", index=False)

    return {
        "overall": output_dir / "token_stats_overall.csv",
        "by_type": output_dir / "token_stats_by_type.csv",
        "by_subclass": output_dir / "token_stats_by_subclass.csv",
        "budget": output_dir / "token_budget_coverage.csv",
        "budget_by_type": output_dir / "token_budget_coverage_by_type.csv",
        "longest": output_dir / "longest_documents.csv",
        "ecdf": output_dir / "token_ecdf_overall.csv",
        "ecdf_by_type": output_dir / "token_ecdf_by_type.csv",
    }
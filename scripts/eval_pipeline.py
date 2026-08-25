#!/usr/bin/env python3
"""Score Langfuse ``document-pipeline`` traces against HF docclass ground truth.

Mirrors the entity-extraction eval runners (manifest + deterministic scorers
+ JSON/markdown report) but reads **Langfuse** as the sole run log — the same
contract The-Mailroom displays. Classification is scored two ways:

- **exact** — predicted ``doc_type`` == HF ``expected``
- **aligned** — ``merger_agreement`` is accepted as ``contract`` (live
  mailroom taxonomy files MAUD rows as contract; the visualizer still shows
  the HF class)

Usage:
    python scripts/eval_pipeline.py --session pilot-hf-...
    python scripts/eval_pipeline.py --since 86400 --environment pilot
    python scripts/eval_pipeline.py --check   # no network: print scorer contract
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from mailroom_ui.intake_normalize import deterministic_normalize, looks_messy  # noqa: E402
from mailroom_ui.pipeline_eval import (  # noqa: E402
    aligned as _aligned,
    classify_failure,
    score_rows,
)

DATASET_ID = "Lucius-Morningstar/docclass-merged"


def _basic_auth() -> str:
    import base64

    pk = os.environ.get("LANGFUSE_PUBLIC_KEY") or ""
    sk = os.environ.get("LANGFUSE_SECRET_KEY") or ""
    if not pk or not sk:
        raise SystemExit("LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY missing (.env)")
    return base64.b64encode(f"{pk}:{sk}".encode()).decode()


def _lf_get(path: str) -> dict:
    host = (os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL")
            or "https://us.cloud.langfuse.com").rstrip("/")
    req = urllib.request.Request(
        host + path,
        headers={"Authorization": f"Basic {_basic_auth()}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode())


def fetch_traces(*, session: str | None, since: int, environment: str, limit: int) -> list[dict]:
    traces: list[dict] = []
    page = 1
    while len(traces) < limit:
        q = [f"limit={min(50, limit - len(traces))}", "name=document-pipeline", f"page={page}"]
        if session:
            q.append(f"sessionId={urllib.parse.quote(session)}")
        if environment:
            # v4 filter: some deployments ignore this; we also filter client-side
            q.append(f"environment={urllib.parse.quote(environment)}")
        data = _lf_get("/api/public/traces?" + "&".join(q))
        batch = data.get("data") or []
        if not batch:
            break
        traces.extend(batch)
        meta = data.get("meta") or {}
        if page >= int(meta.get("totalPages") or 1):
            break
        page += 1
        time.sleep(0.2)
    cutoff = None
    if since:
        cutoff = datetime.now(timezone.utc).timestamp() - since

    def _ts(t):
        raw = t.get("timestamp") or t.get("createdAt") or ""
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    out = []
    for t in traces:
        if cutoff and _ts(t) < cutoff:
            continue
        env = t.get("environment") or (t.get("metadata") or {}).get("environment")
        if environment and env and env != environment:
            continue
        if session:
            sid = t.get("sessionId") or t.get("session_id")
            if sid != session:
                continue
        out.append(t)
        if len(out) >= limit:
            break
    return out


def _pick(d: dict, *keys):
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return None


def _as_dict(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def traces_to_rows(traces: list[dict]) -> list[dict]:
    rows = []
    for t in traces:
        inp = t.get("input") if isinstance(t.get("input"), dict) else {}
        out = t.get("output") if isinstance(t.get("output"), dict) else {}
        meta = t.get("metadata") if isinstance(t.get("metadata"), dict) else {}
        filename = inp.get("filename") or meta.get("filename")
        scores = {s.get("name"): s.get("value") for s in (t.get("scores") or []) if isinstance(s, dict)}
        predicted = out.get("doc_type")
        expected = (
            (out.get("ground_truth") or {}).get("expected_hf_class")
            if isinstance(out.get("ground_truth"), dict) else None
        ) or (meta.get("expected_hf_class") if isinstance(meta, dict) else None)
        started = t.get("timestamp") or t.get("createdAt")
        ended = t.get("updatedAt") or t.get("updated_at")
        seconds = None
        try:
            if started and ended:
                t0 = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(str(ended).replace("Z", "+00:00"))
                seconds = round((t1 - t0).total_seconds(), 2)
        except Exception:
            seconds = None
        row = {
            "trace_id": t.get("id"),
            "filename": filename,
            "expected": expected,
            "predicted": predicted,
            "exact_ok": bool(expected and predicted and expected == predicted),
            "aligned_ok": _aligned(expected, predicted) if expected else False,
            "stage": out.get("stage"),
            "class_conf": out.get("classification_confidence"),
            "extract_conf": out.get("extraction_confidence"),
            "extracted_data": out.get("extracted_data"),
            "error": out.get("error_message") or out.get("error"),
            "cost_usd": scores.get("estimated_cost_usd") or t.get("totalCost"),
            "total_tokens": scores.get("total_tokens"),
            "verdict": scores.get("mailroom-pipeline-judge"),
            "quality": scores.get("mailroom-pipeline-quality"),
            "session": t.get("sessionId") or t.get("session_id"),
            "environment": t.get("environment"),
            "tags": t.get("tags"),
            "seconds": seconds,
            "intake_changed": False,
            "intake_messy": False,
        }
        rows.append(row)
    return rows


def enrich_intake(rows: list[dict]) -> list[dict]:
    """Pull ``normalize-intake`` observation output onto each row."""
    for row in rows:
        tid = row.get("trace_id")
        if not tid:
            continue
        try:
            detail = _lf_get(f"/api/public/traces/{urllib.parse.quote(str(tid))}")
        except Exception:
            continue
        out = detail.get("output") if isinstance(detail.get("output"), dict) else {}
        meta = detail.get("metadata") if isinstance(detail.get("metadata"), dict) else {}
        inp = detail.get("input") if isinstance(detail.get("input"), dict) else {}
        gt = (
            (out.get("ground_truth") if isinstance(out.get("ground_truth"), dict) else None)
            or (inp.get("ground_truth") if isinstance(inp.get("ground_truth"), dict) else None)
            or {}
        )
        for obs in detail.get("observations") or []:
            if not isinstance(obs, dict):
                continue
            name = obs.get("name") or ""
            obs_out = _as_dict(obs.get("output"))
            if name == "normalize-intake":
                row["intake_messy"] = bool(obs_out.get("messy"))
                row["intake_changed"] = bool(
                    obs_out.get("collapsed_blank_runs") or obs_out.get("hyphen_unwraps") or obs_out.get("changed")
                )
                row["intake_method"] = obs_out.get("method")
                row["intake_chars"] = obs_out.get("chars")
            if name == "pipeline-result":
                if not gt:
                    gt = obs_out.get("ground_truth") if isinstance(obs_out.get("ground_truth"), dict) else {}
                if not row.get("extracted_data"):
                    row["extracted_data"] = obs_out.get("extracted_data")
        expected = (
            row.get("expected")
            or gt.get("expected_hf_class")
            or meta.get("expected_hf_class")
            or gt.get("expected_doc_class")
        )
        if expected:
            row["expected"] = expected
            pred = row.get("predicted") or out.get("doc_type")
            row["exact_ok"] = expected == pred
            row["aligned_ok"] = _aligned(expected, pred)
        if not row.get("predicted"):
            row["predicted"] = out.get("doc_type")
            if row.get("expected"):
                row["exact_ok"] = row["expected"] == row.get("predicted")
                row["aligned_ok"] = _aligned(row["expected"], row.get("predicted"))
        if not row.get("stage"):
            row["stage"] = out.get("stage")
        if not row.get("error"):
            row["error"] = out.get("error_message") or out.get("error")
        if row.get("extracted_data") is None:
            row["extracted_data"] = out.get("extracted_data")
        scores = {s.get("name"): s.get("value") for s in (detail.get("scores") or []) if isinstance(s, dict)}
        row["cost_usd"] = row.get("cost_usd") or scores.get("estimated_cost_usd")
        row["total_tokens"] = row.get("total_tokens") or scores.get("total_tokens")
        row["verdict"] = row.get("verdict") or scores.get("mailroom-pipeline-judge")
        row["quality"] = row.get("quality") or scores.get("mailroom-pipeline-quality")
    return rows


def attach_hf_labels(rows: list[dict], split: str = "train") -> list[dict]:
    """Fill missing ``expected`` from the HF ground_truth config, joined on filename."""
    need = [r for r in rows if r.get("filename") and not r.get("expected")]
    if not need:
        return rows
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or ""
    headers = {"User-Agent": "the-mailroom-eval/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    labels: dict[str, str] = {}
    for sp in (split, "test", "train"):
        offset = 0
        while True:
            url = (
                "https://datasets-server.huggingface.co/rows?"
                f"dataset={urllib.parse.quote(DATASET_ID, safe='')}"
                f"&config=ground_truth&split={sp}&offset={offset}&length=100"
            )
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                page = json.loads(resp.read().decode())
            batch = [r["row"] for r in (page.get("rows") or [])]
            if not batch:
                break
            for row in batch:
                labels[row.get("filename")] = row.get("expected")
                # sanitized local names used as Langfuse input.filename
                stem = Path(str(row.get("filename") or "").replace("/", "_").replace(":", "_")).name
                if stem:
                    labels.setdefault(stem, row.get("expected"))
                    labels.setdefault(stem + ".txt", row.get("expected"))
            if len(batch) < 100:
                break
            offset += len(batch)
        if labels:
            break
    for r in rows:
        if not r.get("expected") and r.get("filename") in labels:
            r["expected"] = labels[r["filename"]]
            r["exact_ok"] = r["expected"] == r.get("predicted")
            r["aligned_ok"] = _aligned(r["expected"], r.get("predicted"))
    return rows


def attach_manifest(rows: list[dict], path: str | None) -> list[dict]:
    """Join expected labels from a hf_pilot ``manifest.json`` or ``report.json``."""
    if not path:
        return rows
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    items = payload.get("samples") if isinstance(payload, dict) else payload
    by_local: dict[str, str] = {}
    by_orig: dict[str, str] = {}
    by_trace: dict[str, str] = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        expected = item.get("expected")
        if item.get("local_filename") and expected:
            by_local[item["local_filename"]] = expected
        if item.get("filename") and expected:
            by_orig[item["filename"]] = expected
        if item.get("trace_id") and expected:
            by_trace[str(item["trace_id"])] = expected
    for r in rows:
        if r.get("expected"):
            continue
        expected = (
            by_trace.get(str(r.get("trace_id") or ""))
            or by_local.get(r.get("filename") or "")
            or by_orig.get(r.get("filename") or "")
        )
        if expected:
            r["expected"] = expected
            r["exact_ok"] = expected == r.get("predicted")
            r["aligned_ok"] = _aligned(expected, r.get("predicted"))
    return rows


def render_markdown(summary: dict, rows: list[dict], title: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"- n = **{summary['n']}**",
        f"- exact accuracy = **{summary['exact_accuracy']:.3f}**",
        f"- aligned accuracy (merger_agreement≡contract) = **{summary['aligned_accuracy']:.3f}**",
        f"- cost USD = {summary['cost_usd_sum']}",
        f"- tokens = {summary['tokens_sum']}",
        f"- mean latency s = {summary.get('latency_s_mean', 0)}",
        f"- intake changed / messy = {summary['intake_changed']} / {summary['intake_messy']}",
        "",
        "## Failure modes",
        "",
        "| mode | n |",
        "|---|---|",
    ]
    for mode, n in sorted((summary.get("failure_modes") or {}).items()):
        lines.append(f"| {mode} | {n} |")
    lines += ["", "## Per class", "", "| class | n | exact | aligned |", "|---|---|---|---|"]
    for cls, stats in sorted((summary.get("by_class") or {}).items()):
        lines.append(f"| {cls} | {stats['n']} | {stats['exact']} | {stats['aligned']} |")
    lines += ["", "## Confusion (expected \\ predicted)", ""]
    preds = sorted({p for cells in (summary.get("confusion") or {}).values() for p in cells})
    if preds:
        lines.append("| expected | " + " | ".join(preds) + " |")
        lines.append("|---|" + "|".join(["---"] * len(preds)) + "|")
        for exp, cells in sorted((summary.get("confusion") or {}).items()):
            lines.append("| " + exp + " | " + " | ".join(str(cells.get(p, 0)) for p in preds) + " |")
    lines += ["", "## Samples", "", "| file | expected | predicted | stage | mode |", "|---|---|---|---|---|"]
    for r in rows:
        fn = (r.get("filename") or r.get("trace_id") or "")[:48]
        lines.append(
            f"| {fn} | {r.get('expected')} | {r.get('predicted')} | "
            f"{r.get('stage')} | {classify_failure(r)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", help="Langfuse session id (pilot-hf-...)")
    parser.add_argument("--environment", default="pilot")
    parser.add_argument("--since", type=int, default=86400, help="seconds lookback")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--split", default="train", help="HF split used to join labels")
    parser.add_argument("--manifest", help="hf_pilot manifest.json or report.json for GT join")
    parser.add_argument("--out", help="write JSON report here")
    parser.add_argument("--md", help="write markdown report here")
    parser.add_argument("--check", action="store_true",
                        help="run the scorer on a fixture; no Langfuse/HF calls")
    args = parser.parse_args()

    if args.check:
        fixture = [
            {"expected": "contract", "predicted": "contract", "stage": "archived", "exact_ok": True, "aligned_ok": True},
            {"expected": "merger_agreement", "predicted": "contract", "stage": "archived", "exact_ok": False, "aligned_ok": True},
            {"expected": "correspondence", "predicted": "contract", "stage": "archived", "exact_ok": False, "aligned_ok": False},
            {"expected": "corporate_record", "predicted": "corporate_record", "stage": "failed", "error": "x", "exact_ok": True, "aligned_ok": True},
        ]
        for r in fixture:
            r["filename"] = r["expected"] + ".txt"
        summary = score_rows(fixture)
        assert summary["n"] == 4
        assert abs(summary["exact_accuracy"] - 0.5) < 1e-9
        assert abs(summary["aligned_accuracy"] - 0.75) < 1e-9
        assert classify_failure(fixture[2]) == "wrong_class"
        assert classify_failure(fixture[3]) == "failed"
        messy, stats = deterministic_normalize("A\n\n\n\nB-\nC")
        assert looks_messy("x\n" * 30, None)
        print("check ok", json.dumps(summary))
        return 0

    traces = fetch_traces(
        session=args.session, since=args.since,
        environment=args.environment, limit=args.limit,
    )
    rows = attach_manifest(
        enrich_intake(attach_hf_labels(traces_to_rows(traces), split=args.split)),
        args.manifest,
    )
    summary = score_rows(rows)
    title = f"Pipeline eval — {args.session or args.environment} ({datetime.now(timezone.utc).date()})"
    md = render_markdown(summary, rows, title)
    print(md)
    payload = {"summary": summary, "samples": rows, "session": args.session,
               "environment": args.environment, "dataset": DATASET_ID}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"wrote {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

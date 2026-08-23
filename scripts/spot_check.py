#!/usr/bin/env python3
"""Draw a human-review sample from the pipeline dump -> reports/eda/spot_check.csv.

Each row carries the rendered document text plus its ground-truth fields and an
automatic VERBATIM check (every scalar GT value must appear literally in
doc_text). Reviewers confirm rendering fidelity and GT alignment.

Usage:
    python scripts/spot_check.py [--k 25] [--seed 13]
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DUMP = REPO / "data" / "cms" / "pipeline.jsonl"
OUT = REPO / "reports" / "eda" / "spot_check.csv"

GT_KEYS = ["claim_number", "policy_number", "insurer", "insured_party", "claim_type",
           "date_of_loss", "date_filed", "claimed_amount", "coverage_determination"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=25)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    if not DUMP.exists():
        print("!! data/cms/pipeline.jsonl missing -- run build_pipeline_dump.py first", file=sys.stderr)
        return 1

    rows = [json.loads(l) for l in DUMP.open()]
    rng = random.Random(args.seed)

    # stratify the review by subclass proportionally
    by_sub: dict[str, list] = {}
    for r in rows:
        by_sub.setdefault(r["expected_subclass"], []).append(r)
    picks = []
    for sub, items in sorted(by_sub.items()):
        k = max(1, round(args.k * len(items) / len(rows)))
        picks.extend(rng.sample(items, min(k, len(items))))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["record_id", "expected_subclass", "verbatim_check",
                    *GT_KEYS, "damages_description_snippet", "doc_text_snippet"])
        n_pass = 0
        for r in picks:
            gt = r["metadata"]["ground_truth"]
            doc = r["doc_text"]
            checks = []
            for k in GT_KEYS:
                v = gt.get(k)
                if v is None or v == []:
                    checks.append(True)
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    checks.append(f"${v:,.2f}" in doc)
                else:
                    checks.append(str(v) in doc)
            ok = all(checks)
            n_pass += ok
            w.writerow([
                r["metadata"]["record_id"], r["expected_subclass"],
                "PASS" if ok else "FAIL",
                *[gt.get(k) if gt.get(k) not in ([], ) else "" for k in GT_KEYS],
                (gt.get("damages_description") or "")[:140],
                doc[:280].replace("\n", " | "),
            ])
    print(f"spot check: {n_pass}/{len(picks)} rows PASS verbatim audit -> {OUT}")
    return 0 if n_pass == len(picks) else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build revision-pinned mailroom-corpus eval dumps for the entity eval loop.

Bridges the published HF corpus (``Lucius-Morningstar/mailroom-corpus``) to
the flat local-dump shape the docclass runners consume
(``{filename, doc_text, expected, expected_subclass, expected_fields,
gt_fields, ...}``), at an explicit dataset revision so v7-era and v8-era
experiments are reproducible side by side (HUB-035).

    python scripts/datasets/build_mailroom_corpus_dumps.py \
        --revision bb57c5ad --label v7
    python scripts/datasets/build_mailroom_corpus_dumps.py \
        --revision <v8-sha> --label v8

Outputs (defaults):
    data/datasets/mailroom_corpus_<label>.jsonl          sorter dump (all rows)
    data/manifests/mailroom_corpus_<label>_<arm>.jsonl   per-specialist manifests
    data/manifests/mailroom_corpus_<label>.build.json    build manifest + sha256s

The GT scalar keys are derived from the ``ground_truth`` config at load time
(never hardcoded), so schema growth across corpus versions flows through
untouched. Join key is ``filename``; the ``ground_truth`` config is textless,
so ``doc_text`` comes from the ``default`` config (HUB-019 join contract).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_ID = "Lucius-Morningstar/mailroom-corpus"
DEFAULT_REVISION = "bb57c5ad"  # v7: docclass-merged-v0.1-working freeze (HUB-019)
IDENTITY_KEYS = ("filename", "expected", "expected_subclass", "split")

# canonical specialist families (taxonomy.yaml doc_classes + runner arms)
SPECIALIST_ARMS = {
    "contracts_specialist": frozenset({"contract", "merger_agreement"}),
    "insurance_claims_specialist": frozenset({"insurance_claim"}),
    "correspondence_specialist": frozenset({"correspondence"}),
    "corporate_records_specialist": frozenset({"corporate_record"}),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _row_records(split_rows) -> list[dict]:
    """Normalize a datasets.Dataset split (or list[dict]) into plain dicts."""
    return [dict(r) for r in split_rows]


def load_split_configs(revision: str, dataset_id: str):
    """Load (default, ground_truth) per split at the pinned revision."""
    from datasets import load_dataset  # lazy: keeps the module import offline

    out = {}
    for split in ("train", "test"):
        blind = load_dataset(dataset_id, "default", split=split, revision=revision)
        truth = load_dataset(dataset_id, "ground_truth", split=split, revision=revision)
        out[split] = (_row_records(blind), _row_records(truth))
    return out


def build_dump_rows(split_configs: dict) -> list[dict]:
    """Join default+ground_truth on filename into flat eval rows."""
    rows: list[dict] = []
    for split, (blind, truth) in sorted(split_configs.items()):
        by_name = {b.get("filename"): b for b in blind}
        for gt in truth:
            name = gt.get("filename")
            blind_row = by_name.get(name)
            if blind_row is None:
                print(f"WARN: gt row {name!r} has no default-config match; skipped",
                      file=sys.stderr)
                continue
            gt_fields = {
                k: v for k, v in gt.items()
                if k not in IDENTITY_KEYS and v not in (None, "", [])
            }
            expected_fields = {
                k: v for k, v in gt_fields.items()
                if not k.startswith("source_") and k != "content_sha256"
            }
            doc_text = str(blind_row.get("doc_text") or "")
            if not doc_text.strip():
                print(f"WARN: {name!r} empty doc_text; skipped", file=sys.stderr)
                continue
            rows.append({
                "filename": name,
                "doc_text": doc_text,
                "expected": gt.get("expected"),
                "expected_subclass": gt.get("expected_subclass") or "",
                "expected_fields": expected_fields,
                "gt_fields": gt_fields,
                "split": split,
            })
    return rows


def main_with_args(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default=DEFAULT_REVISION,
                        help=f"HF revision (sha or tag) of {DATASET_ID} "
                             f"(default: {DEFAULT_REVISION} = v7 freeze)")
    parser.add_argument("--label", required=True,
                        help="Short corpus-era label, e.g. v7 / v8 (used in filenames)")
    parser.add_argument("--dataset", default=DATASET_ID)
    parser.add_argument("--out-dir", default="data/datasets")
    parser.add_argument("--manifest-dir", default="data/manifests")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap rows per split (smoke builds only)")
    args = parser.parse_args(argv)

    split_configs = load_split_configs(args.revision, args.dataset)
    if args.limit:
        split_configs = {
            split: (blind[: args.limit], truth[: args.limit])
            for split, (blind, truth) in split_configs.items()
        }
    rows = build_dump_rows(split_configs)
    if not rows:
        parser.error("no rows built — check the revision/config join")

    out_dir = REPO_ROOT / args.out_dir
    manifest_dir = REPO_ROOT / args.manifest_dir
    dump_path = out_dir / f"mailroom_corpus_{args.label}.jsonl"
    write_jsonl(dump_path, rows)

    files = [{"path": str(dump_path.relative_to(REPO_ROOT)),
              "rows": len(rows),
              "sha256": sha256_file(dump_path)}]
    for arm, doc_types in sorted(SPECIALIST_ARMS.items()):
        arm_rows = [r for r in rows if r["expected"] in doc_types]
        if not arm_rows:
            print(f"NOTE: no rows for arm {arm} at this revision", file=sys.stderr)
            continue
        arm_path = manifest_dir / f"mailroom_corpus_{args.label}_{arm}.jsonl"
        write_jsonl(arm_path, arm_rows)
        files.append({"path": str(arm_path.relative_to(REPO_ROOT)),
                      "rows": len(arm_rows),
                      "sha256": sha256_file(arm_path)})

    by_class: dict[str, int] = {}
    for row in rows:
        by_class[row["expected"]] = by_class.get(row["expected"], 0) + 1
    build_manifest = {
        "dataset": args.dataset,
        "revision": args.revision,
        "label": args.label,
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows_total": len(rows),
        "rows_by_class": dict(sorted(by_class.items())),
        "files": files,
        "schema": "flat local-dump shape (sorter runner contract, HUB-035)",
    }
    manifest_path = manifest_dir / f"mailroom_corpus_{args.label}.build.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(build_manifest, indent=2) + "\n",
                             encoding="utf-8")

    print(f"dump:  {dump_path.relative_to(REPO_ROOT)} ({len(rows)} rows)")
    for entry in files[1:]:
        print(f"arm:   {entry['path']} ({entry['rows']} rows)")
    print(f"build: {manifest_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main_with_args())

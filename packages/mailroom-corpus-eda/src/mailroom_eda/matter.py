"""P2 matter/grouping groundwork (plan §13–§16, §14A, HUB-022).

Implements the §14A-decided backfill methodology over the local corpus:

- ``source_native_thread`` — Enron correspondence carries REAL thread
  structure (``metadata.message_id`` / ``metadata.in_reply_to`` / custodian /
  folder, verified on the v7 snapshot). Reply chains become genuine matters:
  ``matter_id`` = the thread root's message id, ``group_id`` = the chain,
  ``group_role: correspondence``, ``relationship: responds_to``. No
  fabrication — a row without thread linkage stays UNASSIGNED (empty
  grouping fields), because §13 forbids inventing structure and §14A forbids
  mixing constructions silently.
- ``synthetic_constructed`` — scaffold only: the construction vocabulary and
  the bundle-derivation contract (§14 bundle families) are defined here;
  manufacturing actual bundle rows is a sanctioned-publish decision (§84),
  flagged ``matter_construction: synthetic_constructed`` when it happens.

Grouping derivations are pure functions over (filename → metadata) joined
rows; the GT config carries no metadata column (verified 31 columns), so the
caller supplies the default-config metadata map.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from .eval_contract import GROUP_ROLES, RELATIONSHIP_TYPES  # noqa: F401

#: metadata keys carrying Enron thread structure (verified v7 metadata union).
THREAD_ROOT_KEY = "message_id"
THREAD_REPLY_KEY = "in_reply_to"
THREAD_CUSTODIAN_KEY = "custodian"

ANGLE_RE = re.compile(r"<([^>]+)>")


def _norm_message_id(value: Any) -> str:
    """Hub message-ids are angle-bracket strings; normalize for graph keys."""
    text = str(value or "").strip()
    inner = ANGLE_RE.match(text) if text.startswith("<") else None
    return (inner.group(1) if inner else text).strip()


def source_native_threads(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build Enron source-native thread matters (§14A method 1).

    Rows are correspondence GT records; ``metadata_by_filename`` maps each
    filename to the default-config ``metadata`` dict. A thread = the weakly
    connected component of message-id ↔ in-reply-to edges INSIDE one
    custodian mailbox (ids are only unique per custodian in the maildir
    world). Rows without message ids (non-Enron correspondence) stay
    unassigned — they carry no fabricated matter.
    """
    by_custodian: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        md = row.get("metadata") or {}
        if isinstance(md, str):
            import json

            try:
                md = json.loads(md)
            except json.JSONDecodeError:
                md = {}
        row = {**row, "_md": md if isinstance(md, dict) else {}}
        by_custodian[str(row["_md"].get(THREAD_CUSTODIAN_KEY) or "")].append(row)

    out: list[dict[str, Any]] = []
    for custodian, crows in by_custodian.items():
        # message_id → row (normalized); only rows WITH ids participate
        id_to_row: dict[str, dict[str, Any]] = {}
        for row in by_custodian[custodian]:
            mid = _norm_message_id(row["_md"].get(THREAD_ROOT_KEY))
            if mid:
                id_to_row[mid] = row

        # union-find over reply edges (bounded: each row has ≤1 in_reply_to)
        parent: dict[str, str] = {}

        def find(x: str) -> str:
            while parent.get(x, x) != x:
                x = parent[x]
            return x

        for row in by_custodian[custodian]:
            mid = _norm_message_id(row["_md"].get(THREAD_ROOT_KEY))
            if not mid:
                continue
            parent.setdefault(mid, mid)
            reply = _norm_message_id(row["_md"].get(THREAD_REPLY_KEY))
            if reply and reply in parent:
                a, b = find(mid), find(reply)
                if a != b:
                    parent[b] = a

        threads: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in by_custodian[custodian]:
            mid = _norm_message_id(row["_md"].get(THREAD_ROOT_KEY))
            if mid and mid in parent:
                threads[find(mid)].append(row)

        for root_id, members in threads.items():
            if len(members) < 2:
                continue  # singletons are standalone documents — no matter
            members.sort(key=lambda r: str(r["_md"].get("date") or ""))
            root_mid = _norm_message_id(members[0]["_md"].get(THREAD_ROOT_KEY))
            matter_id = f"MATTER-ENRON-{custodian}-{root_id[:24]}"
            for position, row in enumerate(members):
                out.append(
                    {
                        "filename": row["filename"],
                        "matter_id": matter_id,
                        "matter_construction": "source_native_thread",
                        "group_id": f"GROUP-THREAD-{root_id[:16]}",
                        "group_role": "correspondence",
                        "relationships": (
                            ["responds_to"] if position > 0 else []
                        ),
                        "thread_position": position,
                        "thread_size": len(members),
                    }
                )
    return out


def enrich_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach source-native grouping to the thread members (by filename).

    Canonical rows that are not part of a source-native thread stay
    UNASSIGNED (empty fields) — §14A: no fabricated matters.
    """
    groups = source_native_threads(rows)
    by_filename = {g["filename"]: g for g in groups}
    out = []
    for row in rows:
        merged = dict(row)
        g = by_filename.get(str(row.get("filename") or ""))
        for key in (
            "matter_id", "matter_construction", "group_id", "group_role",
            "relationships", "thread_position", "thread_size",
        ):
            merged[key] = g[key] if g else ([] if key == "relationships" else "")
        out.append(merged)
    return out

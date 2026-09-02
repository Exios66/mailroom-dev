"""Stable document identity, source provenance, and content hashes.

Groundwork for the mailroom-corpus hardening plan (§9–§11), shipping in the
``v0.2-mailroom-hardened`` release (§84). Every corpus row derives:

- ``document_id`` — stable identity: unique, deterministic, stable across
  rebuilds, independent of row ordering, train/test split, and Hub config.
  Derived from source identity (source_corpus + source filename), NEVER from
  a row index and never from content (two rows may share content — duplicates
  are Mailroom scenarios (§12), but each row is a distinct incoming artifact).
- ``source_corpus`` / ``source_document_id`` / ``source_filename`` /
  ``source_revision`` — provenance (§10): "where did this incoming document
  originate?" Source is an evaluation dimension, not taxonomy (§8).
- ``content_sha256`` — sha256 of the canonical doc_text bytes (utf-8).
- ``normalized_text_sha256`` — sha256 of the normalized text (see
  ``normalize_text``); supports duplicate detection (§12) and rebuild
  verification.

All derivations are pure functions of the row. Wiring into the published
parquet configs is the v0.2 release decision (§84); this module plus the
contract tests (``tests/test_contract.py``) establish and verify the fields
against the pinned corpus snapshot (§44) without pushing a new revision.
"""
from __future__ import annotations

import hashlib
import unicodedata
from typing import Any

# Release marker that ships these fields on the published configs (§84).
SCHEMA_ADDITION = "v0.2-mailroom-hardened"

# The five fused sources, keyed by the canonical five-class taxonomy
# (docs/v7-taxonomy.md; HUB_CLASSES in llm-mailroom's pipeline/hf_corpora.py).
SOURCE_CORPUS_BY_CLASS: dict[str, str] = {
    "contract": "theatticusproject/cuad",
    "merger_agreement": "maud",  # Zenodo 7500064
    "corporate_record": "sec_edgar",
    "correspondence": "Lucius-Morningstar/enron-correspondence-dedup",
    "insurance_claim": "cms_desynpuf",  # rendered via Exios66/claims-data-eda
}


def normalize_text(text: str) -> str:
    """Canonical text form for ``normalized_text_sha256``.

    NFC unicode normalization, CRLF/CR line endings folded to LF, runs of
    whitespace collapsed to a single space, ends stripped. Byte-level
    differences that Mailroom ingestion would not preserve do not produce
    distinct normalized hashes.
    """
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return " ".join(text.split())


def content_sha256(text: str) -> str:
    """sha256 of the canonical doc_text bytes (utf-8) — the canonical-bytes rule."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def normalized_text_sha256(text: str) -> str:
    """sha256 of ``normalize_text(text)`` encoded utf-8."""
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def source_corpus(row: dict[str, Any]) -> str:
    """Originating corpus for a row, from its canonical class (§8, §10)."""
    return SOURCE_CORPUS_BY_CLASS.get(str(row.get("expected") or ""), "unknown")


def source_document_id(row: dict[str, Any]) -> str:
    """Source-native identifier where one exists (§10).

    insurance_claim rows carry the claims-data-eda render ``record_id`` in
    metadata; every other source's stable native id is its filename (CUAD
    file name, MAUD contract_N.txt, EDGAR exhibit name, Enron maildir path).
    """
    md = row.get("metadata") or {}
    record_id = md.get("record_id")
    if record_id:
        return str(record_id)
    return str(row.get("filename") or "")


def document_id(row: dict[str, Any]) -> str:
    """Stable document identity (§9): ``DOC-`` + first 16 hex of sha256 over
    ``source_corpus`` + source filename.

    Deterministic and independent of row order, split, and Hub config.
    Uniqueness rests on the corpus's filename-uniqueness invariant (the v6
    append draws excluded existing filenames; asserted by the contract tests).
    """
    key = f"{source_corpus(row)}\n{row.get('filename') or ''}"
    return "DOC-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def enrich_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the row with identity/provenance/hash fields added."""
    out = dict(row)
    out["document_id"] = document_id(row)
    out["source_corpus"] = source_corpus(row)
    out["source_document_id"] = source_document_id(row)
    out["source_filename"] = str(row.get("filename") or "")
    # Per-row source revision is not tracked by the v7 builder; cast-safe ""
    # until a future builder revision records it (§10 groundwork).
    out["source_revision"] = str(row.get("source_revision") or "")
    out["content_sha256"] = content_sha256(str(row.get("doc_text") or ""))
    out["normalized_text_sha256"] = normalized_text_sha256(str(row.get("doc_text") or ""))
    return out


def enrich_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Enrich every row (input order preserved; identity is order-independent)."""
    return [enrich_row(r) for r in rows]

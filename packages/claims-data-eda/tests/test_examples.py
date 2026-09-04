"""Tests for the committed real-sample PDFs under docs/examples (no network/corpus needed)."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from render_samples import CHARS_PER_LINE, text_to_pdf  # noqa: E402


def _pdf(path: Path) -> bytes:
    return path.read_bytes()


def _check_structure(data: bytes) -> int:
    assert data.startswith(b"%PDF-")
    assert data.rstrip().endswith(b"%%EOF")
    m = re.search(rb"startxref\n(\d+)\n%%EOF", data)
    xref_at = int(m.group(1))
    assert data[xref_at:].startswith(b"xref")
    ids = [int(n) for n in re.findall(rb"\n(\d+) 0 obj", data[:xref_at])]
    if 1 not in ids:
        ids = [1] + ids
    assert ids == list(range(1, len(ids) + 1))
    assert (len(ids) - 2) % 3 == 0
    pages = (len(ids) - 2) // 3
    count = int(re.search(rb"/Count (\d+)", data[:xref_at]).group(1))
    assert count == pages
    return pages


class TestCommittedSamples:
    def test_at_least_five_pdf_samples(self):
        pdfs = sorted((REPO / "docs" / "examples").glob("sample_*.pdf"))
        assert len(pdfs) >= 5

    def test_all_samples_are_valid_pdfs_with_font(self):
        for p in sorted((REPO / "docs" / "examples").glob("sample_*.pdf")):
            data = _pdf(p)
            _check_structure(data)
            assert b"/BaseFont /Courier" in data

    def test_manifest_claims_match_files(self):
        manifest = json.loads((REPO / "docs" / "examples" / "manifest.json").read_text())
        assert manifest["sample_count"] == len(manifest["samples"]) >= 5
        for s in manifest["samples"]:
            p = REPO / "docs" / "examples" / s["pdf"]
            assert p.exists(), s["pdf"]
            data = _pdf(p)
            assert s["pdf_sha256"] == hashlib.sha256(data).hexdigest()
            assert s["pdf_bytes"] == len(data)
            assert s["subclass"] in {"carrier", "inpatient", "outpatient", "pde"}

    def test_strata_are_represented(self):
        manifest = json.loads((REPO / "docs" / "examples" / "manifest.json").read_text())
        assert set(manifest["strata"]) == {"carrier", "inpatient", "outpatient", "pde"}


class TestTextToPdf:
    def test_byte_determinism(self):
        a = text_to_pdf("hello corpus\nsecond line\n", "hdr")
        b = text_to_pdf("hello corpus\nsecond line\n", "hdr")
        assert a == b

    def test_multipage_output(self):
        long_text = "\n".join(f"line {i:04d} " + "x" * CHARS_PER_LINE for i in range(200))
        pages = _check_structure(text_to_pdf(long_text, "hdr"))
        assert pages >= 2

    def test_single_page_basics(self):
        data = text_to_pdf("MEDICARE SUMMARY NOTICE\n(approved)\n", "hdr")
        assert _check_structure(data) == 1
        assert b"\\(approved\\)" in data

    def test_escapes_parens_and_backslash(self):
        data = text_to_pdf("claim (allowed) $1,234 \\ (escaped)\n", "hdr")
        assert _check_structure(data) == 1
        assert b"claim \\(allowed\\)" in data

    def test_non_latin1_replaced(self):
        data = text_to_pdf("caf\xe9 \u203d weird\n", "hdr")  # U+203D not in cp1252 -> '?'
        assert _check_structure(data) == 1
        assert b"caf\xe9 ? weird" in data
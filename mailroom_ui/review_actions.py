"""Operator write-path to llm-mailroom human review.

Document *display* stays Langfuse-only. These helpers proxy approve / reject /
record / requeue / complete to the producer API when ``MAILROOM_PIPELINE_URL``
and a token are set. Missing config is a clear error — never a fabricated
catalog row.

Producer contract (llm-mailroom ``origin/main``): prefer ``/v1`` aliases;
resolve body uses ``override_doc_type`` (not ``doc_type``); lookup returns
``{"document": serialize_document(...)}`` with ``original_filename``. There is
no ``GET /documents/{id}/source`` on producer main — the visualizer tries it
(forks may ship it) and falls back to the lookup catalog row.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from .pipeline_ops import _token, pipeline_base_url, producer_url
from .pipeline_schema import normalize_review_doc_type, normalize_review_subclass

log = logging.getLogger("mailroom.review_actions")

VALID_DISPOSITIONS = frozenset({"resume", "record", "requeue", "complete"})


class ReviewActionError(Exception):
    """Producer call failed. ``status`` is the HTTP status to surface."""

    def __init__(self, message: str, status: int = 502, detail: Any = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.detail = detail


def pipeline_configured() -> bool:
    return bool(pipeline_base_url() and _token())


def _request_json(
    method: str,
    url: str,
    *,
    token: str = "",
    body: Optional[dict[str, Any]] = None,
    timeout: float = 8.0,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            pass
        detail: Any = raw[:400] if raw else (exc.reason or str(exc))
        try:
            parsed = json.loads(raw) if raw else {}
            if isinstance(parsed, dict):
                detail = parsed.get("detail") or parsed.get("error") or parsed
        except Exception:
            pass
        raise ReviewActionError(str(detail)[:400], status=int(exc.code), detail=detail) from exc
    except urllib.error.URLError as exc:
        raise ReviewActionError(f"producer unreachable: {exc.reason}", status=502) from exc
    payload = json.loads(raw) if raw else {}
    return payload if isinstance(payload, dict) else {"data": payload}


def _request_bytes(
    method: str,
    url: str,
    *,
    token: str = "",
    timeout: float = 8.0,
) -> tuple[bytes, str, str]:
    """GET bytes from the producer. Returns (body, content_type, filename)."""
    headers = {"Accept": "*/*"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            content_type = resp.headers.get("Content-Type") or "application/octet-stream"
            disposition = resp.headers.get("Content-Disposition") or ""
            filename = ""
            if "filename=" in disposition:
                filename = disposition.split("filename=", 1)[1].strip().strip('"')
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            pass
        detail: Any = raw[:400] if raw else (exc.reason or str(exc))
        try:
            parsed = json.loads(raw) if raw else {}
            if isinstance(parsed, dict):
                detail = parsed.get("detail") or parsed.get("error") or parsed
        except Exception:
            pass
        raise ReviewActionError(str(detail)[:400], status=int(exc.code), detail=detail) from exc
    except urllib.error.URLError as exc:
        raise ReviewActionError(f"producer unreachable: {exc.reason}", status=502) from exc
    return data, content_type, filename


def _require_pipeline() -> tuple[str, str]:
    base = pipeline_base_url()
    token = _token()
    if not base:
        raise ReviewActionError(
            "MAILROOM_PIPELINE_URL is not set — review resolve needs the llm-mailroom API",
            status=503,
        )
    if not token:
        raise ReviewActionError(
            "MAILROOM_PIPELINE_TOKEN (or MAILROOM_API_TOKEN) is not set",
            status=503,
        )
    return base, token


def _normalize_producer_document(document: dict[str, Any]) -> dict[str, Any]:
    """Alias producer ``original_filename`` so older UI keys still resolve."""
    out = dict(document)
    filename = (
        out.get("original_filename")
        or out.get("file")
        or out.get("filename")
        or ""
    )
    if filename:
        out.setdefault("original_filename", filename)
        out.setdefault("file", filename)
        out.setdefault("filename", filename)
    return out


def _unwrap_document(data: dict[str, Any]) -> Optional[dict[str, Any]]:
    document = data.get("document") if isinstance(data.get("document"), dict) else None
    if document is None:
        return None
    return _normalize_producer_document(document)


def lookup_document(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> dict[str, Any]:
    """GET /v1/lookup on the producer. Raises ReviewActionError on failure."""
    _require_pipeline()
    token = _token()
    params: dict[str, str] = {}
    if doc_id:
        params["doc_id"] = doc_id
    if trace_id:
        params["trace_id"] = trace_id
    if filename:
        params["filename"] = filename
    if not params:
        raise ReviewActionError("provide trace_id, filename, or doc_id", status=400)
    qs = urllib.parse.urlencode(params)
    data = _request_json("GET", producer_url(f"/lookup?{qs}"), token=token, timeout=timeout)
    document = _unwrap_document(data)
    if document is None:
        raise ReviewActionError("Document not found", status=404)
    return document


def fetch_audit(doc_id: str, *, timeout: float = 8.0) -> dict[str, Any]:
    _require_pipeline()
    token = _token()
    return _request_json(
        "GET",
        producer_url(f"/audit/{urllib.parse.quote(doc_id)}"),
        token=token,
        timeout=timeout,
    )


def _lookup_or_id(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> tuple[str, Optional[dict[str, Any]]]:
    """Resolve a producer doc_id, returning the catalog row when lookup hits."""
    resolved = (doc_id or "").strip()
    document: Optional[dict[str, Any]] = None
    try:
        document = lookup_document(
            trace_id=trace_id, filename=filename, doc_id=resolved, timeout=timeout,
        )
        resolved = str(document.get("doc_id") or resolved)
    except ReviewActionError as exc:
        if not resolved or exc.status not in (404,):
            raise
    if not resolved:
        raise ReviewActionError(
            "could not resolve a producer doc_id from this trace", status=404,
        )
    return resolved, document


def _source_from_catalog(document: dict[str, Any], resolved: str) -> dict[str, Any]:
    """Build a viewer payload from GET /lookup when /documents/{id}/source 404s.

    llm-mailroom main has no parked-file source route. The catalog row may still
    carry ``extracted_data`` / ``escalation_reason`` / ``original_filename``.
    """
    filename = (
        document.get("original_filename")
        or document.get("file")
        or document.get("filename")
        or resolved
    )
    chunks: list[str] = []
    text = document.get("extracted_text") or document.get("text")
    if isinstance(text, str) and text.strip():
        chunks.append(text.strip())
    extracted = document.get("extracted_data")
    if extracted not in (None, {}, []):
        dumped = json.dumps(extracted, indent=2, default=str)
        if chunks:
            chunks.append("--- extracted_data ---\n" + dumped)
        else:
            chunks.append(dumped)
    reason = document.get("escalation_reason")
    if isinstance(reason, str) and reason.strip():
        chunks.append("--- escalation ---\n" + reason.strip())
    body = "\n\n".join(chunks).strip() if chunks else None
    if not body:
        body = (
            "This producer has no GET /documents/{doc_id}/source. "
            f"Catalog lookup for {filename} returned no extracted_data or text."
        )
    has_content = bool(chunks)
    return {
        "configured": True,
        "status": "ok",
        "doc_id": document.get("doc_id") or resolved,
        "filename": filename,
        "content_type": "application/json; charset=utf-8" if extracted not in (None, {}, []) and not (
            isinstance(text, str) and text.strip()
        ) else "text/plain; charset=utf-8",
        "text": body,
        "truncated": False,
        "readable": has_content,
        "bytes": len(body.encode("utf-8")),
        "source": "lookup",
        "error": None if has_content else (
            "llm-mailroom main has no GET /documents/{doc_id}/source"
        ),
    }


def fetch_source(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> dict[str, Any]:
    """Parked-file JSON. Tries producer source, then catalog lookup fallback."""
    if not pipeline_configured():
        return {
            "configured": False,
            "text": None,
            "error": (
                "Set MAILROOM_PIPELINE_URL and MAILROOM_PIPELINE_TOKEN to "
                "view parked document text from llm-mailroom."
            ),
        }
    resolved, document = _lookup_or_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=timeout,
    )
    token = _token()
    try:
        data = _request_json(
            "GET",
            producer_url(f"/documents/{urllib.parse.quote(resolved)}/source"),
            token=token,
            timeout=timeout,
        )
        data["configured"] = True
        data["error"] = None
        data.setdefault("source", "producer")
        return data
    except ReviewActionError as exc:
        if exc.status != 404:
            raise
        if document is None:
            try:
                document = lookup_document(doc_id=resolved, timeout=timeout)
            except ReviewActionError:
                document = {"doc_id": resolved}
        return _source_from_catalog(document, resolved)


def fetch_source_download(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 30.0,
) -> tuple[bytes, str, str]:
    """GET /documents/{doc_id}/source?download=1 — original bytes.

    llm-mailroom main does not expose this route. A 404 is returned honestly
    rather than synthesizing a file from catalog JSON.
    """
    resolved, _document = _lookup_or_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=min(timeout, 8.0),
    )
    token = _token()
    try:
        data, content_type, name = _request_bytes(
            "GET",
            producer_url(f"/documents/{urllib.parse.quote(resolved)}/source?download=1"),
            token=token,
            timeout=timeout,
        )
    except ReviewActionError as exc:
        if exc.status == 404:
            raise ReviewActionError(
                "Producer has no GET /documents/{doc_id}/source — cannot download "
                "the original file. Use the text pane (catalog lookup fallback) "
                "or fetch the file from the review bin on the producer host.",
                status=404,
                detail=exc.detail,
            ) from exc
        raise
    return data, content_type, name or filename or resolved


def _class_override_body(
    doc_type: str = "",
    doc_subclass: str = "",
    override_doc_type: str = "",
) -> dict[str, str]:
    """Map visualizer ``doc_type`` onto producer ``override_doc_type``."""
    extra: dict[str, str] = {}
    try:
        kind = normalize_review_doc_type(override_doc_type or doc_type)
    except ValueError as exc:
        raise ReviewActionError(str(exc), status=400) from exc
    if kind:
        extra["override_doc_type"] = kind
    try:
        subclass = normalize_review_subclass(kind or doc_type or None, doc_subclass)
    except ValueError:
        # Producer main does not catalog-gate subclass; a parked token like
        # insurance "fnol" must still resolve. Canonicalize when we can.
        subclass = (doc_subclass or "").strip() or None
    if subclass:
        extra["doc_subclass"] = subclass
        if kind == "contract" or (not kind and (doc_type or "") == "contract"):
            extra["contract_subtype"] = subclass
    return extra


def _coerce_extracted_data(extracted_data: Any) -> Optional[dict[str, Any]]:
    if extracted_data is None or extracted_data == "":
        return None
    if isinstance(extracted_data, str):
        try:
            extracted_data = json.loads(extracted_data)
        except json.JSONDecodeError as exc:
            raise ReviewActionError("extracted_data must be a JSON object", status=400) from exc
    if not isinstance(extracted_data, dict):
        raise ReviewActionError("extracted_data must be a JSON object", status=400)
    return extracted_data


def review_context(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> dict[str, Any]:
    """Probe producer + optional catalog/audit for the REVIEW desk.

    Unconfigured returns HTTP-200-shaped payload (``configured: false``) so
    the UI can show setup copy instead of a hard error.
    """
    if not pipeline_configured():
        return {
            "configured": False,
            "document": None,
            "audit": None,
            "error": (
                "Set MAILROOM_PIPELINE_URL and MAILROOM_PIPELINE_TOKEN to "
                "approve, reject, record, or requeue against llm-mailroom."
            ),
        }
    out: dict[str, Any] = {
        "configured": True,
        "document": None,
        "audit": None,
        "error": None,
    }
    if not (trace_id or filename or doc_id):
        return out
    try:
        document = lookup_document(
            trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=timeout,
        )
        out["document"] = document
        resolved = str(document.get("doc_id") or doc_id or "")
        if resolved:
            try:
                out["audit"] = fetch_audit(resolved, timeout=timeout)
            except ReviewActionError as exc:
                log.info("review audit unavailable: %s", exc.message)
    except ReviewActionError as exc:
        if exc.status == 404:
            out["error"] = "Document not found in the producer catalog"
        else:
            out["error"] = exc.message
    return out


def resolve_review(
    *,
    decision: str,
    disposition: str = "resume",
    notes: str = "",
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    doc_type: str = "",
    doc_subclass: str = "",
    override_doc_type: str = "",
    extracted_data: Any = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """POST /v1/review/{doc_id}/resolve on the producer (JSON body)."""
    decision = (decision or "").strip()
    disposition = (disposition or "resume").strip() or "resume"
    if decision not in ("approved", "rejected"):
        raise ReviewActionError("decision must be 'approved' or 'rejected'", status=400)
    if disposition not in VALID_DISPOSITIONS:
        raise ReviewActionError(
            "disposition must be 'resume', 'record', 'requeue', or 'complete'",
            status=400,
        )
    extra = _class_override_body(doc_type, doc_subclass, override_doc_type)
    extracted = _coerce_extracted_data(extracted_data)
    _require_pipeline()
    token = _token()
    resolved, _document = _lookup_or_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=min(timeout, 8.0),
    )
    body: dict[str, Any] = {
        "decision": decision,
        "notes": notes or "",
        "disposition": disposition,
        **extra,
    }
    if extracted is not None:
        body["extracted_data"] = extracted
    return _request_json(
        "POST",
        producer_url(f"/review/{urllib.parse.quote(resolved)}/resolve"),
        token=token,
        body=body,
        timeout=timeout,
    )

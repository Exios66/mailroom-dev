"""Operator write-path to llm-mailroom human review.

Document *display* stays Langfuse-only. These helpers proxy approve / reject /
record / requeue to the producer API when ``MAILROOM_PIPELINE_URL`` and a
token are set. Missing config is a clear error — never a fabricated catalog
row.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from .pipeline_ops import _token, pipeline_base_url
from .pipeline_schema import normalize_review_doc_type, normalize_review_subclass

log = logging.getLogger("mailroom.review_actions")


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


def lookup_document(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> dict[str, Any]:
    """GET /lookup on the producer. Raises ReviewActionError on failure."""
    base, token = _require_pipeline()
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
    data = _request_json("GET", f"{base}/lookup?{qs}", token=token, timeout=timeout)
    document = data.get("document") if isinstance(data.get("document"), dict) else None
    if document is None:
        raise ReviewActionError("Document not found", status=404)
    return document


def fetch_audit(doc_id: str, *, timeout: float = 8.0) -> dict[str, Any]:
    base, token = _require_pipeline()
    return _request_json("GET", f"{base}/audit/{urllib.parse.quote(doc_id)}", token=token, timeout=timeout)


def _resolved_doc_id(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> str:
    resolved = (doc_id or "").strip()
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
    return resolved


def fetch_source(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 8.0,
) -> dict[str, Any]:
    """GET /documents/{doc_id}/source JSON. Unconfigured returns a 200-shaped payload."""
    if not pipeline_configured():
        return {
            "configured": False,
            "text": None,
            "error": (
                "Set MAILROOM_PIPELINE_URL and MAILROOM_PIPELINE_TOKEN to "
                "view parked document text from llm-mailroom."
            ),
        }
    resolved = _resolved_doc_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=timeout,
    )
    base, token = _require_pipeline()
    data = _request_json(
        "GET",
        f"{base}/documents/{urllib.parse.quote(resolved)}/source",
        token=token,
        timeout=timeout,
    )
    data["configured"] = True
    data["error"] = None
    return data


def fetch_source_download(
    *,
    trace_id: str = "",
    filename: str = "",
    doc_id: str = "",
    timeout: float = 30.0,
) -> tuple[bytes, str, str]:
    """GET /documents/{doc_id}/source?download=1 — original bytes."""
    resolved = _resolved_doc_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=min(timeout, 8.0),
    )
    base, token = _require_pipeline()
    data, content_type, name = _request_bytes(
        "GET",
        f"{base}/documents/{urllib.parse.quote(resolved)}/source?download=1",
        token=token,
        timeout=timeout,
    )
    return data, content_type, name or filename or resolved


def _class_override_body(doc_type: str = "", doc_subclass: str = "") -> dict[str, str]:
    extra: dict[str, str] = {}
    try:
        kind = normalize_review_doc_type(doc_type)
    except ValueError as exc:
        raise ReviewActionError(str(exc), status=400) from exc
    if kind:
        extra["doc_type"] = kind
    try:
        subclass = normalize_review_subclass(kind or doc_type or None, doc_subclass)
    except ValueError as exc:
        raise ReviewActionError(str(exc), status=400) from exc
    if subclass:
        extra["doc_subclass"] = subclass
        if kind == "contract" or (not kind and (doc_type or "") == "contract"):
            extra["contract_subtype"] = subclass
    return extra


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
    timeout: float = 60.0,
) -> dict[str, Any]:
    """POST /review/{doc_id}/resolve on the producer (JSON body)."""
    decision = (decision or "").strip()
    disposition = (disposition or "resume").strip() or "resume"
    if decision not in ("approved", "rejected"):
        raise ReviewActionError("decision must be 'approved' or 'rejected'", status=400)
    if disposition not in ("resume", "record", "requeue"):
        raise ReviewActionError(
            "disposition must be 'resume', 'record', or 'requeue'", status=400,
        )
    extra = _class_override_body(doc_type, doc_subclass)
    base, token = _require_pipeline()
    resolved = _resolved_doc_id(
        trace_id=trace_id, filename=filename, doc_id=doc_id, timeout=min(timeout, 8.0),
    )
    body: dict[str, Any] = {
        "decision": decision,
        "notes": notes or "",
        "disposition": disposition,
        **extra,
    }
    return _request_json(
        "POST",
        f"{base}/review/{urllib.parse.quote(resolved)}/resolve",
        token=token,
        body=body,
        timeout=timeout,
    )

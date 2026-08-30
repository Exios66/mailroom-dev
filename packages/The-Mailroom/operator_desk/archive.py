"""Archive file access for the operator desk.

Mount: ``app.include_router(router)`` → ``/v1/archive``. Reads the local
``archive_index`` (and files under ``MAILROOM_BASE_DIR/archive``). Does not
fabricate catalog rows from Langfuse.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .auth import UserProfile, get_current_user
from .db import archive_dir, base_dir, connect, write_audit

log = logging.getLogger("mailroom.operator.archive")

router = APIRouter(prefix="/v1/archive", tags=["operator-archive"])


class ArchiveEntry(BaseModel):
    doc_id: str
    matter_id: str
    doc_type: str
    archive_path: str
    file_size_bytes: Optional[int] = None
    checksum_sha256: Optional[str] = None
    archived_at: str


def _safe_archive_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base_dir() / path
    try:
        resolved = path.resolve()
    except OSError as exc:
        raise HTTPException(status_code=400, detail="invalid archive path") from exc
    allowed = (archive_dir().resolve(), base_dir().resolve())
    if not any(root == resolved or root in resolved.parents for root in allowed):
        raise HTTPException(status_code=400, detail="archive path escapes base dir")
    return resolved


def _entry_row(doc_id: str):
    conn = connect()
    try:
        return conn.execute(
            "SELECT * FROM archive_index WHERE doc_id = ?", (doc_id,)
        ).fetchone()
    finally:
        conn.close()


@router.get("/list", response_model=List[ArchiveEntry])
async def list_archive(
    matter_id: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    user: UserProfile = Depends(get_current_user),
):
    conn = connect()
    try:
        query = "SELECT * FROM archive_index WHERE 1=1"
        params: list[str] = []
        if matter_id:
            query += " AND matter_id = ?"
            params.append(matter_id)
        if doc_type:
            query += " AND doc_type = ?"
            params.append(doc_type)
        query += " ORDER BY archived_at DESC"
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()
    return [ArchiveEntry(**dict(r)) for r in rows]


@router.get("/{doc_id}/download")
async def download_archive(doc_id: str, user: UserProfile = Depends(get_current_user)):
    row = _entry_row(doc_id)
    if not row or not row["archive_path"]:
        raise HTTPException(status_code=404, detail="Archive entry not found")
    path = _safe_archive_path(row["archive_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File missing from archive storage")
    write_audit(
        action="archive_download",
        user_id=user.user_id,
        target_doc_id=doc_id,
        target_matter_id=row["matter_id"],
    )
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("/{doc_id}/preview")
async def preview_archive(doc_id: str, user: UserProfile = Depends(get_current_user)):
    row = _entry_row(doc_id)
    if not row:
        raise HTTPException(status_code=404, detail="Archive entry not found")
    path = _safe_archive_path(row["archive_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File missing")
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md", ".json", ".csv"):
        content = path.read_text(encoding="utf-8", errors="replace")
        return {"content": content, "type": "text", "mime": "text/plain"}
    if suffix == ".pdf":
        try:
            import fitz

            doc = fitz.open(path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return {"content": text[:5000], "type": "pdf", "mime": "application/pdf"}
        except ImportError:
            return {
                "content": "PDF preview requires PyMuPDF (pip install -e '.[operator]')",
                "type": "pdf",
                "mime": "application/pdf",
            }
    if suffix in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        mime = f"image/{suffix.lstrip('.').replace('jpg', 'jpeg')}"
        return {"content": b64, "type": "image", "mime": mime}
    return {"content": None, "type": "binary", "mime": "application/octet-stream"}


@router.get("/{doc_id}/verify")
async def verify_checksum(doc_id: str, user: UserProfile = Depends(get_current_user)):
    row = _entry_row(doc_id)
    if not row:
        raise HTTPException(status_code=404, detail="Archive entry not found")
    path = _safe_archive_path(row["archive_path"])
    if not path.is_file():
        return {"doc_id": doc_id, "valid": False, "reason": "File missing"}
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = row["checksum_sha256"]
    valid = expected is None or sha256 == expected
    write_audit(
        action="archive_verify",
        user_id=user.user_id,
        target_doc_id=doc_id,
        metadata={"valid": valid},
    )
    return {
        "doc_id": doc_id,
        "valid": valid,
        "computed": sha256,
        "expected": expected,
        "path": str(path),
    }

"""Shared constants + card helpers for the §84 hardened-release scripts
(publish_hardened / reconcile_gt_v8 — HUB-022, HUB-032).

Kept in src so the release tooling has exactly one copy of the column
registries and the card-section anchors; the scripts stay thin CLIs.
"""
from __future__ import annotations

IDENTITY_FIELDS = (
    "document_id", "source_corpus", "source_document_id", "source_filename",
    "source_revision", "content_sha256", "normalized_text_sha256",
)
CONTRACT_FIELDS = (
    "expected_specialist", "expected_stage", "review_expected", "review_reason",
    "retry_expected", "expected_post_retry_state",
    "annotation_source", "annotation_method", "annotation_model",
    "annotation_prompt_version", "annotation_confidence", "annotation_reviewer",
    "annotation_timestamp",
)
MATTER_SCALARS = (
    "matter_id", "matter_construction", "group_id", "group_role",
    "thread_position", "thread_size", "thread_evidence",
)
MATTER_LISTS = ("relationships", "related_document_ids")

#: The live card section owned by the §84 hardened release (HUB-022/HUB-032).
#: `upsert_section` replaces it in place; the anchor heading below must exist
#: exactly once on the live card.
CARD_HEADING = "## Mailroom evaluation hardening (v0.2/v0.3/v0.4, 2026-09-02; reconciled onto the v8 base, HUB-032)"
CARD_ANCHOR = "## Original files (KANBAN-105 addendum, 2026-08-30)"


def fetch_live_card(repo_id: str) -> str | None:
    """The current dataset card (None when offline / no token)."""
    try:
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(repo_id=repo_id, filename="README.md", repo_type="dataset")
        from pathlib import Path

        return Path(path).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"WARN: could not fetch live card ({exc})")
        return None

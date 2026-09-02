"""P2 synthetic bundle-family generator (plan §14, §14A, §87; HUB-022).

Manufactures multi-document matter/group bundles over REAL anchor rows —
the ``synthetic_constructed`` leg of the §14A decision (documented in
DOCCLASS_CONTRACT.md §9; the primary multi-document eval path given that
header threads are structurally absent and subject threads cover only
19/350 correspondence rows).

Design (scaffold — publishes nothing; the §84 v0.2 release decision gates
any push):

- **Families are templates, not fabrications of content**: each family
  declares a REAL anchor document (sampled from the snapshot by class) plus
  manufactured sibling documents whose ``doc_text`` is an explicit scaffold
  template (marked ``[SYNTHETIC SIBLING — grouping-evaluation scaffold]``).
  The grouping structure under test is the matter/group assignment and the
  router's bundle behavior — never the sibling prose.
- **Everything is flagged**: every member row carries
  ``matter_construction: synthetic_constructed``; manufactured members also
  carry ``synthetic: true`` and a ``bundle_family`` key. Coverage reports
  count these separately from source-native and heuristic rows (§14A).
- **Deterministic**: seeded (``RANDOM_STATE = 42`` convention); the same
  seed + snapshot yields byte-identical bundles.

Family templates follow §14's two worked examples (Legal: contract +
amendment + exhibit + signature-page + email-notice; Insurance: claim form
+ EOB + provider bill + correspondence + supporting record) and extend them
to the remaining classes. Roles/relationship types are drawn ONLY from the
closed ``GROUP_ROLES``/``RELATIONSHIP_TYPES`` vocabularies (§15/§16) and
the §87 duplicate axis uses ``DUPLICATE_TYPES`` (§12).
"""
from __future__ import annotations

import random
from typing import Any

from .eval_contract import (
    DUPLICATE_TYPES,
    GROUP_ROLES,
    RELATIONSHIP_TYPES,
    SOURCE_BY_CLASS,
    SPECIALIST_BY_CLASS,
)

SYNTHETIC_FLAG_HEADER = "[SYNTHETIC SIBLING — grouping-evaluation scaffold; not a source document]"

#: Role for manufactured members whose class IS the anchor class.
ROLE_SIBLING = "supporting"

#: §14 family templates. Each member spec:
#:   role        — GROUP_ROLES value
#:   doc_class   — canonical class of the manufactured document
#:   relationship— RELATIONSHIP_TYPES value toward the anchor
#:   label       — stable slug used in filenames/doc_text
#: The anchor itself is member 0 (role ``primary``) and is NOT manufactured.
BUNDLE_FAMILIES: dict[str, dict[str, Any]] = {
    "legal_contract_family": {
        "anchor_class": "contract",
        "members": (
            {"role": "amendment", "doc_class": "contract",
             "relationship": "amendment_of", "label": "amendment"},
            {"role": "exhibit", "doc_class": "contract",
             "relationship": "exhibit_of", "label": "exhibit-a"},
            {"role": "attachment", "doc_class": "contract",
             "relationship": "attachment_of", "label": "signature-page"},
            {"role": "correspondence", "doc_class": "correspondence",
             "relationship": "references", "label": "email-notice"},
        ),
    },
    "insurance_claim_family": {
        "anchor_class": "insurance_claim",
        "members": (
            {"role": "attachment", "doc_class": "insurance_claim",
             "relationship": "attachment_of", "label": "eob"},
            {"role": "supporting", "doc_class": "insurance_claim",
             "relationship": "supplement_to", "label": "provider-bill"},
            {"role": "supporting", "doc_class": "insurance_claim",
             "relationship": "supplement_to", "label": "supporting-record"},
            {"role": "correspondence", "doc_class": "correspondence",
             "relationship": "responds_to", "label": "adjuster-letter"},
        ),
    },
    "merger_family": {
        "anchor_class": "merger_agreement",
        "members": (
            {"role": "amendment", "doc_class": "merger_agreement",
             "relationship": "amendment_of", "label": "amendment"},
            {"role": "exhibit", "doc_class": "merger_agreement",
             "relationship": "exhibit_of", "label": "disclosure-schedule"},
            {"role": "correspondence", "doc_class": "correspondence",
             "relationship": "references", "label": "closing-email"},
        ),
    },
    "corporate_record_family": {
        "anchor_class": "corporate_record",
        "members": (
            {"role": "amendment", "doc_class": "corporate_record",
             "relationship": "amendment_of", "label": "certificate-of-amendment"},
            {"role": "attachment", "doc_class": "corporate_record",
             "relationship": "attachment_of", "label": "consent"},
        ),
    },
    "correspondence_thread_family": {
        "anchor_class": "correspondence",
        "members": (
            {"role": "correspondence", "doc_class": "correspondence",
             "relationship": "responds_to", "label": "reply"},
            {"role": "attachment", "doc_class": "correspondence",
             "relationship": "attachment_of", "label": "attached-memo"},
        ),
    },
}

ARBITER_NOTE = (
    "Arbiter/retry fixtures (§72A) ride the same scaffold: a family whose "
    "member was manufactured to fail first-pass exercises recovery."
)

_SIBLING_TEMPLATE = (
    "{header}\n"
    "Document type: {doc_class} ({role} — {label})\n"
    "Matter: {matter_id}\n"
    "Group: {group_id}\n"
    "Relationship: {relationship} the primary document {anchor_filename}\n"
    "\n"
    "This document was MANUFACTURED by mailroom_eda.bundles to give the "
    "anchor a plausible sibling for multi-document grouping evaluation "
    "(§14/§14A). Its text carries no legal meaning; its ground truth is the "
    "bundle assignment itself (group_role={role}, "
    "relationship_type={relationship}).\n"
)

_DUPLICATE_TEMPLATE = (
    "{header}\n"
    "Document type: {doc_class} (duplicate — {label})\n"
    "Matter: {matter_id}\n"
    "Group: {group_id}\n"
    "Duplicate of: {anchor_filename} ({duplicate_type})\n"
    "\n"
    "MANUFACTURED duplicate member (§87/§12): a {duplicate_type} of the "
    "anchor used to test duplicate detection inside a bundle.\n"
)


def _md_anchor(row: dict[str, Any]) -> str:
    return str(row.get("filename") or "")


def _sibling_row(
    family: str,
    spec: dict[str, Any],
    matter_id: str,
    group_id: str,
    anchor: dict[str, Any],
    seq: int,
) -> dict[str, Any]:
    """Manufacture one sibling row (explicit scaffold text, fully flagged)."""
    doc_class = spec["doc_class"]
    filename = f"{matter_id.lower()}-{spec['label']}.txt"
    text = _SIBLING_TEMPLATE.format(
        header=SYNTHETIC_FLAG_HEADER,
        doc_class=doc_class,
        role=spec["role"],
        label=spec["label"],
        matter_id=matter_id,
        group_id=group_id,
        relationship=spec["relationship"],
        anchor_filename=_md_anchor(anchor),
    )
    return {
        "filename": filename,
        "doc_text": text,
        "expected": doc_class,
        "expected_subclass": "",
        "synthetic": "true",
        "bundle_family": family,
        "bundle_anchor_filename": _md_anchor(anchor),
        "matter_id": matter_id,
        "group_id": group_id,
        "group_role": spec["role"],
        "matter_construction": "synthetic_constructed",
        "relationships": [spec["relationship"]],
        "related_document_ids": [_md_anchor(anchor)],
        "fixture_note": ARBITER_NOTE if spec.get("fixture_note") else "",
    }


def synthetic_bundles(
    rows: list[dict[str, Any]],
    *,
    seed: int = 42,
    families: tuple[str, ...] | None = None,
    anchors_per_family: int = 2,
    with_duplicates: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build §14 bundle instances over real anchor rows (scaffold, no I/O).

    Returns ``(rows, manifest)``:

    - ``rows`` — anchor rows (real documents, enriched with bundle fields)
      followed by manufactured sibling rows. ALL bundle rows carry
      ``matter_construction: synthetic_constructed``; manufactured rows add
      ``synthetic: true``. Anchor rows keep their real ``filename`` (their
      ``doc_text`` is untouched); callers without text should pass GT rows
      and join text separately, as everywhere else in this package.
    - ``manifest`` — per-family counts, construction counts, and the seed —
      the audit trail §14A requires so coverage reports can keep synthetic
      rows a SEPARATE column.

    ``with_duplicates`` adds one manufactured duplicate per family instance
    (§87/§12: ``template_variant`` — the only duplicate type a scaffold can
    honestly manufacture).
    """
    if families is None:
        families = tuple(BUNDLE_FAMILIES)
    unknown = [f for f in families if f not in BUNDLE_FAMILIES]
    if unknown:
        raise KeyError(f"unknown bundle families: {unknown}")
    rng = random.Random(seed)

    by_class: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        doc_class = str(row.get("expected") or "")
        if doc_class in SOURCE_BY_CLASS:
            by_class.setdefault(doc_class, []).append(row)

    out: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {
        "seed": seed,
        "matter_construction": "synthetic_constructed",
        "families": {},
        "members_total": 0,
        "manufactured_total": 0,
    }
    seq = 0
    for family in families:
        template = BUNDLE_FAMILIES[family]
        anchor_class = template["anchor_class"]
        pool = by_class.get(anchor_class, [])
        if len(pool) < anchors_per_family:
            continue  # class absent from the passed rows — skip honestly
        anchors = rng.sample(pool, anchors_per_family)
        fam_manifest = {"anchor_class": anchor_class, "instances": 0,
                        "members": 0, "manufactured": 0}
        for anchor in anchors:
            seq += 1
            matter_id = f"MATTER-SYN-{family[:4].upper().replace('_', '')}-{seq:04d}"
            group_id = f"GROUP-SYN-{seq:04d}"
            members = [dict(anchor)]
            members[0].update(
                {
                    "matter_id": matter_id,
                    "group_id": group_id,
                    "group_role": "primary",
                    "matter_construction": "synthetic_constructed",
                    "bundle_family": family,
                    "bundle_anchor_filename": _md_anchor(anchor),
                    "relationships": [],
                    "related_document_ids": [],
                }
            )
            manufactured = 0
            for spec in template["members"]:
                if spec["role"] not in GROUP_ROLES or spec["relationship"] not in RELATIONSHIP_TYPES:
                    raise AssertionError(
                        f"family {family} member escapes closed vocabulary: {spec}"
                    )
                sibling = _sibling_row(family, spec, matter_id, group_id, anchor, seq)
                members.append(sibling)
                manufactured += 1
            if with_duplicates:
                dup_type = "template_variant"
                assert dup_type in DUPLICATE_TYPES
                dup = _sibling_row(
                    family,
                    {"role": ROLE_SIBLING, "doc_class": anchor_class,
                     "relationship": "related_to", "label": "duplicate"},
                    matter_id, group_id, anchor, seq,
                )
                dup["doc_text"] = _DUPLICATE_TEMPLATE.format(
                    header=SYNTHETIC_FLAG_HEADER,
                    doc_class=anchor_class,
                    label="duplicate",
                    matter_id=matter_id,
                    group_id=group_id,
                    anchor_filename=_md_anchor(anchor),
                    duplicate_type=dup_type,
                )
                dup["filename"] = f"{matter_id.lower()}-duplicate.txt"
                dup["duplicate_type"] = dup_type
                dup["relationships"] = ["duplicate_of"]
                members.append(dup)
                manufactured += 1
            out.extend(members)
            fam_manifest["instances"] += 1
            fam_manifest["members"] += len(members)
            fam_manifest["manufactured"] += manufactured
        if fam_manifest["instances"]:
            manifest["families"][family] = fam_manifest
            manifest["members_total"] += fam_manifest["members"]
            manifest["manufactured_total"] += fam_manifest["manufactured"]
    return out, manifest


def bundle_specialist(row: dict[str, Any]) -> str:
    """Routing expectation for a bundle member (same registry as P1)."""
    return SPECIALIST_BY_CLASS.get(str(row.get("expected") or ""), "")

"""§13–§16 P2 matter/grouping tests (HUB-022, plan §14A)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mailroom_eda import matter as mt


def _corr(filename, message_id, in_reply_to=None, custodian="mbx", date="2001-05-01"):
    return {
        "filename": filename,
        "expected": "correspondence",
        "metadata": {
            "message_id": message_id,
            "in_reply_to": in_reply_to,
            "custodian": custodian,
            "date": date,
        },
    }


def test_thread_of_three_becomes_one_matter():
    rows = [
        _corr("m1", "<a@x>", custodian="k", date="2001-05-01"),
        _corr("m2", "<b@x>", in_reply_to="<a@x>", custodian="k", date="2001-05-02"),
        _corr("m3", "<c@x>", in_reply_to="<b@x>", custodian="k", date="2001-05-03"),
    ]
    groups = mt.source_native_threads(rows)
    assert {g["filename"] for g in groups} == {"m1", "m2", "m3"}
    assert len({g["matter_id"] for g in groups}) == 1
    root = next(g for g in groups if g["thread_position"] == 0)
    assert root["group_role"] == "correspondence"
    assert root["matter_construction"] == "source_native_thread"
    assert root["thread_size"] == 3
    replies = [g for g in groups if g["thread_position"] > 0]
    assert all(g["relationships"] == ["responds_to"] for g in replies)


def test_singletons_stay_unassigned():
    rows = [_corr("solo", "<x@x>", custodian="k")]
    assert mt.source_native_threads(rows) == []
    out = mt.enrich_rows(rows)
    assert out[0]["matter_id"] == "" and out[0]["group_role"] == ""
    assert out[0]["relationships"] == []


def test_cross_custodian_ids_are_isolated():
    # identical message-id text in two mailboxes must NOT join (maildir ids
    # are per-custodian); k1 is a singleton, j1+j2 form the only thread
    rows = [
        _corr("k1", "<same@id>", custodian="k"),
        _corr("k2", "<same@id>", custodian="j"),
        _corr("j1", "<reply@id>", in_reply_to="<same@id>", custodian="j", date="2001-05-02"),
    ]
    groups = mt.source_native_threads(rows)
    files = {g["filename"] for g in groups}
    assert files == {"k2", "j1"}
    assert len({g["matter_id"] for g in groups}) == 1


def test_reply_to_unknown_root_stays_unlinked():
    rows = [_corr("orphan", "<o@x>", in_reply_to="<missing@x>", custodian="k")]
    assert mt.source_native_threads(rows) == []


def test_string_metadata_rows_are_parsed():
    rows = [
        {"filename": "m1", "expected": "correspondence",
         "metadata": '{"message_id": "<a@x>", "custodian": "k", "date": "2001"}'},
        {"filename": "m2", "expected": "correspondence",
         "metadata": '{"message_id": "<b@x>", "in_reply_to": "<a@x>", "custodian": "k"}'},
    ]
    groups = mt.source_native_threads(rows)
    assert len(groups) == 2
    assert len({g["matter_id"] for g in groups}) == 1


def test_vocabularies_align_with_contract():
    assert "correspondence" in mt.GROUP_ROLES
    assert "responds_to" in mt.RELATIONSHIP_TYPES

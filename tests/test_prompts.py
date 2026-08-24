"""Prompt-registry mirror tests: roster, names, override loading."""

from __future__ import annotations

import json

import pytest

from mailroom_ui.prompt_registry import (
    PROMPT_TEMPLATES,
    load_prompt_templates,
    prompt_name,
)

# Removed from the mix per the docclass-pilot doc-class universe.
REMOVED = {"due_diligence_specialist", "compliance_specialist",
           "court_opinions_specialist"}


def test_roster_matches_pilot_universe():
    assert len(PROMPT_TEMPLATES) == 13
    assert not (set(PROMPT_TEMPLATES) & REMOVED)
    for expected in ("sorter", "sorter_reviewer", "contracts_specialist",
                     "corporate_records_specialist", "correspondence_specialist",
                     "insurance_claims_specialist", "arbiter", "boss",
                     "reporter", "judge", "judge-classification",
                     "judge-correctness", "pdf_transcriber"):
        assert expected in PROMPT_TEMPLATES


def test_templates_are_substantive_text():
    for agent, template in PROMPT_TEMPLATES.items():
        assert isinstance(template, str) and len(template) > 200, agent


def test_prompt_name_contract():
    assert prompt_name("sorter") == "mailroom-sorter"
    assert prompt_name("judge-correctness") == "mailroom-judge-correctness"


def test_override_loader(tmp_path):
    override = tmp_path / "prompts.json"
    override.write_text(json.dumps({"sorter": "CUSTOM"}))
    loaded = load_prompt_templates(str(override))
    assert loaded == {"sorter": "CUSTOM"}


def test_override_loader_rejects_bad_shape(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"sorter": 42}))
    with pytest.raises(ValueError):
        load_prompt_templates(str(bad))


def test_schema_roster_consistency():
    """The schema's specialist mapping must only reference agents that exist
    in the prompt registry or are non-LLM roles (transcriber/image)."""
    from mailroom_ui.pipeline_schema import SPECIALIST_BY_DOC_CLASS

    for doc_class, specialist in SPECIALIST_BY_DOC_CLASS.items():
        assert specialist in PROMPT_TEMPLATES, f"{doc_class} -> {specialist} has no prompt"


def test_docclass_registry_shape():
    """KANBAN-090 mirror + pilot-universe variants: 31 docclass prompts."""
    from mailroom_ui.docclass_prompts import DOCLASS_PROMPT_VERSIONS, load_docclass_templates

    assert len(DOCLASS_PROMPT_VERSIONS) == 31
    for key, template in DOCLASS_PROMPT_VERSIONS.items():
        assert isinstance(template, str) and len(template) > 200, key
    assert load_docclass_templates() == DOCLASS_PROMPT_VERSIONS


def test_docclass_override_loader(tmp_path):
    from mailroom_ui.docclass_prompts import load_docclass_templates

    override = tmp_path / "docclass.json"
    override.write_text(json.dumps({"sorter_docclass_v0": "CUSTOM"}))
    assert load_docclass_templates(str(override)) == {"sorter_docclass_v0": "CUSTOM"}
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"sorter_docclass_v0": 42}))
    with pytest.raises(ValueError):
        load_docclass_templates(str(bad))

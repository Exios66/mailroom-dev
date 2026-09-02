#!/usr/bin/env python3
"""Document-class taxonomy parity gate (HUB-019, plan §65/§65A).

Fails (exit 1) when the surfaces that state which document classes are LIVE
ever disagree about the canonical five-class set. The literal source of truth
is ``HUB_CLASSES`` in ``packages/llm-mailroom/src/pipeline/hf_corpora.py`` —
every check diffs against that constant parsed straight out of the file, never
against a hand-maintained copy. ``docs/v7-taxonomy.md`` is the canonical prose
contract.

Strict surfaces (must equal the canonical five):

- ``hf_corpora.py`` ``HUB_CLASSES`` (the anchor itself)
- ``taxonomy.yaml`` ``doc_classes`` live entries (``status: retired`` entries
  are retained machinery, not live classes — docs/v7-taxonomy.md §4)
- llm-mailroom sorter output vocabulary (``sorter_agent.py`` ``DOC_CLASSES``)
- specialist registry coverage (``build_graph.py``
  ``_specialist_extractor_map`` must resolve every live class's specialist)
- ``docs/v7-taxonomy.md`` stated live + v7-represented class blocks
- dojo HF-corpus class universe (``corpus.py`` ``CORPUS_DOC_TYPES`` — pinned
  to ``Lucius-Morningstar/docclass-merged``)
- entity-repo pilot class universe (``PILOT_CLASS_KEYS`` — the docclass GT
  surface)
- sandbox docclass fixture (``docclass_mini.jsonl`` ``doc_type`` values)

Structural surfaces (documented compat/retirement remnants — must CONTAIN the
canonical five up to the documented extract alias ``merger_agreement →
contract``, and may only add classes from the retired roster):

- dojo ``config.py`` ``DOC_CLASS_KEYS`` / ``LIVE_DOC_CLASS_KEYS`` /
  ``RETIRED_DOC_CLASS_KEYS``
- dojo ``mailroom.py`` ``LIVE_DOC_TYPES`` / ``RETIRED_DOC_TYPES`` /
  ``EXTRACT_CLASS_ALIASES``
- entity-repo ``sorter_agent.py`` ``DOC_CLASSES`` / ``DOCCLASS_CLASS_KEYS``

Retired classes (plan §60): ``compliance_filing``, ``court_opinion``,
``due_diligence``. They are former classes, not "extended taxonomy awaiting
coverage"; a surface listing them is tolerated only under the structural
rule above. Reintroducing one as live is a fresh taxonomy decision requiring
its own ``taxonomy_version`` bump — this gate must never learn them as live.

Usage:
    python scripts/taxonomy_parity.py [--json] [--root PATH]

Exit 0 = parity holds; exit 1 = drift (readable diagnostics listed). Stdlib
only, network-free; modeled on the ``github_labels.py audit`` CI-gate pattern.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Plan §60 retired roster — former classes, tolerated only as remnants.
RETIRED_ROSTER = frozenset({"compliance_filing", "court_opinion", "due_diligence"})

#: Documented extract alias (dojo mailroom.py): merger extracts via the
#: contracts specialist / ContractExtraction while staying a distinct class.
#: docs/v7-taxonomy.md; plan §6/§59/§81.
KNOWN_EXTRACT_ALIASES = frozenset({"merger_agreement"})

HF_CORPORA = "packages/llm-mailroom/src/pipeline/hf_corpora.py"
TAXONOMY_YAML = "packages/llm-mailroom/src/config/taxonomy.yaml"
MAILROOM_SORTER = "packages/llm-mailroom/src/langchain_agents/sorter_agent.py"
MAILROOM_GRAPH = "packages/llm-mailroom/src/graph/build_graph.py"
V7_TAXONOMY_DOC = "docs/v7-taxonomy.md"
DOJO_CORPUS = "packages/llm-dojo-scoring/llm_dojo_scoring/corpus.py"
DOJO_CONFIG = "packages/llm-dojo-scoring/llm_dojo_scoring/config.py"
DOJO_MAILROOM = "packages/llm-dojo-scoring/llm_dojo_scoring/mailroom.py"
ENTITY_SORTER = "packages/llm-entity-extraction/agents/sorter_agent.py"
SANDBOX_FIXTURE = "packages/local-mailroom-sandbox/data/fixtures/hf/docclass_mini.jsonl"


class Drift(Exception):
    """One parity violation, with the surface it was found on."""


def read(root: Path, rel: str) -> str:
    path = root / rel
    if not path.is_file():
        raise Drift(f"{rel}: file missing (expected by the parity gate)")
    return path.read_text(encoding="utf-8")


def module_assigns(source: str):
    """Parse a module and return {target_name: literal_value_or_None}.

    List ``+`` concatenations evaluate when every operand is a known literal;
    anything non-literal records None (the caller decides if that is fatal).
    """
    tree = ast.parse(source)
    values: dict[str, object] = {}

    def literal(node):
        try:
            return ast.literal_eval(node)
        except (ValueError, SyntaxError):
            return None

    def resolve(node):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = resolve(node.left), resolve(node.right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            return None
        if isinstance(node, ast.List):
            items = [resolve(item) for item in node.elts]
            return items if all(i is not None for i in items) else None
        if isinstance(node, ast.Name):
            return values.get(node.id)  # previously assigned literal (list concat)
        return literal(node)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            value = resolve(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            values[node.target.id] = resolve(node.value)
    return values


def function_return_literal(source: str, function: str):
    """Literal value returned by a top-level function (e.g. a dict literal)."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function:
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Return):
                    try:
                        return ast.literal_eval(stmt.value)
                    except (ValueError, SyntaxError, TypeError):
                        return None
    return None


def parse_doc_classes(source: str) -> list[dict]:
    """Minimal strict reader for taxonomy.yaml ``doc_classes`` entries.

    Only the scalar fields the gate needs (``key``, ``status``,
    ``specialist``, ``schema``) are read; anything the reader cannot follow
    is a hard error — a parity gate must never silently misparse.
    """
    lines = source.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == "doc_classes:":
            start = i + 1
            break
    if start is None:
        raise Drift("taxonomy.yaml: no top-level 'doc_classes:' block found")

    entries: list[dict] = []
    current: dict | None = None
    field_indent = None  # indent of an entry-level field (nested maps go deeper)
    for line in lines[start:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            break  # next top-level key: block over
        stripped = line.strip()
        is_item = stripped.startswith("- ")
        if is_item:
            if "key:" not in stripped:
                raise Drift(f"taxonomy.yaml: doc_classes list item without 'key:': {stripped!r}")
            current = {}
            entries.append(current)
            field_indent = indent + 2  # continuation fields align after "- "
            stripped = stripped[2:].strip()
            capture = True  # marker-line fields are entry-level by definition
        else:
            if current is None:
                raise Drift(f"taxonomy.yaml: unexpected line under doc_classes: {line.strip()!r}")
            if field_indent is not None and indent < field_indent:
                raise Drift(f"taxonomy.yaml: unexpected dedent inside doc_classes entry: {line.strip()!r}")
            capture = indent == field_indent
        if not capture or ":" not in stripped:
            continue
        field, _, value = stripped.partition(":")
        field = field.strip()
        if field in {"key", "status", "specialist", "schema"}:
            if field in current:
                raise Drift(f"taxonomy.yaml: duplicate field {field!r} in one doc_classes entry")
            current[field] = value.strip().strip("'\"")
    if not entries:
        raise Drift("taxonomy.yaml: doc_classes block parsed to zero entries")
    for entry in entries:
        if "key" not in entry:
            raise Drift("taxonomy.yaml: doc_classes entry missing 'key'")
    return entries


def parse_md_code_block(source: str, heading: str) -> list[str]:
    """Class list from the fenced block directly under a ```heading```.```"""
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == heading:
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip().startswith("```"):
                    block = []
                    for k in range(j + 1, len(lines)):
                        if lines[k].strip().startswith("```"):
                            if not block:
                                raise Drift(f"docs/v7-taxonomy.md: empty class block under {heading!r}")
                            return [v.strip() for v in block]
                        block.append(lines[k].strip())
                    raise Drift(f"docs/v7-taxonomy.md: unterminated code block under {heading!r}")
            raise Drift(f"docs/v7-taxonomy.md: no code block under {heading!r}")
    raise Drift(f"docs/v7-taxonomy.md: heading {heading!r} not found")


def check_equal(surface: str, got, canon: set[str]) -> list[str]:
    got_set = set(got)
    problems = []
    if len(got_set) != len(got):
        problems.append(f"{surface}: duplicate entries: {sorted(got_set ^ set(got)) or got}")
    if got_set != canon:
        problems.append(
            f"{surface}: expected exactly the canonical five {sorted(canon)}; "
            f"missing={sorted(canon - got_set)} unexpected={sorted(got_set - canon)}"
        )
    return problems


def check_structural(surface: str, got, canon: set[str], aliases: frozenset) -> list[str]:
    """Compat-surface rule: canon ⊆ got ∪ aliases; extras ⊆ retired roster."""
    got_set = set(got)
    covered = got_set | set(aliases)
    problems = []
    if not canon <= covered:
        problems.append(
            f"{surface}: missing live classes (beyond documented aliases "
            f"{sorted(aliases)}): {sorted(canon - covered)}"
        )
    illegal = got_set - canon - RETIRED_ROSTER
    if illegal:
        problems.append(
            f"{surface}: classes outside the canonical five and the retired "
            f"roster {sorted(RETIRED_ROSTER)}: {sorted(illegal)} — a new live "
            "class requires a taxonomy decision (plan §61/§62), not a silent add"
        )
    return problems


# --- surface checks (each appends readable problems) -----------------------


def check_hub_classes(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    if values.get("HUB_CLASSES") is None:
        raise Drift(f"{HF_CORPORA}: HUB_CLASSES not found / not a literal tuple")
    return check_equal(HF_CORPORA, values["HUB_CLASSES"], canon)


def check_taxonomy_yaml(source: str, canon: set[str]) -> list[str]:
    entries = parse_doc_classes(source)
    live = [e["key"] for e in entries if e.get("status") != "retired"]
    retired = [e["key"] for e in entries if e.get("status") == "retired"]
    problems = check_equal(f"{TAXONOMY_YAML} (live entries)", live, canon)
    outside = sorted(set(retired) - RETIRED_ROSTER)
    if outside:
        problems.append(
            f"{TAXONOMY_YAML}: entries marked 'status: retired' outside the "
            f"§60 retired roster: {outside}"
        )
    for entry in entries:
        if entry["key"] in canon:
            for field in ("specialist", "schema"):
                if not entry.get(field):
                    problems.append(f"{TAXONOMY_YAML}: live class {entry['key']!r} missing {field!r}")
    merger = next((e for e in entries if e["key"] == "merger_agreement"), None)
    if merger and merger.get("status") != "retired":
        if merger.get("specialist") != "contracts_specialist" or merger.get("schema") != "ContractExtraction":
            problems.append(
                f"{TAXONOMY_YAML}: merger_agreement must route to "
                "contracts_specialist / ContractExtraction while staying a "
                "distinct class (plan §6/§81); got "
                f"specialist={merger.get('specialist')!r} schema={merger.get('schema')!r}"
            )
    return problems


def check_mailroom_sorter(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    doc_classes = values.get("DOC_CLASSES")
    if not isinstance(doc_classes, list):
        raise Drift(f"{MAILROOM_SORTER}: DOC_CLASSES not found / not a literal list")
    keys = [d.get("key") for d in doc_classes if isinstance(d, dict)]
    return check_equal(MAILROOM_SORTER, keys, canon)


def check_specialist_registry(source: str, yaml_source: str, canon: set[str]) -> list[str]:
    mapping = function_return_literal(source, "_specialist_extractor_map") or {}
    entries = parse_doc_classes(yaml_source)
    live_specialists = {
        e.get("specialist") for e in entries if e["key"] in canon and e.get("status") != "retired"
    }
    missing = sorted(s for s in live_specialists if s not in mapping)
    if missing:
        return [
            f"{MAILROOM_GRAPH}: _specialist_extractor_map does not resolve live "
            f"specialists {missing} — dispatch would fail at runtime"
        ]
    return []


def check_v7_doc(source: str, canon: set[str]) -> list[str]:
    problems = []
    problems += check_equal(
        f"{V7_TAXONOMY_DOC} (Live Mailroom document classes)",
        parse_md_code_block(source, "### Live Mailroom document classes"),
        canon,
    )
    problems += check_equal(
        f"{V7_TAXONOMY_DOC} (v7 represented document classes)",
        parse_md_code_block(source, "### v7 represented document classes"),
        canon,
    )
    return problems


def check_dojo_corpus(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    doc_types = values.get("CORPUS_DOC_TYPES")
    if doc_types is None:
        raise Drift(f"{DOJO_CORPUS}: CORPUS_DOC_TYPES not found / not a literal tuple")
    problems = check_equal(f"{DOJO_CORPUS} (HF corpus represented classes)", doc_types, canon)
    absent = values.get("CORPUS_ABSENT_DOC_TYPES")
    if absent is not None:
        outside = sorted(set(absent) - RETIRED_ROSTER)
        if outside:
            problems.append(
                f"{DOJO_CORPUS}: CORPUS_ABSENT_DOC_TYPES outside the §60 retired "
                f"roster: {outside}"
            )
    return problems


def check_dojo_config(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    problems = []
    for name in ("DOC_CLASS_KEYS", "LIVE_DOC_CLASS_KEYS"):
        got = values.get(name)
        if got is None:
            raise Drift(f"{DOJO_CONFIG}: {name} not found / not a literal list")
        problems += check_structural(f"{DOJO_CONFIG} {name}", got, canon, KNOWN_EXTRACT_ALIASES)
    retired = values.get("RETIRED_DOC_CLASS_KEYS")
    if retired is None:
        raise Drift(f"{DOJO_CONFIG}: RETIRED_DOC_CLASS_KEYS not found / not a literal list")
    outside = sorted(set(retired) - RETIRED_ROSTER)
    if outside:
        problems.append(f"{DOJO_CONFIG} RETIRED_DOC_CLASS_KEYS outside the §60 roster: {outside}")
    return problems


def check_dojo_mailroom(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    problems = []
    live = values.get("LIVE_DOC_TYPES")
    if live is None:
        raise Drift(f"{DOJO_MAILROOM}: LIVE_DOC_TYPES not found / not a literal tuple")
    aliases = values.get("EXTRACT_CLASS_ALIASES")
    if not isinstance(aliases, dict):
        raise Drift(f"{DOJO_MAILROOM}: EXTRACT_CLASS_ALIASES not found / not a literal dict")
    problems += check_structural(
        f"{DOJO_MAILROOM} LIVE_DOC_TYPES", live, canon, frozenset(aliases)
    )
    unknown_alias_targets = sorted(v for v in aliases.values() if v not in live and v not in canon)
    if unknown_alias_targets:
        problems.append(
            f"{DOJO_MAILROOM}: EXTRACT_CLASS_ALIASES targets outside LIVE_DOC_TYPES "
            f"and the canonical five: {unknown_alias_targets}"
        )
    retired = values.get("RETIRED_DOC_TYPES")
    if retired is None:
        raise Drift(f"{DOJO_MAILROOM}: RETIRED_DOC_TYPES not found / not a literal tuple")
    outside = sorted(set(retired) - RETIRED_ROSTER)
    if outside:
        problems.append(f"{DOJO_MAILROOM} RETIRED_DOC_TYPES outside the §60 roster: {outside}")
    return problems


def check_entity_sorter(source: str, canon: set[str]) -> list[str]:
    values = module_assigns(source)
    pilot = values.get("PILOT_CLASS_KEYS")
    if pilot is None:
        raise Drift(f"{ENTITY_SORTER}: PILOT_CLASS_KEYS not found / not a literal list")
    problems = check_equal(f"{ENTITY_SORTER} (pilot class universe)", pilot, canon)
    base = values.get("DOC_CLASSES") or []
    if not base:
        raise Drift(f"{ENTITY_SORTER}: DOC_CLASSES not found / not a literal list")
    extended = values.get("DOCCLASS_CLASSES")
    if not isinstance(extended, list):
        raise Drift(
            f"{ENTITY_SORTER}: DOCCLASS_CLASSES not resolvable as a literal "
            "concatenation — sorter surface changed shape?"
        )
    keys = [d.get("key") for d in extended if isinstance(d, dict)]
    problems += check_structural(
        f"{ENTITY_SORTER} DOCCLASS_CLASS_KEYS", keys, canon, KNOWN_EXTRACT_ALIASES
    )
    return problems


def check_sandbox_fixture(source: str, canon: set[str]) -> list[str]:
    allowed = canon | {"unknown"}
    problems = []
    for n, line in enumerate(source.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Drift(f"{SANDBOX_FIXTURE}:{n}: not valid JSONL: {exc}")
        doc_type = row.get("doc_type")
        if doc_type not in allowed:
            problems.append(
                f"{SANDBOX_FIXTURE}:{n}: doc_type {doc_type!r} outside the "
                "canonical five (plan §66/§67)"
            )
    return problems


# --- driver -----------------------------------------------------------------


def run_checks(root: Path) -> list[str]:
    hf = read(root, HF_CORPORA)
    values = module_assigns(hf)
    hub = values.get("HUB_CLASSES")
    if hub is None:
        raise Drift(f"{HF_CORPORA}: HUB_CLASSES not found / not a literal tuple")
    canon = set(hub)
    if len(canon) != len(hub):
        raise Drift(f"{HF_CORPORA}: HUB_CLASSES contains duplicates: {sorted(hub)}")
    if not canon:
        raise Drift(f"{HF_CORPORA}: HUB_CLASSES is empty")

    problems: list[str] = []
    problems += check_hub_classes(hf, canon)
    problems += check_taxonomy_yaml(read(root, TAXONOMY_YAML), canon)
    problems += check_mailroom_sorter(read(root, MAILROOM_SORTER), canon)
    problems += check_specialist_registry(read(root, MAILROOM_GRAPH), read(root, TAXONOMY_YAML), canon)
    problems += check_v7_doc(read(root, V7_TAXONOMY_DOC), canon)
    problems += check_dojo_corpus(read(root, DOJO_CORPUS), canon)
    problems += check_dojo_config(read(root, DOJO_CONFIG), canon)
    problems += check_dojo_mailroom(read(root, DOJO_MAILROOM), canon)
    problems += check_entity_sorter(read(root, ENTITY_SORTER), canon)
    problems += check_sandbox_fixture(read(root, SANDBOX_FIXTURE), canon)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repo root override (tests)")
    args = parser.parse_args(argv)

    try:
        problems = run_checks(args.root)
    except Drift as exc:
        if args.json:
            print(json.dumps({"ok": False, "errors": [str(exc)], "drift": []}, indent=2))
        else:
            print(f"TAXONOMY PARITY: STRUCTURAL ERROR\n  {exc}")
        return 1

    if args.json:
        print(json.dumps({"ok": not problems, "drift": problems}, indent=2))
    elif problems:
        print("TAXONOMY PARITY: DRIFT DETECTED (plan §65A)")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nCanonical source: HUB_CLASSES in packages/llm-mailroom/src/"
            "pipeline/hf_corpora.py; prose contract: docs/v7-taxonomy.md."
        )
    else:
        print("TAXONOMY PARITY: OK — all surfaces agree on the canonical five-class set")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

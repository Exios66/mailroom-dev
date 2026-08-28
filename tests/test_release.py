"""scripts/release.py: version bump + Unreleased → dated section (no duplication)."""

from __future__ import annotations

from pathlib import Path

from scripts.release import (
    bump_version,
    current_version,
    parse_changelog,
    release_changelog,
    write_version,
)

CHANGELOG_FIXTURE = """# Changelog

## [Unreleased]

### Added

- New feature one.
- New feature two.

### Fixed

- A bug.

## [0.2.0] - 2026-08-24

### Added
- Old stuff.
"""


def test_bump_minor():
    assert bump_version((0, 2, 0), "minor") == (0, 3, 0)
    assert bump_version((0, 2, 0), "patch") == (0, 2, 1)
    assert bump_version((0, 2, 0), "major") == (1, 0, 0)


def test_release_changelog_moves_unreleased(tmp_path: Path):
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG_FIXTURE)
    (tmp_path / "pyproject.toml").write_text('version = "0.2.0"\n')
    write_version((0, 3, 0), root=tmp_path)
    assert current_version(tmp_path) == (0, 3, 0)
    release_changelog((0, 3, 0), "review resolve, live floor, skills", root=tmp_path)
    text = (tmp_path / "CHANGELOG.md").read_text()
    bullets, headers = parse_changelog(tmp_path)
    assert bullets == []
    assert headers[0] == "0.3.0"
    assert headers.count("0.3.0") == 1
    assert text.count("New feature one.") == 1
    assert text.count("A bug.") == 1
    assert "## [Unreleased]" in text
    assert "review resolve, live floor, skills" in text
    # Historical section stays put.
    assert "## [0.2.0] - 2026-08-24" in text
    assert text.index("## [Unreleased]") < text.index("## [0.3.0]")
    assert text.index("## [0.3.0]") < text.index("## [0.2.0]")

"""Wikilink helpers."""

from __future__ import annotations

from pathlib import Path

from scripts.wikilinks import extract_wikilink_targets, find_resolved_path_for_link


def test_extract_wikilink_targets_handles_alias() -> None:
    """Left side of pipe is the link target."""
    md = "See [[Real Title|display]] and [[Only]]."
    assert extract_wikilink_targets(md) == ["Real Title", "Only"]


def test_find_resolved_path_for_link(tmp_path) -> None:
    """Resolve by stem match."""
    wiki = tmp_path / "wiki"
    (wiki / "concepts").mkdir(parents=True)
    p = wiki / "concepts" / "foo-bar.md"
    p.write_text("---\ntitle: x\n---\n", encoding="utf-8")
    found = find_resolved_path_for_link("Foo Bar", wiki)
    assert found == p.resolve()

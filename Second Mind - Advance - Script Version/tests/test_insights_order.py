"""Insight listing order (importance, then recency)."""

from __future__ import annotations

from scripts.insights import list_pending_insights


def test_pending_insights_sorted_high_before_low(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("KNS_REPO_ROOT", str(tmp_path))
    wiki = tmp_path / "wiki"
    (wiki / "insights").mkdir(parents=True)
    (wiki / "concepts").mkdir(parents=True)
    (wiki / "concepts" / "low.md").write_text(
        "---\n"
        "title: Low Note\n"
        "tags:\n  - domain/x\n  - type/concept\n"
        "wiki_path: concepts/low.md\n"
        "source: s\n"
        "confidence: 0.5\n"
        "importance: low\n"
        "---\n\nx\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "high.md").write_text(
        "---\n"
        "title: High Note\n"
        "tags:\n  - domain/x\n  - type/concept\n"
        "wiki_path: concepts/high.md\n"
        "source: s\n"
        "confidence: 0.5\n"
        "importance: high\n"
        "---\n\nx\n",
        encoding="utf-8",
    )
    (wiki / "insights" / "low-note.md").write_text(
        "---\nlinked_note: concepts/low.md\nstatus: pending\n---\n\n# Insight: Low Note\n",
        encoding="utf-8",
    )
    (wiki / "insights" / "high-note.md").write_text(
        "---\nlinked_note: concepts/high.md\nstatus: pending\n---\n\n# Insight: High Note\n",
        encoding="utf-8",
    )
    rows = list_pending_insights()
    assert [r.title for r in rows] == ["High Note", "Low Note"]

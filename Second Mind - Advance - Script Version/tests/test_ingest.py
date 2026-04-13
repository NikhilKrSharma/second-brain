"""Tests for ingest helpers."""

from __future__ import annotations

from scripts.ingest import parse_multi_markdown_notes, split_frontmatter, write_wiki_from_llm_output
from scripts.routing import normalize_wiki_path, slugify_title


def test_split_frontmatter_parses_lists() -> None:
    """Lists in YAML frontmatter parse correctly."""
    md = "---\ntitle: T\ntags:\n  - domain/genai\n---\n\nBody\n"
    fields, body = split_frontmatter(md)
    assert fields["title"] == "T"
    assert fields["tags"] == ["domain/genai"]
    assert body.strip() == "Body"


def test_slugify_title() -> None:
    """Slugify produces safe stems."""
    assert slugify_title("Hello World!") == "hello-world"


def test_normalize_wiki_path_from_type_concept() -> None:
    """Concept type routes to concepts folder."""
    path = normalize_wiki_path(
        "wrong/foo.md",
        tags=["domain/genai", "type/concept"],
        title="Attention",
    )
    assert path.startswith("concepts/")
    assert path.endswith(".md")


def test_align_moves_summaries_to_concepts_for_type_concept() -> None:
    """Type concept forces concepts/ even if the model suggested summaries/."""
    from scripts.routing import align_wiki_path_with_type_tags

    path, changed = align_wiki_path_with_type_tags(
        "summaries/my-note.md",
        tags=["domain/ml", "type/concept"],
        title="My Note",
    )
    assert changed is True
    assert path == "concepts/my-note.md"


def test_write_wiki_from_llm_output_respects_wiki_path(
    tmp_path,
    monkeypatch,
) -> None:
    """Notes write under wiki_path inside the wiki root with strict schema."""
    monkeypatch.setenv("KNS_REPO_ROOT", str(tmp_path))
    (tmp_path / "wiki").mkdir()

    md = """---
title: Hello World
tags:
  - domain/genai
  - type/concept
wiki_path: concepts/hello.md
source: raw/inbox/x.md
confidence: 0.9
importance: high
---

# Hi
"""
    outcome = write_wiki_from_llm_output(md, source_relative="raw/inbox/x.md")
    assert outcome.path == tmp_path / "wiki" / "concepts" / "hello.md"
    text = outcome.path.read_text(encoding="utf-8")
    assert "title: Hello World" in text
    assert "confidence:" in text
    assert "source:" in text
    assert "importance: high" in text
    stub = (tmp_path / "wiki" / "insights" / "hello-world.md").read_text(encoding="utf-8")
    assert "linked_note: concepts/hello.md" in stub
    assert "status: pending" in stub


def test_non_atomic_note_warning(tmp_path, monkeypatch) -> None:
    """Long bodies trigger atomicity warning."""
    monkeypatch.setenv("KNS_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("KNS_MAX_NOTE_WORDS", "5")
    (tmp_path / "wiki").mkdir()
    body = "word " * 20
    md = f"""---
title: Long
tags:
  - domain/x
  - type/concept
wiki_path: concepts/long.md
source: s
confidence: 0.9
---

{body}
"""
    outcome = write_wiki_from_llm_output(md, source_relative="s")
    assert outcome.path is not None
    assert any("Non-atomic note" in w for w in outcome.warnings)


def test_parse_multi_markdown_notes_splits_two() -> None:
    """Two frontmatter documents separated by blank line + ---."""
    blob = """---
title: A
tags:
  - domain/x
  - type/concept
wiki_path: concepts/a.md
source: s
confidence: 0.9
importance: low
---

Body A

---
title: B
tags:
  - domain/x
  - type/concept
wiki_path: concepts/b.md
source: s
confidence: 0.9
importance: high
---

Body B
"""
    parts = parse_multi_markdown_notes(blob)
    assert len(parts) == 2
    f0, b0 = split_frontmatter(parts[0])
    f1, b1 = split_frontmatter(parts[1])
    assert f0["title"] == "A"
    assert f1["title"] == "B"
    assert "Body A" in b0
    assert "Body B" in b1


def test_default_importance_medium_when_omitted(tmp_path, monkeypatch) -> None:
    """Missing importance is persisted as medium in written frontmatter."""
    monkeypatch.setenv("KNS_REPO_ROOT", str(tmp_path))
    (tmp_path / "wiki").mkdir()
    md = """---
title: No Imp
tags:
  - domain/x
  - type/concept
wiki_path: concepts/no-imp.md
source: s
confidence: 0.9
---

x
"""
    outcome = write_wiki_from_llm_output(md, source_relative="s")
    text = outcome.path.read_text(encoding="utf-8")
    assert "importance: medium" in text

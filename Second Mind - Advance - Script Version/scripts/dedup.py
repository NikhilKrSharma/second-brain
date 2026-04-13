"""Lightweight duplicate detection against existing wiki notes."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from pathlib import Path

from scripts.paths import wiki_dir


def _normalize_title(text: str) -> str:
    """Lowercase alphanumerics for fuzzy compare."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def title_similarity(a: str, b: str) -> float:
    """Return 0–1 string similarity for titles."""
    na = _normalize_title(a)
    nb = _normalize_title(b)
    if not na or not nb:
        return 0.0
    return float(SequenceMatcher(None, na, nb).ratio())


def _parse_title_from_frontmatter(text: str) -> str | None:
    """Extract ``title:`` from simple YAML frontmatter if present."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None
    block = match.group(1)
    for line in block.splitlines():
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def iter_wiki_markdown_files(root: Path | None = None) -> list[Path]:
    """List ``*.md`` under ``wiki/``."""
    base = root if root is not None else wiki_dir()
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.md") if p.is_file())


def index_wiki_titles(
    root: Path | None = None,
    *,
    skip_insights: bool = False,
) -> list[tuple[Path, str]]:
    """Return ``(path, title)`` for each wiki note.

    Args:
        root: Wiki root; default :func:`scripts.paths.wiki_dir`.
        skip_insights: When True, omit ``insights/`` (avoid matching insight stubs).
    """
    base = root if root is not None else wiki_dir()
    base_resolved = base.resolve()
    items: list[tuple[Path, str]] = []
    for path in iter_wiki_markdown_files(root):
        if skip_insights:
            try:
                rel = path.resolve().relative_to(base_resolved)
                if rel.parts and rel.parts[0] == "insights":
                    continue
            except ValueError:
                continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        title = _parse_title_from_frontmatter(text)
        if not title:
            title = path.stem.replace("-", " ")
        items.append((path, title))
    return items


def find_similar_notes(
    title_hint: str,
    *,
    threshold: float,
    root: Path | None = None,
    max_notes: int = 8,
    skip_insights: bool = True,
) -> list[tuple[Path, str, float]]:
    """Return existing notes similar to ``title_hint``, sorted by score descending.

    Used **before** LLM generation to surface related pages and reduce duplicates.
    """
    hint = title_hint.strip()
    if not hint:
        return []

    scored: list[tuple[Path, str, float]] = []
    for path, title in index_wiki_titles(root, skip_insights=skip_insights):
        score = title_similarity(hint, title)
        if score >= threshold:
            scored.append((path, title, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:max_notes]


def find_most_similar_title(
    new_title: str,
    *,
    threshold: float,
    root: Path | None = None,
    exclude_path: Path | None = None,
    skip_insights: bool = True,
) -> tuple[Path | None, float]:
    """Find an existing note whose title is similar above ``threshold``.

    Returns:
        ``(path, score)`` or ``(None, 0.0)`` if no match.
    """
    best_path: Path | None = None
    best_score = 0.0
    exclude_resolved = exclude_path.resolve() if exclude_path else None
    for path, title in index_wiki_titles(root, skip_insights=skip_insights):
        if exclude_resolved and path.resolve() == exclude_resolved:
            continue
        score = title_similarity(new_title, title)
        if score > best_score:
            best_score = score
            best_path = path
    if best_path is None or best_score < threshold:
        return None, 0.0
    return best_path, best_score


def find_duplicate_pairs(*, threshold: float, root: Path | None = None) -> list[tuple[Path, Path, float]]:
    """Find unordered pairs of distinct notes with title similarity ≥ threshold."""
    items = index_wiki_titles(root, skip_insights=False)
    pairs: list[tuple[Path, Path, float]] = []
    for i, (pa, ta) in enumerate(items):
        for pb, tb in items[i + 1 :]:
            score = title_similarity(ta, tb)
            if score >= threshold:
                pairs.append((pa, pb, score))
    return pairs

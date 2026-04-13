"""Wiki path routing from tags and validation against allowed roots."""

from __future__ import annotations

import re
from typing import Any

_ALLOWED_ROOTS = frozenset({"concepts", "topics", "systems", "projects", "summaries"})


def slugify_title(title: str) -> str:
    """Create a conservative filename stem from a title."""
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "note"


def _folder_from_type_tag(tag: str) -> str | None:
    """Map a ``type/...`` tag to a wiki top-level folder."""
    tag = tag.strip().lower()
    if tag.startswith("type/concept"):
        return "concepts"
    if tag.startswith("type/topic"):
        return "topics"
    if tag.startswith("type/system") or tag.startswith("type/workflow"):
        return "systems"
    if tag.startswith("type/project"):
        return "projects"
    if tag.startswith("type/paper") or tag.startswith("type/idea"):
        return "summaries"
    return None


def infer_wiki_folder_from_tags(tags: list[Any]) -> str:
    """Pick wiki root folder from ``type/*`` tags; default ``summaries``."""
    for raw in tags:
        if not isinstance(raw, str):
            continue
        folder = _folder_from_type_tag(raw)
        if folder is not None:
            return folder
    return "summaries"


def infer_wiki_path_from_tags(*, tags: list[Any], title: str) -> str:
    """Build ``<folder>/<slug>.md`` from tags and title."""
    folder = infer_wiki_folder_from_tags(tags)
    return f"{folder}/{slugify_title(title)}.md"


def first_path_segment(wiki_path: str) -> str:
    """Return first segment of a normalized relative wiki path."""
    cleaned = wiki_path.strip().strip("/").replace("\\", "/")
    if not cleaned:
        return ""
    return cleaned.split("/", 1)[0].lower()


def _basename_stem(path_like: str) -> str:
    """Return filename without directory, ``.md`` stripped."""
    name = path_like.split("/")[-1]
    if name.lower().endswith(".md"):
        return name[:-3]
    return name


def align_wiki_path_with_type_tags(
    wiki_path: str,
    *,
    tags: list[Any],
    title: str,
) -> tuple[str, bool]:
    """Force ``wiki_path`` root to match ``type/*`` tags when mappable.

    Returns:
        ``(path, changed)`` where *changed* is True if the path was rewritten.
    """
    required = infer_wiki_folder_from_tags(tags)
    current = first_path_segment(wiki_path)
    if current == required:
        return wiki_path, False

    stem = _basename_stem(wiki_path)
    if not stem:
        stem = slugify_title(title)
    filename = stem if stem.lower().endswith(".md") else f"{stem}.md"
    return f"{required}/{filename}", True


def normalize_wiki_path(
    wiki_path: str | None,
    *,
    tags: list[Any],
    title: str,
) -> str:
    """Ensure ``wiki_path`` lives under an allowed root, using tags when needed.

    If ``wiki_path`` is missing or its root is not allowed, infer from tags.
    If root is wrong, reuse the candidate filename when possible.
    """
    inferred = infer_wiki_path_from_tags(tags=tags, title=title)
    if not wiki_path or not str(wiki_path).strip():
        return inferred

    candidate = str(wiki_path).strip().strip("/").replace("\\", "/")
    root = first_path_segment(candidate)
    if root in _ALLOWED_ROOTS:
        return candidate

    stem = _basename_stem(candidate)
    slug = stem if stem else slugify_title(title)
    folder = infer_wiki_folder_from_tags(tags)
    if not slug.lower().endswith(".md"):
        slug = f"{slug}.md"
    return f"{folder}/{slug}"

"""Load prompt templates from ``prompts/``."""

from __future__ import annotations

from pathlib import Path

from scripts.paths import prompts_dir

_TEMPLATE_NAMES = {
    "general": "general_ingestion.md",
    "paper": "research_paper.md",
    "youtube": "youtube.md",
    "blog": "blog_article.md",
    "refine": "refine.md",
    "split": "split.md",
}


def load_template(name: str) -> str:
    """Load a prompt template by logical name.

    Args:
        name: One of ``general``, ``paper``, ``youtube``, ``blog``, ``refine``, ``split``.

    Returns:
        Template file contents.

    Raises:
        KeyError: If ``name`` is unknown.
        FileNotFoundError: If the template file is missing.
    """
    if name not in _TEMPLATE_NAMES:
        raise KeyError(f"Unknown template {name!r}; expected one of {sorted(_TEMPLATE_NAMES)}")
    path: Path = prompts_dir() / _TEMPLATE_NAMES[name]
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def resolve_template_for_relative_raw(relative_under_raw: Path) -> str:
    """Pick default template from the first folder under ``raw/``.

    Args:
        relative_under_raw: Path relative to ``raw/`` (file or dir).

    Returns:
        Template name for :func:`load_template`.
    """
    parts = relative_under_raw.parts
    if not parts:
        return "general"
    top = parts[0].lower()
    if top == "research_papers":
        return "paper"
    if top == "youtube":
        return "youtube"
    if top == "blogs":
        return "blog"
    return "general"

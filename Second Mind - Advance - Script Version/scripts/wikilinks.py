"""Wikilink extraction and optional placeholder creation."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.config import KnsConfig
from scripts.logging_utils import append_ingest_log
from scripts.paths import wiki_dir
from scripts.routing import slugify_title

_WIKILINK_RE = re.compile(r"\[\[([^\]]+?)]]")

# Trivial link targets — avoid placeholder spam (extend as needed).
_GENERIC_LINK_TOKENS = frozenset(
    {
        "system",
        "data",
        "model",
        "method",
        "methods",
        "result",
        "results",
        "paper",
        "work",
        "code",
        "time",
        "way",
        "idea",
        "ideas",
        "section",
        "figure",
        "table",
        "example",
        "examples",
        "note",
        "notes",
        "here",
        "above",
        "below",
    },
)


def extract_wikilink_targets(markdown: str) -> list[str]:
    """Return unique wikilink display targets (left side before ``|``)."""
    seen: list[str] = []
    for match in _WIKILINK_RE.finditer(markdown):
        inner = match.group(1).strip()
        if not inner:
            continue
        target = inner.split("|", 1)[0].strip()
        if target and target not in seen:
            seen.append(target)
    return seen


def wikilink_target_counts(markdown: str) -> dict[str, int]:
    """Count occurrences per wikilink target (before deduplication)."""
    counts: dict[str, int] = {}
    for match in _WIKILINK_RE.finditer(markdown):
        inner = match.group(1).strip()
        if not inner:
            continue
        target = inner.split("|", 1)[0].strip()
        if not target:
            continue
        counts[target] = counts.get(target, 0) + 1
    return counts


def should_create_placeholder(
    target: str,
    *,
    occurrence_count: int,
    min_occurrence: int,
) -> bool:
    """Decide if a broken link deserves a placeholder stub."""
    t = target.strip()
    if not t:
        return False
    if occurrence_count >= min_occurrence:
        return True
    tl = t.lower()
    if len(t) > 5 and tl not in _GENERIC_LINK_TOKENS:
        return True
    return False


def find_resolved_path_for_link(target: str, wiki_root: Path) -> Path | None:
    """Resolve a wikilink target to an existing ``wiki/**/*.md`` path if found."""
    clean = target.strip()
    if not clean:
        return None

    slug = slugify_title(clean)
    clean_lower = clean.lower()
    stem_hyphen = clean_lower.replace(" ", "-")

    base_resolved = wiki_root.resolve()
    for path in sorted(wiki_root.rglob("*.md")):
        try:
            rel = path.resolve().relative_to(base_resolved)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] == "insights":
            continue
        stem = path.stem
        stem_l = stem.lower()
        if stem_l == clean_lower or stem_l == stem_hyphen:
            return path
        if slugify_title(stem) == slug:
            return path
    return None


def validate_and_placeholder_wikilinks(
    body: str,
    *,
    cfg: KnsConfig,
) -> tuple[list[str], list[Path]]:
    """Find broken ``[[links]]``; optionally create selective ``wiki/concepts/`` stubs.

    Placeholders are created only when :func:`should_create_placeholder` passes.
    """
    broken: list[str] = []
    created: list[Path] = []
    root = wiki_dir()
    counts = wikilink_target_counts(body)

    for target in extract_wikilink_targets(body):
        resolved = find_resolved_path_for_link(target, root)
        if resolved is not None:
            continue
        broken.append(target)
        append_ingest_log(f"[WARN] broken_wikilink target={target!r}")
        if not cfg.enable_placeholder_links:
            continue
        occ = counts.get(target, 0)
        if not should_create_placeholder(
            target,
            occurrence_count=occ,
            min_occurrence=cfg.placeholder_min_occurrence,
        ):
            append_ingest_log(
                f"[INFO] placeholder_skipped target={target!r} count={occ} "
                f"(min_occ={cfg.placeholder_min_occurrence})",
            )
            continue
        slug = slugify_title(target)
        placeholder = (root / "concepts" / f"{slug}.md").resolve()
        try:
            placeholder.relative_to(root.resolve())
        except ValueError:
            continue
        if placeholder.is_file():
            continue
        placeholder.parent.mkdir(parents=True, exist_ok=True)
        text = (
            f"---\n"
            f"title: {target}\n"
            f"tags:\n  - domain/unknown\n  - type/concept\n"
            f"wiki_path: concepts/{slug}.md\n"
            f"source: placeholder\n"
            f"confidence: 0.3\n"
            f"importance: low\n"
            f"---\n\n"
            f"# {target}\n\n"
            f"(To be defined)\n"
        )
        placeholder.write_text(text, encoding="utf-8")
        created.append(placeholder)
        append_ingest_log(f"[INFO] placeholder_created path={placeholder} for_link={target!r}")

    return broken, created

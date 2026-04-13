"""Discover ingestible files under ``raw/``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.paths import raw_dir

_SKIP_NAMES = {".ds_store", "readme.txt", "readme.md"}
_ALLOWED_UNDERSCORE_DIRS = {"_high", "_low"}


@dataclass(frozen=True)
class RawSource:
    """A file discovered under ``raw/``."""

    path: Path
    relative: Path
    kind: str  # "markdown" | "text" | "pdf"
    priority: int  # 0 = inbox/_high, 1 = normal, 2 = inbox/_low


def _classify(path: Path) -> str | None:
    """Return file kind or None if not ingestible."""
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".txt":
        return "text"
    if suffix == ".pdf":
        return "pdf"
    return None


def _ingest_priority(relative: Path) -> int:
    """Return sort priority: lower is processed first."""
    parts = relative.parts
    if len(parts) >= 2 and parts[0] == "inbox":
        if parts[1] == "_high":
            return 0
        if parts[1] == "_low":
            return 2
    return 1


def _should_skip(path: Path) -> bool:
    """Return True if path segment indicates auxiliary or hidden content."""
    for part in path.parts:
        lowered = part.lower()
        if lowered in _SKIP_NAMES:
            return True
        if part.startswith(".") and part not in {".", ".."}:
            return True
        if part.startswith("_"):
            if part in _ALLOWED_UNDERSCORE_DIRS:
                continue
            return True
    return False


def discover_raw_sources() -> list[RawSource]:
    """Walk ``raw/`` and return ingestible sources in priority order.

    ``raw/inbox/_high`` is always before normal paths; ``raw/inbox/_low`` last.

    Returns:
        List of sources (markdown, text, pdf), excluding hidden and unknown ``_*``.
    """
    root = raw_dir()
    if not root.is_dir():
        return []

    out: list[RawSource] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if _should_skip(rel):
            continue
        kind = _classify(path)
        if kind is None:
            continue
        pri = _ingest_priority(rel)
        out.append(RawSource(path=path, relative=rel, kind=kind, priority=pri))

    out.sort(key=lambda s: (s.priority, s.relative.as_posix()))
    return out


def select_sources_by_limit(sources: list[RawSource], limit: int) -> list[RawSource]:
    """Take the first ``limit`` sources after priority ordering."""
    if limit <= 0:
        return []
    return sources[:limit]

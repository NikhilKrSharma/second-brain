"""Human insight-layer stubs linked to finalized wiki notes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts.logging_utils import append_ingest_log
from scripts.paths import wiki_dir
from scripts.routing import slugify_title

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def insight_stub_path(title: str) -> Path:
    """Path for the insight stub derived from note title."""
    slug = slugify_title(title)
    return wiki_dir() / "insights" / f"{slug}.md"


def wiki_relative_posix(path: Path) -> str:
    """Path of ``path`` relative to ``wiki/``, POSIX."""
    return path.resolve().relative_to(wiki_dir().resolve()).as_posix()


def ensure_insight_stub(*, title: str, linked_note: str) -> Path | None:
    """Create ``wiki/insights/<slug>.md`` if missing with YAML metadata.

    Args:
        title: Note title for heading and slug.
        linked_note: Path relative to ``wiki/`` (e.g. ``concepts/foo.md``).

    Returns:
        Path to stub (new or existing), or ``None`` if title empty.
    """
    title = title.strip()
    if not title:
        return None

    path = insight_stub_path(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        return path

    link = linked_note.strip() or "unknown"
    body = (
        "---\n"
        f"linked_note: {link}\n"
        "status: pending\n"
        "---\n\n"
        f"# Insight: {title}\n\n"
        "## My Understanding\n\n\n"
        "## Key Connections\n\n\n"
        "## Questions / Gaps\n\n\n"
    )
    path.write_text(body, encoding="utf-8")
    append_ingest_log(f"[INFO] insight_stub_created path={path} linked_note={link!r}")
    return path


def _importance_sort_key(level: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(level.lower(), 1)


def _importance_from_note_text(raw: str) -> str:
    """Parse ``importance`` from note YAML without importing ``ingest`` (avoid cycles)."""
    m = _FM_RE.match(raw)
    if not m:
        return "medium"
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return "medium"
    if not isinstance(data, dict):
        return "medium"
    imp = data.get("importance")
    if imp is None:
        return "medium"
    s = str(imp).strip().lower()
    return s if s in {"low", "medium", "high"} else "medium"


def _linked_note_importance_and_mtime(wiki_root: Path, linked_note: str) -> tuple[str, float]:
    """Read ``importance`` and mtime from the linked wiki note, if it exists."""
    link = (linked_note or "").strip()
    if not link or link == "unknown":
        return "medium", 0.0
    note_path = (wiki_root / link).resolve()
    if not note_path.is_file():
        return "medium", 0.0
    try:
        mtime = note_path.stat().st_mtime
    except OSError:
        mtime = 0.0
    try:
        raw = note_path.read_text(encoding="utf-8", errors="replace")
        imp = _importance_from_note_text(raw)
    except OSError:
        return "medium", mtime
    return imp, mtime


@dataclass(frozen=True)
class InsightRecord:
    """Parsed insight stub metadata for CLI listing."""

    path: Path
    title: str
    linked_note: str
    status: str
    importance: str
    note_mtime: float


def _title_from_insight_heading(text: str) -> str:
    """Extract title from ``# Insight: ...`` line."""
    for line in text.splitlines():
        if line.strip().lower().startswith("# insight:"):
            return line.split(":", 1)[1].strip()
    return ""


def load_insight_record(path: Path) -> InsightRecord:
    """Load one insight file into a flat record."""
    text = path.read_text(encoding="utf-8", errors="replace")
    linked = ""
    status = "pending"
    title = ""

    match = _FM_RE.match(text)
    if match:
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            data = None
        if isinstance(data, dict):
            linked = str(data.get("linked_note", "") or "")
            status = str(data.get("status", "pending") or "pending")
    title = _title_from_insight_heading(text) or path.stem.replace("-", " ")
    wiki_root = wiki_dir().resolve()
    importance, mtime = _linked_note_importance_and_mtime(wiki_root, linked)
    return InsightRecord(
        path=path,
        title=title,
        linked_note=linked,
        status=status.lower(),
        importance=importance,
        note_mtime=mtime,
    )


def list_pending_insights() -> list[InsightRecord]:
    """Return pending insight stubs sorted by linked-note importance, then recency."""
    root = wiki_dir() / "insights"
    if not root.is_dir():
        return []
    pending: list[InsightRecord] = []
    for path in sorted(root.glob("*.md")):
        if not path.is_file():
            continue
        rec = load_insight_record(path)
        if rec.status == "pending":
            pending.append(rec)
    pending.sort(
        key=lambda r: (_importance_sort_key(r.importance), -r.note_mtime),
    )
    return pending


def format_insight_recency(ts: float) -> str:
    """ISO UTC label for display; empty timestamp → ``unknown``."""
    if ts <= 0.0:
        return "unknown"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

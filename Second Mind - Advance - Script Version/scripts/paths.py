"""Repository path resolution."""

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    """Return the knowledge-system repository root.

    Uses ``KNS_REPO_ROOT`` when set; otherwise uses the parent of ``scripts/``.

    Returns:
        Absolute path to the repo root.

    Raises:
        RuntimeError: If ``KNS_REPO_ROOT`` is set but invalid.
    """
    env = os.environ.get("KNS_REPO_ROOT", "").strip()
    if env:
        root = Path(env).expanduser().resolve()
        if not root.is_dir():
            raise RuntimeError(f"KNS_REPO_ROOT is not a directory: {root}")
        return root

    return Path(__file__).resolve().parent.parent


def raw_dir() -> Path:
    """Path to ``raw/``."""
    return repo_root() / "raw"


def wiki_dir() -> Path:
    """Path to ``wiki/``."""
    return repo_root() / "wiki"


def prompts_dir() -> Path:
    """Path to ``prompts/``."""
    return repo_root() / "prompts"


def logs_dir() -> Path:
    """Path to ``logs/``."""
    return repo_root() / "logs"


def extracted_dir() -> Path:
    """Path for PDF text extracts (never written under ``raw/``)."""
    d = logs_dir() / "extracted"
    d.mkdir(parents=True, exist_ok=True)
    return d


def staged_dir() -> Path:
    """Path for LLM prompt bundles awaiting paste or API call."""
    d = logs_dir() / "staged"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ingest_log_path() -> Path:
    """Path to the append-only ingest log."""
    p = logs_dir() / "ingest.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

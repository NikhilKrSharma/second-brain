"""Environment-driven configuration for ingest and finalize."""

from __future__ import annotations

import os
from dataclasses import dataclass

# Defaults (overridable via environment)
MAX_NOTE_LENGTH: int = 2000
ENABLE_PLACEHOLDER_LINKS: bool = True
PRE_DEDUP_ENABLED: bool = True
PLACEHOLDER_MIN_OCCURRENCE: int = 2


@dataclass(frozen=True)
class KnsConfig:
    """Runtime options for deduplication, validation, and link handling."""

    dedup_mode: str
    dedup_threshold: float
    strict_frontmatter: bool
    max_note_words: int
    enable_placeholder_links: bool
    pre_dedup_enabled: bool
    placeholder_min_occurrence: int
    auto_split_oversized: bool
    learning_loop_enabled: bool


def _env_bool(key: str, default: bool) -> bool:
    """Parse a boolean environment variable."""
    raw = os.environ.get(key, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _env_int(key: str, default: int) -> int:
    """Parse a positive int environment variable."""
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer.") from exc
    if value < 1:
        raise ValueError(f"{key} must be >= 1.")
    return value


def load_config() -> KnsConfig:
    """Load config from environment variables.

    Returns:
        Parsed configuration with safe defaults.

    Raises:
        ValueError: If numeric env vars are invalid.
    """
    mode = os.environ.get("KNS_DEDUP_MODE", "skip").strip().lower()
    if mode not in {"skip", "append"}:
        mode = "skip"
    try:
        threshold = float(os.environ.get("KNS_DEDUP_THRESHOLD", "0.86"))
    except ValueError as exc:
        raise ValueError("KNS_DEDUP_THRESHOLD must be a float.") from exc
    if not 0 < threshold <= 1:
        raise ValueError("KNS_DEDUP_THRESHOLD must be in (0, 1].")
    strict = os.environ.get("KNS_STRICT_FRONTMATTER", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    max_words = _env_int("KNS_MAX_NOTE_WORDS", MAX_NOTE_LENGTH)
    placeholders = _env_bool("KNS_ENABLE_PLACEHOLDER_LINKS", ENABLE_PLACEHOLDER_LINKS)
    pre_dedup = _env_bool("KNS_PRE_DEDUP_ENABLED", PRE_DEDUP_ENABLED)
    ph_min = _env_int("KNS_PLACEHOLDER_MIN_OCCURRENCE", PLACEHOLDER_MIN_OCCURRENCE)
    auto_split = _env_bool("KNS_AUTO_SPLIT_OVERSIZED", True)
    learning = _env_bool("KNS_LEARNING_LOOP", False)
    return KnsConfig(
        dedup_mode=mode,
        dedup_threshold=threshold,
        strict_frontmatter=strict,
        max_note_words=max_words,
        enable_placeholder_links=placeholders,
        pre_dedup_enabled=pre_dedup,
        placeholder_min_occurrence=ph_min,
        auto_split_oversized=auto_split,
        learning_loop_enabled=learning,
    )

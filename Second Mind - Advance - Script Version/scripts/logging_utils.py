"""Lightweight file logging for ingest operations."""

from __future__ import annotations

from datetime import datetime, timezone

from scripts.paths import ingest_log_path


def append_ingest_log(message: str) -> None:
    """Append one UTF-8 line to ``logs/ingest.log`` with UTC timestamp.

    Args:
        message: Single-line message (newlines are stripped).
    """
    line = f"{datetime.now(timezone.utc).isoformat()} {message.strip().replace(chr(10), ' ')}"
    path = ingest_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")

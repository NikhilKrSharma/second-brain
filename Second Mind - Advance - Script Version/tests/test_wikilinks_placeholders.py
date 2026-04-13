"""Placeholder creation rules for broken wikilinks."""

from __future__ import annotations

from scripts.config import load_config
from scripts.wikilinks import should_create_placeholder, validate_and_placeholder_wikilinks


def test_should_create_placeholder_occurrence_threshold() -> None:
    """Repeated links qualify even when short or generic."""
    assert should_create_placeholder("system", occurrence_count=2, min_occurrence=2) is True
    assert should_create_placeholder("system", occurrence_count=1, min_occurrence=2) is False


def test_should_create_placeholder_long_nongeneric() -> None:
    """Single use of a long, non-generic target qualifies."""
    assert should_create_placeholder("Variational Autoencoder", occurrence_count=1, min_occurrence=2) is True


def test_should_create_placeholder_short_or_generic() -> None:
    """Single short or generic token does not qualify."""
    assert should_create_placeholder("data", occurrence_count=1, min_occurrence=2) is False
    assert should_create_placeholder("short", occurrence_count=1, min_occurrence=2) is False


def test_validate_skips_placeholder_for_single_generic(tmp_path, monkeypatch) -> None:
    """Integration: no stub file for one-off generic link."""
    monkeypatch.setenv("KNS_REPO_ROOT", str(tmp_path))
    (tmp_path / "wiki").mkdir()
    monkeypatch.setenv("KNS_ENABLE_PLACEHOLDER_LINKS", "true")
    monkeypatch.setenv("KNS_PLACEHOLDER_MIN_OCCURRENCE", "2")
    cfg = load_config()
    body = "Mention [[system]] once."
    broken, created = validate_and_placeholder_wikilinks(body, cfg=cfg)
    assert broken == ["system"]
    assert created == []

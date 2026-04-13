"""LLM-assisted refinement of existing wiki notes."""

from __future__ import annotations

from pathlib import Path

from scripts.ingest import call_chat_completions, llm_config_from_env, rebuild_markdown, split_frontmatter
from scripts.logging_utils import append_ingest_log
from scripts.paths import wiki_dir
from scripts.prompts import load_template


def resolve_note_path(arg: Path | str) -> Path:
    """Resolve CLI path to a file under ``wiki/`` or an absolute path."""
    p = Path(arg)
    if p.is_file():
        return p.resolve()
    candidate = (wiki_dir() / p).resolve()
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f"Note not found: {arg}")


def refine_wiki_note(note_path: Path) -> Path:
    """Improve note body clarity/structure via LLM; preserve frontmatter keys.

    Args:
        note_path: Path to an existing ``.md`` file under the vault.

    Returns:
        Path written (same as input).

    Raises:
        ValueError: If LLM is not configured or response is unusable.
    """
    cfg = llm_config_from_env()
    if cfg is None:
        raise ValueError("KNS_LLM_API_KEY is not set.")

    raw = note_path.read_text(encoding="utf-8")
    fields, body = split_frontmatter(raw)
    if not fields:
        raise ValueError("Note must have YAML frontmatter for refine.")

    system = load_template("refine")
    user = (
        "Improve ONLY the markdown body below. Do not add YAML. "
        "Preserve meaning and technical claims; tighten structure and wording.\n\n"
        f"--- BODY START ---\n{body.strip()}\n--- BODY END ---\n"
    )
    new_body = call_chat_completions(cfg=cfg, system=system, user=user).strip()
    if not new_body:
        raise ValueError("Empty refinement response.")

    out = rebuild_markdown(fields, new_body)
    note_path.write_text(out, encoding="utf-8")
    append_ingest_log(f"[INFO] refine_overwrite path={note_path}")
    return note_path

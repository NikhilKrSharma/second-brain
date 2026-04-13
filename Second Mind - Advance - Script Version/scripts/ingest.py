"""Build LLM prompt bundles and (optionally) call an OpenAI-compatible API."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from scripts.config import KnsConfig, load_config
from scripts.dedup import find_most_similar_title, find_similar_notes
from scripts.discover import RawSource, discover_raw_sources
from scripts.insights import ensure_insight_stub, wiki_relative_posix
from scripts.logging_utils import append_ingest_log
from scripts.paths import staged_dir, wiki_dir
from scripts.pdf_extract import extract_pdf_to_markdown
from scripts.prompts import load_template, resolve_template_for_relative_raw
from scripts.routing import align_wiki_path_with_type_tags, normalize_wiki_path
from scripts.wikilinks import validate_and_placeholder_wikilinks


@dataclass
class FinalizeOutcome:
    """Result of writing or skipping a finalized wiki note."""

    path: Path | None
    skipped_duplicate: bool
    duplicate_of: Path | None
    warnings: list[str]
    extra_paths: list[Path] = field(default_factory=list)


def _read_source_body(source: RawSource) -> str:
    """Read textual content for a raw source."""
    if source.kind == "pdf":
        extracted = extract_pdf_to_markdown(source.path)
        return extracted.read_text(encoding="utf-8")
    return source.path.read_text(encoding="utf-8", errors="replace")


def build_user_message(*, source: RawSource, body: str) -> str:
    """Build the user message wrapping raw content with provenance headers."""
    return (
        f"RAW_RELATIVE_PATH: {source.relative.as_posix()}\n"
        f"RAW_KIND: {source.kind}\n"
        f"RAW_ABSOLUTE_PATH: {source.path}\n\n"
        f"--- BEGIN RAW ---\n{body}\n--- END RAW ---\n"
    )


def augment_user_with_pre_dedup(user: str, source: RawSource, cfg: KnsConfig) -> str:
    """Append related-note context before the LLM call when enabled."""
    if not cfg.pre_dedup_enabled:
        return user
    hint = source.path.stem.replace("-", " ").replace("_", " ")
    similar = find_similar_notes(
        hint,
        threshold=cfg.dedup_threshold,
        max_notes=8,
        skip_insights=True,
    )
    if not similar:
        return user
    root = wiki_dir()
    lines = ["", "Related existing notes (avoid duplicating; prefer linking or updating):"]
    for path, existing_title, score in similar:
        rel = path.resolve().relative_to(root.resolve())
        lines.append(f'- "{existing_title}" → {rel.as_posix()} (similarity {score:.2f})')
    append_ingest_log(f"[INFO] pre_dedup_context hint={hint!r} count={len(similar)}")
    return user + "\n".join(lines) + "\n"


def write_staged_bundle(
    *,
    source: RawSource,
    template_name: str,
    system_preamble: str | None = None,
) -> Path:
    """Write a single prompt bundle to ``logs/staged/``."""
    cfg = load_config()
    template = load_template(template_name)
    if system_preamble:
        template = f"{system_preamble.strip()}\n\n{template}"

    body = _read_source_body(source)
    user = augment_user_with_pre_dedup(
        build_user_message(source=source, body=body),
        source,
        cfg,
    )

    staged = staged_dir()
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", source.relative.as_posix())
    out = staged / f"{safe}__{template_name}.bundle.txt"
    bundle = (
        "=== SYSTEM / INSTRUCTIONS (copy everything below 'SYSTEM:' to your system prompt "
        "or use as first message) ===\n\n"
        f"SYSTEM:\n{template}\n\n"
        "=== USER / RAW WRAPPED (second message) ===\n\n"
        f"{user}\n"
    )
    out.write_text(bundle, encoding="utf-8")
    append_ingest_log(f"[INFO] staged path={source.path} template={template_name} -> {out}")
    return out


def prepare_all_staged(template_override: str | None = None) -> list[Path]:
    """Stage bundles for every discoverable raw source."""
    written: list[Path] = []
    for source in discover_raw_sources():
        template = template_override or resolve_template_for_relative_raw(source.relative)
        written.append(write_staged_bundle(source=source, template_name=template))
    return written


@dataclass(frozen=True)
class LlmConfig:
    """OpenAI-compatible chat configuration."""

    base_url: str
    api_key: str
    model: str


def llm_config_from_env() -> LlmConfig | None:
    """Load LLM config from environment, or None if API key missing."""
    import os

    key = os.environ.get("KNS_LLM_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("KNS_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("KNS_LLM_MODEL", "gpt-4o-mini").strip()
    return LlmConfig(base_url=base, api_key=key, model=model)


def call_chat_completions(*, cfg: LlmConfig, system: str, user: str, timeout_s: int = 120) -> str:
    """POST a chat completion request; return assistant text."""
    url = f"{cfg.base_url}/chat/completions"
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"LLM HTTP {exc.code}: {detail}") from exc

    obj = json.loads(raw)
    try:
        return str(obj["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Unexpected LLM response JSON: {raw[:2000]}") from exc


def run_llm_for_source(
    source: RawSource,
    template_name: str,
    cfg: KnsConfig | None = None,
) -> str:
    """Run one LLM ingestion for a source; return assistant markdown."""
    cfg = cfg or load_config()
    llm_cfg = llm_config_from_env()
    if llm_cfg is None:
        raise ValueError("KNS_LLM_API_KEY is not set; use prepare workflow or set env vars.")

    system = load_template(template_name)
    body = _read_source_body(source)
    user = augment_user_with_pre_dedup(
        build_user_message(source=source, body=body),
        source,
        cfg,
    )
    return call_chat_completions(cfg=llm_cfg, system=system, user=user)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

_IMPORTANCE_LEVELS = frozenset({"low", "medium", "high"})
_MAX_AUTO_SPLIT_DEPTH = 1


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from markdown body using safe load."""
    match = _FRONTMATTER_RE.match(markdown)
    if not match:
        return {}, markdown

    fm = match.group(1)
    body = markdown[match.end() :]
    try:
        loaded = yaml.safe_load(fm)
    except yaml.YAMLError as exc:
        raise ValueError("Invalid YAML frontmatter.") from exc
    if loaded is None:
        return {}, body
    if not isinstance(loaded, dict):
        raise ValueError("Frontmatter must be a YAML mapping at the top level.")
    return loaded, body


def _coerce_tags(raw: Any, *, strict: bool) -> tuple[list[str], list[str]]:
    """Normalize tags to a list of strings."""
    warns: list[str] = []
    if raw is None:
        if strict:
            raise ValueError("Missing required field: tags")
        warns.append("[WARN] missing tags; defaulted to domain/unknown + type/concept")
        return ["domain/unknown", "type/concept"], warns
    if isinstance(raw, list):
        out = [str(t).strip() for t in raw if str(t).strip()]
        if not out:
            if strict:
                raise ValueError("tags list is empty")
            warns.append("[WARN] empty tags; defaulted")
            return ["domain/unknown", "type/concept"], warns
        return out, warns
    if strict:
        raise ValueError("tags must be a YAML list")
    warns.append("[WARN] coerced scalar tags to single-element list")
    return [str(raw).strip()], warns


def _coerce_importance(raw: Any, *, strict: bool) -> tuple[str, list[str]]:
    """Normalize ``importance`` to ``low`` | ``medium`` | ``high``."""
    warns: list[str] = []
    if raw is None:
        return "medium", warns
    s = str(raw).strip().lower()
    if s in _IMPORTANCE_LEVELS:
        return s, warns
    if strict:
        raise ValueError("importance must be one of: low, medium, high")
    warns.append("[WARN] invalid importance; defaulted to medium")
    return "medium", warns


def effective_importance(fields: dict[str, Any]) -> str:
    """Return importance for display/rebuild when the key may be absent (legacy notes)."""
    raw = fields.get("importance")
    if raw is None:
        return "medium"
    s = str(raw).strip().lower()
    return s if s in _IMPORTANCE_LEVELS else "medium"


def _coerce_confidence(raw: Any, *, strict: bool) -> tuple[float, list[str]]:
    """Normalize confidence to ``[0, 1]``."""
    warns: list[str] = []
    if raw is None:
        if strict:
            raise ValueError("Missing required field: confidence")
        warns.append("[WARN] missing confidence; defaulted to 0.7")
        return 0.7, warns
    try:
        value = float(raw)
    except (TypeError, ValueError):
        if strict:
            raise ValueError("confidence must be a float") from None
        warns.append("[WARN] invalid confidence; defaulted to 0.7")
        return 0.7, warns
    if not 0 <= value <= 1:
        if strict:
            raise ValueError("confidence must be between 0 and 1")
        warns.append("[WARN] confidence clamped to [0, 1]")
        value = max(0.0, min(1.0, value))
    return value, warns


def normalize_frontmatter(
    fields: dict[str, Any],
    *,
    source_fallback: str,
    strict: bool,
) -> tuple[dict[str, Any], list[str]]:
    """Enforce required keys and return cleaned fields plus warnings."""
    warnings: list[str] = []
    out = dict(fields)

    if "source_raw_path" in out:
        warnings.append("[WARN] removed deprecated key source_raw_path")
        out.pop("source_raw_path", None)

    title_raw = out.get("title")
    if title_raw is None or not str(title_raw).strip():
        if strict:
            raise ValueError("Missing required field: title")
        warnings.append("[WARN] missing title; defaulted to 'untitled'")
        out["title"] = "untitled"
    else:
        out["title"] = str(title_raw).strip()

    tags, w_tags = _coerce_tags(out.get("tags"), strict=strict)
    warnings.extend(w_tags)
    out["tags"] = tags

    src_raw = out.get("source")
    if src_raw is None or not str(src_raw).strip():
        out["source"] = source_fallback
        warnings.append("[WARN] filled source from raw path")
    else:
        out["source"] = str(src_raw).strip()

    conf, w_conf = _coerce_confidence(out.get("confidence"), strict=strict)
    warnings.extend(w_conf)
    out["confidence"] = conf

    imp, w_imp = _coerce_importance(out.get("importance"), strict=strict)
    warnings.extend(w_imp)
    out["importance"] = imp

    wiki_raw = out.get("wiki_path")
    wiki_str = str(wiki_raw).strip() if wiki_raw is not None else ""
    normalized = normalize_wiki_path(wiki_str or None, tags=tags, title=out["title"])
    if not wiki_str:
        warnings.append("[WARN] inferred wiki_path from tags/title")
    elif normalized != wiki_str.strip().strip("/").replace("\\", "/"):
        warnings.append(f"[WARN] adjusted wiki_path from {wiki_str!r} to {normalized!r}")
    aligned, type_aligned = align_wiki_path_with_type_tags(
        normalized,
        tags=tags,
        title=out["title"],
    )
    if type_aligned:
        warnings.append(
            f"[WARN] aligned wiki_path to type tag: {normalized!r} -> {aligned!r}",
        )
    out["wiki_path"] = aligned

    return out, warnings


def rebuild_markdown(fields: dict[str, Any], body: str) -> str:
    """Dump frontmatter with required keys first, then extras."""
    core_keys = ("title", "tags", "wiki_path", "source", "confidence", "importance")
    core: dict[str, Any] = {
        "title": fields["title"],
        "tags": fields["tags"],
        "wiki_path": fields["wiki_path"],
        "source": fields["source"],
        "confidence": fields["confidence"],
        "importance": effective_importance(fields),
    }
    extras = {k: v for k, v in fields.items() if k not in core_keys}
    merged: dict[str, Any] = {**core, **extras}
    fm = yaml.dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
    return f"---\n{fm}\n---\n\n{body.strip()}\n"


def _strip_outer_markdown_fence(text: str) -> str:
    """Remove a single outer ```markdown / ``` fence if the model wrapped output."""
    s = text.strip()
    if not s.startswith("```"):
        return s
    idx = s.find("\n")
    if idx == -1:
        return s
    rest = s[idx + 1 :]
    end_fence = rest.rfind("\n```")
    if end_fence == -1:
        return s
    return rest[:end_fence].strip()


def parse_multi_markdown_notes(text: str) -> list[str]:
    """Split assistant output that contains several YAML-frontmatter notes in sequence."""
    text = _strip_outer_markdown_fence(text)
    if not text.strip():
        return []
    parts: list[str] = []
    pos = 0
    n = len(text)
    sep = "\n\n---\n"
    while pos < n:
        m = _FRONTMATTER_RE.match(text[pos:])
        if not m:
            if not parts:
                return [text.strip()]
            break
        fm_end = pos + m.end()
        nxt = text.find(sep, fm_end)
        if nxt == -1:
            parts.append(text[pos:].strip())
            break
        parts.append(text[pos:nxt].strip())
        # Keep the next note's opening ``---`` (only skip the blank line between notes).
        pos = nxt + 2
    return [p for p in parts if p]


def _valid_split_documents(split_response: str) -> list[str]:
    """Keep only segments with parseable non-empty YAML frontmatter."""
    good: list[str] = []
    for doc in parse_multi_markdown_notes(split_response):
        try:
            fm, _ = split_frontmatter(doc)
        except ValueError:
            continue
        if fm:
            good.append(doc)
    return good


def call_split_note_llm(combined_markdown: str, *, timeout_s: int = 180) -> str:
    """Ask the LLM to split one oversized note into several atomic notes."""
    llm_cfg = llm_config_from_env()
    if llm_cfg is None:
        raise ValueError("KNS_LLM_API_KEY is not set")
    system = load_template("split")
    user = (
        "Split this into multiple atomic notes. Each note must represent one concept.\n\n"
        "Below is ONE markdown note (YAML frontmatter + body). "
        "Follow your system instructions for output format.\n\n"
        f"{combined_markdown.strip()}\n"
    )
    return call_chat_completions(cfg=llm_cfg, system=system, user=user, timeout_s=timeout_s)


def _merge_split_outcomes(outcomes: list[FinalizeOutcome]) -> FinalizeOutcome:
    """Combine results from a multi-part auto-split finalize."""
    warnings: list[str] = []
    paths_ok: list[Path] = []
    dup_of: Path | None = None
    all_skipped = True
    for o in outcomes:
        warnings.extend(o.warnings)
        if o.path is not None:
            paths_ok.append(o.path)
            all_skipped = False
        if o.duplicate_of is not None and dup_of is None:
            dup_of = o.duplicate_of
    if not paths_ok:
        return FinalizeOutcome(
            path=None,
            skipped_duplicate=all_skipped,
            duplicate_of=dup_of,
            warnings=warnings,
            extra_paths=[],
        )
    return FinalizeOutcome(
        path=paths_ok[0],
        skipped_duplicate=False,
        duplicate_of=None,
        warnings=warnings,
        extra_paths=paths_ok[1:],
    )


def _maybe_learning_log(cfg: KnsConfig, fields: dict[str, Any], title: str, paths: list[Path]) -> None:
    if not cfg.learning_loop_enabled or not paths:
        return
    root = wiki_dir().resolve()
    rels = [p.resolve().relative_to(root).as_posix() for p in paths]
    append_ingest_log(
        f"[LEARNING] importance={fields.get('importance', 'medium')!r} "
        f"title={title!r} paths={rels}",
    )


def _check_atomicity(body: str, cfg: KnsConfig, warnings: list[str]) -> None:
    """Warn when body word count suggests a non-atomic note."""
    words = len(body.split())
    if words > cfg.max_note_words:
        msg = (
            f"[WARN] Non-atomic note detected: body is ~{words} words "
            f"(threshold {cfg.max_note_words}); consider splitting."
        )
        warnings.append(msg)
        append_ingest_log(f"[WARN] non_atomic_note word_count={words} max={cfg.max_note_words}")


def _apply_wikilink_pass(body: str, cfg: KnsConfig, warnings: list[str]) -> None:
    """Validate wikilinks; optionally create placeholders."""
    broken, _created = validate_and_placeholder_wikilinks(body, cfg=cfg)
    for target in broken:
        warnings.append(f"[WARN] broken_wikilink → [[{target}]]")


def write_wiki_from_llm_output(
    markdown: str,
    *,
    source_relative: str = "",
    default_subdir: str = "summaries",
    cfg: KnsConfig | None = None,
    create_insight_stub: bool = True,
    _split_depth: int = 0,
) -> FinalizeOutcome:
    """Parse LLM markdown, validate frontmatter, dedupe, write wiki + insight stub."""
    _ = default_subdir
    cfg = cfg or load_config()
    warnings: list[str] = []

    fields, body = split_frontmatter(markdown)
    if not fields:
        msg = "No YAML frontmatter found in LLM output."
        if cfg.strict_frontmatter:
            raise ValueError(msg)
        warnings.append(f"[WARN] {msg} — using minimal defaults")
        fields = {}

    try:
        fields, w2 = normalize_frontmatter(
            fields,
            source_fallback=source_relative or "unknown",
            strict=cfg.strict_frontmatter,
        )
    except ValueError:
        append_ingest_log(f"[ERROR] frontmatter_validation_failed source={source_relative}")
        raise
    warnings.extend(w2)

    words = len(body.split())
    if (
        words > cfg.max_note_words
        and cfg.auto_split_oversized
        and _split_depth < _MAX_AUTO_SPLIT_DEPTH
        and llm_config_from_env() is not None
    ):
        combined = rebuild_markdown(fields, body)
        try:
            split_raw = call_split_note_llm(combined)
            pieces = _valid_split_documents(split_raw)
            if len(pieces) >= 2:
                outcomes = [
                    write_wiki_from_llm_output(
                        doc,
                        source_relative=source_relative,
                        default_subdir=default_subdir,
                        cfg=cfg,
                        create_insight_stub=create_insight_stub,
                        _split_depth=_split_depth + 1,
                    )
                    for doc in pieces
                ]
                merged = _merge_split_outcomes(outcomes)
                if cfg.learning_loop_enabled:
                    append_ingest_log(
                        f"[LEARNING] auto_split source={source_relative!r} "
                        f"parts={len(pieces)} primary={merged.path!s}",
                    )
                return merged
            warnings.append("[WARN] auto_split: model returned fewer than two valid notes; keeping original")
        except (ValueError, OSError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
            warnings.append(f"[WARN] auto_split_failed — keeping original note: {exc}")
            append_ingest_log(f"[WARN] auto_split_failed source={source_relative!r} err={exc!r}")

    _check_atomicity(body, cfg, warnings)
    _apply_wikilink_pass(body, cfg, warnings)

    title = str(fields["title"])
    wiki_rel = str(fields["wiki_path"])
    root = wiki_dir()
    out = (root / wiki_rel).resolve()
    root_resolved = root.resolve()
    try:
        out.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"Refusing to write outside wiki root: {out}") from exc

    dup_path, dup_score = find_most_similar_title(
        title,
        threshold=cfg.dedup_threshold,
        exclude_path=out if out.exists() else None,
        skip_insights=True,
    )

    if dup_path is not None and dup_score >= cfg.dedup_threshold:
        append_ingest_log(
            f"[WARN] duplicate_detected title={title!r} score={dup_score:.3f} existing={dup_path}",
        )
        if cfg.dedup_mode == "skip":
            warnings.append(f"[WARN] skipped duplicate of {dup_path} (score={dup_score:.3f})")
            append_ingest_log(f"[INFO] skipped_duplicate title={title!r} path={dup_path}")
            return FinalizeOutcome(
                path=None,
                skipped_duplicate=True,
                duplicate_of=dup_path,
                warnings=warnings,
                extra_paths=[],
            )

        from datetime import datetime, timezone

        stamp = datetime.now(timezone.utc).isoformat()
        section = (
            f"\n\n---\n\n## Ingest append ({stamp})\n\n"
            f"Source: {fields['source']}\n\n{body.strip()}\n"
        )
        dup_path.parent.mkdir(parents=True, exist_ok=True)
        with dup_path.open("a", encoding="utf-8") as handle:
            handle.write(section)
        append_ingest_log(f"[INFO] appended_duplicate title={title!r} path={dup_path}")
        warnings.append(f"[WARN] appended to existing note {dup_path} (score={dup_score:.3f})")
        if create_insight_stub:
            ensure_insight_stub(title=title, linked_note=wiki_relative_posix(dup_path))
        return FinalizeOutcome(
            path=dup_path,
            skipped_duplicate=False,
            duplicate_of=dup_path,
            warnings=warnings,
            extra_paths=[],
        )

    final_md = rebuild_markdown(fields, body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(final_md, encoding="utf-8")
    append_ingest_log(f"[INFO] wiki_created path={out} title={title!r} source={fields['source']!r}")
    if create_insight_stub:
        ensure_insight_stub(title=title, linked_note=wiki_relative_posix(out))
    if _split_depth == 0:
        _maybe_learning_log(cfg, fields, title, [out])
    return FinalizeOutcome(
        path=out,
        skipped_duplicate=False,
        duplicate_of=None,
        warnings=warnings,
        extra_paths=[],
    )

"""Command-line entrypoint for knowledge-system automation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.config import load_config
from scripts.dedup import find_duplicate_pairs
from scripts.discover import RawSource, discover_raw_sources, select_sources_by_limit
from scripts.insights import format_insight_recency, list_pending_insights
from scripts.ingest import (
    FinalizeOutcome,
    llm_config_from_env,
    prepare_all_staged,
    run_llm_for_source,
    write_wiki_from_llm_output,
)
from scripts.logging_utils import append_ingest_log
from scripts.paths import repo_root
from scripts.pdf_extract import extract_pdf_to_markdown
from scripts.prompts import resolve_template_for_relative_raw


def _load_env_file(path: Path) -> None:
    """Populate ``os.environ`` from a minimal ``KEY=value`` .env file."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _print_outcome(outcome: FinalizeOutcome) -> None:
    """Print finalize warnings and primary path."""
    for w in outcome.warnings:
        print(w, file=sys.stderr)
    if outcome.skipped_duplicate:
        print(f"skipped_duplicate -> {outcome.duplicate_of}", file=sys.stderr)
    elif outcome.path:
        print(outcome.path)
        for extra in outcome.extra_paths:
            print(extra)


def _extract_pdfs_for_sources(sources: list[RawSource]) -> int:
    """Extract PDFs for the given sources; return count extracted."""
    count = 0
    for src in sources:
        if src.kind != "pdf":
            continue
        path = extract_pdf_to_markdown(src.path)
        print(path)
        count += 1
    return count


def _cmd_discover() -> int:
    sources = discover_raw_sources()
    if not sources:
        print("No ingestible files found under raw/.")
        return 0
    for s in sources:
        tmpl = resolve_template_for_relative_raw(s.relative)
        print(
            f"{s.relative.as_posix()}\t{s.kind}\tpriority={s.priority}\ttemplate={tmpl}",
        )
    append_ingest_log(f"[INFO] discover count={len(sources)}")
    return 0


def _cmd_extract_pdfs() -> int:
    count = _extract_pdfs_for_sources(discover_raw_sources())
    if count == 0:
        print("No PDFs found under raw/.")
    append_ingest_log(f"[INFO] extract_pdfs count={count}")
    return 0


def _cmd_prepare(template: str | None) -> int:
    paths = prepare_all_staged(template_override=template)
    if not paths:
        print("Nothing to stage (raw/ empty or no supported files).")
        return 0
    for p in paths:
        print(p)
    print(f"\nStaged {len(paths)} bundle(s) under logs/staged/.")
    return 0


def _cmd_llm_run(limit: int) -> int:
    if llm_config_from_env() is None:
        print("KNS_LLM_API_KEY is not set.", file=sys.stderr)
        return 2
    sources = select_sources_by_limit(discover_raw_sources(), limit)
    if not sources:
        print("No sources found under raw/.")
        return 0
    failed = 0
    for s in sources:
        template = resolve_template_for_relative_raw(s.relative)
        try:
            md = run_llm_for_source(s, template)
            outcome = write_wiki_from_llm_output(
                md,
                source_relative=s.relative.as_posix(),
            )
            _print_outcome(outcome)
        except (ValueError, OSError) as exc:
            append_ingest_log(f"[ERROR] llm_run_failed path={s.relative} err={exc}")
            print(f"ERROR {s.relative}: {exc}", file=sys.stderr)
            failed += 1
    append_ingest_log(f"[INFO] llm_run finished failed={failed} processed={len(sources)}")
    return 1 if failed else 0


def _cmd_finalize(path: Path, default_subdir: str) -> int:
    md = path.read_text(encoding="utf-8")
    outcome = write_wiki_from_llm_output(
        md,
        source_relative=path.name,
        default_subdir=default_subdir,
    )
    _print_outcome(outcome)
    return 0


def _cmd_run(limit: int) -> int:
    """Default pipeline: discover → extract PDFs in batch → LLM → finalize."""
    if llm_config_from_env() is None:
        print("kns run requires KNS_LLM_API_KEY in the environment.", file=sys.stderr)
        return 2
    sources = select_sources_by_limit(discover_raw_sources(), limit)
    if not sources:
        print("No sources found under raw/.")
        return 0
    extracted = _extract_pdfs_for_sources(sources)
    append_ingest_log(f"[INFO] run_extract_pdfs count={extracted} batch={len(sources)}")
    failed = 0
    skipped = 0
    created = 0
    for s in sources:
        template = resolve_template_for_relative_raw(s.relative)
        try:
            md = run_llm_for_source(s, template)
            outcome = write_wiki_from_llm_output(
                md,
                source_relative=s.relative.as_posix(),
            )
            _print_outcome(outcome)
            if outcome.skipped_duplicate:
                skipped += 1
            elif outcome.path:
                created += 1
        except (ValueError, OSError) as exc:
            append_ingest_log(f"[ERROR] run_failed path={s.relative} err={exc}")
            print(f"ERROR {s.relative}: {exc}", file=sys.stderr)
            failed += 1
    append_ingest_log(
        f"[INFO] run_complete batch={len(sources)} created={created} "
        f"skipped_dup={skipped} failed={failed}",
    )
    return 1 if failed else 0


def _cmd_ingest() -> int:
    """Mechanical ingest only: discover + extract all PDFs under raw/."""
    sources = discover_raw_sources()
    count = _extract_pdfs_for_sources(sources)
    if count == 0:
        print("No PDFs found under raw/.")
    append_ingest_log(f"[INFO] ingest_extract_pdfs count={count} sources={len(sources)}")
    return 0


def _cmd_insights() -> int:
    """List insight stubs that are still pending."""
    rows = list_pending_insights()
    if not rows:
        print("No pending insight stubs.")
        append_ingest_log("[INFO] insights_list empty")
        return 0
    for rec in rows:
        recency = format_insight_recency(rec.note_mtime)
        print(
            f"{rec.title!r}\timportance={rec.importance}\tstatus={rec.status}\t"
            f"recency={recency}\tlinked_note={rec.linked_note!r}\tinsight={rec.path.as_posix()}",
        )
    append_ingest_log(f"[INFO] insights_list count={len(rows)}")
    return 0


def _cmd_refine(note_path: Path) -> int:
    """Refine one wiki note via LLM."""
    from scripts.refine import refine_wiki_note, resolve_note_path

    try:
        resolved = resolve_note_path(note_path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        refine_wiki_note(resolved)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(resolved)
    return 0


def _cmd_clean() -> int:
    """Report likely duplicate wiki notes using title similarity."""
    cfg = load_config()
    pairs = find_duplicate_pairs(threshold=cfg.dedup_threshold)
    if not pairs:
        print("No duplicate pairs detected at current threshold.")
        append_ingest_log("[INFO] clean_no_duplicates")
        return 0
    for pa, pb, score in pairs:
        line = f"{score:.3f}\t{pa}\t{pb}"
        print(line)
        append_ingest_log(f"[WARN] clean_duplicate_pair score={score:.3f} a={pa} b={pb}")
    print(f"\nFound {len(pairs)} pair(s). Adjust KNS_DEDUP_THRESHOLD if noisy.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="LLM-powered Obsidian ingest (raw → wiki → insights).",
        prog="kns",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Full pipeline: discover → extract PDFs → LLM → finalize.")
    p_run.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Max sources to process (priority: inbox/_high first, _low last).",
    )

    sub.add_parser("ingest", help="Discover + extract PDFs to logs/extracted/ (no LLM).")

    sub.add_parser(
        "clean",
        help="Find duplicate wiki titles (lint); logs pairs to ingest.log.",
    )

    sub.add_parser(
        "insights",
        help="List insight stubs with status=pending (human follow-up).",
    )

    p_ref = sub.add_parser(
        "refine",
        help="LLM-refine an existing wiki note (body only; preserves frontmatter).",
    )
    p_ref.add_argument(
        "note_path",
        type=Path,
        help="Path under wiki/ (e.g. concepts/foo.md) or absolute path.",
    )

    sub.add_parser("discover", help="List ingestible files under raw/.")

    sub.add_parser("extract-pdfs", help="Extract all PDFs under raw/ to logs/extracted/.")

    p_prep = sub.add_parser("prepare", help="Write prompt bundles to logs/staged/.")
    p_prep.add_argument(
        "--template",
        choices=["general", "paper", "youtube", "blog"],
        default=None,
        help="Override auto-selected template for all sources.",
    )

    p_llm = sub.add_parser(
        "llm-run",
        help="Call OpenAI-compatible API for sources (requires KNS_LLM_API_KEY).",
    )
    p_llm.add_argument("--limit", type=int, default=10, help="Max number of sources to process.")

    p_fin = sub.add_parser(
        "finalize",
        help="Write a saved LLM markdown file into wiki/ using frontmatter.",
    )
    p_fin.add_argument("response_file", type=Path, help="Path to saved LLM markdown output.")
    p_fin.add_argument(
        "--default-subdir",
        default="summaries",
        help="Legacy fallback (routing normally infers wiki_path).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI main entrypoint."""
    try:
        root = repo_root()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    _load_env_file(root / ".env")
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _cmd_run(args.limit)
    if args.command == "ingest":
        return _cmd_ingest()
    if args.command == "clean":
        return _cmd_clean()
    if args.command == "insights":
        return _cmd_insights()
    if args.command == "refine":
        return _cmd_refine(args.note_path)
    if args.command == "discover":
        return _cmd_discover()
    if args.command == "extract-pdfs":
        return _cmd_extract_pdfs()
    if args.command == "prepare":
        return _cmd_prepare(args.template)
    if args.command == "llm-run":
        return _cmd_llm_run(args.limit)
    if args.command == "finalize":
        return _cmd_finalize(args.response_file, args.default_subdir)

    raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

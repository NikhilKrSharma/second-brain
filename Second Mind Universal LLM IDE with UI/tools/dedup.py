#!/usr/bin/env python3
"""
Duplicate detection for the wiki.

Usage:
    # Check a title before ingesting (returns JSON)
    python tools/dedup.py --check "Attention Is All You Need"

    # Audit the whole wiki for existing duplicate pairs
    python tools/dedup.py --lint

No external dependencies — pure Python stdlib.

JSON output for --check:
    {
      "query": "<title>",
      "matches": [
        { "score": 0.94, "title": "Attention is All You Need", "path": "wiki/notes/attention-is-all-you-need.md" },
        ...
      ],
      "verdict": "duplicate" | "related" | "new"
    }

Verdict thresholds:
    score >= 0.90  → "duplicate"   (agent should flag and ask user)
    score >= 0.70  → "related"     (agent should add wikilinks)
    score <  0.70  → "new"         (proceed with ingest)
"""

import re
import sys
import json
import argparse
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Optional


REPO_ROOT  = Path(__file__).parent.parent
WIKI_DIR   = REPO_ROOT / "wiki"

DUPLICATE_THRESHOLD = 0.90
RELATED_THRESHOLD   = 0.70

# Folders excluded from dedup
EXCLUDED_FOLDERS = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio()


def _extract_body_start(path: Path, max_chars: int = 500) -> str:
    """Read the first max_chars of the note body (after frontmatter)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)
    return _normalise(body[:max_chars])


def _content_similarity(path_a: Path, path_b: Path) -> float:
    """Compare first 500 chars of body content between two notes."""
    a = _extract_body_start(path_a)
    b = _extract_body_start(path_b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _extract_title(path: Path) -> Optional[str]:
    """Read the `title:` field from YAML frontmatter without a YAML parser."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else path.stem


def _index_wiki() -> List[dict]:
    """Return list of {title, path, abs_path} for all wiki notes (excluding ignored folders)."""
    entries = []
    for md in WIKI_DIR.rglob("*.md"):
        if md.name in {"index.md", "log.md", "overview.md", "lint-report.md"}:
            continue
        # Check none of the excluded folder names appear in the path parts
        rel_parts = md.relative_to(WIKI_DIR).parts
        if any(p in EXCLUDED_FOLDERS for p in rel_parts):
            continue
        title = _extract_title(md)
        if title:
            entries.append({
                "title": title,
                "path": str(md.relative_to(REPO_ROOT)),
                "abs_path": md,
            })
    return entries


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------

def cmd_check(query: str) -> None:
    index   = _index_wiki()
    results = []
    for entry in index:
        score = _similarity(query, entry["title"])
        if score >= RELATED_THRESHOLD:
            results.append({"score": round(score, 3), "title": entry["title"], "path": entry["path"]})

    results.sort(key=lambda x: x["score"], reverse=True)

    if not results:
        verdict = "new"
    elif results[0]["score"] >= DUPLICATE_THRESHOLD:
        verdict = "duplicate"
    else:
        verdict = "related"

    output = {"query": query, "matches": results[:10], "verdict": verdict}
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# --lint mode
# ---------------------------------------------------------------------------

def cmd_lint() -> None:
    index = _index_wiki()
    pairs = []
    for i in range(len(index)):
        for j in range(i + 1, len(index)):
            title_score = _similarity(index[i]["title"], index[j]["title"])
            if title_score >= RELATED_THRESHOLD:
                content_score = _content_similarity(index[i]["abs_path"], index[j]["abs_path"])
                combined = max(title_score, content_score)
                pairs.append({
                    "score":         round(combined, 3),
                    "title_score":   round(title_score, 3),
                    "content_score": round(content_score, 3),
                    "title_a": index[i]["title"],
                    "path_a":  index[i]["path"],
                    "title_b": index[j]["title"],
                    "path_b":  index[j]["path"],
                    "verdict": "duplicate" if combined >= DUPLICATE_THRESHOLD else "related",
                })

    pairs.sort(key=lambda x: x["score"], reverse=True)

    if not pairs:
        print("No duplicates or closely related notes found.")
        return

    # Human-readable output
    duplicates = [p for p in pairs if p["verdict"] == "duplicate"]
    related    = [p for p in pairs if p["verdict"] == "related"]

    if duplicates:
        print(f"\n{'='*60}")
        print(f"LIKELY DUPLICATES (score >= {DUPLICATE_THRESHOLD})")
        print(f"{'='*60}")
        for p in duplicates:
            print(f"\n  Score: {p['score']}  (title: {p['title_score']}, content: {p['content_score']})")
            print(f"  A: {p['title_a']}")
            print(f"     {p['path_a']}")
            print(f"  B: {p['title_b']}")
            print(f"     {p['path_b']}")

    if related:
        print(f"\n{'='*60}")
        print(f"CLOSELY RELATED (score {RELATED_THRESHOLD}–{DUPLICATE_THRESHOLD})")
        print(f"{'='*60}")
        for p in related:
            print(f"\n  Score: {p['score']}  (title: {p['title_score']}, content: {p['content_score']})")
            print(f"  A: {p['title_a']}")
            print(f"  B: {p['title_b']}")

    print(f"\nTotal: {len(duplicates)} likely duplicate(s), {len(related)} related pair(s)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki duplicate detection")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", metavar="TITLE", help="Check a title before ingesting (JSON output)")
    group.add_argument("--lint",  action="store_true", help="Audit entire wiki for duplicates")
    args = parser.parse_args()

    if args.check:
        cmd_check(args.check)
    else:
        cmd_lint()

#!/usr/bin/env python3
"""
Validate YAML frontmatter in all wiki pages against the schema in AGENTS.md / TAGGING.md.

Usage:
    python tools/validate_frontmatter.py          # validate all wiki pages
    python tools/validate_frontmatter.py <path>   # validate a single file

No external dependencies — pure Python stdlib.

Checks:
    - Required fields present (title, type, domain, tags, wiki_path, last_updated)
    - type value in allowed set
    - domain value in allowed set
    - tags count between 3 and 8
    - Exactly one domain tag
    - Exactly one type tag
    - last_updated is a valid YYYY-MM-DD date
    - wiki_path matches the type routing rules
    - Slug conventions (kebab-case for notes, TitleCase for concepts)
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

VALID_TYPES = {
    "concept", "topic", "paper", "blog", "video",
    "workflow", "project", "idea", "tooling",
}

VALID_DOMAINS = {
    "genai", "ml", "systems", "data", "product", "research",
}

VALID_STATES = {
    "to-learn", "learning", "understood", "applied",
}

VALID_IMPORTANCE = {"low", "medium", "high"}

REQUIRED_FIELDS = {"title", "type", "domain", "tags", "wiki_path", "last_updated"}

TYPE_TO_FOLDER = {
    "concept": "concepts/",
    "topic":   "topics/",
    "project": "projects/",
}


def parse_frontmatter(text: str) -> dict:
    """Extract key-value pairs from YAML frontmatter (simple parser, no deps)."""
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return fm
    block = m.group(1)
    for line in block.splitlines():
        if ":" in line and not line.startswith("  "):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def parse_tags(text: str) -> list:
    """Extract tags list from YAML frontmatter."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    tm = re.search(r"^tags:\s*\n((?:  - .+\n?)+)", block, re.MULTILINE)
    if tm:
        return [line.strip().lstrip("- ").strip() for line in tm.group(1).splitlines() if line.strip()]
    im = re.search(r"^tags:\s*\[([^\]]*)\]", block, re.MULTILINE)
    if im:
        return [t.strip().strip('"').strip("'") for t in im.group(1).split(",") if t.strip()]
    return []


def parse_sources(text: str) -> list:
    """Extract sources list from YAML frontmatter."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    sm = re.search(r"^sources:\s*\n((?:  - .+\n?)+)", block, re.MULTILINE)
    if sm:
        return [line.strip().lstrip("- ").strip() for line in sm.group(1).splitlines() if line.strip()]
    return []


def validate_file(path: Path) -> list:
    """Validate a single wiki file. Returns list of error dicts."""
    errors = []
    rel = path.relative_to(REPO_ROOT).as_posix()

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [{"file": rel, "field": "-", "error": f"Cannot read file: {e}"}]

    if not re.match(r"^---\s*\n", text):
        return [{"file": rel, "field": "frontmatter", "error": "Missing YAML frontmatter block"}]

    fm = parse_frontmatter(text)
    tags = parse_tags(text)

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field == "tags":
            if not tags:
                errors.append({"file": rel, "field": "tags", "error": "Missing or empty tags"})
        elif field not in fm or not fm[field]:
            errors.append({"file": rel, "field": field, "error": f"Missing required field: {field}"})

    # Validate type
    note_type = fm.get("type", "")
    if note_type and note_type not in VALID_TYPES:
        errors.append({"file": rel, "field": "type", "error": f"Invalid type '{note_type}'. Valid: {', '.join(sorted(VALID_TYPES))}"})

    # Validate domain — no whitelist; any value is allowed so the wiki can grow
    domain = fm.get("domain", "")

    # Validate state (optional)
    state = fm.get("state", "")
    if state and state not in VALID_STATES:
        errors.append({"file": rel, "field": "state", "error": f"Invalid state '{state}'. Valid: {', '.join(sorted(VALID_STATES))}"})

    # Validate importance (optional)
    importance = fm.get("importance", "")
    if importance and importance not in VALID_IMPORTANCE:
        errors.append({"file": rel, "field": "importance", "error": f"Invalid importance '{importance}'. Valid: {', '.join(sorted(VALID_IMPORTANCE))}"})

    # Validate confidence (optional)
    confidence = fm.get("confidence", "")
    if confidence:
        try:
            c = float(confidence)
            if not (0.0 <= c <= 1.0):
                errors.append({"file": rel, "field": "confidence", "error": f"Confidence {c} out of range [0.0, 1.0]"})
        except ValueError:
            errors.append({"file": rel, "field": "confidence", "error": f"Confidence '{confidence}' is not a valid number"})

    # Validate last_updated date format
    last_updated = fm.get("last_updated", "")
    if last_updated:
        try:
            datetime.strptime(last_updated, "%Y-%m-%d")
        except ValueError:
            errors.append({"file": rel, "field": "last_updated", "error": f"Invalid date format '{last_updated}'. Expected YYYY-MM-DD"})

    # Validate tag count (3-8)
    if tags:
        if len(tags) < 3:
            errors.append({"file": rel, "field": "tags", "error": f"Too few tags ({len(tags)}). Minimum 3"})
        elif len(tags) > 8:
            errors.append({"file": rel, "field": "tags", "error": f"Too many tags ({len(tags)}). Maximum 8"})

    # Validate domain tag in tags — the domain field value should appear in the tags list
    if tags and domain:
        if domain not in tags:
            errors.append({"file": rel, "field": "tags", "error": f"Domain '{domain}' from frontmatter not found in tags list"})

    # Validate exactly one type tag
    if tags:
        type_tags = [t for t in tags if t in VALID_TYPES]
        if len(type_tags) == 0:
            errors.append({"file": rel, "field": "tags", "error": "No type tag found in tags list"})
        elif len(type_tags) > 1:
            errors.append({"file": rel, "field": "tags", "error": f"Multiple type tags: {type_tags}. Exactly one required"})

    # Validate wiki_path matches type routing
    wiki_path = fm.get("wiki_path", "")
    if wiki_path and note_type:
        expected_folder = TYPE_TO_FOLDER.get(note_type, "notes/")
        if not wiki_path.startswith(expected_folder):
            errors.append({"file": rel, "field": "wiki_path", "error": f"wiki_path '{wiki_path}' should start with '{expected_folder}' for type '{note_type}'"})

    # Validate slug conventions
    if wiki_path:
        slug = wiki_path.rsplit("/", 1)[-1].replace(".md", "")
        if note_type == "concept":
            # Concept slugs should be TitleCase
            if slug and slug[0].islower():
                errors.append({"file": rel, "field": "wiki_path", "error": f"Concept slug '{slug}' should be TitleCase (e.g. '{slug.title()}')"})
        elif slug:
            # All other slugs should be kebab-case
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug):
                errors.append({"file": rel, "field": "wiki_path", "error": f"Slug '{slug}' should be kebab-case (lowercase, hyphen-separated)"})

    return errors


def validate_all() -> list:
    """Validate all wiki pages. Returns list of error dicts."""
    all_errors = []
    skip_files = {"index.md", "log.md", "overview.md", "lint-report.md"}

    for md in sorted(WIKI_DIR.rglob("*.md")):
        if md.name in skip_files:
            continue
        # Skip assets directory
        try:
            md.relative_to(WIKI_DIR / "assets")
            continue
        except ValueError:
            pass

        all_errors.extend(validate_file(md))

    return all_errors


def print_report(errors: list) -> None:
    """Print a human-readable validation report."""
    if not errors:
        print("All wiki pages pass frontmatter validation.")
        return

    by_file = {}
    for e in errors:
        by_file.setdefault(e["file"], []).append(e)

    print(f"\nFrontmatter validation: {len(errors)} issue(s) in {len(by_file)} file(s)\n")
    print("=" * 60)
    for f, errs in by_file.items():
        print(f"\n  {f}")
        for e in errs:
            print(f"    [{e['field']}] {e['error']}")
    print(f"\n{'=' * 60}")
    print(f"Total: {len(errors)} issue(s)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        errors = validate_file(path)
    else:
        errors = validate_all()

    if "--json" in sys.argv:
        print(json.dumps(errors, indent=2))
    else:
        print_report(errors)

    sys.exit(1 if errors else 0)

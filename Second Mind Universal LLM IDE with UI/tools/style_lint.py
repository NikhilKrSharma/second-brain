#!/usr/bin/env python3
"""
Style lint checks for concise-first response instructions.

Usage:
    python tools/style_lint.py

The script scans AGENTS.md, Copilot/Cursor instructions, slash prompts, and
`.cursor/skills/**/SKILL.md` for verbose-default keywords that can cause long
first-stage responses.
"""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

TARGET_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / ".github/copilot-instructions.md",
    REPO_ROOT / ".cursor/rules/wiki-agent.mdc",
]

TARGET_FILES.extend(sorted((REPO_ROOT / ".github/prompts").glob("*.md")))
TARGET_FILES.extend(sorted((REPO_ROOT / ".cursor/prompts").glob("*.md")))

_skills_dir = REPO_ROOT / ".cursor" / "skills"
if _skills_dir.is_dir():
    TARGET_FILES.extend(sorted(_skills_dir.rglob("SKILL.md")))

# Keywords that often indicate verbose-by-default responses.
PATTERNS = [
    re.compile(r"\bthorough\b", re.IGNORECASE),
    re.compile(r"\bdetailed\b", re.IGNORECASE),
    re.compile(r"\bcomprehensive\b", re.IGNORECASE),
    re.compile(r"\bin-depth\b", re.IGNORECASE),
    re.compile(r"\bdeep\s+dive\b", re.IGNORECASE),
]

# Allow these phrases because they explicitly gate long output to user request.
ALLOWLIST_SNIPPETS = (
    "only after the user explicitly asks",
    "only if the user explicitly asks",
    "only on explicit user request",
    "explicitly asks for more detail",
    "asks for a detailed explanation",
)


def _is_allowlisted(line: str) -> bool:
    lowered = line.lower()
    return any(snippet in lowered for snippet in ALLOWLIST_SNIPPETS)


def main() -> int:
    findings = []

    for path in TARGET_FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        for idx, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or _is_allowlisted(line):
                continue

            for pattern in PATTERNS:
                if pattern.search(line):
                    findings.append((path.relative_to(REPO_ROOT), idx, raw_line.rstrip()))
                    break

    if not findings:
        print("Style lint: no verbose-default keywords found in scanned files.")
        return 0

    print("Style lint: found potential verbose-default wording:\n")
    for rel_path, line_no, line_text in findings:
        print(f"- {rel_path}:{line_no}: {line_text}")

    print(f"\nTotal findings: {len(findings)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

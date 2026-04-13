"""Extract text from PDFs without modifying files under ``raw/``."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from scripts.logging_utils import append_ingest_log
from scripts.paths import extracted_dir


def extract_pdf_to_markdown(pdf_path: Path) -> Path:
    """Extract PDF text to ``logs/extracted/<stem>.md``.

    Args:
        pdf_path: Path to a ``.pdf`` file.

    Returns:
        Path to the written markdown file.

    Raises:
        FileNotFoundError: If ``pdf_path`` does not exist.
        ValueError: If the file is not a PDF.
    """
    if not pdf_path.is_file():
        raise FileNotFoundError(str(pdf_path))
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    parts: list[str] = [f"# Extracted: {pdf_path.name}\n", f"Source: `{pdf_path}`\n\n---\n\n"]
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"## Page {i}\n\n{text.strip()}\n\n")

    out = extracted_dir() / f"{pdf_path.stem}.md"
    out.write_text("".join(parts), encoding="utf-8")
    append_ingest_log(f"extract_pdf path={pdf_path} -> {out}")
    return out

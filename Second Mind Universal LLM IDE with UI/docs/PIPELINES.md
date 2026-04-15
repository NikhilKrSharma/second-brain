# Source Pipelines

How different source types flow through the system: from raw capture to wiki note.

---

## Routing Table

| Raw subfolder | Prompt template | Default wiki folder | Notes |
|---|---|---|---|
| `raw/inbox/` | `prompts/general.md` | `wiki/notes/` | Catch-all inbox |
| `raw/research/` | `prompts/research.md` | `wiki/notes/` | Papers, blogs, articles, videos, web clips |
| `raw/work/` | `prompts/general.md` | `wiki/projects/` | Work-related material |
| `raw/<anything else>/` | `prompts/general.md` | `wiki/notes/` | **Fallback — always applies** |

### Fallback rule
Any subfolder under `raw/` that doesn't match a known folder above automatically uses `prompts/general.md` and routes to `wiki/notes/`. You can freely create new subfolders (e.g. `raw/podcasts/`, `raw/courses/`, `raw/newsletters/`) without updating any rules.

To give a custom subfolder its own prompt template, add a row to this table and note it in `AGENTS.md` routing.

---

## Per-Source Pipeline Details

### Research Sources (`raw/research/`)

This folder holds all external learning material: academic papers, blog posts, articles, YouTube/podcast transcripts, web clips, newsletters, and any other reference content.

1. **If PDF/DOCX/XLSX/PPTX:** agent runs `python tools/extract.py <path>` — outputs structured markdown to `raw/research/<stem>_extracted.md` preserving text, tables, and image references
2. Agent ingests the extracted markdown using `prompts/research.md`
3. Output: `wiki/notes/<slug>.md`
4. Agent creates insight stub in `wiki/insights/`

**Tips:**
- Include a `.md` sidecar alongside the PDF if you already have notes (agent merges)
- Set `confidence` lower if OCR was noisy
- For video transcripts, include title, URL, and channel at the top
- Auto-generated transcripts are often noisy — note this and lower confidence
- Include author name and publication date at the top of articles
- Flag opinion pieces explicitly so agent calibrates confidence correctly

### Inbox Captures (`raw/inbox/`)

1. Dump quick notes, bullet captures, speculative ideas
2. Use `now/` for anything time-sensitive
3. Agent ingests using `prompts/general.md`
4. Output: `wiki/notes/<slug>.md`

### Work Materials (`raw/work/`)

1. Meeting notes, design docs, technical specs, project briefs
2. Agent ingests using `prompts/general.md`
3. Output: `wiki/projects/<slug>.md` (not notes)

---

## Document Extraction Details

`tools/extract.py` handles PDF, DOCX, XLSX, and PPTX files:
- **PDF** (requires `pymupdf4llm`): Text flow preserved, tables to markdown, images extracted
- **DOCX** (requires `python-docx`): Headings, bold/italic, lists, tables, embedded images
- **XLSX** (requires `openpyxl`): Each sheet as a markdown table
- **PPTX** (requires `python-pptx`): Slides with text, tables, images, speaker notes

Images saved as `<stem>_images/<page>_<n>.png` alongside the extracted markdown.
Image references inserted inline as `![](path/to/image.png)`.

**Ingest:** Copy images needed in the wiki into `wiki/assets/images/<slug>/` and reference them from the note with paths relative to the note file (see `docs/assets.md`). Do not point wiki notes at `raw/` for long-term image hosting.

Run manually: `python tools/extract.py raw/research/my-paper.pdf`

The agent runs this automatically when the source file is a `.pdf`, `.docx`, `.xlsx`, or `.pptx`.

---

## Dedup Check

Before writing any new note, the agent runs:
```
python tools/dedup.py --check "<title>"
```

Results (JSON):
- **Score ≥ 0.90** — likely duplicate. Agent flags it and asks: skip / append to existing / keep both.
- **Score 0.70–0.89** — related note exists. Agent adds wikilinks between them automatically.
- **Score < 0.70** — new note, proceed.

Run full wiki dedup audit: `python tools/dedup.py --lint`

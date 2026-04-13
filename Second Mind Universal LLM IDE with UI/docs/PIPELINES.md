# Source Pipelines

How different source types flow through the system: from raw capture to wiki note.

---

## Routing Table

| Raw subfolder | Prompt template | Default wiki folder | Notes |
|---|---|---|---|
| `raw/inbox/` | `prompts/general.md` | `wiki/summaries/` | Catch-all inbox |
| `raw/inbox/_high/` | `prompts/general.md` | `wiki/summaries/` | Processed first |
| `raw/research_papers/` | `prompts/research_paper.md` | `wiki/summaries/` | PDFs extracted first |
| `raw/youtube/` | `prompts/youtube.md` | `wiki/summaries/` | Transcript + metadata |
| `raw/blogs/` | `prompts/blog.md` | `wiki/summaries/` | Articles, newsletters |
| `raw/clips/` | `prompts/blog.md` | `wiki/summaries/` | Obsidian Web Clipper drops |
| `raw/work/` | `prompts/general.md` | `wiki/projects/` | Work-related material |
| `raw/<anything else>/` | `prompts/general.md` | `wiki/summaries/` | **Fallback — always applies** |

### Fallback rule
Any subfolder under `raw/` that doesn't match a known folder above automatically uses `prompts/general.md` and routes to `wiki/summaries/`. You can freely create new subfolders (e.g. `raw/podcasts/`, `raw/courses/`, `raw/newsletters/`, `raw/clips/`) without updating any rules.

To give a custom subfolder its own prompt template, add a row to this table and note it in `AGENTS.md` routing.

---

## Per-Source Pipeline Details

### Research Papers (`raw/research_papers/`)

1. **If PDF/DOCX/XLSX/PPTX:** agent runs `python tools/extract.py <path>` — outputs structured markdown to `raw/research_papers/<stem>_extracted.md` preserving text, tables, and image references
2. Agent ingests the extracted markdown using `prompts/research_paper.md`
3. Output: `wiki/summaries/<slug>.md`
4. Agent creates insight stub in `wiki/insights/`

**Tips:**
- Include a `.md` sidecar alongside the PDF if you already have notes (agent merges)
- Set `confidence` lower if OCR was noisy

### YouTube / Video (`raw/youtube/`)

1. Get transcript — paste into a `.md` file with title, URL, and channel at the top
2. Agent ingests using `prompts/youtube.md`
3. Output: `wiki/summaries/<slug>.md`

**Tips:**
- Auto-generated transcripts are often noisy — note this and lower confidence
- Include timestamp references for key moments if possible

### Blogs & Articles (`raw/blogs/`)

1. Export article as plain text or markdown (browser reader view, Readability, etc.)
2. Agent ingests using `prompts/blog.md`
3. Output: `wiki/summaries/<slug>.md`

**Tips:**
- Include author name and publication date at the top
- Flag opinion pieces explicitly so agent calibrates confidence correctly

### Inbox Captures (`raw/inbox/`)

1. Dump quick notes, bullet captures, speculative ideas
2. Use `_high/` for anything time-sensitive
3. Agent ingests using `prompts/general.md`
4. Output: `wiki/summaries/<slug>.md`

### Work Materials (`raw/work/`)

1. Meeting notes, design docs, technical specs, project briefs
2. Agent ingests using `prompts/general.md`
3. Output: `wiki/projects/<slug>.md` (not summaries)

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

Run manually: `python tools/extract.py raw/research_papers/my-paper.pdf`

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

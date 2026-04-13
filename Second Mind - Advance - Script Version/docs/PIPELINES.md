# Ingest pipelines

## Priority folders

Under `raw/inbox/`, use:

- `_high/` — processed **first** when `kns run` / `kns llm-run` apply `--limit`.
- `_low/` — processed **last** (may be skipped if the limit is exhausted).

## A. Research papers

1. **Acquire:** place the PDF under `raw/research_papers/` (do not edit in place after archival).
2. **Optional metadata sidecar:** add `paper-slug.md` beside it with YAML:
   ```yaml
   ---
   title: "Paper title"
   authors: ["A", "B"]
   year: 2025
   url: https://arxiv.org/abs/...
   venue: arXiv
   ---
   Your quick notes or abstract paste.
   ```
3. **Text extraction:** `uv run python -m scripts extract-pdfs` → read `logs/extracted/<stem>.md` (debug OCR issues here).
4. **LLM structuring:** run `prepare` (auto-selects paper template) or paste `prompts/research_paper.md` + extracted text.
5. **Wiki output:** ensure the model emits YAML frontmatter including `wiki_path` (e.g. `summaries/paper-slug.md`) and `[[links]]` to related concepts.
6. **Split:** if the model outputs multiple concepts, split into `wiki/concepts/*` and leave a summary under `wiki/summaries/`.

**Best practices:** keep the PDF immutable; fix extraction errors in the sidecar or wiki, not by editing the PDF.

## B. YouTube

1. **Capture:** paste transcript + video URL into `raw/youtube/<video-slug>.md`. Tools you may use separately: YouTube transcript export, `yt-dlp`, or manual copy.
2. **Preprocess:** remove timestamps if they harm readability; keep chapter headings if present.
3. **LLM:** use `prompts/youtube.md` (auto via `prepare` for `raw/youtube/`).
4. **Wiki:** default `wiki/summaries/` or `wiki/topics/` if the video is a broad survey.

**Best practices:** store the canonical URL in frontmatter; prefer transcripts over auto-generated titles alone.

## C. Blogs / articles

1. **Capture:** Reader mode export or Markdown clip to `raw/blogs/`.
2. **Format:** one article per file; include `url` and `published` in frontmatter when known.
3. **LLM:** `prompts/blog_article.md`.
4. **Wiki:** arguments → bullet claims; link contradictory notes with `[[...]]`.

**Best practices:** if paywalled, save permissible excerpt + your paraphrase in raw, not full copyrighted text.

## Automation hooks

- `uv run python -m scripts discover` — dry-run inventory.
- `uv run python -m scripts prepare` — emit `logs/staged/*.bundle.txt`.
- `uv run python -m scripts finalize <response.md>` — write into `wiki/`.

See `README.md` for API mode.

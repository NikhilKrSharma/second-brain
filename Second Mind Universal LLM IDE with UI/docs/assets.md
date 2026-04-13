# Wiki assets — images, diagrams, video

Downloaded or copied **binary** files for wiki notes live under **`wiki/assets/`**. **`raw/` stays immutable** — never save new downloads into `raw/`; **copy** (or re-download) into `wiki/assets/` during ingest.

See also: Ingest Workflow in `AGENTS.md`, media sections in `prompts/*.md`.

---

## Layout

| Path | Use |
|------|-----|
| `wiki/assets/images/<note-slug-or-topic>/` | Raster/vector images (PNG, JPG, SVG, WebP) |
| `wiki/assets/diagrams/<note-slug-or-topic>/` | Exported diagram PNG/SVG, or companion `.mmd` source if you keep one |
| `wiki/assets/files/<note-slug-or-topic>/` | Optional PDFs or other attachments referenced from a note |

Use a short folder name per note or topic (e.g. `stryker-sync`, `paper-attention-2017`) so many figures from one ingest stay grouped.

---

## Markdown paths (Obsidian + graph)

Write image paths **relative to the wiki note file**:

- Note: `wiki/summaries/my-topic.md`
- Image: `wiki/assets/images/my-topic/fig1.png`
- Markdown: `![](../assets/images/my-topic/fig1.png)`

From `wiki/concepts/Foo.md`, the same asset is still `../assets/images/...` (go up to `wiki/`, then into `assets/`).

`tools/build_graph.py` rewrites these for the **graph panel** so they resolve from `graph/graph.html` (see README — use `python tools/serve_graph.py` for HTTP; it serves the **repo root**).

---

## Video

Do **not** store video files in the wiki. Use **embed URLs only**:

- Link: `[Title](https://www.youtube.com/embed/VIDEO_ID)` or equivalent Vimeo embed URL
- Optional: sanitized `<iframe>` (allowed domains only) in the note — see graph viewer docs in `README.md`

---

## Provenance

Every asset (and key factual claims, when non-obvious) should be traceable in the note body under **`### Sources and media`** (see prompt templates): description, local path, original URL or `raw/...` path, optional retrieved date.

---

## PDF / Office extraction

`tools/extract.py` writes images next to the extracted markdown under `raw/.../<stem>_images/`. On ingest, the agent **copies** needed images into `wiki/assets/images/<slug>/` and updates `![](...)` paths in the wiki note — it does not leave wiki notes pointing at `raw/` binaries.

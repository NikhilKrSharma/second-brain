# Operating workflow

## Daily — capture

- Append-only saves into `raw/inbox/` (bullets, links, half-baked thoughts).
- For papers/videos/blogs, drop into the matching `raw/` subtree the same day you consume them.
- Do **not** polish raw; correctness happens at wiki layer.

## Weekly — ingest + lint

- `uv run python -m scripts discover` (sanity inventory).
- `uv run python -m scripts prepare` → process bundles with your LLM → `finalize` each response.
- For PDFs: `extract-pdfs` if you added new files; spot-check `logs/extracted/`.
- Obsidian: fix broken `[[links]]`, merge duplicate titles, tag states honestly.

## Monthly — review + refine

- Promote stable ideas from `wiki/summaries/` → `wiki/concepts/` (split atoms).
- Write 1–3 notes in `wiki/insights/` synthesizing what changed in your thinking.
- Prune tags; archive stale `wiki/projects/` into a yearly archive note or folder.
- Re-read **My Notes** sections you left empty—fill or delete the parent note.

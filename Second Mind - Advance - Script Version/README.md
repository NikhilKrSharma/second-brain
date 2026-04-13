# LLM-powered personal knowledge system (Obsidian)

Raw captures live under `raw/`. Prompt templates live in `prompts/`. Processed notes land in `wiki/`. Automation lives in `scripts/` (Python + UV).

**Paradigm:** raw → processed wiki → human insights (`wiki/insights/`).

## Quick start

1. Install [UV](https://docs.astral.sh/uv/).
2. Copy `.env.example` → `.env` and set `KNS_LLM_API_KEY` for the default workflow.
3. `uv sync`
4. Drop captures under `raw/` (use `raw/inbox/_high/` for urgent items; `_low/` is deprioritized within the limit).
5. **Default pipeline:** `uv run kns run --limit 25`  
   (discover → extract PDFs for the batch → LLM → finalize with routing, dedup, insight stubs).
6. **Mechanical only (no LLM):** `uv run kns ingest` (PDF extraction).
7. **Duplicate lint:** `uv run kns clean`
8. **Pending insights:** `uv run kns insights` (sorted by linked note **importance** high→low, then recency; columns: title, importance, status, recency).
9. **Refine a note:** `uv run kns refine concepts/my-note.md` (LLM improves body; keeps frontmatter).
10. **Legacy / manual:** `prepare`, `llm-run`, `finalize` still work (`uv run kns <cmd>` or `uv run python -m scripts <cmd>`).

See `docs/env.md` and `docs/PIPELINES.md`.

## Folder purposes

| Path | Purpose |
|------|---------|
| `raw/inbox` | Fast captures (clippings, bullets, “to process”). |
| `raw/inbox/_high` | Same as inbox but processed first when using `--limit`. |
| `raw/inbox/_low` | Same as inbox but processed last (only if the limit allows). |
| `raw/research_papers` | PDFs and companion `.md` metadata sidecars. |
| `raw/youtube` | Transcripts, video notes, URLs + your paste. |
| `raw/blogs` | Article text or exports before structuring. |
| `raw/work` | Job-specific captures (tickets, design notes). |
| `wiki/concepts` | Atomic definitions and mechanisms. |
| `wiki/topics` | Curated maps / MOCs linking many notes. |
| `wiki/systems` | Architectures, pipelines, platform knowledge. |
| `wiki/projects` | Time-bounded work bodies of knowledge. |
| `wiki/insights` | **Human-written** synthesis (not LLM dumps). |
| `wiki/summaries` | Default target for first-pass LLM outputs. |
| `prompts/` | Copy-paste prompt templates. |
| `logs/` | `ingest.log`, `staged/` bundles, `extracted/` PDF text. |
| `scripts/` | Ingest automation. |

Tagging rules: `docs/TAGGING.md`. Obsidian usage: `docs/OBSIDIAN.md`.

## Rules of thumb

- Do not edit files under `raw/` except to add new captures (treat as append-only truth of what you ingested).
- Validate important claims (equations, APIs, benchmarks) against the source.
- Prefer several small wiki notes over one giant page.
- Notes carry YAML `importance: low | medium | high` (default **medium**; override anytime in the file).
- Oversized LLM outputs can be **auto-split** into multiple atomic notes via a second LLM call (`KNS_AUTO_SPLIT_OVERSIZED`, on by default when `KNS_LLM_API_KEY` is set).
- Optional **learning loop** logging: set `KNS_LEARNING_LOOP=true` to append `[LEARNING]` lines to `logs/ingest.log` after writes.
- Keep `wiki/insights/` explicitly human.

Cadence details: `docs/WORKFLOW.md`.

## License

Personal use; adapt freely.

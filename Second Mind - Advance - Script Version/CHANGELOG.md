# Changelog

## [0.4.0] — 2026-04-10

### Added

- **`importance: low | medium | high`** in wiki YAML (default `medium`); used for insight ordering and future filtering.
- **Auto-split:** when body exceeds `KNS_MAX_NOTE_WORDS` and `KNS_AUTO_SPLIT_OVERSIZED` is on, a second LLM pass (`prompts/split.md`) splits into multiple atomic notes; on failure the original note is kept with warnings.
- **Smart placeholders:** `KNS_PLACEHOLDER_MIN_OCCURRENCE` (default `2`) plus “long non-generic target” rule in `scripts/wikilinks.py`.
- **Learning loop:** optional `[LEARNING]` log lines via `KNS_LEARNING_LOOP`.
- `FinalizeOutcome.extra_paths` for additional files written in one finalize (e.g. split).
- `parse_multi_markdown_notes`, `call_split_note_llm` in `scripts/ingest.py`.

### Changed

- `kns insights`: sorted by linked-note importance (high → low) then recency; output shows title, importance, status, recency.
- Ingestion prompts: `importance` field, stronger “non-trivial wikilinks only” guidance.
- `refine.md`: avoid generic wikilinks in refined bodies.

## [0.3.0] — 2026-04-10

### Added

- **Pre-write dedup:** similar existing note titles injected into the LLM user message (`KNS_PRE_DEDUP_ENABLED`, default on); logged as `pre_dedup_context`.
- **Atomicity check:** word-count warning on finalize (`KNS_MAX_NOTE_WORDS`, default 2000).
- **Wikilink validation** + optional placeholders under `wiki/concepts/` (`KNS_ENABLE_PLACEHOLDER_LINKS`).
- Insight stubs now include YAML: `linked_note`, `status: pending`.
- CLI: `kns insights`, `kns refine <wiki/path.md>`.
- `prompts/refine.md` and `scripts/refine.py`, `scripts/wikilinks.py`.
- Config module constants: `MAX_NOTE_LENGTH`, `ENABLE_PLACEHOLDER_LINKS`, `PRE_DEDUP_ENABLED` (env-overridable).

### Changed

- Prompts: stronger atomicity, CRITICAL quality instructions, confidence guidance, wikilink discipline.

## [0.2.0] — 2026-04-10

### Added

- CLI `kns` (alias `kns-ingest`): `run` (default pipeline), `ingest` (PDF extract only), `clean` (duplicate scan).
- `scripts/config.py` for `KNS_DEDUP_MODE`, `KNS_DEDUP_THRESHOLD`, `KNS_STRICT_FRONTMATTER`.
- `scripts/routing.py`: wiki path normalization + **type-tag alignment** (`type/concept` → `concepts/`, etc.).
- `scripts/dedup.py`: title similarity vs existing wiki notes (`skip` or `append`); insights excluded from match targets.
- `scripts/insights.py`: auto-create `wiki/insights/<slug>.md` stubs after each successful finalize.
- `FinalizeOutcome` from `write_wiki_from_llm_output` (warnings, skip/append duplicate reporting).
- Inbox priority: `raw/inbox/_high/` and `raw/inbox/_low/`.

### Changed

- **Strict frontmatter** enforcement (with defaults + warnings): `title`, `tags`, `wiki_path`, `source`, `confidence`.
- Prompt templates updated for the new schema and atomic-note rules.
- `discover` lists `priority=`; ordering is high → normal → low.

## [0.1.0] — 2026-04-10

### Added

- Initial folder layout under `raw/` and `wiki/`.
- Prompt templates: general ingestion, research paper, YouTube, blog/article.
- Python ingest CLI (`scripts/`): discover, PDF extract to `logs/extracted/`, prepare staged bundles, optional OpenAI-compatible `llm-run`, `finalize` for markdown responses.
- Documentation: tagging, pipelines, Obsidian guide, environment variables, operating workflow.
- PyYAML-backed frontmatter parsing for `finalize`.
- Pytest coverage for frontmatter, slugify, and wiki writes.

### Changed

- Skip `README.txt` / `README.md` (case-insensitive) during discovery so folder instructions are not ingested.

### Repository hygiene

- Ignore generated `logs/staged/`, `logs/extracted/`, and `logs/ingest.log` in git.

# Environment variables

Copy `.env.example` to `.env` in the repo root. Values are read by `scripts/cli.py` on startup.

| Variable | Required | Description |
|----------|----------|-------------|
| `KNS_LLM_API_KEY` | No | Enables `llm-run`. Omit for manual copy/paste workflow. |
| `KNS_LLM_BASE_URL` | No | Default `https://api.openai.com/v1`. Use your provider’s OpenAI-compatible endpoint. |
| `KNS_LLM_MODEL` | No | Default `gpt-4o-mini`. |
| `KNS_REPO_ROOT` | No | Absolute path to this repo if auto-detection fails. |
| `KNS_DEDUP_MODE` | No | `skip` (default) or `append` when a similar title exists in `wiki/`. |
| `KNS_DEDUP_THRESHOLD` | No | Title similarity in `(0, 1]`, default `0.86`. |
| `KNS_STRICT_FRONTMATTER` | No | `true` / `1` / `yes` to require complete YAML from the model. |
| `KNS_MAX_NOTE_WORDS` | No | Word-count threshold for “non-atomic note” warnings (default `2000`). |
| `KNS_ENABLE_PLACEHOLDER_LINKS` | No | `true`/`false` — create `wiki/concepts/<slug>.md` for missing `[[links]]`. |
| `KNS_PRE_DEDUP_ENABLED` | No | `true`/`false` — inject similar-note titles into the LLM user message before generation. |
| `KNS_PLACEHOLDER_MIN_OCCURRENCE` | No | Minimum `[[wikilink]]` occurrences before creating a `wiki/concepts/` stub (default `2`). Long non-generic targets can still get a stub on first use. |
| `KNS_AUTO_SPLIT_OVERSIZED` | No | `true`/`false` — if body word count exceeds `KNS_MAX_NOTE_WORDS`, call the LLM with `prompts/split.md` to emit multiple atomic notes (default on). |
| `KNS_LEARNING_LOOP` | No | `true`/`false` — write `[LEARNING]` lines to `logs/ingest.log` after successful finalize (default off). |

Never commit `.env`. Rotate keys if leaked.

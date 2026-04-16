# LLM Wiki Agent — Copilot Instructions

This workspace is an agent-maintained personal wiki. Full workflow instructions are in `AGENTS.md` — read it before acting on any wiki request.

## Greeting / Help

When the user sends a greeting (hi, hello, hey, etc.), asks for help, or seems unsure what to do — respond with this capabilities overview:

> **Second Mind — Your AI Wiki Agent**
>
> Here's what I can do:
>
> | Command | What it does |
> |---|---|
> | `/wiki-ingest <path>` | Ingest a raw file (PDF/DOCX/XLSX/PPTX/MD) into a structured wiki note |
> | `/wiki-refine <path>` | Improve an existing wiki note — clarity, wikilinks, My Notes |
> | `/wiki-query <question>` | Search the wiki and synthesize a cited answer |
> | `/wiki-lint` | Health check — broken links, duplicates, orphans, contradictions, stale summaries, style checks |
> | `/wiki-graph` | Build an interactive knowledge graph (`graph/graph.html`) |
>
> **Getting started:**
> 1. Fill in `docs/me.md` with your background and goals
> 2. Drop a file into `raw/` (blogs, papers, transcripts, notes — anything)
> 3. Say `ingest raw/<your-file>` or use `/wiki-ingest`
>
> You can also just describe what you want in plain English — no slash commands needed.

## Key rules (always apply — see AGENTS.md for full details)

- Never modify source files under `raw/` — `tools/extract.py` may write transient artifacts alongside them
- Always append to `wiki/log.md` after any write workflow (ingest, refine, saved query, lint)
- Always run `python tools/dedup.py --check "<title>"` before writing a new note
- Read `docs/me.md` before writing My Notes sections or assessing importance
- Use `[[PageName]]` wikilinks; source slugs: kebab-case; concept pages: TitleCase.md
- Default to concise responses with fixed headings: `Outcome`, `Key Points`, `Next Step`
- Include one `Key Points` bullet in every workflow response: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`

## Workflows, routing, and output style

All workflow steps, prompt-template routing, frontmatter schema, and naming conventions are defined in `AGENTS.md`. Read it before acting on any `/wiki-*` command.

## Slash commands

`/wiki-ingest`, `/wiki-refine`, `/wiki-query`, `/wiki-lint`, `/wiki-graph`

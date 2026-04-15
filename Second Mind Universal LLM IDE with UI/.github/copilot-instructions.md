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

## Quick reference

- **Ingest** a source → follow the Ingest Workflow in AGENTS.md (detect type → extract PDF/DOCX/XLSX/PPTX if needed → dedup check → select prompt template → write note → create/update concepts → update index & overview → insight stub → log)
- **Refine** a note → read `prompts/refine.md`, improve body only, preserve frontmatter exactly
- **Query** the wiki → read `wiki/index.md` + `docs/me.md`, read relevant pages, synthesize with `[[wikilink]]` citations
- **Lint** the wiki → run `python tools/dedup.py --lint`, check orphan pages, broken links, contradictions, style drift via `python tools/style_lint.py`
- **Build graph** → run `python tools/build_graph.py --open`
- After any `/wiki-*` workflow, run `python tools/build_graph.py --open` before responding so `graph/graph.html` stays current

## Key rules

- Never modify files under `raw/` — they are immutable source documents (ingest copies media into `wiki/assets/` per `docs/assets.md`; video = embed URLs only)
- Always append to `wiki/log.md` after any workflow completes
- Always rebuild the graph with `python tools/build_graph.py --open` after any `/wiki-*` workflow
- Always run `python tools/dedup.py --check "<title>"` before writing a new note
- Read `docs/me.md` before writing My Notes sections or assessing importance
- Use `[[PageName]]` wikilinks; source slugs: kebab-case; concept pages: TitleCase.md
- `wiki/insights/` is human-only — agent creates STUBS ONLY (status: pending)
- New folders under `raw/` automatically fall back to prompts/general.md + wiki/notes/

## Output style

- Default to concise first-stage responses with globally fixed headings: `Outcome`, `Key Points`, `Next Step`
- Keep first-stage `Key Points` to 3-5 bullets by default
- Include one `Key Points` bullet in every workflow response: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`
- Rarely exceed 5 bullets only when correctness or completeness would otherwise be lost
- Use one short sentence per bullet where possible; avoid filler and repeated rationale
- Expand into a detailed explanation only after the user explicitly asks for more detail
- Keep heading names fixed across all workflows and plain-language requests

## Prompt routing

| raw/ subfolder | Template |
|---|---|
| research/ | prompts/research.md |
| work/ | prompts/general.md → wiki/projects/ |
| anything else | prompts/general.md → wiki/notes/ |

## Slash commands

`/wiki-ingest`, `/wiki-refine`, `/wiki-query`, `/wiki-lint`, `/wiki-graph`

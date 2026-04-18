# LLM Wiki Agent — Schema & Workflow Instructions

This wiki is maintained entirely by your coding agent. Just open this folder in Cursor or VS Code with Copilot and talk to it. No API keys needed. The agent calls these utilities (pure stdlib unless you add extraction deps — see `requirements.txt`): `tools/extract.py` and `tools/dedup.py` for ingest/dedup; `tools/style_lint.py` and `tools/validate_frontmatter.py` during `/wiki-lint`. Graph builds are user-initiated via `/wiki-graph` (which calls `start-graph.sh`) — never run automatically.

**Orientation:** `AGENTS.md` is the single source of truth for all workflows. Cursor auto-loads `.cursor/rules/wiki-agent.mdc`; VS Code Copilot auto-loads `.github/copilot-instructions.md`. Human-facing documentation is in `README.md`.

**Personal context:** Read `docs/me.md` whenever writing a "My Notes" section, assessing importance, or personalizing a query answer.

## Output Style

- Default to concise first-stage responses with globally fixed headings: `Outcome`, `Key Points`, `Next Step`
- Keep first-stage `Key Points` to 3-5 bullets by default
- Include one `Key Points` bullet in every workflow response: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`
- Rarely exceed 5 bullets only when correctness or completeness would otherwise be lost
- Expand into a detailed explanation only after the user explicitly asks for more detail
- Keep heading names fixed across all workflows and plain-language requests

---

## Slash Commands

| Command | What it does |
|---|---|
| `/wiki-ingest <path>` | Ingest a source file into the wiki |
| `/wiki-refine <path>` | Improve an existing wiki note |
| `/wiki-query <question>` | Query the wiki and synthesize an answer |
| `/wiki-lint` | Wiki health check — orphans, broken links, duplicates, contradictions, stale notes, style drift (see Lint Workflow) |
| `/wiki-graph` | Build the knowledge graph |

Cursor: `.cursor/rules/` + `.cursor/skills/` · VS Code Copilot: `.github/prompts/`

---

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

---

## Directory Layout

```
raw/                    # Immutable source documents — NEVER modify these
  inbox/                # Quick captures and general notes
  research/             # Papers, blogs, articles, videos, web clips, external references
  work/                 # Work-related materials (meeting notes, specs, project docs)
  assets/               # Images and attachments

wiki/                   # Agent writes here
  index.md              # Catalog of all pages — update on every ingest
  log.md                # Append-only chronological record
  overview.md           # Living synthesis across all sources
  notes/                # First-pass generated notes — everything lands here first
  concepts/             # Atomic definitions and mechanisms (promoted from notes)
  topics/               # Curated maps / MOCs (Maps of Content)
  projects/             # Time-bounded work bodies of knowledge
  assets/               # Images, diagrams, optional files for notes (see docs/assets.md)
    images/             # Per-note or per-topic image folders
    diagrams/           # Diagram exports / sources
    files/              # Optional PDFs and attachments

prompts/                # Source-type extraction templates (agent reads these)
docs/                   # Reference docs for agent and human
  me.md                 # Personal context — read during ingest and query
  TAGGING.md            # Tag taxonomy and rules
  WORKFLOW.md           # Daily/weekly/monthly operating cadence
  PIPELINES.md          # Source routing table and pipeline details
  assets.md             # wiki/assets layout, paths, video embed rules
tools/                  # Utility scripts (agent calls these)
  build_graph.py        # Builds graph.json + graph.html (no deps; called by start-graph.sh)
  serve_graph.py        # Serves repo root over HTTP for graph + media (called by start-graph.sh)
  extract.py            # PDF/DOCX/XLSX/PPTX -> structured markdown
  dedup.py              # Duplicate detection (no deps)
  style_lint.py         # Instruction/prompt verbose-default scan (no deps)
  validate_frontmatter.py  # Frontmatter schema validation (no deps)
deleted/                # Soft-deleted wiki pages (serve_graph.py HTTP DELETE)
graph/                  # Auto-generated graph output
requirements.txt        # pip install -r requirements.txt (extraction deps)
```

---

## Frontmatter Schema

Every wiki page uses this YAML frontmatter:

```yaml
---
title: "Specific, synthesized title"
type: concept | topic | paper | blog | video | workflow | project | idea | tooling
domain: genai | ml | systems | data | product | research
tags:
  - <domain tag>
  - <type tag>
  - <additional facet tags>
state: to-learn | learning | understood | applied   # optional
importance: low | medium | high                     # default: medium
confidence: 0.0-1.0                                 # extraction confidence
sources:
  - <raw file path(s)>
last_updated: YYYY-MM-DD
wiki_path: <folder/slug.md>
---
```

See `docs/TAGGING.md` for full tag taxonomy and rules.

**Routing:** `wiki_path` determines the folder:
| type | default folder |
|---|---|
| `concept` | `concepts/` |
| `topic` | `topics/` |
| `project` | `projects/` |
| everything else | `notes/` |

**Type decision tree (choose the first match):**
1. Atomic definition or mechanism — a single well-bounded idea → `concept`
2. Curated map linking multiple concepts (survey or MOC) → `topic`
3. Time-bounded body of work with deliverables → `project`
4. Process, procedure, or operational pattern → `workflow`
5. Speculative, half-formed, or exploratory → `idea`
6. Tool, library, framework, or platform → `tooling`
7. Otherwise → keep source format (`paper`, `blog`, `video`) and route to `notes/`

**Slug rules:** lowercase, hyphen-separated, ASCII, derived from title.

---

## Prompt Templates

The agent selects a template based on the source's `raw/` subfolder:

| raw/ subfolder | Template | Default wiki folder |
|---|---|---|
| `research/` | `prompts/research.md` | `notes/` |
| `work/` | `prompts/general.md` | `projects/` |
| `inbox/` or any other | `prompts/general.md` | `notes/` |

**Fallback:** any folder not listed above uses `prompts/general.md` and routes to `notes/`. New folders under `raw/` work automatically — no rule changes needed.

---

## Ingest Workflow

Triggered by: *"ingest `<file>`"* or `/wiki-ingest`

Steps (in order):

1. **Read `docs/me.md`** — calibrate importance and the My Notes section
2. **Detect source type** — from the `raw/` subfolder path
3. **If PDF/DOCX/XLSX/PPTX** — run `python tools/extract.py <path>`, ingest the `_extracted.md` output instead
4. **Run dedup check** — `python tools/dedup.py --check "<proposed title>"`
   - Score >= 0.90 → stop, flag as likely duplicate, ask user: **skip** / **append** / **keep both**
     - **Append:** merge new content into the existing note — add new sections, update existing ones with newer information, combine source lists, bump `last_updated`. Do not duplicate shared content.
   - Score 0.70-0.89 → proceed, note the related page, add wikilinks between them
   - Score < 0.70 → proceed normally
5. **Load prompt template** — based on routing table above
6. **Read the source file** fully
7. **Read `wiki/index.md`** and `wiki/overview.md` for current wiki context
8. **Write the wiki note** — following the selected prompt template exactly (frontmatter schema + body structure)
   - **Media (optional):** Add figures or Mermaid diagrams only when they materially aid understanding; otherwise omit. Use `wiki/assets/` per `docs/assets.md`; **never** write new binaries into `raw/`. Copy PDF/PPTX-extracted images from `raw/.../<stem>_images/` into `wiki/assets/images/<slug>/` and fix `![](...)` paths relative to the note.
   - **Video:** embed URLs only (e.g. YouTube/Vimeo embed links or iframes per template); do not store video files in the wiki.
   - **Provenance:** Include **`### Sources and media`** listing each asset and key textual claims (path, original URL or `raw/...`, optional date).
9. **Update / create concept pages** — for key ideas, entities, and frameworks (if substantial enough for a standalone concept)
10. **Update `wiki/index.md`** — add entry in the appropriate section
11. **Update `wiki/overview.md`** — revise synthesis if this source warrants it
12. **Flag contradictions** with existing wiki content
13. **Append to `wiki/log.md`**: `## [YYYY-MM-DD] ingest | <Title>`

---

## Refine Workflow

Triggered by: *"refine `<wiki path>`"* or `/wiki-refine`

Steps:
1. Read the target wiki note
2. Read `docs/me.md`
3. Load `prompts/refine.md`
4. Improve the note body following `prompts/refine.md` — preserve frontmatter exactly
5. Overwrite the file with improved body
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] refine | <Title>`

---

## Query Workflow

Triggered by: *"query: `<question>`"* or `/wiki-query`

Steps:
1. Read `wiki/index.md` to identify relevant pages
2. Read `docs/me.md` to personalize the answer
3. Read up to ~10 most relevant wiki pages
4. Synthesize a concise first-stage answer with `[[PageName]]` wikilink citations
  - Use fixed headings: `Outcome`, `Key Points`, `Next Step`
  - Put the main synthesis in `Key Points` as 3-5 bullets by default
  - Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`
  - Expand only if the user explicitly asks for a detailed explanation
5. Include a `## Sources` section listing pages used
6. Ask if the user wants it saved as `wiki/notes/<slug>.md`
7. If saving: append to `wiki/log.md`: `## [YYYY-MM-DD] query | <question>`

If the user chose **not** to save, skip step 7 (no log entry needed).

---

## Lint Workflow

Triggered by: *"lint"* or `/wiki-lint`

Check for:
- **Orphan pages** — wiki pages with no inbound `[[links]]` from other pages
- **Broken links** — `[[WikiLinks]]` pointing to pages that don't exist
- **Duplicate notes** — run `python tools/dedup.py --lint`
- **Frontmatter validation** — run `python tools/validate_frontmatter.py` (checks required fields, valid types/domains, tag counts, slug conventions)
- **Contradictions** — claims that conflict across pages
- **Stale notes** — pages not updated after newer sources changed the picture
- **Missing concept pages** — concepts mentioned in 3+ pages but lacking their own page
- **Data gaps** — questions the wiki can't answer; suggest sources
- **Response style drift** — run `python tools/style_lint.py` and report findings

Output a structured lint report using fixed headings: `Outcome`, `Key Points`, `Next Step`.
Keep `Key Points` to 3-5 bullets by default and expand only on explicit user request.
Ask if user wants it saved to `wiki/lint-report.md`.
Append to `wiki/log.md`: `## [YYYY-MM-DD] lint | Wiki health check`

---

## Graph Workflow

Triggered by: *"build graph"* or `/wiki-graph`

> **Note:** Run `start-graph.sh` to build and see the graph.

```bash
./start-graph.sh
```

This script automatically:
- Parses all `[[wikilinks]]` across wiki pages
- Rewrites local markdown image paths for the reader pane
- Builds `graph/graph.json` and `graph/graph.html`
- Starts a local server on `http://127.0.0.1:8765/graph/graph.html`
- Appends to `wiki/log.md` automatically

After it runs, summarize with fixed headings: `Outcome`, `Key Points`, `Next Step`.
Keep `Key Points` to 3-5 bullets by default.
`/wiki-graph` is user-initiated only — it is never run automatically by other workflows.

---

## Key Rules

- **Never modify source files under `raw/`** — they are immutable. `tools/extract.py` may write transient `_extracted.md` / `_images/` artifacts alongside them
- **Media for wiki notes** lives under `wiki/assets/` (`docs/assets.md`); ingest **copies** from `raw/.../_images/` when needed; **video = embed URLs only**
- **Always append to `wiki/log.md`** after any workflow completes
- **Always run dedup before writing** a new note
- **Read `docs/me.md`** before writing My Notes or assessing importance

---

## Naming Conventions

- Wiki note slugs: `kebab-case.md`
- Concept pages: `TitleCase.md` (e.g. `ReinforcementLearning.md`, `RAG.md`, `OpenAI.md`)

---

## Index Format

```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — living synthesis

## Notes
- [Note Title](notes/slug.md) — one-line description

## Concepts
- [Concept Name](concepts/ConceptName.md) — one-line definition

## Topics
- [Topic Name](topics/TopicName.md) — one-line description

## Projects
- [Project Name](projects/slug.md) — one-line description
```

---

## Log Format

`## [YYYY-MM-DD] <operation> | <title>`

Operations: `ingest`, `refine`, `query`, `lint`, `graph`

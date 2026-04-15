# Second Mind — Personal Knowledge Wiki

> Agent-maintained knowledge base. Drop files into `raw/`, talk to your agent, get structured wiki notes.

**Works in:** Cursor (IDE + Agent mode) · VS Code with GitHub Copilot
**Requires:** No API keys. Optional dependencies for document extraction (PDF/DOCX/XLSX/PPTX).

---

## Quick Start

```
1. Fill in  docs/me.md          ← your background, projects, goals (agent uses this)
2. Drop a file into  raw/       ← blog, paper, video transcript, note
3. Run /wiki-ingest raw/...    ← agent writes a structured wiki note
```

| Command | What it does |
|---|---|
| `/wiki-ingest <path>` | Ingest a raw file → structured wiki note |
| `/wiki-refine <path>` | Improve an existing wiki note |
| `/wiki-query <question>` | Search + synthesize an answer from the wiki |
| `/wiki-lint` | Health check — broken links, duplicates, orphans, style drift |
| `/wiki-graph` | Build interactive knowledge graph (`graph/graph.html`) |

Every `/wiki-*` workflow automatically refreshes `graph/graph.html` before it finishes.

> You can also describe what you want in plain English instead of using slash commands.

---

## Table of Contents

- [Second Mind — Personal Knowledge Wiki](#second-mind--personal-knowledge-wiki)
  - [Quick Start](#quick-start)
  - [Table of Contents](#table-of-contents)
  - [How It Works](#how-it-works)
  - [Setup](#setup)
    - [1. Open the workspace](#1-open-the-workspace)
    - [2. Fill in `docs/me.md`](#2-fill-in-docsmemd)
    - [3. Install document extraction dependencies (optional)](#3-install-document-extraction-dependencies-optional)
  - [Directory Structure](#directory-structure)
  - [Commands Reference](#commands-reference)
    - [`/wiki-ingest <path>`](#wiki-ingest-path)
    - [`/wiki-refine <path>`](#wiki-refine-path)
    - [`/wiki-query <question>`](#wiki-query-question)
    - [`/wiki-lint`](#wiki-lint)
    - [`/wiki-graph`](#wiki-graph)
  - [Workflows](#workflows)
    - [Daily — Capture](#daily--capture)
    - [Weekly — Process](#weekly--process)
    - [Monthly — Promote \& Synthesize](#monthly--promote--synthesize)
  - [Source Type Routing](#source-type-routing)
  - [Frontmatter Schema](#frontmatter-schema)
  - [Tagging System](#tagging-system)
  - [Prompt Templates](#prompt-templates)
  - [Tool Scripts](#tool-scripts)
    - [`tools/build_graph.py`](#toolsbuild_graphpy)
    - [`tools/extract.py`](#toolsextractpy)
    - [`tools/dedup.py`](#toolsdeduppy)
    - [`tools/style_lint.py`](#toolsstyle_lintpy)
  - [Wiki Folder Hierarchy](#wiki-folder-hierarchy)
  - [Insight Workflow](#insight-workflow)
  - [Extending the Workspace](#extending-the-workspace)
    - [Adding a new raw source folder](#adding-a-new-raw-source-folder)
    - [Changing extraction behavior](#changing-extraction-behavior)
    - [Changing the frontmatter schema](#changing-the-frontmatter-schema)
    - [Adding a new slash command](#adding-a-new-slash-command)
    - [Changing dedup thresholds](#changing-dedup-thresholds)
  - [Key Rules](#key-rules)

---

## How It Works

```
raw/  →  agent (ingest)  →  wiki/notes/  →  you (promote)  →  concepts/ | topics/ | insights/
```

1. **You** drop source files into `raw/` — no structure required
2. **Agent** reads the source, picks the right extraction template, checks for duplicates, writes a structured wiki note, creates concept pages, and leaves an insight stub for you
3. **You** review, promote mature notes to permanent folders, and write your own synthesis in `wiki/insights/`

The agent handles extraction and first-pass structuring. You own promotion and synthesis.

---

## Setup

### 1. Open the workspace

Open this folder in **Cursor** or **VS Code with GitHub Copilot**. No configuration needed — the agent instructions are auto-loaded:
- Cursor auto-loads `.cursor/rules/wiki-agent.mdc`
- VS Code Copilot auto-loads `.github/copilot-instructions.md`

### 2. Fill in `docs/me.md`

This is the most important setup step. The agent reads it during every ingest to calibrate:
- What's personally relevant to you
- What importance level to assign
- What to write in the "My Notes" section

Open `docs/me.md` and fill in your background, current projects, active learning goals, and domains of interest.

### 3. Install document extraction dependencies (optional)

Only needed if you want to ingest non-markdown files:

```bash
pip install pymupdf4llm    # PDF
pip install python-docx    # DOCX
pip install openpyxl       # XLSX
pip install python-pptx    # PPTX
```

Or install all at once: `pip install -r requirements.txt`

Everything else works with zero dependencies.

---

## Directory Structure

```
raw/                      # IMMUTABLE — never modify files here
  inbox/                  # General captures, quick notes
  research/               # Papers, blogs, articles, videos, web clips, external references
  work/                   # Work docs, meeting notes, specs
  assets/                 # Images and attachments

wiki/                     # Agent owns this layer (except insights/)
  index.md                # Master catalog — updated on every ingest
  log.md                  # Append-only operation history
  overview.md             # Living synthesis across all sources
  notes/                  # First-pass generated notes (everything starts here)
  concepts/               # Atomic, permanent definitions (promoted manually)
  topics/                 # Maps of Content / curated topic surveys
  projects/               # Time-bounded work bodies of knowledge
  insights/               # YOUR synthesis — agent writes stubs only
  assets/                 # Images, diagrams, files for notes (see docs/assets.md)
    images/
    diagrams/
    files/

prompts/                  # Extraction templates per source type
  general.md              # Generic captures, inbox, work
  research.md             # Papers, articles, videos, external references
  refine.md               # Improving existing notes

docs/                     # Reference docs
  me.md                   # YOUR personal context ← fill this in
  TAGGING.md              # Tag taxonomy and rules
  WORKFLOW.md             # Daily/weekly/monthly cadence
  PIPELINES.md            # Source routing and pipeline details
  assets.md               # wiki/assets paths, media, video embed rules

tools/                    # Utility scripts (agent calls these)
  build_graph.py          # Knowledge graph builder (no deps)
  serve_graph.py          # Serves repo root over HTTP (graph + wiki media)
  extract.py              # PDF/DOCX/XLSX/PPTX -> structured markdown
  dedup.py                # Duplicate detection (no deps)

graph/                    # Auto-generated graph output
  graph.json              # Node/edge data
  graph.html              # Interactive vis.js visualization

.cursor/
  rules/wiki-agent.mdc    # Auto-injected into every Cursor AI request
  prompts/                # Cursor slash commands

.github/
  copilot-instructions.md # Auto-injected into every Copilot chat
  prompts/                # Copilot slash commands

AGENTS.md                 # Single source of truth for all agent workflows
requirements.txt          # pymupdf4llm, python-docx, openpyxl, python-pptx
```

---

## Commands Reference

All commands work as slash commands in Cursor or VS Code Copilot, or as plain English requests.

### `/wiki-ingest <path>`

Ingests a raw source file into the wiki.

```
/wiki-ingest raw/research/my-article.md
/wiki-ingest raw/research/attention-paper.pdf
/wiki-ingest raw/inbox/my-notes.md
```

**What the agent does:**
1. Reads `docs/me.md` to calibrate importance and My Notes
2. Detects source type from the `raw/` subfolder
3. If PDF/DOCX/XLSX/PPTX → runs `python tools/extract.py` first
4. Runs `python tools/dedup.py --check "<title>"` — flags duplicates before writing
5. Selects the right prompt template
6. Writes the wiki note with full frontmatter schema
7. Creates/updates concept pages
8. Updates `wiki/index.md` and `wiki/overview.md`
9. Creates an insight stub in `wiki/insights/`
10. Appends to `wiki/log.md`
11. Rebuilds `graph/graph.html`

---

### `/wiki-refine <path>`

Improves an existing wiki note — body only, frontmatter is never touched.

```
/wiki-refine wiki/notes/my-note.md
```

**What the agent does:** reads `prompts/refine.md`, rewrites for clarity, fills gaps, enriches My Notes from `docs/me.md`, adds wikilinks, then rebuilds `graph/graph.html`.

---

### `/wiki-query <question>`

Searches the wiki and synthesizes a cited answer.

```
/wiki-query What are the main approaches to LLM alignment?
/wiki-query Summarize everything I know about RAG
```

Agent reads up to ~10 relevant pages, synthesizes with `[[WikiLink]]` citations, offers to save the result to `wiki/notes/`, and refreshes `graph/graph.html` before finishing.

---

### `/wiki-lint`

Health check for the entire wiki.

Checks: broken `[[wikilinks]]`, orphan pages (no inbound links), duplicate notes (`tools/dedup.py --lint`), contradictions across pages, stale notes, missing concept pages, pending insight stubs, and response style drift (`tools/style_lint.py`).

Offers to save the report to `wiki/lint-report.md`, then rebuilds `graph/graph.html` before finishing.

---

### `/wiki-graph`

Runs `python tools/build_graph.py --open`.

Produces `graph/graph.html` — an interactive graph with pan, zoom, rotate, node search, connection highlighting. Nodes colored by type (source/entity/concept/synthesis). Opens in your browser automatically. This same graph refresh runs automatically after other `/wiki-*` workflows that update wiki state.

**Note:** `graph.html` loads **vis-network**, **marked**, **DOMPurify**, and **mermaid** from CDNs so `file://` works when local bundles are unavailable. You need network access for that path. **Local server (recommended for images in the panel):** `python tools/serve_graph.py` opens `http://127.0.0.1:8765/graph/graph.html` — the server roots at the **repo**, so `wiki/assets/...` loads in the reader pane. **Offline:** switch `<script>` / `<link>` in `graph/template.html` to local `./vis-network.min.js` (and siblings) and mirror the other libs if needed.

**Keyboard shortcuts in the graph:** `+`/`-` zoom · `F` fit · arrows pan · `R` rotate · `Esc` reset · `?` help

---

## Workflows

### Daily — Capture

Goal: get things in with zero friction. Don't process, just save.

| Source type | Where to drop |
|---|---|
| Quick note, idea, bullet capture | `raw/inbox/` |
| Blog post, article, newsletter | `raw/research/` |
| YouTube / podcast transcript | `raw/research/` |
| Research paper | `raw/research/` (PDF or `.md`) |
| Work doc, meeting note, spec | `raw/work/` |
| Anything else | `raw/inbox/` or a new subfolder (auto-routed) |

**Format:** plain `.md` or `.pdf`. Include the source URL if available. No other structure required.

---

### Weekly — Process

Goal: turn this week's captures into structured wiki notes.

1. Open Cursor or VS Code in this folder
2. Start with `raw/inbox/`, then the rest
3. Run `/wiki-ingest <path>` for each file
4. Handle any dedup flags the agent raises (skip / append / keep both)
5. Spot-check a few generated notes for quality
6. Optionally run `/wiki-lint` if the wiki is getting large

**Time estimate:** ~20–40 min depending on volume.

---

### Monthly — Promote & Synthesize

Goal: consolidate what you've learned, promote stable knowledge, write your own synthesis.

1. **Promote notes** — review `wiki/notes/`, move well-understood notes to `concepts/` or `topics/` (change `wiki_path` in frontmatter + move file)
2. **Write insights** — open `wiki/insights/`, pick 1–3 pending stubs, write your actual synthesis (this is the human-only layer — the agent never fills this in)
3. **Synthesize across sources** — run `/wiki-query` on cross-cutting themes, save good answers to `wiki/notes/`
4. **Review the graph** — it is refreshed automatically after `/wiki-query`, `/wiki-ingest`, `/wiki-refine`, and `/wiki-lint`; run `/wiki-graph` manually only when you want an extra refresh on demand
5. **Full lint** — run `/wiki-lint` for a complete health check
6. **Update your state tags** — change `state: to-learn` → `learning` → `understood` → `applied` as your understanding evolves

**Time estimate:** ~45–60 min.

---

## Source Type Routing

The agent selects a prompt template based on which `raw/` subfolder the file is in:

| raw/ subfolder | Prompt template | Default wiki output |
|---|---|---|
| `inbox/` | `prompts/general.md` | `wiki/notes/` |
| `research/` | `prompts/research.md` | `wiki/notes/` |
| `work/` | `prompts/general.md` | `wiki/projects/` |
| **any other subfolder** | `prompts/general.md` | `wiki/notes/` ← **fallback** |

**Key point:** you can freely create new subfolders under `raw/` (e.g. `raw/podcasts/`, `raw/courses/`, `raw/newsletters/`) without changing any rules. They auto-fall back to `general.md` + `notes/`. To give a folder its own template later, add it to this table in `docs/PIPELINES.md` and note it in `AGENTS.md`.

---

## Frontmatter Schema

Every wiki page uses this YAML frontmatter:

```yaml
---
title: "Specific, synthesized title"
type: concept | topic | paper | blog | video | workflow | project | idea | tooling | insight
domain: genai | ml | systems | data | product | research
tags:
  - <domain tag>        # e.g. genai
  - <type tag>          # e.g. paper
  - <facet tags...>     # e.g. attention-mechanism, fine-tuning
state: to-learn | learning | understood | applied   # optional — for active learning
importance: low | medium | high                     # default: medium
confidence: 0.0–1.0                                 # agent's confidence in extraction
sources:
  - raw/path/to/source.md
last_updated: YYYY-MM-DD
wiki_path: notes/my-note.md                     # determines which folder the note lives in
---
```

**`wiki_path` routing:**

| type value | folder |
|---|---|
| `concept` | `concepts/` |
| `topic` | `topics/` |
| `project` | `projects/` |
| `insight` | `insights/` |
| everything else | `notes/` |

---

## Tagging System

Full rules in `docs/TAGGING.md`. Summary:

**Domain tags** (exactly one): `genai` · `ml` · `systems` · `data` · `product` · `research`

**Type tags** (exactly one, matches `type` field): `concept` · `topic` · `paper` · `blog` · `video` · `workflow` · `project` · `idea` · `tooling`

**State tags** (optional): `to-learn` · `learning` · `understood` · `applied`

**Rules:**
- Minimum 3 tags, maximum 8
- For concepts already in the wiki, use `[[WikiLinks]]` instead of repeating tags
- Don't invent new domain or type tags — use the taxonomy
- Additional facet tags: lowercase, hyphen-separated (e.g. `rag`, `inference-optimization`)

---

## Prompt Templates

Located in `prompts/`. The agent reads these during ingest — you don't call them directly, but you can edit them to change extraction behavior.

| File | Used for | Key sections it produces |
|---|---|---|
| `general.md` | Inbox, work, anything unclassified | Overview · Core Ideas · Deep Explanation · Examples · Connections · Applications · Limitations · My Notes |
| `research.md` | Papers, articles, videos, external references | One-Line Thesis · Summary · Key Contributions · Novel Mechanisms · Comparisons · Limitations · Experiments · Glossary · My Notes |
| `refine.md` | Improving existing notes | (used by `/wiki-refine` — no new sections created) |

To change how a source type is extracted, edit the corresponding template file. The agent will use your updated instructions on the next ingest.

---

## Tool Scripts

Located in `tools/`. The agent calls these automatically — you rarely need to run them manually.

### `tools/build_graph.py`

Builds the knowledge graph. No dependencies.

```bash
python tools/build_graph.py          # build graph.json + graph.html
python tools/build_graph.py --open   # build + open in browser
```

Parses all `[[wikilinks]]` across `wiki/`, rewrites local `![](...)` image paths so the reader pane resolves them from `graph/graph.html`, then writes `graph/graph.json` and `graph/graph.html`, appends to `wiki/log.md`.

The interactive graph UI (edit `graph/template.html`, then rebuild) supports toggling labels, three label sizes, hover-only labels, an overview reset control, **Preview/Raw/Edit** in the reader pane with optional **save-to-disk** (see `serve_graph.py` below), reader **theme** colors, **node color by** type/folder/tag, **graph forces** sliders, and stores preferences in browser `localStorage` under **`wg-state-v4`** (older **`wg-state-v3`** is still read once for migration).

### `tools/serve_graph.py`

Serves the **repository root** on `http://127.0.0.1:8765/` by default so `graph/graph.html` can load `wiki/assets/...` images in the side panel. Use when **offline** (with local script bundles in `graph/`) or whenever `file://` media fails.

**Editing notes from the graph:** open the graph via this server (not `file://`), then use **Edit** → **Save** in the Content panel. Saving requires **`--allow-write`**, which enables **`PUT`** only for paths under **`wiki/`** ending in **`.md`**. The server binds to **`127.0.0.1`** only; never expose **`--allow-write`** on an untrusted network. If `PUT` is disabled or fails, the UI falls back to **downloading** the file for you to replace manually. After saving, run **`python tools/build_graph.py`** to refresh embedded graph data.

```bash
python tools/serve_graph.py              # opens /graph/graph.html in browser
python tools/serve_graph.py --no-open    # print URL only
python tools/serve_graph.py --allow-write  # allow graph UI to save wiki/*.md via PUT
```

---

### `tools/extract.py`

Extracts documents into structured LLM-ready markdown. Supports PDF, DOCX, XLSX, PPTX.

```bash
pip install pymupdf4llm python-docx openpyxl python-pptx  # one-time setup
python tools/extract.py raw/research/my-paper.pdf
python tools/extract.py raw/work/report.docx
python tools/extract.py raw/work/data.xlsx
python tools/extract.py raw/work/slides.pptx
```

Outputs: `<stem>_extracted.md` + `<stem>_images/` (for PDF/PPTX). Preserves text flow, converts tables to markdown, extracts images.

The agent runs this automatically when the source file is a `.pdf`, `.docx`, `.xlsx`, or `.pptx`.

---

### `tools/dedup.py`

Duplicate detection. No dependencies.

```bash
# Check a title before ingesting (returns JSON)
python tools/dedup.py --check "Attention Is All You Need"

# Audit the entire wiki for existing duplicate pairs
python tools/dedup.py --lint
```

The agent runs `--check` automatically before every new note write. Thresholds:
- Score ≥ 0.90 → **duplicate** — agent flags and asks: skip / append / keep both
- Score 0.70–0.89 → **related** — agent adds wikilinks between them
- Score < 0.70 → **new** — proceed normally

---

### `tools/style_lint.py`

Style guard for concise-first agent outputs. No dependencies.

```bash
python tools/style_lint.py
```

Scans instruction and prompt files for verbose-default wording (for example: `thorough`, `detailed`, `comprehensive`) unless those terms are explicitly gated by user request.

---

## Wiki Folder Hierarchy

```
wiki/notes/        ← everything lands here first (agent-written)
       ↓  (you promote when understood)
wiki/concepts/     ← atomic, permanent definitions
wiki/topics/       ← curated topic maps / MOCs
wiki/projects/     ← time-bounded work knowledge
       ↓  (you write)
wiki/insights/     ← YOUR synthesis (agent creates stubs, you fill them)
```

**Promoting a note:** change `wiki_path` in the frontmatter (e.g. `notes/rag.md` → `concepts/RAG.md`), update `state` if applicable, and move the file. Update `wiki/index.md` entry.

---

## Insight Workflow

`wiki/insights/` is the only folder the agent never fully writes — it creates stubs only:

```yaml
---
title: "Insight: <topic>"
type: insight
linked_note: wiki/notes/some-note.md
status: pending
created: 2026-04-11
---
```

You write the insight body when you're ready. An insight is your synthesis — what you actually think after reading multiple sources. It connects ideas, draws conclusions, identifies patterns. It's what makes the wiki yours.

**Workflow:** pending stub → you open it → you write the body → change `status: pending` to `status: complete`.

---

## Extending the Workspace

### Adding a new raw source folder

Just create it: `raw/podcasts/`, `raw/courses/`, `raw/newsletters/` — anything you want. The agent automatically falls back to `prompts/general.md` + `wiki/notes/`. No rule changes needed.

To give it a custom template later:
1. Create `prompts/podcasts.md` following the structure of an existing template
2. Add a row to the routing table in `docs/PIPELINES.md`
3. Add the same row to the prompt routing section in `AGENTS.md`

### Changing extraction behavior

Edit the prompt template file in `prompts/`. The next ingest for that source type will use your updated instructions. Don't change the frontmatter schema section unless you also update `AGENTS.md` to match.

### Changing the frontmatter schema

1. Update the schema in `AGENTS.md` (Frontmatter Schema section)
2. Update the schema block in the relevant `prompts/*.md` files
3. Update `.cursor/rules/wiki-agent.mdc` and `.github/copilot-instructions.md` if the change is significant

### Adding a new slash command

For **Cursor:** create `.cursor/prompts/<command-name>.md` with a `description:` frontmatter field.
For **Copilot:** create `.github/prompts/<command-name>.prompt.md` with `mode: agent` frontmatter.

Follow the structure of existing command files as a template.

### Changing dedup thresholds

Edit `tools/dedup.py`, lines near the top:
```python
DUPLICATE_THRESHOLD = 0.90   # change this
RELATED_THRESHOLD   = 0.70   # and this
```

---

## Key Rules

1. **Never modify files under `raw/`** — they are immutable source documents. The agent will never modify them either.
2. **`wiki/insights/` is human-only** — agent writes stubs (status: pending), you write the body.
3. **`wiki/log.md` is append-only** — every workflow operation appends a timestamped entry.
4. **Dedup runs before every write** — agent always checks for duplicates before creating a new note.
5. **`docs/me.md` is read on every ingest and query** — keep it up to date as your projects and goals change.
6. **`AGENTS.md` is the single source of truth** — if anything conflicts with another file, `AGENTS.md` wins.

# General Ingestion Prompt

Use this template for any source that doesn't match a more specific type (research papers, YouTube, blogs). Applies to: inbox captures, notes, articles, documentation, podcasts, newsletters, courses, or any unclassified source.

Before writing, read `docs/me.md` to calibrate relevance, importance, and the My Notes section.

---

## Required Output: YAML Frontmatter

```yaml
---
title: "Concise, specific title (not the file name — synthesize the actual concept)"
type: concept | topic | workflow | project | idea | tooling
domain: genai | ml | systems | data | product | research
tags:
  - <domain tag>
  - <type tag>
  - <additional facet tags — min 3, max 8 total>
state: to-learn | learning | understood | applied   # omit if not actively learning
importance: low | medium | high                     # default: medium; calibrate from docs/me.md
confidence: 0.0–1.0                                 # your confidence in the extraction accuracy
sources:
  - <original file path>
last_updated: <today's date YYYY-MM-DD>
wiki_path: <relative path within wiki/, e.g. summaries/my-note.md>
---
```

**Confidence calibration:**
- Noisy or incomplete source (quick note, partial transcript) → 0.4–0.6
- Opinion piece or personal note without citations → 0.5–0.6
- Well-structured article, documentation, or verified material → 0.7–0.9

**Routing rules for `wiki_path`:**
- `type: concept` → `concepts/<slug>.md`
- `type: topic` → `topics/<slug>.md`
- `type: project` → `projects/<slug>.md`
- Everything else → `notes/<slug>.md`

**Type decision tree (choose the first match):**
1. Is it an atomic definition or mechanism — a single well-bounded idea? → `concept`
2. Is it a curated map linking multiple concepts (a survey or MOC)? → `topic`
3. Is it a time-bounded body of work with deliverables? → `project`
4. Is it a process, procedure, or operational pattern? → `workflow`
5. Is it speculative, half-formed, or exploratory? → `idea`
6. Is it about a tool, library, framework, or platform? → `tooling`
7. Otherwise → keep the source format (`paper`, `blog`, `video`) and route to `notes/`

**Slug rules:** lowercase, hyphen-separated, ASCII, derived from title.

---

## Required Output: Note Body

### Overview
2–3 sentences. What is this? Why does it matter?

### Core Ideas
The essential content — distilled, no fluff. Use bullet points for lists of facts; prose for explanations. Aim for clarity over completeness.

### Deep Explanation
Expand on the most important or non-obvious aspects. Include mechanisms, how it works, key distinctions.

### Examples
Concrete illustrations, use cases, or instantiations of the core idea.

### Connections
- [[RelatedConcept]] — how it relates
- [[EntityName]] — role or relevance

### Applications
How this can be applied, what problems it solves, where it's used.

### Limitations & Open Questions
What doesn't this cover? What are the known weaknesses or unresolved aspects?

### My Notes
*Calibrate using `docs/me.md`.* What's personally relevant — connections to current work, projects, or learning goals. What to follow up on. What's surprising or actionable.

### Figures and diagrams (optional)
Include only when they materially aid understanding. Use relative image paths from this note (see `docs/assets.md`), e.g. `![](../assets/images/<slug>/fig1.png)`. You may add a fenced code block with language tag `mermaid` for flow/sequence/architecture when the source implies structure and prose alone is insufficient.

### Sources and media
**Required** if the note includes any image, Mermaid diagram, video embed, or file under `wiki/assets/`; otherwise a single line pointing to frontmatter `sources:` is enough.

| Kind | Description | Local path (if any) | Canonical source (URL and/or `raw/...`) | Retrieved |
|------|-------------|---------------------|-------------------------------------------|-----------|
| … | … | … | … | … |

---

## Media and assets (ingest rules)

- **Never** save new downloads into `raw/` — copy binaries into `wiki/assets/images/`, `wiki/assets/diagrams/`, or `wiki/assets/files/` (see `docs/assets.md`). After `extract.py`, copy needed figures from `raw/.../<stem>_images/` into `wiki/assets/...` and update `![](...)` paths.
- **Video:** embed URLs only (e.g. `https://www.youtube.com/embed/VIDEO_ID` or Vimeo equivalent); do not store video files in the wiki.

---

## Rules
- One concept per note. If the source covers multiple distinct topics, flag it and suggest splitting.
- Prefer `[[WikiLinks]]` for concepts over repeating tags.
- Do not invent facts not present in the source.
- Omit sections that genuinely don't apply rather than writing "N/A".

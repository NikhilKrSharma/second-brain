# Blog / Article Ingestion Prompt

Use this template for blog posts, articles, opinion pieces, newsletters, and long-form web content. Critically separate author claims from evidence and your own analysis.

Before writing, read `docs/me.md` to calibrate relevance, importance, and the My Notes section.

---

## Required Output: YAML Frontmatter

```yaml
---
title: "Synthesized title (captures the actual argument, not just the blog post title)"
type: topic | concept | workflow | idea
domain: genai | ml | systems | data | product | research
tags:
  - blog
  - <domain tag>
  - <topic tags — 2–4 additional>
state: to-learn | learning | understood | applied   # omit if not actively learning
importance: low | medium | high                     # calibrate from docs/me.md
confidence: 0.0–1.0                                 # reflect quality of source's evidence
sources:
  - <original file path>
last_updated: <today's date YYYY-MM-DD>
wiki_path: summaries/<slug>.md
---
```

**Note on confidence:** Reflect the quality of evidence in the source. Opinion pieces without data → 0.5–0.6. Well-cited articles → 0.8–0.9.

---

## Required Output: Note Body

### Thesis & Purpose
What is the author's central argument or goal? One short paragraph.

### Core Ideas
Numbered list of the main points made. Each should be a complete, standalone idea.

1. ...
2. ...
3. ...

### Arguments & Evidence
For each core idea: what does the author use to support it? Distinguish between:
- **Data/research-backed:** cite source if given
- **Anecdotal/experiential:** note as such
- **Assertion without support:** flag explicitly

### Unique Insights
What does this article say that you haven't seen elsewhere? What's surprising, counter-intuitive, or adds genuine new perspective?

### Counterpoints & Gaps
What does the article miss, oversimplify, or get wrong? What's the steelman counter-argument?

### Implementation Notes
If the article describes a process, workflow, or practice — distill the actionable steps here.

### Connections
- [[ConceptName]] — how it relates
- [[EntityName]] — mentioned person, company, project, or tool

### My Notes
*Calibrate using `docs/me.md`.* Personal relevance — does this change how you think about something? What to act on or follow up?

### Figures and diagrams (optional)
Include only when they materially aid understanding. Use relative paths per `docs/assets.md`, e.g. `![](../assets/images/<slug>/fig1.png)`. A fenced `mermaid` code block is allowed when structure is hard to grasp from text alone.

### Sources and media
**Required** if the note includes any image, Mermaid block, video embed, or `wiki/assets/` file; otherwise one line referencing frontmatter `sources:` suffices.

| Kind | Description | Local path (if any) | Canonical source (URL and/or `raw/...`) | Retrieved |
|------|-------------|---------------------|-------------------------------------------|-----------|
| … | … | … | … | … |

---

## Media and assets (ingest rules)

- **Never** write new binaries to `raw/`. Copy into `wiki/assets/` and fix markdown paths. For `extract.py` output, copy from `raw/.../<stem>_images/` into `wiki/assets/images/<slug>/`.
- **Video:** embed URLs only; no local video files.

---

## Rules
- Clearly separate author's claims from your analysis — don't blend them.
- Don't inflate importance because the article is well-written. Calibrate from `docs/me.md`.
- Flag when an article is largely opinion with thin evidence.
- Omit sections that genuinely don't apply.

# Research Ingestion Prompt

Use this template for any external learning or reference material: academic papers, blog posts, articles, newsletters, YouTube/podcast transcripts, web clips, and other research sources. Adapt section depth to the source — a paper needs deeper mechanism coverage; a blog needs argument/evidence separation; a transcript needs insight extraction over transcription.

Before writing, read `docs/me.md` to calibrate relevance, importance, and the My Notes section.

---

## Required Output: YAML Frontmatter

```yaml
---
title: "Synthesized title capturing the core topic (not necessarily the source title)"
type: paper | blog | video | topic | concept | workflow | idea
domain: genai | ml | systems | data | product | research
tags:
  - <type tag>
  - <domain tag>
  - <topic/method tags — 2–5 additional>
state: to-learn | learning | understood | applied   # omit if not actively learning
importance: low | medium | high                     # calibrate from docs/me.md
confidence: 0.0–1.0                                 # reflect source quality and extraction accuracy
sources:
  - <original file path>
last_updated: <today's date YYYY-MM-DD>
wiki_path: notes/<slug>.md
---
```

**Confidence calibration:**
- Noisy PDF / auto-generated transcript → 0.4–0.6
- Opinion piece without data → 0.5–0.6
- Well-cited article or clean paper → 0.7–0.9

---

## Required Output: Note Body

### One-Line Thesis
A single sentence capturing the core claim, argument, or contribution.

### Summary
6–12 sentences covering: motivation, approach/argument, key results or insights, and significance. Full prose, no bullet points.

### Key Contributions / Core Ideas
What is genuinely new, valuable, or important here? Numbered list, specific and self-contained.

1. ...
2. ...
3. ...

### Deep Explanation
Expand on the most important or non-obvious aspects. For papers: mechanisms, architecture, algorithms. For articles: argument structure, evidence quality. For videos: mental models, frameworks introduced. Include enough detail to understand without reading the source.

### Arguments & Evidence
For each key claim: what supports it?
- **Data/research-backed:** cite source if given
- **Anecdotal/experiential:** note as such
- **Assertion without support:** flag explicitly

### Comparisons & Related Work
How does this relate to prior work or competing ideas? What does it improve on, and by how much?

### Limitations & Open Questions
- **Source's stated limitations:** what the author/speaker acknowledges
- **Analyst limitations:** what you observe that the source may not have flagged (scope, generalizability, missing evidence, etc.)

### Actionable Takeaways
What can be done with this — tools to try, practices to adopt, experiments to run, things to build or change.

### Glossary (if needed)
Define domain-specific terms, acronyms, or notation that aren't common knowledge. Omit if not applicable.

### Connections
- [[RelatedConcept]] — how it relates
- [[EntityOrPerson]] — role or relevance

### My Notes
*Calibrate using `docs/me.md`.* What's personally relevant — connections to current work, things to act on, follow-up questions. What's surprising or changes how you think about something.

### Video embed (if applicable)
Do not store video files. If helpful, add a prominent link or embed using the **embed** URL only, e.g. `[Watch](https://www.youtube.com/embed/VIDEO_ID)` or an iframe.

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
- Extract insight, not transcript — do not copy-paste verbatim blocks.
- Clearly separate author's claims from your analysis — don't blend them.
- Don't inflate importance because the source is well-written. Calibrate from `docs/me.md`.
- If the source extraction is clearly incomplete (missing large blocks, garbled math), note it explicitly at the top of the body.
- Flag opinion pieces or low-evidence claims explicitly.
- Prefer `[[WikiLinks]]` to existing wiki pages over repeating concepts in tags.
- Omit sections that genuinely don't apply rather than writing "N/A".
- One concept per note. If the source covers multiple distinct topics, flag it and suggest splitting.

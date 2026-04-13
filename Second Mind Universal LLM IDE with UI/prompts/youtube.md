# YouTube / Video Ingestion Prompt

Use this template for YouTube video transcripts, talk recordings, podcast transcripts, or any spoken-word source. The source file should include the video/episode title, URL or channel, and the transcript text.

Before writing, read `docs/me.md` to calibrate relevance, importance, and the My Notes section.

---

## Required Output: YAML Frontmatter

```yaml
---
title: "Synthesized title capturing the core topic (not necessarily the video title)"
type: topic | concept | workflow | idea
domain: genai | ml | systems | data | product | research
tags:
  - video
  - <domain tag>
  - <topic tags — 2–4 additional>
state: to-learn | learning | understood | applied   # omit if not actively learning
importance: low | medium | high                     # calibrate from docs/me.md
confidence: 0.0–1.0                                 # lower for poor-quality transcripts
sources:
  - <original file path>
last_updated: <today's date YYYY-MM-DD>
wiki_path: summaries/<slug>.md
---
```

---

## Required Output: Note Body

### Context
Speaker/channel, format (lecture, interview, talk, podcast), approximate date if available. One paragraph.

### Key Insights
The most valuable ideas from the video — distilled, not transcribed. 5–10 bullet points. Each should be a self-contained, specific insight, not a vague summary.

### Mental Models & Frameworks
Any conceptual models, heuristics, or structured ways of thinking introduced. Explain each clearly.

### Actionable Takeaways
What can be done with this — tools to try, practices to adopt, things to build or change.

### Claims to Verify
Assertions made that aren't self-evidently true and merit independent checking. Note speaker confidence vs. actual evidence.

### Connections
- [[ConceptName]] — how it connects
- [[EntityName]] — mentioned person, company, or project

### My Notes
*Calibrate using `docs/me.md`.* What's personally relevant — connections to current work, things to act on, follow-up questions.

### Video embed (optional)
Do not store video files. If helpful, add a prominent link or embed using the **embed** URL only, e.g. `[Watch](https://www.youtube.com/embed/VIDEO_ID)` or an iframe to the same pattern / Vimeo `player.vimeo.com/video/...`.

### Figures and diagrams (optional)
Thumbnails or slides rarely apply; use only if the source file includes meaningful images — store under `wiki/assets/images/<slug>/` per `docs/assets.md`. Mermaid allowed for talk structure when it adds clarity.

### Sources and media
Include the canonical watch URL, transcript `raw/...` path, and any embed used.

| Kind | Description | Local path (if any) | Canonical source (URL and/or `raw/...`) | Retrieved |
|------|-------------|---------------------|-------------------------------------------|-----------|
| … | … | … | … | … |

---

## Media and assets (ingest rules)

- **Video:** embed URLs only; no local video files in `wiki/assets/`.
- **Images:** follow `docs/assets.md`; never place new downloads under `raw/` except the transcript source already there.

---

## Rules
- Extract insight, not transcript. Do not copy-paste verbatim blocks.
- If the transcript quality is poor (auto-generated, heavily garbled), lower confidence and note quality issues.
- Separate factual claims from opinions — attribute clearly if it matters.
- Omit sections that genuinely don't apply.

# Research Paper Ingestion Prompt

Use this template for academic papers, preprints, and technical reports. The source may be a clean markdown export or a PDF-extracted text (possibly noisy — handle gracefully).

Before writing, read `docs/me.md` to calibrate relevance, importance, and the My Notes section.

---

## Required Output: YAML Frontmatter

```yaml
---
title: "Paper title — exact or lightly cleaned"
type: paper
domain: genai | ml | systems | data | product | research
tags:
  - paper
  - <domain tag>
  - <method/topic tags — 2–5 additional>
state: to-learn | learning | understood | applied   # omit if not actively learning
importance: low | medium | high                     # calibrate from docs/me.md
confidence: 0.0–1.0                                 # lower if source was OCR/noisy PDF
sources:
  - <original file path>
last_updated: <today's date YYYY-MM-DD>
wiki_path: summaries/<slug>.md
---
```

**Note on confidence:** Set lower (0.5–0.7) if extraction was from a noisy PDF, if tables/figures were lost, or if mathematical notation was garbled.

---

## Required Output: Note Body

### One-Line Thesis
A single sentence capturing the core claim or contribution.

### Summary
8–12 sentences covering: motivation, approach, key results, and significance. No bullet points here — full prose.

### Key Contributions
- What is genuinely new here (method, dataset, benchmark, insight)?
- Numbered, specific, not generic.

### Novel Mechanisms or Techniques
Explain *how* the core technical approach works. Include architecture decisions, training procedures, algorithmic steps — enough detail to understand the mechanism without reading the paper.

### Comparisons & Related Work
How does this relate to prior work? What does it improve on, and by how much? What baselines does it beat?

### Limitations
**Paper's stated limitations:** what the authors acknowledge.
**Analyst limitations:** what you observe that the authors may not have flagged (scope, generalizability, missing ablations, etc.).

### Experiments & Results
Key numbers, datasets, evaluation protocols. Be specific — include metric names and values where available.

### Glossary
Define domain-specific terms, acronyms, or notation used in the paper that aren't common knowledge.

### Connections
- [[RelatedPaper]] — how it relates
- [[ConceptName]] — concept this paper advances or relies on

### My Notes
*Calibrate using `docs/me.md`.* How does this connect to current work or interests? What would you want to try, reproduce, or read next? What claims need verification?

### Figures and diagrams (optional)
When figures from the paper matter for understanding, copy them from `raw/.../<stem>_images/` (after extraction) into `wiki/assets/images/<slug>/` and embed with relative `![](...)` paths per `docs/assets.md`. Add Mermaid only for high-level method or system flow when no figure exists and it clarifies the mechanism.

### Sources and media
**Required** if any image, diagram export, or Mermaid block is included; list each figure’s original label/page and source PDF path.

| Kind | Description | Local path (if any) | Canonical source (URL and/or `raw/...`) | Retrieved |
|------|-------------|---------------------|-------------------------------------------|-----------|
| … | … | … | … | … |

---

## Media and assets (ingest rules)

- Do not manually add new files under `raw/`; `extract.py` may write `_extracted.md` and `_images/` next to the PDF. Copy promoted images into `wiki/assets/` for the wiki note; reference them with paths relative to the note file.

---

## Rules
- Do not hallucinate experimental results — if numbers aren't in the source, omit them.
- If the PDF extraction is clearly incomplete (missing large blocks), note it explicitly at the top of the body.
- Flag mathematical notation that was garbled and couldn't be recovered.
- Prefer [[WikiLinks]] to existing wiki pages over repeating concepts in tags.

# Tagging System

All wiki pages must follow this tagging schema. Tags are facets — they make notes discoverable. Prefer `[[WikiLinks]]` for concepts (they create graph edges); use tags for domain, type, and state facets.

---

## Domain Tags (exactly one per note)

| Tag | Covers |
|---|---|
| `genai` | Generative AI, LLMs, foundation models, prompting, fine-tuning, agents |
| `ml` | Classical ML, deep learning, computer vision, NLP, training, evaluation |
| `systems` | Distributed systems, infrastructure, databases, networking, OS |
| `data` | Data engineering, pipelines, storage, processing, analytics |
| `product` | Product thinking, strategy, GTM, growth, UX, metrics |
| `research` | Research methodology, academic processes, meta-science |

If a note spans two domains, pick the primary one. Do not invent new domain tags.

---

## Type Tags (exactly one per note — must match frontmatter `type` field)

| Tag / Type | Use for |
|---|---|
| `concept` | Atomic definition or mechanism — a single well-bounded idea |
| `topic` | Curated map of concepts, a survey, or a MOC (Map of Content) |
| `paper` | Academic paper or preprint |
| `blog` | Blog post, article, newsletter, opinion piece |
| `video` | YouTube video, talk, lecture, podcast episode |
| `workflow` | Process, procedure, or operational pattern |
| `project` | Time-bounded body of work |
| `idea` | Speculative, half-formed, or exploratory |
| `tooling` | Tools, libraries, frameworks, platforms |

---

## State Tags (optional — use only when actively engaging with the material)

| Tag | Meaning |
|---|---|
| `to-learn` | Captured, not yet processed |
| `learning` | Actively studying |
| `understood` | Solid grasp, could explain it |
| `applied` | Used in real work |

State tags are for your active learning queue. Leave them off for reference material you're just archiving.

---

## Importance Field (frontmatter, not a tag)

Set in YAML as `importance: low | medium | high`. Default is `medium`.

Use `docs/me.md` to calibrate — high importance means directly relevant to current projects, domain expertise, or active learning goals.

---

## Rules

- Minimum 3 tags, maximum 8.
- One domain tag, one type tag, optional state tag, remaining are facets.
- For concepts already in the wiki, use `[[WikiLinks]]` instead of creating a tag.
- Do not create new domain or type tags — use the defined taxonomy.
- Additional facet tags should be lowercase, hyphen-separated (e.g. `attention-mechanism`, `fine-tuning`, `rag`).

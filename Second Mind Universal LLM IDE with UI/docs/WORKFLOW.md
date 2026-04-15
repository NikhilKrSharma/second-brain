# Operating Workflow

How to use this knowledge system day-to-day. The goal is low friction capture, consistent processing, and periodic synthesis — all driven by agent commands.

---

## Daily — Capture

**What:** Save anything worth keeping as a raw file. Don't process yet — just get it in.

| Source type | Where to save |
|---|---|
| Quick notes, bullets, ideas | `raw/inbox/` (use `now/` if time-sensitive) |
| Blog posts, articles | `raw/research/` |
| YouTube / video transcripts | `raw/research/` |
| Research papers (PDF or text) | `raw/research/` |
| Work-related materials | `raw/work/` |
| Anything else | `raw/inbox/` or create a subfolder under `raw/` |

**Format for raw files:**
- Plain markdown (`.md`) or PDF
- Include the source URL in a comment or frontmatter if available
- No structure required — just get it in

---

## Weekly — Process

**What:** Turn raw captures into wiki notes using `/wiki-ingest`.

1. Review what's accumulated in `raw/` (start with `raw/inbox/`)
2. For each file, run `/wiki-ingest <path>`
3. The agent: detects type → selects prompt template → runs dedup check → writes wiki note → creates insight stub
4. For PDFs/DOCX/XLSX/PPTX: agent calls `python tools/extract.py <path>` first, then ingests the output
5. Review any dedup flags the agent raised — decide whether to merge, skip, or keep both
6. Run `/wiki-lint` occasionally to catch broken links and orphan pages

---

## Monthly — Promote & Synthesize

**What:** Review summaries and promote stable knowledge into permanent pages.

1. Review `wiki/notes/` — what has become well-understood?
   - Promote mature notes by changing `wiki_path` to `concepts/` or `topics/`
   - Update `state` tag to `understood` or `applied`
2. Review `wiki/insights/` stubs — write 1–3 completed insight notes (human-only)
3. Run `/wiki-query` on cross-cutting themes to synthesize across sources
4. Save good query answers as `wiki/notes/` pages
5. Review tags for consistency — prune or consolidate facet tags
6. Review `graph/graph.html` to see what's connected; it is refreshed automatically after each `/wiki-*` workflow, and you can still run `/wiki-graph` on demand. For notes with images under `wiki/assets/`, run `python tools/serve_graph.py` and open `http://127.0.0.1:8765/graph/graph.html` so the reader pane can load media over HTTP.

---

## Insight Workflow (ongoing)

`wiki/insights/` is **human-only** — the agent never writes completed insights, only stubs.

When the agent ingests a source, it creates a stub:
```yaml
---
title: "Insight: <topic>"
type: insight
linked_note: <wiki path of the source note>
status: pending
created: YYYY-MM-DD
---
```

You write the insight when you're ready. An insight is synthesis — it connects ideas, draws conclusions, identifies patterns across multiple sources. It's what you actually think, not what a source says.

---

## Key Principle

> `raw/` → agent process → `wiki/notes/` → human promote → `concepts/` / `topics/` / `insights/`

The agent handles extraction and first-pass structuring. You own promotion and synthesis.

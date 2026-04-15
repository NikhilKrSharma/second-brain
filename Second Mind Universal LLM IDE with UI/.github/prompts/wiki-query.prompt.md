---
mode: agent
description: Query the LLM Wiki and synthesize an answer
---

Query the LLM Wiki and synthesize an answer.

The argument is the question to answer, e.g. `What are the main themes across all sources?`

Follow the Query Workflow defined in AGENTS.md:
1. Read wiki/index.md to identify the most relevant pages
2. Read docs/me.md to personalize the answer
3. Read those pages (up to ~10 most relevant)
4. Synthesize a concise first-stage answer with [[PageName]] wikilink citations
	- Use fixed headings: `Outcome`, `Key Points`, `Next Step`
	- Put the primary synthesis in `Key Points` as 3-5 bullets by default
	- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`
	- Expand into a detailed explanation only if the user explicitly asks
5. Include a ## Sources section at the end listing pages you drew from
6. Ask the user if they want the answer saved as wiki/notes/<slug>.md
7. If saving: append to wiki/log.md: ## [today's date] query | <question>
8. Rebuild the graph by running `python tools/build_graph.py --open` so graph/graph.html is refreshed before the workflow completes

If the wiki is empty, say so and suggest running /wiki-ingest first.

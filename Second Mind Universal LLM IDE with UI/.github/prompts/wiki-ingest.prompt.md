---
mode: agent
description: Ingest a source document into the LLM Wiki
---

Ingest a source document into the LLM Wiki.

The argument should be the path to a file in raw/, e.g. `raw/blogs/my-article.md`

Follow the Ingest Workflow defined in AGENTS.md exactly:

1. Read docs/me.md — calibrate importance and My Notes section
2. Detect source type from the raw/ subfolder path
3. If the file is a .pdf, .docx, .xlsx, or .pptx — run `python tools/extract.py <path>`, then ingest the _extracted.md output instead
4. Determine the proposed wiki title from the source
5. Run dedup check: `python tools/dedup.py --check "<proposed title>"`
   - Score >= 0.90 → stop, flag as likely duplicate, ask user: skip / append / keep both
   - Score 0.70-0.89 → proceed, note the related page, add wikilinks between them
   - Score < 0.70 → proceed normally
6. Select prompt template based on raw/ subfolder:
   - research_papers/ → prompts/research_paper.md
   - youtube/ → prompts/youtube.md
   - blogs/ → prompts/blog.md
   - clips/ → prompts/blog.md
   - work/ → prompts/general.md → wiki/projects/
   - anything else → prompts/general.md → wiki/summaries/
7. Read the source file fully
8. Read wiki/index.md and wiki/overview.md for current wiki context
9. Write the wiki note following the selected prompt template (frontmatter schema + body)
10. Create/update entity pages (wiki/entities/) for key people, companies, projects
11. Create/update concept pages (wiki/concepts/) for key ideas and frameworks
12. Update wiki/index.md — add entry in the correct section
13. Update wiki/overview.md — revise synthesis if warranted
14. Create insight stub in wiki/insights/<slug>.md (status: pending, linked_note: <wiki_path>)
15. Flag any contradictions with existing wiki content
16. Append to wiki/log.md: ## [today's date] ingest | <Title>
17. Rebuild the graph by running `python tools/build_graph.py --open` so graph/graph.html reflects the new wiki state

After completing all writes, respond using fixed headings: `Outcome`, `Key Points`, `Next Step`.
- Keep `Key Points` to 3-5 bullets by default.
- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`.
- Include: what was added, pages created/updated, dedup flags, contradictions.
- Expand only if the user explicitly asks for more detail.

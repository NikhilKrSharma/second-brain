---
mode: agent
description: Health-check the LLM Wiki for issues
---

Health-check the LLM Wiki for issues.

Follow the Lint Workflow defined in AGENTS.md:

Structural checks (use search tools):
1. Orphan pages — wiki pages with no inbound [[wikilinks]] from other pages
2. Broken links — [[WikiLinks]] pointing to pages that don't exist
3. Duplicate notes — run `python tools/dedup.py --lint`
4. Missing concept pages — concepts or entities referenced in 3+ pages but lacking their own page
5. Pending insight stubs — count and list wiki/insights/ pages with `status: pending`

Semantic checks (read and reason over page content):
6. Contradictions — claims that conflict between pages
7. Stale notes — pages not updated after newer sources changed the picture
8. Data gaps — important questions the wiki can't answer; suggest specific sources to find
9. Response style drift — run `python tools/style_lint.py` and include findings

Output using fixed headings: `Outcome`, `Key Points`, `Next Step`.
- Keep `Key Points` to 3-5 bullets by default.
- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`.
- Expand only if the user explicitly asks for more detail.
At the end, ask if the user wants it saved to wiki/lint-report.md.

Append to wiki/log.md: ## [today's date] lint | Wiki health check
Then rebuild the graph by running `python tools/build_graph.py --open` so graph/graph.html reflects the latest wiki state.

---
name: wiki-refine
description: Improve an existing wiki note. Use when the user asks to refine, polish, or clarify a wiki page.
---

# Wiki Refine

Improve an existing wiki note.

Usage: /wiki-refine <wiki-path>

The argument should be the path to an existing wiki note, e.g. `wiki/notes/my-note.md`

Follow the Refine Workflow defined in AGENTS.md:

1. Read the target wiki note fully
2. Read docs/me.md - calibrate the My Notes section and relevance
3. Read prompts/refine.md - follow its instructions exactly
4. Improve the note body:
   - Rewrite unclear or dense passages for clarity
   - Fill obvious gaps using only information already present in the note
   - Enrich the My Notes section using context from docs/me.md
   - Add [[WikiLinks]] where a concept clearly maps to an existing wiki page
   - Remove filler, redundancy, and hedging language
5. Preserve the frontmatter (YAML) exactly - do not change any fields
6. Preserve all section headings exactly
7. Overwrite the file with the improved body
8. Append to wiki/log.md: ## [today's date] refine | <Title>

After completing, respond using fixed headings: `Outcome`, `Key Points`, `Next Step`.
- Keep `Key Points` to 3-5 bullets by default.
- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`.
- Focus on what changed and why at a high level.
- Expand only if the user explicitly asks for more detail.

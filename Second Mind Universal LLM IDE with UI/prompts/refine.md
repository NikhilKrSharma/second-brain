# Note Refinement Prompt

Use this template to improve an existing wiki note. You will receive the current note body (without frontmatter). Improve it and return only the improved body — no YAML, no fences.

Before refining, read `docs/me.md` to calibrate the My Notes section and relevance assessments.

---

## What to improve

- **Clarity:** Rewrite unclear or overly dense passages. Prefer plain language.
- **Structure:** Ensure sections are properly separated and logically ordered.
- **Completeness:** Fill obvious gaps if the current body is thin. Don't add invented facts — only infer from what's already present.
- **My Notes:** If the section is empty, thin, or generic, enrich it using context from `docs/me.md`.
- **Wikilinks:** Add `[[WikiLinks]]` where a concept or entity clearly maps to an existing wiki page. Don't add speculative links.
- **Conciseness:** Remove filler, redundancy, and hedging language that adds no value.

## What NOT to change

- The frontmatter (YAML) — do not touch it at all
- Section headings — preserve them exactly
- Factual claims already present — don't contradict or silently change them
- The overall scope of the note — don't expand into a different topic
- **Media:** Keep `![](...)` paths, fenced `mermaid` code blocks, video embeds/iframes, and the **Sources and media** table unless you are fixing an obvious path error (see `docs/assets.md`)

## Output contract

Return the improved markdown body only. No YAML block, no code fences, no commentary. Start directly with the first section heading.

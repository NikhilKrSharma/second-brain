# Obsidian integration

## Using `wiki/` as the vault (recommended)

Point Obsidian at **`wiki/`** only if this repository is dedicated to processed knowledge. If you already have a larger vault, symlink `wiki/` into it:

```bash
ln -s /path/to/knowledge-system/wiki /path/to/MainVault/knowledge-wiki
```

Then open your main vault and edit notes under the symlinked folder.

## Wikilinks `[[...]]`

- Links resolve by **note title = filename without `.md`** (Obsidian default).
- Use aliases when titles collide: `[[Attention Is All You Need|Transformer paper]]`.
- Prefer links to `concepts/` from `summaries/` to build a dense graph.

## Graph view

- **Filter:** `path:wiki/concepts` to see the conceptual core.
- **Pin** important hubs (e.g. “GenAI map”) in `wiki/topics/`.
- **Orphans:** periodically link orphan notes from a MOC note.

## Insights layer

- `wiki/insights/` is for **your** synthesis: decisions, opinions, “what I believe now”, career narratives.
- Do not bulk-move LLM output here; promote only after editing and endorsing every sentence.
- Template habit: end each insight with “Sources:” linking `[[...]]` to evidence notes.

## Optional plugins (non-required)

- Dataview: query by `tags` frontmatter.
- Templater: insert capture templates into `raw/inbox` outside Obsidian (text editor) if you prefer.

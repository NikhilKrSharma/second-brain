---
name: wiki-graph
description: Build the LLM Wiki knowledge graph. Use when the user asks to build or refresh wiki graph output.
---

# Wiki Graph

Build the LLM Wiki knowledge graph.

Usage: /wiki-graph

Run the script:
```
python tools/build_graph.py --open
```

The script is pure Python stdlib (no dependencies). It will:
1. Parse all [[wikilinks]] across wiki pages
2. Build nodes (one per page) and edges (one per link), tagged EXTRACTED
3. Write graph/graph.json with {nodes, edges, built: today}
4. Write graph/graph.html as a self-contained vis.js visualization
5. Append to wiki/log.md automatically

After the script completes, respond using fixed headings: `Outcome`, `Key Points`, `Next Step`.
- Keep `Key Points` to 3-5 bullets by default.
- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`.
- Include node count, edge count, and most connected nodes (hubs).
- Expand only if the user explicitly asks for more detail.

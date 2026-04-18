---
mode: agent
description: Build the LLM Wiki knowledge graph
---

Build the LLM Wiki knowledge graph.

> **Note:** Run `start-graph.sh` to build and see the interactive graph.
> It will automatically start the server and open the graph in your browser.

```bash
./start-graph.sh
```

This builds the knowledge graph by:
1. Parsing all [[wikilinks]] across wiki pages
2. Building nodes (one per page) and edges (one per link)
3. Writing graph/graph.json with {nodes, edges, built: today}
4. Writing graph/graph.html as a self-contained vis.js visualization
5. Starting a local server on http://127.0.0.1:8765/graph/graph.html
6. Appending to wiki/log.md automatically

After the script completes, respond using fixed headings: `Outcome`, `Key Points`, `Next Step`.
- Keep `Key Points` to 3-5 bullets by default.
- Include one `Key Points` bullet: `Files changed: <created/modified file paths>`; if none, state `Files changed: none`.
- Include node count, edge count, and most connected nodes (hubs).
- Expand only if the user explicitly asks for more detail.

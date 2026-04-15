#!/usr/bin/env python3
"""
Build the LLM Wiki knowledge graph.

Usage:
    python tools/build_graph.py          # build graph.json + graph.html
    python tools/build_graph.py --open   # also open graph.html in browser

No external dependencies — pure Python stdlib.

Outputs:
    graph/graph.json   — node/edge data
    graph/graph.html   — interactive vis.js UI (CDN libs; see template comment)

Local markdown image paths in note bodies are rewritten to URLs relative to ``graph/`` so the
reader pane resolves ``wiki/assets/`` when opened via ``file://`` or ``python tools/serve_graph.py``.
"""

import os
import re
import json
import argparse
import webbrowser
from pathlib import Path
from datetime import date
from typing import List, Optional

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
GRAPH_DIR = REPO_ROOT / "graph"
LOG_FILE = WIKI_DIR / "log.md"

TYPE_COLORS = {
    "paper":     "#4e9af1",
    "blog":      "#4e9af1",
    "video":     "#4e9af1",
    "concept":   "#f5a623",
    "topic":     "#e0a040",
    "project":   "#e06050",
    "workflow":  "#8899aa",
    "idea":      "#cc77dd",
    "tooling":   "#cc77dd",
    "insight":   "#ff8899",
}
DEFAULT_COLOR = "#aaaaaa"

EDGE_COLORS = {
    "EXTRACTED": "#888888",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict:
    """Extract simple key: value pairs from YAML frontmatter."""
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def find_wikilinks(text: str) -> List[str]:
    """Return all [[PageName]] targets found in text."""
    return re.findall(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]", text)


def page_id(path: Path) -> str:
    """Stable node ID: wiki-relative path with forward slashes."""
    return path.relative_to(WIKI_DIR).as_posix()


_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def rewrite_local_image_paths_for_graph(
    body: str,
    note_path: Path,
    repo_root: Path,
    graph_dir: Path,
) -> str:
    """Rewrite markdown image targets so they resolve from graph/graph.html.

    Note files use paths relative to the note (e.g. ``../assets/images/x.png``).
    The graph panel loads HTML whose base URL is ``graph/graph.html``, so we
    emit paths relative to ``graph_dir`` (typically ``../wiki/assets/...``).
    """

    def repl(m: re.Match[str]) -> str:
        alt = m.group(1)
        rest = m.group(2).strip()
        if rest.startswith(("http://", "https://", "data:")):
            return m.group(0)
        url = rest.split()[0].strip("<>")
        if not url or url.startswith(("#", "mailto:")):
            return m.group(0)
        try:
            resolved = (note_path.parent / url).resolve()
        except (OSError, RuntimeError):
            return m.group(0)
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            return m.group(0)
        if not resolved.is_file():
            return m.group(0)
        try:
            rel = Path(os.path.relpath(resolved, graph_dir)).as_posix()
        except ValueError:
            return m.group(0)
        return f"![{alt}]({rel})"

    return _MD_IMAGE.sub(repl, body)


def slug_to_path(slug: str) -> Optional[Path]:
    """Resolve a [[Slug]] to a file path, tolerating missing extension."""
    candidates = [
        WIKI_DIR / f"{slug}.md",
        WIKI_DIR / "notes" / f"{slug}.md",
        WIKI_DIR / "concepts" / f"{slug}.md",
        WIKI_DIR / "topics" / f"{slug}.md",
        WIKI_DIR / "projects" / f"{slug}.md",
        WIKI_DIR / "insights" / f"{slug}.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def parse_tags(text: str) -> List[str]:
    """Extract tags list from YAML frontmatter (handles list-style and inline)."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    # Find tags: block
    tm = re.search(r"^tags:\s*\n((?:  - .+\n?)+)", block, re.MULTILINE)
    if tm:
        return [l.strip().lstrip("- ").strip() for l in tm.group(1).splitlines() if l.strip()]
    # Inline: tags: [a, b]
    im = re.search(r"^tags:\s*\[([^\]]*)\]", block, re.MULTILINE)
    if im:
        return [t.strip().strip('"').strip("'") for t in im.group(1).split(",") if t.strip()]
    return []


def build(open_after: bool = False) -> None:
    GRAPH_DIR.mkdir(exist_ok=True)
    repo_root = REPO_ROOT.resolve()
    graph_dir = GRAPH_DIR.resolve()

    pages = [p for p in WIKI_DIR.rglob("*.md") if p.name not in ("log.md", "index.md", "overview.md")]

    nodes = {}
    raw_edges = []        # (source_id, target_slug)
    broken_links = []     # (source_id, source_label, slug) — unresolved wikilinks

    for path in pages:
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        nid = page_id(path)
        node_type = fm.get("type", "")
        # Strip frontmatter for display content
        body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)
        body_out = rewrite_local_image_paths_for_graph(
            body.strip(),
            path.resolve(),
            repo_root,
            graph_dir,
        )
        tags = parse_tags(text)
        nodes[nid] = {
            "id":           nid,
            "label":        fm.get("title", path.stem),
            "type":         node_type,
            "color":        TYPE_COLORS.get(node_type, DEFAULT_COLOR),
            "content":      body_out,
            "last_updated": fm.get("last_updated", ""),
            "tags":         tags,
            "wiki_path":    fm.get("wiki_path", nid),
            "sources":      fm.get("sources", ""),
            "meta": {
                "domain":     fm.get("domain", ""),
                "importance": fm.get("importance", ""),
                "state":      fm.get("state", ""),
                "confidence": fm.get("confidence", ""),
            },
        }
        for link in find_wikilinks(text):
            raw_edges.append((nid, link.strip()))

    # Resolve edges — only keep links to known pages
    edges = []
    seen = set()
    for src_id, target_slug in raw_edges:
        target_path = slug_to_path(target_slug)
        if target_path is None:
            src_label = nodes.get(src_id, {}).get("label", src_id)
            broken_links.append({"from_id": src_id, "from_label": src_label, "slug": target_slug})
            continue
        tgt_id = page_id(target_path)
        key = (src_id, tgt_id)
        if key in seen or src_id == tgt_id:
            continue
        seen.add(key)
        edges.append({
            "from":  src_id,
            "to":    tgt_id,
            "type":  "EXTRACTED",
            "color": EDGE_COLORS["EXTRACTED"],
        })

    graph = {
        "nodes":        list(nodes.values()),
        "edges":        edges,
        "broken_links": broken_links,
        "built":        date.today().isoformat(),
    }

    json_path = GRAPH_DIR / "graph.json"
    json_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}  ({len(nodes)} nodes, {len(edges)} edges)")

    html_path = GRAPH_DIR / "graph.html"
    html_path.write_text(_render_html(graph), encoding="utf-8")
    print(f"Wrote {html_path}")

    # Append to log
    today = date.today().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{today}] graph | Knowledge graph rebuilt\n")

    if open_after:
        webbrowser.open(html_path.as_uri())


# ---------------------------------------------------------------------------
# HTML renderer — reads graph/template.html and substitutes data blobs
# ---------------------------------------------------------------------------

def _json_for_inline_script(data: object) -> str:
    """Serialize JSON for embedding inside <script>. HTML tokenization runs first:
    ``<!--`` inside a script would start an HTML comment and truncate the script.
    ``</`` can close ``</script>``. Escape both so the graph still loads.
    """
    blob = json.dumps(data)
    blob = blob.replace("</", "<\\/")
    blob = blob.replace("<!--", "\\u003c!--")
    return blob


def _render_html(graph: dict) -> str:
    template_path = GRAPH_DIR / "template.html"
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found: {template_path}\n"
            "Make sure graph/template.html exists (it ships with the repo)."
        )

    nodes_json = _json_for_inline_script(graph["nodes"])
    edges_json = _json_for_inline_script(graph["edges"])
    broken_json = _json_for_inline_script(graph.get("broken_links", []))

    pages_map = {}
    for n in graph["nodes"]:
        pages_map[n["id"]] = {
            "label":        n.get("label", ""),
            "content":      n.get("content", ""),
            "meta":         n.get("meta", {}),
            "tags":         n.get("tags", []),
            "last_updated": n.get("last_updated", ""),
            "wiki_path":    n.get("wiki_path", n["id"]),
            "type":         n.get("type", ""),
        }
    pages_json = _json_for_inline_script(pages_map)

    template = template_path.read_text(encoding="utf-8")
    return (template
        .replace("__NODES__",   nodes_json)
        .replace("__EDGES__",   edges_json)
        .replace("__PAGES__",   pages_json)
        .replace("__BROKEN__",  broken_json)
        .replace("__BUILT__",   graph["built"])
        .replace("__N_NODES__", str(len(graph["nodes"])))
        .replace("__N_EDGES__", str(len(graph["edges"])))
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the wiki knowledge graph.")
    parser.add_argument("--open", action="store_true", help="Open graph.html in browser after build")
    args = parser.parse_args()
    build(open_after=args.open)

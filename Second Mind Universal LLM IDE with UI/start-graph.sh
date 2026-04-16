#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Building knowledge graph..."
uv run tools/build_graph.py

echo "Starting server with write mode on http://127.0.0.1:8765/graph/graph.html"
uv run tools/serve_graph.py --allow-write --port 8765

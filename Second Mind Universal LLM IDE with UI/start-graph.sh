#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
# Kill any process already holding port 8766 so the server always starts fresh
lsof -ti:8766 | xargs kill -9 2>/dev/null || true
echo "Building knowledge graph..."
uv run tools/build_graph.py

echo "Starting server with write mode on http://127.0.0.1:8766/graph/graph.html"
uv run tools/serve_graph.py --allow-write --port 8766

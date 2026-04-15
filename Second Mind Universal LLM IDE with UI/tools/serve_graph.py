#!/usr/bin/env python3
"""Serve the repository root over HTTP so the graph reader pane can load wiki media.

Serves ``REPO_ROOT`` (not only ``graph/``) so image paths like ``../wiki/assets/...``
resolve when viewing ``/graph/graph.html``. Pure stdlib.

Optional ``PUT`` (with ``--allow-write``) persists ``wiki/**/*.md`` for in-browser edit/save.
Optional ``DELETE`` (with ``--allow-write``) soft-deletes wiki pages by moving them to ``deleted/``.

Example:
    python tools/serve_graph.py
    python tools/serve_graph.py --port 9000 --no-open
    python tools/serve_graph.py --allow-write   # enables PUT for wiki .md only (localhost only)
"""

from __future__ import annotations

import argparse
import shutil
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
DELETED_DIR = REPO_ROOT / "deleted"
MAX_PUT_BYTES = 5_000_000


def _safe_wiki_md_target(url_path: str) -> Path | None:
    """Return a resolved path under ``wiki/`` for a PUT target, or None if invalid.

    Args:
        url_path: Request path (e.g. ``/wiki/notes/foo.md``).

    Returns:
        Resolved ``.md`` path inside ``wiki``, or None.
    """
    raw = unquote(url_path.split("?", 1)[0])
    if not raw.startswith("/wiki/"):
        return None
    rel = raw[len("/wiki/") :].lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    target = (WIKI_DIR / rel).resolve()
    wiki_resolved = WIKI_DIR.resolve()
    try:
        target.relative_to(wiki_resolved)
    except ValueError:
        return None
    if target.suffix.lower() != ".md":
        return None
    return target


def main() -> None:
    """Parse CLI args and run a threaded HTTP server rooted at the repo."""
    parser = argparse.ArgumentParser(description="Serve repo root for Wiki Graph + wiki assets.")
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        metavar="N",
        help="TCP port (default: 8765)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open a browser tab",
    )
    parser.add_argument(
        "--allow-write",
        action="store_true",
        help="Allow HTTP PUT/DELETE for wiki/*.md (localhost only; do not expose to untrusted networks)",
    )
    args = parser.parse_args()

    allow_write = args.allow_write

    class _GraphHandler(SimpleHTTPRequestHandler):
        """Serves repo files; optional PUT for wiki markdown."""

        def __init__(self, *a: Any, **kw: Any) -> None:
            super().__init__(*a, directory=str(REPO_ROOT), **kw)

        def do_PUT(self) -> None:  # noqa: N802 — stdlib name
            """Write wiki markdown if ``--allow-write``; otherwise 403."""
            if not allow_write:
                self.send_error(HTTPStatus.FORBIDDEN, "Writes disabled (run with --allow-write)")
                return
            target = _safe_wiki_md_target(self.path)
            if target is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Invalid wiki path")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_error(HTTPStatus.LENGTH_REQUIRED, "Bad Content-Length")
                return
            if length > MAX_PUT_BYTES:
                self.send_error(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    f"Body exceeds {MAX_PUT_BYTES} bytes",
                )
                return
            if length < 0:
                self.send_error(HTTPStatus.BAD_REQUEST, "Bad Content-Length")
                return
            body = self.rfile.read(length)
            try:
                text = body.decode("utf-8")
            except UnicodeDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Body must be UTF-8")
                return
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            except OSError as exc:
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
                return
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

        def do_DELETE(self) -> None:  # noqa: N802 — stdlib name
            """Soft-delete a wiki page by moving it to ``deleted/`` if ``--allow-write``."""
            if not allow_write:
                self.send_error(HTTPStatus.FORBIDDEN, "Writes disabled (run with --allow-write)")
                return
            target = _safe_wiki_md_target(self.path)
            if target is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Invalid wiki path")
                return
            if not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File does not exist")
                return
            wiki_resolved = WIKI_DIR.resolve()
            rel = target.relative_to(wiki_resolved)
            dest = DELETED_DIR / rel
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(dest))
            except OSError as exc:
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
                return
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), _GraphHandler)
    url = f"http://127.0.0.1:{args.port}/graph/graph.html"
    print(f"Serving {REPO_ROOT}\n  {url}")
    if allow_write:
        print(
            "  *** PUT/DELETE enabled for wiki/**/*.md (UTF-8, max "
            f"{MAX_PUT_BYTES} bytes). DELETE moves files to deleted/.\n"
            "  Bind: 127.0.0.1 only — do not expose to untrusted networks. ***"
        )
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

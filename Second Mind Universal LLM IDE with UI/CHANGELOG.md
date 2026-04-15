# Changelog

All notable changes to this Second Mind LLM Wiki workspace are recorded here.

## [Unreleased]

### Added

- **Graph node delete** (`graph/template.html`, `tools/serve_graph.py`): delete button (🗑) in the side-panel header soft-deletes a wiki page — moves the file to `deleted/` (preserving subfolder structure) and removes the node + edges from the live graph. Requires `python tools/serve_graph.py --allow-write`. New `do_DELETE` handler in `serve_graph.py`; `deleted/` added to `.gitignore`.
- **Graph left filter sidebar** (`graph/template.html`): collapsible/resizable left panel with **By Type**, **By Folder**, and **By Tag** filter sections. Sidebar toggles via `☰` toolbar button or `\` key; resizable via drag handle; state persisted in `wg-state-v5`.
- **Graph reset button** (`graph/template.html`): `⟲` toolbar button with confirmation dialog clears all localStorage settings and reloads the page to defaults.

### Changed

- **Graph rotation** (`graph/template.html`): replaced CSS `transform: rotate()` with programmatic node-position rotation so labels always stay horizontal and readable at any angle.
- **Graph fetch error** (`graph/template.html`): improved error messages in the reader pane when wiki files cannot be loaded over HTTP — now provides actionable guidance instead of a generic error.
- **Graph reader images** (`graph/template.html`): fixed image rendering in the reader pane — relative image paths from fetched full files (e.g. `../assets/images/...`) are now resolved against the note's URL before HTML parsing, eliminating 404s that occurred when paths were incorrectly resolved against `graph/graph.html`.
- **Graph toolbar** (`graph/template.html`): filters and color-by moved from top toolbar into the new left panel; toolbar is cleaner with only essential controls. LocalStorage key bumped to `wg-state-v5` (reads `v4`/`v3` for migration).

- **Graph reader pane** (`graph/template.html`): **Preview / Raw / Edit** modes, **Save** (HTTP `PUT` when `python tools/serve_graph.py --allow-write`, else **download** `.md`), **Theme** popover (presets + text/background/code colors), unsaved-change confirm when leaving a note; **`Ctrl/⌘+S`** in the editor. Full note load via `GET` when served over HTTP (preserves frontmatter); `file://` shows embedded body with a banner. LocalStorage key **`wg-state-v4`** (migrates reads from `wg-state-v3`).
- **Graph toolbar**: **Color** dropdown — nodes colored **by type**, **by folder** (first path segment), or **by first tag** (stable hue hash).
- **Graph forces** overlay card: sliders for link length, stiffness, repulsion, center gravity (persisted in `wg-state-v4`).
- **`tools/serve_graph.py`**: optional **`--allow-write`** — accepts **`PUT`** for **`wiki/**/*.md`** only (UTF-8, max 5 MB), path-normalized under `wiki/`; bind remains **`127.0.0.1`** only — do not expose to untrusted networks.

- Wiki ingest: [Stryker SmartHospital Platform](https://www.stryker.com/us/en/portfolios/medical-surgical-equipment/smart-hospital.html) — `raw/clips/stryker-smart-hospital-platform.md`, `wiki/summaries/stryker-smart-hospital-platform.md`, `wiki/concepts/SmartHospitalPlatform.md`, `wiki/assets/images/stryker-smart-hospital/` (20 JPEGs from Stryker CDN), insight stub `stryker-smarthospital-platform-architecture.md`.
- Wiki ingest: [Stryker medical and surgical equipment (US portfolio hub)](https://www.stryker.com/us/en/portfolios/medical-surgical-equipment.html) — `raw/clips/stryker-medical-surgical-equipment.md`, `wiki/summaries/stryker-medical-surgical-equipment.md`, insight stub `stryker-medical-surgical-portfolio.md`.
- **`docs/assets.md`** — `wiki/assets/` layout (`images/`, `diagrams/`, `files/`), markdown path conventions, video embed rules, provenance.
- **`wiki/assets/`** tree with `.gitkeep` placeholders for tracked empty folders.
- **Ingest prompts** (`prompts/general.md`, `blog.md`, `research_paper.md`, `youtube.md`): optional **Figures and diagrams**, required **Sources and media** when media/embeds exist; `wiki/assets/` copy rules; Mermaid and embed-URL guidance. **`prompts/refine.md`**: preserve media and provenance sections.
- **Graph reader pane** (`graph/template.html`): **DOMPurify** + **mermaid** (CDN), `panelHtmlFromMarkdown` pipeline, CSS for `img` / `iframe` / `.mermaid`, iframe allowlist (YouTube/Vimeo embed hosts only).
- Wiki ingest: [Stryker workplace communications](https://www.stryker.com/us/en/services-and-solutions/workplace-communications.html) — `raw/clips/stryker-workplace-communications.md`, `wiki/summaries/stryker-workplace-communications.md`, concept `NonHospitalVoceraVerticals`, entity `Smartbadge`, insight stub `workplace-communications-verticals.md`.

### Fixed

- `graph/template.html`: **`http:` / `https:`** links in the reader pane get **`target="_blank"`** and **`rel="noopener noreferrer"`** via **`configureExternalLinks`** so external sites open in a new tab without leaving the graph.
- `graph/template.html`: after rendering the reading pane, **`resolvePanelImageSrcs`** rewrites relative `../wiki/assets/...` image targets to **absolute** `file:` / `http:` URLs via `new URL(src, graphPageUrl)` so thumbnails load reliably (dynamic `innerHTML` + `file://` often left images blank). DOMPurify **`alt`** / **`loading`** allowed on `img`.
- `graph/template.html`: `mermaid.run({ querySelector: '#pane-content' })` targeted the **panel root**, so Mermaid tried to parse **all rendered note text** as diagram syntax → bomb icon / “Syntax error in text”. Now uses `#pane-content .mermaid` so only fenced ` ```mermaid ` blocks render.
- `graph/template.html`: load **vis-network** (standalone UMD) and **marked** from **HTTPS CDN** instead of same-directory `.min.js` files. Opening `graph.html` via `file://` from Google Drive (and similar) often leaves local scripts empty or unreadable, so `vis` was never defined, `new vis.Network` threw, and **no category filters or graph** were created. Added a red error banner if libraries are still missing; documented offline fallback.
- `tools/serve_graph.py`: stdlib HTTP server for the **repo root** (default port 8765) so `/graph/graph.html` can load `wiki/assets/...`; opens `http://127.0.0.1:PORT/graph/graph.html`.
- `graph/template.html`: graph canvas used `height: 100%` inside flex without a resolved height, so vis.js often got a **0px-tall** container (empty canvas). `#network` now fills `#network-wrap` with `position: absolute; inset: 0`, flex chain uses `min-height: 0`, and `restoreState` calls `network.fit()` when localStorage is missing or the saved view is invalid. LocalStorage key bumped to `wg-state-v3` to drop bad saved cameras; window `resize` triggers `network.redraw()`.
- `tools/build_graph.py`: escape `<!--` when inlining wiki JSON into `graph.html` so HTML does not treat it as a comment inside `<script>` (which broke vis.js and showed raw page text).
- `graph/template.html`: file header comment must not contain `__NODES__`-style tokens (the builder replaces all occurrences, which previously dumped the full graph into the HTML comment).

### Changed

- **Removed** the experimental Wikipedia-style **wiki reader** (`wiki_reader.html`, `wiki_reader_template.html`, `reader_shared.js`), **save API** in `serve_graph.py`, **`content_source`** in `build_graph` nodes, graph **Reader** button and URL-hash deep linking — graph-only workflow restored.

- **`graph/template.html`** (rebuild with `tools/build_graph.py`): label **Aa** toggle, **S/M/L** font scale, **⌖** hover-or-selected-only labels, **⌂** overview (clear selection, exit 2-hop, reset rotation, fit); **`L`** / **`Home`** shortcuts; **`showLabels`**, **`labelFontIdx`**, **`labelsHoverOnly`** persisted in **`wg-state-v3`**; node dot size **`~√degree`** with capped label font; label **background** + **stroke**; **forceAtlas2Based** physics with **`avoidOverlap`** and longer springs; search **jump pulse** on the target node.
- **`tools/build_graph.py`**: rewrites local markdown `![](...)` targets to paths relative to `graph/` so the side panel resolves images under `wiki/` (e.g. `../wiki/assets/...`).
- **`AGENTS.md`**: ingest steps and Key Rules for `wiki/assets/`, media provenance, video embeds; graph workflow mentions image rewrite; directory layout lists `wiki/assets/` and `docs/assets.md`.
- **`README.md`**, **`docs/PIPELINES.md`**: `wiki/assets/`, `serve_graph.py` repo-root URL `/graph/graph.html`, `build_graph` image rewrite.
- **`.cursor/rules/wiki-agent.mdc`**, **`.github/copilot-instructions.md`**, **`.cursor/skills/wiki-ingest/SKILL.md`**: ingest copies media to `wiki/assets/`; video embed URLs only.
- **`docs/WORKFLOW.md`**: monthly step mentions `serve_graph.py` for graph panel media.
- **`AGENTS.md`**: document all agent utilities (`extract`, `dedup`, `build_graph`, `style_lint`); expand `/wiki-lint` slash-command and greeting descriptions; add `style_lint.py` to directory layout; align `extract.py` column spacing; Query workflow step 4 now includes the `Files changed` bullet required by global Output Style.
- `.github/copilot-instructions.md` and `.cursor/rules/wiki-agent.mdc`: `/wiki-lint` greeting row mentions stale summaries and style checks; ingest quick reference includes entities/concepts and index/overview; Copilot insights rule matches stub wording `(status: pending)`; Cursor ingest quick reference matches the same chain.
- `README.md`: fixed double space before `/wiki-ingest` in quick start.
- `tools/style_lint.py`: also scans `.cursor/skills/**/SKILL.md` alongside instructions and slash prompts.

## [0.1.1] - 2026-04-11

### Added

- `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, and `wiki/syntheses/` directories (tracked with `.gitkeep`) so the on-disk tree matches the schema.
- `raw/assets/` for optional local attachments (e.g. Obsidian fixed attachment path).
- `.gitignore` for common local and Python artifacts, secrets, and graph cache.
- `.env.example` and `docs/env.md` documenting optional `ANTHROPIC_API_KEY` for `tools/`.
- Git repository initialized for version history of markdown and config.

### Changed

- `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`: directory layout documents `raw/assets/`; orientation notes (no `README.md`, pointer to `docs/env.md` / `.env.example`).
- `wiki/overview.md`: agent-first ingest instructions, valid `last_updated`, and pointer to `raw/assets/`.

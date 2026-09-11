# GraphTrace AI — M4 Frontend

**Owner: Member 4** · Phase 1 implementation

Vite + React + TypeScript frontend that connects to the M3 FastAPI backend and lets you visually explore the software knowledge graph.

## Quick start

```bash
# 1. Install deps (one-time)
npm install

# 2. Start M3 backend first (from project root)
uvicorn backend.app.main:app --reload --port 8000

# 3. Start M4 frontend
npm run dev
# → http://localhost:5173
```

The dev server proxies `/api/*` → `http://localhost:8000` (configured in `vite.config.ts`).

## Pages

| Route | Description |
|---|---|
| `/` | Project list. Upload ZIP or import JSON graph. |
| `/projects/:id` | Dashboard — node counts, type breakdown, quick actions. |
| `/projects/:id/graph` | **Interactive graph explorer** — force layout, node coloring, click to explore, search + type filter. |

## Architecture

```
src/
├── api.ts              ← typed fetch wrappers for all M3 endpoints
├── nodeColors.ts       ← node type → colour/size constants
├── index.css           ← dark-mode design system (CSS variables)
├── App.tsx             ← router
├── main.tsx            ← entry point
├── pages/
│   ├── Home.tsx        ← project list + upload modal
│   ├── Dashboard.tsx   ← project stats
│   └── GraphExplorer.tsx ← force graph + detail panel
└── components/
    ├── AppShell.tsx    ← topbar layout
    ├── UploadModal.tsx ← ZIP/JSON import
    └── NodeCard.tsx    ← selected node details + neighbours
```

## M3 API endpoints used

- `GET  /projects` — list all projects
- `POST /projects/analyze` — upload ZIP (calls M1 pipeline)
- `POST /projects/import` — import ArtifactGraph JSON
- `GET  /projects/:id` — project summary/stats
- `GET  /projects/:id/graph` — full graph for visualization
- `GET  /projects/:id/dependencies/:nodeId` — dependency traversal
- `GET  /projects/:id/requirements` — requirement nodes
- `GET  /projects/:id/traceability/:reqId` — traceability path

## Build

```bash
npm run build   # outputs to dist/
npm run preview # preview production build
```

"""
╔══════════════════════════════════════════════════════════════════╗
║  M4 — Frontend & Visualization                                   ║
║  Owner: Member 4                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  This folder is the complete M4 frontend for GraphTrace AI.      ║
║  It is a standalone Vite + React + TypeScript application.       ║
║                                                                  ║
║  Tech stack:                                                      ║
║    Vite 8 + React 19 + TypeScript                                ║
║    react-force-graph-2d  — interactive graph canvas              ║
║    react-router-dom      — client-side routing                   ║
║    Vanilla CSS dark-mode design system (src/index.css)           ║
║                                                                  ║
║  Key source files:                                                ║
║    src/api.ts             — typed M3 API client (all endpoints)  ║
║    src/nodeColors.ts      — node type → colour/size mapping      ║
║    src/pages/Home.tsx     — project list + upload modal          ║
║    src/pages/Dashboard.tsx — project stats + node type chart     ║
║    src/pages/GraphExplorer.tsx — interactive force graph         ║
║    src/components/NodeCard.tsx — node detail + neighbours panel  ║
║    src/components/UploadModal.tsx — ZIP upload / JSON import     ║
║                                                                  ║
║  API proxy:                                                       ║
║    /api/* → http://localhost:8000 (M3 FastAPI backend)           ║
║    Configured in vite.config.ts                                   ║
║                                                                  ║
║  Phase 1 scope:                                                   ║
║    ✅ Project list & upload                                       ║
║    ✅ Dashboard (stats, node type breakdown)                      ║
║    ✅ Interactive graph (force layout, node colours, filtering)   ║
╚══════════════════════════════════════════════════════════════════╝
"""
# This file exists so Python tools recognise frontend/ in the project tree.
# The actual frontend is JavaScript/TypeScript — run it with npm.

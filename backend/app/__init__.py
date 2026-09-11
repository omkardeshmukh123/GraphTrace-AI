"""
╔══════════════════════════════════════════════════════════════════╗
║  M3 — FastAPI Backend                                            ║
║  Owner: Member 3                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Responsibility:                                                  ║
║    Production FastAPI server: input validation, upload lifecycle, ║
║    REST API, graph reads, dependency/path/traceability queries.   ║
║                                                                   ║
║  Key files:                                                       ║
║    main.py          — App factory (CORS, error handlers, lifespan)║
║    config.py        — Settings via GRAPHTRACE_* env vars          ║
║    models.py        — ArtifactGraph contract (shared by ALL devs) ║
║    analysis.py      — Upload → parse → store pipeline             ║
║    uploads.py       — Hardened ZIP extraction                     ║
║    plugins.py       — Plugin loader (parser + graph_writer)       ║
║    errors.py        — AppError exception class                    ║
║    api/routes.py    — All REST endpoints (9 endpoints)            ║
║    graph/store.py   — LocalGraphStore + Neo4jGraphStore           ║
║    graph/queries.py — BFS traversals (deps, paths, traceability)  ║
║                                                                   ║
║  Integration stubs (implemented by M1/M2):                       ║
║    graph/builder.py   ← M2 implements the Neo4j writer plugin     ║
║    parsers/pipeline.py← M1 implements the parser plugin           ║
║                                                                   ║
║  Run:                                                             ║
║    uvicorn backend.app.main:app --reload --port 8000              ║
╚══════════════════════════════════════════════════════════════════╝
"""

# GraphTrace AI — Backend Module Ownership

This document shows who owns which folder and what each member is responsible for.

---

## 📁 Folder → Owner Mapping

```
backend/
│
├── artifact_intelligence/      ← ✅ M1 (Member 1) — Artifact Intelligence
│   ├── analyzer.py             ← M1: Orchestrator
│   ├── zip_handler.py          ← M1: ZIP extraction & file scanning
│   ├── code_parser.py          ← M1: Python/JS/TS class & function extraction
│   ├── readme_parser.py        ← M1: README metadata extraction
│   └── models.py               ← M1: Internal Entity, Relationship, ArtifactData
│
├── knowledge_graph/            ← ✅ M2 (Member 2) — Knowledge Graph Engine
│   ├── connection.py           ← M2: Neo4j driver singleton
│   ├── schema.py               ← M2: Constraints & index setup
│   ├── builder.py              ← M2: Writes ArtifactData → Neo4j
│   ├── queries.py              ← M2: GraphQueryEngine (reads from Neo4j)
│   ├── resolver.py             ← M2: Entity deduplication (MERGE-based)
│   └── models.py               ← M2: Internal graph node/edge types
│
├── app/                        ← ✅ M3 (Member 3) — FastAPI Backend
│   ├── main.py                 ← M3: App factory, CORS, error handlers
│   ├── config.py               ← M3: Settings (GRAPHTRACE_* env vars)
│   ├── models.py               ← M3: ArtifactGraph contract ⬅ SHARED CONTRACT
│   ├── analysis.py             ← M3: Upload → parse → store pipeline
│   ├── uploads.py              ← M3: Hardened ZIP extraction
│   ├── plugins.py              ← M3: Plugin loader (parser + graph_writer)
│   ├── errors.py               ← M3: AppError
│   ├── api/routes.py           ← M3: 9 REST endpoints
│   ├── graph/store.py          ← M3: LocalGraphStore + Neo4jGraphStore
│   ├── graph/queries.py        ← M3: BFS dependency/path/traceability traversals
│   │
│   ├── parsers/pipeline.py     ← ✅ M1 implements this (M1→M3 bridge)
│   └── graph/builder.py        ← ✅ M2 implements this (M2→M3 bridge)
│
├── shared/                     ← ✅ Common (used by all members)
│   └── contract.py             ← Re-exports ArtifactGraph from app/models.py
│
├── api/                        ← ✅ M1+M2 Standalone API (pre-M3 work)
│   ├── projects.py             ← M1+M2: Upload + analyze endpoints
│   └── graph.py                ← M1+M2: Graph query endpoints for M4
│
├── config.py                   ← M1+M2 Standalone config (NEO4J_URI etc.)
├── main.py                     ← M1+M2 Standalone server (port 8001)
│
└── tests/
    ├── test_m1_parsers.py      ← M1 unit tests (25 tests)
    ├── test_m2_graph.py        ← M2 Neo4j tests (needs .env)
    ├── test_parser_plugin.py   ← M1→M3 integration tests (20 tests)
    ├── test_api.py             ← M3 API tests
    └── test_neo4j_adapter.py   ← M3 Neo4j adapter tests
```

---

## 🔗 How the Members Connect

```
                  Upload project.zip + SRS.md
                          ↓
              M3: POST /projects/analyze
              (backend/app/api/routes.py)
                          ↓
              M3: analyze() pipeline
              (backend/app/analysis.py)
                          ↓
              M1 plugin: parse_project()         ← M1's bridge
              (backend/app/parsers/pipeline.py)
                          ↓ uses
              M1 core: ArtifactAnalyzer          ← M1's module
              (backend/artifact_intelligence/)
                          ↓ produces
              ArtifactGraph (shared contract)    ← M3 defined, all use
              (backend/app/models.py)
                          ↓
              M2 plugin: write_graph()           ← M2's bridge
              (backend/app/graph/builder.py)
                          ↓ uses
              M2 core: Neo4j connection          ← M2's module
              (backend/knowledge_graph/)
                          ↓
              Neo4j AuraDB
                          ↓ queried by
              M3: graph queries                  ← M3's module
              (backend/app/graph/queries.py)
                          ↓
              REST API → M4 Frontend
```

---

## 🚀 Running Each Member's Server

| Member | Command | Port | Purpose |
|--------|---------|------|---------|
| M1+M2 standalone | `uvicorn backend.main:app --reload --port 8001` | 8001 | Test M1/M2 work independently |
| M3 full backend | `uvicorn backend.app.main:app --reload --port 8000` | 8000 | Primary production server |

Both read from `backend/.env`.

---

## 📝 Notes for Each Member

- **M1**: Your core work is in `artifact_intelligence/`. Your M3 bridge is at `app/parsers/pipeline.py`.
- **M2**: Your core work is in `knowledge_graph/`. Your M3 bridge is at `app/graph/builder.py`.
- **M3**: Your core work is in `app/`. Your `app/models.py` is the shared contract everyone imports.
- **M4**: You'll call M3's REST API. See the endpoint table in the main README.
- **shared/**: Import `ArtifactGraph` from here if you need it outside of `app/`.

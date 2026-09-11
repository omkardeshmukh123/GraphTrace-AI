# GraphTrace AI

> An Explainable Software Engineering Intelligence Platform based on a Software Knowledge Graph.

---

## Project Structure

```
graphtrace-ai/
├── backend/                            ← All Python backend code
│   ├── artifact_intelligence/          ← M1: Parse raw artifacts → ArtifactGraph JSON
│   │   ├── models.py                   ← Internal Entity/Relationship/ArtifactData models
│   │   ├── zip_handler.py              ← ZIP extraction & file scanning
│   │   ├── readme_parser.py            ← README.md parsing
│   │   ├── code_parser.py              ← Python/JS/TS class+function extraction
│   │   └── analyzer.py                 ← M1 orchestrator
│   │
│   ├── knowledge_graph/                ← M2: Neo4j standalone adapter (local dev)
│   │   ├── connection.py               ← Driver singleton
│   │   ├── schema.py                   ← Constraints & indexes
│   │   ├── builder.py                  ← Standalone write API
│   │   └── queries.py                  ← Standalone query API
│   │
│   ├── app/                            ← M3: FastAPI Backend (primary server)
│   │   ├── main.py                     ← App factory (CORS, error handlers, lifespan)
│   │   ├── config.py                   ← Settings via GRAPHTRACE_* env vars
│   │   ├── models.py                   ← Shared ArtifactGraph contract (M1↔M2↔M3)
│   │   ├── analysis.py                 ← Analysis pipeline orchestrator
│   │   ├── uploads.py                  ← Secure ZIP extraction
│   │   ├── plugins.py                  ← Plugin loader (parser + graph_writer)
│   │   ├── errors.py                   ← AppError class
│   │   ├── api/routes.py               ← All REST endpoints
│   │   ├── graph/
│   │   │   ├── store.py                ← LocalGraphStore + Neo4jGraphStore
│   │   │   ├── queries.py              ← Graph traversals (BFS, paths, traceability)
│   │   │   └── builder.py             ← [M2] Neo4j writer plugin (our implementation)
│   │   └── parsers/
│   │       └── pipeline.py             ← [M1] Parser plugin (our implementation)
│   │
│   ├── tests/
│   │   ├── test_m1_parsers.py          ← 25 M1 unit tests (no Neo4j)
│   │   ├── test_parser_plugin.py       ← 20 M1→M3 integration tests (no Neo4j)
│   │   ├── test_m2_graph.py            ← M2 Neo4j integration tests (needs .env)
│   │   ├── test_api.py                 ← M3 API tests (from Member 3)
│   │   └── test_neo4j_adapter.py       ← M3 Neo4j adapter tests
│   │
│   ├── requirements.txt                ← Unified dependencies (M1+M2+M3)
│   └── .env.example                    ← Copy to .env and fill credentials
│
├── docs/
│   ├── INTEGRATION.md                  ← M1/M2/M3 interface contracts
│   ├── dev_diary.md                    ← Phase 1 development diary
│   ├── GT_Modules.md                   ← Module & phase breakdown
│   └── GraphTrace AI — Complete Project Master Specification.md
│
├── sample_project/                     ← Test repository (e-commerce app)
├── sample_data/                        ← Demo graph JSON + sample SRS
├── shared/artifact_schema.json         ← JSON Schema for ArtifactGraph
├── scripts/                            ← Utility scripts
└── pytest.ini
```

---

## Architecture: How M1, M2, M3 Connect

```
Upload project.zip + optional SRS.md + mappings.json
              ↓ POST /projects/analyze
M3 FastAPI (backend/app/main.py)
              ↓ calls plugin
M1 Parser Plugin (backend/app/parsers/pipeline.py)
              ↓ uses
M1 ArtifactAnalyzer (backend/artifact_intelligence/)
              ↓ produces
ArtifactGraph (backend/app/models.py)  ← shared contract
              ↓
M2 Graph Writer Plugin (backend/app/graph/builder.py)
              ↓ writes to
Neo4j AuraDB
              ↓ queried by
M3 GraphQueryEngine (backend/app/graph/queries.py)
              ↓ served via
REST API → M4 Frontend (Phase 1+)
```

**Key integration points:**
- `backend/app/models.py` → single source of truth for the `ArtifactGraph` contract
- `backend/app/parsers/pipeline.py` → M1 implements M3's parser plugin interface
- `backend/app/graph/builder.py` → M2 implements M3's Neo4j writer plugin interface
- `docs/INTEGRATION.md` → detailed interface contract and checklist

---

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env and fill in NEO4J credentials from console.neo4j.io
```

### 3. Start the Server (M3 — Primary)

```bash
# From project root:
uvicorn backend.app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive API.

---

## Running Tests

```bash
# From project root:

# M1 unit tests (no Neo4j required)
.\backend\venv\Scripts\python -m pytest backend/tests/test_m1_parsers.py -v

# M1→M3 integration tests (no Neo4j required)
.\backend\venv\Scripts\python -m pytest backend/tests/test_parser_plugin.py -v

# All tests without Neo4j
.\backend\venv\Scripts\python -m pytest backend/tests/test_m1_parsers.py backend/tests/test_parser_plugin.py -v

# All tests (needs Neo4j .env for M2/M3 tests)
.\backend\venv\Scripts\python -m pytest -v
```

**Current status: 45/45 tests passing ✅** (M1 unit + M1→M3 integration)

---

## API Endpoints (M3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/health/ready` | Neo4j connectivity check |
| `GET` | `/projects` | List all analyzed projects |
| `POST` | `/projects/analyze` | Upload ZIP + analyze (requires parser plugin) |
| `POST` | `/projects/import` | Import pre-built ArtifactGraph JSON |
| `GET` | `/projects/{id}` | Project summary |
| `GET` | `/projects/{id}/graph` | Full graph (filterable by type/search) |
| `GET` | `/projects/{id}/dependencies/{node_id}` | Upstream/downstream deps |
| `GET` | `/projects/{id}/paths` | Shortest path between two nodes |
| `GET` | `/projects/{id}/requirements` | All requirements + mapping status |
| `GET` | `/projects/{id}/traceability/{req_id}` | Requirement → code trace |

---

## Development Team

| Member | Layer | Responsibility |
|--------|-------|---------------|
| **M1** | Artifact Intelligence | `backend/artifact_intelligence/` + `backend/app/parsers/pipeline.py` |
| **M2** | Knowledge Graph Engine | `backend/knowledge_graph/` + `backend/app/graph/builder.py` |
| **M3** | FastAPI Backend | `backend/app/` (main, routes, queries, store, models) |
| **M4** | Frontend & Visualization | React dashboard (Phase 1+) |

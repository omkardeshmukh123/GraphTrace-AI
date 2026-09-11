# GraphTrace AI

> An Explainable Software Engineering Intelligence Platform based on a Software Knowledge Graph.

---

## Project Structure

```
graphtrace-ai/
├── backend/
│   ├── artifact_intelligence/          ← M1: Parse artifacts → ArtifactGraph
│   │   ├── models.py                   ← Internal Entity/Relationship models
│   │   ├── zip_handler.py              ← File scanning & inventory
│   │   ├── readme_parser.py            ← README.md extraction
│   │   ├── code_parser.py              ← Python/JS/TS class+function extraction
│   │   └── analyzer.py                 ← M1 orchestrator
│   │
│   ├── app/                            ← M3: Primary FastAPI server
│   │   ├── main.py                     ← App factory (CORS, error handling, lifespan)
│   │   ├── config.py                   ← Settings via GRAPHTRACE_* env vars
│   │   ├── models.py                   ← ArtifactGraph contract (shared by all modules)
│   │   ├── analysis.py                 ← Upload → parse → store pipeline
│   │   ├── uploads.py                  ← Secure ZIP extraction
│   │   ├── plugins.py                  ← Plugin loader (parser + graph_writer)
│   │   ├── errors.py                   ← AppError class
│   │   ├── api/routes.py               ← All REST endpoints
│   │   ├── graph/
│   │   │   ├── store.py                ← LocalGraphStore + Neo4jGraphStore
│   │   │   ├── queries.py              ← BFS traversals (deps, paths, traceability)
│   │   │   └── builder.py             ← [M2] Neo4j writer plugin
│   │   └── parsers/
│   │       └── pipeline.py             ← [M1] Parser plugin (M1 → M3 bridge)
│   │
│   ├── tests/
│   │   ├── test_m1_parsers.py          ← 25 M1 unit tests
│   │   ├── test_parser_plugin.py       ← 20 M1→M3 integration tests
│   │   ├── test_m2_graph.py            ← M2 Neo4j tests (needs .env)
│   │   ├── test_api.py                 ← M3 API tests
│   │   └── test_neo4j_adapter.py       ← M3 Neo4j adapter tests
│   │
│   ├── requirements.txt                ← Unified deps (M1+M2+M3)
│   └── .env.example                    ← Copy to .env and fill in credentials
│
├── docs/
│   ├── INTEGRATION.md                  ← M1/M2/M3 interface contracts & checklist
│   ├── dev_diary.md                    ← Phase 1 development diary
│   ├── GT_Modules.md                   ← Module & phase breakdown
│   └── GraphTrace AI — Complete Project Master Specification.md
│
├── sample_project/                     ← Test repo: e-commerce app (Python + JS)
│   ├── src/
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   └── user_repository.py
│   ├── frontend/
│   │   └── payment_service.js
│   └── README.md
│
├── scripts/
│   ├── make_demo.py                    ← Generates .data/demo_graph.json + sample_project.zip
│   └── generate_contract.py            ← Generates shared/artifact_schema.json
│
├── shared/
│   └── artifact_schema.json            ← JSON Schema for ArtifactGraph (auto-generated)
│
├── .gitignore
├── pytest.ini
└── README.md
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

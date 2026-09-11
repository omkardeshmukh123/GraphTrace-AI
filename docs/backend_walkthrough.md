# Walkthrough — Backend (Members 1, 2 & 3) Implementation

## Overview
The GraphTrace AI backend is the intelligence and persistence engine of the platform. It is structured into three modular components corresponding to Member responsibilities, unified by a shared Pydantic data contract:

- **Member 1 (Artifact Intelligence)**: Extracts structured software entities (files, classes, functions, modules, requirements) and their relationships from raw source code and documentation.
- **Member 2 (Knowledge Graph Engine)**: Persists entities and relationships into Neo4j with idempotent graph mutations and provides Cypher query capabilities.
- **Member 3 (FastAPI Core & Orchestration)**: Exposes a secured, hardened REST API, coordinates the upload-to-analysis pipeline, implements graph traversal algorithms (BFS, shortest path, traceability), and provides fallback in-memory storage alongside Neo4j.

---

## Architecture & File Structure

```
backend/
├── artifact_intelligence/      # ── Member 1: Artifact Intelligence Core ──
│   ├── analyzer.py             # Pipeline orchestrator (Zip + Readme + Code parsers)
│   ├── zip_handler.py          # Archive extraction, filesystem scanning & language metrics
│   ├── code_parser.py          # Python AST + JS/TS regex/structural parser
│   ├── readme_parser.py        # Markdown documentation & metadata extractor
│   └── models.py               # M1 internal domain models (Entity, Relationship, ArtifactData)
│
├── knowledge_graph/            # ── Member 2: Knowledge Graph Engine Core ──
│   ├── connection.py           # Neo4j driver singleton & connection lifecycle
│   ├── schema.py               # Constraint setup, uniqueness rules & index creation
│   ├── builder.py              # Cypher builder writing ArtifactData -> Neo4j via MERGE
│   ├── queries.py              # GraphQueryEngine (project tree, node inspection, stats)
│   ├── resolver.py             # Entity deduplication & cross-file resolution
│   └── models.py               # M2 internal node/edge schema definitions
│
├── app/                        # ── Member 3: FastAPI Backend & Integrations ──
│   ├── main.py                 # FastAPI application factory, CORS, exception handlers
│   ├── config.py               # Pydantic Settings (GRAPHTRACE_* environment variables)
│   ├── models.py               # ArtifactGraph contract ⬅ SHARED CANONICAL CONTRACT
│   ├── analysis.py             # Ingestion workflow: upload -> extract -> parse -> store
│   ├── uploads.py              # Security-hardened archive validation & extraction
│   ├── plugins.py              # Dynamic plugin loader (M1 parser & M2 graph writer)
│   ├── errors.py               # Centralized exception hierarchy (AppError, NotFoundError, etc.)
│   ├── api/
│   │   └── routes.py           # 11 REST API endpoints
│   ├── parsers/
│   │   └── pipeline.py         # M1 -> M3 Bridge: translates M1 output to ArtifactGraph
│   └── graph/
│       ├── builder.py          # M2 -> M3 Bridge: translates ArtifactGraph to Neo4j writer
│       ├── store.py            # LocalGraphStore (in-memory/JSON) & Neo4jGraphStore
│       └── queries.py          # Traversal algorithms: BFS dependencies, shortest path, traceability
│
├── shared/
│   └── contract.py             # Shared contract re-export for cross-module usage
│
└── tests/
    ├── test_m1_parsers.py      # M1 unit tests (25 tests)
    ├── test_parser_plugin.py   # M1 -> M3 integration & validation tests (20 tests)
    ├── test_api.py             # M3 REST API, security & hardening tests (20 tests)
    ├── test_neo4j_adapter.py   # M3 Neo4j adapter & contract tests (3 tests)
    └── test_m2_graph.py        # M2 Neo4j live integration tests (12 tests)
```

---

## Member Responsibilities & Key Modules

### Member 1: Artifact Intelligence ([`artifact_intelligence/`](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/artifact_intelligence))
- **[zip_handler.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/artifact_intelligence/zip_handler.py)**: Safely inspects and extracts project archives; recursively scans directories while filtering cache/dist folders (`__pycache__`, `node_modules`, `.git`); calculates language distribution statistics.
- **[code_parser.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/artifact_intelligence/code_parser.py)**: Parses source files into AST representations. For Python, utilizes `ast` to detect classes, top-level functions, methods, line ranges, and docstrings. For JavaScript/TypeScript, uses structural token patterns to discover classes and exported functions. Emits `CONTAINS`, `DEFINES`, and `CALLS` relations.
- **[readme_parser.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/artifact_intelligence/readme_parser.py)**: Extracts title, description, architecture notes, and technology tags from Markdown documentation, producing `DOCUMENT` nodes and `HAS_README` edges.
- **[analyzer.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/artifact_intelligence/analyzer.py)**: Coordinates the parsers and produces an aggregated `ArtifactData` container.
- **M1&rarr;M3 Bridge ([app/parsers/pipeline.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/parsers/pipeline.py))**: Implements `parse_project()` conforming to M3's plugin interface. Converts M1 internal entities into the canonical `ArtifactGraph`, mapping requirements files (SRS/Markdown/JSON) to `REQUIREMENT` nodes linked via `CONTAINS`.

### Member 2: Knowledge Graph Engine ([`knowledge_graph/`](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/knowledge_graph))
- **[connection.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/knowledge_graph/connection.py)**: Manages Neo4j Bolt driver sessions with automatic reconnection, connection pooling, and credential configuration for Neo4j AuraDB.
- **[schema.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/knowledge_graph/schema.py)**: Applies Cypher constraints (`CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE`) and indexes on `project_id`, `name`, and labels.
- **[builder.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/knowledge_graph/builder.py)**: Persists graph data using parameterized Cypher `MERGE` statements for idempotent insertion, preventing duplicate nodes and relationships across repeated runs.
- **[queries.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/knowledge_graph/queries.py)**: Powers the `GraphQueryEngine` to retrieve project hierarchies, node details, degree metrics, and neighbor subgraphs.
- **M2&rarr;M3 Bridge ([app/graph/builder.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/graph/builder.py))**: Implements `write_graph()` to accept M3's `ArtifactGraph` and stream entities directly into Neo4j.

### Member 3: FastAPI Backend & Platform ([`app/`](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app))
- **[models.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/models.py)**: The canonical Pydantic model contract (`ArtifactGraph`, `Node`, `Relationship`, `NodeType`, `RelationshipType`, `ProjectSummary`, `GraphView`, `DependencyView`, `PathView`, `TraceabilityView`).
- **[uploads.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/uploads.py)**: Multi-layer security validation against Zip Slip vulnerabilities, absolute paths, traversal sequences (`../`), forbidden Windows device names (`CON`, `PRN`, `AUX`), unpack ratio limits, and total size constraints.
- **[analysis.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/analysis.py)**: Orchestrates the synchronous project analysis pipeline: archive reception &rarr; quarantine extraction &rarr; M1 parser execution &rarr; `ArtifactGraph` validation &rarr; persistence &rarr; temporary directory cleanup.
- **[graph/store.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/graph/store.py)**: Provides dual-store abstraction:
  - `LocalGraphStore`: In-memory storage with optional JSON persistence for lightweight local development and automated CI.
  - `Neo4jGraphStore`: Production-grade storage communicating with Neo4j.
- **[graph/queries.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/graph/queries.py)**: Implements fast in-memory graph algorithms:
  - Subgraph filtering by node types, relationship types, and search queries.
  - Upstream and downstream dependency tree extraction (BFS with depth control).
  - Shortest path discovery between any two nodes.
  - Full requirements-to-code traceability chains.

---

## Shared Data Contract (`ArtifactGraph`)

All modules interoperate via the shared model defined in [app/models.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/models.py):

```python
class Node(BaseModel):
    id: str
    name: str
    type: NodeType  # PROJECT, FILE, PACKAGE, CLASS, FUNCTION, METHOD, REQUIREMENT, DOCUMENT
    properties: dict[str, Any] = Field(default_factory=dict)

class Relationship(BaseModel):
    source: str
    target: str
    type: RelationshipType  # CONTAINS, DEFINES, CALLS, IMPORTS, IMPLEMENTS, DEPENDS_ON, HAS_README
    properties: dict[str, Any] = Field(default_factory=dict)

class ArtifactGraph(BaseModel):
    project_id: str
    nodes: list[Node]
    relationships: list[Relationship]
    metadata: dict[str, Any] = Field(default_factory=dict)
```

---

## REST API Endpoints ([app/api/routes.py](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/api/routes.py))

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check, active store type (`local` / `neo4j`), parser status |
| `GET` | `/health/ready` | Readiness check verifying store connectivity (`store.ping()`) |
| `GET` | `/projects` | List all analyzed projects with summary statistics |
| `POST` | `/projects/analyze` | Multipart upload of ZIP archive + optional requirements + mapping |
| `POST` | `/projects/import` | Import pre-parsed `ArtifactGraph` JSON directly |
| `GET` | `/projects/{project_id}` | Retrieve single project metadata and metrics |
| `GET` | `/projects/{project_id}/graph` | Retrieve filtered subgraph (by node type, relation, search) |
| `GET` | `/projects/{project_id}/dependencies/{node_id}` | Upstream / downstream dependency tree |
| `GET` | `/projects/{project_id}/paths` | Shortest path between source and target nodes |
| `GET` | `/projects/{project_id}/requirements` | List requirements associated with a project |
| `GET` | `/projects/{project_id}/traceability/{req_id}` | Full requirement &rarr; implementation traceability tree |

---

## Verification & Test Results

The backend is backed by an automated test suite run via `pytest`:

```bash
backend\venv\Scripts\python.exe -m pytest backend/tests -v
```

### Test Breakdown:
- **`test_m1_parsers.py` (25 tests)**: Verifies `ZipHandler`, `ReadmeParser`, `CodeParser`, language distribution extraction, AST method discovery, and deduplication.
- **`test_parser_plugin.py` (20 tests)**: Validates M1&rarr;M3 bridge, project-level metadata attachment, requirement node extraction, and Pydantic contract compliance.
- **`test_api.py` (20 tests)**: Verifies REST endpoints, upload workflows, Zip Slip protection, forbidden Windows filenames, symlink safety, and CORS configuration.
- **`test_neo4j_adapter.py` (3 tests)**: Verifies read/write adapter contracts and scope guarantees.
- **`test_m2_graph.py` (12 tests)**: Validates Neo4j schema creation, Cypher insertion, and query engine against live database instances.

### Execution Summary:
```
================= 81 passed, 12 skipped, 1 warning in 11.27s =================
```
*(12 live Neo4j tests are skipped automatically when Neo4j is offline, maintaining 100% test suite pass rate).*

---

## Running the Backend

### Local Mode (In-Memory / Zero Neo4j dependency)
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Neo4j Mode (Production / AuraDB)
1. Configure credentials in `backend/.env`:
   ```env
   GRAPHTRACE_STORE=neo4j
   NEO4J_URI=neo4j+s://<your-aura-instance>.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=<your-password>
   ```
2. Start the server:
   ```bash
   venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```

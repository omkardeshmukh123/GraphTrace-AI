# 📓 GraphTrace AI — Phase 1 Development Diary

> **Phase**: Phase 1 — Basic Software Understanding  
> **Members**: M1 (Artifact Intelligence) + M2 (Knowledge Graph Engine)  
> **Phase Gate**: *"Can we upload a project and visually explore its software structure?"*  
> **Started**: 2026-09-10

---

## Session 2 — 2026-09-11

### Goals
- Push M1+M2 work to a safe branch before pulling M3
- Pull Member 3's work from `origin/main` and integrate locally
- Achieve 45/45 tests passing before any git merge

### Work Done

#### 1. Branch Safety
- Created `feature/m1-m2-phase1` branch with all M1+M2 work committed and pushed
- Pulled M3's `main` branch (36 new files, 2062 insertions)

#### 2. M3 Code Analysis
Member 3 built a production-grade FastAPI backend in `backend/app/`:
- `main.py` — App factory with request size limits, structured error handlers, CORS
- `models.py` — Shared `ArtifactGraph` contract (Node, Relationship, with uuid5 IDs)
- `api/routes.py` — 9 REST endpoints covering projects, graph, deps, paths, traceability
- `graph/store.py` — `LocalGraphStore` (file-based) + `Neo4jGraphStore` (cloud)
- `graph/queries.py` — Pure-Python BFS graph traversals
- `analysis.py` — Orchestrator calling parser plugin + mapping application
- `uploads.py` — Hardened ZIP extraction (path traversal, reserved names, size limits)
- `plugins.py` — Dynamic plugin loader (parser + writer as env-configured callables)
- `docs/INTEGRATION.md` — Detailed M1/M2/M3 interface contract

**Key insight**: M3 left `backend/app/parsers/pipeline.py` and `backend/app/graph/builder.py` as stubs for us to implement.

#### 3. M1 → M3 Parser Plugin (`backend/app/parsers/pipeline.py`)
- Implements M3's parser plugin interface: `parse_project(*, project_id, repository_root, requirements_text) → ArtifactGraph`
- Converts M1's `Entity/Relationship` → M3's `Node/Relationship` (uuid5 IDs, `PROJECT` type)
- Maps entity types: REPOSITORY→PROJECT, FOLDER→PACKAGE, FILE→FILE, CLASS→CLASS, etc.
- Maps relationship types: CONTAINS, DOCUMENTED_BY
- Adds `reference` property to FUNCTION/CLASS nodes for manual mapping support
- Parses REQUIREMENT nodes from Markdown SRS (handles `## REQ-001:`, `**REQ-002**:` formats)

#### 4. M2 → M3 Neo4j Writer (`backend/app/graph/builder.py`)
- Implements M3's writer plugin interface: `write_graph(*, graph, driver, database) → None`
- Creates `Entity` label + optional extra labels (Class, Function, File, etc.)
- Stores `properties_json` as JSON string per M3's read contract
- Atomic transaction: PROJECT node first → batch UNWIND for remaining nodes → batch UNWIND for rels
- Detects duplicate projects → raises `AppError(409)` before any write
- Whitelists 10 relationship types to prevent Cypher injection
- Uses `_ensure_schema()` to create uniqueness constraint idempotently

#### 5. Infrastructure
- `pytest.ini`: Added `pythonpath = . backend` so both `backend.*` and top-level packages resolve
- `backend/requirements.txt`: Unified M1+M2+M3 deps (fastapi, pydantic, neo4j, httpx)
- `backend/.env.example`: Combined config for both M2 standalone and M3 full server
- `README.md`: Full architecture diagram, setup guide, API table, team breakdown
- Cherry-picked M1/M2 files from feature branch onto main

### Test Results
```
M1 unit tests (test_m1_parsers.py):    25/25 PASSED
M1→M3 integration (test_parser_plugin.py): 20/20 PASSED
Total:                                  45/45 PASSED ✅
```

### Git State
- `feature/m1-m2-phase1`: M1+M2 standalone (backup)
- `main`: Fully integrated M1+M2+M3, pushed to GitHub

### Next Session
- M4: Frontend React app (dependency graph visualization)
- Enable Neo4j end-to-end once credentials are set up
- Run M3's own test suite (`test_api.py`, `test_neo4j_adapter.py`)

---

## Session 1 — 2026-09-10

### Environment Check
- Python 3.11.9 ✅
- pip 26.0.1 ✅
- Node v24.19.0 ✅
- Docker ❌ — **Decision**: Use Neo4j AuraDB Free (cloud) instead

### Decision Log
| # | Decision | Reason |
|---|----------|--------|
| D1 | Neo4j AuraDB Free over local Neo4j Desktop | Docker unavailable; AuraDB needs only a .env URI — zero install |
| D2 | Phase 1 parsing is regex-based, not Tree-sitter | Tree-sitter is Phase 2 scope; regex is sufficient to get files/classes/functions into the graph |
| D3 | FastAPI from day 1 | M3 and M4 will depend on the REST layer; avoid rework |
| D4 | Python + JavaScript as Phase 1 languages | Most common; cover both OOP (classes) and functional (functions) patterns |
| D5 | Pydantic models as M1→M2 contract | Clean interface boundary; M2 doesn't need to know how M1 parsed |
| D6 | MERGE (not CREATE) for Neo4j writes | Prevents duplicate nodes on repeated analysis runs |

---

## Build Log

### 📁 Step 1 — Project Scaffolding
_Status_: ✅ Done

**Files created:**
- `.gitignore` — skips uploads/, extracted/, venv/, .env, __pycache__
- `backend/requirements.txt` — fastapi, uvicorn, neo4j, pydantic, pytest, httpx
- `backend/.env.example` — template for NEO4J_URI / USER / PASSWORD
- `backend/config.py` — Pydantic-settings singleton (`settings` object)
- `README.md` — full setup + API reference

**Note**: Virtual environment created at `backend/venv/`

---

### 🧠 Step 2 — M1 Artifact Intelligence
_Status_: ✅ Done

**Files created:**

| File | Purpose |
|------|---------|
| `artifact_intelligence/__init__.py` | Package init, exports public interface |
| `artifact_intelligence/models.py` | **M1→M2 contract**: Entity, Relationship, ArtifactData + type constants |
| `artifact_intelligence/zip_handler.py` | ZIP extraction + recursive file scan + artifact classification |
| `artifact_intelligence/readme_parser.py` | Extracts title, description, sections, tech keywords from README.md |
| `artifact_intelligence/code_parser.py` | Regex-based Python/JS/TS parser: extracts FOLDER, FILE, CLASS, FUNCTION entities |
| `artifact_intelligence/analyzer.py` | Orchestrator: runs all parsers, merges + deduplicates output |

**Key design decisions:**
- `models.py` is the hard interface boundary — M2 depends ONLY on this, not on parsing logic
- `code_parser.py` uses position-based heuristic to attribute methods to their parent class
- `analyzer.py` deduplicates by entity `id` and `(source, type, target)` tuples
- `zip_handler.py` skips `.git`, `node_modules`, `__pycache__`, `venv` etc.

---

### 🗄️ Step 3 — M2 Knowledge Graph Engine
_Status_: ✅ Done

**Files created:**

| File | Purpose |
|------|---------|
| `knowledge_graph/__init__.py` | Package init |
| `knowledge_graph/connection.py` | Neo4j driver singleton with `verify_connectivity()` on first call |
| `knowledge_graph/models.py` | NodeLabel + RelType constants; includes M1→Neo4j mapping dicts |
| `knowledge_graph/schema.py` | Creates UNIQUE constraints + indexes on startup (idempotent, IF NOT EXISTS) |
| `knowledge_graph/resolver.py` | Entity dedup — Phase 1 uses MERGE; Phase 3+ will add cross-artifact name matching |
| `knowledge_graph/builder.py` | Batch UNWIND writes: groups entities by label, rels by type for performance |
| `knowledge_graph/queries.py` | M2→M3 query API: `get_graph_data`, `get_node`, `get_children`, `get_stats`, `get_project_tree` |

**Key design decisions:**
- `builder.py` uses `UNWIND $batch` for performance — avoids N individual Cypher queries
- `_is_neo4j_safe()` filters out nested dicts and None before writing properties
- `queries.py` exposes **only Python functions** — no Cypher leaks into M3
- `resolver.py` is intentionally minimal for Phase 1; documented extension points for Phase 3

---

### 🌐 Step 4 — API Layer
_Status_: ✅ Done

**Files created:**

| File | Endpoints |
|------|----------|
| `api/projects.py` | `POST /projects/upload`, `POST /projects/{id}/analyze`, `GET /projects/`, `GET /projects/{id}/status` |
| `api/graph.py` | `GET /projects/{id}/graph`, `GET /projects/{id}/stats`, `GET /projects/{id}/tree`, `GET /entities/{id}`, `GET /entities/{id}/children` |
| `main.py` | FastAPI app + CORS + startup/shutdown lifespan |

**Note**: In-memory `_project_store` used for Phase 1 (stores artifact_data between upload and analyze calls). Will be replaced by a DB in later phases.

**CORS configured** for `http://localhost:3000` (M4 React frontend)

---

### 🧪 Step 5 — Tests
_Status_: ✅ Done

| Test File | Coverage |
|-----------|----------|
| `tests/test_m1_parsers.py` | ZipHandler, ReadmeParser, CodeParser, ArtifactAnalyzer — 20 test cases, no Neo4j needed |
| `tests/test_m2_graph.py` | KnowledgeGraphBuilder, GraphQueryEngine — 12 test cases, requires Neo4j .env |

**Sample project created** at `sample_project/` with:
- `README.md` — mentions Python, FastAPI, React, Neo4j
- `src/auth_service.py` — AuthService, JWTService (Python)
- `src/order_service.py` — OrderService, OrderRepository (Python)
- `src/user_repository.py` — UserRepository + top-level functions (Python)
- `frontend/payment_service.js` — PaymentService, CartManager + top-level functions (JS)

---

### 📦 Step 6 — Dependency Installation
_Status_: ✅ Done

```
Successfully installed: annotated-types, anyio, certifi, click, colorama,
fastapi-0.115.0, h11, httpcore, httptools, httpx-0.27.2, idna, iniconfig,
neo4j-5.24.0, packaging, pluggy, pydantic-2.9.2, pydantic-core-2.23.4,
pydantic-settings-2.5.2, pytest-8.3.3, pytest-asyncio-0.24.0,
python-dotenv-1.0.1, python-multipart-0.0.12, pytz, pyyaml, sniffio,
starlette-0.38.6, typing-extensions, uvicorn-0.30.6, watchfiles, websockets
```

---

### ✅ Step 7 — M1 Test Results
_Status_: ✅ **25/25 PASSED**

```
tests/test_m1_parsers.py::TestZipHandler::test_scan_finds_python_files     PASSED
tests/test_m1_parsers.py::TestZipHandler::test_scan_finds_js_files         PASSED
tests/test_m1_parsers.py::TestZipHandler::test_scan_finds_readme           PASSED
tests/test_m1_parsers.py::TestZipHandler::test_language_counts             PASSED
tests/test_m1_parsers.py::TestZipHandler::test_skips_pycache               PASSED
tests/test_m1_parsers.py::TestReadmeParser::test_extracts_title            PASSED
tests/test_m1_parsers.py::TestReadmeParser::test_extracts_description      PASSED
tests/test_m1_parsers.py::TestReadmeParser::test_detects_technologies      PASSED
tests/test_m1_parsers.py::TestReadmeParser::test_extracts_sections         PASSED
tests/test_m1_parsers.py::TestReadmeParser::test_creates_has_readme_rel    PASSED
tests/test_m1_parsers.py::TestCodeParser::test_detects_python_classes      PASSED
tests/test_m1_parsers.py::TestCodeParser::test_detects_js_classes          PASSED
tests/test_m1_parsers.py::TestCodeParser::test_detects_python_methods      PASSED
tests/test_m1_parsers.py::TestCodeParser::test_detects_top_level_functions PASSED
tests/test_m1_parsers.py::TestCodeParser::test_creates_folder_entities     PASSED
tests/test_m1_parsers.py::TestCodeParser::test_creates_contains_rels       PASSED
tests/test_m1_parsers.py::TestCodeParser::test_creates_defines_rels        PASSED
tests/test_m1_parsers.py::TestCodeParser::test_no_duplicate_entity_ids     PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_full_pipeline         PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_metadata_keys         PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_readme_true           PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_all_entity_types      PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_no_readme_project     PASSED
tests/test_m1_parsers.py::TestArtifactAnalyzer::test_no_duplicates_merge   PASSED
25 passed in 0.32s ✅
```

### ⏳ Step 8 — M2 Tests (pending Neo4j credentials)
_Status_: 🟡 Pending

M2 tests are written (`tests/test_m2_graph.py`, 12 test cases) but require:
1. Neo4j AuraDB account → https://console.neo4j.io
2. `backend/.env` filled with NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
3. Run: `.\venv\Scripts\python -m pytest tests/test_m2_graph.py -v`

---

## 🏁 Session 1 Summary

| Component | Files | Status |
|-----------|-------|--------|
| Scaffolding | .gitignore, requirements.txt, config.py, .env.example | ✅ |
| M1 — ZIP Handler | zip_handler.py | ✅ |
| M1 — README Parser | readme_parser.py | ✅ |
| M1 — Code Parser | code_parser.py | ✅ |
| M1 — Orchestrator | analyzer.py | ✅ |
| M1 — Models | models.py | ✅ |
| M2 — Connection | connection.py | ✅ |
| M2 — Models | models.py | ✅ |
| M2 — Schema | schema.py | ✅ |
| M2 — Resolver | resolver.py | ✅ |
| M2 — Builder | builder.py | ✅ |
| M2 — Queries | queries.py | ✅ |
| API — Projects | api/projects.py | ✅ |
| API — Graph | api/graph.py | ✅ |
| FastAPI App | main.py | ✅ |
| M1 Tests | test_m1_parsers.py | ✅ **25/25** |
| M2 Tests | test_m2_graph.py | 🟡 Awaiting Neo4j |
| Sample Project | sample_project/ | ✅ |
| README | README.md | ✅ |

**Total: 19 files created, 25 tests passing**

---

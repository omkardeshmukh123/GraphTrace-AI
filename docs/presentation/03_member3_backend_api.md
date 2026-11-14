# 🌐 Member 3 — FastAPI Backend & Integration Engine
## Full Presentation Script, Phase Breakdown & Viva Prep

> **Role**: Backend Architect & Integration Engineer — The coordinator and brain of the system  
> **Time Slot**: 6:30 – 9:00 (2.5 minutes)  
> **Phases Owned**: Phase 1 (FastAPI core, REST API, graph store) · Phase 2 (Dep/path queries, traceability engine) · Phase 3 (Requirement traceability endpoints) · Phase 4 (Architecture REST API, synthesizer)

---

## 🎤 Your Full Speaking Script

### Receive Handoff & Take Ownership (6:30 – 6:50)

> *"Thanks [M2]. You've seen the data being extracted and stored. But how does the frontend actually get this data? How does uploading a ZIP file trigger a full graph analysis? How does the system stay secure and reliable? That's what I built — the FastAPI backend, the integration layer, and the intelligence engine."*

### Explain the Backend Role (6:50 – 7:30)

> *"My module is the coordinator. When you upload a project — here's what actually happens."*

> *"The ZIP file hits my backend. I validate it first — checking for path traversal attacks, reserved Windows device names like CON or PRN, unpack ratio limits. Only a clean archive gets through."*

> *"Then I call Member 1's parser plugin — that's the analysis you saw happen. The parser returns an ArtifactGraph — a validated Pydantic model. I check it against my shared contract: exactly one PROJECT node, all relationship endpoints must exist in the graph, IDs must be unique."*

> *"If it passes, I call Member 2's writer plugin to persist it — either to local JSON files or Neo4j cloud. And I make all of this accessible through a REST API that Member 4's frontend calls."*

### Show the API (7:30 – 8:00)

*(briefly open `http://localhost:8000/docs` or point to the running system)*

> *"I exposed 13 REST endpoints. The frontend doesn't talk to the database directly — it talks to my API, and I handle everything behind the scenes. Projects, graphs, dependencies, shortest paths, requirements, traceability, architecture — all behind clean HTTP endpoints."*

> *"The API documentation is auto-generated from my code using FastAPI's OpenAPI integration. Every endpoint, every parameter, every response model is documented here — this is what made it easy for Member 4 to build the frontend without any confusion about what data was available."*

### The Integration Story (8:00 – 8:30)

> *"The hardest part of a 4-person project isn't writing code — it's making everyone's code work together. On day one, I defined the shared `ArtifactGraph` contract in `models.py`. Every member agreed to this interface. Member 1 produces it. Member 2 reads it. Member 4 consumes it."*

> *"This meant we could develop in parallel. Member 1 didn't need to wait for Member 2 to finish Neo4j before testing. Member 4 didn't need a live backend to build the UI. I provided test doubles — mock implementations that satisfy the contract — so everyone could move independently."*

> *"And we set up 101 automated tests. If anyone breaks the contract, tests fail immediately. That's why we have zero regressions across all 4 phases."*

### Phase 4 Highlight — Architecture Endpoints & Synthesizer (8:30 – 9:00)

> *"In Phase 4, I added four new API endpoints for the Architecture Explorer — returning systems, components, their dependencies, and the full technology stack."*

> *"But the most interesting piece was the architecture synthesizer. If a project was uploaded in Phase 1 before the architecture parser existed, it has zero component nodes. What do we do? Instead of showing an empty page, my query layer detects this and dynamically synthesizes the architecture from the existing code graph — finding package nodes, file patterns, and README metadata to construct a meaningful architecture on the fly. And it persists the result back to storage, so the next time you open it, it's instant."*

> *"[Hand off to M4]"*

---

## 📌 Your Technical Work — Phase by Phase

### Phase 1 — FastAPI Core & API Layer (Sep 10–11, 2026)

| File | What it does |
|------|-------------|
| `app/main.py` | FastAPI application factory — request size limits (50MB), structured exception handlers, CORS config for port 5173, startup/shutdown lifespan |
| `app/models.py` | **The shared canonical contract** — `ArtifactGraph`, `Node`, `Relationship`, `NodeType`, `RelationshipType`, `ProjectSummary`, `GraphView`, `DependencyView`, `PathView`, `TraceabilityView` |
| `app/api/routes.py` | 13 REST endpoints — projects CRUD, graph retrieval, dependency BFS, shortest path, requirements, traceability, architecture |
| `app/uploads.py` | Multi-layer security: Zip Slip prevention, `../` traversal checks, reserved Windows device names (`CON`, `PRN`, `AUX`), symlink rejection, unpack ratio limits, 50MB size cap |
| `app/analysis.py` | Upload pipeline orchestrator: archive reception → quarantine extraction → M1 parser → ArtifactGraph validation → M2/local persistence → temp cleanup |
| `app/plugins.py` | Dynamic plugin loader — `GRAPHTRACE_PARSER` and `GRAPHTRACE_GRAPH_WRITER` env vars configure which parser and writer to use at runtime |
| `app/graph/store.py` | Dual-store abstraction: `LocalGraphStore` (JSON files in `.data/`) + `Neo4jGraphStore` (cloud) — both implement the same interface |
| `app/errors.py` | Centralized exception hierarchy — `AppError`, `NotFoundError`, `ConflictError` with structured JSON error responses |
| `app/config.py` | Pydantic Settings — all `GRAPHTRACE_*` environment variables with defaults so tests run offline |

**Initial API endpoint count**: 9 endpoints  
**Tests written**: 33 API integration tests covering upload, security hardening, graph retrieval, error handling ✅

---

### Phase 2 — Graph Intelligence Engine (Sep 11, 2026)

**New algorithms in `app/graph/queries.py`:**

| Algorithm | What it does |
|-----------|-------------|
| Subgraph filter | Filters the full graph by node types, relationship types, search query — returns a reduced `GraphView` |
| Downstream BFS | Starting from a node, traverses `CALLS`, `IMPORTS`, `DEPENDS_ON`, `USES` edges forward — groups results by hop distance |
| Upstream BFS | Same but reversed — finds everything that depends on this node |
| Shortest path | BFS from source to target — returns the exact sequence of nodes and edges connecting them |
| Traceability chain | From a REQUIREMENT node, follows `IMPLEMENTED_BY` → code entities, then collects all containment context |

**Endpoints enabled by this work:**
- `GET /projects/{id}/dependencies/{node_id}?direction=downstream&depth=3`
- `GET /projects/{id}/paths?source=X&target=Y`
- `GET /projects/{id}/requirements`
- `GET /projects/{id}/traceability/{req_id}`

**Bug fixed**: Hardcoded Python-only file detection in `uploads.py` — broadened to `{.py, .js, .jsx, .ts, .tsx}` so frontend-only repos aren't rejected with a 400 error

---

### Phase 3 — Requirement Traceability (Sep–Oct 2026)

- Added `REQUIREMENT` and `DOCUMENT` node types to the shared contract in `models.py`
- Added `IMPLEMENTED_BY` relationship type with strict direction semantics: Requirement → code node only
- Added `ARCH_TYPES` set: `{"SYSTEM", "COMPONENT", "SERVICE", "TECHNOLOGY"}` for type-based filtering
- Updated `analysis.py` to apply manual mapping files: `POST /projects/analyze` accepts an optional `mappings.json` that creates `IMPLEMENTED_BY` edges with `provenance=manual`
- Mapping validation: each reference must resolve to exactly one entity — ambiguous or missing references return HTTP 422 and no graph is published
- Re-exported all Phase 3 models via `shared/contract.py` for clean cross-module imports

**Test result**: Full suite 81 passed, 12 skipped (live Neo4j), 0 failed across all M1+M2+M3 work ✅

---

### Phase 4 — Architecture REST API & Dynamic Synthesizer (Oct 21, 2026)

**New Pydantic response models in `app/models.py`:**
- `ArchitectureStats` — counts of systems, components, services, technologies, and cross-component communication edges
- `ArchitectureView(GraphView)` — the full architectural subgraph with stats attached
- `ComponentSummary` — layer category, folder path, technologies used, exposed endpoints, nested service/file counts
- `ComponentDependencyView` — a component's outgoing calls, incoming callers, used technologies, and exposed services
- `TechItem` and `TechStackView` — technology items with version tags grouped by category

**Four new REST endpoints in `app/api/routes.py`:**
```
GET /projects/{project_id}/architecture         → ArchitectureView with stats
GET /projects/{project_id}/components           → list[ComponentSummary]
GET /projects/{project_id}/components/{id}/dependencies  → ComponentDependencyView
GET /projects/{project_id}/technologies         → TechStackView
```

**The Architecture Synthesizer (`ensure_architecture` in `app/graph/queries.py`):**
- Detects when a stored graph has 0 COMPONENT nodes (legacy project uploaded before Phase 4)
- Dynamically synthesizes from existing FILE, PACKAGE, DOCUMENT nodes:
  - SYSTEM: top-level project hub from README metadata
  - COMPONENTS: Frontend UI (from Vite/Tailwind/React/src), Supabase Cloud Platform, Integration Layer, Security & Core Library, Quality & Test Suite
  - SERVICES: edge functions, API gateways, service classes
  - TECHNOLOGIES: from README badges, package definitions, config files
  - COMMUNICATIONS: auto-connects gateways to services, intra-service flows
- **Atomic persistence**: routes call `store.update(graph)` — the synthesized architecture is written back to disk so the next request is instant

**Store update protocol added to `app/graph/store.py`:**
- Added `update(graph)` method to `GraphStore` protocol
- Implemented in both `LocalGraphStore` (atomic JSON file replace) and `Neo4jGraphStore`
- All 4 architecture routes call `store.update()` after synthesis — zero manual intervention needed

**Test result**: 73 tests passing in 2.31s across M1+M2+M3 all phases ✅

---

## ❓ Your Viva Questions & Answers

**Q: Why FastAPI instead of Flask or Django?**  
A: *"FastAPI is built on modern Python async standards. It auto-generates OpenAPI documentation from type annotations — no manual documentation needed. It uses Pydantic for request/response validation, so malformed data is rejected before it reaches business logic. And it's significantly faster than Flask for high-throughput APIs because of its async foundation."*

**Q: What is Pydantic and why is it important here?**  
A: *"Pydantic validates that incoming data matches a declared schema. If the frontend sends a node with a missing ID, Pydantic rejects it with a 422 error before any of our code runs. This means we can trust the data shape everywhere inside the system. It's the difference between catching a bug at the API boundary versus discovering it hours later in a database write."*

**Q: What is the shared ArtifactGraph contract and why was it so important?**  
A: *"It's the single most important design decision we made. On day one, before anyone wrote parsing or database code, I defined the `ArtifactGraph` model — what a Node looks like, what a Relationship looks like, what fields are required. Every member agreed to this. Member 1 produces it, Member 2 consumes it, Member 4 displays it. Because of this shared contract, all 4 of us could develop in parallel and integrate in a single day."*

**Q: How does the plugin system work?**  
A: *"The parser and graph writer are configured via environment variables — `GRAPHTRACE_PARSER` and `GRAPHTRACE_GRAPH_WRITER`. The backend dynamically imports whatever callable is specified. This means you can swap the parser without touching the backend code. It's how Member 1's parser plugs in cleanly — the backend never imports `artifact_intelligence` directly."*

**Q: What security measures did you implement for file uploads?**  
A: *"Five layers. First, we check for Zip Slip — malicious ZIPs that use `../` paths to write files outside the extraction directory. Second, we reject absolute paths. Third, we block reserved Windows device names like CON, PRN, AUX that can crash Windows systems when created as files. Fourth, we reject symlinks. Fifth, we enforce a 50MB size cap and check the unpack ratio to prevent ZIP bomb attacks."*

**Q: What is the architecture synthesizer and why did you need it?**  
A: *"When we added Phase 4 architecture features, we realized projects uploaded in Phase 1 had no component data — they predated the architecture parser. Instead of breaking the user experience for existing projects, the synthesizer detects this case and builds the architecture on-the-fly from the code graph that already exists. It inspects package names, file patterns, and README keywords to construct meaningful components. This is the most complex piece of logic in the backend."*

**Q: How do you handle the case where Neo4j is not available?**  
A: *"The `LocalGraphStore` is a full fallback — it stores graphs as JSON files in `.data/graphs/`. All queries run in-memory against this data. The switch between local and Neo4j is a single environment variable. For the presentation we're running in local mode — it requires zero cloud infrastructure."*

**Q: What's the difference between `/graph` and `/architecture` endpoints?**  
A: *"`/graph` returns the full code-level graph — files, classes, functions, their relationships. It's everything. `/architecture` filters and aggregates this into the high-level architectural view — only SYSTEM, COMPONENT, SERVICE, TECHNOLOGY nodes and the relationships between them. It's the same data, presented at a higher level of abstraction."*

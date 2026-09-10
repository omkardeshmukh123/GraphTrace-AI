# GraphTrace AI

> An Explainable Software Engineering Intelligence Platform based on a Software Knowledge Graph.

---

## Project Structure

```
graphtrace-ai/
├── backend/                        ← Python FastAPI backend
│   ├── main.py                     ← FastAPI entry point
│   ├── config.py                   ← Settings & env vars
│   ├── requirements.txt
│   ├── .env.example                ← Copy to .env and fill credentials
│   │
│   ├── artifact_intelligence/      ← M1: Parse raw artifacts → JSON
│   │   ├── models.py               ← Entity, Relationship, ArtifactData (M1→M2 contract)
│   │   ├── zip_handler.py          ← ZIP extraction & artifact scanning
│   │   ├── readme_parser.py        ← README.md parsing
│   │   ├── code_parser.py          ← File/Class/Function extraction
│   │   └── analyzer.py             ← M1 orchestrator
│   │
│   ├── knowledge_graph/            ← M2: Build & query the Neo4j Knowledge Graph
│   │   ├── connection.py           ← Neo4j driver singleton
│   │   ├── models.py               ← NodeLabel & RelType constants
│   │   ├── schema.py               ← Constraints & indexes setup
│   │   ├── resolver.py             ← Entity deduplication
│   │   ├── builder.py              ← ArtifactData → Neo4j graph
│   │   └── queries.py              ← Graph query functions (M2→M3 API)
│   │
│   ├── api/
│   │   ├── projects.py             ← POST /projects/upload, POST /projects/{id}/analyze
│   │   └── graph.py                ← GET /projects/{id}/graph, GET /entities/{id}
│   │
│   └── tests/
│       ├── test_m1_parsers.py      ← M1 unit tests (no Neo4j required)
│       └── test_m2_graph.py        ← M2 integration tests (Neo4j required)
│
└── sample_project/                 ← Small test repo for Phase 1 verification
    ├── README.md
    ├── src/
    │   ├── auth_service.py
    │   ├── order_service.py
    │   └── user_repository.py
    └── frontend/
        └── payment_service.js
```

---

## Phase 1 Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Neo4j AuraDB

1. Go to [https://console.neo4j.io](https://console.neo4j.io)
2. Create a **free AuraDB instance**
3. Download the credentials file or copy the connection URI
4. Create your `.env` file:

```bash
cp .env.example .env
```

5. Edit `.env` and fill in your credentials:

```env
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### 4. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Phase 1 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Neo4j connectivity check |
| `POST` | `/projects/upload` | Upload a project ZIP |
| `POST` | `/projects/{id}/analyze` | Build the Knowledge Graph |
| `GET` | `/projects/` | List all analyzed projects |
| `GET` | `/projects/{id}/status` | Get project status |
| `GET` | `/projects/{id}/graph` | Full graph data (nodes + edges) |
| `GET` | `/projects/{id}/stats` | Node counts by type |
| `GET` | `/projects/{id}/tree` | Hierarchical project tree |
| `GET` | `/entities/{id}` | Single entity detail |
| `GET` | `/entities/{id}/children` | Direct children of an entity |

---

## Running Tests

### M1 Tests (no Neo4j required)

```bash
cd backend
pytest tests/test_m1_parsers.py -v
```

### M2 Tests (Neo4j required — fill .env first)

```bash
cd backend
pytest tests/test_m2_graph.py -v
```

### All Tests

```bash
pytest tests/ -v
```

---

## Phase 1 Pipeline

```
Upload project.zip
      ↓
M1: ZipHandler → extract + scan files
      ↓
M1: ReadmeParser → REPOSITORY + README entities
      ↓
M1: CodeParser → FOLDER + FILE + CLASS + FUNCTION entities
      ↓
ArtifactData (JSON) ← M1→M2 contract
      ↓
M2: KnowledgeGraphBuilder → MERGE nodes + relationships into Neo4j
      ↓
Knowledge Graph in Neo4j ← explorable via API
      ↓
M3: GraphQueryEngine → query functions (Phase 1 basics)
      ↓
M4: API responses → frontend visualization (Phase 1 via /docs)
```

---

## Development Team

| Member | Layer | Responsibility |
|--------|-------|---------------|
| **M1** | Artifact Intelligence | Parse raw project → structured JSON |
| **M2** | Knowledge Graph Engine | Build + query the Neo4j graph |
| **M3** | Intelligence & Reasoning | Graph queries, GraphRAG, LLM (Phase 3+) |
| **M4** | Frontend & Visualization | React dashboard, graph explorer (Phase 1+) |

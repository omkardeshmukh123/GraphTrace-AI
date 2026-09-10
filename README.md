# GraphTrace AI

Software knowledge graph for dependency analysis and requirement traceability.
This repository currently contains the **backend developer's Phase 1–3 API work**.

Implemented: FastAPI, ZIP validation/extraction, parser coordination, shared JSON
contract, persistent local graph storage, Neo4j read adapter, graph filtering,
dependency traversal, shortest paths, manual requirement mappings and traceability.

Your teammate still implements the real artifact parser, Neo4j setup and atomic
graph writer. The frontend is separate. Phase 1–3 end-to-end gates are pending
those integrations; the local demo uses explicitly hand-authored graph data.

## Run locally

Use Python 3.11 or newer. Commands below run from the repository root on Windows
PowerShell; activation is unnecessary because they use the virtual environment's
Python directly.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
Copy-Item backend/.env.example backend/.env
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for the interactive API. The default local mode
needs neither Neo4j nor a parser to import and query structured JSON.

## Try the backend now

With the server running, use another PowerShell terminal:

```powershell
$demo = Get-Content sample_data/demo_graph.json -Raw
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/projects/import -ContentType application/json -Body $demo
Invoke-RestMethod http://127.0.0.1:8000/projects/demo/graph
Invoke-RestMethod 'http://127.0.0.1:8000/projects/demo/dependencies/method-find?direction=upstream'
Invoke-RestMethod 'http://127.0.0.1:8000/projects/demo/paths?source=function-login&target=method-find'
Invoke-RestMethod http://127.0.0.1:8000/projects/demo/requirements
Invoke-RestMethod http://127.0.0.1:8000/projects/demo/traceability/req-login
```

Import the demo once; a repeated import returns **409** rather than overwriting.
The graph persists under `.data/graphs/` across server restarts.

The demo exposes this path:

```text
REQ-001 → login_user → AuthService.login → UserRepository.find
```

REQ-002 is intentionally unmapped. API graph responses contain `nodes` and
`relationships`; each relationship retains its actual source/target direction.

## Real repository analysis

First follow [the teammate integration contract](docs/INTEGRATION.md) and configure
`GRAPHTRACE_PARSER`. Generate a ZIP fixture:

```powershell
.\.venv\Scripts\python.exe -m scripts.make_demo
```

In `/docs`, open `POST /projects/analyze`, click **Try it out**, then select:

- `repository`: `.data/sample_project.zip`
- `requirements`: `sample_data/requirements.md` (optional)
- `mappings`: `sample_data/mappings.json` (optional)

Analysis runs synchronously and returns a new project ID after successful storage.
Without a configured parser it returns **503 integration_not_configured**. The API
never substitutes a demo graph for a real repository. Every upload creates a new
project; incremental updates and background progress tracking are future work.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/health` | Process health and selected store |
| GET | `/health/ready` | Storage connectivity |
| GET | `/projects` | Project summaries and counts |
| POST | `/projects/import` | Import a validated artifact graph |
| POST | `/projects/analyze` | Analyze ZIP + optional Markdown SRS/mappings |
| GET | `/projects/{project_id}` | Project summary |
| GET | `/projects/{project_id}/graph` | Graph with optional filters |
| GET | `/projects/{project_id}/dependencies/{node_id}` | Upstream/downstream traversal |
| GET | `/projects/{project_id}/paths` | One shortest path between source and target |
| GET | `/projects/{project_id}/requirements` | Requirements and mapping status |
| GET | `/projects/{project_id}/traceability/{requirement_id}` | Explicit mappings and contextual code paths |

Use repeated `node_type` / `relationship_type` query parameters for multiple
filters, e.g. `?node_type=CLASS&node_type=METHOD`. `search` matches node name or ID
case-insensitively. Graph filters retain only edges whose endpoints remain visible.

Dependency queries take `direction=upstream|downstream`, `max_depth=1..10`
(default 3), and optional `relationship_type`. The root is included, with distance
zero. For **A CALLS B**, B is downstream of A; A is upstream of B. Class-level
dependencies require corresponding parser-emitted DEPENDS_ON edges.

Path queries require `source` and `target`, with `max_depth` defaulting to 6 and
`directed=true`. Set `directed=false` to traverse either direction. Returned edge
directions are preserved even during reverse traversal. `found=false` means no
path was found **within the requested depth and filters**.

Traceability follows IMPLEMENTED_BY first, then code dependencies/containment.
It returns direct `implementation_ids`, contextual `evidence_paths`, and
`mapping_status`. Mapped does not mean correctness, test coverage or verified
completion. `depth_limited=true` means reachable context extends beyond the result.

Errors use `{"error":{"code":"...","message":"..."}}`. Invalid requests return
422, missing projects/nodes 404, duplicate projects 409, excessive input 413,
invalid parser output 502 and unavailable integrations/database 503.

## Repository layout

```text
backend/app/
  api/routes.py       HTTP endpoints
  main.py             App lifecycle, CORS, errors, request size limits
  config.py           Environment settings
  models.py           Shared data contract and ID helper
  uploads.py          Safe ZIP extraction and sidecar validation
  analysis.py         Parser → manual mappings → storage coordination
  parsers/            Teammate's parsers go here
  graph/store.py      Local and Neo4j adapters
  graph/queries.py    Dependency/path/traceability queries
backend/tests/        API and integration-contract tests
shared/               Generated artifact JSON Schema
sample_project/       Small Python parser input
sample_data/          Hand-authored graph, requirements, mappings
docs/INTEGRATION.md    Exact teammate handoff
scripts/              Fixture and schema generation
```

## Tests and limits

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests exercise graph validation, isolation, cycles, path direction/depth, mapping
status, persistence, uploads, cleanup, size limits and integration failures. Neo4j
adapter tests use a test double; a live database and real parser must be validated
separately using the integration checklist.

Prototype limits: 20 MiB ZIP, 100 MiB extracted content, 2,000 ZIP entries,
1 MiB each for requirements/mappings, 5,000 nodes and 20,000 relationships.
ZIP uploads containing links, path traversal, case collisions or unsupported files
are rejected. Uploaded code is never executed by this backend. Requests are
bounded during body reading; uploads are removed after analysis.

This is a local development API with no authentication. Project scoping separates
graph queries but is not user access control. Run it on localhost while building.
There is no PDF parsing, automatic requirement matching, frontend, GraphRAG, LLM,
test intelligence or change-impact module in this backend milestone.

Implementation references: [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/),
[FastAPI application lifespan](https://fastapi.tiangolo.com/advanced/events/),
[Neo4j Python query parameters](https://neo4j.com/docs/python-manual/current/query-simple/).

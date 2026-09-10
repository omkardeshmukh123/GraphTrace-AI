# Backend / parser / graph-builder handoff

This document is the contract between the two developers for Phases 1–3.

| Owner | Responsibility |
| --- | --- |
| Backend developer | FastAPI, input validation, upload lifecycle, coordination, manual mapping application, graph reads, dependency/path queries, traceability responses |
| Parser/graph developer | Tree-sitter extraction, README/Markdown requirements parsing, entity resolution, Neo4j provisioning, schema constraints, atomic graph creation |

The backend can already operate on `sample_data/demo_graph.json`. That file is
hand-authored, not parser output. No production parser or Neo4j writer is bundled.

## 1. Shared artifact format

`shared/artifact_schema.json` is generated from `backend/app/models.py`:

```powershell
python -m scripts.generate_contract
```

Example (abbreviated properties):

```json
{
  "schema_version": "1.0",
  "project_id": "project-123",
  "nodes": [
    {"id": "project-123", "type": "PROJECT", "name": "Example", "properties": {}},
    {"id": "req-1", "type": "REQUIREMENT", "name": "Login", "properties": {"reference": "REQ-001"}},
    {"id": "function-1", "type": "FUNCTION", "name": "login", "properties": {"reference": "auth.py::login", "path": "auth.py", "line_start": 1}}
  ],
  "relationships": [
    {"source": "project-123", "target": "function-1", "type": "CONTAINS", "properties": {}},
    {"source": "req-1", "target": "function-1", "type": "IMPLEMENTED_BY", "properties": {"provenance": "manual"}}
  ]
}
```

Rules enforced by backend model validation (including rules beyond JSON Schema):

- Exactly one PROJECT node; its ID equals `project_id`.
- IDs are URL-safe strings of 1–160 characters, starting with an ASCII letter or
  digit; subsequent characters may include letters, digits, `_`, `.`, `:`, `-`.
- IDs must be unique within a project. Database identity is `(project_id, id)`.
  Use `make_node_id(project_id, node_type, reference)` to generate stable opaque
  IDs for the same project. Re-uploading currently creates a new project ID.
- All relationship endpoints must exist in the same graph. No duplicate
  `(source, type, target)` triples.
- `IMPLEMENTED_BY` points from REQUIREMENT to a code node. `IMPLEMENTS` is
  reserved for code/interface relationships; these are different relationships.
- Metadata belongs inside `properties`, a JSON object. Preserve source paths,
  line ranges, language, qualified names, requirement descriptions and categories.
- Use repository-relative POSIX paths, never paths inside temporary uploads.
- At most 5,000 nodes and 20,000 relationships. Oversized Neo4j reads fail
  explicitly instead of returning silently incomplete graphs.

Direction conventions:

| Relationship | Source → target |
| --- | --- |
| CONTAINS | Parent → child |
| IMPORTS | Importing file/module → imported file/module |
| CALLS | Caller → callee |
| DEPENDS_ON | Dependent → dependency |
| EXTENDS / IMPLEMENTS | Subtype/implementation → base/interface |
| IMPLEMENTED_BY | Requirement → code |
| PART_OF | Child → parent |
| DOCUMENTED_BY | Entity → document |

Dependency queries use IMPORTS, CALLS, EXTENDS, IMPLEMENTS, DEPENDS_ON and USES
by default. They do not automatically climb CONTAINS edges. To support class
dependencies, the parser should emit class-level DEPENDS_ON relationships in
addition to method-level CALLS. Unresolved external calls must not be guessed.

## 2. Parser interface (friend implements this)

Place the implementation under `backend/app/parsers/`, for example `pipeline.py`:

```python
from pathlib import Path
from backend.app.models import ArtifactGraph

def parse_project(
    *, project_id: str, repository_root: Path, requirements_text: str | None
) -> ArtifactGraph:
    # Parse Python/README files and the supplied Markdown SRS.
    # Return the ArtifactGraph contract, or a dict with the same fields.
    ...
```

Configure `backend/.env`:

```dotenv
GRAPHTRACE_PARSER=backend.app.parsers.pipeline:parse_project
```

This is a synchronous callable. The API runs it in FastAPI's worker thread pool.
It receives a safely extracted folder, with a single enclosing ZIP folder removed
where applicable. Common generated/dependency directories are excluded. It must
not execute uploaded code, install dependencies, or launch project scripts.

The uploaded Markdown SRS is passed as UTF-8 text, or `None`. The parser owns
extracting requirements, categories, actors, descriptions, and references. Do not
claim support for PDF parsing or automatic implementation detection in this phase.

The folder is temporary and removed on success or failure. Copy any source
snippets needed later into artifact properties. Do not return temporary paths.
Parser errors or invalid output produce HTTP 502, with details in backend logs.

## 3. Manual mappings

Upload the optional `mappings` JSON file with `POST /projects/analyze`:

```json
[
  {"requirement": "REQ-001", "implementation": "controller.py::login_user"}
]
```

Each reference matches either a node ID or `properties.reference`, and must resolve
to exactly one entity. Use requirement references such as `REQ-001` and qualified
code references such as `auth.py::AuthService.login`. Ambiguous/missing references
return HTTP 422 and publish no graph. The backend adds IMPLEMENTED_BY edges with
`properties.provenance = "manual"`. Existing identical edges are preserved.

The traceability response separates direct `implementation_ids` from contextual
dependency/containment paths. One shortest evidence path is returned per reachable
node. A mapped requirement is not proof of implementation correctness or coverage.

## 4. Neo4j storage contract (friend provisions and writes this)

Every graph node must have the `Entity` label and these properties:

```text
project_id       string
id               string
type             uppercase contract node type
name             string
properties_json  JSON-encoded string of the artifact properties object
```

Extra labels such as CLASS or FUNCTION are optional. Relationship types must
match the contract enum. Relationship metadata is also stored as `properties_json`.
All edges connect entities in the same project. The backend deliberately reads
only edges whose source and target both belong to the requested project.

Create the uniqueness constraint before graph writes:

```cypher
CREATE CONSTRAINT entity_identity IF NOT EXISTS
FOR (n:Entity) REQUIRE (n.project_id, n.id) IS UNIQUE;
```

Implement the writer under `backend/app/graph/builder.py`:

```python
from backend.app.models import ArtifactGraph

def write_graph(*, graph: ArtifactGraph, driver, database: str) -> None:
    # Create the entire graph in one driver.session(...).execute_write(...).
    # CREATE the PROJECT node first; reject existing projects with AppError(409,
    # "project_exists", "Project already exists."). Do not overwrite a project.
    # Create remaining entities and relationships atomically.
    # Whitelist enum relationship types before interpolating Cypher identifiers.
    # Parameterize all values; propagate failures so the transaction rolls back.
    ...
```

The backend owns driver lifetime; the writer must not close it. Failed writes
must leave no partial graph. The uniqueness constraint must handle concurrent
attempts to create the same project as well as sequential duplicates.

Enable the adapter only after implementing the writer and starting Neo4j:

```dotenv
GRAPHTRACE_STORE=neo4j
GRAPHTRACE_NEO4J_URI=bolt://localhost:7687
GRAPHTRACE_NEO4J_USERNAME=neo4j
GRAPHTRACE_NEO4J_PASSWORD=your-local-password
GRAPHTRACE_NEO4J_DATABASE=neo4j
GRAPHTRACE_GRAPH_WRITER=backend.app.graph.builder:write_graph
```

Neo4j reads use parameterized Cypher. For today's small repositories, the backend
loads a bounded project snapshot and computes dependency/path/traceability
traversals in Python. Large-graph server-side traversal is later work. Local JSON
and Neo4j modes are separate stores; switching modes does not migrate data.

## 5. Integration checklist

1. Generate `.data/sample_project.zip` with `python -m scripts.make_demo`.
2. Enable the parser in local mode. Upload the ZIP, `sample_data/requirements.md`
   and `sample_data/mappings.json` through `/docs`.
3. Verify all CALLS endpoints exist, references match mapping inputs, and file
   paths are relative to the extracted repository root.
4. Verify the resulting project graph, upstream/downstream dependencies and
   REQ-001 implementation path. REQ-002 must remain unmapped.
5. Implement the Neo4j writer, constraints and transaction rollback behavior.
6. Enable Neo4j mode; repeat upload and queries against the actual database.
7. Attempt duplicate import: expect 409 with the original graph intact. Attempt
   invalid input: ensure no partial project appears in Neo4j.

The checked-in tests cover the API with local storage, parser contract test doubles,
and a Neo4j read-adapter test double. They do not establish that a real parser or
live Neo4j pipeline works; run this checklist when those pieces are available.

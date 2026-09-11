# Project Architecture Reorganization Report
**Reference Documents**: `docs/GT_Modules.md` and `docs/GraphTrace AI — Complete Project Master Specification.md`  
**Purpose**: Align codebase folder structure and module ownership strictly with team member responsibilities.

---

## 1. Executive Summary & Root Cause

The current repository layout has architectural clutter because files performing **Member 1 (Artifact Intelligence)** and **Member 2 (Knowledge Graph Engine)** tasks were placed inside Member 3's **`backend/app/`** folder:

1. **`backend/app/parsers/pipeline.py`** is sitting in Member 3's folder, even though its entire purpose is running Member 1's parsers and producing the structured artifact output.
2. **`backend/app/graph/builder.py`** is sitting in Member 3's folder, even though its entire purpose is writing nodes, relationships, and schema constraints to Neo4j, which is Member 2's core responsibility.

This creates confusion, duplicate/parallel schemas, and scatters individual member responsibilities across directories.

---

## 2. Member Responsibilities (Per `GT_Modules.md` & Master Spec)

```
┌────────────────────────────────┐
│   MEMBER 1                     │
│   Artifact Intelligence        │
│   (artifact_intelligence/)     │
│   "Raw Project → Structured    │
│    Software Knowledge"         │
└──────────────┬─────────────────┘
               │ Structured JSON / Artifact Graph
               ▼
┌────────────────────────────────┐
│   MEMBER 2                     │
│   Knowledge Graph Engine       │
│   (knowledge_graph/)           │
│   "Structured Knowledge →      │
│    Connected Neo4j Graph"      │
└──────────────┬─────────────────┘
               │ Connected Graph / Cypher Queries
               ▼
┌────────────────────────────────┐
│   MEMBER 3                     │
│   Intelligence & Reasoning     │
│   (app/)                       │
│   "Knowledge Graph → Analysis, │
│    Reasoning & APIs"           │
└──────────────┬─────────────────┘
               │ REST APIs
               ▼
┌────────────────────────────────┐
│   MEMBER 4                     │
│   Frontend & Visualization     │
│   (frontend/)                  │
│   "Interactive Developer UI"   │
└────────────────────────────────┘
```

### Member 1: Artifact Intelligence (`backend/artifact_intelligence/`)
- **Official Responsibility**: *"Make GraphTrace AI understand software artifacts. Raw Project → Structured Software Knowledge."*
- **Assigned Modules from `GT_Modules.md`**:
  1. **Requirement Intelligence**: SRS & Markdown requirement extraction (`REQ-xxx`, categories, descriptions).
  2. **Architecture Intelligence**: README analysis, project structure, component and technology detection.
  3. **Code Intelligence**: AST analysis, files, packages, classes, functions, calls, imports, inheritance.
  4. **Test & Documentation Intelligence**: Test cases, docs, README parsing.
  5. **Common Artifact Output**: Define the structured output format, normalize all extracted knowledge, and hand off the complete structured artifact graph to Member 2.
- **Misplaced File**: [`backend/app/parsers/pipeline.py`](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/parsers/pipeline.py)
  - **Verdict**: This file is Member 1's pipeline orchestrator! It runs the analyzers, parses SRS requirements, and outputs the normalized graph. **It belongs in `backend/artifact_intelligence/pipeline.py`**.

---

### Member 2: Knowledge Graph Engine (`backend/knowledge_graph/`)
- **Official Responsibility**: *"Turn Member 1's extracted information into the Software Knowledge Graph. Structured Software Knowledge → Connected Software Knowledge Graph."*
- **Assigned Modules from `GT_Modules.md`**:
  1. **Graph Schema Design**: Define node types (`PROJECT`, `FILE`, `CLASS`, `FUNCTION`, `REQUIREMENT`, etc.), relationship types (`CONTAINS`, `CALLS`, `IMPORTS`, `DEPENDS_ON`, `IMPLEMENTED_BY`), and rules.
  2. **Neo4j Integration**: Neo4j driver connection, database configuration, transaction handling.
  3. **Node & Relationship Creation**: Create all nodes and edges in Neo4j in atomic batches.
  4. **Entity Resolution**: Prevent duplicate nodes, handle entity IDs and multi-tenant scoping.
  5. **Graph Query Engine (Data Layer)**: Cypher queries to load graph nodes and edges from Neo4j.
- **Misplaced File**: [`backend/app/graph/builder.py`](file:///d:/GraphTrace-Ai/GraphTrace-AI/backend/app/graph/builder.py)
  - **Verdict**: This file creates the Neo4j constraints and writes nodes and relationships in atomic batches. **It belongs in `backend/knowledge_graph/builder.py`**.

---

### Member 3: Intelligence & Reasoning Engine (`backend/app/`)
- **Official Responsibility**: *"Make the Knowledge Graph intelligent and useful for developers. Knowledge Graph → Analysis, Reasoning & Explainable Intelligence."*
- **Assigned Modules from `GT_Modules.md`**:
  1. **Graph Query Engine & Traversal**: BFS upstream/downstream dependency traversal, shortest paths between code elements.
  2. **Requirement Traceability**: Link requirements to implementing code, compute evidence paths, determine mapped/unmapped status.
  3. **Dependency Intelligence**: Upstream/downstream caller/callee distance analysis, cycle detection.
  4. **Intelligence APIs & Web Server**: Expose the REST APIs (`/dependencies`, `/paths`, `/traceability`, `/projects`) via FastAPI.
  5. **Storage & Controller Coordination**: Coordinate the upload lifecycle, local offline fallback vs live Neo4j persistence.
- **What Belongs in `backend/app/`**:
  - `api/routes.py` — REST API Endpoints.
  - `graph/queries.py` — Member 3's BFS, dependency, shortest-path, and traceability reasoning engine.
  - `graph/store.py` — Persistence abstraction (offline JSON store + Neo4j store wrapper calling Member 2).
  - `main.py`, `config.py`, `errors.py`, `uploads.py`, `analysis.py` — FastAPI application lifecycle, security, and controllers.

---

## 3. Detailed File-by-File Placement

| Current Location | Actual Owner | Intended Location per Spec | Rationale |
|---|---|---|---|
| `backend/app/parsers/pipeline.py` | **Member 1** | `backend/artifact_intelligence/pipeline.py` | Runs M1 parsers & extracts SRS requirements into common artifact output. |
| `backend/app/parsers/__init__.py` | **Member 1** | *Delete (Folder deprecated)* | `app/parsers/` folder is removed completely from Member 3. |
| `backend/app/graph/builder.py` | **Member 2** | `backend/knowledge_graph/builder.py` | Creates Neo4j uniqueness constraints and writes graph entities in atomic transactions. |
| `backend/app/graph/queries.py` | **Member 3** | `backend/app/graph/queries.py` *(Kept)* | In-memory BFS dependency traversal, shortest paths, and traceability reasoning. |
| `backend/app/graph/store.py` | **Member 3** | `backend/app/graph/store.py` *(Kept)* | Application storage controller coordinating local offline JSON and calling M2's Neo4j builder. |
| `backend/app/api/routes.py` | **Member 3** | `backend/app/api/routes.py` *(Kept)* | Intelligence REST endpoints. |
| `backend/app/analysis.py` | **Member 3** | `backend/app/analysis.py` *(Kept)* | Orchestrator calling M1 pipeline, M2 builder, and M3 store. |

---

## 4. Target Clean Repository Structure

```text
backend/
├── artifact_intelligence/              # 🟢 MEMBER 1 (Raw Project → Structured Knowledge)
│   ├── __init__.py
│   ├── analyzer.py                     #   Orchestrator across parsers
│   ├── code_parser.py                  #   AST, class, function, call parsing
│   ├── readme_parser.py                #   README & architecture parser
│   ├── zip_handler.py                  #   ZIP extraction & file scanning
│   ├── pipeline.py                     #   ← MOVED FROM app/parsers/ (Module 1.6 Output Pipeline)
│   └── models.py                       #   M1 Data Models
│
├── knowledge_graph/                    # 🟢 MEMBER 2 (Structured Knowledge → Neo4j Graph)
│   ├── __init__.py
│   ├── connection.py                   #   Neo4j driver singleton
│   ├── schema.py                       #   Constraint & index definitions
│   ├── builder.py                      #   ← UNIFIED (Writes nodes & edges atomically to Neo4j)
│   ├── resolver.py                     #   Entity deduplication & identity resolution
│   ├── queries.py                      #   Direct Neo4j Cypher read queries
│   └── models.py                       #   M2 schema models
│
└── app/                                # 🟢 MEMBER 3 (Intelligence, Reasoning & Web APIs)
    ├── __init__.py
    ├── main.py                         #   FastAPI factory & middleware
    ├── config.py                       #   Pydantic application settings
    ├── errors.py                       #   Standard error handlers (404, 409, 422, 502)
    ├── models.py                       #   API schemas & unified ArtifactGraph contract
    ├── plugins.py                      #   Dynamic plugin loader
    ├── uploads.py                      #   Upload validation & security
    ├── analysis.py                     #   Analysis workflow controller (calls M1 -> M2 -> M3)
    ├── api/
    │   ├── __init__.py
    │   └── routes.py                   #   FastAPI routes (/dependencies, /paths, /traceability)
    └── graph/
        ├── __init__.py
        ├── queries.py                  #   M3 BFS dependency traversal, paths & traceability
        └── store.py                    #   Storage manager (calls knowledge_graph.builder for Neo4j)
```

> **Notice the cleanup**:
> - `backend/app/parsers/` is **completely removed** — Member 3 no longer hosts parser code.
> - `backend/app/graph/builder.py` is **moved to Member 2's `knowledge_graph/`** — Member 3 no longer hosts Neo4j write logic.
> - Every member's folder contains **only their work**.

---

## 5. Step-by-Step Execution Plan

1. **Move M1 Parser Pipeline**:
   - Move `backend/app/parsers/pipeline.py` to `backend/artifact_intelligence/pipeline.py`.
   - Remove the now-empty `backend/app/parsers/` folder.
   - Update `pipeline.py` internal imports to reference local `artifact_intelligence` modules.

2. **Unify M2 Neo4j Writer**:
   - Merge `backend/app/graph/builder.py` into `backend/knowledge_graph/builder.py` as the official Neo4j writer.
   - Remove `backend/app/graph/builder.py`.

3. **Update Member 3 References & Defaults**:
   - In `backend/app/analysis.py` and `backend/app/config.py`:
     - Default parser plugin: `backend.artifact_intelligence.pipeline:parse_project`.
     - Default graph writer plugin: `backend.knowledge_graph.builder:write_graph`.

4. **Update Tests**:
   - Update import in `backend/tests/test_parser_plugin.py` to import `parse_project` from `backend.artifact_intelligence.pipeline`.
   - Update import in `backend/tests/test_neo4j_adapter.py` to import `write_graph` from `backend.knowledge_graph.builder`.

5. **Verification**:
   - Run full pytest suite across all 93 tests to ensure **100% tests pass** with zero regressions.
   - Update `docs/dev_diary.md` with the refactoring log.

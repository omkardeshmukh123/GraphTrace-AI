# 🗄️ Member 2 — Knowledge Graph Engine
## Full Presentation Script, Phase Breakdown & Viva Prep

> **Role**: Knowledge Graph Engineer — The memory and structure of the system  
> **Time Slot**: 4:00 – 6:30 (2.5 minutes)  
> **Phases Owned**: Phase 1 (Neo4j schema + graph builder) · Phase 2 (Dep queries) · Phase 3 (Requirement nodes) · Phase 4 (Architecture schema + query engine)

---

## 🎤 Your Full Speaking Script

### Receive Handoff & Set the Scene (4:00 – 4:20)

> *"Thanks [M1]. So we've just analyzed a project — my teammate's parser has extracted hundreds of entities and relationships. But where does all of that actually go? That's my job. I'm [your name], and I built the Knowledge Graph Engine — the memory of GraphTrace AI."*

### Explain the Graph — What It Looks Like (4:20 – 4:50)

> *"Let me navigate to the Knowledge Graph. This is what the system now knows about the project."*  
*(click 🔭 Launch Graph from the dashboard)*

> *"What you're looking at is a live knowledge graph. Every single dot on this canvas is a real entity from the codebase — a file, a class, a function, a service, a component. Every line connecting two dots is a relationship — this file contains this class, this function calls that one, this service communicates with that database."*

> *"Notice the colors — that's not random. Blue dots are files. Green are classes. Pink are functions. Amber are methods. Purple are packages. Rose are requirements. Each color means something specific."*

### Walk Through the Graph Interactively (4:50 – 5:30)

> *"Now watch what happens when I click on a node."*  
*(click any CLASS node)*

> *"An inspector panel slides in showing me everything about this entity — its name, its type, what line in the file it was defined on, its language. And below that, all its direct connections — what it's inside of, what functions are defined inside it, and what other nodes it relates to."*

> *"I can click any of those neighbors and jump to them directly. I'm traversing the graph interactively — following relationships like a map."*

*(use the search box — type a class name)*

> *"I can also search for anything by name. Type a class name — it highlights immediately in the graph. If I'm exploring an unfamiliar project, this lets me find the exact entity I care about without scrolling through hundreds of nodes."*

### Explain the Database Layer (5:30 – 6:10)

> *"Behind this visualization, everything is persisted in Neo4j — a graph database. My module handles all of that. In Phase 1, I designed the graph schema: defined what node types exist, what properties each type carries, and what relationship types are allowed."*

> *"I built the graph builder — when Member 1's parser finishes, my builder receives the ArtifactGraph data and writes it to Neo4j using batch UNWIND operations. Instead of one database call per node, I group hundreds of nodes into a single query. Fast and atomic."*

> *"I also designed the schema constraints — uniqueness rules so the same entity can never be written twice, even if the same project is uploaded repeatedly. We use MERGE operations — 'create this if it doesn't exist, update it if it does.'"*

> *"In Phase 4, I extended all of this for architecture nodes — SYSTEM, COMPONENT, SERVICE, TECHNOLOGY — adding new constraints, new indexes, and new query methods for the architecture explorer."*

### Handoff (6:10 – 6:30)

> *"The graph is built and queryable. But how does the frontend get this data, and what intelligence sits on top? [M3] will walk you through the backend that ties everything together."*

---

## 📌 Your Technical Work — Phase by Phase

### Phase 1 — Graph Schema & Builder (Sep 10–11, 2026)

| File | What it does |
|------|-------------|
| `knowledge_graph/connection.py` | Neo4j Bolt driver singleton — manages connection lifecycle, pooling, `verify_connectivity()` on startup |
| `knowledge_graph/schema.py` | Idempotent schema setup — creates UNIQUE constraints and lookup indexes using `IF NOT EXISTS` |
| `knowledge_graph/builder.py` | Batch writer — groups entities by label type, uses `UNWIND $batch` Cypher for performance |
| `knowledge_graph/queries.py` | GraphQueryEngine — `get_graph_data`, `get_node`, `get_children`, `get_stats`, `get_project_tree` |
| `knowledge_graph/resolver.py` | Entity deduplication — Phase 1 uses MERGE; designed with Phase 3 extension points documented |
| `knowledge_graph/models.py` | NodeLabel and RelType constants + reverse mapping dicts for M1→Neo4j type conversion |
| `app/graph/builder.py` (M2→M3 bridge) | Implements `write_graph()` plugin interface — translates ArtifactGraph → Neo4j atomic transaction |

**Key design decision**: `_is_neo4j_safe()` filter — strips nested dicts and None values before writing properties, preventing Neo4j serialization errors on complex data  
**Key design decision**: PROJECT node is written first in a separate step, then remaining nodes batch-written, then relationships batch-written — if any step fails, the transaction rolls back completely

---

### Phase 2 — Dependency Query Intelligence (Sep 11, 2026)

- GraphQueryEngine enhanced to support directed graph traversal: *"what does this call?"* (downstream) and *"who calls this?"* (upstream)
- Added BFS (Breadth-First Search) traversal with configurable depth — returns dependencies grouped by hop count
- Shortest path algorithm added — given any two node IDs, finds the minimum-hop path connecting them
- These query methods are what power Member 3's `/dependencies` and `/paths` REST endpoints
- **Critical bug fixed**: `os.link` fails across Windows drive boundaries — added safe fallback to `os.replace` with strict 409 duplicate checking preserved

---

### Phase 3 — Requirement Nodes & Traceability Support (Sep–Oct 2026)

- Added `REQUIREMENT` and `DOCUMENT` to NodeLabel constants
- Added `IMPLEMENTED_BY`, `DOCUMENTED_BY` to RelType constants with proper direction semantics
- Schema updated with constraints for requirement nodes
- Resolver extended to match requirement reference strings (`REQ-001`) against code entity `reference` properties for semi-automatic traceability linking
- Standalone standalone M1+M2 server (`port 8001`) exposes `/requirements` and `/traceability` mirroring production API

---

### Phase 4 — Architecture Graph Schema & Query Engine (Oct 21, 2026)

**Extended `knowledge_graph/models.py`:**
- New NodeLabel values: `SYSTEM`, `COMPONENT`, `SERVICE`, `TECHNOLOGY`
- New RelType values: `COMMUNICATES_WITH`, `EXPOSES`, `TESTED_BY`, `PART_OF`, `USES`
- Built `NodeLabel.FROM_ENTITY_TYPE` and `RelType.FROM_REL_TYPE` reverse mapping dicts — maps M1/M3 string types to Neo4j label strings
- Defined `ARCH_NODE_TYPES` set for fast O(1) filtering in queries

**Extended `knowledge_graph/schema.py`:**
- Added uniqueness constraints for all 4 architecture node types using `IF NOT EXISTS` (idempotent — safe to run repeatedly)
- Added performance indexes on `System.project_id`, `Component.name`, `Component.category`, `Service.name`, `Service.service_name`, `Technology.tech_name`, `Technology.category`
- Exposed `generate_schema_queries()` function for dry-run DDL inspection without touching a live database

**New `knowledge_graph/graph_writer.py` (Phase 4 M2→M3 plugin):**
- Updated `_ALLOWED_REL_TYPES` whitelist to include all 5 new architecture relationship types
- Updated `_EXTRA_LABELS` to map SYSTEM→System, COMPONENT→Component, SERVICE→Service, TECHNOLOGY→Technology (PascalCase Neo4j labels)
- All writes happen inside a single Neo4j transaction with rollback on any failure

**New architecture query methods in `knowledge_graph/queries.py`:**
- `get_architecture_view(project_id)` — fetches the architectural subgraph with aggregate stats
- `get_components(project_id)` — retrieves components with folder paths, exposed services, and tech badges
- `get_component_dependencies(component_id)` — maps incoming/outgoing COMMUNICATES_WITH edges, used technologies, and exposed endpoints
- `get_technology_stack(project_id)` — groups technologies by category (web-framework, database, library, build-tool)

**Test result**: 15 new unit tests — all 35 passed (`test_m2_phase4.py` + `test_parser_plugin.py`) ✅

---

## ❓ Your Viva Questions & Answers

**Q: Why Neo4j instead of a relational database like PostgreSQL?**  
A: *"Code is fundamentally a network, not a table. A relational database would need complex multi-table JOINs to answer 'what does this function transitively depend on?' — that's expensive. Neo4j stores relationships as first-class data structures, so traversing 5 hops of dependencies is a single Cypher query that takes milliseconds."*

**Q: What is Cypher?**  
A: *"Cypher is Neo4j's query language. It's pattern-based — you describe the graph structure you're looking for, and Neo4j finds it. For example: `(a:Class)-[:CALLS]->(b:Function)` means 'find all classes that call functions.' It reads almost like a diagram, which makes it intuitive."*

**Q: What is MERGE and why use it instead of CREATE?**  
A: *"MERGE means 'create this node if it doesn't exist, otherwise match the existing one.' If you use CREATE, uploading the same project twice creates duplicate nodes. MERGE is idempotent — you can run it a thousand times and the graph stays consistent. It's essential for a tool where people might re-analyze a project after making code changes."*

**Q: What are batch UNWIND operations?**  
A: *"Instead of sending one database query per node — which would be hundreds of round trips — UNWIND lets you send a list of all nodes in one query. The database processes them all server-side. For a 200-node project, this is the difference between ~200 queries and 3 queries. It's a standard Neo4j performance pattern."*

**Q: What are schema constraints and why do you need them?**  
A: *"A uniqueness constraint tells the database to reject any node whose ID already exists. Without this, two parallel uploads of the same project could create duplicate nodes before we detect the conflict. The constraint enforces correctness at the database level, not just in application code."*

**Q: What is Neo4j AuraDB?**  
A: *"AuraDB is the managed cloud version of Neo4j — no installation, no Docker, no maintenance. You create an account, get a connection URI and credentials, put them in a `.env` file, and you're connected. We chose it because we can't run Docker in our environment, and AuraDB is free for small projects."*

**Q: How does entity resolution work?**  
A: *"In Phase 1, two entities are the same if they have the same ID — which we generate deterministically using uuid5 from the project ID, entity type, and reference path. So the same file analyzed twice always produces the same ID, and MERGE handles the deduplication at the database level. Phase 3 adds name-based fuzzy matching for cross-file class resolution — that's the `resolver.py` extension point."*

**Q: What happens if the Neo4j write fails halfway through?**  
A: *"Everything runs inside a single Neo4j transaction. If anything fails — network error, constraint violation, bad data — the entire transaction rolls back. The database is left in exactly the same state as before the write started. No partial graphs."*

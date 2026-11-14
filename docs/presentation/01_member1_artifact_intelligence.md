# 🧠 Member 1 — Artifact Intelligence
## Full Presentation Script, Phase Breakdown & Viva Prep

> **Role**: Artifact Intelligence Engineer — The eyes of the system  
> **Time Slot**: 0:00 – 4:00 (opening + live demo)  
> **Phases Owned**: Phase 1 (Code + README parsing) · Phase 2 (Dependency intelligence) · Phase 3 (Requirement parsing) · Phase 4 (Architecture extraction)

---

## 🎤 Your Full Speaking Script

### Opening Hook (0:00 – 0:30)

> *"Imagine you're handed a ZIP file. Inside is a software project — thousands of lines of code, dozens of files, folder inside folder. No README worth reading. And you have to understand it in one day. That's the daily reality for developers joining a new team."*

> *"GraphTrace AI was built to solve exactly that. I'm [your name], and I built the Artifact Intelligence layer — the module that reads and understands what's inside that ZIP file."*

### What Artifact Intelligence Does (0:30 – 1:30)

> *"My module is the first thing that runs when you upload a project. It's a pipeline of parsers — each one responsible for extracting a different kind of knowledge from the code."*

> *"In Phase 1, I built three parsers. First — a ZIP Handler that safely opens the archive, scans every file, and classifies them by language. It skips irrelevant folders like node_modules, venv, and __pycache__ automatically."*

> *"Second — a README Parser. It reads the documentation and pulls out the project title, description, technologies mentioned, and architecture notes. This becomes a DOCUMENT node in the graph."*

> *"Third — a Code Parser. For Python files, it uses Python's own AST module to find every class, every function, every method, and what line they're on. For JavaScript and TypeScript it uses structural pattern matching. The result is a complete map of the code's structure."*

> *"In Phase 3, I added Requirement parsing — my module reads Markdown SRS documents and extracts structured requirements like REQ-001, REQ-002, turning natural language descriptions into graph nodes that can later be traced to code."*

> *"And in Phase 4 — Architecture Intelligence. My parser now reads folder names, config files like package.json, requirements.txt, docker-compose.yml, and vite.config — and identifies the architectural layers: frontend, backend, database, API surface, auth service. These become COMPONENT, SERVICE, and TECHNOLOGY nodes."*

### Live Demo — Upload and Analyze (1:30 – 4:00)

**Step 1 — Show the home screen** *(20 sec)*  
> *"This is the GraphTrace AI home screen. You can see existing analyzed projects here — each card shows the project name, how many entities were found, and how many relationships connect them."*

**Step 2 — Click Upload** *(20 sec)*  
> *"To analyze a new project, I click Upload Project. I can drag and drop a ZIP file — no configuration, no setup. Just the code."*  
*(drag sample_project.zip into the modal)*

**Step 3 — Watch it process** *(40 sec)*  
> *"Behind the scenes, right now, my Artifact Intelligence module is running all four parsers in sequence. First the ZIP handler extracts and scans the files. Then the README parser captures the documentation. Then the code parser walks through every Python and JavaScript file. Then the architecture parser identifies components and services. Then all of this is normalized into the shared data contract — the ArtifactGraph format — and handed to the graph database."*

**Step 4 — Analysis complete** *(30 sec)*  
> *"And there it is. In under two seconds. The system found [X] entities and [Y] relationships. Files, classes, functions, components, services, technologies — all extracted, structured, and stored."*

**Step 5 — Click View Dashboard, hand off** *(10 sec)*  
> *"Let me click through to the dashboard and hand this over to [M2] who will show you what the graph actually contains."*

---

## 📌 Your Technical Work — Phase by Phase

### Phase 1 — Basic Artifact Parsing (Sep 10–11, 2026)

| File | What it does |
|------|-------------|
| `artifact_intelligence/zip_handler.py` | Extracts ZIP safely, scans recursively, classifies files by language, skips build/cache folders |
| `artifact_intelligence/readme_parser.py` | Extracts title, description, tech keywords, sections from Markdown — produces DOCUMENT node |
| `artifact_intelligence/code_parser.py` | Python AST parser + JS/TS regex parser — extracts FOLDER, FILE, CLASS, FUNCTION, METHOD entities |
| `artifact_intelligence/analyzer.py` | Orchestrator — runs all parsers, merges outputs, deduplicates by entity ID |
| `artifact_intelligence/models.py` | Internal data types: Entity, Relationship, ArtifactData — the M1→M2 contract |
| `app/parsers/pipeline.py` | Bridge: converts M1 internal types → M3's ArtifactGraph contract (uuid5 IDs, type mappings) |

**Test result**: 25 unit tests — all passed on day one ✅  
**Key achievement**: Bidirectional type mapping between M1's Entity model and M3's Node model, ensuring perfect data handoff

---

### Phase 2 — Dependency Intelligence Contributions (Sep 11, 2026)

- Enhanced code parser to emit `CALLS` relationships between functions — not just structure, but actual function call chains
- Improved JS/TS parsing to cover ES6 exports, arrow functions, and default exports
- Added language distribution metrics — the system reports what percentage of the codebase is Python vs JavaScript
- Fixed cross-team integration bugs: broadened source file detection from Python-only to `{.py, .js, .jsx, .ts, .tsx}` so frontend-only repos aren't rejected

---

### Phase 3 — Requirement Intelligence (Sep–Oct 2026)

- Implemented SRS Markdown parser inside `pipeline.py`
- Supports two heading formats: `## REQ-001: Description` and `**REQ-002**:` bold format
- Each requirement becomes a `REQUIREMENT` node with its ID and description
- Requirements linked to the PROJECT node via `CONTAINS` relationship
- Added `reference` property to all FUNCTION and CLASS nodes so manual traceability mappings can be verified

---

### Phase 4 — Architecture Intelligence (Oct 21, 2026)

**New file:** `artifact_intelligence/architecture_parser.py`

| What it detects | How |
|----------------|-----|
| COMPONENT entities | Maps top-level folder names (`frontend`, `backend`, `api`, `auth`, `db`, `src`) to named architectural layers |
| SERVICE entities | Reads `docker-compose.yml` service entries + scans for `*_service.py`, `*gateway*.py`, `*logger*.py` files |
| TECHNOLOGY entities | Reads `requirements.txt`, `package.json`, `pyproject.toml`, `vite.config.ts`, `tailwind.config.ts` |
| COMMUNICATES_WITH | Auto-generates frontend→backend, backend→db, auth→db communication edges |
| EXPOSES | Detects route/controller file patterns and marks them as exposed API surfaces |
| CONTAINS | Links COMPONENT nodes directly to their FOLDER nodes in the code hierarchy |

**Extended `architecture_parser.py` after Session 9 bug fix:**
- Added context-aware `src/` classification — detects whether `src` is a Frontend UI or Application Core based on what config files exist alongside it
- Added edge function scanner (`**/functions/*/index.ts`) for Supabase-style architectures
- Expanded `FOLDER_COMPONENT_MAP` with 12 new folder name mappings (`supabase`, `functions`, `integrations`, `lib`, `components`, `hooks`, `pkg`, `modules`, `domain`, `controllers`, `routes`)
- Added heuristics for Tailwind, Vite, Vitest, Supabase, TypeScript config file detection

**Verification**: Analysis of `API-Validator-main` after fix: **1 System, 5 Components, 4 Services, 10 Technologies, 8 Inter-service calls** ✅

---

## ❓ Your Viva Questions & Answers

**Q: How does the code parser actually work for Python?**  
A: *"It uses Python's built-in `ast` module — the same thing Python uses internally to parse source code. We walk the AST tree, and every time we see a ClassDef node, we extract a CLASS entity. Every FunctionDef inside a class becomes a METHOD. Every top-level FunctionDef becomes a FUNCTION. We also capture line numbers so the UI can show exactly where in the file each entity is."*

**Q: Why regex for JavaScript instead of a proper parser?**  
A: *"JavaScript's AST is significantly more complex — especially ES6 syntax. For Phase 1, regex patterns matched ~90% of real-world JS patterns with zero dependencies. Phase 2 scope is to swap this for tree-sitter, a battle-tested multi-language parser used by GitHub's code intelligence."*

**Q: How does the architecture parser handle a project it's never seen before?**  
A: *"In two ways. First, the static parser uses a lookup table of common folder names — if it sees a folder called 'controllers', it maps it to an API Surface component. Second, if the project was already in the database but was uploaded before Phase 4 existed, Member 3's synthesizer reconstructs the architecture dynamically from the existing code nodes. We always produce a result — never an empty screen."*

**Q: What is the ArtifactGraph contract?**  
A: *"It's the shared JSON format defined in `app/models.py`. Every node has an ID, a type, a name, and a properties dictionary. Every relationship has a source ID, target ID, and type. My module outputs this format. Member 2 reads it to write to Neo4j. Member 3 validates it. Member 4 displays it. Everyone depends on this same contract."*

**Q: How do you prevent duplicate entities when re-analyzing?**  
A: *"My analyzer deduplicates by entity ID before passing data downstream. The IDs are generated deterministically using uuid5 — the same file at the same path always produces the same ID. At the database layer, Member 2 uses MERGE operations in Neo4j, which further prevents duplicates."*

**Q: How did Phase 4 architecture detection break for the API-Validator project?**  
A: *"The project was analyzed in Phase 1, before the architecture parser existed. The stored graph had no COMPONENT nodes. When we added the architecture page in Phase 4, it queried for components and found zero. We fixed this in two ways — first, we expanded the static parser to handle more folder structures. Second, we added a dynamic synthesizer that runs when zero components are found, building architecture from whatever code data already exists."*

**Q: How many entities does a typical project produce?**  
A: *"For the sample project — a small Python + JavaScript app — we extract around 48–60 nodes and 50+ relationships. For a larger project like the ecommerce demo, we get 198 nodes and 226 relationships across all phases. The system supports up to 5,000 nodes per project."*

---

## 🧘 Calm-Down Protocol
If anything breaks during the upload demo, say: *"Let me demonstrate using our pre-loaded ecommerce demo, which shows the full power of the system."* Navigate to ecommerce-platform. Never show panic — pivot confidently.

# 🗄️ Member 2 — Knowledge Graph Engine
## Presentation Script & Speaking Notes

> **Role**: Graph & Data Layer  
> **Time Slot**: 4:30 – 7:00 (2.5 minutes)  
> **You own**: Explaining the graph, navigating the Graph Explorer, showing the data layer

---

## 🎤 Your Speaking Section — Flow

### Line 1 — Receive handoff & set context (20 sec)
> *"Thanks [M1]. So we've just analyzed a project. Now, what did the system actually learn? Let me show you."*

### Line 2 — Explain the graph visually (40 sec)
*(On the Graph Explorer page — click "🔭 Launch Graph" on the dashboard)*

> *"What you're looking at is a knowledge graph — a living map of the project. Every dot is an entity in the code: a file, a class, a function, a service. Every line between them is a relationship — this file contains this class, this function calls that one."*

*(point to different colored nodes)*

> *"The colors represent types — blue for files, green for classes, pink for functions, purple for packages. You can toggle types on and off using these buttons."*

### Line 3 — Interact with the graph (60 sec)
- Click on a **node** to show the inspector panel
- Say: *"If I click on any node, I get a full profile — its name, type, what it's connected to. I can then click those neighbors and traverse the graph manually."*
- Use the **search box**: type a class name
- Say: *"I can also search for anything — type a class name and it highlights immediately."*
- Drag a node around: *"And this is a live physics simulation — nodes repel and attract based on connections."*

### Line 4 — Bridge to the database (20 sec)
> *"Behind this visualization, everything is stored in a knowledge graph database — Neo4j. My module handles writing all these nodes and relationships in batch, and querying them efficiently. This is what makes the Architecture Explorer possible — structured graph data that can be traversed in any direction."*

### Line 5 — Handoff (10 sec)
> *"Now [M3 name] will walk you through the smart backend that powers all of this."*

---

## 📌 Your Technical Contribution (know this for viva)

**What you built:** `knowledge_graph/` — the data storage and query engine

| Component | What it does |
|---|---|
| `connection.py` | Connects to Neo4j cloud database |
| `schema.py` | Sets up the database structure (constraints, indexes) |
| `builder.py` | Writes all nodes and relationships in fast batch operations |
| `queries.py` | Retrieves graph data for the frontend to display |
| `graph_writer.py` | Phase 4 plugin — writes architecture data to Neo4j |

**Key design decision:** Using `MERGE` instead of `CREATE` in Neo4j means you can re-analyze a project without creating duplicate data.

---

## 🧩 The Database in Plain English (Practice this explanation)

> *"Think of Neo4j like a map app. Normal databases store tables — rows and columns. Neo4j stores dots and lines — nodes and relationships. For code analysis, this is a perfect fit because code IS a network. Functions call each other, files import each other, services depend on services. Graph databases make this natural to store and query."*

---

## ❓ Viva Questions You'll Likely Get

**Q: Why Neo4j and not a regular database like MySQL?**  
A: "Relational databases struggle with many-to-many relationships and graph traversals — you'd need complex JOIN chains. Neo4j is built for exactly this — 'give me everything connected to this node within 3 hops' is a single Cypher query."

**Q: What is Cypher?**  
A: "It's Neo4j's query language. It looks like a diagram — you write `(node)-[:RELATIONSHIP]->(other_node)`. It's very readable compared to SQL for graph data."

**Q: How do you prevent duplicate data?**  
A: "We use `MERGE` — a Neo4j operation that says 'create this if it doesn't exist, otherwise update it'. So re-uploading a project is safe."

**Q: How fast is the graph writing?**  
A: "We use batch UNWIND operations — instead of writing one node at a time, we send hundreds in a single query. This keeps it fast even for large projects."

**Q: What's Neo4j AuraDB?**  
A: "It's the managed cloud version of Neo4j — no installation required, just a connection URI in a config file. We chose it because we can't run Docker in this environment."

---

## 🎯 Things to Point to on Screen

| What to show | Where to find it |
|---|---|
| The graph nodes | Graph Explorer page — colored dots |
| Node inspector | Click any node — right panel slides in |
| Node type legend | Filter toggles at the top of graph |
| Search functionality | Search box in graph explorer |

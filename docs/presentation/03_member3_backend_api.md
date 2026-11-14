# 🌐 Member 3 — FastAPI Backend & Integration
## Presentation Script & Speaking Notes

> **Role**: Backend Architect / API Layer  
> **Time Slot**: 7:00 – 9:30 (2.5 minutes)  
> **You own**: The "brain" explanation, API layer, integration story

---

## 🎤 Your Speaking Section — Flow

### Line 1 — Receive handoff & take control (15 sec)
> *"Thanks [M2]. So you've seen the data layer — but how does the frontend actually get all that information? That's where my module comes in."*

### Line 2 — Explain the backend without going technical (45 sec)
> *"I built the central backend — the brain of GraphTrace AI. Think of it as the coordinator. When you upload a project, my backend receives it, tells Member 1's parser to analyze it, takes the results, stores them in the graph database, and makes them available through a clean API."*

*(optionally open `http://localhost:8000/docs` in a tab briefly)*

> *"If I open the backend docs — this is automatically generated from our code — you can see every 'endpoint' or function that the frontend can call. Upload a project, get a graph, fetch architecture data, find paths between nodes — all organized here."*

### Line 3 — The integration story (45 sec)
> *"One of the challenges in team projects is getting everyone's code to work together. My module was designed to be the integration layer. I defined a shared data contract — a standard format every member agreed on. Member 1's parser outputs this format. Member 2's database writer reads it. Member 4's frontend consumes it."*

> *"This is why we have 101 tests passing — the contract is fully verified. If you break the contract, a test fails. That's how we caught bugs early."*

### Line 4 — Quick highlight of architecture endpoints (30 sec)
> *"For Phase 4 — Architecture Intelligence — I added four new API endpoints. The frontend can ask: 'What's the architecture of this project?' And the backend answers with a full breakdown: systems, components, services, technologies, and how they communicate."*

### Line 5 — Handoff (15 sec)
> *"And all of this is wrapped in a beautiful interface — [M4 name] will show you the finished product."*

---

## 📌 Your Technical Contribution (know this for viva)

**What you built:** `backend/app/` — the production API server

| Component | What it does |
|---|---|
| `main.py` | The FastAPI application — handles all requests, security, error handling |
| `api/routes.py` | 13 REST endpoints the frontend calls |
| `graph/store.py` | Saves and loads project graphs from local files or Neo4j |
| `graph/queries.py` | Smart algorithms to traverse and analyze the graph data |
| `analysis.py` | Orchestrator — coordinates M1 parser → M3 store |
| `uploads.py` | Secure ZIP handling (protects against malicious uploads) |
| `models.py` | Shared data contract used by all 4 members |

**Tests you wrote/integrated:** 33 API integration tests — all passing ✅

---

## 🧩 The API Layer in Plain English (Practice this)

> *"An API is like a waiter in a restaurant. The frontend is the customer — it asks for things. The backend is the kitchen — it prepares things. I'm the waiter — I take the order, relay it to the right kitchen station, and bring back the result. The menu of available orders is documented at `/docs`."*

---

## 🔑 Key Endpoints to Know (in plain language)

| Endpoint | What it does (plain English) |
|---|---|
| `POST /projects/analyze` | "Here's a ZIP file, analyze it" |
| `GET /projects` | "Show me all analyzed projects" |
| `GET /projects/{id}/graph` | "Give me the full node graph for this project" |
| `GET /projects/{id}/architecture` | "Show me the high-level architecture" |
| `GET /projects/{id}/components` | "List all components and their details" |
| `DELETE /projects/{id}` | "Delete this project so I can start fresh" |

---

## ❓ Viva Questions You'll Likely Get

**Q: Why FastAPI and not Django or Flask?**  
A: "FastAPI is modern, fast, and generates documentation automatically. It also validates incoming data automatically using Pydantic — so if the frontend sends the wrong data format, it's rejected before it even reaches our code."

**Q: What is CORS and why did you configure it?**  
A: "CORS is a browser security rule that stops websites from calling other websites' APIs. Since our frontend runs on port 5173 and backend on 8000 — different ports — we had to explicitly allow this. It's one line of config."

**Q: What happens if someone uploads a malicious ZIP file?**  
A: "Member 3's `uploads.py` has several safeguards — it checks for path traversal attacks (files trying to escape the target directory), reserved system filenames, and file size limits. We reject anything suspicious before extraction."

**Q: How did you manage the team integration?**  
A: "I defined the `ArtifactGraph` data contract in `models.py` on day one. Every member codes to this interface. I also set up pytest — our testing framework — so everyone could write tests independently and we'd catch conflicts early."

**Q: What is Pydantic?**  
A: "It's a Python library that validates data shapes. You describe what a 'Node' looks like — it must have an id, a type, some properties — and Pydantic automatically checks every piece of data matches that description. Great for APIs."

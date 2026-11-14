# 🎨 Member 4 — Frontend & Visualization
## Full Presentation Script, Phase Breakdown & Viva Prep

> **Role**: Frontend & Visualization Engineer — The face of the system  
> **Time Slot**: 9:00 – 11:30 (2.5 minutes)  
> **Phases Owned**: Phase 1 (React SPA, Graph Explorer, Dashboard) · Phase 2 (Traceability, Dependencies, Ask AI UI, full design overhaul) · Phase 3 (Requirement traceability matrix) · Phase 4 (Architecture Explorer — topology canvas, services directory, tech stack matrix, dependency drawer)

---

## 🎤 Your Full Speaking Script

### Receive Handoff & Set Expectations (9:00 – 9:20)

> *"Thanks [M3]. You've heard about parsers, databases, APIs. Now let me show you what a user actually sees and touches. I'm [your name], and I built the entire frontend — every screen, every animation, every interaction."*

> *"I'll start with what we built in Phase 1 and 2 — then show you the crown jewel of Phase 4: the Architecture Intelligence Explorer."*

### Phase 1 & 2 — The Core UI (9:20 – 9:50)

*(navigate to Home page — already open)*

> *"This is the home screen. Every project that's been analyzed appears here as a card — project name, entity count, edge count, language breakdown. The Upload button is always visible — one click to drop in a new ZIP."*

*(click into a project → Dashboard)*

> *"The dashboard gives you the project overview — total entities, graph density, a breakdown of entity types, and quick-launch buttons to every view."*

*(click Knowledge Graph)*

> *"The Knowledge Graph Explorer. This is a live physics simulation — nodes repel each other and edges attract them, the graph settles into its natural layout. You can click any node to inspect it, search by name, filter by type, freeze the physics, zoom to fit — full control."*

*(briefly show Traceability and Dependencies tabs in nav)*

> *"Phase 2 added Traceability — click a requirement and trace its path all the way down to the implementing function. And Dependencies — pick any class or function and see everything it calls downstream, or everything that depends on it upstream, configurable to any depth."*

### Phase 4 — Architecture Intelligence Explorer (9:50 – 11:10)

*(navigate to Architecture tab)*

> *"Now — Phase 4. The Architecture Intelligence Explorer. This is what I'm most proud of."*

*(point to KPI banner)*

> *"At the top — five live metrics: Systems, Components, Services, Technologies, and Inter-Service Calls. These aren't hardcoded numbers. Every time you open this page, they're computed fresh from the actual graph data."*

*(on Topology Canvas — let it render fully before speaking)*

> *"This is the Architecture Topology Canvas. It's not just a pretty graph — every node here is a real architectural entity from the analyzed codebase."*

> *"The large indigo node at the center — that's the SYSTEM. The entire project. The purple squircle nodes are COMPONENTS — logical layers like Frontend, Backend, API Surface. The cyan pods are microservices and service classes. The amber crystalline chips are technologies — React, FastAPI, Neo4j, Tailwind."*

> *"The animated particles flowing along the cyan lines? Those are inter-service communications. You're literally watching data flow through the architecture in real time."*

*(hover over a node)*

> *"Hovering illuminates the node and its direct connections — everything unrelated fades out. You immediately see what matters."*

*(click a component card → dependency drawer opens)*

> *"If I click a component, a drawer slides in from the right showing me: what this component calls, what calls it, what technologies it uses, and what APIs it exposes. Full bidirectional dependency mapping in one click."*

*(switch to Services tab)*

> *"The Services Directory — every microservice detected in the project, with its status, its parent component, what it calls, and what calls it."*

*(switch to Technology Stack tab)*

> *"The Technology Stack Matrix — all detected technologies grouped by category. Web frameworks, databases, build tools — automatically categorized from config files. No manual labeling."*

### Handoff to Closing (11:10 – 11:30)

> *"And this is fully interactive — you can click through every layer of the architecture, drill into any component, follow any service call. The whole system, from ZIP upload to this canvas, runs in under 5 seconds."*

> *"Let me hand back to the team to wrap up."*

---

## 📌 Your Technical Work — Phase by Phase

### Phase 1 — React SPA Foundation (Sep 11, 2026)

| File | What it does |
|------|-------------|
| `frontend/vite.config.ts` | Vite + React setup with `/api` reverse proxy to port 8000 — eliminates all CORS issues in development |
| `frontend/src/index.css` | Entire design system: dark mode, glassmorphic card primitives, semantic color tokens, micro-interaction animations |
| `frontend/src/nodeColors.ts` | Node type → color, glow, icon, size mapping for graph rendering |
| `frontend/src/api.ts` | Fully typed fetch client — all API calls with TypeScript interfaces matching backend Pydantic models |
| `frontend/src/pages/Home.tsx` | Projects dashboard — cards with entity counts, language pills, status badges, upload trigger |
| `frontend/src/pages/Dashboard.tsx` | Per-project metrics, entity distribution breakdown, quick-launch hub |
| `frontend/src/pages/GraphExplorer.tsx` | 2D force-directed graph using `react-force-graph-2d` — node type toggles, text search, hover tooltips, camera controls |
| `frontend/src/components/NodeCard.tsx` | Inspector sidebar — node properties, clickable neighbor list for manual graph traversal |
| `frontend/src/components/UploadModal.tsx` | ZIP drag-and-drop upload modal with JSON import option |
| `frontend/src/components/AppShell.tsx` | Navigation header with real-time backend health badge |

**Build result**: 0 TypeScript errors, 0 lint warnings — clean production bundle ✅

---

### Phase 2 — Full Design Overhaul & New Developer Views (Sep–Oct 2026)

**Complete design system rebuild (`index.css`):**
- Deep obsidian background (`#080a0f`) with radial gradient mesh lighting
- Glassmorphic panels with `backdrop-filter: blur(20px)` and hairline borders
- Developer fonts: `Plus Jakarta Sans` for UI text, `JetBrains Mono` for code/IDs
- Animated particle flows along graph relationship edges
- Pulsing status indicators, smooth button elevations, animated dropzones

**New navigation in `AppShell.tsx`:**
- Active project context switcher — switch projects from anywhere without returning to home
- Full route links: Projects · Dashboard · Knowledge Graph · Traceability · Dependencies · Ask AI
- Engine status pill: `Local Engine` or `Neo4j Cloud` based on backend health response

**Three entirely new pages:**

| Page | What it shows |
|------|--------------|
| `Traceability.tsx` | Requirement cards (Mapped/Unmapped badges), linked code implementations, evidence graph traversal paths |
| `Dependencies.tsx` | Searchable focal entity picker, Downstream/Upstream direction switch, BFS depth slider (1–5 hops), shortest path calculator |
| `AskAI.tsx` | Natural language explainability chat, pre-packaged developer prompt chips, grounded responses with graph evidence paths |

**Enhanced `GraphExplorer.tsx`:**
- Multi-ring glow halos for selected/hovered nodes
- Animated particle flow on `CALLS`, `IMPORTS`, `CONTAINS` edges
- Neighbor focus mode — dims unrelated entities on hover
- Tabbed inspector: Overview / Properties / Relationships

---

### Phase 3 — Traceability Matrix (Sep–Oct 2026)

- `Traceability.tsx` fully connected to `GET /requirements` and `GET /traceability/{req_id}` endpoints
- Requirement cards show: ID, description, Mapped/Unmapped status badge, implementation count
- Click any requirement → evidence panel shows exact graph traversal chain: REQ-001 → Component → Class → Method
- Entity chips in the traversal path are clickable — navigate directly to that node in the graph explorer

---

### Phase 4 — Architecture Intelligence Explorer (Oct 21, 2026)

**New TypeScript interfaces in `api.ts`:**
- `ArchitectureStats`, `ArchitectureView`, `ComponentSummary`, `ComponentDependencyView`, `TechItem`, `TechStackView`
- 4 new API client methods: `getArchitecture()`, `getComponents()`, `getComponentDependencies()`, `getTechnologies()`

**`Architecture.tsx` — the full page:**

**KPI Metric Banner (5 cards):**
- Systems, Components, Services, Technologies, Inter-Service Calls
- Each card is clickable — highlights the relevant tab and scrolls to it
- `Explore ↗` micro-link on each card

**Tab 1 — Topology Canvas:**
- 2D force-directed simulation with fully custom canvas rendering
- Node hierarchy with distinct visual language:
  - SYSTEM: planetary orbital hub with rotating dashed outer ring and radial gradient core
  - COMPONENT: cyber squircle with dual neon stroke and specular highlight
  - SERVICE: glowing cyan pod with live emerald green status beacon (`●`)
  - TECHNOLOGY: amber crystalline chip with circuit accent lines
- Multi-layer cyber grid background (`36px` gridlines) with radial vignette illumination
- Edge types with distinct styles:
  - `COMMUNICATES_WITH`: electric cyan arcs (`linkCurvature=0.2`), animated particles (`density=5`), directional arrows
  - `CONTAINS`: soft lavender structural lines
  - `USES`: amber dashed lines
  - `EXPOSES`: emerald dotted lines
- Hover = neighborhood illumination, everything else fades
- Clicking any edge opens the Inter-Service Communication Drawer
- Float controls: category filters, physics pause/resume, auto-zoom fit

**Tab 2 — Component Catalog:**
- Filter pills: All / Frontend / Application / Service / Library
- Glass cards per component: folder path, service count, file count, tech count, exposed endpoints preview
- "Inspect Dependencies" button → opens the sliding Dependency Drawer

**Tab 3 — Services Directory:**
- Per-service cards with: live status badge (`● ONLINE`), parent component tag, outbound calls list, inbound callers list
- All services clickable → launches the Service Inspector

**Tab 4 — Technology Stack Matrix:**
- Technologies grouped by category: web-framework, ui-framework, database, cache, task-queue, build-tool
- Version tags where detected, component usage badges

**Component Dependency Drawer (slide-in panel):**
- Outbound Service Calls with direction indicator
- Inbound Callers
- Technologies Bound (databases, caches, frameworks)
- Exposed Endpoints

**Navigation integration:**
- `AppShell.tsx`: added `🏛️ Architecture` nav tab, Phase 4 badge
- `App.tsx`: registered route `/projects/:projectId/architecture`
- `Dashboard.tsx`: Architecture launch card in the Exploration Hub

**Critical React bug fixed:**
- D3 force simulation mutates `link.source` and `link.target` from string IDs to object references in-place
- This caused React child rendering crashes when trying to display `link.source` as text
- Fixed by introducing `getEntityId()` sanitization across all lookup keys and text interpolations

**Build result**: 0 TypeScript errors, 0 lint warnings in 10.37s production build ✅  
**Browser verification**: 0 console errors, all 5 KPI cards render, topology animates, drawer opens, all 4 tabs function ✅

---

## ❓ Your Viva Questions & Answers

**Q: What framework did you use and why?**  
A: *"React with TypeScript. React is component-based — the KPI card, the node inspector, the topology canvas are all self-contained components that can be tested and developed independently. TypeScript adds compile-time type checking so if the backend changes a response format and I haven't updated the TypeScript interface, the build fails — not silently at runtime in production."*

**Q: How does the force-directed graph work?**  
A: *"We use `react-force-graph-2d` which runs a D3-based physics simulation. Nodes are particles that repel each other, and edges are springs that pull connected nodes together. The simulation runs until it reaches equilibrium — the layout you see reflects the actual connectivity of the codebase. Highly connected nodes cluster together, isolated ones spread out."*

**Q: How do the animated particles work?**  
A: *"The particle animation is a built-in feature of `react-force-graph-2d`. We configure the density, speed, and color per link type. COMMUNICATES_WITH links get 5 high-density particles — they look like data flowing between services. CONTAINS links get no particles — they're structural, not communication. This visual distinction makes the type of relationship immediately obvious."*

**Q: Why did you choose a dark glassmorphic design?**  
A: *"Code analysis tools are used by developers — a dark interface reduces eye strain during long sessions. Glassmorphic design — frosted glass panels with blur — creates depth without clutter. The design communicates that this is a professional, technical tool, not a consumer app. The glow effects on nodes make the graph feel alive rather than static."*

**Q: How did you handle the D3 mutation bug?**  
A: *"D3's force simulation mutates `link.source` and `link.target` from string IDs to object references during simulation. When React tried to render these as text — for edge labels or the drawer — it received an object where it expected a string, causing a child rendering crash. I introduced a `getEntityId()` helper that checks the type of the value: if it's already a string, use it directly; if it's an object, extract the ID property. Applied consistently across all 23 places these values appear."*

**Q: What is Vite and why use it over Create React App?**  
A: *"Vite is a modern build tool that uses native ES modules during development — no bundling step, so hot reload is near-instant. Create React App uses webpack, which re-bundles on every change and can be slow on large projects. Vite also has built-in proxy support — that's how `/api` calls are forwarded to port 8000 without CORS issues."*

**Q: How did you implement the Ask AI page without an actual AI backend?**  
A: *"The Ask AI page (`AskAI.tsx`) is a client-side explainability interface. It calls Member 3's traceability and dependency endpoints — which return structured graph traversal data — and presents that data as a conversational response. The 'AI' is the graph traversal intelligence. The page includes pre-packaged prompt chips for common questions and displays the evidence paths the system used to reach its answer. Full AI integration with a language model is planned for Phase 5."*

**Q: What's the most complex component you built?**  
A: *"`Architecture.tsx` — it's 600+ lines integrating the topology canvas, four tabs, the dependency drawer, the inter-service drawer, the KPI cards, all the API calls, TypeScript type safety across 6 different response models, D3 mutation handling, and the custom canvas rendering logic for 4 completely different node visual styles. It's the most technically complete thing I've built."*

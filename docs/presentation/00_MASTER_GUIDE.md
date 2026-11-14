# 🎯 GraphTrace AI — Team Presentation Master Guide

> **Event**: Group Project Demonstration + Viva  
> **Duration**: 10–15 minutes total  
> **Team**: Member 1 (Artifact Intelligence) · Member 2 (Knowledge Graph Engine) · Member 3 (FastAPI Backend) · Member 4 (Frontend & Visualization)  
> **Current Status**: Phase 4 — Architecture Intelligence ✅ COMPLETE

---

## ⏱️ Time Budget — 13 Minutes

| Slot | Speaker | Section | Duration |
|------|---------|---------|----------|
| 0:00–1:30 | **Member 1** | Opening — The problem, the idea, our solution | 1.5 min |
| 1:30–4:00 | **Member 1** | Live Demo Part 1 — Upload, Analyze, Graph appears | 2.5 min |
| 4:00–6:30 | **Member 2** | Graph Explorer + Graph Database deep dive | 2.5 min |
| 6:30–9:00 | **Member 3** | Backend API, integration story, traceability engine | 2.5 min |
| 9:00–11:30 | **Member 4** | Architecture Explorer — the full visual showcase | 2.5 min |
| 11:30–13:00 | **All** | Phases completed, what's next, closing | 1.5 min |

---

## 🔊 Smooth Handoff Lines (memorize these)

| From → To | Exact line to say |
|-----------|-------------------|
| **M1 → M2** | *"The analysis is done and the graph is built. Let me hand it to [M2] who will show you what the system actually knows and how it's stored."* |
| **M2 → M3** | *"So that's the data layer. But what ties everything together is the backend intelligence — [M3] will walk you through how it all connects."* |
| **M3 → M4** | *"And all of this intelligence is wrapped in a polished interface that [M4] built. Let me hand it over."* |
| **M4 → Close** | *"That's the full system. Let's talk about where we are and where we're heading."* |

---

## 🖥️ Pre-Presentation Setup Checklist

> Do this **before** anyone enters the room.

- [ ] Run `launch.bat` from the project root — wait for both servers to confirm ready
- [ ] Open browser at `http://localhost:5173` — confirm the home screen loads
- [ ] Delete existing test projects using the **🗑️ Reset** button — start completely fresh
- [ ] Keep `sample_project.zip` on the Desktop for quick drag-and-drop
- [ ] Also keep the ecommerce-platform demo project data in `.data/` as a backup
- [ ] Set browser zoom to **110%** so text is readable from the back
- [ ] Turn off all browser notifications and OS notifications
- [ ] Close all other applications
- [ ] Have the backend docs tab at `http://localhost:8000/docs` ready but minimized

---

## 🔥 Project Pitch — One Sentence (all 4 members should know this)

> *"GraphTrace AI takes any codebase as a ZIP file and instantly produces an interactive visual map of its architecture — components, services, technologies, dependencies, and how they all connect — stored as a knowledge graph."*

---

## 📌 Key Project Numbers (cite these in viva with confidence)

| Metric | Value |
|--------|-------|
| Phases completed | Phase 1 ✅ Phase 2 ✅ Phase 3 ✅ **Phase 4 ✅** |
| Backend tests passing | **101 tests, 0 failures** |
| Phase 1 test count | 81 passed (25 M1 + 20 M1→M3 + 33 API + 3 Neo4j adapter) |
| Phase 4 additional tests | 20 new tests (M2 Phase 4 + M3 Phase 4) |
| API endpoints | 13 REST endpoints |
| Node types supported | PROJECT, FILE, PACKAGE, CLASS, FUNCTION, METHOD, REQUIREMENT, DOCUMENT, SYSTEM, COMPONENT, SERVICE, TECHNOLOGY |
| Relationship types | 15+ (CONTAINS, CALLS, IMPORTS, DEPENDS_ON, COMMUNICATES_WITH, EXPOSES, USES, PART_OF, TESTED_BY, …) |
| Frontend pages | Home, Dashboard, Graph Explorer, Traceability, Dependencies, Ask AI, Architecture Explorer |
| Languages parsed | Python, JavaScript, TypeScript |

---

## ❓ Universal Viva Questions (every member should know these answers)

**Q: What is a knowledge graph?**  
A: *"A knowledge graph is a database where data is stored as nodes (entities) and edges (relationships) rather than tables. It's ideal for code because code is naturally a network — files import other files, functions call functions, services depend on services."*

**Q: Why not just use GitHub's built-in tools?**  
A: *"GitHub shows you code but it doesn't understand architecture. GraphTrace AI reads the entire structure and shows you a visual map of how every piece connects — including which requirements map to which code, and which services talk to each other."*

**Q: What's the most technically impressive part of this project?**  
A: *"Phase 4 — the architecture synthesizer. If a project was uploaded before our architecture parser existed, the system dynamically reconstructs the architecture from whatever data is already stored. It never shows an empty result."*

**Q: How did 4 members avoid breaking each other's code?**  
A: *"We defined a shared data contract — `ArtifactGraph` in `models.py` — on day one. Every member codes to this interface. If anyone breaks the contract, 101 tests fail immediately. That's our safety net."*

**Q: What problem does this actually solve in the real world?**  
A: *"When a new developer joins a team, understanding an unfamiliar codebase takes days. With GraphTrace AI, you upload it and get an architecture map in seconds. Onboarding becomes visual and instant."*

---

## 🚨 Contingency Table

| Problem | Immediate fix |
|---------|--------------|
| Backend not responding | Re-run `launch.bat`; check port 8000 in Task Manager |
| Frontend blank page | Hard-refresh `Ctrl+Shift+R`; check port 5173 |
| Upload fails mid-demo | *"Let me show you using our pre-loaded project"* → navigate to ecommerce-platform |
| Architecture shows 0 nodes | Click "Architecture" tab again — the synthesizer runs on first access |
| Graph explorer too slow | Use the node type filters to reduce visible nodes |
| Neo4j errors in logs | These are safe to ignore — we run in local storage mode |

---

## ✅ Each Member's Single Most Important Thing

| Member | The one thing to nail |
|--------|----------------------|
| **M1** | The upload → analyze moment must visually complete on screen. Practice 3×. |
| **M2** | Explain graph visually: *"dots are entities, lines are relationships."* Don't use jargon. |
| **M3** | Show the `/docs` swagger page briefly — it makes the API tangible without explaining all endpoints. |
| **M4** | Let the topology canvas render fully before talking. The visuals are the argument. |

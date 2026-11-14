# 🎯 GraphTrace AI — Team Presentation Master Guide

> **Event**: Group Project Demonstration + Viva  
> **Duration**: 10–15 minutes total  
> **Team**: 4 Members  
> **Format**: Live demo + Q&A

---

## ⏱️ Time Budget (13 minutes total)

| Slot | Who | What | Time |
|------|-----|------|------|
| 0:00 – 1:30 | **Member 1** | Opening — What problem we solved & the idea | 1.5 min |
| 1:30 – 4:30 | **Member 1** | Live Demo Part 1 — Upload + Analyze a project | 3 min |
| 4:30 – 7:00 | **Member 2** | Graph Explorer walkthrough + architecture insight | 2.5 min |
| 7:00 – 9:30 | **Member 3** | Backend Intelligence — how the brain works | 2.5 min |
| 9:30 – 11:30 | **Member 4** | Frontend & Architecture Explorer visual walkthrough | 2 min |
| 11:30 – 13:00 | **All** | Future goals & wrap-up | 1.5 min |

---

## 🗣️ Speaking Handoff Script

Use these exact phrases to smoothly hand off between members:

- **M1 → M2**: *"Now that the project is analyzed and the graph is built, let me hand it over to [M2 name] who'll show you what the system actually knows."*
- **M2 → M3**: *"The visualization is powered by a smart backend — [M3 name] will walk you through the intelligence behind it."*
- **M3 → M4**: *"And all of this is wrapped in a polished interface — [M4 name] will show you the architecture explorer."*
- **M4 → Close**: *"Before we wrap up, let's talk about where this is headed."*

---

## 🖥️ Demo Setup Checklist (Do BEFORE presentation)

- [ ] Start the backend server: open terminal in project root → run `launch.bat`
- [ ] Open browser at `http://localhost:5173`
- [ ] Delete any existing test projects using the **Reset (🗑️)** button — start fresh
- [ ] Have your demo ZIP file ready (use `sample_project.zip` from the `backend/` folder)
- [ ] Zoom browser to 110% for readability
- [ ] Close all other tabs and notifications

---

## 🔥 One-Line Project Pitch (memorize this)

> *"GraphTrace AI lets you drop in any codebase as a ZIP and instantly see its architecture — components, services, technologies, and how they connect — through an interactive visual graph."*

---

## 🧠 Key Facts to Remember

| Topic | What to Say |
|-------|-------------|
| What is it? | An AI-powered code analysis and visualization tool |
| What does it do? | Reads a project ZIP → extracts structure → shows interactive graph |
| Tech stack | Python (FastAPI), React, Neo4j (graph database) |
| Total tests | 101 tests passing ✅ |
| Phase completed | Phase 1 (Core + Architecture Intelligence) |
| Lines of code | ~5,000+ across backend + frontend |

---

## ❓ Common Viva Questions & Suggested Answers

**Q: Why did you use a graph database?**  
A: "Code is naturally a graph — files contain classes, classes call each other, services depend on services. A graph database like Neo4j makes these relationships first-class citizens you can query and traverse."

**Q: What problem does this solve?**  
A: "When you join a new project or audit someone else's code, understanding the structure takes days. GraphTrace AI does it in seconds and shows you a visual map."

**Q: How does the architecture detection work?**  
A: "Member 1's parser reads folder names, config files, and code patterns to identify components and services. Member 3 exposes this via API, and Member 4 renders it as an interactive canvas."

**Q: What's next for the project?**  
A: "Phase 2 targets AI-powered semantic search — asking questions about the codebase in plain English. Phase 3 adds requirement traceability."

**Q: Did you use any AI/ML?**  
A: "Phase 1 uses smart static analysis (rule-based). The AI layer is planned for Phase 2 — semantic embeddings and natural language querying."

**Q: How do you handle large projects?**  
A: "The parser skips non-essential folders like `node_modules` and `venv`. Batch graph writes are used for performance. Scaling is a Phase 3 concern."

---

## ✅ Each Member's "One Thing to Nail"

| Member | The one thing |
|--------|--------------|
| M1 | The live upload → analyze → graph moment must work. Practice it 3x. |
| M2 | Explain the graph in plain English. "These dots are files, these lines are relationships." |
| M3 | Don't go too deep into API endpoints. Show confidence, stay high-level. |
| M4 | Let the visuals speak. Click around — the UI is your strongest argument. |

---

## 🚨 Contingency Plans

| Problem | Fix |
|---------|-----|
| Backend not starting | Run `launch.bat` again; check port 8000 is free |
| Frontend blank page | Hard-refresh (Ctrl+Shift+R); check port 5173 |
| Upload fails | Use the pre-loaded demo project (ecommerce-platform already in the system) |
| Graph doesn't render | Click "Reset Zoom" on the graph page |
| Neo4j errors | We use LOCAL storage mode — Neo4j is optional, ignore those errors |

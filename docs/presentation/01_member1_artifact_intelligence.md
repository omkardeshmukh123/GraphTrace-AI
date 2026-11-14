# 🧠 Member 1 — Artifact Intelligence
## Presentation Script & Speaking Notes

> **Role**: Project Lead / Demo Driver  
> **Time Slot**: 0:00 – 4:30 (first ~4.5 minutes)  
> **You own**: The opening pitch + live upload demo

---

## 🎤 Your Opening (1.5 min) — Memorize this flow

### Line 1 — Hook
> *"Imagine joining a new software project. You have thousands of files in front of you. Where do you even start?"*

*(pause 2 seconds)*

### Line 2 — Problem
> *"Every developer has been there. Understanding someone else's code takes days, sometimes weeks. We built GraphTrace AI to change that."*

### Line 3 — Solution
> *"GraphTrace AI takes any project — just as a ZIP file — and gives you back a live, interactive map of its architecture. Files, classes, services, how they talk to each other — all in seconds."*

### Line 4 — Team Intro
> *"I'm [your name]. I built the intelligence layer that reads and understands the code — called Artifact Intelligence. My teammates built the graph database layer, the backend API, and the visual interface. Let me show you how it works."*

---

## 🖥️ Live Demo (3 min) — Step by Step

### Step 1 — Show the home screen (30 sec)
- Point to the project cards
- Say: *"This is our dashboard. Each card is a project that's been analyzed. You can see the stats right there — nodes, relationships, status."*

### Step 2 — Click Upload (30 sec)
- Click the **"Upload Project"** button (top right)
- Say: *"To analyze a new project, you just upload a ZIP file. No config, no setup — just the code."*
- Drag in `sample_project.zip`

### Step 3 — Watch Analysis (60 sec)
- Say: *"Behind the scenes, my module — Artifact Intelligence — is scanning every file. It reads the README, identifies folders, finds classes and functions in Python and JavaScript, and detects the architectural structure — things like frontend, backend, API layer."*
- When it completes: *"And there it is — analyzed in under 2 seconds."*

### Step 4 — Show the new project card (30 sec)
- Point to the stats: *"Already we can see: X nodes, Y relationships detected."*
- Click **"View Dashboard"**
- Say: *"Let's hand this over to [M2 name] to explore what we just discovered."*

---

## 📌 Your Technical Contribution (know this for viva)

**What you built:** `artifact_intelligence/` — the parsing engine

| What it does | Plain English version |
|---|---|
| Reads ZIP files | Safely extracts uploaded projects |
| Parses README | Finds project name, description, technologies mentioned |
| Parses Python & JS code | Finds all classes, functions, methods and their relationships |
| Detects architecture | Identifies frontend/backend/API/service layers from folder names and config files |
| Outputs a graph contract | Packages everything as a standard data format for the rest of the system |

**Tests you wrote:** 25 unit tests — all passing ✅

---

## ❓ Viva Questions You'll Likely Get

**Q: How does Artifact Intelligence actually read the code?**  
A: "It uses pattern matching — regular expressions — to scan through files. For Python it finds `class MyClass:` and `def my_function():`. For JavaScript it finds ES6 class declarations and functions. It's similar to how IDEs do syntax highlighting but for structure extraction."

**Q: What if someone uploads a project in a language you don't support?**  
A: "Phase 1 supports Python and JavaScript/TypeScript. The architecture detection still works since it uses folder names and config files, not just code. Full multi-language support is Phase 2."

**Q: Why regex and not a proper parser?**  
A: "Regex is fast, has zero dependencies, and was sufficient to prove the concept. Phase 2 will upgrade to tree-sitter — a real syntax tree parser — for more precise extraction."

---

## 🧘 Calm-Down Reminder
If the demo upload fails: *"Let me use our pre-loaded demo project to show you the full experience"* → navigate to the ecommerce-platform project. Never panic, just pivot.

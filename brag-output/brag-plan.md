# GraphTrace AI — Brag Plan

## Invocation
`/brag` (no flags — defaults applied)

---

## Planning Rubric

**1. What is the app?**
GraphTrace AI takes a zipped software repository and builds a live, queryable knowledge graph from it — parsing classes, functions, requirements, and documentation into typed nodes and typed edges, then letting engineers explore dependencies, trace requirements to code, and interrogate the architecture visually.

**2. Most impressive / funniest claim?**
"Drop any codebase in. Under 1.2 seconds later, you can click any requirement and trace it to the exact line of code that implements it."

**3. Visual hook?**
The force-directed graph explorer: glowing colored nodes (indigo classes, teal files, pink functions, amber methods) drifting and snapping against a near-black obsidian background. The brand gradient on titles and edge glows.

**4. What to show from actual UI?**
- Home hero headline
- Upload modal: drag a ZIP ? progress bar
- Graph Explorer: force-directed colored nodes for the demo project
- Traceability view: requirement node ? highlighted path ? code node

**5. Shortest satisfying video?**
20 seconds.

**6. Tone?**
- **Preset:** `polished`
- **Creative direction:** "Premium developer intelligence platform — the VS Code of software archaeology."

**7. Audio?**
Deep ambient tech bed, dark and spacious. Clean UI SFX when graph materializes. Subtle node-arrival ticks. Audio-reactive treatment: very restrained.

**8. Share caption?**
"Drop in any codebase. GraphTrace AI builds a live knowledge graph of every class, function, dependency, and requirement — and shows you exactly why anything calls anything else."

**9. User flow worth showing?**
1. Upload ZIP ? progress bar fills
2. Graph appears — nodes radiate outward by type
3. Click requirement ? path lights up to code

---

## Tone: `polished`
Mixed case, light-medium weight, slow crossfades (0.6-0.8s), one idea per scene, confidence through restraint.

---

## Storyboard

**Format:** Landscape (16:9)  
**Duration:** 20 seconds

### Scene 1 — Hook (0:00–0:02) — 2s
- Pure obsidian black
- Single centered line fades in: *"What does this code actually do?"*
- Hold. Silence.
- Crossfade 0.6s

### Scene 2 — Upload (0:02–0:05) — 3s
- Upload modal, ZIP icon slides in, border glows indigo
- Progress bar fills in ~1s
- Check-mark + `< 1.2s` appears in JetBrains Mono
- SFX: file-drop tap + confirm tone
- Crossfade 0.6s

### Scene 3 — Graph Reveal (0:05–0:10) — 5s  CENTERPIECE
- Start: one glowing project node (#818cf8)
- Nodes radiate outward in 5-6 waves, color-coded by type
- Edges draw between them as glowing lines
- Graph settles; constellation holds
- Top-left overlay: `247 entities indexed / 189 relationships mapped` (JetBrains Mono, small)
- SFX: per-group arrival tick, very quiet
- Slide-right 0.5s

### Scene 4 — Traceability (0:10–0:15) — 5s
- Zoomed-in graph, requirement node visible (REQ-023, #f43f5e)
- Cursor clicks ? pulse ring expands
- Path lights up sequentially: REQ-023 ? AuthService ? validate_token() ? user_repository.py
- 4 hops, 0.5s each; brand gradient on lit edges; other nodes dim
- Bottom overlay: `Requirement ? Implementation / Traced in one click.`
- SFX: quiet ping per hop
- Crossfade 0.7s

### Scene 5 — Outro (0:15–0:20) — 5s
- Pure black
- `GraphTrace AI` fades in, centered, large, gradient fill
- `Explainable Software Engineering Intelligence` fades in below, small, #94a3b8
- Glow pulse expands once behind the name
- SFX: single resonant logo hit
- Hold ? fade to black

---

## Scene Duration Check
| Scene | Duration | Total |
|-------|----------|-------|
| 1 — Hook | 2s | 2s |
| 2 — Upload | 3s | 5s |
| 3 — Graph Reveal | 5s | 10s |
| 4 — Traceability | 5s | 15s |
| 5 — Outro | 5s | 20s |

Total: 20 seconds ?

---

## Color Palette
| Role | Value |
|------|-------|
| Background | `#080a0f` |
| Primary accent | `#6366f1` |
| Brand gradient | `135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%` |
| Text primary | `#f8fafc` |
| Text secondary | `#94a3b8` |
| Node: class | `#34d399` |
| Node: function | `#f472b6` |
| Node: file | `#38bdf8` |
| Node: method | `#fb923c` |
| Node: requirement | `#f43f5e` |
| Node: project | `#818cf8` |
| Border glow | `rgba(99, 102, 241, 0.4)` |

## Fonts
| Role | Family | Weight |
|------|--------|--------|
| Display | Plus Jakarta Sans | 700, 800 |
| Body | Plus Jakarta Sans | 400, 500 |
| Metrics/Code | JetBrains Mono | 400, 500 |

Google Fonts: `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap`

---

## Music Cue Guidance
- Track: Ambient tech bed — slow, dark, spacious. Low-frequency pulse, subtle high shimmer.
- Audio-reactive: very restrained — graph node glow breathes with RMS, logo glow coincides with swell
- SFX intent: file-drop tap, confirm tone, node-arrival ticks (x6), path-hop pings (x4), resonant logo hit

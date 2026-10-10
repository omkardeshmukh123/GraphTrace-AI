# GraphTrace AI — Composition Brief

## What this is
A 20-second polished brag video for GraphTrace AI — an Explainable Software Engineering Intelligence Platform that turns a zipped software repository into an interactive, queryable knowledge graph.

## Product source material
- **README headline:** "An Explainable Software Engineering Intelligence Platform based on a Software Knowledge Graph."
- **Home hero:** "Deep Architectural Understanding & Explainable Intelligence"
- **Home hero desc:** "GraphTrace AI connects source code, AST entities, requirements, and documentation into a unified, queryable software knowledge graph with real-time traceability and dependency analysis."
- **Analysis speed (from UI):** `< 1.2s` (multi-language AST parser)
- **Test status (from README):** 45/45 tests passing
- **Routes:** Home, Dashboard, GraphExplorer, Traceability, Dependencies, AskAI
- **Real entity names from codebase:** ArtifactGraph, CodeParser, GraphStore, Neo4jStore, AuthService (from sample_project), validate_token(), user_repository.py, get_user_by_id(), REQ-001 (from sample data)

## Tone
**polished** — Mixed case, light-medium weight, generous letter-spacing, slow crossfades (0.6-0.8s), one idea per scene, confidence through restraint.

## Format
1920x1080 landscape, 20 seconds, 60fps.

## Color palette
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

## Fonts
- Display/headlines: **Plus Jakarta Sans** 700, 800
- Body/labels: **Plus Jakarta Sans** 400, 500
- Metrics/code: **JetBrains Mono** 400, 500

## Music
- Track: `assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`
- Volume: 0.28 (polished = restrained bed)
- Cue preset: `assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json`
- Tempo: 109.96 BPM

## Beat locks (3 major moments)
1. Graph constellation settles: aligned to strong cue at **8.74s** (intensity 0.99)
2. Traceability click: aligned to strong cue at **10.93s** (intensity 0.97)
3. Logo reveal: aligned to strong cue at **17.47s** (intensity 0.99)

## Scene summary

| # | Scene | Time | Key moment |
|---|-------|------|------------|
| 1 | Hook | 0-2s | "What does this code actually do?" fades in on black |
| 2 | Upload | 2-5s | ZIP drag, progress bar fills, < 1.2s confirm |
| 3 | Graph Reveal | 5-10s | Nodes radiate in 6 beat-locked waves, constellation settles |
| 4 | Traceability | 10-15s | Click REQ-023, 4-hop path lights up in brand gradient |
| 5 | Outro | 15-20s | "GraphTrace AI" in gradient, tagline, logo SFX |

## Audio-reactive treatment
Very restrained (polished tone). Center project node ring can breathe subtly with RMS. No waveform bars.

## SFX mapping
| Moment | File | Track | Volume |
|--------|------|-------|--------|
| File drop (2.1s) | interface/drop_001.ogg | 11 | 0.60 |
| Confirm (3.85s) | interface/drop_002.ogg | 12 | 0.55 |
| Node waves x6 (5.34-8.19s) | ui/click1.ogg | 13-18 | 0.35?0.22 |
| Click req (10.15s) | ui/mouseclick1.ogg | 19 | 0.65 |
| Path hops x4 (10.70-12.20s) | impact/impactGlass_light_001.ogg | 20-23 | 0.40?0.34 |
| Logo hit (17.40s) | impact/impactBell_heavy_000.ogg | 24 | 0.55 |

## What Hyperframes owns
- Exact animation timing, easing, and mechanics
- Runtime choices and linting rules
- Render workflow
- Any audio-reactive data extraction

## What /brag owns (already decided)
- Product angle, storyboard, tone, format
- Audio selection and music cue guidance
- Delivery expectations

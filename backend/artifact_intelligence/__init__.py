"""
╔══════════════════════════════════════════════════════════════════╗
║  M1 — Artifact Intelligence Module                               ║
║  Owner: Member 1                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Responsibility:                                                  ║
║    Parse raw project artifacts (ZIP, Python, JS, README) into    ║
║    a structured ArtifactData object that feeds into M2/M3.       ║
║                                                                   ║
║  Key files:                                                       ║
║    analyzer.py      — Orchestrator: combines all parsers          ║
║    zip_handler.py   — ZIP extraction & file inventory             ║
║    code_parser.py   — Extracts classes & functions (Python/JS/TS) ║
║    readme_parser.py — Extracts metadata, tech stack, sections     ║
║    models.py        — Internal Entity, Relationship, ArtifactData ║
║                                                                   ║
║  Output contract:                                                 ║
║    ArtifactData → consumed by backend/app/parsers/pipeline.py     ║
║    which converts it into the shared ArtifactGraph (see shared/)  ║
║                                                                   ║
║  Integration:                                                     ║
║    backend/app/parsers/pipeline.py implements the M3 parser       ║
║    plugin interface using this module.                            ║
╚══════════════════════════════════════════════════════════════════╝
"""

from .models import Entity, Relationship, ArtifactData
from .analyzer import ArtifactAnalyzer

__all__ = ["Entity", "Relationship", "ArtifactData", "ArtifactAnalyzer"]

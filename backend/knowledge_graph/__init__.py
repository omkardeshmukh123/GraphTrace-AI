"""
╔══════════════════════════════════════════════════════════════════╗
║  M2 — Knowledge Graph Engine                                     ║
║  Owner: Member 2                                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Responsibility:                                                  ║
║    Store and query the software knowledge graph in Neo4j.         ║
║    Provides both a standalone adapter and the M3 plugin bridge.   ║
║                                                                   ║
║  Key files:                                                       ║
║    connection.py  — Neo4j driver singleton                        ║
║    schema.py      — Constraints & indexes setup                   ║
║    builder.py     — KnowledgeGraphBuilder: writes ArtifactData    ║
║    queries.py     — GraphQueryEngine: reads graph data            ║
║    resolver.py    — Entity deduplication (MERGE-based)            ║
║    models.py      — Internal graph node/edge types                ║
║                                                                   ║
║  Standalone entry point:                                          ║
║    backend/main.py  (runs M1+M2 server on port 8001)             ║
║                                                                   ║
║  Integration with M3:                                            ║
║    backend/app/graph/builder.py implements the M3 graph_writer    ║
║    plugin interface using this module's Neo4j connection.         ║
╚══════════════════════════════════════════════════════════════════╝
"""

from .builder import KnowledgeGraphBuilder
from .queries import GraphQueryEngine
from .connection import get_driver, close_driver

__all__ = ["KnowledgeGraphBuilder", "GraphQueryEngine", "get_driver", "close_driver"]

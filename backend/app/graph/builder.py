"""
DEPRECATED SHIM — DO NOT USE DIRECTLY
======================================
This file is a backward-compatibility re-export shim.

The canonical location of the M2 → M3 Neo4j write bridge is now:
    backend/knowledge_graph/graph_writer.py

Update your imports to:
    from backend.knowledge_graph.graph_writer import write_graph
"""
import warnings

warnings.warn(
    "backend.app.graph.builder is deprecated. "
    "Import from backend.knowledge_graph.graph_writer instead.",
    DeprecationWarning,
    stacklevel=2,
)

from backend.knowledge_graph.graph_writer import write_graph  # noqa: F401, E402

__all__ = ["write_graph"]

"""
M2 — Knowledge Graph Engine
Package init: exports the primary public interface.
"""

from .builder import KnowledgeGraphBuilder
from .queries import GraphQueryEngine
from .connection import get_driver, close_driver

__all__ = ["KnowledgeGraphBuilder", "GraphQueryEngine", "get_driver", "close_driver"]

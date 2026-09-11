"""
shared/ — Cross-Member Shared Contract
=======================================
This package re-exports the ArtifactGraph data contract defined by M3 in
backend/app/models.py so that M1 and M2 can import it cleanly without
depending on the full M3 app package.

Usage in M1/M2 code:
    from backend.shared.contract import ArtifactGraph, Node, Relationship, make_node_id

The single source of truth remains backend/app/models.py — edit there, not here.
"""

from backend.app.models import (
    ArtifactGraph,
    Node,
    Relationship,
    NodeType,
    RelationshipType,
    ManualMapping,
    ProjectSummary,
    GraphView,
    DependencyView,
    PathView,
    RequirementSummary,
    TraceabilityView,
    DEPENDENCY_TYPES,
    CODE_TYPES,
    make_node_id,
)

__all__ = [
    "ArtifactGraph",
    "Node",
    "Relationship",
    "NodeType",
    "RelationshipType",
    "ManualMapping",
    "ProjectSummary",
    "GraphView",
    "DependencyView",
    "PathView",
    "RequirementSummary",
    "TraceabilityView",
    "DEPENDENCY_TYPES",
    "CODE_TYPES",
    "make_node_id",
]

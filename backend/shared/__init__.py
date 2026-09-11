"""
shared/ — Cross-Member Shared Package
======================================
Contains the shared data contract and utilities used by all members.

Members:
  M1 (artifact_intelligence/) → imports ArtifactGraph from here to produce output
  M2 (knowledge_graph/)       → imports ArtifactGraph from here to write to Neo4j
  M3 (app/)                   → defines the contract in app/models.py (source of truth)

Import cleanly:
    from backend.shared.contract import ArtifactGraph, Node, Relationship
"""

from backend.shared.contract import (
    ArtifactGraph,
    Node,
    Relationship,
    make_node_id,
)

__all__ = ["ArtifactGraph", "Node", "Relationship", "make_node_id"]

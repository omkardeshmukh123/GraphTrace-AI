"""
M1 — Artifact Intelligence — Data Models
=========================================
Defines the standard M1 → M2 contract:
  ArtifactData = { entities: [Entity], relationships: [Relationship], metadata: {} }

This is the ONLY format M2 (Knowledge Graph Engine) expects from M1.
M2 must never depend on how M1 extracted the data — only on this schema.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any


# ─── Entity Types ─────────────────────────────────────────────────────────────
class EntityType:
    """All valid node types in Phase 1 of GraphTrace AI."""
    REPOSITORY   = "REPOSITORY"
    FOLDER       = "FOLDER"
    FILE         = "FILE"
    CLASS        = "CLASS"
    FUNCTION     = "FUNCTION"
    README       = "README"


# ─── Relationship Types ───────────────────────────────────────────────────────
class RelationshipType:
    """All valid relationship types in Phase 1."""
    CONTAINS     = "CONTAINS"    # Folder→Folder, Folder→File, File→Class, Class→Function
    HAS_README   = "HAS_README"  # Repository→README
    DEFINES      = "DEFINES"     # File→Class, File→Function


# ─── Core Data Models ─────────────────────────────────────────────────────────
class Entity(BaseModel):
    """
    Represents a single node to be created in the Knowledge Graph.

    id          — unique stable identifier, e.g. "class:src/auth.py:AuthService"
    type        — one of EntityType constants
    name        — human-readable short name, e.g. "AuthService"
    properties  — additional metadata (language, path, description, line_number, etc.)
    """
    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Entity(id={self.id!r}, type={self.type}, name={self.name!r})"


class Relationship(BaseModel):
    """
    Represents a directed edge between two entities.

    source      — id of the source entity
    type        — one of RelationshipType constants
    target      — id of the target entity
    properties  — additional metadata (e.g. weight, confidence)
    """
    source: str
    type: str
    target: str
    properties: dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Relationship({self.source!r} -[{self.type}]-> {self.target!r})"


class ArtifactData(BaseModel):
    """
    The complete M1 output — everything M2 needs to build the Knowledge Graph.

    entities        — all nodes extracted from the project
    relationships   — all directed edges between those nodes
    metadata        — project-level info (name, language counts, file counts, etc.)
    """
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def summary(self) -> str:
        entity_counts: dict[str, int] = {}
        for e in self.entities:
            entity_counts[e.type] = entity_counts.get(e.type, 0) + 1
        return (
            f"ArtifactData: {len(self.entities)} entities, "
            f"{len(self.relationships)} relationships | {entity_counts}"
        )

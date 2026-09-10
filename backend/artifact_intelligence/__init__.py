"""
M1 — Artifact Intelligence
Package init: exports the primary public interface.
"""

from .models import Entity, Relationship, ArtifactData
from .analyzer import ArtifactAnalyzer

__all__ = ["Entity", "Relationship", "ArtifactData", "ArtifactAnalyzer"]

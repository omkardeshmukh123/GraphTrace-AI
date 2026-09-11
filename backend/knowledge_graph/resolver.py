"""
M2 — Knowledge Graph Engine — Entity Resolver
===============================================
Prevents duplicate nodes in the graph when:
  - The same project is analyzed multiple times
  - The same entity appears in multiple artifact sources (code + docs + tests)

Phase 1 strategy: MERGE on `id` (already the uniqueness constraint key).
  - If node exists → SET new properties (update)
  - If node doesn't exist → CREATE it

Phase 3+ enhancement: cross-artifact name matching
  (e.g., "AuthService" in code matches "AuthService" in README)

This module is intentionally kept simple for Phase 1.
The builder calls resolve() before every node write.
"""

from neo4j import Session
from .models import NodeLabel


class EntityResolver:
    """
    Checks for existing nodes by `id` before creation.
    Currently wraps MERGE semantics (Neo4j handles deduplication natively).

    The resolver's role will grow significantly in Phase 3
    when cross-artifact entity linking is introduced.
    """

    def resolve_entity_id(self, entity_id: str, session: Session) -> bool:
        """
        Check if a node with the given id already exists in the graph.
        Returns True if it exists, False if it's new.
        """
        result = session.run(
            "MATCH (n {id: $id}) RETURN count(n) AS cnt",
            id=entity_id,
        )
        record = result.single()
        return record and record["cnt"] > 0

    def normalize_entity_id(self, entity_id: str) -> str:
        """
        Normalize an entity id for consistent matching.
        Phase 1: lowercase + strip whitespace.
        """
        return entity_id.strip().lower()

    def get_or_suggest_canonical_id(
        self,
        entity_name: str,
        entity_type: str,
        session: Session,
    ) -> str | None:
        """
        Phase 1: Not yet implemented — returns None.
        Phase 3+: Will search for existing nodes with same name + type
                  across different artifact sources (cross-artifact linking).
        """
        return None

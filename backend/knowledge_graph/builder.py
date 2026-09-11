"""
M2 — Knowledge Graph Engine — Graph Builder
=============================================
Takes M1's ArtifactData and writes it to Neo4j.

Pipeline per entity:
  1. Map M1 EntityType → Neo4j NodeLabel
  2. MERGE node by `id` (resolver handles dedup)
  3. SET all properties

Pipeline per relationship:
  1. Map M1 RelationshipType → Neo4j RelType
  2. MERGE relationship by (source_id, rel_type, target_id)

Uses batch writes (unwind) for performance:
  - All nodes in one query per label type
  - All relationships in one query per rel type

Returns BuildResult with counts for the API response.
"""

from dataclasses import dataclass, field
from neo4j import Driver

from artifact_intelligence.models import ArtifactData, Entity, Relationship
from .models import NodeLabel, RelType
from .connection import get_driver


@dataclass
class BuildResult:
    """Summary of what was written to Neo4j."""
    project_id: str
    nodes_created: int = 0
    nodes_updated: int = 0
    relationships_created: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "nodes_created": self.nodes_created,
            "nodes_updated": self.nodes_updated,
            "relationships_created": self.relationships_created,
            "success": self.success,
            "errors": self.errors,
        }


class KnowledgeGraphBuilder:
    """
    Converts ArtifactData (M1 output) into Neo4j nodes and relationships.
    """

    def __init__(self, driver: Driver | None = None):
        self._driver = driver or get_driver()

    def build(self, artifact_data: ArtifactData) -> BuildResult:
        """
        Main entry point: write all entities and relationships to Neo4j.
        """
        project_id = artifact_data.metadata.get("project_id", "unknown")
        result = BuildResult(project_id=project_id)

        try:
            with self._driver.session() as session:
                # ── 1. Write nodes grouped by label ───────────────────────
                nodes_by_label = self._group_entities_by_label(artifact_data.entities)
                for label, entities in nodes_by_label.items():
                    created, updated = self._merge_nodes(session, label, entities)
                    result.nodes_created += created
                    result.nodes_updated += updated

                # ── 2. Write relationships grouped by type ─────────────────
                rels_by_type = self._group_rels_by_type(artifact_data.relationships)
                for rel_type, rels in rels_by_type.items():
                    created = self._merge_relationships(session, rel_type, rels)
                    result.relationships_created += created

        except Exception as exc:
            result.errors.append(str(exc))
            print(f"[M2 Builder] ERROR: {exc}")

        print(
            f"[M2 Builder] Built graph for project {project_id}: "
            f"{result.nodes_created} nodes created, "
            f"{result.nodes_updated} updated, "
            f"{result.relationships_created} relationships created."
        )
        return result

    # ─── Node writing ─────────────────────────────────────────────────────────

    def _merge_nodes(
        self, session, label: str, entities: list[Entity]
    ) -> tuple[int, int]:
        """
        Batch MERGE all nodes of the same label.
        Returns (created_count, updated_count).
        """
        if not entities:
            return 0, 0

        # Build batch list for UNWIND
        batch = [
            {
                "id": e.id,
                "name": e.name,
                **{k: v for k, v in e.properties.items() if _is_neo4j_safe(v)},
            }
            for e in entities
        ]

        query = f"""
        UNWIND $batch AS row
        MERGE (n:{label} {{id: row.id}})
        ON CREATE SET n = row, n.created_at = timestamp()
        ON MATCH  SET n += row, n.updated_at = timestamp()
        RETURN
            sum(CASE WHEN n.created_at = timestamp() THEN 1 ELSE 0 END) AS created,
            sum(CASE WHEN n.updated_at = timestamp() THEN 1 ELSE 0 END) AS updated
        """

        result = session.run(query, batch=batch)
        record = result.single()
        created = record["created"] if record else 0
        updated = record["updated"] if record else 0
        return created, updated

    # ─── Relationship writing ─────────────────────────────────────────────────

    def _merge_relationships(
        self, session, rel_type: str, rels: list[Relationship]
    ) -> int:
        """
        Batch MERGE all relationships of the same type.
        Returns count of relationships merged.
        """
        if not rels:
            return 0

        batch = [
            {
                "source_id": r.source,
                "target_id": r.target,
                **{k: v for k, v in r.properties.items() if _is_neo4j_safe(v)},
            }
            for r in rels
        ]

        query = f"""
        UNWIND $batch AS row
        MATCH (a {{id: row.source_id}})
        MATCH (b {{id: row.target_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        ON CREATE SET r.created_at = timestamp()
        RETURN count(r) AS cnt
        """

        result = session.run(query, batch=batch)
        record = result.single()
        return record["cnt"] if record else 0

    # ─── Grouping helpers ─────────────────────────────────────────────────────

    def _group_entities_by_label(
        self, entities: list[Entity]
    ) -> dict[str, list[Entity]]:
        """Group entities by their Neo4j label."""
        groups: dict[str, list[Entity]] = {}
        for entity in entities:
            label = NodeLabel.FROM_ENTITY_TYPE.get(entity.type, entity.type.capitalize())
            groups.setdefault(label, []).append(entity)
        return groups

    def _group_rels_by_type(
        self, relationships: list[Relationship]
    ) -> dict[str, list[Relationship]]:
        """Group relationships by their Neo4j relationship type."""
        groups: dict[str, list[Relationship]] = {}
        for rel in relationships:
            rel_type = RelType.FROM_REL_TYPE.get(rel.type, rel.type)
            groups.setdefault(rel_type, []).append(rel)
        return groups


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_neo4j_safe(value) -> bool:
    """
    Neo4j properties must be primitive types or lists of primitives.
    Filter out nested dicts, None values, etc.
    """
    if value is None:
        return False
    if isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(isinstance(v, (str, int, float, bool)) for v in value)
    return False

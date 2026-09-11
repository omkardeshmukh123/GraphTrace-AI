"""
M2 → M3 Neo4j Graph Writer
============================
Implements the graph_writer interface defined in docs/INTEGRATION.md.

M3's Neo4jGraphStore calls this via the plugin system:
    GRAPHTRACE_GRAPH_WRITER=backend.app.graph.builder:write_graph

Contract (from INTEGRATION.md):
  - Every node gets the Entity label + project_id, id, type, name, properties_json
  - Extra labels (CLASS, FUNCTION, etc.) are optional
  - Relationship types match the contract enum
  - All writes in a single execute_write transaction
  - PROJECT node created first; reject with AppError(409) if project already exists
  - Failed writes must leave no partial graph (transaction rollback)
  - Create uniqueness constraint before first write

Neo4j schema (from INTEGRATION.md):
    CREATE CONSTRAINT entity_identity IF NOT EXISTS
    FOR (n:Entity) REQUIRE (n.project_id, n.id) IS UNIQUE;
"""

import json
import logging
from typing import Any

from backend.app.errors import AppError
from backend.app.models import ArtifactGraph

logger = logging.getLogger(__name__)

# Whitelist of allowed relationship types (prevents Cypher injection)
_ALLOWED_REL_TYPES = {
    "CONTAINS", "IMPORTS", "CALLS", "EXTENDS", "IMPLEMENTS",
    "DEPENDS_ON", "IMPLEMENTED_BY", "DOCUMENTED_BY", "USES", "PART_OF",
}

# Optional extra labels for richer Neo4j schema
_EXTRA_LABELS: dict[str, str] = {
    "FILE":        "File",
    "CLASS":       "Class",
    "FUNCTION":    "Function",
    "METHOD":      "Method",
    "PACKAGE":     "Package",
    "MODULE":      "Module",
    "REQUIREMENT": "Requirement",
    "DOCUMENT":    "Document",
    "TECHNOLOGY":  "Technology",
    "PROJECT":     "Project",
}


def write_graph(*, graph: ArtifactGraph, driver, database: str) -> None:
    """
    Write the entire ArtifactGraph to Neo4j in a single transaction.
    Called by M3's Neo4jGraphStore.save().

    Raises:
        AppError(409) — if the project already exists
        AppError(500) — on any other write failure (triggers transaction rollback)
    """
    _ensure_schema(driver, database)

    with driver.session(database=database) as session:
        session.execute_write(_write_transaction, graph)

    logger.info(
        "Wrote project %s: %d nodes, %d relationships",
        graph.project_id, len(graph.nodes), len(graph.relationships),
    )


def _ensure_schema(driver, database: str) -> None:
    """
    Create the uniqueness constraint required by M3's read adapter.
    Idempotent — uses IF NOT EXISTS.
    """
    with driver.session(database=database) as session:
        session.run(
            """
            CREATE CONSTRAINT entity_identity IF NOT EXISTS
            FOR (n:Entity) REQUIRE (n.project_id, n.id) IS UNIQUE
            """
        )


def _write_transaction(tx, graph: ArtifactGraph) -> None:
    """
    All graph writes inside a single Neo4j transaction.
    On any failure, Neo4j rolls back — no partial graphs.
    """
    project_id = graph.project_id

    # ── 1. Check for existing project (reject duplicates) ─────────────────
    existing = tx.run(
        "MATCH (n:Entity {project_id: $project_id, id: $project_id}) RETURN count(n) AS cnt",
        project_id=project_id,
    ).single()

    if existing and existing["cnt"] > 0:
        raise AppError(409, "project_exists", "Project already exists. Use a new project ID.")

    # ── 2. Find and create the PROJECT node first ──────────────────────────
    project_node = next(
        (n for n in graph.nodes if n.id == graph.project_id), None
    )
    if project_node is None:
        raise AppError(500, "missing_project_node", "ArtifactGraph is missing its PROJECT node.")

    _create_node(tx, project_node, project_id)

    # ── 3. Create all remaining nodes in batches ───────────────────────────
    other_nodes = [n for n in graph.nodes if n.id != project_id]
    batch_size = 200
    for i in range(0, len(other_nodes), batch_size):
        batch = other_nodes[i : i + batch_size]
        _create_nodes_batch(tx, batch, project_id)

    # ── 4. Create all relationships in batches ─────────────────────────────
    for i in range(0, len(graph.relationships), batch_size):
        batch = graph.relationships[i : i + batch_size]
        _create_relationships_batch(tx, batch, project_id)


def _create_node(tx, node, project_id: str) -> None:
    """Create a single node (used for the PROJECT node)."""
    extra_label = _EXTRA_LABELS.get(node.type, "")
    label_clause = f":Entity:{extra_label}" if extra_label else ":Entity"

    tx.run(
        f"""
        CREATE (n{label_clause} {{
            project_id: $project_id,
            id: $id,
            type: $type,
            name: $name,
            properties_json: $properties_json
        }})
        """,
        project_id=project_id,
        id=node.id,
        type=node.type,
        name=node.name,
        properties_json=json.dumps(dict(node.properties)),
    )


def _create_nodes_batch(tx, nodes: list, project_id: str) -> None:
    """Batch-create nodes using UNWIND for performance."""
    if not nodes:
        return

    # Group by type to apply correct extra labels
    groups: dict[str, list] = {}
    for node in nodes:
        groups.setdefault(node.type, []).append(node)

    for node_type, group in groups.items():
        extra_label = _EXTRA_LABELS.get(node_type, "")
        label_clause = f":Entity:{extra_label}" if extra_label else ":Entity"

        batch = [
            {
                "project_id": project_id,
                "id": n.id,
                "type": n.type,
                "name": n.name,
                "properties_json": json.dumps(dict(n.properties)),
            }
            for n in group
        ]

        tx.run(
            f"""
            UNWIND $batch AS row
            CREATE (n{label_clause} {{
                project_id: row.project_id,
                id: row.id,
                type: row.type,
                name: row.name,
                properties_json: row.properties_json
            }})
            """,
            batch=batch,
        )


def _create_relationships_batch(tx, relationships: list, project_id: str) -> None:
    """Batch-create relationships, grouped by type."""
    if not relationships:
        return

    # Group by relationship type for safe Cypher interpolation
    groups: dict[str, list] = {}
    for rel in relationships:
        if rel.type not in _ALLOWED_REL_TYPES:
            logger.warning("Skipping disallowed relationship type: %s", rel.type)
            continue
        groups.setdefault(rel.type, []).append(rel)

    for rel_type, group in groups.items():
        batch = [
            {
                "source_id": r.source,
                "target_id": r.target,
                "properties_json": json.dumps(dict(r.properties)),
            }
            for r in group
        ]

        # rel_type is safe — we checked against _ALLOWED_REL_TYPES whitelist
        tx.run(
            f"""
            UNWIND $batch AS row
            MATCH (a:Entity {{project_id: $project_id, id: row.source_id}})
            MATCH (b:Entity {{project_id: $project_id, id: row.target_id}})
            CREATE (a)-[r:{rel_type} {{properties_json: row.properties_json}}]->(b)
            """,
            batch=batch,
            project_id=project_id,
        )

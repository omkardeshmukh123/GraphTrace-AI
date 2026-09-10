"""
M2 — Knowledge Graph Engine — Graph Query Engine
==================================================
Provides clean graph query functions for M3 (Intelligence & Reasoning Engine).

M3 must NEVER write raw Cypher queries.
M3 must NEVER import Neo4j directly.
M3 uses only these functions — this is the M2→M3 interface contract.

Phase 1 query functions:
  get_graph_data(project_id)   → all nodes + relationships for visualization
  get_all_nodes(project_id)    → list of all nodes (with properties)
  get_node(entity_id)          → single node detail
  get_children(entity_id)      → nodes connected via CONTAINS
  get_stats(project_id)        → count of nodes by type
  get_project_tree(project_id) → hierarchy starting from Repository node
"""

from neo4j import Driver
from .connection import get_driver


class GraphQueryEngine:
    """
    All graph query operations for Phase 1.
    Returns plain Python dicts — no Neo4j types exposed to callers.
    """

    def __init__(self, driver: Driver | None = None):
        self._driver = driver or get_driver()

    # ─── Primary visualization query ─────────────────────────────────────────

    def get_graph_data(self, project_id: str) -> dict:
        """
        Return all nodes and relationships for a project.
        Used by M4 (Frontend) to render the interactive graph.

        Returns:
            {
              "nodes": [{ "id", "label", "name", "type", ...properties }],
              "edges": [{ "source", "target", "type" }]
            }
        """
        with self._driver.session() as session:
            # All nodes for this project
            nodes_result = session.run(
                """
                MATCH (n)
                WHERE n.project_id = $project_id OR n.id STARTS WITH ('repository:' + $project_id)
                RETURN
                    n.id        AS id,
                    labels(n)[0] AS label,
                    n.name      AS name,
                    properties(n) AS props
                """,
                project_id=project_id,
            )
            nodes = []
            for record in nodes_result:
                node = {
                    "id": record["id"],
                    "label": record["label"],
                    "name": record["name"],
                    **{
                        k: v for k, v in record["props"].items()
                        if k not in ("id", "name") and v is not None
                    },
                }
                nodes.append(node)

            # All relationships between those nodes
            edges_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE (a.project_id = $project_id OR a.id STARTS WITH ('repository:' + $project_id))
                  AND (b.project_id = $project_id OR b.id STARTS WITH ('repository:' + $project_id))
                RETURN
                    a.id AS source,
                    type(r) AS rel_type,
                    b.id AS target
                """,
                project_id=project_id,
            )
            edges = [
                {"source": r["source"], "type": r["rel_type"], "target": r["target"]}
                for r in edges_result
            ]

        return {"nodes": nodes, "edges": edges}

    # ─── Node queries ─────────────────────────────────────────────────────────

    def get_all_nodes(self, project_id: str) -> list[dict]:
        """Return all nodes belonging to a project."""
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE n.project_id = $project_id
                RETURN n.id AS id, labels(n)[0] AS label, n.name AS name,
                       properties(n) AS props
                ORDER BY label, name
                """,
                project_id=project_id,
            )
            return [
                {"id": r["id"], "label": r["label"], "name": r["name"],
                 **r["props"]}
                for r in result
            ]

    def get_node(self, entity_id: str) -> dict | None:
        """Return a single node by its id, or None if not found."""
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (n {id: $id})
                RETURN n.id AS id, labels(n)[0] AS label, n.name AS name,
                       properties(n) AS props
                """,
                id=entity_id,
            )
            record = result.single()
            if not record:
                return None
            return {"id": record["id"], "label": record["label"],
                    "name": record["name"], **record["props"]}

    def get_children(self, entity_id: str) -> list[dict]:
        """
        Return all nodes directly connected via CONTAINS or DEFINES.
        Used for the tree-drill-down in the frontend.
        """
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (parent {id: $id})-[r:CONTAINS|DEFINES]->(child)
                RETURN child.id AS id, labels(child)[0] AS label,
                       child.name AS name, type(r) AS rel_type,
                       properties(child) AS props
                ORDER BY label, name
                """,
                id=entity_id,
            )
            return [
                {
                    "id": r["id"], "label": r["label"],
                    "name": r["name"], "via": r["rel_type"],
                    **r["props"],
                }
                for r in result
            ]

    # ─── Statistics ───────────────────────────────────────────────────────────

    def get_stats(self, project_id: str) -> dict:
        """
        Return node counts grouped by type for the dashboard.
        Example: { "File": 12, "Class": 8, "Function": 34 }
        """
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE n.project_id = $project_id
                RETURN labels(n)[0] AS label, count(n) AS cnt
                ORDER BY cnt DESC
                """,
                project_id=project_id,
            )
            counts = {r["label"]: r["cnt"] for r in result}

            # Also count relationships
            rel_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.project_id = $project_id
                RETURN count(r) AS total_rels
                """,
                project_id=project_id,
            )
            rel_record = rel_result.single()
            counts["_total_relationships"] = rel_record["total_rels"] if rel_record else 0

        return counts

    # ─── Project listing ──────────────────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """Return all Repository nodes (one per analyzed project)."""
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (r:Repository)
                RETURN r.id AS id, r.name AS name, r.project_id AS project_id,
                       r.description AS description, r.technologies AS technologies,
                       r.created_at AS created_at
                ORDER BY r.created_at DESC
                """
            )
            return [dict(r) for r in result]

    def get_project_tree(self, project_id: str) -> dict | None:
        """
        Return hierarchical tree: Repository → Folders → Files → Classes/Functions.
        Used for the tree-panel in the frontend.
        """
        with self._driver.session() as session:
            # Get the repository node
            repo_result = session.run(
                """
                MATCH (r:Repository)
                WHERE r.id = 'repository:' + $project_id OR r.project_id = $project_id
                RETURN r.id AS id, r.name AS name, properties(r) AS props
                LIMIT 1
                """,
                project_id=project_id,
            )
            repo_record = repo_result.single()
            if not repo_record:
                return None

            root = {
                "id": repo_record["id"],
                "name": repo_record["name"],
                "type": "Repository",
                "children": self._get_children_recursive(repo_record["id"], session, depth=0),
            }
            return root

    def _get_children_recursive(self, node_id: str, session, depth: int) -> list[dict]:
        """Recursively fetch children (max depth 4 for Phase 1)."""
        if depth >= 4:
            return []

        result = session.run(
            """
            MATCH (parent {id: $id})-[r:CONTAINS|DEFINES|HAS_README]->(child)
            RETURN child.id AS id, child.name AS name,
                   labels(child)[0] AS label, type(r) AS rel_type
            ORDER BY label, name
            """,
            id=node_id,
        )
        children = []
        for r in result:
            child = {
                "id": r["id"],
                "name": r["name"],
                "type": r["label"],
                "via": r["rel_type"],
                "children": self._get_children_recursive(r["id"], session, depth + 1),
            }
            children.append(child)
        return children

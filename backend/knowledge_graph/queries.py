"""
M2 — Knowledge Graph Engine — Graph Query Engine
==================================================
Provides graph query functions for M2 standalone server and knowledge graph inspection.

Phase 1 query functions:
  get_graph_data(project_id)        → all nodes + relationships for visualization
  get_all_nodes(project_id)         → list of all nodes (with properties)
  get_node(entity_id)               → single node detail
  get_children(entity_id)           → nodes connected via CONTAINS
  get_stats(project_id)             → count of nodes by type
  get_project_tree(project_id)      → hierarchy starting from Repository node

Phase 4 query functions (Architecture Intelligence):
  get_architecture_view(project_id)     → SYSTEM + COMPONENT + SERVICE + TECHNOLOGY subgraph
  get_components(project_id)            → all COMPONENT nodes with category/metadata
  get_component_dependencies(comp_id)   → COMMUNICATES_WITH + USES graph for one component
  get_technology_stack(project_id)      → all TECHNOLOGY nodes grouped by category
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

    # ─── Phase 4: Architecture Intelligence queries ────────────────────────────────

    def get_architecture_view(self, project_id: str) -> dict:
        """
        Return the architectural subgraph for a project:
          - All SYSTEM, COMPONENT, SERVICE, TECHNOLOGY nodes
          - All relationships between them (PART_OF, CONTAINS, USES,
            COMMUNICATES_WITH, EXPOSES)

        Used by M4 Architecture Visualization panel.

        Returns:
            {
              "nodes": [{ "id", "type", "name", "category", ...props }],
              "edges": [{ "source", "type", "target" }]
            }
        """
        with self._driver.session() as session:
            # Arch nodes
            nodes_result = session.run(
                """
                MATCH (n)
                WHERE n.project_id = $project_id
                  AND labels(n)[0] IN ['System', 'Component', 'Service', 'Technology']
                RETURN
                    n.id        AS id,
                    labels(n)[0] AS label,
                    n.name      AS name,
                    properties(n) AS props
                ORDER BY label, name
                """,
                project_id=project_id,
            )
            nodes = []
            node_ids: set[str] = set()
            for record in nodes_result:
                node = {
                    "id":    record["id"],
                    "type":  record["label"],
                    "name":  record["name"],
                    **{k: v for k, v in record["props"].items()
                       if k not in ("id", "name") and v is not None},
                }
                nodes.append(node)
                node_ids.add(record["id"])

            # Edges between arch nodes only
            edges_result = session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.project_id = $project_id
                  AND labels(a)[0] IN ['System', 'Component', 'Service', 'Technology']
                  AND labels(b)[0] IN ['System', 'Component', 'Service', 'Technology']
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

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total_components": sum(1 for n in nodes if n["type"] == "Component"),
                "total_services":   sum(1 for n in nodes if n["type"] == "Service"),
                "total_technologies": sum(1 for n in nodes if n["type"] == "Technology"),
            },
        }

    def get_components(self, project_id: str) -> list[dict]:
        """
        Return all COMPONENT nodes for a project, with category and metadata.
        Used by M4 Component Panel and Architecture Diagram.

        Returns:
            List of component dicts sorted by category then name.
        """
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (c:Component)
                WHERE c.project_id = $project_id
                OPTIONAL MATCH (c)-[:USES]->(t:Technology)
                OPTIONAL MATCH (c)-[:EXPOSES]->(api:Component)
                RETURN
                    c.id       AS id,
                    c.name     AS name,
                    c.category AS category,
                    c.folder   AS folder,
                    collect(DISTINCT t.name) AS technologies,
                    collect(DISTINCT api.name) AS exposes
                ORDER BY category, name
                """,
                project_id=project_id,
            )
            return [
                {
                    "id":           r["id"],
                    "name":         r["name"],
                    "category":     r["category"],
                    "folder":       r["folder"],
                    "technologies": [t for t in r["technologies"] if t],
                    "exposes":      [e for e in r["exposes"] if e],
                }
                for r in result
            ]

    def get_component_dependencies(self, component_id: str) -> dict:
        """
        Return the dependency graph for a single component:
          - Outgoing COMMUNICATES_WITH (what this component depends on)
          - Incoming COMMUNICATES_WITH (what depends on this component)
          - Outgoing USES (technologies this component uses)
          - Outgoing EXPOSES (APIs this component exposes)

        Used by M4 Architecture Explorer drill-down.

        Returns:
            {
              "component": { id, name, category },
              "calls":     [{ id, name, type }],     # COMMUNICATES_WITH targets
              "called_by": [{ id, name, type }],     # COMMUNICATES_WITH sources
              "uses":      [{ id, name, tech_name, category }],
              "exposes":   [{ id, name }],
            }
        """
        with self._driver.session() as session:
            # Get the component itself
            comp_result = session.run(
                """
                MATCH (c {id: $id})
                RETURN c.id AS id, c.name AS name,
                       c.category AS category, labels(c)[0] AS label
                """,
                id=component_id,
            )
            comp_record = comp_result.single()
            if not comp_record:
                return {"error": "Component not found", "id": component_id}

            component = {
                "id":       comp_record["id"],
                "name":     comp_record["name"],
                "category": comp_record["category"],
                "type":     comp_record["label"],
            }

            # Outgoing COMMUNICATES_WITH
            calls_result = session.run(
                """
                MATCH (c {id: $id})-[:COMMUNICATES_WITH]->(target)
                RETURN target.id AS id, target.name AS name, labels(target)[0] AS type
                ORDER BY name
                """,
                id=component_id,
            )
            calls = [dict(r) for r in calls_result]

            # Incoming COMMUNICATES_WITH
            called_by_result = session.run(
                """
                MATCH (source)-[:COMMUNICATES_WITH]->(c {id: $id})
                RETURN source.id AS id, source.name AS name, labels(source)[0] AS type
                ORDER BY name
                """,
                id=component_id,
            )
            called_by = [dict(r) for r in called_by_result]

            # USES (technology dependencies)
            uses_result = session.run(
                """
                MATCH (c {id: $id})-[:USES]->(t:Technology)
                RETURN t.id AS id, t.name AS name,
                       t.tech_name AS tech_name, t.category AS category
                ORDER BY name
                """,
                id=component_id,
            )
            uses = [dict(r) for r in uses_result]

            # EXPOSES (API surface)
            exposes_result = session.run(
                """
                MATCH (c {id: $id})-[:EXPOSES]->(api)
                RETURN api.id AS id, api.name AS name
                ORDER BY name
                """,
                id=component_id,
            )
            exposes = [dict(r) for r in exposes_result]

        return {
            "component": component,
            "calls":     calls,
            "called_by": called_by,
            "uses":      uses,
            "exposes":   exposes,
        }

    def get_technology_stack(self, project_id: str) -> dict:
        """
        Return all TECHNOLOGY nodes for a project, grouped by category.

        Used by M4 Technology Stack panel and project dashboard.

        Returns:
            {
              "all": [{ id, name, tech_name, category }],
              "by_category": {
                "web-framework": [...],
                "database": [...],
                ...
              }
            }
        """
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (t:Technology)
                WHERE t.project_id = $project_id
                OPTIONAL MATCH (c:Component)-[:USES]->(t)
                RETURN
                    t.id        AS id,
                    t.name      AS name,
                    t.tech_name AS tech_name,
                    t.category  AS category,
                    collect(DISTINCT c.name) AS used_by_components
                ORDER BY category, name
                """,
                project_id=project_id,
            )
            all_techs = []
            by_category: dict[str, list] = {}
            for r in result:
                tech = {
                    "id":                  r["id"],
                    "name":                r["name"],
                    "tech_name":           r["tech_name"],
                    "category":            r["category"] or "other",
                    "used_by_components": [c for c in r["used_by_components"] if c],
                }
                all_techs.append(tech)
                cat = tech["category"]
                by_category.setdefault(cat, []).append(tech)

        return {"all": all_techs, "by_category": by_category}

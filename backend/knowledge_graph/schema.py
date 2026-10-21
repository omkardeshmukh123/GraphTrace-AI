"""
M2 — Knowledge Graph Engine — Schema Setup (Standalone Development)
====================================================================
Creates Neo4j constraints and indexes for M2 standalone server mode.

Note: In the integrated M3 production server, backend/app/graph/builder.py
manages the production schema using the unified (n:Entity) label with
scoped (project_id, id) uniqueness.

Phase 1 schema:
  Constraints:
    - Repository.id, Folder.id, File.id, Class.id, Function.id, Readme.id  UNIQUE

Phase 4 schema (Architecture Intelligence):
  Constraints:
    - System.id, Component.id, Service.id, Technology.id  UNIQUE
  Indexes:
    - Component.category   (filter components by layer)
    - Service.service_name (fast service lookup)
    - Technology.tech_name (filter by tech stack)
    - Technology.category  (filter by tech category)
"""

from neo4j import Driver
from .models import NodeLabel


def generate_schema_queries() -> list[str]:
    """
    Generate all Cypher DDL query strings for constraints and indexes (Phase 1 + Phase 4).
    Useful for schema inspection, dry-runs, and testing.
    """
    labels = [
        # Phase 1
        NodeLabel.REPOSITORY,
        NodeLabel.FOLDER,
        NodeLabel.FILE,
        NodeLabel.CLASS,
        NodeLabel.FUNCTION,
        NodeLabel.README,
        # Phase 4 — Architecture Intelligence
        NodeLabel.SYSTEM,
        NodeLabel.COMPONENT,
        NodeLabel.SERVICE,
        NodeLabel.TECHNOLOGY,
        NodeLabel.REQUIREMENT,
        NodeLabel.DOCUMENT,
    ]
    queries = []
    for label in labels:
        constraint_name = f"constraint_{label.lower()}_id_unique"
        queries.append(
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.id IS UNIQUE"
        )

    index_specs = [
        # Phase 1 — code entity indexes
        (NodeLabel.REPOSITORY, "project_id",   "idx_repo_project_id"),
        (NodeLabel.REPOSITORY, "name",          "idx_repo_name"),
        (NodeLabel.FOLDER,     "name",          "idx_folder_name"),
        (NodeLabel.FILE,       "name",          "idx_file_name"),
        (NodeLabel.FILE,       "language",      "idx_file_language"),
        (NodeLabel.CLASS,      "name",          "idx_class_name"),
        (NodeLabel.FUNCTION,   "name",          "idx_function_name"),

        # Phase 4 — architecture entity indexes
        (NodeLabel.SYSTEM,     "project_id",   "idx_system_project_id"),
        (NodeLabel.COMPONENT,  "name",          "idx_component_name"),
        (NodeLabel.COMPONENT,  "category",      "idx_component_category"),
        (NodeLabel.SERVICE,    "name",          "idx_service_name"),
        (NodeLabel.SERVICE,    "service_name",  "idx_service_service_name"),
        (NodeLabel.TECHNOLOGY, "name",          "idx_technology_name"),
        (NodeLabel.TECHNOLOGY, "tech_name",     "idx_technology_tech_name"),
        (NodeLabel.TECHNOLOGY, "category",      "idx_technology_category"),
        (NodeLabel.REQUIREMENT, "name",         "idx_requirement_name"),
    ]
    for label, prop, idx_name in index_specs:
        queries.append(
            f"CREATE INDEX {idx_name} IF NOT EXISTS "
            f"FOR (n:{label}) ON (n.{prop})"
        )
    return queries


def run_schema_setup(driver: Driver) -> None:
    """
    Create all constraints and indexes. Safe to call multiple times.
    Uses CREATE CONSTRAINT IF NOT EXISTS (Neo4j 4.4+).
    """
    with driver.session() as session:
        for q in generate_schema_queries():
            session.run(q)
    print("[M2 Schema] Schema setup complete (Phase 1 + Phase 4).")


def _create_uniqueness_constraints(session) -> None:
    """Unique constraint on the `id` property for every node label."""
    labels = [
        # Phase 1
        NodeLabel.REPOSITORY,
        NodeLabel.FOLDER,
        NodeLabel.FILE,
        NodeLabel.CLASS,
        NodeLabel.FUNCTION,
        NodeLabel.README,
        # Phase 4 — Architecture Intelligence
        NodeLabel.SYSTEM,
        NodeLabel.COMPONENT,
        NodeLabel.SERVICE,
        NodeLabel.TECHNOLOGY,
        NodeLabel.REQUIREMENT,
        NodeLabel.DOCUMENT,
    ]
    for label in labels:
        constraint_name = f"constraint_{label.lower()}_id_unique"
        session.run(
            f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{label})
            REQUIRE n.id IS UNIQUE
            """
        )
        print(f"[M2 Schema]  ✓ Constraint on {label}.id")


def _create_indexes(session) -> None:
    """Indexes for common lookup patterns (Phase 1 + Phase 4)."""
    index_specs = [
        # Phase 1 — code entity indexes
        (NodeLabel.REPOSITORY, "project_id",   "idx_repo_project_id"),
        (NodeLabel.REPOSITORY, "name",          "idx_repo_name"),
        (NodeLabel.FOLDER,     "name",          "idx_folder_name"),
        (NodeLabel.FILE,       "name",          "idx_file_name"),
        (NodeLabel.FILE,       "language",      "idx_file_language"),
        (NodeLabel.CLASS,      "name",          "idx_class_name"),
        (NodeLabel.FUNCTION,   "name",          "idx_function_name"),

        # Phase 4 — architecture entity indexes
        (NodeLabel.SYSTEM,     "project_id",   "idx_system_project_id"),
        (NodeLabel.COMPONENT,  "name",          "idx_component_name"),
        (NodeLabel.COMPONENT,  "category",      "idx_component_category"),
        (NodeLabel.SERVICE,    "name",          "idx_service_name"),
        (NodeLabel.SERVICE,    "service_name",  "idx_service_service_name"),
        (NodeLabel.TECHNOLOGY, "name",          "idx_technology_name"),
        (NodeLabel.TECHNOLOGY, "tech_name",     "idx_technology_tech_name"),
        (NodeLabel.TECHNOLOGY, "category",      "idx_technology_category"),
        (NodeLabel.REQUIREMENT, "name",         "idx_requirement_name"),
    ]
    for label, prop, idx_name in index_specs:
        session.run(
            f"""
            CREATE INDEX {idx_name} IF NOT EXISTS
            FOR (n:{label})
            ON (n.{prop})
            """
        )
        print(f"[M2 Schema]  ✓ Index {label}.{prop}")

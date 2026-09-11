"""
M2 — Knowledge Graph Engine — Schema Setup
============================================
Creates Neo4j constraints and indexes.

Run once on application startup (idempotent — safe to re-run).

Phase 1 schema:
  Constraints:
    - Repository.id   UNIQUE
    - Folder.id       UNIQUE
    - File.id         UNIQUE
    - Class.id        UNIQUE
    - Function.id     UNIQUE
    - Readme.id       UNIQUE

  Indexes:
    - All node types: index on `name` for fast name lookups
    - File: index on `language`
    - Repository: index on `project_id`
"""

from neo4j import Driver
from .models import NodeLabel


def run_schema_setup(driver: Driver) -> None:
    """
    Create all constraints and indexes. Safe to call multiple times.
    Uses CREATE CONSTRAINT IF NOT EXISTS (Neo4j 4.4+).
    """
    with driver.session() as session:
        _create_uniqueness_constraints(session)
        _create_indexes(session)
    print("[M2 Schema] Schema setup complete.")


def _create_uniqueness_constraints(session) -> None:
    """Unique constraint on the `id` property for every node label."""
    labels = [
        NodeLabel.REPOSITORY,
        NodeLabel.FOLDER,
        NodeLabel.FILE,
        NodeLabel.CLASS,
        NodeLabel.FUNCTION,
        NodeLabel.README,
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
    """Indexes for common lookup patterns."""
    index_specs = [
        # (label, property, index_name)
        (NodeLabel.REPOSITORY, "project_id",  "idx_repo_project_id"),
        (NodeLabel.REPOSITORY, "name",         "idx_repo_name"),
        (NodeLabel.FOLDER,     "name",         "idx_folder_name"),
        (NodeLabel.FILE,       "name",         "idx_file_name"),
        (NodeLabel.FILE,       "language",     "idx_file_language"),
        (NodeLabel.CLASS,      "name",         "idx_class_name"),
        (NodeLabel.FUNCTION,   "name",         "idx_function_name"),
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

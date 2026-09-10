"""
M2 — Knowledge Graph Engine — Neo4j Connection
================================================
Manages the Neo4j driver as a module-level singleton.

Usage:
    from knowledge_graph.connection import get_driver, close_driver

    driver = get_driver()
    with driver.session() as session:
        session.run("RETURN 1")

    # On app shutdown:
    close_driver()
"""

from neo4j import GraphDatabase, Driver
from config import settings

_driver: Driver | None = None


def get_driver() -> Driver:
    """Return the singleton Neo4j driver, creating it if necessary."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        # Verify connectivity immediately so startup fails fast on bad credentials
        _driver.verify_connectivity()
        print(f"[M2 Connection] Connected to Neo4j: {settings.neo4j_uri}")
    return _driver


def close_driver() -> None:
    """Close the Neo4j driver on application shutdown."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        print("[M2 Connection] Neo4j driver closed.")

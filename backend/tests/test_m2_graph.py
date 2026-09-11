"""
Tests — M2 Knowledge Graph Engine
===================================
Tests for:
  - KnowledgeGraphBuilder: writing ArtifactData to Neo4j
  - GraphQueryEngine: querying the graph
  - EntityResolver: deduplication

NOTE: These tests require a real Neo4j connection.
Set up your .env before running:
    cp .env.example .env
    # fill in NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

Run with:
    cd backend
    pytest tests/test_m2_graph.py -v

Tests use a unique project_id per run to avoid cross-test contamination.
Cleanup runs in teardown.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from artifact_intelligence.models import (
    ArtifactData, Entity, Relationship,
    EntityType, RelationshipType,
)
from knowledge_graph.builder import KnowledgeGraphBuilder
from knowledge_graph.queries import GraphQueryEngine
from knowledge_graph.connection import get_driver


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driver():
    """Single driver for all M2 tests."""
    try:
        d = get_driver()
        d.verify_connectivity()
        yield d
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")


@pytest.fixture
def project_id():
    """Unique project ID per test to avoid contamination."""
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_artifact_data(project_id):
    """A minimal but realistic ArtifactData for M2 tests."""
    repo_id = f"repository:{project_id}"
    folder_id = f"folder:{project_id}:src"
    file_id = f"file:{project_id}:src/auth.py"
    class_id = f"class:{project_id}:src/auth.py:AuthService"
    func_id = f"function:{project_id}:src/auth.py:AuthService.login"

    entities = [
        Entity(id=repo_id, type=EntityType.REPOSITORY, name="TestProject",
               properties={"project_id": project_id}),
        Entity(id=folder_id, type=EntityType.FOLDER, name="src",
               properties={"project_id": project_id, "relative_path": "src"}),
        Entity(id=file_id, type=EntityType.FILE, name="auth.py",
               properties={"project_id": project_id, "language": "Python"}),
        Entity(id=class_id, type=EntityType.CLASS, name="AuthService",
               properties={"project_id": project_id, "language": "Python"}),
        Entity(id=func_id, type=EntityType.FUNCTION, name="login",
               properties={"project_id": project_id, "is_method": True}),
    ]

    relationships = [
        Relationship(source=repo_id, type=RelationshipType.CONTAINS, target=folder_id),
        Relationship(source=folder_id, type=RelationshipType.CONTAINS, target=file_id),
        Relationship(source=file_id, type=RelationshipType.DEFINES, target=class_id),
        Relationship(source=class_id, type=RelationshipType.CONTAINS, target=func_id),
    ]

    return ArtifactData(
        entities=entities,
        relationships=relationships,
        metadata={"project_id": project_id, "project_name": "TestProject"},
    )


def _cleanup(driver, project_id: str):
    """Remove all test nodes from Neo4j after each test."""
    with driver.session() as session:
        session.run(
            "MATCH (n) WHERE n.project_id = $pid DETACH DELETE n",
            pid=project_id,
        )


# ─── Builder Tests ────────────────────────────────────────────────────────────

class TestKnowledgeGraphBuilder:

    def test_build_returns_success(self, driver, sample_artifact_data, project_id):
        try:
            builder = KnowledgeGraphBuilder(driver)
            result = builder.build(sample_artifact_data)
            assert result.success, f"Build failed: {result.errors}"
        finally:
            _cleanup(driver, project_id)

    def test_nodes_are_created(self, driver, sample_artifact_data, project_id):
        try:
            builder = KnowledgeGraphBuilder(driver)
            result = builder.build(sample_artifact_data)
            assert result.nodes_created > 0 or result.nodes_updated > 0
        finally:
            _cleanup(driver, project_id)

    def test_relationships_are_created(self, driver, sample_artifact_data, project_id):
        try:
            builder = KnowledgeGraphBuilder(driver)
            result = builder.build(sample_artifact_data)
            assert result.relationships_created > 0
        finally:
            _cleanup(driver, project_id)

    def test_idempotent_rebuild(self, driver, sample_artifact_data, project_id):
        """Running build twice should not duplicate nodes (MERGE behavior)."""
        try:
            builder = KnowledgeGraphBuilder(driver)
            result1 = builder.build(sample_artifact_data)
            result2 = builder.build(sample_artifact_data)

            query = GraphQueryEngine(driver)
            nodes = query.get_all_nodes(project_id)
            # Node count should equal len(entities) — no duplicates
            assert len(nodes) == len(sample_artifact_data.entities)
        finally:
            _cleanup(driver, project_id)


# ─── Query Engine Tests ───────────────────────────────────────────────────────

class TestGraphQueryEngine:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, driver, sample_artifact_data, project_id):
        """Build the graph before each test, clean up after."""
        builder = KnowledgeGraphBuilder(driver)
        builder.build(sample_artifact_data)
        self.query = GraphQueryEngine(driver)
        self.project_id = project_id
        self.artifact_data = sample_artifact_data

        yield

        _cleanup(driver, project_id)

    def test_get_all_nodes(self):
        nodes = self.query.get_all_nodes(self.project_id)
        assert len(nodes) == len(self.artifact_data.entities)

    def test_get_node_by_id(self):
        repo_id = f"repository:{self.project_id}"
        node = self.query.get_node(repo_id)
        assert node is not None
        assert node["name"] == "TestProject"

    def test_get_node_returns_none_for_missing(self):
        node = self.query.get_node("nonexistent:id")
        assert node is None

    def test_get_children(self):
        repo_id = f"repository:{self.project_id}"
        children = self.query.get_children(repo_id)
        child_names = [c["name"] for c in children]
        assert "src" in child_names

    def test_get_stats(self):
        stats = self.query.get_stats(self.project_id)
        assert "File" in stats
        assert "Class" in stats
        assert "Function" in stats
        assert stats["_total_relationships"] >= 4

    def test_get_graph_data(self):
        data = self.query.get_graph_data(self.project_id)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == len(self.artifact_data.entities)
        assert len(data["edges"]) == len(self.artifact_data.relationships)

    def test_get_project_tree(self):
        tree = self.query.get_project_tree(self.project_id)
        assert tree is not None
        assert tree["type"] == "Repository"
        assert len(tree["children"]) > 0

    def test_list_projects_includes_test_project(self):
        projects = self.query.list_projects()
        project_ids = [p.get("project_id") for p in projects]
        assert self.project_id in project_ids

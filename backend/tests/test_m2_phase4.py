"""
Tests — M2 Knowledge Graph Engine (Phase 4 — Architecture Intelligence)
========================================================================
Validates Member 2's Phase 4 deliverables:
  - Architecture node labels & relationship constants (models.py)
  - Reverse mapping from M1/M3 entity and relationship types
  - Schema setup queries and constraints for architectural nodes (schema.py)
  - Graph writer whitelist and extra label mapping (graph_writer.py)
  - Graph builder entity grouping and batch mapping (builder.py)
  - Query engine architecture queries and result parsing (queries.py)
"""

from unittest.mock import MagicMock
import pytest

from backend.knowledge_graph.models import NodeLabel, RelType, ARCH_NODE_TYPES
from backend.knowledge_graph.schema import generate_schema_queries
from backend.knowledge_graph.graph_writer import _ALLOWED_REL_TYPES, _EXTRA_LABELS, write_graph
from backend.knowledge_graph.builder import KnowledgeGraphBuilder
from backend.knowledge_graph.queries import GraphQueryEngine
from backend.artifact_intelligence.models import Entity, Relationship, ArtifactData
from backend.app.models import ArtifactGraph, Node, Relationship as AppRelationship


class TestM2Phase4Models:
    """Tests that NodeLabel, RelType, and ARCH_NODE_TYPES are correctly defined."""

    def test_arch_node_labels_defined(self):
        assert NodeLabel.SYSTEM == "System"
        assert NodeLabel.COMPONENT == "Component"
        assert NodeLabel.SERVICE == "Service"
        assert NodeLabel.TECHNOLOGY == "Technology"
        assert NodeLabel.REQUIREMENT == "Requirement"
        assert NodeLabel.DOCUMENT == "Document"

    def test_arch_rel_types_defined(self):
        assert RelType.COMMUNICATES_WITH == "COMMUNICATES_WITH"
        assert RelType.EXPOSES == "EXPOSES"
        assert RelType.TESTED_BY == "TESTED_BY"
        assert RelType.PART_OF == "PART_OF"
        assert RelType.USES == "USES"

    def test_arch_node_types_set(self):
        assert NodeLabel.SYSTEM in ARCH_NODE_TYPES
        assert NodeLabel.COMPONENT in ARCH_NODE_TYPES
        assert NodeLabel.SERVICE in ARCH_NODE_TYPES
        assert NodeLabel.TECHNOLOGY in ARCH_NODE_TYPES

    def test_node_label_reverse_mapping(self):
        mapping = NodeLabel.FROM_ENTITY_TYPE
        assert mapping["SYSTEM"] == "System"
        assert mapping["COMPONENT"] == "Component"
        assert mapping["SERVICE"] == "Service"
        assert mapping["TECHNOLOGY"] == "Technology"

    def test_rel_type_reverse_mapping(self):
        mapping = RelType.FROM_REL_TYPE
        assert mapping["COMMUNICATES_WITH"] == "COMMUNICATES_WITH"
        assert mapping["EXPOSES"] == "EXPOSES"
        assert mapping["TESTED_BY"] == "TESTED_BY"
        assert mapping["USES"] == "USES"
        assert mapping["PART_OF"] == "PART_OF"


class TestM2Phase4Schema:
    """Tests schema setup queries for architecture nodes."""

    def test_schema_queries_include_arch_constraints(self):
        queries = generate_schema_queries()
        assert len(queries) >= 10
        joined = "\n".join(queries)

        for label in ["System", "Component", "Service", "Technology"]:
            assert f"FOR (n:{label}) REQUIRE n.id IS UNIQUE" in joined


class TestM2Phase4GraphWriter:
    """Tests M2 graph_writer plugin updates for Phase 4."""

    def test_whitelist_contains_phase4_rels(self):
        assert "COMMUNICATES_WITH" in _ALLOWED_REL_TYPES
        assert "EXPOSES" in _ALLOWED_REL_TYPES
        assert "TESTED_BY" in _ALLOWED_REL_TYPES
        assert "USES" in _ALLOWED_REL_TYPES
        assert "PART_OF" in _ALLOWED_REL_TYPES

    def test_extra_labels_contain_arch_types(self):
        assert _EXTRA_LABELS["SYSTEM"] == "System"
        assert _EXTRA_LABELS["COMPONENT"] == "Component"
        assert _EXTRA_LABELS["SERVICE"] == "Service"
        assert _EXTRA_LABELS["TECHNOLOGY"] == "Technology"

    def test_write_graph_with_mock_driver(self):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        graph = ArtifactGraph(
            project_id="proj-arch-test",
            nodes=[
                Node(id="proj-arch-test", type="PROJECT", name="ArchTest"),
                Node(id="sys-1", type="SYSTEM", name="CoreSystem"),
                Node(id="comp-1", type="COMPONENT", name="AuthModule"),
                Node(id="svc-1", type="SERVICE", name="AuthService"),
                Node(id="tech-1", type="TECHNOLOGY", name="FastAPI"),
            ],
            relationships=[
                AppRelationship(source="sys-1", type="CONTAINS", target="comp-1"),
                AppRelationship(source="comp-1", type="PART_OF", target="sys-1"),
                AppRelationship(source="svc-1", type="EXPOSES", target="comp-1"),
                AppRelationship(source="comp-1", type="USES", target="tech-1"),
                AppRelationship(source="svc-1", type="COMMUNICATES_WITH", target="comp-1"),
            ]
        )

        def mock_exec(fn, g):
            mock_tx = MagicMock()
            mock_tx.run.return_value.single.return_value = {"cnt": 0}
            fn(mock_tx, g)
        mock_session.execute_write.side_effect = mock_exec

        write_graph(graph=graph, driver=mock_driver, database="neo4j")
        assert mock_driver.session.called


class TestM2Phase4Builder:
    """Tests grouping and batch mapping of architecture entities in KnowledgeGraphBuilder."""

    def test_builder_groups_arch_entities(self):
        builder = KnowledgeGraphBuilder(driver=MagicMock())
        entities = [
            Entity(id="s1", type="SYSTEM", name="Sys"),
            Entity(id="c1", type="COMPONENT", name="Comp"),
            Entity(id="srv1", type="SERVICE", name="Srv"),
            Entity(id="t1", type="TECHNOLOGY", name="Tech"),
        ]
        groups = builder._group_entities_by_label(entities)
        assert "System" in groups
        assert "Component" in groups
        assert "Service" in groups
        assert "Technology" in groups

    def test_builder_groups_arch_relationships(self):
        builder = KnowledgeGraphBuilder(driver=MagicMock())
        rels = [
            Relationship(source="s1", type="COMMUNICATES_WITH", target="s2"),
            Relationship(source="c1", type="EXPOSES", target="srv1"),
            Relationship(source="srv1", type="TESTED_BY", target="test1"),
            Relationship(source="c1", type="USES", target="t1"),
        ]
        groups = builder._group_rels_by_type(rels)
        assert "COMMUNICATES_WITH" in groups
        assert "EXPOSES" in groups
        assert "TESTED_BY" in groups
        assert "USES" in groups


class TestM2Phase4QueryEngine:
    """Tests Phase 4 architecture query methods in GraphQueryEngine."""

    def test_get_architecture_view(self):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        query_engine = GraphQueryEngine(driver=mock_driver)

        mock_session.run.side_effect = [
            # First query: nodes
            [
                {
                    "id": "c1",
                    "label": "Component",
                    "name": "AuthComp",
                    "props": {
                        "technology": "Python",
                        "path": "src/auth",
                    }
                }
            ],
            # Second query: relationships
            [
                {
                    "source": "c1",
                    "target": "c2",
                    "rel_type": "COMMUNICATES_WITH",
                }
            ]
        ]

        result = query_engine.get_architecture_view("test-proj")
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "AuthComp"
        assert result["nodes"][0]["type"] == "Component"
        assert len(result["edges"]) == 1
        assert result["edges"][0]["type"] == "COMMUNICATES_WITH"

    def test_get_components(self):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        query_engine = GraphQueryEngine(driver=mock_driver)
        mock_session.run.return_value = [
            {
                "id": "comp-1",
                "name": "AuthComponent",
                "category": "core",
                "folder": "src/auth",
                "technologies": ["FastAPI"],
                "exposes": ["login"],
            }
        ]

        components = query_engine.get_components("test-proj")
        assert len(components) == 1
        assert components[0]["id"] == "comp-1"
        assert components[0]["category"] == "core"
        assert components[0]["folder"] == "src/auth"
        assert "FastAPI" in components[0]["technologies"]

    def test_get_component_dependencies(self):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        query_engine = GraphQueryEngine(driver=mock_driver)

        comp_mock_res = MagicMock()
        comp_mock_res.single.return_value = {
            "id": "comp-1", "name": "AuthComp", "category": "core", "label": "Component"
        }

        mock_session.run.side_effect = [
            # Component record
            comp_mock_res,
            # Calls (outgoing)
            [{"id": "comp-2", "name": "UserComp", "type": "COMPONENT"}],
            # Called by (incoming)
            [{"id": "comp-3", "name": "GatewayComp", "type": "COMPONENT"}],
            # Technologies
            [{"id": "t1", "name": "JWT", "tech_name": "jwt", "category": "security"}],
            # Exposes
            [{"id": "s1", "name": "LoginSvc"}],
        ]

        deps = query_engine.get_component_dependencies("comp-1")
        assert deps is not None
        assert deps["component"]["id"] == "comp-1"
        assert len(deps["calls"]) == 1
        assert len(deps["called_by"]) == 1
        assert len(deps["uses"]) == 1
        assert len(deps["exposes"]) == 1

    def test_get_technology_stack(self):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        query_engine = GraphQueryEngine(driver=mock_driver)
        mock_session.run.return_value = [
            {
                "id": "t-1",
                "name": "FastAPI",
                "tech_name": "fastapi",
                "category": "web-framework",
                "used_by_components": ["AuthComp", "UserComp"],
            },
            {
                "id": "t-2",
                "name": "Neo4j",
                "tech_name": "neo4j",
                "category": "database",
                "used_by_components": ["GraphComp"],
            },
        ]

        stack = query_engine.get_technology_stack("test-proj")
        assert len(stack["all"]) == 2
        assert "web-framework" in stack["by_category"]
        assert "database" in stack["by_category"]
        assert stack["all"][0]["tech_name"] == "fastapi"

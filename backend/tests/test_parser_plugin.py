"""
Tests — M1 → M3 Integration (Parser Plugin)
=============================================
Tests that our pipeline.py parser plugin produces a valid ArtifactGraph
that satisfies M3's model validation rules.

Run with (from project root):
    python -m pytest backend/tests/test_parser_plugin.py -v

No Neo4j required — uses in-memory validation only.
"""

from pathlib import Path

import pytest
from backend.app.parsers.pipeline import parse_project
from backend.app.models import ArtifactGraph

# The sample project we built for M1 testing
# pytest.ini has pythonpath = . backend, so both backend/ and project root are on path
SAMPLE_PROJECT = Path(__file__).parent.parent.parent / "sample_project"


class TestParserPlugin:
    """Tests that parse_project() satisfies the M3 ArtifactGraph contract."""

    @pytest.fixture(scope="class")
    def graph(self):
        """Parse the sample project once, reuse across all tests in this class."""
        return parse_project(
            project_id="test-integration-001",
            repository_root=SAMPLE_PROJECT,
            requirements_text=None,
        )

    def test_returns_artifact_graph(self, graph):
        """Return type must be a valid ArtifactGraph (passes M3 model validation)."""
        assert isinstance(graph, ArtifactGraph)

    def test_project_id_matches(self, graph):
        """graph.project_id must equal the passed project_id."""
        assert graph.project_id == "test-integration-001"

    def test_exactly_one_project_node(self, graph):
        """Exactly one PROJECT node must exist, with id == project_id."""
        projects = [n for n in graph.nodes if n.type == "PROJECT"]
        assert len(projects) == 1
        assert projects[0].id == graph.project_id

    def test_no_duplicate_node_ids(self, graph):
        """All node IDs must be unique within the graph."""
        ids = [n.id for n in graph.nodes]
        assert len(ids) == len(set(ids)), "Duplicate node IDs found!"

    def test_all_relationship_endpoints_exist(self, graph):
        """All relationship source and target IDs must exist as nodes."""
        node_ids = {n.id for n in graph.nodes}
        for rel in graph.relationships:
            assert rel.source in node_ids, f"Relationship source {rel.source!r} has no matching node"
            assert rel.target in node_ids, f"Relationship target {rel.target!r} has no matching node"

    def test_no_duplicate_relationships(self, graph):
        """No duplicate (source, type, target) triples allowed."""
        seen: set[tuple] = set()
        for rel in graph.relationships:
            key = (rel.source, rel.type, rel.target)
            assert key not in seen, f"Duplicate relationship: {key}"
            seen.add(key)

    def test_has_file_nodes(self, graph):
        """Should have FILE nodes for .py and .js files."""
        files = [n for n in graph.nodes if n.type == "FILE"]
        assert len(files) >= 4, "Expected at least 4 FILE nodes"

    def test_has_class_nodes(self, graph):
        """Should have CLASS nodes for AuthService, OrderService etc."""
        classes = [n for n in graph.nodes if n.type == "CLASS"]
        class_names = [c.name for c in classes]
        assert "AuthService" in class_names
        assert "OrderService" in class_names

    def test_has_function_nodes(self, graph):
        """Should have FUNCTION nodes for methods."""
        functions = [n for n in graph.nodes if n.type == "FUNCTION"]
        assert len(functions) > 0

    def test_has_package_nodes(self, graph):
        """Should have PACKAGE nodes for src/ and frontend/ directories."""
        packages = [n for n in graph.nodes if n.type == "PACKAGE"]
        names = [p.name for p in packages]
        assert "src" in names
        assert "frontend" in names

    def test_has_document_node(self, graph):
        """Should have DOCUMENT node for README.md."""
        docs = [n for n in graph.nodes if n.type == "DOCUMENT"]
        assert len(docs) >= 1

    def test_node_properties_have_path(self, graph):
        """FILE nodes should have a 'path' property."""
        file_nodes = [n for n in graph.nodes if n.type == "FILE"]
        for node in file_nodes:
            assert "path" in node.properties, f"FILE node {node.name!r} missing 'path' property"

    def test_function_nodes_have_reference(self, graph):
        """FUNCTION nodes should have 'reference' for manual mappings."""
        func_nodes = [n for n in graph.nodes if n.type == "FUNCTION"]
        for node in func_nodes:
            assert "reference" in node.properties, f"FUNCTION {node.name!r} missing 'reference'"

    def test_m3_model_validation_passes(self, graph):
        """Re-validate through M3's Pydantic model — must not raise."""
        # Round-trip through JSON to ensure serialization works too
        json_str = graph.model_dump_json()
        reloaded = ArtifactGraph.model_validate_json(json_str)
        assert reloaded.project_id == graph.project_id

    def test_no_self_loop_relationships(self, graph):
        """No relationship should point from a node to itself."""
        for rel in graph.relationships:
            assert rel.source != rel.target, f"Self-loop found on {rel.source!r}"


class TestParserPluginWithRequirements:
    """Tests that requirements parsing from Markdown SRS works correctly."""

    SAMPLE_SRS = """
# Software Requirements Specification

## REQ-001: User Authentication
The system shall allow users to log in with username and password.

## REQ-002: Order Creation
Users shall be able to create orders containing multiple items.

**REQ-003**: Payment Processing — The system shall support card and UPI payments.
"""

    def test_requirements_parsed_as_nodes(self):
        graph = parse_project(
            project_id="test-req-parsing",
            repository_root=SAMPLE_PROJECT,
            requirements_text=self.SAMPLE_SRS,
        )
        req_nodes = [n for n in graph.nodes if n.type == "REQUIREMENT"]
        req_refs = [n.properties.get("reference") for n in req_nodes]

        assert "REQ-001" in req_refs
        assert "REQ-002" in req_refs
        assert "REQ-003" in req_refs

    def test_requirements_have_correct_names(self):
        graph = parse_project(
            project_id="test-req-names",
            repository_root=SAMPLE_PROJECT,
            requirements_text=self.SAMPLE_SRS,
        )
        req_nodes = {
            n.properties.get("reference"): n.name
            for n in graph.nodes if n.type == "REQUIREMENT"
        }
        assert "User Authentication" in req_nodes.get("REQ-001", "")

    def test_requirements_connected_to_project(self):
        graph = parse_project(
            project_id="test-req-conn",
            repository_root=SAMPLE_PROJECT,
            requirements_text=self.SAMPLE_SRS,
        )
        req_ids = {n.id for n in graph.nodes if n.type == "REQUIREMENT"}
        part_of_rels = {r.source for r in graph.relationships if r.type == "PART_OF"}
        for req_id in req_ids:
            assert req_id in part_of_rels, f"REQUIREMENT {req_id} not connected via PART_OF"

    def test_no_duplicate_requirements(self):
        graph = parse_project(
            project_id="test-req-dedup",
            repository_root=SAMPLE_PROJECT,
            requirements_text=self.SAMPLE_SRS,
        )
        req_refs = [n.properties.get("reference") for n in graph.nodes if n.type == "REQUIREMENT"]
        assert len(req_refs) == len(set(req_refs)), "Duplicate REQUIREMENT nodes found"

    def test_m3_validation_passes_with_requirements(self):
        """Full ArtifactGraph validation must pass even with REQUIREMENT + PART_OF."""
        graph = parse_project(
            project_id="test-req-validate",
            repository_root=SAMPLE_PROJECT,
            requirements_text=self.SAMPLE_SRS,
        )
        # This calls M3's model_validator — will raise if contract is violated
        reloaded = ArtifactGraph.model_validate(graph.model_dump())
        assert reloaded.project_id == graph.project_id

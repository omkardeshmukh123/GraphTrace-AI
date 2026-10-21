"""
Tests — M3 FastAPI Backend (Phase 4 — Architecture Intelligence API)
====================================================================
Validates Member 3's Phase 4 endpoints, queries, and Pydantic schemas:
  - GET /projects/{project_id}/architecture
  - GET /projects/{project_id}/components
  - GET /projects/{project_id}/components/{component_id}/dependencies
  - GET /projects/{project_id}/technologies
  - Error handling (404 for missing project/node, 422 for invalid component type)
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.models import ArtifactGraph, Node, Relationship


@pytest.fixture
def arch_graph() -> ArtifactGraph:
    """ArtifactGraph containing architecture nodes and relationships."""
    nodes = [
        Node(id="arch-demo", type="PROJECT", name="Architecture Demo"),
        # Systems & Components
        Node(id="sys-core", type="SYSTEM", name="Core System", properties={"description": "Main platform"}),
        Node(id="comp-auth", type="COMPONENT", name="AuthModule", properties={"category": "security", "folder": "src/auth"}),
        Node(id="comp-orders", type="COMPONENT", name="OrderModule", properties={"category": "core", "folder": "src/orders"}),
        Node(id="comp-gateway", type="COMPONENT", name="ApiGateway", properties={"category": "gateway", "folder": "src/gateway"}),
        # Services & Technologies
        Node(id="svc-jwt", type="SERVICE", name="JwtAuthService", properties={"service_name": "jwt"}),
        Node(id="tech-fastapi", type="TECHNOLOGY", name="FastAPI", properties={"tech_name": "fastapi", "category": "web-framework"}),
        Node(id="tech-postgres", type="TECHNOLOGY", name="PostgreSQL", properties={"tech_name": "postgres", "category": "database"}),
        # Code level files
        Node(id="file-auth", type="FILE", name="auth.py", properties={"reference": "src/auth/auth.py"}),
        Node(id="file-orders", type="FILE", name="orders.py", properties={"reference": "src/orders/orders.py"}),
    ]

    triples = [
        ("arch-demo", "CONTAINS", "sys-core"),
        ("sys-core", "CONTAINS", "comp-auth"),
        ("sys-core", "CONTAINS", "comp-orders"),
        ("sys-core", "CONTAINS", "comp-gateway"),
        ("comp-auth", "CONTAINS", "file-auth"),
        ("comp-orders", "CONTAINS", "file-orders"),
        ("comp-auth", "CONTAINS", "svc-jwt"),
        ("comp-auth", "EXPOSES", "svc-jwt"),
        ("comp-auth", "USES", "tech-fastapi"),
        ("comp-auth", "USES", "tech-postgres"),
        ("comp-orders", "USES", "tech-postgres"),
        ("comp-gateway", "COMMUNICATES_WITH", "comp-auth"),
        ("comp-gateway", "COMMUNICATES_WITH", "comp-orders"),
        ("comp-orders", "COMMUNICATES_WITH", "comp-auth"),
    ]

    edges = [
        Relationship(source=src, target=tgt, type=rel_type)
        for src, rel_type, tgt in triples
    ]

    return ArtifactGraph(project_id="arch-demo", nodes=nodes, relationships=edges)


@pytest.fixture
def client(tmp_path, arch_graph):
    settings = Settings(_env_file=None, data_dir=tmp_path, store="local", parser="", graph_writer="")
    app = create_app(settings)
    with TestClient(app) as test_client:
        # Import the architecture graph fixture
        res = test_client.post("/projects/import", json=arch_graph.model_dump())
        assert res.status_code == 201
        yield test_client


def test_get_architecture_view(client):
    res = client.get("/projects/arch-demo/architecture")
    assert res.status_code == 200
    data = res.json()

    assert data["project_id"] == "arch-demo"
    assert "nodes" in data
    assert "relationships" in data
    assert "stats" in data

    # Verify only architecture nodes are returned (no files)
    node_types = {n["type"] for n in data["nodes"]}
    assert "FILE" not in node_types
    assert "SYSTEM" in node_types
    assert "COMPONENT" in node_types
    assert "SERVICE" in node_types
    assert "TECHNOLOGY" in node_types

    # Verify stats
    stats = data["stats"]
    assert stats["total_systems"] == 1
    assert stats["total_components"] == 3
    assert stats["total_services"] == 1
    assert stats["total_technologies"] == 2
    assert stats["total_communications"] == 3


def test_get_components_list(client):
    res = client.get("/projects/arch-demo/components")
    assert res.status_code == 200
    components = res.json()

    assert len(components) == 3
    names = {c["name"] for c in components}
    assert names == {"AuthModule", "OrderModule", "ApiGateway"}

    auth_comp = next(c for c in components if c["name"] == "AuthModule")
    assert auth_comp["category"] == "security"
    assert auth_comp["folder"] == "src/auth"
    assert "FastAPI" in auth_comp["technologies"]
    assert "PostgreSQL" in auth_comp["technologies"]
    assert "JwtAuthService" in auth_comp["exposes"]
    assert auth_comp["file_count"] == 1
    assert auth_comp["service_count"] == 1


def test_get_component_dependencies(client):
    # Test ApiGateway component (outgoing calls to AuthModule and OrderModule)
    res = client.get("/projects/arch-demo/components/comp-gateway/dependencies")
    assert res.status_code == 200
    data = res.json()

    assert data["component"]["name"] == "ApiGateway"
    calls_names = {c["name"] for c in data["calls"]}
    assert "AuthModule" in calls_names
    assert "OrderModule" in calls_names

    # Test AuthModule (called by ApiGateway and OrderModule)
    res_auth = client.get("/projects/arch-demo/components/comp-auth/dependencies")
    assert res_auth.status_code == 200
    auth_data = res_auth.json()

    called_by_names = {c["name"] for c in auth_data["called_by"]}
    assert "ApiGateway" in called_by_names
    assert "OrderModule" in called_by_names
    uses_names = {u["name"] for u in auth_data["uses"]}
    assert "FastAPI" in uses_names
    assert "PostgreSQL" in uses_names
    exposes_names = {e["name"] for e in auth_data["exposes"]}
    assert "JwtAuthService" in exposes_names


def test_get_technologies_stack(client):
    res = client.get("/projects/arch-demo/technologies")
    assert res.status_code == 200
    data = res.json()

    assert data["project_id"] == "arch-demo"
    assert len(data["all"]) == 2

    by_category = data["by_category"]
    assert "web-framework" in by_category
    assert "database" in by_category

    fastapi_item = next(t for t in data["all"] if t["name"] == "FastAPI")
    assert fastapi_item["used_by_components"] == ["AuthModule"]

    pg_item = next(t for t in data["all"] if t["name"] == "PostgreSQL")
    assert sorted(pg_item["used_by_components"]) == ["AuthModule", "OrderModule"]


def test_architecture_errors(client):
    # Missing project
    res = client.get("/projects/non-existent-project/architecture")
    assert res.status_code == 404

    # Missing component
    res = client.get("/projects/arch-demo/components/missing-comp/dependencies")
    assert res.status_code == 404

    # Node is not a COMPONENT (e.g. requesting dependencies of a FILE)
    res = client.get("/projects/arch-demo/components/file-auth/dependencies")
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "not_a_component"

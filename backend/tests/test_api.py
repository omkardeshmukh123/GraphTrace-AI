import io
import json
import stat
from zipfile import ZipFile, ZipInfo

import pytest
from fastapi.testclient import TestClient
from neo4j.exceptions import ServiceUnavailable

from backend.app.config import Settings
from backend.app.graph.store import LocalGraphStore
from backend.app.main import create_app
from backend.app.models import ArtifactGraph, Node
from scripts.make_demo import demo_graph


@pytest.fixture
def settings(tmp_path):
    return Settings(_env_file=None, data_dir=tmp_path, store="local", parser="", graph_writer="")


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as active:
        yield active


@pytest.fixture
def seeded(client):
    assert client.post("/projects/import", json=demo_graph().model_dump()).status_code == 201
    return client


def zip_bytes(entries):
    output = io.BytesIO()
    with ZipFile(output, "w") as archive:
        for name, content in entries:
            if isinstance(name, str):
                info = ZipInfo(name)
                # Preserve raw ZIP names instead of the Windows writer normalizing them.
                info.filename = name
                archive.writestr(info, content)
            else:
                archive.writestr(name, content)
    return output.getvalue()


@pytest.fixture
def integrated(settings, monkeypatch):
    def parse(*, project_id, repository_root, requirements_text):
        assert (repository_root / "auth.py").read_text() == "def login(): pass"
        return ArtifactGraph(project_id=project_id, nodes=[
            Node(id=project_id, type="PROJECT", name="Uploaded sample"),
            Node(id="login", type="FUNCTION", name="login", properties={"reference": "auth.py::login"}),
            Node(id="req", type="REQUIREMENT", name="Login", properties={"reference": "REQ-001", "description": requirements_text}),
        ])
    monkeypatch.setattr("backend.app.analysis.load_plugin", lambda *args: parse)
    with TestClient(create_app(settings)) as active:
        yield active


def test_health_and_openapi(client):
    assert client.get("/health").json() == {"status": "ok", "store": "local", "parser_configured": False}
    assert client.get("/health/ready").status_code == 200
    assert "/projects/analyze" in client.get("/openapi.json").json()["paths"]


def test_import_summary_filters_and_persistence(seeded, settings):
    project = seeded.get("/projects/demo").json()
    assert project["counts"]["REQUIREMENT"] == 2
    assert project["source"] == "hand_authored_demo"
    assert seeded.get("/projects").json() == [project]
    graph = seeded.get("/projects/demo/graph", params={"node_type": "CLASS", "relationship_type": "DEPENDS_ON"}).json()
    assert len(graph["nodes"]) == 2
    assert len(graph["relationships"]) == 1
    result = seeded.get("/projects/demo/graph", params={"search": "AUTHSERVICE"}).json()
    assert {n["id"] for n in result["nodes"]} == {"class-auth", "method-login"}
    assert LocalGraphStore(settings.data_dir).get("demo") == demo_graph()
    assert seeded.post("/projects/import", json=demo_graph().model_dump()).status_code == 409
    assert not list((settings.data_dir / "graphs").glob("*.tmp"))


def test_dependency_direction_depth_and_cycles(seeded):
    result = seeded.get("/projects/demo/dependencies/method-find", params={"direction": "upstream"}).json()
    assert result["distances"] == {"method-find": 0, "method-login": 1, "function-login": 2}
    result = seeded.get("/projects/demo/dependencies/function-login", params={"max_depth": 1}).json()
    assert result["distances"] == {"function-login": 0, "method-login": 1}
    assert result["depth_limited"] is True
    assert seeded.get("/projects/demo/dependencies/method-find").json()["distances"] == {"method-find": 0}
    graph = demo_graph().model_dump()
    graph["project_id"] = "cyclic"
    graph["nodes"][0]["id"] = "cyclic"
    for edge in graph["relationships"]:
        if edge["source"] == "demo":
            edge["source"] = "cyclic"
    graph["relationships"].append({"source": "method-find", "target": "function-login", "type": "CALLS"})
    assert seeded.post("/projects/import", json=graph).status_code == 201
    result = seeded.get("/projects/cyclic/dependencies/function-login").json()
    assert len(result["nodes"]) == 3
    assert result["depth_limited"] is False


def test_shortest_paths(seeded):
    url = "/projects/demo/paths"
    params = {"source": "function-login", "target": "method-find"}
    assert seeded.get(url, params=params).json()["node_ids"] == ["function-login", "method-login", "method-find"]
    assert seeded.get(url, params={**params, "max_depth": 1}).json()["found"] is False
    reverse = {"source": "method-find", "target": "function-login"}
    assert seeded.get(url, params=reverse).json()["found"] is False
    assert seeded.get(url, params={**reverse, "directed": False}).json()["found"] is True
    assert seeded.get(url, params={"source": "method-find", "target": "method-find"}).json()["node_ids"] == ["method-find"]


def test_requirement_mapping_and_evidence(seeded):
    requirements = seeded.get("/projects/demo/requirements").json()
    assert [r["mapping_status"] for r in requirements] == ["mapped", "unmapped"]
    trace = seeded.get("/projects/demo/traceability/req-login").json()
    assert trace["implementation_ids"] == ["function-login"]
    assert ["req-login", "function-login", "method-login", "method-find"] in trace["evidence_paths"]
    unmapped = seeded.get("/projects/demo/traceability/req-audit").json()
    assert unmapped["mapping_status"] == "unmapped"
    assert unmapped["evidence_paths"] == []
    assert len(unmapped["nodes"]) == 1
    assert seeded.get("/projects/demo/traceability/class-auth").status_code == 422


def test_project_isolation(seeded):
    isolated = {"project_id": "other", "nodes": [{"id": "other", "name": "Other", "type": "PROJECT"}]}
    assert seeded.post("/projects/import", json=isolated).status_code == 201
    assert seeded.get("/projects/other/dependencies/method-find").status_code == 404
    assert seeded.get("/projects/other/requirements").json() == []
    assert len(seeded.get("/projects/other/graph").json()["nodes"]) == 1
    assert seeded.get("/projects/missing/graph").status_code == 404


def test_portable_storage_ids(client, settings):
    graph = {"project_id": "project:windows", "nodes": [{"id": "project:windows", "name": "Portable", "type": "PROJECT"}]}
    assert client.post("/projects/import", json=graph).status_code == 201
    assert client.get("/projects/project:windows").json()["id"] == "project:windows"
    assert client.get("/projects").json()[0]["id"] == "project:windows"
    assert all(":" not in path.name for path in (settings.data_dir / "graphs").iterdir())


@pytest.mark.parametrize("mutation", ["duplicate_node", "missing_endpoint", "duplicate_edge", "wrong_mapping", "no_project"])
def test_invalid_graph_contract(client, mutation):
    graph = demo_graph().model_dump()
    if mutation == "duplicate_node":
        graph["nodes"].append(graph["nodes"][0])
    elif mutation == "missing_endpoint":
        graph["relationships"][0]["target"] = "missing"
    elif mutation == "duplicate_edge":
        graph["relationships"].append(graph["relationships"][0])
    elif mutation == "wrong_mapping":
        graph["relationships"][-1]["source"] = "method-find"
    else:
        graph["nodes"].pop(0)
    result = client.post("/projects/import", json=graph)
    assert result.status_code == 422
    assert client.get("/projects").json() == []


def test_query_validation(seeded):
    assert seeded.get("/projects/demo/graph?node_type=INVALID").status_code == 422
    assert seeded.get("/projects/demo/dependencies/method-find?max_depth=999").status_code == 422
    assert seeded.get("/projects/demo/dependencies/method-find?direction=sideways").status_code == 422


def test_missing_parser_is_explicit(client):
    result = client.post("/projects/analyze", files={"repository": ("project.zip", zip_bytes([("auth.py", "pass")]))})
    assert result.status_code == 503
    assert result.json()["error"]["code"] == "integration_not_configured"
    assert client.get("/projects").json() == []


def test_upload_parser_mapping_and_cleanup(integrated, settings):
    files = {
        "repository": ("project.zip", zip_bytes([("wrapped/auth.py", "def login(): pass")])),
        "requirements": ("requirements.md", "REQ-001: Login"),
        "mappings": ("mappings.json", json.dumps([{"requirement": "REQ-001", "implementation": "auth.py::login"}])),
    }
    response = integrated.post("/projects/analyze", files=files)
    assert response.status_code == 201, response.text
    project_id = response.json()["id"]
    assert response.json()["source"] == "repository"
    trace = integrated.get(f"/projects/{project_id}/traceability/req").json()
    assert trace["implementation_ids"] == ["login"]
    assert trace["relationships"][0]["properties"]["provenance"] == "manual"
    assert list((settings.data_dir / "uploads").iterdir()) == []


@pytest.mark.parametrize("name", ["../escape.py", "/escape.py", "C:/escape.py", "folder\\escape.py", "CON.py", "folder/../escape.py", "folder./escape.py"])
def test_zip_unsafe_paths(integrated, settings, name):
    response = integrated.post("/projects/analyze", files={"repository": ("project.zip", zip_bytes([(name, "pass")]))})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unsafe_archive"
    assert list((settings.data_dir / "uploads").iterdir()) == []
    assert integrated.get("/projects").json() == []


def test_symlink_case_collision_and_bad_zip(integrated):
    symlink = ZipInfo("link.py")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    for content in [zip_bytes([(symlink, "../outside")]), zip_bytes([("a/file.py", "pass"), ("A/other.py", "pass")]), b"not a ZIP"]:
        assert integrated.post("/projects/analyze", files={"repository": ("project.zip", content)}).status_code == 422


def test_extraction_limits(integrated, settings):
    settings.max_extracted_bytes = 4
    response = integrated.post("/projects/analyze", files={"repository": ("project.zip", zip_bytes([("auth.py", "def login(): pass")]))})
    assert response.status_code == 413
    assert list((settings.data_dir / "uploads").iterdir()) == []


def test_unresolved_mapping_is_atomic(integrated, settings):
    response = integrated.post("/projects/analyze", files={
        "repository": ("project.zip", zip_bytes([("auth.py", "def login(): pass")])),
        "mappings": ("mapping.json", '[{"requirement":"missing","implementation":"login"}]'),
    })
    assert response.status_code == 422
    assert integrated.get("/projects").json() == []
    assert list((settings.data_dir / "uploads").iterdir()) == []


def test_parser_failure_cleans_up(integrated, settings, monkeypatch):
    monkeypatch.setattr("backend.app.analysis.load_plugin", lambda *args: lambda **kwargs: {"invalid": "graph"})
    result = integrated.post("/projects/analyze", files={"repository": ("project.zip", zip_bytes([("auth.py", "pass")]))})
    assert result.status_code == 502
    assert integrated.get("/projects").json() == []
    assert list((settings.data_dir / "uploads").iterdir()) == []


def test_neo4j_unavailable_returns_503(client, monkeypatch):
    def fail():
        raise ServiceUnavailable("Do not expose connection details")
    monkeypatch.setattr(client.app.state.store, "ping", fail)
    result = client.get("/health/ready")
    assert result.status_code == 503
    assert "connection details" not in result.text


def test_cors(client):
    result = client.options("/projects", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert result.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_total_body_limit(client, settings):
    limit = settings.max_upload_bytes + 2 * settings.max_sidecar_bytes + 1024 * 1024
    result = client.post("/projects/import", content=b"x" * (limit + 1), headers={"Content-Type": "application/json"})
    assert result.status_code == 413


def test_multipart_body_limit(client, settings):
    limit = settings.max_upload_bytes + 2 * settings.max_sidecar_bytes + 1024 * 1024
    result = client.post("/projects/analyze", files={"repository": ("project.zip", b"x" * limit)})
    assert result.status_code == 413


@pytest.mark.parametrize("mappings", ["not json", "{}", '[{"requirement":"REQ-001"}]'])
def test_invalid_mapping_file(integrated, mappings):
    result = integrated.post("/projects/analyze", files={
        "repository": ("project.zip", zip_bytes([("auth.py", "def login(): pass")])),
        "mappings": ("mapping.json", mappings),
    })
    assert result.status_code == 422
    assert integrated.get("/projects").json() == []

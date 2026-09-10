"""Generate a clearly labeled hand-authored graph and a ZIP for parser integration."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from backend.app.models import ArtifactGraph, Node, Relationship


def demo_graph() -> ArtifactGraph:
    nodes = [
        Node(id="demo", type="PROJECT", name="Authentication demo", properties={"source": "hand_authored_demo"}),
        Node(id="file-controller", type="FILE", name="controller.py", properties={"reference": "controller.py"}),
        Node(id="file-auth", type="FILE", name="auth.py", properties={"reference": "auth.py"}),
        Node(id="file-repository", type="FILE", name="repository.py", properties={"reference": "repository.py"}),
        Node(id="class-auth", type="CLASS", name="AuthService", properties={"reference": "auth.py::AuthService", "path": "auth.py", "line_start": 4}),
        Node(id="class-repository", type="CLASS", name="UserRepository", properties={"reference": "repository.py::UserRepository", "path": "repository.py", "line_start": 1}),
        Node(id="function-login", type="FUNCTION", name="login_user", properties={"reference": "controller.py::login_user", "path": "controller.py", "line_start": 5}),
        Node(id="method-login", type="METHOD", name="AuthService.login", properties={"reference": "auth.py::AuthService.login", "path": "auth.py", "line_start": 8}),
        Node(id="method-find", type="METHOD", name="UserRepository.find", properties={"reference": "repository.py::UserRepository.find", "path": "repository.py", "line_start": 2}),
        Node(id="req-login", type="REQUIREMENT", name="REQ-001: User lookup", properties={"reference": "REQ-001", "category": "functional", "description": "Check whether a username exists through the login entry point.", "actor": "User"}),
        Node(id="req-audit", type="REQUIREMENT", name="REQ-002: Audit history", properties={"reference": "REQ-002", "category": "functional", "description": "Record each login attempt.", "actor": "Administrator"}),
        Node(id="readme", type="DOCUMENT", name="README.md", properties={"path": "README.md"}),
    ]
    triples = [
        ("demo", "CONTAINS", "file-controller"), ("demo", "CONTAINS", "file-auth"),
        ("demo", "CONTAINS", "file-repository"), ("demo", "CONTAINS", "req-login"),
        ("demo", "CONTAINS", "req-audit"), ("demo", "CONTAINS", "readme"),
        ("file-controller", "CONTAINS", "function-login"), ("file-auth", "CONTAINS", "class-auth"),
        ("file-repository", "CONTAINS", "class-repository"), ("class-auth", "CONTAINS", "method-login"),
        ("class-repository", "CONTAINS", "method-find"), ("file-controller", "IMPORTS", "file-auth"),
        ("file-controller", "IMPORTS", "file-repository"), ("file-auth", "IMPORTS", "file-repository"),
        ("function-login", "CALLS", "method-login"), ("method-login", "CALLS", "method-find"),
        ("class-auth", "DEPENDS_ON", "class-repository"), ("req-login", "IMPLEMENTED_BY", "function-login"),
    ]
    edges = [Relationship(source=source, type=kind, target=target,
                          properties={"provenance": "manual" if kind == "IMPLEMENTED_BY" else "hand_authored_demo"})
             for source, kind, target in triples]
    return ArtifactGraph(project_id="demo", nodes=nodes, relationships=edges)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with (root / "sample_data" / "demo_graph.json").open("w", encoding="utf-8", newline="\n") as file:
        file.write(demo_graph().model_dump_json(indent=2) + "\n")
    output = root / ".data" / "sample_project.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted((root / "sample_project").rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(root / "sample_project").as_posix())
    print("Created sample_data/demo_graph.json (hand-authored fixture) and .data/sample_project.zip")

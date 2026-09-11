"""
Generate a hand-authored demo ArtifactGraph and a sample project ZIP.

Usage:
    python -m scripts.make_demo

Outputs:
    .data/demo_graph.json       — hand-authored fixture for POST /projects/import
    .data/sample_project.zip    — ZIP of sample_project/ for POST /projects/analyze
"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from backend.app.models import ArtifactGraph, Node, Relationship


def demo_graph() -> ArtifactGraph:
    """
    Hand-authored ArtifactGraph for the sample e-commerce project.
    Import via: POST /projects/import
    """
    nodes = [
        Node(id="demo", type="PROJECT", name="E-Commerce Demo", properties={"source": "hand_authored"}),

        # Files
        Node(id="file-auth",       type="FILE", name="auth_service.py",   properties={"reference": "src/auth_service.py",   "path": "src/auth_service.py",   "language": "python"}),
        Node(id="file-order",      type="FILE", name="order_service.py",  properties={"reference": "src/order_service.py",  "path": "src/order_service.py",  "language": "python"}),
        Node(id="file-repo",       type="FILE", name="user_repository.py",properties={"reference": "src/user_repository.py","path": "src/user_repository.py","language": "python"}),
        Node(id="file-payment",    type="FILE", name="payment_service.js",properties={"reference": "frontend/payment_service.js","path": "frontend/payment_service.js","language": "javascript"}),

        # Classes
        Node(id="class-auth",      type="CLASS", name="AuthService",      properties={"reference": "src/auth_service.py::AuthService",    "path": "src/auth_service.py"}),
        Node(id="class-order",     type="CLASS", name="OrderService",     properties={"reference": "src/order_service.py::OrderService",   "path": "src/order_service.py"}),
        Node(id="class-repo",      type="CLASS", name="UserRepository",   properties={"reference": "src/user_repository.py::UserRepository","path": "src/user_repository.py"}),
        Node(id="class-payment",   type="CLASS", name="PaymentService",   properties={"reference": "frontend/payment_service.js::PaymentService","path": "frontend/payment_service.js"}),

        # Methods
        Node(id="fn-login",        type="FUNCTION", name="login",         properties={"reference": "src/auth_service.py::AuthService.login",        "path": "src/auth_service.py"}),
        Node(id="fn-create-order", type="FUNCTION", name="create_order",  properties={"reference": "src/order_service.py::OrderService.create_order","path": "src/order_service.py"}),
        Node(id="fn-find-user",    type="FUNCTION", name="find_by_email", properties={"reference": "src/user_repository.py::UserRepository.find_by_email","path": "src/user_repository.py"}),
        Node(id="fn-process",      type="FUNCTION", name="processPayment",properties={"reference": "frontend/payment_service.js::PaymentService.processPayment","path": "frontend/payment_service.js"}),

        # Requirements
        Node(id="req-001", type="REQUIREMENT", name="User Authentication",
             properties={"reference": "REQ-001", "description": "Users shall authenticate via email and password.", "category": "functional"}),
        Node(id="req-002", type="REQUIREMENT", name="Order Creation",
             properties={"reference": "REQ-002", "description": "Authenticated users shall create orders.", "category": "functional"}),

        # Document
        Node(id="readme", type="DOCUMENT", name="README.md", properties={"path": "README.md"}),
    ]

    triples = [
        # Project → contents
        ("demo", "CONTAINS", "file-auth"),
        ("demo", "CONTAINS", "file-order"),
        ("demo", "CONTAINS", "file-repo"),
        ("demo", "CONTAINS", "file-payment"),
        ("demo", "CONTAINS", "req-001"),
        ("demo", "CONTAINS", "req-002"),
        ("demo", "DOCUMENTED_BY", "readme"),

        # Files → classes
        ("file-auth",    "CONTAINS", "class-auth"),
        ("file-order",   "CONTAINS", "class-order"),
        ("file-repo",    "CONTAINS", "class-repo"),
        ("file-payment", "CONTAINS", "class-payment"),

        # Classes → methods
        ("class-auth",    "CONTAINS", "fn-login"),
        ("class-order",   "CONTAINS", "fn-create-order"),
        ("class-repo",    "CONTAINS", "fn-find-user"),
        ("class-payment", "CONTAINS", "fn-process"),

        # Imports
        ("file-auth",  "IMPORTS", "file-repo"),
        ("file-order", "IMPORTS", "file-repo"),

        # Calls
        ("fn-login",        "CALLS", "fn-find-user"),
        ("fn-create-order", "CALLS", "fn-find-user"),

        # Traceability
        ("req-001", "IMPLEMENTED_BY", "fn-login"),
        ("req-002", "IMPLEMENTED_BY", "fn-create-order"),
    ]

    edges = [
        Relationship(
            source=src, target=tgt, type=kind,
            properties={"provenance": "manual" if kind == "IMPLEMENTED_BY" else "hand_authored"},
        )
        for src, kind, tgt in triples
    ]

    return ArtifactGraph(project_id="demo", nodes=nodes, relationships=edges)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output_dir = root / ".data"
    output_dir.mkdir(exist_ok=True)

    # Write demo graph JSON (for import endpoint)
    graph_path = output_dir / "demo_graph.json"
    graph_path.write_text(demo_graph().model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Created {graph_path.relative_to(root)}")

    # Write sample_project ZIP (for analyze endpoint)
    zip_path = output_dir / "sample_project.zip"
    sample_dir = root / "sample_project"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(sample_dir.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(sample_dir).as_posix())
    print(f"Created {zip_path.relative_to(root)}")
    print("\nUsage:")
    print(f"  Import graph:   curl -X POST http://localhost:8000/projects/import -H 'Content-Type: application/json' -d @{graph_path}")
    print(f"  Analyze ZIP:    curl -X POST http://localhost:8000/projects/analyze -F 'repository=@{zip_path}'")

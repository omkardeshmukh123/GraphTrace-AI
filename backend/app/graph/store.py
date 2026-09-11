import json
import os
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Protocol

from pydantic import TypeAdapter

from backend.app.config import Settings
from backend.app.errors import AppError
from backend.app.models import ArtifactGraph, Identifier, ProjectSummary
from backend.app.plugins import load_plugin


def summarize(graph: ArtifactGraph) -> ProjectSummary:
    project = next(node for node in graph.nodes if node.id == graph.project_id)
    return ProjectSummary(
        id=graph.project_id, name=project.name, node_count=len(graph.nodes),
        relationship_count=len(graph.relationships),
        counts=dict(Counter(node.type for node in graph.nodes)),
        source=str(project.properties.get("source", "import")),
    )


class GraphStore(Protocol):
    def get(self, project_id: str) -> ArtifactGraph: ...
    def save(self, graph: ArtifactGraph) -> None: ...
    def list_projects(self) -> list[ProjectSummary]: ...
    def check_writable(self) -> None: ...
    def ping(self) -> None: ...
    def close(self) -> None: ...


class LocalGraphStore:
    """Persistent development adapter. A graph is published only after a complete write."""

    def __init__(self, data_dir: Path):
        self.directory = data_dir.resolve() / "graphs"
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, project_id: str) -> Path:
        TypeAdapter(Identifier).validate_python(project_id)
        # IDs may contain colons; never interpret them as Windows stream names.
        digest = sha256(project_id.encode("utf-8")).hexdigest()
        return self.directory / f"graph-{digest}.json"

    def get(self, project_id: str) -> ArtifactGraph:
        try:
            return ArtifactGraph.model_validate_json(self._path(project_id).read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise AppError(404, "project_not_found", "Project does not exist.") from exc

    def save(self, graph: ArtifactGraph) -> None:
        target = self._path(graph.project_id)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory, suffix=".tmp", delete=False) as file:
            temporary = Path(file.name)
            try:
                file.write(graph.model_dump_json(indent=2))
                file.flush()
                os.fsync(file.fileno())
            except Exception:
                file.close()
                temporary.unlink(missing_ok=True)
                raise
        try:
            # An atomic link prevents both partial reads and accidental overwrites.
            # temporary and target are both created inside self.directory on the same filesystem.
            try:
                os.link(temporary, target)
            except (OSError, NotImplementedError) as err:
                if isinstance(err, FileExistsError):
                    raise
                if target.exists():
                    raise FileExistsError
                os.replace(temporary, target)
        except FileExistsError as exc:
            raise AppError(409, "project_exists", "This project ID already exists; use a new project ID.") from exc
        finally:
            temporary.unlink(missing_ok=True)

    def list_projects(self) -> list[ProjectSummary]:
        graphs = [ArtifactGraph.model_validate_json(path.read_text(encoding="utf-8"))
                  for path in self.directory.glob("graph-*.json")]
        return [summarize(graph) for graph in sorted(graphs, key=lambda graph: graph.project_id)]

    def check_writable(self) -> None:
        pass

    def ping(self) -> None:
        if not self.directory.is_dir():
            raise AppError(503, "storage_unavailable", "Local graph directory is unavailable.")

    def close(self) -> None:
        pass


class Neo4jGraphStore:
    """Reads the shared Entity schema; delegates graph writes to the teammate's builder."""

    def __init__(self, settings: Settings):
        from neo4j import GraphDatabase

        self.settings = settings
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
            connection_timeout=5, connection_acquisition_timeout=5,
            max_transaction_retry_time=5,
        )

    def ping(self) -> None:
        self.driver.verify_connectivity()

    def close(self) -> None:
        self.driver.close()

    def check_writable(self) -> None:
        load_plugin(self.settings.graph_writer, "GRAPH_WRITER")
        self.ping()

    def save(self, graph: ArtifactGraph) -> None:
        writer = load_plugin(self.settings.graph_writer, "GRAPH_WRITER")
        writer(graph=graph, driver=self.driver, database=self.settings.neo4j_database)

    def get(self, project_id: str) -> ArtifactGraph:
        # Both reads use one transaction; all endpoints must belong to this project.
        def read(tx):
            nodes = list(tx.run(
                "MATCH (n:Entity {project_id: $project_id}) "
                "RETURN n.id AS id, n.type AS type, n.name AS name, "
                "n.properties_json AS properties_json ORDER BY n.id LIMIT 5001",
                project_id=project_id,
            ))
            if not nodes:
                raise AppError(404, "project_not_found", "Project does not exist.")
            edges = list(tx.run(
                "MATCH (a:Entity {project_id: $project_id})-[r]->(b:Entity {project_id: $project_id}) "
                "RETURN a.id AS source, b.id AS target, type(r) AS type, "
                "r.properties_json AS properties_json ORDER BY a.id, type(r), b.id LIMIT 20001",
                project_id=project_id,
            ))
            if len(nodes) > 5000 or len(edges) > 20000:
                raise AppError(413, "graph_too_large", "This prototype supports 5,000 nodes and 20,000 relationships per project.")
            def decode(record):
                values = dict(record)
                values["properties"] = json.loads(values.pop("properties_json") or "{}")
                return values
            return ArtifactGraph(project_id=project_id, nodes=[decode(n) for n in nodes], relationships=[decode(r) for r in edges])

        with self.driver.session(database=self.settings.neo4j_database) as session:
            return session.execute_read(read)

    def list_projects(self) -> list[ProjectSummary]:
        def read(tx):
            return [row["id"] for row in tx.run(
                "MATCH (p:Entity {type: 'PROJECT'}) WHERE p.id = p.project_id "
                "RETURN p.id AS id ORDER BY p.id"
            )]
        with self.driver.session(database=self.settings.neo4j_database) as session:
            ids = session.execute_read(read)
        return [summarize(self.get(project_id)) for project_id in ids]

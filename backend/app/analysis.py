import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi import UploadFile
from pydantic import TypeAdapter, ValidationError

from backend.app.config import Settings
from backend.app.errors import AppError
from backend.app.graph.store import GraphStore, summarize
from backend.app.models import ArtifactGraph, CODE_TYPES, ManualMapping, Relationship
from backend.app.plugins import load_plugin
from backend.app.uploads import extract_repository, read_sidecar

logger = logging.getLogger(__name__)


def apply_mappings(graph: ArtifactGraph, mappings: list[ManualMapping]) -> ArtifactGraph:
    def resolve(reference: str):
        ref_norm = reference.replace("\\", "/")
        matches = [
            node for node in graph.nodes
            if node.id == reference
            or node.properties.get("reference") == reference
            or (isinstance(node.properties.get("reference"), str) and node.properties["reference"].replace("\\", "/") == ref_norm)
        ]
        if len(matches) != 1:
            raise AppError(422, "mapping_unresolved", f"Mapping reference must identify exactly one node: {reference}")
        return matches[0]

    edges = list(graph.relationships)
    seen = {(edge.source, edge.type, edge.target) for edge in edges}
    for mapping in mappings:
        source, target = resolve(mapping.requirement), resolve(mapping.implementation)
        if source.type != "REQUIREMENT" or target.type not in CODE_TYPES:
            raise AppError(422, "invalid_mapping", "Mappings must connect a requirement to a code entity.")
        key = (source.id, "IMPLEMENTED_BY", target.id)
        if key not in seen:
            edges.append(Relationship(source=source.id, target=target.id, type="IMPLEMENTED_BY", properties={"provenance": "manual"}))
            seen.add(key)
    return ArtifactGraph(project_id=graph.project_id, nodes=graph.nodes, relationships=edges)


def analyze(repository: UploadFile, requirements: UploadFile | None, mappings: UploadFile | None,
            settings: Settings, store: GraphStore):
    parser = load_plugin(settings.parser, "PARSER")
    store.check_writable()
    requirements_text = read_sidecar(requirements, {".md", ".markdown"}, settings.max_sidecar_bytes)
    mappings_text = read_sidecar(mappings, {".json"}, settings.max_sidecar_bytes)
    try:
        manual_mappings = TypeAdapter(list[ManualMapping]).validate_json(mappings_text) if mappings_text is not None else []
    except ValidationError as exc:
        raise AppError(422, "invalid_mappings", "Mappings must be a JSON array of requirement/implementation objects.") from exc
    project_id = uuid4().hex
    uploads = settings.data_dir.resolve() / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    # This directory is created by us underneath the configured data directory;
    # TemporaryDirectory removes only that request's files, even after failures.
    with TemporaryDirectory(prefix="analysis-", dir=uploads) as temporary:
        root = extract_repository(repository, Path(temporary), settings)
        try:
            result = parser(project_id=project_id, repository_root=root, requirements_text=requirements_text)
            graph = ArtifactGraph.model_validate(result)
            if graph.project_id != project_id:
                raise ValueError("Parser returned another project ID")
        except Exception as exc:
            logger.exception("Parser failed for project %s", project_id)
            raise AppError(502, "parser_failed", "Parser failed or returned an invalid artifact graph. Check backend logs.") from exc
        graph = apply_mappings(graph, manual_mappings)
        updated_nodes = [
            node.model_copy(update={"properties": {**node.properties, "source": "repository"}})
            if node.id == project_id else node
            for node in graph.nodes
        ]
        graph = ArtifactGraph(
            schema_version=graph.schema_version,
            project_id=graph.project_id,
            nodes=updated_nodes,
            relationships=graph.relationships,
        )
        store.save(graph)
    return summarize(graph)

from typing import Annotated, Literal

from fastapi import APIRouter, File, Query, Request, UploadFile

from backend.app.analysis import analyze
from backend.app.graph import queries
from backend.app.graph.store import summarize
from backend.app.models import (
    ArtifactGraph, DependencyView, GraphView, Identifier, NodeType, PathView,
    ProjectSummary, RelationshipType, RequirementSummary, TraceabilityView,
)

router = APIRouter()
Types = Annotated[list[RelationshipType] | None, Query()]
Depth = Annotated[int, Query(ge=1, le=10)]


@router.get("/health", tags=["Health"])
def health(request: Request):
    return {"status": "ok", "store": request.app.state.settings.store,
            "parser_configured": bool(request.app.state.settings.parser)}


@router.get("/health/ready", tags=["Health"])
def ready(request: Request):
    request.app.state.store.ping()
    return {"status": "ready", "store": request.app.state.settings.store}


@router.get("/projects", response_model=list[ProjectSummary], tags=["Projects"])
def list_projects(request: Request):
    return request.app.state.store.list_projects()


@router.post("/projects/analyze", response_model=ProjectSummary, status_code=201, tags=["Projects"])
def analyze_project(request: Request, repository: Annotated[UploadFile, File()],
                    requirements: Annotated[UploadFile | None, File()] = None,
                    mappings: Annotated[UploadFile | None, File()] = None):
    """Synchronous small-project analysis. Requires the teammate's configured parser."""
    return analyze(repository, requirements, mappings, request.app.state.settings, request.app.state.store)


@router.post("/projects/import", response_model=ProjectSummary, status_code=201, tags=["Projects"])
def import_project(graph: ArtifactGraph, request: Request):
    """Import the shared JSON contract, including fixtures or externally parsed projects."""
    store = request.app.state.store
    store.check_writable()
    store.save(graph)
    return summarize(graph)


@router.get("/projects/{project_id}", response_model=ProjectSummary, tags=["Projects"])
def project(project_id: Identifier, request: Request):
    return summarize(request.app.state.store.get(project_id))


@router.get("/projects/{project_id}/graph", response_model=GraphView, tags=["Graph"])
def graph(project_id: Identifier, request: Request,
          node_type: Annotated[list[NodeType] | None, Query()] = None,
          relationship_type: Types = None, search: Annotated[str | None, Query(max_length=200)] = None):
    return queries.filter_graph(request.app.state.store.get(project_id), node_type, relationship_type, search)


@router.get("/projects/{project_id}/dependencies/{node_id}", response_model=DependencyView, tags=["Dependencies"])
def dependencies(project_id: Identifier, node_id: Identifier, request: Request,
                 direction: Literal["upstream", "downstream"] = "downstream",
                 max_depth: Depth = 3, relationship_type: Types = None):
    """For A CALLS B: B is downstream of A; A is upstream of B. Root is included."""
    return queries.dependencies(request.app.state.store.get(project_id), node_id, direction, max_depth, relationship_type)


@router.get("/projects/{project_id}/paths", response_model=PathView, tags=["Dependencies"])
def paths(project_id: Identifier, request: Request, source: Identifier, target: Identifier,
          max_depth: Depth = 6, directed: bool = True, relationship_type: Types = None):
    """Return one shortest path within max_depth. Empty paths are not proof of disconnection."""
    return queries.shortest_path(request.app.state.store.get(project_id), source, target, max_depth, directed, relationship_type)


@router.get("/projects/{project_id}/requirements", response_model=list[RequirementSummary], tags=["Requirements"])
def requirements(project_id: Identifier, request: Request):
    return queries.requirements(request.app.state.store.get(project_id))


@router.get("/projects/{project_id}/traceability/{requirement_id}", response_model=TraceabilityView, tags=["Requirements"])
def traceability(project_id: Identifier, requirement_id: Identifier, request: Request, max_depth: Depth = 5):
    return queries.traceability(request.app.state.store.get(project_id), requirement_id, max_depth)

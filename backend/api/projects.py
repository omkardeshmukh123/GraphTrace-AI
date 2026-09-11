"""
API — Projects Router
======================
Endpoints for project upload and analysis.

POST /projects/upload        — Accept a ZIP file, save it, return project_id
POST /projects/{id}/analyze  — Trigger M1 parsing + M2 graph build
GET  /projects/              — List all analyzed projects
GET  /projects/{id}/status   — Get project metadata / analysis status
"""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from artifact_intelligence import ArtifactAnalyzer
from knowledge_graph import KnowledgeGraphBuilder, GraphQueryEngine
from config import settings

router = APIRouter(prefix="/projects", tags=["Projects"])

# In-memory project state store (Phase 1; replace with DB in Phase 2+)
_project_store: dict[str, dict] = {}


# ─── Request / Response models ────────────────────────────────────────────────

class UploadResponse(BaseModel):
    project_id: str
    filename: str
    size_bytes: int
    message: str


class AnalyzeResponse(BaseModel):
    project_id: str
    project_name: str
    nodes_created: int
    nodes_updated: int
    relationships_created: int
    success: bool
    errors: list[str]
    summary: dict


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_project(file: UploadFile = File(...)):
    """
    Upload a project ZIP file.
    Returns a project_id that you use for /analyze.
    """
    # Validate file type
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted.")

    file_bytes = await file.read()
    size_bytes = len(file_bytes)

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.max_upload_size_mb} MB.",
        )

    # Run M1 analysis (includes extraction)
    analyzer = ArtifactAnalyzer(
        upload_dir=settings.upload_dir,
        extracted_dir=settings.extracted_dir,
    )
    artifact_data = analyzer.analyze_zip(file_bytes, file.filename)
    project_id = artifact_data.metadata["project_id"]

    # Store for later retrieval
    _project_store[project_id] = {
        "project_id": project_id,
        "filename": file.filename,
        "size_bytes": size_bytes,
        "status": "uploaded",
        "artifact_data": artifact_data,
    }

    return UploadResponse(
        project_id=project_id,
        filename=file.filename,
        size_bytes=size_bytes,
        message=f"Uploaded successfully. Use POST /projects/{project_id}/analyze to build the graph.",
    )


@router.post("/{project_id}/analyze", response_model=AnalyzeResponse)
async def analyze_project(project_id: str):
    """
    Trigger M1 parsing + M2 graph build for an uploaded project.
    """
    if project_id not in _project_store:
        raise HTTPException(status_code=404, detail=f"Project {project_id!r} not found. Upload first.")

    store_entry = _project_store[project_id]
    artifact_data = store_entry.get("artifact_data")

    if artifact_data is None:
        raise HTTPException(status_code=500, detail="Artifact data missing from store.")

    # Run M2 graph build
    builder = KnowledgeGraphBuilder()
    build_result = builder.build(artifact_data)

    # Update store
    _project_store[project_id]["status"] = "analyzed" if build_result.success else "error"
    _project_store[project_id]["build_result"] = build_result

    # Node count summary
    query_engine = GraphQueryEngine()
    stats = query_engine.get_stats(project_id)

    return AnalyzeResponse(
        project_id=project_id,
        project_name=artifact_data.metadata.get("project_name", "Unknown"),
        nodes_created=build_result.nodes_created,
        nodes_updated=build_result.nodes_updated,
        relationships_created=build_result.relationships_created,
        success=build_result.success,
        errors=build_result.errors,
        summary=stats,
    )


@router.get("/", summary="List all analyzed projects")
async def list_projects():
    """Return all Repository nodes from the graph."""
    query_engine = GraphQueryEngine()
    projects = query_engine.list_projects()
    return {"projects": projects, "count": len(projects)}


@router.get("/{project_id}/status")
async def project_status(project_id: str):
    """Get analysis status and metadata for a project."""
    # Check local store first
    if project_id in _project_store:
        store_entry = _project_store[project_id]
        return {
            "project_id": project_id,
            "status": store_entry.get("status", "unknown"),
            "filename": store_entry.get("filename"),
            "metadata": store_entry.get("artifact_data", {}).metadata
            if store_entry.get("artifact_data") else {},
        }

    # Check graph (project analyzed in a previous session)
    query_engine = GraphQueryEngine()
    node = query_engine.get_node(f"repository:{project_id}")
    if node:
        return {"project_id": project_id, "status": "analyzed", "node": node}

    raise HTTPException(status_code=404, detail=f"Project {project_id!r} not found.")

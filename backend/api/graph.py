"""
API — Graph Router
===================
Endpoints for querying the Knowledge Graph.
These are the endpoints M4 (Frontend) will call to render visualizations.

GET /projects/{id}/graph      — All nodes + edges (for graph visualization)
GET /projects/{id}/stats      — Node counts by type (for dashboard)
GET /projects/{id}/tree       — Hierarchical tree view
GET /entities/{id}            — Single entity detail
GET /entities/{id}/children   — Direct children via CONTAINS / DEFINES
"""

from fastapi import APIRouter, HTTPException
from knowledge_graph import GraphQueryEngine

router = APIRouter(tags=["Graph"])
_query_engine = GraphQueryEngine()


# ─── Project-level graph endpoints ───────────────────────────────────────────

@router.get("/projects/{project_id}/graph", summary="Get full graph data for visualization")
async def get_graph(project_id: str):
    """
    Returns all nodes and edges for a project.
    Format is ready for React Flow / Cytoscape.js consumption by M4.
    """
    data = _query_engine.get_graph_data(project_id)
    if not data["nodes"]:
        raise HTTPException(
            status_code=404,
            detail=f"No graph data found for project {project_id!r}. Has it been analyzed?"
        )
    return {
        "project_id": project_id,
        "node_count": len(data["nodes"]),
        "edge_count": len(data["edges"]),
        "nodes": data["nodes"],
        "edges": data["edges"],
    }


@router.get("/projects/{project_id}/stats", summary="Get node counts by type")
async def get_stats(project_id: str):
    """
    Returns node counts per type — used by the dashboard summary panel.
    Example: { "File": 12, "Class": 8, "Function": 34, "_total_relationships": 67 }
    """
    stats = _query_engine.get_stats(project_id)
    return {"project_id": project_id, "stats": stats}


@router.get("/projects/{project_id}/tree", summary="Get hierarchical project tree")
async def get_tree(project_id: str):
    """
    Returns a nested tree: Repository → Folders → Files → Classes/Functions.
    Used for the tree-panel sidebar in the frontend.
    """
    tree = _query_engine.get_project_tree(project_id)
    if tree is None:
        raise HTTPException(
            status_code=404,
            detail=f"Project {project_id!r} not found in graph."
        )
    return {"project_id": project_id, "tree": tree}


# ─── Entity-level endpoints ───────────────────────────────────────────────────

@router.get("/entities/{entity_id:path}", summary="Get a single entity's details")
async def get_entity(entity_id: str):
    """
    Fetch full details for any entity by its id.
    entity_id can contain slashes (e.g. "class:proj:src/auth.py:AuthService")
    — handled by the :path converter.
    """
    node = _query_engine.get_node(entity_id)
    if node is None:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id!r} not found.")
    return node


@router.get("/entities/{entity_id:path}/children", summary="Get direct children of an entity")
async def get_children(entity_id: str):
    """
    Returns all nodes directly CONTAINS or DEFINES children of the given entity.
    Used for click-to-expand in the frontend tree.
    """
    children = _query_engine.get_children(entity_id)
    return {
        "entity_id": entity_id,
        "children": children,
        "count": len(children),
    }

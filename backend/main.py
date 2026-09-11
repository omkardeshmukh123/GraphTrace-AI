"""
GraphTrace AI — FastAPI Entry Point
=====================================
Starts the backend server, mounts all routers, and runs Neo4j schema setup
on startup.

Run with:
    uvicorn main:app --reload --port 8000

Swagger UI available at: http://localhost:8000/docs
ReDoc available at:      http://localhost:8000/redoc
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from knowledge_graph.connection import get_driver, close_driver
from knowledge_graph.schema import run_schema_setup
from api.projects import router as projects_router
from api.graph import router as graph_router


# ─── Lifespan (startup / shutdown) ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic."""
    print(f"\n{'='*50}")
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"{'='*50}\n")

    # Ensure storage directories exist
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.extracted_dir).mkdir(parents=True, exist_ok=True)
    print(f"[Startup] Storage dirs ready: {settings.upload_dir}/, {settings.extracted_dir}/")

    # Connect to Neo4j + run schema setup
    try:
        driver = get_driver()
        run_schema_setup(driver)
        print("[Startup] Neo4j connected and schema ready ✓")
    except Exception as e:
        print(f"[Startup] WARNING: Neo4j connection failed: {e}")
        print("[Startup] App will start, but graph endpoints will fail until Neo4j is reachable.")
        print("[Startup] → Copy backend/.env.example to backend/.env and fill in your AuraDB credentials.")

    yield  # Server is running

    # Shutdown
    close_driver()
    print("[Shutdown] Neo4j driver closed.")


# ─── App factory ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "GraphTrace AI Backend API — "
        "Converts software artifacts into a Knowledge Graph "
        "and provides traceability, dependency analysis, and explainable intelligence."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── CORS (for M4 React frontend) ────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(projects_router)
app.include_router(graph_router)


# ─── Health check ────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Check connectivity to Neo4j."""
    try:
        driver = get_driver()
        driver.verify_connectivity()
        neo4j_status = "connected"
    except Exception as e:
        neo4j_status = f"error: {e}"

    return {
        "status": "ok" if neo4j_status == "connected" else "degraded",
        "neo4j": neo4j_status,
    }

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired
from starlette.exceptions import HTTPException

from backend.app.api.routes import router
from backend.app.config import Settings
from backend.app.errors import AppError
from backend.app.graph.store import GraphStore, LocalGraphStore, Neo4jGraphStore

logger = logging.getLogger(__name__)


class RequestSizeLimit:
    """Bound the body during reading, including multipart uploads without Content-Length."""

    def __init__(self, app, limit: int):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        size = 0

        async def limited_receive():
            nonlocal size
            message = await receive()
            if message["type"] == "http.request":
                size += len(message.get("body", b""))
                if size > self.limit:
                    raise HTTPException(413, "Request body exceeds the configured limit.")
            return message

        await self.app(scope, limited_receive, send)


def create_app(settings: Settings | None = None, store: GraphStore | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(application):
        application.state.store = store or (LocalGraphStore(settings.data_dir) if settings.store == "local" else Neo4jGraphStore(settings))
        try:
            yield
        finally:
            application.state.store.close()

    application = FastAPI(title="GraphTrace AI Backend", version="0.1.0", lifespan=lifespan,
                          description="Phase 1–3 graph, dependency, and manual requirement traceability APIs.")
    application.state.settings = settings
    application.add_middleware(RequestSizeLimit, limit=settings.max_upload_bytes + 2 * settings.max_sidecar_bytes + 1024 * 1024)
    application.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                               allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @application.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        issues = [{"location": list(issue["loc"]), "message": issue["msg"]} for issue in exc.errors()]
        return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": "Request validation failed.", "issues": issues}})

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"error": {"code": "http_error", "message": str(exc.detail)}})

    async def database_error(request: Request, exc: Exception):
        logger.error("Neo4j operation failed", exc_info=exc)
        return JSONResponse(status_code=503, content={"error": {"code": "graph_unavailable", "message": "Neo4j is unavailable or its schema/configuration is invalid. Check backend logs."}})

    for error_type in (Neo4jError, ServiceUnavailable, SessionExpired):
        application.add_exception_handler(error_type, database_error)

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.error("Unexpected backend error", exc_info=exc)
        return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "Unexpected backend error. Check backend logs."}})

    application.include_router(router)
    return application


app = create_app()

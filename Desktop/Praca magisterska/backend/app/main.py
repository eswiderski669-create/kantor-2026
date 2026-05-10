# FastAPI: async server, request/response validation, and auto-generated OpenAPI documentation.

from fastapi import FastAPI

from app.api.v1 import health
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="RAG API for master's thesis project (WWSI).",
)
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/api/v1/health",
    }

"""
CrimeNet Intelligence Platform — FastAPI Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.postgres import AsyncSessionLocal, create_tables
from app.db.neo4j import ensure_constraints, close_driver
from app.api import auth, cases, documents, graph, investigation
from app.services.auth import AuthService

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    logger.info("Starting CrimeNet backend...")
    # Create PostgreSQL tables (idempotent)
    try:
        await create_tables()
        logger.info("PostgreSQL tables ready")
        if settings.auth_disabled:
            async with AsyncSessionLocal() as db:
                await AuthService.get_demo_user(db)
                await db.commit()
            logger.info("Local demo access enabled (no sign-in required)")
    except Exception as e:
        logger.error(f"PostgreSQL startup error: {e}")

    # Create Neo4j constraints
    try:
        await ensure_constraints()
        logger.info("Neo4j constraints ready")
    except Exception as e:
        logger.warning(f"Neo4j startup warning (will retry on use): {e}")

    yield

    # Shutdown
    await close_driver()
    logger.info("CrimeNet backend stopped")


app = FastAPI(
    title="CrimeNet Intelligence Platform",
    description="AI-Driven Criminal Network Intelligence Through Multimodal Knowledge Graphs",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


# Health check
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "crimenet-backend"}


# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(investigation.router, prefix="/api")

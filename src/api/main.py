"""
FastAPI application entry point.

Start with:
    uvicorn src.api.main:app --reload --port 8000

Or via CLI:
    python main.py --api
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.history import router as history_router
from src.api.routes.research import router as research_router
from src.utils.config import Config
from src.utils.tracing import setup_tracing

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("Starting Intelligent Research Agent API…")
    Config.validate()
    setup_tracing()

    # Ensure data directories exist
    Config.get_data_dir()
    Config.get_output_path("_init")   # creates outputs/ if missing

    # Pre-warm the SQLite schema
    from src.memory.db import init_db
    init_db()
    logger.info("SQLite DB ready at %s", Config.SQLITE_DB_PATH)

    logger.info(
        "API ready on %s:%s — docs at http://%s:%s/docs",
        Config.API_HOST, Config.API_PORT,
        Config.API_HOST, Config.API_PORT,
    )
    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("API shutting down.")


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Intelligent Research Agent API",
    description=(
        "Multi-agent AI research platform. "
        "POST a topic → get a live WebSocket stream of agent activity → "
        "receive a fully structured, cited, fact-checked report."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS — allow the React dev server (localhost:5173) and production build
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:4173",   # Vite preview
        "http://localhost:3000",   # Create-React-App fallback
        "http://localhost:80",     # nginx in Docker
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request timing middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed:.1f}"
    return response


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception for %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(research_router, prefix="/api/v1", tags=["Research"])
app.include_router(history_router,  prefix="/api/v1", tags=["Reports"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "model":  Config.MODEL_NAME,
        "db":     Config.SQLITE_DB_PATH,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Intelligent Research Agent API v2",
        "docs":    "/docs",
        "health":  "/health",
    }

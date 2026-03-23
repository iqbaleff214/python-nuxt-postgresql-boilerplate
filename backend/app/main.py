import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import run_migrations
from app.core.seed import seed_superadmin
from app.core.redis import (
    init_arq_pool,
    close_arq_pool,
    init_pubsub_pool,
    close_pubsub_pool,
)
from app.core.security import limiter
from app.api.v1.router import v1_router
from app.ws.notifications import ws_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up %s...", settings.APP_NAME)
    try:
        await run_migrations()
        logger.info("Database migrations complete.")
        await seed_superadmin()
    except Exception as exc:
        logger.warning("Migration failed (may be OK if DB not ready): %s", exc)

    await init_pubsub_pool()
    await init_arq_pool()
    logger.info("Redis pools initialized.")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_arq_pool()
    await close_pubsub_pool()
    logger.info("Redis pools closed.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI boilerplate with auth, 2FA, notifications, and more.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"] if loc != "body"),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
            "data": None,
            "meta": None,
        },
    )


@app.exception_handler(status.HTTP_429_TOO_MANY_REQUESTS)
async def too_many_requests_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "message": "Too many requests. Please slow down.",
            "errors": None,
            "data": None,
            "meta": None,
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": None,
            "data": None,
            "meta": None,
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(v1_router)
app.include_router(ws_router)

# ── Static files (local storage) ──────────────────────────────────────────────
if settings.STORAGE_BACKEND == "local":
    import os
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.STORAGE_PATH), name="static")


@app.get("/health", tags=["health"])
async def health_check():
    return {"success": True, "message": "OK", "data": {"status": "healthy"}}

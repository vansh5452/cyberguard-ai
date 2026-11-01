"""
CyberGuard AI API - FastAPI application entrypoint.

Frontend -> REST API -> FastAPI Backend -> Prediction Service ->
Existing ML Model (TF-IDF + Logistic Regression) -> Database / API Response
"""
import time
from contextlib import asynccontextmanager

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import analytics, auth, health, model, predictions, safety, simulator
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limit import _prune_stale, is_allowed
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(f"{settings.APP_NAME} starting up (environment={settings.ENVIRONMENT})")
    yield
    logger.info(f"{settings.APP_NAME} shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Cyberbullying Detection System - REST API backend "
                 "wrapping the existing TF-IDF + Logistic Regression model.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- lifecycle


# ------------------------------------------------------------ error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Our routes raise HTTPException(detail={"code":..., "message":...});
    # normalize plain-string details too so every error follows one format.
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        payload = {"success": False, "error": detail}
    else:
        payload = {"success": False, "error": {"code": "HTTP_ERROR", "message": str(detail)}}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak internal stack traces to the client.
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        },
    )


# --------------------------------------------------------------- middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.time() - start) * 1000:.1f}"
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Health checks and interactive docs are exempt so local dev / uptime
    # monitors never get throttled by RATE_LIMIT_PER_MINUTE.
    exempt_paths = (f"{settings.API_V1_PREFIX}/health", "/docs", "/redoc", "/openapi.json")
    if request.url.path.startswith(exempt_paths):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    if not is_allowed(client_ip):
        _prune_stale()
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMITED",
                    "message": f"Too many requests. Limit is {settings.RATE_LIMIT_PER_MINUTE} per minute.",
                },
            },
        )
    return await call_next(request)


# ------------------------------------------------------------------ routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(model.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulator.router, prefix=settings.API_V1_PREFIX)
app.include_router(safety.router, prefix=settings.API_V1_PREFIX)


# Mount static frontend dashboard if available
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend_static")

    @app.get("/dashboard", include_in_schema=False)
    def dashboard():
        return FileResponse(str(frontend_dir / "index.html"))


@app.get("/", tags=["Health"], summary="Root")
def root():
    if frontend_dir.exists() and (frontend_dir / "index.html").exists():
        return FileResponse(str(frontend_dir / "index.html"))
    return {"service": settings.APP_NAME, "docs": "/docs", "health": f"{settings.API_V1_PREFIX}/health"}

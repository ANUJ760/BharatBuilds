"""BharatBuilds API — entrypoint.

Includes:
- Centralized structured logging setup (JSON logs)
- Request ID tracing middleware (propagating X-Request-ID)
- Global exception handlers returning consistent JSON error shapes:
  {"error": ..., "message": ..., "detail": ..., "request_id": ...}
- Core routers for apps, deployment, sharing, and timeline
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.routes_apps import router as apps_router
from backend.api.routes_deploy import router as deploy_router
from backend.api.routes_maintenance import router as maintenance_router
from backend.api.routes_share import router as share_router
from backend.api.routes_timeline import router as timeline_router
from backend.config import Settings, get_settings
from backend.logger import configure_logging, get_logger

from fastapi.middleware.cors import CORSMiddleware

# Initialize structured logging
configure_logging()
logger = get_logger("bharatbuilds.api")

app = FastAPI(
    title="BharatBuilds API",
    version="0.1.0",
    description="A cloud for small software — prompt to live app in under a minute.",
)

# ── CORS Middleware ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ── Request ID Middleware ─────────────────────────────────────────────────


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Assign or propagate a unique X-Request-ID and bind to structured logger."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Exception Handlers ───────────────────────────────────────────────────


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard HTTPExceptions with consistent JSON error shape."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.warning(
        "HTTPException raised",
        status_code=exc.status_code,
        detail=str(exc.detail),
        path=request.url.path,
        request_id=request_id,
    )
    detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    headers = dict(exc.headers) if exc.headers else {}
    headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": detail_msg,
            "detail": exc.detail,
            "request_id": request_id,
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request payload validation errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request parameters or payload",
            "detail": exc.errors(),
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler returning 500 with request_id."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(
        "Unhandled server error",
        error=str(exc),
        path=request.url.path,
        request_id=request_id,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request",
            "detail": str(exc),
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


# ── Routers ──────────────────────────────────────────────────────────────
app.include_router(apps_router)
app.include_router(deploy_router)
app.include_router(maintenance_router)
app.include_router(share_router)
app.include_router(timeline_router)



# ── Health ───────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """Liveness check.

    Also reports which required config values are present (booleans only —
    actual values are never echoed).
    """
    try:
        settings: Settings = get_settings()
        config_present = {
            "aws_region": bool(settings.aws_region),
            "bedrock_model_id": bool(settings.bedrock_model_id),
            "dynamodb_table_name": bool(settings.dynamodb_table_name),
            "s3_assets_bucket": bool(settings.s3_assets_bucket),
            "cognito_user_pool_id": bool(settings.cognito_user_pool_id),
            "cognito_app_client_id": bool(settings.cognito_app_client_id),
            "ses_sender_email": bool(settings.ses_sender_email),
            "deploy_lambda_function_name": bool(
                settings.deploy_lambda_function_name
            ),
        }
        return {"status": "ok", "config": config_present}
    except Exception:
        return {"status": "ok", "config": "not_loaded"}

"""BharatBuilds API — entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.routes_apps import router as apps_router
from backend.api.routes_deploy import router as deploy_router
from backend.api.routes_timeline import router as timeline_router
from backend.config import Settings, get_settings

app = FastAPI(
    title="BharatBuilds API",
    version="0.1.0",
    description="A cloud for small software — prompt to live app in under a minute.",
)

# ── Routers ──────────────────────────────────────────────────────────────
app.include_router(apps_router)
app.include_router(deploy_router)
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

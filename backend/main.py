"""BharatBuilds API — entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from backend.config import Settings, get_settings

app = FastAPI(
    title="BharatBuilds API",
    version="0.1.0",
    description="A cloud for small software — prompt to live app in under a minute.",
)


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
        # Settings validation failed — still return a healthy status
        # but signal that config is not loaded.
        return {"status": "ok", "config": "not_loaded"}

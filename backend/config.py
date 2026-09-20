"""Centralized settings loader with env validation.

Reads configuration from environment variables (or a .env file via
python-dotenv). Every required AWS resource ID is validated at startup —
a missing value raises a clear error, not a silent ``None``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — all values sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── AWS ──────────────────────────────────────────────────────────────
    aws_region: str = Field(default="ap-south-1", description="AWS region")
    aws_profile: str = Field(default="", description="AWS CLI profile name (leave empty to use access keys)")

    # ── Google Gemini ───────────────────────────────────────────────────
    gemini_api_key: str = Field(
        ..., description="Google Gemini API Key"
    )
    gemini_model_id: str = Field(
        default="gemini-2.5-pro",
        description="Gemini model identifier for the agent",
    )

    # ── DynamoDB ─────────────────────────────────────────────────────────
    dynamodb_table_name: str = Field(
        ..., description="DynamoDB table name (app_id PK, step_id SK)"
    )

    # ── S3 ───────────────────────────────────────────────────────────────
    s3_assets_bucket: str = Field(
        ..., description="S3 bucket for generated app assets"
    )

    # ── Cognito ──────────────────────────────────────────────────────────
    cognito_user_pool_id: str = Field(..., description="Cognito User Pool ID")
    cognito_app_client_id: str = Field(..., description="Cognito App Client ID")

    # ── SES ──────────────────────────────────────────────────────────────
    ses_sender_email: str = Field(
        default="", description="Verified SES sender email address"
    )

    # ── Lambda ───────────────────────────────────────────────────────────
    deploy_lambda_function_name: str = Field(
        ..., description="Lambda function name for fast-path deploy"
    )

    # ── App ──────────────────────────────────────────────────────────────
    backend_env: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance (cached after first call)."""
    return Settings()  # type: ignore[call-arg]

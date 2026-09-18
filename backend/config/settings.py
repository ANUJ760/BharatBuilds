"""Application settings and configuration management."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "MicroAgent"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", description="Environment: development, staging, production")
    log_level: str = Field(default="INFO", description="Logging level")

    # AWS Configuration
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_account_id: Optional[str] = Field(default=None, description="AWS account ID")

    # Amazon Bedrock
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="Bedrock model ID for agent",
    )
    bedrock_region: str = Field(default="us-east-1", description="Bedrock region")

    # DynamoDB
    dynamodb_table_name: str = Field(default="microagent-data", description="Main DynamoDB table")
    dynamodb_endpoint_url: Optional[str] = Field(default=None, description="DynamoDB endpoint (local dev)")

    # S3
    s3_bucket_name: str = Field(default="microagent-artifacts", description="S3 bucket for artifacts")
    s3_endpoint_url: Optional[str] = Field(default=None, description="S3 endpoint (local dev)")

    # Cognito
    cognito_region: str = Field(default="us-east-1", description="Cognito region")
    cognito_user_pool_id: str = Field(default="", description="Cognito user pool ID")
    cognito_app_client_id: str = Field(default="", description="Cognito app client ID")
    cognito_app_client_secret: Optional[str] = Field(default=None, description="Cognito app client secret")

    # Google OAuth
    google_client_id: str = Field(default="", description="Google OAuth client ID")
    google_client_secret: str = Field(default="", description="Google OAuth client secret")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/connections/google/callback",
        description="Google OAuth redirect URI",
    )

    # SES
    ses_sender_email: str = Field(default="noreply@microagent.app", description="SES sender email")
    ses_region: str = Field(default="us-east-1", description="SES region")

    # API Configuration
    api_cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )
    api_prefix: str = Field(default="/api", description="API route prefix")

    # Security
    jwt_secret_key: str = Field(default="change-me-in-production", description="JWT signing key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60, description="JWT expiration in minutes")

    # Cedar Authorization
    cedar_policy_store_path: str = Field(
        default="policies/cedar",
        description="Path to Cedar policy files",
    )

    # Workflow Execution
    workflow_timeout_seconds: int = Field(default=300, description="Default workflow timeout")
    max_workflow_steps: int = Field(default=50, description="Maximum workflow steps")

    # Agent Configuration
    agent_max_iterations: int = Field(default=10, description="Maximum agent iterations")
    agent_timeout_seconds: int = Field(default=180, description="Agent execution timeout")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute per user")

    # Feature Flags
    enable_approval_flow: bool = Field(default=True, description="Require approval for sensitive actions")
    enable_timeline: bool = Field(default=True, description="Enable decision timeline tracking")
    enable_snapshots: bool = Field(default=True, description="Enable code snapshots")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

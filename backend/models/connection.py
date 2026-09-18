"""Connection domain model."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConnectionStatus(str, Enum):
    """Connection status."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


class ConnectionProvider(str, Enum):
    """External connection provider."""

    GOOGLE_SHEETS = "google_sheets"
    GOOGLE_DRIVE = "google_drive"
    GOOGLE = "google"


class Connection(BaseModel):
    """External resource connection."""

    connection_id: str = Field(..., description="Unique connection identifier")
    organization_id: str = Field(..., description="Organization owning this connection")
    user_id: str = Field(..., description="User who created the connection")
    provider: ConnectionProvider = Field(..., description="Connection provider")
    resource_id: Optional[str] = Field(None, description="External resource identifier")
    resource_name: Optional[str] = Field(None, description="Human-readable resource name")
    scopes: list[str] = Field(default_factory=list, description="Granted OAuth scopes")
    status: ConnectionStatus = Field(default=ConnectionStatus.ACTIVE, description="Connection status")
    credential_reference: str = Field(..., description="Reference to stored credentials (not the credentials themselves)")
    metadata: dict = Field(default_factory=dict, description="Provider-specific metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Credential expiration timestamp")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True


class ConnectionCreate(BaseModel):
    """Connection creation request."""

    provider: ConnectionProvider
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    scopes: list[str]
    credential_reference: str
    metadata: Optional[dict] = None
    expires_at: Optional[datetime] = None


class ConnectionUpdate(BaseModel):
    """Connection update request."""

    status: Optional[ConnectionStatus] = None
    credential_reference: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[dict] = None

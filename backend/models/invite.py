"""Invite domain model."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from backend.models.user import UserRole


class InviteStatus(str, Enum):
    """Invite status."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invite(BaseModel):
    """App sharing invite."""

    invite_id: str = Field(..., description="Unique invite identifier")
    app_id: str = Field(..., description="App being shared")
    organization_id: str = Field(..., description="Organization owning the app")
    invited_by: str = Field(..., description="User who created the invite")
    email: EmailStr = Field(..., description="Email of invited user")
    role: UserRole = Field(..., description="Role granted by invite")
    status: InviteStatus = Field(default=InviteStatus.PENDING, description="Invite status")
    token: str = Field(..., description="Unique invite token")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    accepted_at: Optional[datetime] = Field(None, description="Acceptance timestamp")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True


class InviteCreate(BaseModel):
    """Invite creation request."""

    app_id: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER


class InviteUpdate(BaseModel):
    """Invite update request."""

    status: Optional[InviteStatus] = None
    accepted_at: Optional[datetime] = None

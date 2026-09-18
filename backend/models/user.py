"""User domain model."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User roles within an organization."""

    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(BaseModel):
    """User entity."""

    user_id: str = Field(..., description="Unique user identifier")
    organization_id: str = Field(..., description="Organization the user belongs to")
    email: EmailStr = Field(..., description="User email address")
    role: UserRole = Field(..., description="User role within organization")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(default=None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Whether user is active")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True


class UserCreate(BaseModel):
    """User creation request."""

    email: EmailStr
    organization_id: str
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """User update request."""

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

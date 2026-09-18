"""Organization domain model."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Organization(BaseModel):
    """Organization entity."""

    organization_id: str = Field(..., description="Unique organization identifier")
    name: str = Field(..., description="Organization name", min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether organization is active")
    settings: dict = Field(default_factory=dict, description="Organization settings")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class OrganizationCreate(BaseModel):
    """Organization creation request."""

    name: str = Field(..., min_length=1, max_length=200)
    settings: Optional[dict] = None


class OrganizationUpdate(BaseModel):
    """Organization update request."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    settings: Optional[dict] = None
    is_active: Optional[bool] = None

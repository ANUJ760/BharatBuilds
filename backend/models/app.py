"""App domain model."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class App(BaseModel):
    """Generated application entity."""

    app_id: str = Field(..., description="Unique app identifier")
    organization_id: str = Field(..., description="Organization owning this app")
    created_by: str = Field(..., description="User who created the app")
    name: str = Field(..., description="App name")
    description: Optional[str] = Field(None, description="App description")
    workflow_id: str = Field(..., description="Workflow that generated this app")
    deployment_url: Optional[str] = Field(None, description="Live deployment URL")
    current_snapshot_id: Optional[str] = Field(None, description="Current code snapshot reference")
    is_active: bool = Field(default=True, description="Whether app is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    deployed_at: Optional[datetime] = Field(None, description="Last deployment timestamp")
    metadata: dict = Field(default_factory=dict, description="App metadata")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class AppCreate(BaseModel):
    """App creation request."""

    name: str
    description: Optional[str] = None
    workflow_id: str


class AppUpdate(BaseModel):
    """App update request."""

    name: Optional[str] = None
    description: Optional[str] = None
    deployment_url: Optional[str] = None
    current_snapshot_id: Optional[str] = None
    is_active: Optional[bool] = None
    deployed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

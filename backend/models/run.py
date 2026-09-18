"""Run domain model."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Workflow run status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"


class Run(BaseModel):
    """Workflow run execution."""

    run_id: str = Field(..., description="Unique run identifier")
    workflow_id: str = Field(..., description="Workflow being executed")
    organization_id: str = Field(..., description="Organization owning this run")
    triggered_by: str = Field(..., description="User who triggered the run")
    status: RunStatus = Field(default=RunStatus.PENDING, description="Run status")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Run input data")
    result: Optional[dict[str, Any]] = Field(None, description="Run result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Run start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Run completion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: dict = Field(default_factory=dict, description="Run metadata")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate run duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class RunCreate(BaseModel):
    """Run creation request."""

    workflow_id: str
    input_data: Optional[dict[str, Any]] = None


class RunUpdate(BaseModel):
    """Run update request."""

    status: Optional[RunStatus] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

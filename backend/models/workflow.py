"""Workflow domain model."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowTriggerType(str, Enum):
    """Workflow trigger type."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"


class WorkflowTrigger(BaseModel):
    """Workflow trigger configuration."""

    type: WorkflowTriggerType
    schedule: Optional[str] = Field(None, description="Cron schedule for scheduled triggers")
    event_type: Optional[str] = Field(None, description="Event type for event triggers")


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    tool: str = Field(..., description="Tool to execute")
    input: Optional[dict[str, Any]] = Field(None, description="Step input parameters")
    condition: Optional[str] = Field(None, description="Conditional execution expression")


class WorkflowAction(BaseModel):
    """Workflow action definition."""

    name: str = Field(..., description="Action name")
    requires_approval: bool = Field(default=False, description="Whether action requires human approval")
    tool: Optional[str] = Field(None, description="Tool to execute for this action")


class WorkflowDefinition(BaseModel):
    """Validated workflow definition."""

    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    trigger: WorkflowTrigger = Field(..., description="Workflow trigger")
    inputs: list[str] = Field(default_factory=list, description="Required inputs")
    steps: list[WorkflowStep] = Field(..., description="Workflow steps")
    actions: list[WorkflowAction] = Field(default_factory=list, description="Workflow actions")
    allowed_tools: list[str] = Field(default_factory=list, description="Tools agent is allowed to use")
    allowed_resources: list[str] = Field(default_factory=list, description="Resources agent can access")


class Workflow(BaseModel):
    """Workflow entity."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    organization_id: str = Field(..., description="Organization owning this workflow")
    created_by: str = Field(..., description="User who created the workflow")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    workflow_definition: WorkflowDefinition = Field(..., description="Validated workflow definition")
    is_active: bool = Field(default=True, description="Whether workflow is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class WorkflowCreate(BaseModel):
    """Workflow creation request."""

    name: str
    description: Optional[str] = None
    workflow_definition: WorkflowDefinition


class WorkflowUpdate(BaseModel):
    """Workflow update request."""

    name: Optional[str] = None
    description: Optional[str] = None
    workflow_definition: Optional[WorkflowDefinition] = None
    is_active: Optional[bool] = None

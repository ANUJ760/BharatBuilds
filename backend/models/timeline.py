"""Timeline domain model."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TimelineStepType(str, Enum):
    """Timeline step type."""

    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    AUTHORIZATION = "authorization"
    CODE_GENERATION = "code_generation"
    DEPLOYMENT = "deployment"
    ERROR = "error"
    RETRY = "retry"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"


class TimelineStepStatus(str, Enum):
    """Timeline step status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    REVERTED = "reverted"
    SKIPPED = "skipped"


class TokenUsage(BaseModel):
    """Token usage metrics."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class TimelineStep(BaseModel):
    """Decision timeline step - represents one agent action/decision."""

    step_id: str = Field(..., description="Unique step identifier")
    workflow_id: str = Field(..., description="Workflow this step belongs to")
    run_id: str = Field(..., description="Run this step belongs to")
    organization_id: str = Field(..., description="Organization owning this step")
    parent_step_id: Optional[str] = Field(None, description="Parent step for branching/retry")
    type: TimelineStepType = Field(..., description="Step type")
    status: TimelineStepStatus = Field(default=TimelineStepStatus.PENDING, description="Step status")

    # Step execution details
    input: Optional[dict[str, Any]] = Field(None, description="Step input")
    plan: Optional[str] = Field(None, description="Agent reasoning/plan text")
    tool: Optional[str] = Field(None, description="Tool called")
    tool_arguments: Optional[dict[str, Any]] = Field(None, description="Tool call arguments")
    output: Optional[dict[str, Any]] = Field(None, description="Step output/result")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    # Metrics
    latency_ms: Optional[int] = Field(None, description="Step execution latency in milliseconds")
    token_usage: Optional[TokenUsage] = Field(None, description="Token usage for this step")

    # Code/deployment tracking
    code_diff: Optional[str] = Field(None, description="Code changes made in this step")
    snapshot_reference: Optional[str] = Field(None, description="Reference to code snapshot (S3 key)")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    # Metadata
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    # Transient field for tree building (not persisted)
    children: list = Field(default_factory=list, description="Transient child steps for tree view")

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

    @property
    def duration_ms(self) -> Optional[int]:
        """Calculate step duration in milliseconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return self.latency_ms


class TimelineStepCreate(BaseModel):
    """Timeline step creation request."""

    workflow_id: str
    run_id: str
    parent_step_id: Optional[str] = None
    type: TimelineStepType
    input: Optional[dict[str, Any]] = None
    plan: Optional[str] = None
    tool: Optional[str] = None
    tool_arguments: Optional[dict[str, Any]] = None


class TimelineStepUpdate(BaseModel):
    """Timeline step update request."""

    status: Optional[TimelineStepStatus] = None
    output: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    latency_ms: Optional[int] = None
    token_usage: Optional[TokenUsage] = None
    code_diff: Optional[str] = None
    snapshot_reference: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

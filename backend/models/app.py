"""Core Pydantic data models for the BharatBuilds platform.

All models use strict validation. Timestamps default to UTC. IDs are
generated lazily via ``uuid4`` so callers never need to supply them
unless they already have one (e.g., during deserialization from DynamoDB).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────


class AppStatus(StrEnum):
    """Lifecycle status of a deployed app."""

    PENDING = "pending"
    BUILDING = "building"
    DEPLOYED = "deployed"
    FAILED = "failed"
    CODE_READY = "code_ready"


class StepType(StrEnum):
    """Type of an agent pipeline step."""

    CLARIFY = "clarify"
    PLAN = "plan"
    TOOL_CALL = "tool_call"
    CODEGEN = "codegen"
    RETRY = "retry"
    DEPLOY = "deploy"
    REVERT = "revert"
    # Auto-Maintenance lifecycle steps
    MAINTENANCE_DETECT = "maintenance_detect"
    MAINTENANCE_DIAGNOSE = "maintenance_diagnose"
    MAINTENANCE_PATCH = "maintenance_patch"
    MAINTENANCE_VERIFY = "maintenance_verify"
    MAINTENANCE_PROMOTE = "maintenance_promote"
    MAINTENANCE_REJECT = "maintenance_reject"


class StepStatus(StrEnum):
    """Outcome status of a timeline step."""

    OK = "ok"
    ERROR = "error"
    REVERTED = "reverted"


class MaintenanceStatus(StrEnum):
    """Lifecycle status of an auto-maintenance job."""

    PENDING = "pending"
    DIAGNOSING = "diagnosing"
    PATCHING = "patching"
    VERIFYING = "verifying"
    PROMOTED = "promoted"
    REJECTED = "rejected"
    FAILED = "failed"


class Role(StrEnum):
    """Access roles for shared apps."""

    VIEWER = "viewer"
    EDITOR = "editor"
    OWNER = "owner"


# ── Core Models ──────────────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class App(BaseModel):
    """A deployed user app."""

    app_id: str = Field(default_factory=_new_id)
    owner_id: str
    title: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1)
    live_url: Optional[str] = None
    status: AppStatus = AppStatus.PENDING
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class TimelineStep(BaseModel):
    """A single node in the decision timeline."""

    app_id: str
    step_id: str = Field(default_factory=_new_id)
    parent_step_id: Optional[str] = None
    step_type: StepType
    input_text: Optional[str] = None
    reasoning: Optional[str] = None
    code_snapshot: Optional[str] = None
    code_diff: Optional[str] = None
    latency_ms: Optional[int] = Field(default=None, ge=0)
    token_usage: Optional[int] = Field(default=None, ge=0)
    status: StepStatus = StepStatus.OK
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class Invite(BaseModel):
    """An invitation to share an app with another user."""

    app_id: str
    email: str = Field(min_length=3, max_length=254)
    role: Role = Role.VIEWER
    invited_at: datetime = Field(default_factory=_utcnow)


# ── Clarify Models ───────────────────────────────────────────────────────


class ClarifyQuestion(BaseModel):
    """A single clarifying question posed to the user."""

    question: str
    suggested_default: str
    why_it_matters: str


class ClarifyResponse(BaseModel):
    """Result of the ambiguity-check pass (0–3 questions)."""

    needs_clarification: bool
    questions: list[ClarifyQuestion] = Field(
        default_factory=list, max_length=3
    )


# ── Maintenance Models ───────────────────────────────────────────────────


class MaintenanceIssue(BaseModel):
    """A detected runtime or functional defect triggering auto-maintenance."""

    issue_id: str = Field(default_factory=_new_id)
    issue_type: str = Field(min_length=1, description="Category (e.g. '5xx_error', 'syntax_error', 'runtime_exception')")
    severity: str = Field(default="high", description="Severity level: low, medium, high, critical")
    error_message: str = Field(min_length=1, description="Primary error or exception message")
    stack_trace: Optional[str] = None
    endpoint: Optional[str] = None
    detection_source: str = Field(default="synthetic_probe", description="Source of detection")
    detected_at: datetime = Field(default_factory=_utcnow)


class MaintenanceJob(BaseModel):
    """Tracking record for an autonomous maintenance lifecycle execution."""

    job_id: str = Field(default_factory=_new_id)
    app_id: str
    status: MaintenanceStatus = MaintenanceStatus.PENDING
    issue: MaintenanceIssue
    candidate_step_id: Optional[str] = None
    attempt_count: int = Field(default=1, ge=1)
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class RepairResult(BaseModel):
    """Result of an automated diagnostic and code repair execution."""

    diagnosis: str = Field(default="", description="Root cause diagnosis of the issue")
    summary: str = Field(default="", description="Summary of the modifications made")
    patched_code: str = Field(default="", description="Complete repaired source code")
    is_success: bool = Field(default=True, description="Whether repair succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if repair failed")


class HealthCheckResult(BaseModel):
    """Result of an HTTP synthetic health probe on a deployed app."""

    url: str
    is_healthy: bool
    status_code: Optional[int] = None
    latency_ms: Optional[int] = Field(default=None, ge=0)
    error_message: Optional[str] = None
    checked_at: datetime = Field(default_factory=_utcnow)


class CandidateVerificationResult(BaseModel):
    """Structured outcome of local candidate code verification."""

    passed: bool
    checks_performed: list[str] = Field(default_factory=list)
    checks_passed: list[str] = Field(default_factory=list)
    checks_failed: list[str] = Field(default_factory=list)
    entry_point: Optional[str] = None
    response_sample: Optional[str] = None
    error_message: Optional[str] = None
    verified_at: datetime = Field(default_factory=_utcnow)


class MaintenanceResult(BaseModel):
    """Structured outcome returned by MaintenanceOrchestrator."""

    job: MaintenanceJob
    status: MaintenanceStatus
    diagnosis: Optional[str] = None
    summary: Optional[str] = None
    candidate_code: Optional[str] = None
    repair_result: Optional[RepairResult] = None
    verification_result: Optional[CandidateVerificationResult] = None
    timeline_steps: list[TimelineStep] = Field(default_factory=list)






"""App and TimelineStep Pydantic models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class App(BaseModel):
    app_id: str
    owner_id: str
    title: str
    prompt: str
    live_url: Optional[str] = None
    status: str = "pending"
    created_at: datetime = datetime.utcnow()


class TimelineStep(BaseModel):
    app_id: str
    step_id: str
    step_type: str  # plan | tool_call | codegen | retry | deploy
    input_text: Optional[str] = None
    reasoning: Optional[str] = None
    code_diff: Optional[str] = None
    latency_ms: Optional[int] = None
    token_usage: Optional[int] = None
    status: str = "ok"  # ok | error | reverted
    created_at: datetime = datetime.utcnow()


class Invite(BaseModel):
    app_id: str
    email: str
    role: str = "viewer"  # viewer | editor

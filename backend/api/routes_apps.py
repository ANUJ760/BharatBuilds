"""Create / list / get deployed apps + clarify endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agent.clarify import check_ambiguity
from backend.config import get_settings

router = APIRouter(prefix="/apps", tags=["apps"])


# ── Request / response schemas ───────────────────────────────────────────


class ClarifyRequest(BaseModel):
    """Request body for the clarify endpoint."""

    prompt: str


class CreateAppRequest(BaseModel):
    """Request body for creating a new app."""

    prompt: str
    owner_id: str
    title: str = ""


# ── Routes ───────────────────────────────────────────────────────────────


@router.post("/clarify")
async def clarify(body: ClarifyRequest):
    """Run the ambiguity-check pass on a prompt.

    Returns 0–3 clarifying questions with suggested defaults.
    """
    settings = get_settings()
    response = await check_ambiguity(
        body.prompt,
        model_id=settings.bedrock_model_id,
        region=settings.aws_region,
    )
    return response.model_dump()


@router.post("/")
async def create_app(body: CreateAppRequest):
    """Create a new app from a prompt (triggers the agent pipeline)."""
    # TODO: wire to planner.py in Commit 11
    return {"status": "pending", "message": "App creation will be wired in Commit 11"}


@router.get("/")
async def list_apps():
    """List the current user's deployed apps."""
    # TODO: query DynamoDB
    return {"apps": []}


@router.get("/{app_id}")
async def get_app(app_id: str):
    """Get a single app's details."""
    # TODO: fetch from DynamoDB
    return {"app_id": app_id, "status": "not_implemented"}

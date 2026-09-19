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

class UpdateAppRequest(BaseModel):
    title: str


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
    """Initiate a new app entry."""
    import uuid
    app_id = str(uuid.uuid4())
    return {
        "app_id": app_id,
        "owner_id": body.owner_id,
        "title": body.title or f"App {app_id[:8]}",
        "prompt": body.prompt,
        "status": "pending",
    }


@router.get("/")
async def list_apps(owner_id: str):
    """List apps for a specific owner."""
    from backend.storage.dynamodb_client import scan_apps_by_owner
    settings = get_settings()
    apps = scan_apps_by_owner(
        settings.dynamodb_table_name,
        owner_id,
        region=settings.aws_region,
    )
    return {"apps": apps}

@router.delete("/{app_id}")
async def delete_app(app_id: str):
    """Delete an app's metadata (soft delete)."""
    from backend.storage.dynamodb_client import delete_item
    settings = get_settings()
    # For now, just delete the __metadata__ item so it won't show in the list
    delete_item(
        settings.dynamodb_table_name,
        app_id,
        "__metadata__",
        region=settings.aws_region,
    )
    return {"status": "deleted"}

@router.put("/{app_id}")
async def update_app(app_id: str, body: UpdateAppRequest):
    """Update an app's metadata."""
    from fastapi import HTTPException
    from backend.storage.dynamodb_client import get_item, put_item
    settings = get_settings()
    
    item = get_item(
        settings.dynamodb_table_name,
        app_id,
        "__metadata__",
        region=settings.aws_region,
    )
    if not item:
        raise HTTPException(status_code=404, detail="App not found")
        
    item["title"] = body.title
    put_item(
        settings.dynamodb_table_name,
        item,
        region=settings.aws_region,
    )
    return item


@router.get("/{app_id}")
async def get_app(app_id: str):
    """Get a single app's details from DynamoDB."""
    from fastapi import HTTPException
    from backend.storage.dynamodb_client import get_item

    settings = get_settings()
    item = get_item(
        settings.dynamodb_table_name,
        app_id,
        "__metadata__",
        region=settings.aws_region,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="App not found")
    return item

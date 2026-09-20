"""Create / list / get deployed apps + clarify endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.agent.clarify import check_ambiguity
from backend.config import get_settings
from backend.storage.dynamodb_client import put_item, get_item
from backend.auth.roles import require_viewer

router = APIRouter(prefix="/apps", tags=["apps"])


class ClarifyRequest(BaseModel):
    prompt: str


class CreateAppRequest(BaseModel):
    prompt: str
    owner_id: str
    title: str = ""

class UpdateAppRequest(BaseModel):
    title: str


@router.post("/clarify")
async def clarify(body: ClarifyRequest):
    settings = get_settings()
    response = await check_ambiguity(
        body.prompt,
        model_id=settings.gemini_model_id,
        region=settings.aws_region,
    )
    return response.model_dump()


@router.post("/")
async def create_app(body: CreateAppRequest):
    settings = get_settings()
    app_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    title = body.title or f"App {app_id[:8]}"
    
    item = {
        "app_id": app_id,
        "step_id": "__metadata__",
        "owner_id": body.owner_id,
        "title": title,
        "prompt": body.prompt,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    
    put_item(
        settings.dynamodb_table_name,
        item,
        region=settings.aws_region
    )
    
    return {
        "app_id": app_id,
        "owner_id": body.owner_id,
        "title": title,
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
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    put_item(
        settings.dynamodb_table_name,
        item,
        region=settings.aws_region,
    )
    return item


@router.get("/{app_id}")
async def get_app(app_id: str):
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

@router.get("/{app_id}/live")
async def live_app(app_id: str):
    """Serve the generated HTML app directly."""
    from backend.agent.trace_logger import get_timeline
    from backend.models.app import StepType
    
    steps = await get_timeline(app_id)
    # Find the latest codegen step
    for step in reversed(steps):
        if step.step_type == StepType.CODEGEN and step.code_snapshot:
            return HTMLResponse(content=step.code_snapshot, status_code=200)
            
    return HTMLResponse(content="<h1>App not ready or no code generated yet.</h1>", status_code=404)


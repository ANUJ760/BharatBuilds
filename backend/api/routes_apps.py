"""Create / list / get deployed apps + clarify endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
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
    # Scan table for owner_id's apps (Note: For production, a GSI on owner_id is recommended)
    import boto3
    settings = get_settings()
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
    table = dynamodb.Table(settings.dynamodb_table_name)
    
    from boto3.dynamodb.conditions import Attr
    response = table.scan(
        FilterExpression=Attr('step_id').eq('__metadata__') & Attr('owner_id').eq(owner_id)
    )
    return {"apps": response.get("Items", [])}


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

@router.put("/{app_id}")
async def update_app(app_id: str, body: dict):
    settings = get_settings()
    item = get_item(settings.dynamodb_table_name, app_id, "__metadata__", region=settings.aws_region)
    if not item:
        raise HTTPException(status_code=404, detail="App not found")
    item['title'] = body.get('title', item.get('title'))
    item['updated_at'] = datetime.now(timezone.utc).isoformat()
    put_item(settings.dynamodb_table_name, item, region=settings.aws_region)
    return item

@router.delete("/{app_id}")
async def delete_app(app_id: str):
    from backend.storage.dynamodb_client import delete_item
    settings = get_settings()
    delete_item(settings.dynamodb_table_name, app_id, "__metadata__", region=settings.aws_region)
    return {"status": "deleted"}

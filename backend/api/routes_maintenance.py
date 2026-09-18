"""Maintenance API endpoints for BharatBuilds."""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from backend.agent.maintenance_orchestrator import MaintenanceOrchestrator
from backend.agent.trace_logger import get_timeline
from backend.auth.roles import require_editor
from backend.config import get_settings
from backend.models.app import MaintenanceIssue, MaintenanceResult

logger = logging.getLogger(__name__)

router = APIRouter(tags=["maintenance"])


@router.post(
    "/apps/{app_id}/maintenance",
    response_model=MaintenanceResult,
    dependencies=[Depends(require_editor)],
)
async def trigger_maintenance(
    app_id: str,
    issue: MaintenanceIssue,
) -> MaintenanceResult:
    """Trigger an autonomous diagnosis and code repair on a deployed app.

    Loads the latest code snapshot from the app's timeline, invokes the
    MaintenanceOrchestrator, verifies the candidate fix, logs timeline events,
    and returns the structured maintenance result.
    """
    settings = get_settings()

    # 1. Fetch latest code snapshot from timeline
    timeline = await get_timeline(
        app_id,
        table_name=settings.dynamodb_table_name,
        region=settings.aws_region,
    )

    existing_code: str | None = None
    for step in reversed(timeline):
        if step.code_snapshot:
            existing_code = step.code_snapshot
            break

    if not existing_code:
        logger.warning("Maintenance requested for app %s with no code snapshots", app_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existing code snapshot found for app {app_id}. App must be deployed before running maintenance.",
        )

    # 2. Invoke MaintenanceOrchestrator
    orchestrator = MaintenanceOrchestrator(
        model_id=settings.bedrock_model_id,
        region=settings.aws_region,
        table_name=settings.dynamodb_table_name,
    )

    result = await orchestrator.run_maintenance(
        app_id,
        issue,
        existing_code=existing_code,
        persist_timeline=True,
    )

    return result

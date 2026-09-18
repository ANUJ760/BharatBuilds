"""GET /apps/{id}/timeline, GET /apps/{id}/timeline/{step_id}."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.agent.trace_logger import get_step, get_timeline

router = APIRouter(tags=["timeline"])


@router.get("/apps/{app_id}/timeline")
async def list_timeline(app_id: str):
    """Fetch the full decision timeline for an app.

    Returns an ordered list of steps: plan, tool calls, codegen,
    retries, deploys, and reverts.
    """
    steps = await get_timeline(app_id)
    return {
        "app_id": app_id,
        "step_count": len(steps),
        "steps": [s.model_dump() for s in steps],
    }


@router.get("/apps/{app_id}/timeline/{step_id}")
async def get_timeline_step(app_id: str, step_id: str):
    """Fetch a single timeline step by ID.

    Includes the full detail: input, reasoning, code diff, latency,
    token usage, and status.
    """
    step = await get_step(app_id, step_id)
    if step is None:
        raise HTTPException(status_code=404, detail="Step not found")
    return step.model_dump()

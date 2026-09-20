"""Deploy-related endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.agent.planner import plan_and_execute
from backend.agent.trace_logger import log_steps
from backend.auth.roles import require_editor
from backend.config import get_settings
from backend.deploy.lambda_deployer import deploy_to_lambda
from backend.models.app import App, StepType, TimelineStep
from backend.storage.dynamodb_client import put_item

router = APIRouter(prefix="/deploy", tags=["deploy"])


class DeployRequest(BaseModel):
    """Request body for deploying an app."""

    prompt: str
    owner_id: str
    title: str = ""
    clarifications: dict[str, str] | None = None


@router.post("/{app_id}")
async def deploy_app(app_id: str, body: DeployRequest):
    """Run the full pipeline: plan → codegen → deploy → log timeline.

    This is the main entry point for creating and deploying an app.
    """
    settings = get_settings()

    # Run the planner to generate code
    code, steps = await plan_and_execute(
        body.prompt,
        clarifications=body.clarifications,
        model_id=settings.gemini_model_id,
        region=settings.aws_region,
        app_id=app_id,
    )

    if not code:
        # Log whatever steps we have, then fail
        await log_steps(steps)
        raise HTTPException(
            status_code=500,
            detail="Code generation failed — see timeline for details",
        )

    # Deploy to Lambda
    function_url = await deploy_to_lambda(
        app_id,
        code,
        function_name=settings.deploy_lambda_function_name,
        region=settings.aws_region,
    )

    # Log the deploy step
    deploy_step = TimelineStep(
        app_id=app_id,
        step_type=StepType.DEPLOY,
        parent_step_id=steps[-1].step_id if steps else None,
        code_snapshot=code,
        reasoning=f"Deployed to {function_url}",
    )
    steps.append(deploy_step)

    # Persist all timeline steps
    await log_steps(steps)

    # Persist app metadata
    app = App(
        app_id=app_id,
        owner_id=body.owner_id,
        title=body.title or f"App {app_id[:8]}",
        prompt=body.prompt,
        live_url=function_url,
        status="deployed",
    )
    put_item(
        settings.dynamodb_table_name,
        {"app_id": app_id, "step_id": "__metadata__", **app.model_dump(mode="json")},
        region=settings.aws_region,
    )

    return {
        "app_id": app_id,
        "live_url": function_url,
        "status": "deployed",
        "steps_logged": len(steps),
    }


@router.get("/{app_id}/status")
async def deploy_status(app_id: str):
    """Check the deploy status of an app."""
    settings = get_settings()
    from backend.storage.dynamodb_client import get_item

    item = get_item(
        settings.dynamodb_table_name,
        app_id,
        "__metadata__",
        region=settings.aws_region,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="App not found")
    return {
        "app_id": app_id,
        "status": item.get("status", "unknown"),
        "live_url": item.get("live_url"),
    }

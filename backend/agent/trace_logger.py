"""Writes every agent step to DynamoDB as a timeline node.

Each step from the planner (plan, tool_call, codegen, retry, deploy,
revert) is persisted as a :class:`TimelineStep` in DynamoDB using the
single-table design: ``app_id`` (PK) + ``step_id`` (SK).
"""

from __future__ import annotations

import logging
from datetime import timezone
from typing import Any

from backend.config import get_settings
from backend.models.app import TimelineStep
from backend.storage.dynamodb_client import put_item, query_by_app_id, get_item

logger = logging.getLogger(__name__)


def _step_to_item(step: TimelineStep) -> dict[str, Any]:
    """Convert a TimelineStep to a DynamoDB-compatible dict.

    Handles datetime serialization and strips ``None`` values to keep
    items lean.
    """
    data = step.model_dump()
    # Serialize datetime to ISO string
    for key in ("created_at",):
        if data.get(key) is not None:
            data[key] = data[key].isoformat()
    # Strip None values — DynamoDB doesn't like them
    return {k: v for k, v in data.items() if v is not None}


def _item_to_step(item: dict[str, Any]) -> TimelineStep:
    """Convert a DynamoDB item back to a TimelineStep."""
    return TimelineStep(**item)


async def log_step(
    step: TimelineStep,
    *,
    table_name: str = "",
    region: str = "",
) -> str:
    """Persist an agent step to DynamoDB.

    Parameters
    ----------
    step:
        The timeline step to persist.
    table_name:
        DynamoDB table name. Reads from config if empty.
    region:
        AWS region. Reads from config if empty.

    Returns
    -------
    str
        The ``step_id`` of the persisted step.
    """
    if not table_name or not region:
        settings = get_settings()
        table_name = table_name or settings.dynamodb_table_name
        region = region or settings.aws_region

    item = _step_to_item(step)
    put_item(table_name, item, region=region)
    logger.info(
        "Logged timeline step: app_id=%s step_id=%s type=%s",
        step.app_id,
        step.step_id,
        step.step_type,
    )
    return step.step_id


async def log_steps(
    steps: list[TimelineStep],
    *,
    table_name: str = "",
    region: str = "",
) -> list[str]:
    """Persist multiple agent steps to DynamoDB.

    Returns a list of ``step_id``s.
    """
    return [
        await log_step(step, table_name=table_name, region=region)
        for step in steps
    ]


async def get_timeline(
    app_id: str,
    *,
    table_name: str = "",
    region: str = "",
) -> list[TimelineStep]:
    """Fetch all timeline steps for an app, ordered by step_id."""
    if not table_name or not region:
        settings = get_settings()
        table_name = table_name or settings.dynamodb_table_name
        region = region or settings.aws_region

    items = query_by_app_id(table_name, app_id, region=region)
    steps: list[TimelineStep] = []
    for item in items:
        # Single-table design: filter out app metadata and invite records
        step_id = item.get("step_id", "")
        if step_id.startswith("__") or step_id.startswith("invite#"):
            continue
        if "step_type" not in item:
            continue
        try:
            steps.append(_item_to_step(item))
        except Exception as exc:
            logger.warning("Skipping malformed timeline item %s: %s", step_id, exc)

    steps.sort(key=lambda s: (s.created_at, s.step_id))
    return steps


async def get_step(
    app_id: str,
    step_id: str,
    *,
    table_name: str = "",
    region: str = "",
) -> TimelineStep | None:
    """Fetch a single timeline step."""
    if not table_name or not region:
        settings = get_settings()
        table_name = table_name or settings.dynamodb_table_name
        region = region or settings.aws_region

    item = get_item(table_name, app_id, step_id, region=region)
    if item is None:
        return None
    return _item_to_step(item)

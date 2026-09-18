"""DynamoDB client for app metadata, decision timeline, and code snapshots.

Uses single-table design with ``app_id`` as partition key and ``step_id``
as sort key for timeline queries. All helpers read the table name from
:pymod:`backend.config`.
"""

from __future__ import annotations

from typing import Any

import boto3
from boto3.dynamodb.conditions import Key


def _get_table(table_name: str, region: str = "ap-south-1"):
    """Return a DynamoDB Table resource."""
    dynamodb = boto3.resource("dynamodb", region_name=region)
    return dynamodb.Table(table_name)


def put_item(table_name: str, item: dict[str, Any], *, region: str = "ap-south-1") -> None:
    """Put a single item into the table.

    Raises ``botocore.exceptions.ClientError`` on failure.
    """
    table = _get_table(table_name, region=region)
    table.put_item(Item=item)


def get_item(
    table_name: str,
    app_id: str,
    step_id: str,
    *,
    region: str = "ap-south-1",
) -> dict[str, Any] | None:
    """Get a single item by composite key. Returns ``None`` if not found."""
    table = _get_table(table_name, region=region)
    response = table.get_item(Key={"app_id": app_id, "step_id": step_id})
    return response.get("Item")


def query_by_app_id(
    table_name: str,
    app_id: str,
    *,
    region: str = "ap-south-1",
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Query all items for a given ``app_id``, ordered by ``step_id``.

    Returns up to *limit* items.
    """
    table = _get_table(table_name, region=region)
    response = table.query(
        KeyConditionExpression=Key("app_id").eq(app_id),
        Limit=limit,
        ScanIndexForward=True,
    )
    return response.get("Items", [])


def delete_item(
    table_name: str,
    app_id: str,
    step_id: str,
    *,
    region: str = "ap-south-1",
) -> None:
    """Delete a single item by composite key."""
    table = _get_table(table_name, region=region)
    table.delete_item(Key={"app_id": app_id, "step_id": step_id})

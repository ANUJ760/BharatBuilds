"""DynamoDB client for MicroAgent."""
import json
from typing import Any, Optional

import boto3
import structlog
from botocore.exceptions import ClientError

from backend.config.settings import get_settings

logger = structlog.get_logger(__name__)


class DynamoDBClient:
    """DynamoDB client wrapper."""

    def __init__(self):
        """Initialize DynamoDB client."""
        settings = get_settings()

        session = boto3.Session()

        config = {
            "region_name": settings.aws_region,
        }

        if settings.dynamodb_endpoint_url:
            config["endpoint_url"] = settings.dynamodb_endpoint_url

        self.dynamodb = session.resource("dynamodb", **config)
        self.table_name = settings.dynamodb_table_name
        self.table = self.dynamodb.Table(self.table_name)

    def put_item(self, item: dict[str, Any]) -> None:
        """Put item in DynamoDB.

        Args:
            item: Item to store

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            self.table.put_item(Item=item)
            logger.info("put_item_success", table=self.table_name, pk=item.get("pk"))
        except ClientError as e:
            logger.error("put_item_failed", error=str(e), table=self.table_name)
            raise

    def get_item(self, pk: str, sk: str) -> Optional[dict[str, Any]]:
        """Get item from DynamoDB.

        Args:
            pk: Partition key
            sk: Sort key

        Returns:
            Item if found, None otherwise

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            response = self.table.get_item(Key={"pk": pk, "sk": sk})
            item = response.get("Item")
            logger.info("get_item_success", table=self.table_name, pk=pk, sk=sk, found=item is not None)
            return item
        except ClientError as e:
            logger.error("get_item_failed", error=str(e), table=self.table_name, pk=pk, sk=sk)
            raise

    def query(
        self,
        pk: str,
        sk_prefix: Optional[str] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_forward: bool = True,
    ) -> list[dict[str, Any]]:
        """Query items by partition key.

        Args:
            pk: Partition key
            sk_prefix: Optional sort key prefix for begins_with condition
            index_name: Optional GSI name
            limit: Optional result limit
            scan_forward: Query order (True = ascending, False = descending)

        Returns:
            List of items

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            query_kwargs: dict[str, Any] = {
                "KeyConditionExpression": "pk = :pk",
                "ExpressionAttributeValues": {":pk": pk},
                "ScanIndexForward": scan_forward,
            }

            if sk_prefix:
                query_kwargs["KeyConditionExpression"] += " AND begins_with(sk, :sk)"
                query_kwargs["ExpressionAttributeValues"][":sk"] = sk_prefix

            if index_name:
                query_kwargs["IndexName"] = index_name

            if limit:
                query_kwargs["Limit"] = limit

            response = self.table.query(**query_kwargs)
            items = response.get("Items", [])

            logger.info(
                "query_success",
                table=self.table_name,
                pk=pk,
                sk_prefix=sk_prefix,
                count=len(items),
            )

            return items
        except ClientError as e:
            logger.error("query_failed", error=str(e), table=self.table_name, pk=pk)
            raise

    def update_item(
        self,
        pk: str,
        sk: str,
        updates: dict[str, Any],
    ) -> None:
        """Update item attributes.

        Args:
            pk: Partition key
            sk: Sort key
            updates: Dictionary of attribute updates

        Raises:
            ClientError: If DynamoDB operation fails
        """
        if not updates:
            return

        try:
            update_expression_parts = []
            expression_attribute_values = {}
            expression_attribute_names = {}

            for i, (key, value) in enumerate(updates.items()):
                attr_name = f"#attr{i}"
                attr_value = f":val{i}"
                update_expression_parts.append(f"{attr_name} = {attr_value}")
                expression_attribute_names[attr_name] = key
                expression_attribute_values[attr_value] = value

            update_expression = "SET " + ", ".join(update_expression_parts)

            self.table.update_item(
                Key={"pk": pk, "sk": sk},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )

            logger.info("update_item_success", table=self.table_name, pk=pk, sk=sk)
        except ClientError as e:
            logger.error("update_item_failed", error=str(e), table=self.table_name, pk=pk, sk=sk)
            raise

    def delete_item(self, pk: str, sk: str) -> None:
        """Delete item from DynamoDB.

        Args:
            pk: Partition key
            sk: Sort key

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            self.table.delete_item(Key={"pk": pk, "sk": sk})
            logger.info("delete_item_success", table=self.table_name, pk=pk, sk=sk)
        except ClientError as e:
            logger.error("delete_item_failed", error=str(e), table=self.table_name, pk=pk, sk=sk)
            raise

    def batch_write(self, items: list[dict[str, Any]]) -> None:
        """Batch write items to DynamoDB.

        Args:
            items: List of items to write

        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            logger.info("batch_write_success", table=self.table_name, count=len(items))
        except ClientError as e:
            logger.error("batch_write_failed", error=str(e), table=self.table_name)
            raise

"""DynamoDB client for app metadata, timeline, and code snapshots."""
import boto3


def get_table(table_name: str):
    """Return a DynamoDB Table resource."""
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)

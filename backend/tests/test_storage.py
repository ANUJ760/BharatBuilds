"""Tests for DynamoDB and S3 storage clients — mocked via ``moto``."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from backend.storage import dynamodb_client, s3_client

TEST_REGION = "ap-south-1"
TEST_TABLE = "test-bharatbuilds"
TEST_BUCKET = "test-bharatbuilds-assets"


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture()
def dynamodb_table():
    """Create a mocked DynamoDB table for the duration of a test."""
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name=TEST_REGION)
        ddb.create_table(
            TableName=TEST_TABLE,
            KeySchema=[
                {"AttributeName": "app_id", "KeyType": "HASH"},
                {"AttributeName": "step_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "app_id", "AttributeType": "S"},
                {"AttributeName": "step_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield TEST_TABLE


@pytest.fixture()
def s3_bucket():
    """Create a mocked S3 bucket for the duration of a test."""
    with mock_aws():
        client = boto3.client("s3", region_name=TEST_REGION)
        client.create_bucket(
            Bucket=TEST_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": TEST_REGION},
        )
        yield TEST_BUCKET


# ── DynamoDB Tests ───────────────────────────────────────────────────────


class TestDynamoDBClient:
    """DynamoDB client wrapper tests."""

    def test_put_and_get_item(self, dynamodb_table):
        item = {"app_id": "app-1", "step_id": "step-1", "data": "hello"}
        dynamodb_client.put_item(dynamodb_table, item, region=TEST_REGION)

        result = dynamodb_client.get_item(
            dynamodb_table, "app-1", "step-1", region=TEST_REGION
        )
        assert result is not None
        assert result["data"] == "hello"

    def test_get_item_not_found(self, dynamodb_table):
        result = dynamodb_client.get_item(
            dynamodb_table, "nonexistent", "nope", region=TEST_REGION
        )
        assert result is None

    def test_query_by_app_id(self, dynamodb_table):
        for i in range(3):
            dynamodb_client.put_item(
                dynamodb_table,
                {"app_id": "app-1", "step_id": f"step-{i:03d}", "seq": i},
                region=TEST_REGION,
            )
        # Different app — should not appear
        dynamodb_client.put_item(
            dynamodb_table,
            {"app_id": "app-2", "step_id": "step-000", "seq": 99},
            region=TEST_REGION,
        )

        results = dynamodb_client.query_by_app_id(
            dynamodb_table, "app-1", region=TEST_REGION
        )
        assert len(results) == 3
        assert all(r["app_id"] == "app-1" for r in results)
        # Verify sort order
        assert [int(r["seq"]) for r in results] == [0, 1, 2]

    def test_delete_item(self, dynamodb_table):
        item = {"app_id": "app-1", "step_id": "step-del", "val": "gone"}
        dynamodb_client.put_item(dynamodb_table, item, region=TEST_REGION)
        dynamodb_client.delete_item(
            dynamodb_table, "app-1", "step-del", region=TEST_REGION
        )
        assert (
            dynamodb_client.get_item(
                dynamodb_table, "app-1", "step-del", region=TEST_REGION
            )
            is None
        )


# ── S3 Tests ─────────────────────────────────────────────────────────────


class TestS3Client:
    """S3 client wrapper tests."""

    def test_upload_and_get_asset(self, s3_bucket):
        uri = s3_client.upload_asset(
            s3_bucket,
            "apps/app-1/main.py",
            "print('hello')",
            content_type="text/x-python",
            region=TEST_REGION,
        )
        assert uri == f"s3://{s3_bucket}/apps/app-1/main.py"

        data = s3_client.get_asset(
            s3_bucket, "apps/app-1/main.py", region=TEST_REGION
        )
        assert data == b"print('hello')"

    def test_upload_bytes(self, s3_bucket):
        s3_client.upload_asset(
            s3_bucket,
            "apps/app-1/data.bin",
            b"\x00\x01\x02",
            region=TEST_REGION,
        )
        data = s3_client.get_asset(
            s3_bucket, "apps/app-1/data.bin", region=TEST_REGION
        )
        assert data == b"\x00\x01\x02"

    def test_get_asset_url(self, s3_bucket):
        s3_client.upload_asset(
            s3_bucket, "apps/app-1/file.txt", "content", region=TEST_REGION
        )
        url = s3_client.get_asset_url(
            s3_bucket, "apps/app-1/file.txt", region=TEST_REGION
        )
        assert "apps/app-1/file.txt" in url
        assert s3_bucket in url

    def test_delete_asset(self, s3_bucket):
        s3_client.upload_asset(
            s3_bucket, "apps/del/file.txt", "bye", region=TEST_REGION
        )
        s3_client.delete_asset(s3_bucket, "apps/del/file.txt", region=TEST_REGION)
        # S3 doesn't raise on get_object for deleted keys in moto,
        # but we can verify via list
        client = boto3.client("s3", region_name=TEST_REGION)
        resp = client.list_objects_v2(Bucket=s3_bucket, Prefix="apps/del/")
        assert resp.get("KeyCount", 0) == 0

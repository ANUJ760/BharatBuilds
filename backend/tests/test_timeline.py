"""Tests for trace logger and timeline endpoints — mocked DynamoDB via moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from backend.agent.trace_logger import get_step, get_timeline, log_step, log_steps
from backend.models.app import StepStatus, StepType, TimelineStep

TEST_REGION = "ap-south-1"
TEST_TABLE = "test-timeline"


@pytest.fixture()
def dynamodb_table():
    """Create a mocked DynamoDB table."""
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


class TestTraceLogger:
    """Trace logger tests with mocked DynamoDB."""

    @pytest.mark.asyncio
    async def test_log_and_get_step(self, dynamodb_table):
        step = TimelineStep(
            app_id="app-1",
            step_type=StepType.PLAN,
            input_text="Build a todo app",
            reasoning="Planning phase",
            latency_ms=100,
        )

        step_id = await log_step(
            step, table_name=dynamodb_table, region=TEST_REGION
        )
        assert step_id == step.step_id

        retrieved = await get_step(
            "app-1", step_id, table_name=dynamodb_table, region=TEST_REGION
        )
        assert retrieved is not None
        assert retrieved.app_id == "app-1"
        assert retrieved.step_type == StepType.PLAN
        assert retrieved.input_text == "Build a todo app"

    @pytest.mark.asyncio
    async def test_get_step_not_found(self, dynamodb_table):
        result = await get_step(
            "nonexistent", "nope", table_name=dynamodb_table, region=TEST_REGION
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_log_steps_and_get_timeline(self, dynamodb_table):
        steps = [
            TimelineStep(
                app_id="app-1",
                step_id=f"step-{i:03d}",
                step_type=StepType.PLAN if i == 0 else StepType.CODEGEN,
                parent_step_id=f"step-{i - 1:03d}" if i > 0 else None,
                reasoning=f"Step {i}",
            )
            for i in range(4)
        ]

        ids = await log_steps(
            steps, table_name=dynamodb_table, region=TEST_REGION
        )
        assert len(ids) == 4

        timeline = await get_timeline(
            "app-1", table_name=dynamodb_table, region=TEST_REGION
        )
        assert len(timeline) == 4
        # Verify ordering by step_id
        assert [s.step_id for s in timeline] == [
            "step-000",
            "step-001",
            "step-002",
            "step-003",
        ]
        # Verify parent linkage
        assert timeline[0].parent_step_id is None
        assert timeline[1].parent_step_id == "step-000"
        assert timeline[2].parent_step_id == "step-001"

    @pytest.mark.asyncio
    async def test_step_with_code_snapshot(self, dynamodb_table):
        step = TimelineStep(
            app_id="app-2",
            step_type=StepType.CODEGEN,
            code_snapshot="print('hello')",
            code_diff="+print('hello')",
            latency_ms=200,
            token_usage=500,
            status=StepStatus.OK,
        )

        await log_step(step, table_name=dynamodb_table, region=TEST_REGION)

        retrieved = await get_step(
            "app-2", step.step_id, table_name=dynamodb_table, region=TEST_REGION
        )
        assert retrieved is not None
        assert retrieved.code_snapshot == "print('hello')"
        assert retrieved.latency_ms == 200
        assert retrieved.token_usage == 500

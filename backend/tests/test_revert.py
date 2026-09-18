"""Tests for the revert endpoint — mocked DynamoDB + Lambda."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import boto3
import pytest
from moto import mock_aws

from backend.agent.trace_logger import get_timeline, log_step
from backend.api.routes_timeline import revert_to_step
from backend.models.app import StepStatus, StepType, TimelineStep

TEST_REGION = "ap-south-1"
TEST_TABLE = "test-revert"
TEST_FUNCTION = "test-bharatbuilds-deploy"

CODE_V1 = "def render(): return '<h1>Version 1</h1>'"
CODE_V2 = "def render(): return '<h1>Version 2</h1>'"


def _mock_settings():
    """Return a mock Settings object with test values."""
    return MagicMock(
        dynamodb_table_name=TEST_TABLE,
        aws_region=TEST_REGION,
        deploy_lambda_function_name=TEST_FUNCTION,
    )


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


class TestRevert:
    """Revert endpoint tests."""

    @pytest.mark.asyncio
    @patch("backend.api.routes_timeline.deploy_to_lambda", new_callable=AsyncMock)
    @patch("backend.agent.trace_logger.get_settings")
    @patch("backend.api.routes_timeline.get_settings")
    async def test_revert_deploys_old_code(
        self, mock_route_settings, mock_logger_settings, mock_deploy, dynamodb_table
    ):
        # All get_settings calls return the same mock
        mock_route_settings.return_value = _mock_settings()
        mock_logger_settings.return_value = _mock_settings()

        mock_deploy.return_value = (
            f"https://{TEST_FUNCTION}.lambda-url.{TEST_REGION}.on.aws/"
        )

        # Create version 1 step
        step_v1 = TimelineStep(
            app_id="app-revert",
            step_id="step-v1",
            step_type=StepType.CODEGEN,
            code_snapshot=CODE_V1,
        )
        await log_step(step_v1, table_name=dynamodb_table, region=TEST_REGION)

        # Create version 2 step
        step_v2 = TimelineStep(
            app_id="app-revert",
            step_id="step-v2",
            step_type=StepType.CODEGEN,
            code_snapshot=CODE_V2,
            parent_step_id="step-v1",
        )
        await log_step(step_v2, table_name=dynamodb_table, region=TEST_REGION)

        # Revert to version 1
        result = await revert_to_step("app-revert", "step-v1")

        assert result["reverted_to_step"] == "step-v1"
        assert result["status"] == "reverted"
        assert "lambda-url" in result["live_url"]

        # Verify deploy was called with V1 code
        mock_deploy.assert_called_once_with(
            "app-revert",
            CODE_V1,
            function_name=TEST_FUNCTION,
            region=TEST_REGION,
        )

        # Verify a revert step was logged
        timeline = await get_timeline(
            "app-revert", table_name=dynamodb_table, region=TEST_REGION
        )
        revert_steps = [s for s in timeline if s.step_type == StepType.REVERT]
        assert len(revert_steps) == 1
        assert revert_steps[0].status == StepStatus.REVERTED
        assert revert_steps[0].parent_step_id == "step-v1"
        assert revert_steps[0].code_snapshot == CODE_V1

    @pytest.mark.asyncio
    @patch("backend.agent.trace_logger.get_settings")
    @patch("backend.api.routes_timeline.get_settings")
    async def test_revert_missing_step_returns_404(
        self, mock_route_settings, mock_logger_settings, dynamodb_table
    ):
        mock_route_settings.return_value = _mock_settings()
        mock_logger_settings.return_value = _mock_settings()

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await revert_to_step("app-missing", "step-missing")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("backend.agent.trace_logger.get_settings")
    @patch("backend.api.routes_timeline.get_settings")
    async def test_revert_step_without_snapshot_returns_400(
        self, mock_route_settings, mock_logger_settings, dynamodb_table
    ):
        mock_route_settings.return_value = _mock_settings()
        mock_logger_settings.return_value = _mock_settings()

        # Step without code_snapshot
        step = TimelineStep(
            app_id="app-nosnapshot",
            step_id="step-plan",
            step_type=StepType.PLAN,
            reasoning="Just a plan, no code",
        )
        await log_step(step, table_name=dynamodb_table, region=TEST_REGION)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await revert_to_step("app-nosnapshot", "step-plan")
        assert exc_info.value.status_code == 400

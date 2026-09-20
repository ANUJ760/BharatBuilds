"""Tests for the Maintenance Orchestrator (Phase 10)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agent.maintenance_orchestrator import MaintenanceOrchestrator
from backend.agent.repair import CodeRepairProvider
from backend.models.app import (
    CandidateDeploymentResult,
    CandidateVerificationResult,
    HealthCheckResult,
    MaintenanceIssue,
    MaintenanceStatus,
    PromotionResult,
    RepairResult,
    StepStatus,
    StepType,
    TimelineStep,
)

SAMPLE_APP_ID = "test-app-123"
SAMPLE_FUNCTION_NAME = "test-lambda-function"
SAMPLE_BROKEN_CODE = "def render(): return 1 / 0"
SAMPLE_VALID_PATCH = "def render(): return '<h1>Fixed App</h1>'"
SAMPLE_INVALID_PATCH = "def broken( return 1"


@pytest.fixture
def sample_issue() -> MaintenanceIssue:
    return MaintenanceIssue(
        issue_type="5xx_error",
        severity="high",
        error_message="ZeroDivisionError in render()",
        endpoint="/",
        detection_source="synthetic_probe",
    )


def _mock_candidate_deployer(version: str = "1", url: str = "https://candidate.test.on.aws/"):
    return AsyncMock(
        return_value=CandidateDeploymentResult(
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_version=version,
            candidate_url=url,
        )
    )


def _mock_candidate_promoter(promoted_version: str = "1", previous_version: str = "0", url: str = "https://prod.test.on.aws/"):
    return AsyncMock(
        return_value=PromotionResult(
            function_name=SAMPLE_FUNCTION_NAME,
            promoted_version=promoted_version,
            previous_version=previous_version,
            prod_url=url,
        )
    )


def _mock_health_prober(is_healthy: bool = True, status_code: int = 200, latency_ms: int = 45, error_message: str | None = None):
    return AsyncMock(
        return_value=HealthCheckResult(
            url="https://candidate.test.on.aws/",
            is_healthy=is_healthy,
            status_code=status_code,
            latency_ms=latency_ms,
            error_message=error_message,
        )
    )


class TestMaintenanceOrchestrator:
    """MaintenanceOrchestrator unit test suite for Phase 10."""

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_successful_maintenance_first_attempt(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Division by zero in render",
                summary="Replaced division with valid HTML string",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="1")
        mock_prober = _mock_health_prober(is_healthy=True, status_code=200, latency_ms=50)
        mock_promoter = _mock_candidate_promoter(promoted_version="1", previous_version="0")

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.PROMOTED
        assert result.job.attempt_count == 1
        assert result.job.candidate_version == "1"
        assert result.job.promoted_version == "1"
        assert result.job.previous_version == "0"
        assert result.candidate_code == SAMPLE_VALID_PATCH
        assert result.verification_result.passed is True
        assert result.health_check_result.is_healthy is True
        assert result.promotion_result.promoted_version == "1"
        assert len(result.timeline_steps) == 5  # DETECT, DIAGNOSE, PATCH, VERIFY, PROMOTE

        step_types = [s.step_type for s in result.timeline_steps]
        assert step_types == [
            StepType.MAINTENANCE_DETECT,
            StepType.MAINTENANCE_DIAGNOSE,
            StepType.MAINTENANCE_PATCH,
            StepType.MAINTENANCE_VERIFY,
            StepType.MAINTENANCE_PROMOTE,
        ]
        assert mock_log_step.call_count == 5
        mock_deployer.assert_called_once()
        mock_prober.assert_called_once_with("https://candidate.test.on.aws/", timeout_seconds=pytest.approx(10.0))
        mock_promoter.assert_called_once_with(function_name=SAMPLE_FUNCTION_NAME, candidate_version="1", region="ap-south-1")

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_candidate_health_5xx_leads_to_rejection_prod_untouched(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Division by zero in render",
                summary="Replaced division with valid HTML string",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="2", url="https://candidate-v2.test.on.aws/")
        mock_prober = _mock_health_prober(
            is_healthy=False,
            status_code=500,
            latency_ms=120,
            error_message="HTTP 500 Server Error: Internal Server Error",
        )
        mock_promoter = _mock_candidate_promoter()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.REJECTED
        assert result.job.candidate_version == "2"
        assert result.job.promoted_version is None
        assert result.health_check_result.is_healthy is False
        assert result.health_check_result.status_code == 500
        assert result.promotion_result is None

        # Production promoter MUST NOT be called
        mock_promoter.assert_not_called()

        # Last timeline step must be MAINTENANCE_REJECT
        last_step = result.timeline_steps[-1]
        assert last_step.step_type == StepType.MAINTENANCE_REJECT
        assert last_step.status == StepStatus.OK
        assert "Production alias remains untouched on stable version" in last_step.reasoning
        assert "HTTP 500" in last_step.reasoning

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_candidate_health_timeout_leads_to_rejection(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="3")
        mock_prober = _mock_health_prober(
            is_healthy=False,
            status_code=None,
            latency_ms=10000,
            error_message="Request timed out after 10.0s",
        )
        mock_promoter = _mock_candidate_promoter()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.REJECTED
        mock_promoter.assert_not_called()
        assert result.timeline_steps[-1].step_type == StepType.MAINTENANCE_REJECT
        assert "Request timed out" in result.timeline_steps[-1].error_message

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_candidate_health_network_failure_leads_to_rejection(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="3")
        mock_prober = _mock_health_prober(
            is_healthy=False,
            status_code=None,
            latency_ms=15,
            error_message="Connection failed: [Errno 111] Connection refused",
        )
        mock_promoter = _mock_candidate_promoter()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.REJECTED
        mock_promoter.assert_not_called()
        assert result.timeline_steps[-1].step_type == StepType.MAINTENANCE_REJECT
        assert "Connection failed" in result.timeline_steps[-1].error_message

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_promotion_tracks_previous_production_version(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="4")
        mock_prober = _mock_health_prober(is_healthy=True, status_code=200, latency_ms=40)
        mock_promoter = _mock_candidate_promoter(promoted_version="4", previous_version="3")

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.PROMOTED
        assert result.job.promoted_version == "4"
        assert result.job.previous_version == "3"
        assert result.promotion_result.previous_version == "3"
        assert "replacing version 3" in result.job.summary

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_candidate_deployment_failure_leads_to_failed_status(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = AsyncMock(side_effect=RuntimeError("Lambda update_function_code failed"))
        mock_prober = _mock_health_prober()
        mock_promoter = _mock_candidate_promoter()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.FAILED
        assert "Candidate deployment failed" in result.summary
        mock_prober.assert_not_called()
        mock_promoter.assert_not_called()
        assert result.timeline_steps[-1].step_type == StepType.MAINTENANCE_REJECT
        assert result.timeline_steps[-1].status == StepStatus.ERROR

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_promotion_alias_update_failure_does_not_produce_promoted(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="5")
        mock_prober = _mock_health_prober(is_healthy=True, status_code=200)
        mock_promoter = AsyncMock(side_effect=RuntimeError("AWS ClientError: update_alias failed"))

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.FAILED
        assert "Promotion failed while updating prod alias" in result.summary
        assert result.job.candidate_version == "5"
        assert result.job.promoted_version is None
        assert result.timeline_steps[-1].step_type == StepType.MAINTENANCE_REJECT
        assert result.timeline_steps[-1].status == StepStatus.ERROR
        assert "Candidate version 5 preserved for diagnosis" in result.timeline_steps[-1].reasoning

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_local_verification_passes_semantic_distinction(self, mock_log_step, sample_issue):
        """Fix semantic problem: local verification passing is VERIFYING, not PROMOTED."""
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Bug fix",
                summary="Valid patch",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        # Local verification will pass, but candidate health check will fail
        mock_deployer = _mock_candidate_deployer(version="6")
        mock_prober = _mock_health_prober(is_healthy=False, status_code=502, error_message="HTTP 502 Bad Gateway")
        mock_promoter = _mock_candidate_promoter()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.verification_result.passed is True
        # Must be REJECTED, never PROMOTED if health probe fails
        assert result.status == MaintenanceStatus.REJECTED
        assert result.job.status == MaintenanceStatus.REJECTED
        mock_promoter.assert_not_called()

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_successful_maintenance_on_second_attempt(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        # Attempt 1 returns broken syntax, Attempt 2 returns valid code
        mock_provider.diagnose_and_repair = AsyncMock(
            side_effect=[
                RepairResult(
                    diagnosis="Attempt 1 bug diagnosis",
                    summary="Syntax error patch",
                    patched_code=SAMPLE_INVALID_PATCH,
                    is_success=True,
                ),
                RepairResult(
                    diagnosis="Attempt 2 refined diagnosis",
                    summary="Corrected syntax patch",
                    patched_code=SAMPLE_VALID_PATCH,
                    is_success=True,
                ),
            ]
        )

        mock_deployer = _mock_candidate_deployer(version="2")
        mock_prober = _mock_health_prober(is_healthy=True, status_code=200)
        mock_promoter = _mock_candidate_promoter(promoted_version="2", previous_version="1")

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            function_name=SAMPLE_FUNCTION_NAME,
            max_attempts=2,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.PROMOTED
        assert result.job.attempt_count == 2
        assert mock_provider.diagnose_and_repair.call_count == 2
        assert result.verification_result.passed is True
        assert result.promotion_result.promoted_version == "2"

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_rejection_after_max_attempts(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        # Both attempts return code that fails candidate verification
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="Repeatedly produces invalid code",
                summary="Broken syntax",
                patched_code=SAMPLE_INVALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer()
        mock_promoter = _mock_candidate_promoter()
        mock_prober = _mock_health_prober()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            max_attempts=2,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.REJECTED
        assert result.job.attempt_count == 2
        assert mock_provider.diagnose_and_repair.call_count == 2
        assert result.verification_result.passed is False

        mock_deployer.assert_not_called()
        mock_prober.assert_not_called()
        mock_promoter.assert_not_called()

        last_step = result.timeline_steps[-1]
        assert last_step.step_type == StepType.MAINTENANCE_REJECT
        assert "production remains untouched" in last_step.reasoning

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_repair_provider_failure(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="",
                summary="",
                patched_code="",
                is_success=False,
                error_message="Bedrock quota exceeded",
            )
        )

        mock_deployer = _mock_candidate_deployer()
        mock_promoter = _mock_candidate_promoter()
        mock_prober = _mock_health_prober()

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.FAILED
        assert "Bedrock quota exceeded" in result.summary

        mock_deployer.assert_not_called()
        mock_prober.assert_not_called()
        mock_promoter.assert_not_called()

        last_step = result.timeline_steps[-1]
        assert last_step.step_type == StepType.MAINTENANCE_REJECT
        assert last_step.status == StepStatus.ERROR

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.get_timeline", new_callable=AsyncMock)
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_no_existing_code_found(self, mock_log_step, mock_get_timeline, sample_issue):
        mock_get_timeline.return_value = []  # No steps in timeline

        orchestrator = MaintenanceOrchestrator()
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=None,
            persist_timeline=True,
        )

        assert result.status == MaintenanceStatus.FAILED
        assert "No existing code snapshot found" in result.summary
        assert len(result.timeline_steps) == 1
        assert result.timeline_steps[0].step_type == StepType.MAINTENANCE_REJECT

    @pytest.mark.asyncio
    @patch("backend.agent.maintenance_orchestrator.log_step", new_callable=AsyncMock)
    async def test_persist_timeline_false_does_not_call_log_step(self, mock_log_step, sample_issue):
        mock_provider = MagicMock(spec=CodeRepairProvider)
        mock_provider.diagnose_and_repair = AsyncMock(
            return_value=RepairResult(
                diagnosis="OK",
                summary="Fixed",
                patched_code=SAMPLE_VALID_PATCH,
                is_success=True,
            )
        )

        mock_deployer = _mock_candidate_deployer(version="1")
        mock_prober = _mock_health_prober(is_healthy=True, status_code=200)
        mock_promoter = _mock_candidate_promoter(promoted_version="1")

        orchestrator = MaintenanceOrchestrator(
            repair_provider=mock_provider,
            candidate_deployer=mock_deployer,
            candidate_promoter=mock_promoter,
            health_prober=mock_prober,
        )
        result = await orchestrator.run_maintenance(
            SAMPLE_APP_ID,
            sample_issue,
            existing_code=SAMPLE_BROKEN_CODE,
            persist_timeline=False,
        )

        assert result.status == MaintenanceStatus.PROMOTED
        assert mock_log_step.call_count == 0


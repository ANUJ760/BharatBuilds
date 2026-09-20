"""Tests for core Pydantic data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.models import (
    App,
    AppStatus,
    ClarifyQuestion,
    ClarifyResponse,
    Invite,
    MaintenanceIssue,
    MaintenanceJob,
    MaintenanceStatus,
    Role,
    StepStatus,
    StepType,
    TimelineStep,
)


class TestApp:
    """App model tests."""

    def test_create_minimal(self):
        app = App(owner_id="user-1", title="My App", prompt="build me a todo app")
        assert app.app_id  # auto-generated
        assert app.owner_id == "user-1"
        assert app.status == AppStatus.PENDING
        assert app.live_url is None
        assert app.created_at is not None

    def test_create_full(self):
        app = App(
            app_id="fixed-id",
            owner_id="user-1",
            title="Expense Tracker",
            prompt="build an expense tracker",
            live_url="https://example.com/app/fixed-id",
            status=AppStatus.DEPLOYED,
        )
        assert app.app_id == "fixed-id"
        assert app.status == AppStatus.DEPLOYED
        assert app.live_url == "https://example.com/app/fixed-id"

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            App(owner_id="user-1", title="", prompt="build something")

    def test_rejects_empty_prompt(self):
        with pytest.raises(ValidationError):
            App(owner_id="user-1", title="My App", prompt="")


class TestTimelineStep:
    """TimelineStep model tests."""

    def test_create_minimal(self):
        step = TimelineStep(app_id="app-1", step_type=StepType.PLAN)
        assert step.step_id  # auto-generated
        assert step.app_id == "app-1"
        assert step.step_type == StepType.PLAN
        assert step.status == StepStatus.OK

    def test_create_with_code_snapshot(self):
        step = TimelineStep(
            app_id="app-1",
            step_type=StepType.CODEGEN,
            code_snapshot="print('hello')",
            code_diff="+print('hello')",
            latency_ms=150,
            token_usage=500,
        )
        assert step.code_snapshot == "print('hello')"
        assert step.latency_ms == 150

    def test_rejects_negative_latency(self):
        with pytest.raises(ValidationError):
            TimelineStep(app_id="app-1", step_type=StepType.PLAN, latency_ms=-1)

    def test_rejects_negative_token_usage(self):
        with pytest.raises(ValidationError):
            TimelineStep(app_id="app-1", step_type=StepType.PLAN, token_usage=-5)


class TestInvite:
    """Invite model tests."""

    def test_create_invite(self):
        invite = Invite(app_id="app-1", email="user@example.com", role=Role.EDITOR)
        assert invite.role == Role.EDITOR

    def test_default_role_is_viewer(self):
        invite = Invite(app_id="app-1", email="user@example.com")
        assert invite.role == Role.VIEWER


class TestClarifyModels:
    """ClarifyQuestion / ClarifyResponse tests."""

    def test_clarify_no_questions(self):
        resp = ClarifyResponse(needs_clarification=False)
        assert resp.questions == []

    def test_clarify_with_questions(self):
        resp = ClarifyResponse(
            needs_clarification=True,
            questions=[
                ClarifyQuestion(
                    question="Single-user or multi-user?",
                    suggested_default="Single-user",
                    why_it_matters="Affects data model and auth flow",
                ),
            ],
        )
        assert len(resp.questions) == 1
        assert resp.questions[0].suggested_default == "Single-user"


class TestMaintenanceModels:
    """MaintenanceIssue, MaintenanceStatus, and MaintenanceJob tests."""

    def test_maintenance_step_type_enums(self):
        assert StepType.MAINTENANCE_DETECT == "maintenance_detect"
        assert StepType.MAINTENANCE_DIAGNOSE == "maintenance_diagnose"
        assert StepType.MAINTENANCE_PATCH == "maintenance_patch"
        assert StepType.MAINTENANCE_VERIFY == "maintenance_verify"
        assert StepType.MAINTENANCE_PROMOTE == "maintenance_promote"
        assert StepType.MAINTENANCE_REJECT == "maintenance_reject"

    def test_maintenance_issue_creation_and_defaults(self):
        issue = MaintenanceIssue(
            issue_type="5xx_error",
            error_message="Internal server error on GET /",
        )
        assert issue.issue_id
        assert issue.issue_type == "5xx_error"
        assert issue.severity == "high"
        assert issue.detection_source == "synthetic_probe"
        assert issue.detected_at is not None
        assert issue.stack_trace is None

    def test_maintenance_issue_full(self):
        issue = MaintenanceIssue(
            issue_id="custom-issue-id",
            issue_type="runtime_exception",
            severity="critical",
            error_message="ZeroDivisionError: division by zero",
            stack_trace="Traceback (most recent call last):\n  File 'app_code.py', line 10",
            endpoint="/calculate",
            detection_source="health_check",
        )
        assert issue.issue_id == "custom-issue-id"
        assert issue.severity == "critical"
        assert issue.endpoint == "/calculate"
        assert issue.stack_trace is not None

    def test_maintenance_issue_validation(self):
        with pytest.raises(ValidationError):
            MaintenanceIssue(issue_type="", error_message="some error")
        with pytest.raises(ValidationError):
            MaintenanceIssue(issue_type="5xx", error_message="")

    def test_maintenance_job_creation_and_lifecycle(self):
        from backend.models import MaintenanceJob, MaintenanceStatus

        issue = MaintenanceIssue(
            issue_type="syntax_error",
            error_message="SyntaxError: invalid syntax",
        )
        job = MaintenanceJob(app_id="app-123", issue=issue)

        assert job.job_id
        assert job.app_id == "app-123"
        assert job.status == MaintenanceStatus.PENDING
        assert job.issue.issue_type == "syntax_error"
        assert job.attempt_count == 1
        assert job.candidate_step_id is None

    def test_maintenance_serialization_roundtrip(self):
        from backend.models import MaintenanceJob, MaintenanceStatus

        issue = MaintenanceIssue(
            issue_type="5xx_error",
            error_message="Handler crashed",
            severity="high",
        )
        job = MaintenanceJob(
            app_id="app-456",
            status=MaintenanceStatus.VERIFYING,
            issue=issue,
            candidate_step_id="step-cand-1",
        )

        dumped = job.model_dump(mode="json")
        loaded = MaintenanceJob.model_validate(dumped)

        assert loaded.job_id == job.job_id
        assert loaded.status == MaintenanceStatus.VERIFYING
        assert loaded.issue.error_message == "Handler crashed"
        assert loaded.candidate_step_id == "step-cand-1"


class TestMaintenanceTimelineStep:
    """TimelineStep compatibility with maintenance step types."""

    def test_maintenance_steps_in_timeline(self):
        detect_step = TimelineStep(
            app_id="app-1",
            step_type=StepType.MAINTENANCE_DETECT,
            reasoning="Synthetic health check probe received 500 error",
        )
        diagnose_step = TimelineStep(
            app_id="app-1",
            step_type=StepType.MAINTENANCE_DIAGNOSE,
            parent_step_id=detect_step.step_id,
            reasoning="Identified unhandled division by zero in render()",
        )
        patch_step = TimelineStep(
            app_id="app-1",
            step_type=StepType.MAINTENANCE_PATCH,
            parent_step_id=diagnose_step.step_id,
            code_snapshot="def render(): return 'fixed'",
            code_diff="+def render(): return 'fixed'",
        )
        verify_step = TimelineStep(
            app_id="app-1",
            step_type=StepType.MAINTENANCE_VERIFY,
            parent_step_id=patch_step.step_id,
            status=StepStatus.OK,
            reasoning="All candidate health checks passed",
        )
        promote_step = TimelineStep(
            app_id="app-1",
            step_type=StepType.MAINTENANCE_PROMOTE,
            parent_step_id=verify_step.step_id,
            status=StepStatus.OK,
            reasoning="Candidate promoted to live Lambda",
        )

        assert detect_step.step_type == StepType.MAINTENANCE_DETECT
        assert diagnose_step.parent_step_id == detect_step.step_id
        assert patch_step.code_snapshot == "def render(): return 'fixed'"
        assert verify_step.status == StepStatus.OK
        assert promote_step.step_type == StepType.MAINTENANCE_PROMOTE


class TestDeploymentAndPromotionModels:
    """CandidateDeploymentResult and PromotionResult tests."""

    def test_candidate_deployment_result(self):
        from backend.models import CandidateDeploymentResult

        res = CandidateDeploymentResult(
            function_name="bharatbuilds-fn",
            candidate_version="3",
            candidate_url="https://candidate-url.test",
        )
        assert res.function_name == "bharatbuilds-fn"
        assert res.candidate_version == "3"
        assert res.candidate_url == "https://candidate-url.test"
        assert res.deployed_at is not None

    def test_promotion_result(self):
        from backend.models import PromotionResult

        res = PromotionResult(
            function_name="bharatbuilds-fn",
            promoted_version="3",
            previous_version="2",
            prod_url="https://prod-url.test",
        )
        assert res.function_name == "bharatbuilds-fn"
        assert res.promoted_version == "3"
        assert res.previous_version == "2"
        assert res.prod_url == "https://prod-url.test"
        assert res.promoted_at is not None


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

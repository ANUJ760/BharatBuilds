"""Tests for the clarify-then-build ambiguity check pass."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from backend.agent.clarify import check_ambiguity
from backend.models.app import ClarifyResponse


# ── Fixtures ─────────────────────────────────────────────────────────────

NO_QUESTIONS_PAYLOAD = {"needs_clarification": False, "questions": []}

THREE_QUESTIONS_PAYLOAD = {
    "needs_clarification": True,
    "questions": [
        {
            "question": "Single-user or multi-user?",
            "suggested_default": "Single-user",
            "why_it_matters": "Multi-user needs auth and per-user data isolation",
        },
        {
            "question": "Should data persist across sessions?",
            "suggested_default": "Yes, persist to a database",
            "why_it_matters": "Ephemeral data means no DB; persistent needs DynamoDB",
        },
        {
            "question": "Do you need email notifications?",
            "suggested_default": "No",
            "why_it_matters": "Email requires SES setup and a verified sender address",
        },
    ],
}


# ── Tests ────────────────────────────────────────────────────────────────


class TestCheckAmbiguity:
    """check_ambiguity tests with mocked Bedrock calls."""

    @pytest.mark.asyncio
    @patch("backend.agent.clarify.invoke_model_json")
    async def test_no_clarification_needed(self, mock_invoke):
        mock_invoke.return_value = NO_QUESTIONS_PAYLOAD

        result = await check_ambiguity(
            "Build me a simple todo list",
            model_id="deepseek.v3-1",
        )

        assert isinstance(result, ClarifyResponse)
        assert result.needs_clarification is False
        assert result.questions == []
        mock_invoke.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.agent.clarify.invoke_model_json")
    async def test_three_questions(self, mock_invoke):
        mock_invoke.return_value = THREE_QUESTIONS_PAYLOAD

        result = await check_ambiguity(
            "Build me a tracker",
            model_id="deepseek.v3-1",
        )

        assert isinstance(result, ClarifyResponse)
        assert result.needs_clarification is True
        assert len(result.questions) == 3
        assert result.questions[0].question == "Single-user or multi-user?"
        assert result.questions[0].suggested_default == "Single-user"
        assert result.questions[0].why_it_matters

    @pytest.mark.asyncio
    @patch("backend.agent.clarify.invoke_model_json")
    async def test_one_question(self, mock_invoke):
        mock_invoke.return_value = {
            "needs_clarification": True,
            "questions": [
                {
                    "question": "Public or private?",
                    "suggested_default": "Private",
                    "why_it_matters": "Affects auth requirements",
                }
            ],
        }

        result = await check_ambiguity("Build an app", model_id="deepseek.v3-1")

        assert result.needs_clarification is True
        assert len(result.questions) == 1

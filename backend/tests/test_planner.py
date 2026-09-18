"""Tests for the ReAct planner and codegen — mocked Bedrock responses."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from backend.agent.codegen import generate_code
from backend.agent.planner import plan_and_execute
from backend.models.app import StepStatus, StepType


# ── Helpers ──────────────────────────────────────────────────────────────

MOCK_PLAN = {
    "app_title": "Todo Tracker",
    "features": ["Add tasks", "Mark complete", "Delete tasks"],
    "data_model": "Tasks with title, status, created_at",
    "ui_description": "Simple list with checkboxes",
    "technical_notes": "In-memory storage, no DB needed",
}

MOCK_CODE = '''\
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8080))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Todo App</h1>")

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
'''

MOCK_REVIEW_PASS = {"is_valid": True, "issues": []}

MOCK_REVIEW_FAIL = {
    "is_valid": False,
    "issues": ["Missing import for json module"],
    "fix_instructions": "Add 'import json' at the top of the file",
}


def _mock_invoke_return(payload):
    """Create a side_effect function for invoke_model_json / invoke_model."""
    return payload


# ── Tests ────────────────────────────────────────────────────────────────


class TestCodegen:
    """codegen.generate_code tests."""

    @pytest.mark.asyncio
    @patch("backend.agent.codegen.invoke_model")
    async def test_generate_basic(self, mock_invoke):
        mock_invoke.return_value = MOCK_CODE

        code = await generate_code(
            "Build a todo app", model_id="deepseek.v3-1"
        )
        assert "HTTPServer" in code
        assert "Todo" in code
        mock_invoke.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.agent.codegen.invoke_model")
    async def test_generate_with_clarifications(self, mock_invoke):
        mock_invoke.return_value = MOCK_CODE

        code = await generate_code(
            "Build a tracker",
            clarifications={"scope": "single-user", "persist": "no"},
            model_id="deepseek.v3-1",
        )
        # Verify clarifications were passed in the prompt
        call_args = mock_invoke.call_args
        prompt_sent = call_args[0][0]
        assert "single-user" in prompt_sent
        assert "persist" in prompt_sent

    @pytest.mark.asyncio
    @patch("backend.agent.codegen.invoke_model")
    async def test_strips_markdown_fences(self, mock_invoke):
        mock_invoke.return_value = f"```python\n{MOCK_CODE}\n```"

        code = await generate_code("Build an app", model_id="deepseek.v3-1")
        assert not code.startswith("```")
        assert not code.endswith("```")


class TestPlanner:
    """plan_and_execute tests with mocked Bedrock."""

    @pytest.mark.asyncio
    @patch("backend.agent.planner.invoke_model_json")
    @patch("backend.agent.planner.generate_code")
    async def test_successful_plan_and_codegen(self, mock_codegen, mock_invoke_json):
        # Plan returns successfully, review passes
        mock_invoke_json.side_effect = [MOCK_PLAN, MOCK_REVIEW_PASS]
        mock_codegen.return_value = MOCK_CODE

        code, steps = await plan_and_execute(
            "Build a todo app",
            model_id="deepseek.v3-1",
            app_id="test-app",
        )

        assert code == MOCK_CODE
        assert len(steps) == 3  # plan + codegen + review
        assert steps[0].step_type == StepType.PLAN
        assert steps[0].status == StepStatus.OK
        assert steps[1].step_type == StepType.CODEGEN
        assert steps[1].status == StepStatus.OK
        assert steps[1].code_snapshot == MOCK_CODE
        assert steps[2].step_type == StepType.TOOL_CALL  # review

    @pytest.mark.asyncio
    @patch("backend.agent.planner.invoke_model_json")
    @patch("backend.agent.planner.generate_code")
    async def test_retry_on_review_failure(self, mock_codegen, mock_invoke_json):
        # Plan succeeds, first review fails, second attempt passes
        mock_invoke_json.side_effect = [
            MOCK_PLAN,        # plan
            MOCK_REVIEW_FAIL, # review (fail)
            MOCK_REVIEW_PASS, # review (pass after retry)
        ]
        mock_codegen.return_value = MOCK_CODE

        code, steps = await plan_and_execute(
            "Build a todo app",
            model_id="deepseek.v3-1",
            app_id="test-app",
        )

        assert code == MOCK_CODE
        # plan + codegen + review(fail) + retry + codegen + review(pass) = 6
        assert len(steps) == 6
        assert steps[0].step_type == StepType.PLAN
        assert steps[1].step_type == StepType.CODEGEN
        assert steps[2].step_type == StepType.TOOL_CALL  # failed review
        assert steps[2].status == StepStatus.ERROR
        assert steps[3].step_type == StepType.RETRY
        assert steps[4].step_type == StepType.CODEGEN
        assert steps[5].step_type == StepType.TOOL_CALL  # passed review
        assert steps[5].status == StepStatus.OK

    @pytest.mark.asyncio
    @patch("backend.agent.planner.invoke_model_json")
    @patch("backend.agent.planner.generate_code")
    async def test_with_clarifications(self, mock_codegen, mock_invoke_json):
        mock_invoke_json.side_effect = [MOCK_PLAN, MOCK_REVIEW_PASS]
        mock_codegen.return_value = MOCK_CODE

        code, steps = await plan_and_execute(
            "Build a tracker",
            clarifications={"scope": "single-user"},
            model_id="deepseek.v3-1",
            app_id="test-app",
        )

        assert code == MOCK_CODE
        # Plan step should include clarifications in input
        assert "single-user" in steps[0].input_text

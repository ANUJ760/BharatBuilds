"""Tests for the maintenance diagnosis and code repair module."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

# Ensure boto3 mocks exist in environments where AWS SDK is mocked
if "boto3" not in sys.modules:
    sys.modules["boto3"] = MagicMock()
if "botocore" not in sys.modules:
    sys.modules["botocore"] = MagicMock()
if "botocore.exceptions" not in sys.modules:
    mock_exceptions = MagicMock()
    mock_exceptions.ClientError = type("ClientError", (Exception,), {})
    sys.modules["botocore.exceptions"] = mock_exceptions

import pytest

from backend.agent.repair import (
    BedrockCodeRepairProvider,
    CodeRepairProvider,
    _format_issue_prompt,
    _validate_python_syntax,
    diagnose_and_repair,
)
from backend.models.app import MaintenanceIssue, RepairResult


SAMPLE_EXISTING_CODE = """\
def render():
    return 10 / 0
"""

SAMPLE_FIXED_CODE = """\
def render():
    return "<h1>Fixed: No division by zero</h1>"
""".strip()


@pytest.fixture
def sample_issue() -> MaintenanceIssue:
    return MaintenanceIssue(
        issue_type="runtime_exception",
        severity="critical",
        error_message="ZeroDivisionError: division by zero",
        stack_trace="Traceback (most recent call last):\n  File 'app_code.py', line 2, in render\n    return 10 / 0",
        endpoint="/render",
        detection_source="synthetic_probe",
    )


class TestRepairPromptFormatting:
    """Prompt construction tests."""

    def test_format_issue_prompt_contains_all_details(self, sample_issue):
        prompt = _format_issue_prompt(SAMPLE_EXISTING_CODE, sample_issue)
        assert "ZeroDivisionError: division by zero" in prompt
        assert "/render" in prompt
        assert "runtime_exception" in prompt
        assert "Traceback (most recent call last)" in prompt
        assert "10 / 0" in prompt


class TestSyntaxValidation:
    """Python syntax validation helper tests."""

    def test_valid_syntax(self):
        is_valid, err = _validate_python_syntax("def render(): return 'ok'")
        assert is_valid is True
        assert err is None

    def test_invalid_syntax(self):
        is_valid, err = _validate_python_syntax("def render( return 'syntax error'")
        assert is_valid is False
        assert "SyntaxError" in err

    def test_empty_syntax(self):
        is_valid, err = _validate_python_syntax("   ")
        assert is_valid is False
        assert "empty" in err.lower()


class TestBedrockCodeRepairProvider:
    """BedrockCodeRepairProvider unit tests with mocked Bedrock responses."""

    @pytest.mark.asyncio
    @patch("backend.agent.repair.invoke_model_json")
    async def test_successful_repair(self, mock_invoke_json, sample_issue):
        mock_invoke_json.return_value = {
            "diagnosis": "Division by zero in render() function causes 500 error on GET /render.",
            "summary": "Replaced '10 / 0' with static HTML output.",
            "patched_code": SAMPLE_FIXED_CODE,
        }

        provider = BedrockCodeRepairProvider(model_id="test-model", region="ap-south-1")
        result = await provider.diagnose_and_repair(SAMPLE_EXISTING_CODE, sample_issue)

        assert result.is_success is True
        assert "Division by zero" in result.diagnosis
        assert "Replaced" in result.summary
        assert result.patched_code == SAMPLE_FIXED_CODE
        assert result.error_message is None

    @pytest.mark.asyncio
    @patch("backend.agent.repair.invoke_model_json")
    async def test_repair_strips_markdown_fences(self, mock_invoke_json, sample_issue):
        mock_invoke_json.return_value = {
            "diagnosis": "Syntax issue",
            "summary": "Fixed syntax",
            "patched_code": f"```python\n{SAMPLE_FIXED_CODE}\n```",
        }

        result = await diagnose_and_repair(SAMPLE_EXISTING_CODE, sample_issue)

        assert result.is_success is True
        assert "```" not in result.patched_code
        assert "def render():" in result.patched_code

    @pytest.mark.asyncio
    async def test_empty_existing_code_fails_gracefully(self, sample_issue):
        result = await diagnose_and_repair("", sample_issue)
        assert result.is_success is False
        assert "cannot be empty" in result.error_message

    @pytest.mark.asyncio
    @patch("backend.agent.repair.invoke_model_json")
    async def test_missing_patched_code_in_response(self, mock_invoke_json, sample_issue):
        mock_invoke_json.return_value = {
            "diagnosis": "Identified error",
            "summary": "No code provided",
            "patched_code": "",
        }

        result = await diagnose_and_repair(SAMPLE_EXISTING_CODE, sample_issue)
        assert result.is_success is False
        assert "did not contain valid patched code" in result.error_message

    @pytest.mark.asyncio
    @patch("backend.agent.repair.invoke_model_json")
    async def test_invalid_syntax_in_patched_code(self, mock_invoke_json, sample_issue):
        mock_invoke_json.return_value = {
            "diagnosis": "Bug found",
            "summary": "Attempted fix",
            "patched_code": "def broken_syntax( { missing closing paren",
        }

        result = await diagnose_and_repair(SAMPLE_EXISTING_CODE, sample_issue)
        assert result.is_success is False
        assert "SyntaxError" in result.error_message

    @pytest.mark.asyncio
    @patch("backend.agent.repair.invoke_model_json")
    async def test_bedrock_exception_handled_safely(self, mock_invoke_json, sample_issue):
        mock_invoke_json.side_effect = RuntimeError("Bedrock service timeout")

        result = await diagnose_and_repair(SAMPLE_EXISTING_CODE, sample_issue)
        assert result.is_success is False
        assert "Model invocation failed" in result.error_message


class TestCustomRepairProvider:
    """Test custom CodeRepairProvider pluggability."""

    @pytest.mark.asyncio
    async def test_custom_provider_can_be_injected(self, sample_issue):
        class MockCustomProvider(CodeRepairProvider):
            async def diagnose_and_repair(
                self,
                existing_code: str,
                issue: MaintenanceIssue,
            ) -> RepairResult:
                return RepairResult(
                    diagnosis="Custom diagnostic provider",
                    summary="Custom patch applied",
                    patched_code="def render(): return 'custom'",
                    is_success=True,
                )

        custom_provider = MockCustomProvider()
        result = await diagnose_and_repair(
            SAMPLE_EXISTING_CODE,
            sample_issue,
            provider=custom_provider,
        )

        assert result.is_success is True
        assert result.diagnosis == "Custom diagnostic provider"
        assert result.patched_code == "def render(): return 'custom'"

"""Tests for candidate code verification module."""

from __future__ import annotations

import pytest

from backend.agent.candidate_verifier import verify_candidate_code
from backend.models.app import CandidateVerificationResult


VALID_RENDER_CODE = """\
def render():
    return "<h1>My Verified App</h1><p>Running smoothly</p>"
"""

VALID_HANDLER_CODE = """\
def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "{\\"status\\": \\"ok\\"}"
    }
"""

SYNTAX_ERROR_CODE = """\
def render(
    return "broken syntax"
"""

MISSING_ENTRY_POINT_CODE = """\
# A module without render() or handler()
x = 10
y = 20
def helper_only():
    return x + y
"""

RUNTIME_ERROR_RENDER_CODE = """\
def render():
    x = 10 / 0  # ZeroDivisionError
    return f"Result: {x}"
"""

RUNTIME_ERROR_HANDLER_CODE = """\
def handler(event, context):
    raise KeyError("Missing required key in config")
"""

HANDLER_500_STATUS_CODE = """\
def handler(event, context):
    return {
        "statusCode": 500,
        "body": "Database connection failed"
    }
"""

MODULE_LOAD_CRASH_CODE = """\
# Fails during module evaluation
raise ValueError("Invalid initialization parameters")

def render():
    return "never reached"
"""


class TestCandidateVerifier:
    """Unit tests for verify_candidate_code."""

    def test_valid_render_code_passes(self):
        result = verify_candidate_code(VALID_RENDER_CODE)
        assert result.passed is True
        assert result.entry_point == "render"
        assert result.checks_passed == [
            "syntax_compilation",
            "security_safety_guard",
            "entry_point_detection",
            "runtime_execution",
        ]
        assert result.checks_failed == []
        assert result.error_message is None
        assert "My Verified App" in result.response_sample

    def test_valid_handler_code_passes(self):
        result = verify_candidate_code(VALID_HANDLER_CODE)
        assert result.passed is True
        assert result.entry_point == "handler"
        assert result.checks_passed == [
            "syntax_compilation",
            "security_safety_guard",
            "entry_point_detection",
            "runtime_execution",
        ]
        assert result.checks_failed == []
        assert result.error_message is None


    def test_syntax_error_fails(self):
        result = verify_candidate_code(SYNTAX_ERROR_CODE)
        assert result.passed is False
        assert "syntax_compilation" in result.checks_failed
        assert "SyntaxError" in result.error_message

    def test_missing_entry_point_fails(self):
        result = verify_candidate_code(MISSING_ENTRY_POINT_CODE)
        assert result.passed is False
        assert "entry_point_detection" in result.checks_failed
        assert "Missing entry point" in result.error_message

    def test_runtime_error_in_render_fails(self):
        result = verify_candidate_code(RUNTIME_ERROR_RENDER_CODE)
        assert result.passed is False
        assert "runtime_execution" in result.checks_failed
        assert "ZeroDivisionError" in result.error_message

    def test_runtime_error_in_handler_fails(self):
        result = verify_candidate_code(RUNTIME_ERROR_HANDLER_CODE)
        assert result.passed is False
        assert "runtime_execution" in result.checks_failed
        assert "KeyError" in result.error_message

    def test_handler_returning_500_fails(self):
        result = verify_candidate_code(HANDLER_500_STATUS_CODE)
        assert result.passed is False
        assert "runtime_execution" in result.checks_failed
        assert "500" in result.error_message

    def test_module_load_crash_fails(self):
        result = verify_candidate_code(MODULE_LOAD_CRASH_CODE)
        assert result.passed is False
        assert "entry_point_detection" in result.checks_failed
        assert "ValueError" in result.error_message

    def test_empty_code_fails(self):
        result = verify_candidate_code("   ")
        assert result.passed is False
        assert "syntax_compilation" in result.checks_failed
        assert "cannot be empty" in result.error_message

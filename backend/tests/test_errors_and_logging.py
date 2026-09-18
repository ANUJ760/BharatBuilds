"""Tests for global error handling, consistent JSON error shapes, and structured logging."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.logger import configure_logging, get_logger
from backend.main import app


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestGlobalErrorHandling:
    """Test consistent JSON error responses: {error, message, request_id}."""

    def test_404_not_found_shape(self, client):
        resp = client.get("/nonexistent-endpoint-xyz")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert "message" in data
        assert "request_id" in data
        assert resp.headers.get("X-Request-ID") == data["request_id"]

    def test_422_validation_error_shape(self, client):
        # Missing required 'prompt'
        resp = client.post("/apps/clarify", json={})
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"
        assert "message" in data
        assert "request_id" in data
        assert "detail" in data
        assert resp.headers.get("X-Request-ID") == data["request_id"]

    @patch("backend.api.routes_apps.check_ambiguity")
    @patch("backend.api.routes_apps.get_settings")
    def test_deliberate_bedrock_failure_returns_consistent_error(
        self, mock_settings, mock_clarify, client
    ):
        mock_settings.return_value = MagicMock(
            bedrock_model_id="deepseek.v3-1",
            aws_region="ap-south-1",
        )
        # Trigger deliberate error during prompt clarify (e.g. Bedrock Throttling or failure)
        mock_clarify.side_effect = RuntimeError("Amazon Bedrock service is currently unavailable")

        resp = client.post("/apps/clarify", json={"prompt": "build me an app"})
        assert resp.status_code == 500
        data = resp.json()

        # Check required error format: {error, message, request_id}
        assert data["error"] == "InternalServerError"
        assert "unexpected error" in data["message"].lower()
        assert "Bedrock service is currently unavailable" in str(data["detail"])
        assert "request_id" in data
        assert resp.headers.get("X-Request-ID") == data["request_id"]


class TestStructuredLogging:
    """Test structured JSON log formatter."""

    def test_structured_log_line_format(self, capsys):
        configure_logging(log_level="info", json_format=True)
        test_logger = get_logger("test.audit")
        test_logger.info("agent_step_executed", step_id="step-123", latency_ms=45)

        captured = capsys.readouterr().out.strip()
        lines = [line for line in captured.splitlines() if "agent_step_executed" in line]
        assert len(lines) >= 1

        log_json = json.loads(lines[-1])
        assert log_json["event"] == "agent_step_executed"
        assert log_json["step_id"] == "step-123"
        assert log_json["latency_ms"] == 45
        assert log_json["level"] == "info"
        assert "timestamp" in log_json

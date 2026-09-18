"""Tests for the Bedrock client wrapper — fully mocked, no real AWS calls."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from backend.agent import bedrock_client


# ── Helpers ──────────────────────────────────────────────────────────────


def _mock_bedrock_response(body: dict) -> dict:
    """Build a mock response dict matching the boto3 invoke_model shape."""
    return {
        "body": BytesIO(json.dumps(body).encode()),
    }


# ── Tests ────────────────────────────────────────────────────────────────


class TestInvokeModel:
    """invoke_model tests with mocked Bedrock."""

    @patch.object(bedrock_client, "_get_client")
    def test_plain_text_messages_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {"content": [{"type": "text", "text": "Hello world"}]}
        )

        result = bedrock_client.invoke_model(
            "Say hello", model_id="deepseek.v3-1"
        )
        assert result == "Hello world"
        mock_client.invoke_model.assert_called_once()

    @patch.object(bedrock_client, "_get_client")
    def test_deepseek_choices_format(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {
                "choices": [
                    {"message": {"role": "assistant", "content": "DeepSeek reply"}}
                ]
            }
        )

        result = bedrock_client.invoke_model(
            "Test prompt", model_id="deepseek.v3-1"
        )
        assert result == "DeepSeek reply"

    @patch.object(bedrock_client, "_get_client")
    def test_completion_format(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {"completion": "Old-style completion"}
        )

        result = bedrock_client.invoke_model("Test", model_id="test-model")
        assert result == "Old-style completion"


class TestInvokeModelJson:
    """invoke_model_json tests."""

    @patch.object(bedrock_client, "_get_client")
    def test_json_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        payload = {"key": "value", "count": 42}
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {"content": [{"type": "text", "text": json.dumps(payload)}]}
        )

        result = bedrock_client.invoke_model_json(
            "Return JSON", model_id="deepseek.v3-1"
        )
        assert result == payload

    @patch.object(bedrock_client, "_get_client")
    def test_json_with_markdown_fences(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        raw_text = '```json\n{"parsed": true}\n```'
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {"content": [{"type": "text", "text": raw_text}]}
        )

        result = bedrock_client.invoke_model_json(
            "Return JSON", model_id="deepseek.v3-1"
        )
        assert result == {"parsed": True}

    @patch.object(bedrock_client, "_get_client")
    def test_invalid_json_raises(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.invoke_model.return_value = _mock_bedrock_response(
            {"content": [{"type": "text", "text": "this is not json at all"}]}
        )

        with pytest.raises(ValueError, match="Failed to parse"):
            bedrock_client.invoke_model_json(
                "Return JSON", model_id="deepseek.v3-1"
            )


class TestRetryBehavior:
    """Verify exponential backoff retry logic."""

    @patch.object(bedrock_client, "time")
    @patch.object(bedrock_client, "_get_client")
    def test_retries_on_throttling(self, mock_get_client, mock_time):
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        throttle_error = ClientError(
            {"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
            "InvokeModel",
        )
        success_response = _mock_bedrock_response(
            {"content": [{"type": "text", "text": "finally"}]}
        )

        mock_client.invoke_model.side_effect = [
            throttle_error,
            throttle_error,
            success_response,
        ]

        result = bedrock_client.invoke_model("retry me", model_id="test")
        assert result == "finally"
        assert mock_client.invoke_model.call_count == 3
        assert mock_time.sleep.call_count == 2

    @patch.object(bedrock_client, "_get_client")
    def test_raises_after_max_retries(self, mock_get_client):
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        throttle_error = ClientError(
            {"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
            "InvokeModel",
        )
        mock_client.invoke_model.side_effect = throttle_error

        with pytest.raises(ClientError):
            bedrock_client.invoke_model("fail", model_id="test")
        # 1 initial + 3 retries = 4 total
        assert mock_client.invoke_model.call_count == 4

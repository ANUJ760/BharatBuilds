"""Tests for the HTTP synthetic health probe module."""

from __future__ import annotations

import httpx
import pytest

from backend.agent.health_probe import probe_url
from backend.models.app import HealthCheckResult


@pytest.mark.asyncio
async def test_probe_200_success():
    """Test successful 200 OK response."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<h1>App Healthy</h1>")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://example.com/app", client=client)

    assert result.is_healthy is True
    assert result.status_code == 200
    assert result.latency_ms is not None and result.latency_ms >= 0
    assert result.error_message is None
    assert result.url == "https://example.com/app"


@pytest.mark.asyncio
async def test_probe_201_created_success():
    """Test 201 Created is treated as healthy."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, text="Created")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://example.com/app", client=client)

    assert result.is_healthy is True
    assert result.status_code == 201
    assert result.error_message is None


@pytest.mark.asyncio
async def test_probe_404_client_error():
    """Test 404 Client Error response."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="Not Found")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://example.com/missing", client=client)

    assert result.is_healthy is False
    assert result.status_code == 404
    assert "404" in result.error_message
    assert "Client Error" in result.error_message


@pytest.mark.asyncio
async def test_probe_500_server_error():
    """Test 500 Server Error response."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal server error: division by zero")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://example.com/broken", client=client)

    assert result.is_healthy is False
    assert result.status_code == 500
    assert "500 Server Error" in result.error_message
    assert "division by zero" in result.error_message


@pytest.mark.asyncio
async def test_probe_timeout():
    """Test timeout exception handling."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Read timed out")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://example.com/slow", timeout_seconds=2.0, client=client)

    assert result.is_healthy is False
    assert result.status_code is None
    assert "timed out" in result.error_message.lower()


@pytest.mark.asyncio
async def test_probe_connection_error():
    """Test network connection error handling."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Failed to establish a new connection")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("https://unreachable-host.aws.internal", client=client)

    assert result.is_healthy is False
    assert result.status_code is None
    assert "Connection failed" in result.error_message


@pytest.mark.asyncio
async def test_probe_empty_url():
    """Test empty URL edge case."""
    result = await probe_url("")
    assert result.is_healthy is False
    assert "cannot be empty" in result.error_message


@pytest.mark.asyncio
async def test_probe_url_protocol_normalization():
    """Test URL without http/https schema is normalized to https."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.scheme == "https"
        return httpx.Response(200, text="OK")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_url("app.lambda-url.ap-south-1.on.aws", client=client)

    assert result.is_healthy is True
    assert result.url == "https://app.lambda-url.ap-south-1.on.aws"

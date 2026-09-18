"""HTTP Synthetic Health Probe for deployed applications.

Performs asynchronous HTTP health checks against deployed application URLs
(e.g., Lambda Function URLs, ALB routes) to detect 5xx server errors, client
errors, timeouts, and network connection failures.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from backend.models.app import HealthCheckResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 10.0


async def probe_url(
    url: str,
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    client: httpx.AsyncClient | None = None,
) -> HealthCheckResult:
    """Perform an asynchronous HTTP health check on a target URL.

    Parameters
    ----------
    url:
        The target HTTP(S) URL of the deployed application.
    timeout_seconds:
        Maximum duration to wait for response before timing out.
    method:
        HTTP method (defaults to "GET").
    headers:
        Optional custom HTTP headers.
    client:
        Optional existing httpx.AsyncClient instance (useful for testing or connection pooling).

    Returns
    -------
    HealthCheckResult
        Structured outcome containing health status, HTTP status code, latency, and errors.
    """
    if not url or not url.strip():
        return HealthCheckResult(
            url=url or "",
            is_healthy=False,
            status_code=None,
            latency_ms=0,
            error_message="Target URL cannot be empty",
        )

    target_url = url.strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = f"https://{target_url}"

    start_time = time.monotonic()
    req_headers = {"User-Agent": "BharatBuilds-HealthProbe/1.0", **(headers or {})}

    async def _execute_request(http_client: httpx.AsyncClient) -> HealthCheckResult:
        try:
            response = await http_client.request(
                method=method.upper(),
                url=target_url,
                headers=req_headers,
                timeout=timeout_seconds,
            )
            latency_ms = int((time.monotonic() - start_time) * 1000)
            status_code = response.status_code

            # 2xx is considered healthy
            if 200 <= status_code < 300:
                logger.debug("Health probe SUCCESS: url=%s status=%d latency=%dms", target_url, status_code, latency_ms)
                return HealthCheckResult(
                    url=target_url,
                    is_healthy=True,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    error_message=None,
                )

            # 4xx is client error
            if 400 <= status_code < 500:
                err = f"HTTP {status_code} Client Error"
                logger.warning("Health probe CLIENT ERROR: url=%s status=%d", target_url, status_code)
                return HealthCheckResult(
                    url=target_url,
                    is_healthy=False,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    error_message=err,
                )

            # 5xx is server error
            err_body = response.text[:200].strip() if response.text else "No response body"
            err = f"HTTP {status_code} Server Error: {err_body}"
            logger.warning("Health probe SERVER ERROR: url=%s status=%d err=%s", target_url, status_code, err)
            return HealthCheckResult(
                url=target_url,
                is_healthy=False,
                status_code=status_code,
                latency_ms=latency_ms,
                error_message=err,
            )

        except httpx.TimeoutException:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            err = f"Request timed out after {timeout_seconds:.1f}s"
            logger.warning("Health probe TIMEOUT: url=%s (%s)", target_url, err)
            return HealthCheckResult(
                url=target_url,
                is_healthy=False,
                status_code=None,
                latency_ms=latency_ms,
                error_message=err,
            )

        except (httpx.ConnectError, httpx.NetworkError) as exc:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            err = f"Connection failed: {exc}"
            logger.warning("Health probe CONNECTION FAILED: url=%s (%s)", target_url, err)
            return HealthCheckResult(
                url=target_url,
                is_healthy=False,
                status_code=None,
                latency_ms=latency_ms,
                error_message=err,
            )

        except Exception as exc:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            err = f"Health probe exception: {exc}"
            logger.error("Health probe UNEXPECTED ERROR: url=%s (%s)", target_url, err)
            return HealthCheckResult(
                url=target_url,
                is_healthy=False,
                status_code=None,
                latency_ms=latency_ms,
                error_message=err,
            )

    if client is not None:
        return await _execute_request(client)

    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as new_client:
        return await _execute_request(new_client)

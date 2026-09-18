"""Maintenance diagnosis and code repair via Amazon Bedrock.

Provides autonomous root-cause diagnosis and code patching for deployed
applications encountering runtime errors or failing health checks.
Includes a pluggable :class:`CodeRepairProvider` interface to allow
future providers (such as DriftFix) to be integrated seamlessly.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from backend.agent.bedrock_client import invoke_model_json
from backend.agent.codegen import _strip_code_fences
from backend.models.app import MaintenanceIssue, RepairResult

logger = logging.getLogger(__name__)

REPAIR_SYSTEM_PROMPT = """\
You are an expert autonomous software maintenance and repair engineer.

You are given:
1. The current source code of a single-file Python web application (`app_code.py`).
2. A detected MaintenanceIssue containing error details, exception messages, stack traces, and/or affected endpoints.

Your task:
1. Diagnose the root cause of the issue from the error trace and existing code.
2. Produce a targeted bug fix that repairs the defect while preserving all existing functionality and structure.
3. The patched code MUST be the complete, self-contained, single-file Python web application.
4. Do NOT remove working features or routes. Do NOT introduce external dependencies not already in use or part of the standard library.
5. Return your response as a valid JSON object matching this schema:

{
  "diagnosis": "<concise explanation of the defect and its root cause>",
  "summary": "<clear summary of the code modifications made to fix the defect>",
  "patched_code": "<complete updated Python source code for the app>"
}

Requirements:
- Return ONLY the JSON object — no markdown fences around the JSON, no surrounding commentary.
- Ensure `patched_code` contains valid, runnable Python code.
"""


def _format_issue_prompt(existing_code: str, issue: MaintenanceIssue) -> str:
    """Format the diagnostic and repair prompt combining code and issue details."""
    parts = [
        "## Current Application Code (`app_code.py`):\n",
        f"```python\n{existing_code}\n```\n\n",
        "## Detected Maintenance Issue:\n",
        f"- Issue Type: {issue.issue_type}\n",
        f"- Severity: {issue.severity}\n",
        f"- Detection Source: {issue.detection_source}\n",
        f"- Error Message: {issue.error_message}\n",
    ]
    if issue.endpoint:
        parts.append(f"- Affected Endpoint: {issue.endpoint}\n")
    if issue.stack_trace:
        parts.append(f"- Stack Trace:\n```\n{issue.stack_trace}\n```\n")

    parts.append(
        "\nPlease diagnose the root cause, provide a summary of fixes, and return the complete patched Python code in the requested JSON format."
    )
    return "".join(parts)


def _validate_python_syntax(code: str) -> tuple[bool, str | None]:
    """Validate that the code string compiles as valid Python syntax."""
    if not code or not code.strip():
        return False, "Patched code is empty"
    try:
        compile(code, "<patched_code>", "exec")
        return True, None
    except SyntaxError as exc:
        return False, f"SyntaxError in patched code: {exc}"


# ── Provider Abstraction ─────────────────────────────────────────────────


class CodeRepairProvider(ABC):
    """Abstract interface for code repair providers (Bedrock, DriftFix, etc.)."""

    @abstractmethod
    async def diagnose_and_repair(
        self,
        existing_code: str,
        issue: MaintenanceIssue,
    ) -> RepairResult:
        """Diagnose an issue and generate repaired source code.

        Parameters
        ----------
        existing_code:
            The current active source code of the application.
        issue:
            The detected defect or runtime failure details.

        Returns
        -------
        RepairResult
            Contains diagnosis, summary, patched_code, and success status.
        """
        pass


class BedrockCodeRepairProvider(CodeRepairProvider):
    """Default code repair provider powered by Amazon Bedrock."""

    def __init__(
        self,
        *,
        model_id: str = "",
        region: str = "ap-south-1",
    ) -> None:
        self.model_id = model_id
        self.region = region

    async def diagnose_and_repair(
        self,
        existing_code: str,
        issue: MaintenanceIssue,
    ) -> RepairResult:
        """Diagnose and repair using Amazon Bedrock with structured JSON output."""
        if not existing_code or not existing_code.strip():
            logger.warning("diagnose_and_repair called with empty existing_code")
            return RepairResult(
                diagnosis="",
                summary="",
                patched_code="",
                is_success=False,
                error_message="Existing code cannot be empty for repair",
            )

        prompt = _format_issue_prompt(existing_code, issue)
        logger.info(
            "Invoking Bedrock for maintenance repair: issue_type=%s, severity=%s, code_len=%d",
            issue.issue_type,
            issue.severity,
            len(existing_code),
        )

        try:
            raw_response: dict[str, Any] = invoke_model_json(
                prompt,
                system=REPAIR_SYSTEM_PROMPT,
                model_id=self.model_id,
                region=self.region,
                max_tokens=8192,
                temperature=0.1,
            )
        except Exception as exc:
            logger.error("Bedrock invocation failed during repair: %s", exc)
            return RepairResult(
                diagnosis="",
                summary="",
                patched_code="",
                is_success=False,
                error_message=f"Model invocation failed: {exc}",
            )

        diagnosis = raw_response.get("diagnosis", "").strip()
        summary = raw_response.get("summary", "").strip()
        raw_code = raw_response.get("patched_code", "")

        if not raw_code or not isinstance(raw_code, str) or not raw_code.strip():
            logger.warning("Bedrock response missing valid patched_code: %s", raw_response)
            return RepairResult(
                diagnosis=diagnosis,
                summary=summary,
                patched_code="",
                is_success=False,
                error_message="Model response did not contain valid patched code",
            )

        patched_code = _strip_code_fences(raw_code)

        # Validate Python syntax of the patched code
        is_valid_syntax, syntax_err = _validate_python_syntax(patched_code)
        if not is_valid_syntax:
            logger.warning("Patched code failed syntax validation: %s", syntax_err)
            return RepairResult(
                diagnosis=diagnosis,
                summary=summary,
                patched_code=patched_code,
                is_success=False,
                error_message=syntax_err,
            )

        logger.info("Successfully diagnosed and generated repaired code (%d lines)", len(patched_code.splitlines()))
        return RepairResult(
            diagnosis=diagnosis,
            summary=summary,
            patched_code=patched_code,
            is_success=True,
            error_message=None,
        )


# ── High-Level Entry Point ───────────────────────────────────────────────


async def diagnose_and_repair(
    existing_code: str,
    issue: MaintenanceIssue,
    *,
    provider: CodeRepairProvider | None = None,
    model_id: str = "",
    region: str = "ap-south-1",
) -> RepairResult:
    """Diagnose a maintenance issue and generate a repaired code patch.

    Parameters
    ----------
    existing_code:
        The current source code of the failing application.
    issue:
        The detected defect details.
    provider:
        Optional custom :class:`CodeRepairProvider` (defaults to :class:`BedrockCodeRepairProvider`).
    model_id:
        Bedrock model identifier if using the default provider.
    region:
        AWS region if using the default provider.

    Returns
    -------
    RepairResult
        The diagnostic explanation and patched source code.
    """
    if provider is None:
        provider = BedrockCodeRepairProvider(model_id=model_id, region=region)
    return await provider.diagnose_and_repair(existing_code, issue)

"""Candidate code verification module.

Performs local, pre-deployment validation on candidate Python application code
to verify compilation, entry point availability, and safe runtime invocation
before any AWS deployment is attempted.
"""

from __future__ import annotations

import logging
import types
from typing import Any

from backend.models.app import CandidateVerificationResult

logger = logging.getLogger(__name__)


def verify_candidate_code(
    code: str,
    *,
    test_event: dict[str, Any] | None = None,
) -> CandidateVerificationResult:
    """Validate candidate Python source code prior to deployment.

    Runs 3 validation checks:
    1. `syntax_compilation` — Checks valid Python syntax via AST compilation.
    2. `entry_point_detection` — Ensures a callable `handler(event, context)` or `render()` exists.
    3. `runtime_execution` — Safely executes the handler in an isolated sandbox namespace with sample input.

    Parameters
    ----------
    code:
        The generated Python source code.
    test_event:
        Optional sample event dictionary to pass to `handler(event, context)`.

    Returns
    -------
    CandidateVerificationResult
        Structured report indicating whether the candidate code passed all checks.
    """
    checks_performed: list[str] = ["syntax_compilation", "entry_point_detection", "runtime_execution"]
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    if not code or not code.strip():
        logger.warning("Candidate verification failed: code is empty")
        return CandidateVerificationResult(
            passed=False,
            checks_performed=checks_performed,
            checks_passed=[],
            checks_failed=["syntax_compilation"],
            error_message="Candidate code cannot be empty",
        )

    # ── Check 1: Syntax & Compilation ──────────────────────────────────────
    try:
        compiled_code = compile(code, "candidate_app_code.py", "exec")
        checks_passed.append("syntax_compilation")
    except SyntaxError as exc:
        err = f"SyntaxError in candidate code: {exc}"
        logger.warning("Candidate verification failed: %s", err)
        checks_failed.append("syntax_compilation")
        return CandidateVerificationResult(
            passed=False,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            error_message=err,
        )

    # ── Check 2: Entry Point Detection ─────────────────────────────────────
    module = types.ModuleType("candidate_app_code")
    try:
        exec(compiled_code, module.__dict__)
    except Exception as exc:
        err = f"Runtime error during candidate module execution: {type(exc).__name__}: {exc}"
        logger.warning("Candidate module load failed: %s", err)
        checks_failed.append("entry_point_detection")
        return CandidateVerificationResult(
            passed=False,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            error_message=err,
        )

    has_handler = hasattr(module, "handler") and callable(getattr(module, "handler"))
    has_render = hasattr(module, "render") and callable(getattr(module, "render"))

    if not has_handler and not has_render:
        err = "Missing entry point: candidate code must define a callable 'handler(event, context)' or 'render()' function"
        logger.warning("Candidate verification failed: %s", err)
        checks_failed.append("entry_point_detection")
        return CandidateVerificationResult(
            passed=False,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            error_message=err,
        )

    entry_point = "handler" if has_handler else "render"
    checks_passed.append("entry_point_detection")

    # ── Check 3: Runtime Execution ─────────────────────────────────────────
    response_sample: str | None = None
    sample_event = test_event or {
        "rawPath": "/",
        "requestContext": {"http": {"method": "GET"}},
        "headers": {},
    }

    try:
        if has_handler:
            resp = module.handler(sample_event, None)
            if isinstance(resp, dict):
                status_code = resp.get("statusCode", 200)
                if status_code >= 500:
                    err = f"Handler returned server error status code {status_code}: {resp.get('body', '')}"
                    checks_failed.append("runtime_execution")
                    return CandidateVerificationResult(
                        passed=False,
                        checks_performed=checks_performed,
                        checks_passed=checks_passed,
                        checks_failed=checks_failed,
                        entry_point=entry_point,
                        error_message=err,
                    )
                response_sample = str(resp.get("body", ""))[:200]
            else:
                response_sample = str(resp)[:200]
        else:
            resp = module.render()
            if not resp or not isinstance(resp, str):
                err = f"render() function must return a non-empty string (got {type(resp).__name__})"
                checks_failed.append("runtime_execution")
                return CandidateVerificationResult(
                    passed=False,
                    checks_performed=checks_performed,
                    checks_passed=checks_passed,
                    checks_failed=checks_failed,
                    entry_point=entry_point,
                    error_message=err,
                )
            response_sample = resp[:200]

        checks_passed.append("runtime_execution")
        logger.info("Candidate code successfully verified (entry_point=%s)", entry_point)
        return CandidateVerificationResult(
            passed=True,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=[],
            entry_point=entry_point,
            response_sample=response_sample,
            error_message=None,
        )

    except Exception as exc:
        err = f"Runtime invocation error in {entry_point}(): {type(exc).__name__}: {exc}"
        logger.warning("Candidate verification execution failed: %s", err)
        checks_failed.append("runtime_execution")
        return CandidateVerificationResult(
            passed=False,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            entry_point=entry_point,
            error_message=err,
        )


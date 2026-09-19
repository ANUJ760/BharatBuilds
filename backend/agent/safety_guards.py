"""Safety guards and policy validation for autonomous maintenance.

Guards include:
1. Concurrency control: prevents concurrent maintenance executions for the same app_id.
2. Input sanitization: strips prompt injection vectors and caps length of untrusted logs/traces.
3. Code safety inspection: blocks attempts to access AWS credentials, invoke raw OS shells, or modify infrastructure/auth.
"""

from __future__ import annotations

import ast
import asyncio
import logging
import re
from typing import ClassVar

from backend.models.app import MaintenanceIssue

logger = logging.getLogger(__name__)

# Maximum length for untrusted text fields to prevent prompt-flooding attacks
MAX_UNTRUSTED_TEXT_LENGTH = 2000

# Prompt injection signature patterns to neutralize
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|other)?\s*(instructions?|prompts?|rules?|commands?)", re.IGNORECASE),
    re.compile(r"system\s*:", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
    re.compile(r"```\s*system", re.IGNORECASE),
]

# Forbidden modules and attributes that small apps should not use
FORBIDDEN_MODULES = {
    "subprocess",
    "pty",
    "ctypes",
    "socketserver",
    "multiprocessing",
}

FORBIDDEN_CALLS = {
    "os.system",
    "os.popen",
    "os.spawn",
    "os.exec",
    "eval",
    "exec",
    "__import__",
}


# ── Concurrency Lock ───────────────────────────────────────────────────────


class AppConcurrencyLock:
    """In-memory concurrency lock manager per app_id."""

    _active_apps: ClassVar[set[str]] = set()
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def acquire(cls, app_id: str) -> bool:
        """Attempt to acquire a maintenance lock for app_id.

        Returns True if acquired, False if already in progress.
        """
        async with cls._lock:
            if app_id in cls._active_apps:
                logger.warning("Concurrency lock rejected: app %s is already in maintenance", app_id)
                return False
            cls._active_apps.add(app_id)
            logger.debug("Concurrency lock acquired for app %s", app_id)
            return True

    @classmethod
    async def release(cls, app_id: str) -> None:
        """Release the maintenance lock for app_id."""
        async with cls._lock:
            cls._active_apps.discard(app_id)
            logger.debug("Concurrency lock released for app %s", app_id)

    @classmethod
    def is_locked(cls, app_id: str) -> bool:
        """Check if app_id is currently locked."""
        return app_id in cls._active_apps


# ── Input Sanitization ────────────────────────────────────────────────────


def sanitize_text(text: str | None, max_len: int = MAX_UNTRUSTED_TEXT_LENGTH) -> str:
    """Sanitize untrusted input strings from logs or user submissions.

    - Truncates excessively long inputs.
    - Neutralizes known prompt injection phrases.
    """
    if not text:
        return ""

    sanitized = text.strip()
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len] + "... [truncated]"

    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[filtered_instruction]", sanitized)

    return sanitized


def sanitize_issue(issue: MaintenanceIssue) -> MaintenanceIssue:
    """Return a copy of MaintenanceIssue with all text fields sanitized."""
    return MaintenanceIssue(
        issue_id=issue.issue_id,
        issue_type=sanitize_text(issue.issue_type, max_len=100),
        severity=issue.severity,
        error_message=sanitize_text(issue.error_message, max_len=MAX_UNTRUSTED_TEXT_LENGTH),
        stack_trace=sanitize_text(issue.stack_trace, max_len=MAX_UNTRUSTED_TEXT_LENGTH) if issue.stack_trace else None,
        endpoint=sanitize_text(issue.endpoint, max_len=200) if issue.endpoint else None,
        detection_source=sanitize_text(issue.detection_source, max_len=100),
        detected_at=issue.detected_at,
    )


# ── Code Safety Static Analysis ──────────────────────────────────────────


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor that detects forbidden module imports and dangerous calls."""

    def __init__(self) -> None:
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in FORBIDDEN_MODULES:
                self.violations.append(f"Forbidden module import: '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module in FORBIDDEN_MODULES:
            self.violations.append(f"Forbidden module import: '{node.module}'")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Detect calls like os.system(...)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            call_name = f"{node.func.value.id}.{node.func.attr}"
            for forbidden in FORBIDDEN_CALLS:
                if call_name.startswith(forbidden):
                    self.violations.append(f"Forbidden dangerous call: '{call_name}()'")
        elif isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.violations.append(f"Forbidden dangerous call: '{node.func.id}()'")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        # Detect attempts to access AWS secret keys from env
        if isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name):
            if node.value.value.id == "os" and node.value.attr == "environ":
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    key = node.slice.value.upper()
                    if "AWS_SECRET" in key or "AWS_ACCESS_KEY" in key or "AWS_SESSION" in key or "COGNITO" in key:
                        self.violations.append(f"Forbidden environment secret access: 'os.environ[\"{node.slice.value}\"]'")
        self.generic_visit(node)


def check_code_safety(code: str) -> tuple[bool, str | None]:
    """Inspect candidate Python source code for security violations.

    Returns
    -------
    tuple[bool, str | None]
        (is_safe, violation_reason)
    """
    if not code or not code.strip():
        return False, "Code is empty"

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc}"

    visitor = SecurityASTVisitor()
    visitor.visit(tree)

    if visitor.violations:
        reason = "; ".join(visitor.violations)
        logger.warning("Code safety violation detected: %s", reason)
        return False, f"Security violation: {reason}"

    return True, None

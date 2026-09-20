"""Code generation via Amazon Bedrock.

Takes a resolved prompt (with clarify answers merged) and produces
app source code as a string. The planner calls this as one step in
its ReAct loop.
"""

from __future__ import annotations

import logging

from backend.agent.gemini_client import invoke_model

logger = logging.getLogger(__name__)

CODEGEN_SYSTEM_PROMPT = """\
You are a code generator for a small-software platform. Given a user's
app description (and any clarification answers), generate a complete,
working, single-file Python web application.

Requirements:
1. Use Python with a simple HTTP server (Flask-style or stdlib).
2. The app must be self-contained in a single file called main.py.
3. Include inline HTML templates — no external files needed.
4. The app should be immediately runnable with `python main.py`.
5. Listen on port 8080 by default (via PORT env var).
6. Return ONLY the Python source code — no markdown fences, no explanation.
"""


async def generate_code(
    prompt: str,
    clarifications: dict | None = None,
    *,
    model_id: str = "",
    region: str = "ap-south-1",
) -> str:
    """Generate app source code from a resolved prompt.

    Parameters
    ----------
    prompt:
        The user's original app request.
    clarifications:
        Optional dict of clarification answers merged into the context.
    model_id:
        Bedrock model identifier.
    region:
        AWS region.

    Returns
    -------
    str
        The generated Python source code.
    """
    full_prompt = prompt
    if clarifications:
        clarify_text = "\n".join(
            f"- {k}: {v}" for k, v in clarifications.items()
        )
        full_prompt = (
            f"{prompt}\n\nClarification answers:\n{clarify_text}"
        )

    logger.info("Generating code for prompt (len=%d)", len(full_prompt))

    code = invoke_model(
        full_prompt,
        system=CODEGEN_SYSTEM_PROMPT,
        model_id=model_id,
        region=region,
        max_tokens=8192,
        temperature=0.2,
    )

    # Strip markdown fences if the model wrapped the code
    code = _strip_code_fences(code)

    return code


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences from generated code."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```python or ```)
        lines = lines[1:]
        # Remove last line if it's a closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()

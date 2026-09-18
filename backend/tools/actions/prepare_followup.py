"""General action tools."""
from typing import Any, Dict, List


async def prepare_followup(recipients: List[str], subject: str, body: str) -> Dict[str, Any]:
    """Prepare a follow-up action (like sending an email) requiring approval.

    This tool intentionally does NOT send the email, it prepares the payload
    that will be presented to a human for approval.
    """

    return {
        "action_type": "send_email",
        "payload": {
            "to": recipients,
            "subject": subject,
            "body": body
        },
        "status": "prepared",
        "requires_human_approval": True
    }

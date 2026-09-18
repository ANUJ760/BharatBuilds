"""Verification workflow tools."""
from typing import Any, Dict, List

from backend.tools.sheets.get_rows import search_rows
from backend.tools.drive.list_files import list_files


async def check_required_documents(employee_id: str, required_types: List[str]) -> Dict[str, Any]:
    """Check if an employee has all required documents."""

    # In a real workflow, the mapping between employee and drive folder
    # would come from a connection or database
    folder_id = f"emp_{employee_id}_folder"

    files = await list_files(folder_id=folder_id)
    file_names = [f["name"].lower() for f in files]

    results = {}
    missing = []

    for req_type in required_types:
        # Simple heuristic for demo purposes
        found = any(req_type.lower() in fname for fname in file_names)
        results[req_type] = found
        if not found:
            missing.append(req_type)

    is_verified = len(missing) == 0

    return {
        "employee_id": employee_id,
        "document_status": results,
        "missing_documents": missing,
        "status": "VERIFIED" if is_verified else "PENDING_DOCUMENTS",
        "is_verified": is_verified
    }


async def generate_verification_report(employee_ids: List[str]) -> Dict[str, Any]:
    """Generate a combined verification report."""
    reports = []
    required_docs = ["photo", "id_proof", "offer_letter"]

    for emp_id in employee_ids:
        report = await check_required_documents(emp_id, required_docs)
        reports.append(report)

    return {
        "total_checked": len(reports),
        "verified_count": sum(1 for r in reports if r["is_verified"]),
        "reports": reports
    }

"""Google Sheets tools."""
from typing import Any, Dict, List


async def get_rows(spreadsheet_id: str, range_name: str) -> List[Dict[str, Any]]:
    """Get rows from a Google Sheet. MOCK implementation."""
    # In production, this would use GoogleSheetsConnector
    if spreadsheet_id == "demo_employees":
        return [
            {
                "employee_id": "EMP001",
                "name": "Rahul Sharma",
                "email": "rahul.sharma@example.com",
                "joining_date": "2026-09-18",
                "department": "Engineering"
            },
            {
                "employee_id": "EMP002",
                "name": "Priya Patel",
                "email": "priya.patel@example.com",
                "joining_date": "2026-09-20",
                "department": "Design"
            }
        ]
    return []


async def search_rows(spreadsheet_id: str, range_name: str, query_column: str, query_value: str) -> List[Dict[str, Any]]:
    """Search for specific rows in a Google Sheet."""
    rows = await get_rows(spreadsheet_id, range_name)
    return [r for r in rows if str(r.get(query_column, "")).lower() == str(query_value).lower()]

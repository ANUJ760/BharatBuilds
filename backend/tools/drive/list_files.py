"""Google Drive tools."""
from typing import Any, Dict, List


async def list_files(folder_id: str, query: str = "") -> List[Dict[str, Any]]:
    """List files in a Google Drive folder. MOCK implementation."""
    # In production, this would use GoogleDriveConnector
    if folder_id == "emp_EMP001_folder":
        return [
            {"id": "doc1", "name": "Profile_Photo.jpg", "mimeType": "image/jpeg"},
            {"id": "doc2", "name": "ID_Proof_Aadhar.pdf", "mimeType": "application/pdf"},
            {"id": "doc3", "name": "Offer_Letter_Signed.pdf", "mimeType": "application/pdf"},
        ]
    elif folder_id == "emp_EMP002_folder":
        return [
            {"id": "doc4", "name": "Profile_Photo.jpg", "mimeType": "image/jpeg"},
            # Missing ID proof and offer letter for EMP002
        ]

    return []

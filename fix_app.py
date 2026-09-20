import sys
import boto3
from datetime import datetime, timezone
from backend.config import get_settings
from dotenv import load_dotenv
load_dotenv()
import uuid

app_id = "abe59589-6452-47af-a6b3-ff5e9d296970"
settings = get_settings()
dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
table = dynamodb.Table(settings.dynamodb_table_name)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Attendance Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow">
        <h1 class="text-2xl font-bold mb-4">Student Attendance Tracker</h1>
        <p class="text-green-600 mb-4">System successfully recovered! The AI initially stopped halfway while building your application, leaving a blank page. You can now use the Update App box on the left to ask the AI to continue building or add more features.</p>
        <div class="border rounded p-4">
            <h2 class="text-lg font-semibold">Today's Attendance</h2>
            <ul class="mt-4 space-y-2">
                <li class="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span>John Doe</span>
                    <button class="px-3 py-1 bg-blue-500 text-white rounded">Mark Present</button>
                </li>
                <li class="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span>Jane Smith</span>
                    <button class="px-3 py-1 bg-blue-500 text-white rounded">Mark Present</button>
                </li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

step_id = str(uuid.uuid4())

item = {
    "app_id": app_id,
    "step_id": step_id,
    "step_type": "codegen",
    "code_snapshot": html,
    "reasoning": "Manual recovery fix",
    "timestamp": datetime.now(timezone.utc).isoformat(),
}

table.put_item(Item=item)
print("Fixed app deployed to DynamoDB!")

#!/usr/bin/env python3
"""Quick test for the fixed bulk analyze functionality"""
import requests
import json

test_data = {
    "items": [
        {
            "Summary": "Video Upload Limits for New Users",
            "Issue Type": "New Feature", 
            "Priority": "High",
            "Status": "In Progress",
            "Issue key": "TT-001",
            "Due date": "2024-12-31"
        }
    ]
}

print("Testing bulk-csv-analysis-json endpoint...")
try:
    response = requests.post(
        "http://localhost:8001/api/bulk-csv-analysis-json",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Task ID: {data.get('task_id')}")
        print(f"Message: {data.get('message')}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Failed: {e}")

#!/usr/bin/env python3
"""
Test Congress API only
"""

import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

async def test_congress_direct():
    """Test Congress API directly"""
    api_key = os.getenv("CONGRESS_API_KEY")
    if not api_key:
        print("ERROR: No Congress API key found")
        return False
    
    print(f"Testing with API key: {api_key[:10]}...")
    
    # Test direct HTTP request
    url = "https://api.congress.gov/v3/bill/118"
    params = {
        "query": "social media",
        "limit": 5,
        "format": "json"
    }
    headers = {
        "X-API-Key": api_key
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                bills = data.get("bills", [])
                print(f"SUCCESS: Found {len(bills)} bills")
                
                if bills:
                    first_bill = bills[0]
                    print(f"Sample bill: {first_bill.get('title', 'Unknown')}")
                    return True
                else:
                    print("No bills in response")
                    return False
            else:
                print(f"API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Request failed: {e}")
        return False

async def main():
    print("Testing Congress.gov API directly...")
    success = await test_congress_direct()
    
    if success:
        print("\nSUCCESS: Government API is working!")
        print("You now have verified access to official legal data for grading.")
    else:
        print("\nFAILED: API needs debugging")

if __name__ == "__main__":
    asyncio.run(main())
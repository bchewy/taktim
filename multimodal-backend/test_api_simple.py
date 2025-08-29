#!/usr/bin/env python3
"""
Simple test for Government Legal APIs
Tests API connectivity and accuracy for grading requirements
"""

import asyncio
import json
import os
from datetime import datetime
from src.utils.legal_apis import LegalResearchAggregator, GovInfoAPI, CongressAPI

async def test_congress_api():
    """Test Congress.gov API with your key"""
    print("\n[TEST] Congress.gov API")
    
    congress = CongressAPI()
    try:
        # Check if API key is loaded
        if not congress.api_key:
            print("ERROR: Congress API key not found in environment")
            return False
        
        print(f"API Key loaded: {congress.api_key[:10]}...")
        
        # Test search for social media bills
        result = await congress.search_bills("social media", congress=118)
        
        if "bills" in result and result["bills"]:
            print(f"SUCCESS: Found {len(result['bills'])} bills")
            
            # Show first bill
            first_bill = result["bills"][0]
            print(f"  Sample: {first_bill.get('title', 'Unknown')[:80]}...")
            return True
        else:
            print("WARNING: No bills found")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await congress.close()

async def test_govinfo_api():
    """Test GovInfo.gov API"""
    print("\n[TEST] GovInfo.gov API")
    
    govinfo = GovInfoAPI()
    try:
        # Test search
        result = await govinfo.search_regulations("children privacy")
        
        if "results" in result and result["results"]:
            print(f"SUCCESS: Found {len(result['results'])} regulations")
            
            # Show first regulation
            first_reg = result["results"][0]
            print(f"  Sample: {first_reg.get('title', 'Unknown')[:80]}...")
            return True
        else:
            print("WARNING: No regulations found")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await govinfo.close()

async def test_full_research():
    """Test full legal research"""
    print("\n[TEST] Full Legal Research")
    
    aggregator = LegalResearchAggregator()
    try:
        result = await aggregator.research_topic("social media children")
        
        fed_count = len(result.get("federal_regulations", []))
        bill_count = len(result.get("congressional_bills", []))
        state_count = len(result.get("state_laws", {}))
        
        print(f"SUCCESS: Research completed")
        print(f"  Federal regs: {fed_count}")
        print(f"  Congressional bills: {bill_count}")  
        print(f"  State laws: {state_count}")
        
        total = fed_count + bill_count + state_count
        return total > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await aggregator.close()

async def main():
    """Run all tests"""
    print("="*50)
    print("GOVERNMENT LEGAL API TESTING")
    print("For grading accuracy requirements")
    print("="*50)
    
    # Run tests
    congress_ok = await test_congress_api()
    govinfo_ok = await test_govinfo_api()
    research_ok = await test_full_research()
    
    # Calculate score
    total_tests = 3
    passed = sum([congress_ok, govinfo_ok, research_ok])
    accuracy = (passed / total_tests) * 100
    
    print("\n" + "="*50)
    print("TEST RESULTS")
    print("="*50)
    print(f"Congress API: {'PASS' if congress_ok else 'FAIL'}")
    print(f"GovInfo API: {'PASS' if govinfo_ok else 'FAIL'}")
    print(f"Full Research: {'PASS' if research_ok else 'FAIL'}")
    print(f"\nAccuracy Score: {accuracy:.1f}% ({passed}/{total_tests})")
    
    if accuracy >= 66.7:
        print("STATUS: Ready for grading!")
    else:
        print("STATUS: Needs debugging")
    
    # Save results
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "congress_api": congress_ok,
        "govinfo_api": govinfo_ok,
        "full_research": research_ok,
        "accuracy_percentage": accuracy,
        "grading_ready": accuracy >= 66.7
    }
    
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: api_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
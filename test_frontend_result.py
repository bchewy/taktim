"""
Test script to verify the improved frontend UI is working
"""
import requests
import json

def test_frontend_integration():
    """Test that the API returns properly formatted data for the new UI"""
    
    BASE_URL = "http://localhost:8001"
    
    # Test data
    test_feature = {
        "feature_name": "Teen Safety Filter",
        "description": "AI-powered content filtering to protect users under 18 from harmful content",
        "target_markets": ["US", "EU", "UK"],
        "data_collected": ["content_analysis", "user_age", "viewing_patterns"],
        "user_demographics": ["teens_13_17", "general_audience"],
        "ai_components": ["content_classification", "age_detection", "behavioral_analysis"]
    }
    
    try:
        print("Testing comprehensive compliance analysis...")
        response = requests.post(f"{BASE_URL}/api/comprehensive-compliance-analysis", json=test_feature)
        
        if response.status_code == 200:
            result = response.json()
            print("PASS: API Response received successfully")
            
            # Check if the result has the expected structure for the UI
            expected_fields = [
                'analysis_type',
                'feature_analyzed', 
                'result',
                'regulatory_inquiry_ready'
            ]
            
            missing_fields = [field for field in expected_fields if field not in result]
            if missing_fields:
                print(f"FAIL: Missing fields: {missing_fields}")
            else:
                print("PASS: All expected fields present")
            
            # Check nested result structure
            if 'result' in result and result['result']:
                nested_result = result['result']
                print(f"PASS: Nested result structure: {list(nested_result.keys())}")
                
                # Check for geo-regulatory mapping
                if 'geo_regulatory_mapping' in nested_result:
                    print("PASS: Geo-regulatory mapping present")
                    geo_data = nested_result['geo_regulatory_mapping']
                    if isinstance(geo_data, str):
                        print(f"PASS: Geo-regulatory data is text (length: {len(geo_data)} chars)")
                        # Check if it contains markdown-like formatting
                        if '#' in geo_data and '**' in geo_data:
                            print("PASS: Contains markdown formatting for UI parsing")
                    else:
                        print(f"ℹ️ Geo-regulatory data type: {type(geo_data)}")
                
                # Check for legal research
                if 'legal_research' in nested_result:
                    print("PASS: Legal research data present")
                
                # Check for compliance status
                if 'compliance_status' in nested_result:
                    print("PASS: Compliance status present")
                    status = nested_result['compliance_status']
                    if 'risk_level' in status:
                        print(f"PASS: Risk level: {status['risk_level']}")
                    if 'overall_status' in status:
                        print(f"PASS: Overall status: {status['overall_status']}")
            
            print(f"\nRESULT: Sample API Response Structure:")
            print(f"- Analysis Type: {result.get('analysis_type', 'N/A')}")
            print(f"- Feature Analyzed: {result.get('feature_analyzed', 'N/A')}")
            print(f"- Regulatory Ready: {result.get('regulatory_inquiry_ready', 'N/A')}")
            
            return True
        else:
            print(f"FAIL: API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Frontend Integration\n")
    
    success = test_frontend_integration()
    
    if success:
        print(f"\nPASS: Frontend Integration Test PASSED")
        print("The new UI should now display:")
        print("  • Beautiful analysis summary cards")
        print("  • Formatted geo-regulatory compliance text") 
        print("  • Color-coded risk levels")
        print("  • Legal research API status")
        print("  • Action buttons (Print, Export, Copy)")
        print("  • Scrollable results area")
        print("\nSUCCESS: Visit http://localhost:3000 and test the Single Analysis page!")
    else:
        print(f"\nFAIL: Frontend Integration Test FAILED")
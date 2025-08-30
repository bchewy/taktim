"""
Test script to verify the backend API works with the simplified payload
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"FAIL: Health test failed: {e}")
        return False

def test_comprehensive_compliance_simplified():
    """Test comprehensive compliance analysis with simplified payload (no removed fields)"""
    print("\nTesting comprehensive compliance analysis with simplified payload...")
    
    # This is our new simplified payload without the removed fields
    feature_data = {
        "feature_name": "AI Video Recommendation Engine",
        "description": "Personalized video feed using ML to recommend content based on viewing history and user preferences. Features AI-powered recommendation algorithms for teens and adults.",
        "target_markets": ["US", "EU"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/comprehensive-compliance-analysis", json=feature_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: API accepts simplified payload")
            print(f"Analysis type: {result.get('analysis_type', 'Unknown')}")
            print(f"Feature analyzed: {result.get('feature_analyzed', 'Unknown')}")
            return True
        elif response.status_code == 422:
            # This would indicate a validation error with our simplified payload
            print(f"FAIL: Validation error - our payload structure is wrong")
            print(f"Error: {response.text}")
            return False
        elif "AuthenticationError" in response.text or "API key" in response.text:
            # This is expected - the API accepts our payload but fails on OpenAI key
            print(f"SUCCESS: API accepts simplified payload (fails on OpenAI key as expected)")
            return True
        else:
            print(f"FAIL: Unexpected error: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Request failed: {e}")
        return False

def test_geo_regulatory_mapping_simplified():
    """Test geo-regulatory mapping with simplified payload"""
    print("\nTesting geo-regulatory mapping with simplified payload...")
    
    feature_data = {
        "feature_name": "AI Content Discovery Feed",
        "description": "AI-powered content discovery system that uses machine learning to personalize content recommendations for users including teens",
        "target_markets": ["US", "EU", "Canada"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/geo-regulatory-mapping", json=feature_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Geo-regulatory endpoint accepts simplified payload")
            return True
        elif response.status_code == 422:
            print(f"FAIL: Validation error - our payload structure is wrong")
            print(f"Error: {response.text}")
            return False
        elif "AuthenticationError" in response.text or "API key" in response.text:
            print(f"SUCCESS: Geo-regulatory endpoint accepts simplified payload (fails on OpenAI key as expected)")
            return True
        else:
            print(f"FAIL: Unexpected error: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Request failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Backend API with Simplified Payload ===")
    print("Testing our changes to remove data_collected, user_demographics, and ai_components fields\n")
    
    # Test each endpoint
    health_ok = test_health()
    comprehensive_ok = test_comprehensive_compliance_simplified()
    geo_ok = test_geo_regulatory_mapping_simplified()
    
    print("\n=== SUMMARY ===")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Comprehensive compliance (simplified): {'✅ PASS' if comprehensive_ok else '❌ FAIL'}")
    print(f"Geo-regulatory mapping (simplified): {'✅ PASS' if geo_ok else '❌ FAIL'}")
    
    if health_ok and comprehensive_ok and geo_ok:
        print("\n🎉 ALL TESTS PASSED! The backend successfully accepts the simplified payload.")
        print("✅ The removed fields (data_collected, user_demographics, ai_components) are no longer required.")
        print("✅ The frontend can now send just feature_name, description, and target_markets.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

"""
Test the API endpoints directly
"""
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

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

def test_legal_analyze():
    """Test basic legal analysis"""
    print("\nTEST: Testing legal analysis...")
    
    feature_data = {
        "feature_name": "AI Video Recommendation Engine",
        "description": "Personalized video feed using ML to recommend content based on viewing history",
        "target_markets": ["US", "EU"],
        "data_collected": ["user_viewing_history", "like_interactions", "device_info"],
        "user_demographics": ["general_audience", "teens_13_17"],
        "ai_components": ["recommendation_algorithm", "content_filtering"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/legal-analyze", json=feature_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"PASS: Legal analysis successful")
            print(f"Analysis type: {result.get('compliance_status', 'Unknown')}")
            return True
        else:
            print(f"FAIL: Legal analysis failed: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Legal analysis test failed: {e}")
        return False

def test_comprehensive_compliance():
    """Test comprehensive compliance analysis"""
    print("\nTEST: Testing comprehensive compliance analysis...")
    
    feature_data = {
        "feature_name": "AI Video Recommendation Engine",
        "description": "Personalized video feed using ML to recommend content based on viewing history",
        "target_markets": ["US", "EU"],
        "data_collected": ["user_viewing_history", "like_interactions", "device_info"],
        "user_demographics": ["general_audience", "teens_13_17"],
        "ai_components": ["recommendation_algorithm", "content_filtering"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/comprehensive-compliance-analysis", json=feature_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"PASS: Comprehensive analysis successful")
            print(f"Analysis type: {result.get('analysis_type', 'Unknown')}")
            
            # Check if geo-regulatory agent worked
            if 'error' in result.get('result', {}):
                print(f"FAIL: Geo-Regulatory Agent Error: {result['result']['error']}")
                return False
            else:
                print(f"PASS: Geo-Regulatory Agent working properly")
                return True
        else:
            print(f"FAIL: Comprehensive analysis failed: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Comprehensive analysis test failed: {e}")
        return False

def test_geo_regulatory_mapping():
    """Test geo-regulatory mapping directly"""
    print("\nTEST: Testing geo-regulatory mapping...")
    
    feature_data = {
        "feature_name": "AI Video Recommendation Engine",
        "description": "Personalized video feed using ML to recommend content",
        "target_markets": ["US", "EU"],
        "data_collected": ["user_viewing_history", "like_interactions"],
        "user_demographics": ["general_audience", "teens_13_17"],
        "ai_components": ["recommendation_algorithm"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/geo-regulatory-mapping", json=feature_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"PASS: Geo-regulatory mapping successful")
            return True
        else:
            print(f"FAIL: Geo-regulatory mapping failed: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: Geo-regulatory mapping test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API Endpoints\n")
    
    # Test all endpoints
    tests = [
        ("Health Check", test_health),
        ("Legal Analysis", test_legal_analyze),  
        ("Geo-Regulatory Mapping", test_geo_regulatory_mapping),
        ("Comprehensive Compliance", test_comprehensive_compliance),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print(f"\nRESULTS: Test Results:")
    for test_name, passed in results.items():
        status = "PASS: PASS" if passed else "FAIL: FAIL"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nSummary: {total_passed}/{total_tests} tests passed")
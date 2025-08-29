#!/usr/bin/env python3
"""
Test script for the Enhanced Legal Knowledge Agent with Government APIs
Run this to test the legal compliance analysis functionality with real-time legal research
"""

import asyncio
import sys
import requests
import json
from datetime import datetime

# Test TikTok features
TEST_FEATURES = [
    {
        "feature_name": "AI Dance Challenge Generator",
        "description": "Uses AI to create personalized dance challenges based on user's movement analysis and preferences. Targets teens and young adults.",
        "target_markets": ["US", "EU", "Canada"],
        "data_collected": ["video_uploads", "biometric_movement_analysis", "user_preferences", "location_data"],
        "user_demographics": ["13-25", "dance_enthusiasts"],
        "ai_components": ["computer_vision", "movement_analysis", "recommendation_engine"]
    },
    {
        "feature_name": "Kids Safe Mode",
        "description": "Special mode for users under 13 with enhanced safety features and parental controls.",
        "target_markets": ["US"],
        "data_collected": ["minimal_profile_data", "parental_email"],
        "user_demographics": ["under_13"],
        "ai_components": ["content_filtering"]
    },
    {
        "feature_name": "Location-Based AR Filters",
        "description": "AR filters that change based on user's geographic location and local landmarks.",
        "target_markets": ["Global"],
        "data_collected": ["precise_location", "camera_data", "device_sensors"],
        "user_demographics": ["general_audience"],
        "ai_components": ["computer_vision", "geolocation_processing"]
    }
]

API_BASE_URL = "http://localhost:8001"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_legal_analysis(feature_data):
    """Test legal compliance analysis for a feature"""
    print(f"\n🔍 Testing legal analysis for: {feature_data['feature_name']}")
    print(f"📝 Description: {feature_data['description'][:80]}...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/legal-analyze",
            json=feature_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Legal analysis completed")
            print(f"   Compliance Status: {result.get('compliance_status', 'N/A')}")
            print(f"   Risk Level: {result.get('overall_risk_level', 'N/A')}")
            print(f"   Key Regulations: {len(result.get('key_regulations', []))}")
            print(f"   Requirements: {len(result.get('compliance_requirements', []))}")
            return result
        else:
            print(f"❌ Legal analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_quick_check():
    """Test quick legal check endpoint"""
    print(f"\n⚡ Testing quick legal check")
    
    form_data = {
        "feature_name": "Voice Changer Filter",
        "description": "Real-time voice modification for video content",
        "target_markets": "US,EU",
        "user_demographics": "teens,adults"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/legal-quick-check",
            data=form_data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Quick check completed for: {result.get('feature_name')}")
            return result
        else:
            print(f"❌ Quick check failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Quick check request failed: {e}")
        return None

def test_api_research():
    """Test legal API research functionality directly"""
    print(f"\n🔬 Testing Legal API Research")
    
    try:
        # Test direct API integration
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'src'))
        
        from src.utils.legal_apis import LegalResearchAggregator
        
        async def run_api_test():
            aggregator = LegalResearchAggregator()
            try:
                result = await aggregator.research_topic("children privacy protection")
                print(f"✅ Direct API test: Found {len(result.get('federal_regulations', []))} federal regulations")
                return True
            except Exception as e:
                print(f"❌ Direct API test failed: {e}")
                return False
            finally:
                await aggregator.close()
        
        success = asyncio.run(run_api_test())
        return success
        
    except ImportError as e:
        print(f"⚠️  API modules not available: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Legal Knowledge Agent with Government APIs")
    print("=" * 70)
    
    # Check if API is running
    if not test_api_health():
        print("\n❌ API is not running. Please start the server with:")
        print("   cd C:\\Users\\lauwe\\side_projects\\taktim\\multimodal-backend")
        print("   python main.py")
        sys.exit(1)
    
    print(f"\n📊 Testing with {len(TEST_FEATURES)} sample TikTok features")
    
    # Test API research functionality
    api_test_success = test_api_research()
    
    print(f"\n📊 Testing with {len(TEST_FEATURES)} sample TikTok features")
    
    # Test each feature
    results = []
    for i, feature in enumerate(TEST_FEATURES, 1):
        print(f"\n--- Test {i}/{len(TEST_FEATURES)} ---")
        result = test_legal_analysis(feature)
        if result:
            results.append(result)
    
    # Test quick check
    quick_result = test_quick_check()
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 70)
    print(f"🔬 Direct API test: {'✅ Success' if api_test_success else '❌ Failed'}")
    print(f"✅ Successful analyses: {len(results)}")
    print(f"⚡ Quick check: {'✅ Success' if quick_result else '❌ Failed'}")
    
    if results:
        print(f"\n📈 Analysis Results:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.get('compliance_status', 'Unknown')} - {result.get('overall_risk_level', 'Unknown')} risk")
    
    # Enhanced summary
    total_tests = (1 if api_test_success else 0) + len(results) + (1 if quick_result else 0)
    max_tests = 1 + len(TEST_FEATURES) + 1
    
    print(f"\n🎯 Enhanced Legal Knowledge Agent Status:")
    print(f"   📊 Test Results: {total_tests}/{max_tests} tests passed")
    print(f"   🌐 Government APIs: {'Connected' if api_test_success else 'Not Connected'}")
    print(f"   🚀 System Status: {'Ready for Production!' if total_tests >= max_tests - 1 else 'Needs Debugging'}")
    
    if not api_test_success:
        print(f"\n💡 Note: Government API integration failed. The agent will still work using LLM knowledge,")
        print(f"   but won't have access to real-time legal research. Check your internet connection")
        print(f"   and ensure GovInfo.gov and Congress.gov are accessible.")

if __name__ == "__main__":
    main()
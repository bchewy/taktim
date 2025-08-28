#!/usr/bin/env python3
"""
Quick integration test for the enhanced GeoGov system
Tests the integrated Perplexity + Exa scraping with dynamic inputs
"""

import asyncio
import json
from run_analysis import AnalysisRunner
from main import scraping_aggregator


async def test_single_feature():
    """Test analysis of a single feature"""
    print("🧪 Testing single feature analysis...")
    
    runner = AnalysisRunner()
    
    # Test feature from our inputs
    test_feature = {
        "feature_id": "TEST-001",
        "title": "EU Recommender System with Profiling",
        "description": "Personalized content recommendation system that uses user profiling and behavioral data. Deployed in EU markets.",
        "docs": ["https://internal/recommender-system-eu"],
        "code_hints": [
            "if region == 'EU': apply_dsa_requirements()",
            "user_profile.behavioral_data.collect()",
            "recommendation_engine.personalize(user_preferences)"
        ],
        "tags": ["recommender", "personalization", "EU", "profiling"],
        "expected_compliance": True,
        "expected_regulations": ["EU-DSA"]
    }
    
    try:
        decision = await runner.analyze_feature(test_feature)
        
        print(f"\n✅ Analysis Result:")
        print(f"   Feature ID: {decision.feature_id}")
        print(f"   Compliance Required: {decision.needs_geo_compliance}")
        print(f"   Regulations: {', '.join(decision.regulations)}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Reasoning: {decision.reasoning}")
        
        return decision
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
    finally:
        await scraping_aggregator.close()


async def test_scraping_integration():
    """Test the scraping integration"""
    print("\n🧪 Testing scraping integration...")
    
    runner = AnalysisRunner()
    
    # Test regulations from our config
    test_regulations = [
        {"name": "EU Digital Services Act", "jurisdiction": "EU"},
        {"name": "California SB976", "jurisdiction": "California"}
    ]
    
    try:
        # Test knowledge base refresh
        result = await runner.refresh_knowledge_base(test_regulations)
        
        print(f"✅ Scraping Result:")
        print(f"   Documents Indexed: {result.get('ingested', 0)}")
        print(f"   Regulations Processed: {result.get('regulations_processed', 0)}")
        print(f"   Sources: {json.dumps(result.get('sources', {}), indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Scraping test failed: {e}")
        return None
    finally:
        await scraping_aggregator.close()


async def test_mini_batch():
    """Test a mini batch analysis"""
    print("\n🧪 Testing mini batch analysis...")
    
    runner = AnalysisRunner()
    
    mini_features = [
        {
            "feature_id": "BATCH-001",
            "title": "Basic Content Feed",
            "description": "Simple chronological content feed with no personalization",
            "tags": ["content", "chronological"],
            "expected_compliance": False
        },
        {
            "feature_id": "BATCH-002", 
            "title": "EU Targeted Ads for Minors",
            "description": "Advertising system that targets minors under 18 in EU markets",
            "code_hints": ["if user.age < 18 and region == 'EU': target_ads()"],
            "tags": ["advertising", "minors", "EU", "targeting"],
            "expected_compliance": True,
            "expected_regulations": ["EU-DSA"]
        }
    ]
    
    try:
        decisions = await runner.run_batch_analysis(mini_features)
        summary = runner.generate_summary_report(decisions, mini_features)
        
        print(f"\n✅ Batch Analysis Results:")
        print(f"   Total Features: {summary['summary']['total_features_analyzed']}")
        print(f"   Compliance Required: {summary['summary']['features_requiring_compliance']}")
        print(f"   Average Confidence: {summary['summary']['average_confidence']:.2f}")
        print(f"   Accuracy: {summary['summary']['prediction_accuracy']:.1%}")
        
        return decisions
        
    except Exception as e:
        print(f"❌ Batch test failed: {e}")
        return None
    finally:
        await scraping_aggregator.close()


async def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests")
    print("=" * 50)
    
    # Test 1: Single feature analysis
    feature_result = await test_single_feature()
    
    # Test 2: Scraping integration
    scraping_result = await test_scraping_integration()
    
    # Test 3: Mini batch
    batch_result = await test_mini_batch()
    
    # Summary
    print("\n🎉 Integration Tests Complete!")
    print("=" * 50)
    
    tests_passed = 0
    if feature_result:
        tests_passed += 1
        print("✅ Single feature analysis: PASS")
    else:
        print("❌ Single feature analysis: FAIL")
    
    if scraping_result:
        tests_passed += 1
        print("✅ Scraping integration: PASS")
    else:
        print("❌ Scraping integration: FAIL")
    
    if batch_result:
        tests_passed += 1
        print("✅ Mini batch analysis: PASS")
    else:
        print("❌ Mini batch analysis: FAIL")
    
    print(f"\n🎯 Tests Passed: {tests_passed}/3")
    
    if tests_passed == 3:
        print("🎉 All systems integrated successfully!")
        print("\nNext steps:")
        print("1. Run: python3 run_analysis.py")
        print("2. Or start FastAPI: uvicorn main:app --reload")
        print("3. Test API: POST http://localhost:8000/api/refresh_corpus")
    else:
        print("⚠️  Some integrations need attention. Check error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
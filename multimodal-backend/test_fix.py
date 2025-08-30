#!/usr/bin/env python3
"""
Test the fixed multimodal crew to ensure it doesn't get stuck in loops
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

def test_simple_analysis():
    """Test simplified comprehensive analysis"""
    try:
        from src.agents.multimodal_crew import MultimodalCrew
        
        print("✅ Successfully imported MultimodalCrew")
        
        # Create crew instance
        crew = MultimodalCrew()
        print("✅ Successfully created MultimodalCrew instance")
        
        # Test data - simple task
        test_feature = {
            "project_name": "Simple Test Feature",
            "summary": "Test feature for loop prevention",
            "project_description": "A basic test to ensure our fix works",
            "project_type": "Test",
            "priority": "Low"
        }
        
        print("🔄 Testing comprehensive compliance analysis...")
        
        # This should complete without infinite loops
        result = crew.analyze_comprehensive_compliance(test_feature)
        
        print("✅ Analysis completed successfully!")
        print(f"Status: {result.get('compliance_status', 'Unknown')}")
        print(f"Risk Level: {result.get('risk_level', 'Unknown')}")
        
        if result.get('error'):
            print(f"⚠️  Error in analysis: {result['error']}")
        else:
            print("✅ No errors detected")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing infinite loop fix...")
    print("="*50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set - test will fail")
        sys.exit(1)
    
    success = test_simple_analysis()
    
    if success:
        print("="*50)
        print("✅ All tests passed! Fix appears to be working.")
    else:
        print("="*50)
        print("❌ Tests failed - further investigation needed.")
        sys.exit(1)
#!/usr/bin/env python3
"""Test RAG toggle functionality"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_mode(use_rag: bool, feature: dict):
    """Test analysis in specified mode"""
    mode = "RAG" if use_rag else "Direct"
    
    # Set RAG mode
    toggle_resp = requests.post(f"{BASE_URL}/api/toggle_rag?enable={str(use_rag).lower()}")
    print(f"📊 Set mode to {mode}: {toggle_resp.json()['message']}")
    
    # Test analysis
    print(f"\n🧪 Testing {mode} mode...")
    start = time.time()
    
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze", json=feature, timeout=20)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ {mode} analysis completed in {elapsed:.2f}s")
            print(f"   Compliance needed: {result.get('needs_compliance')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')[:150]}")
            return elapsed
        else:
            print(f"❌ Error {resp.status_code}: {resp.text[:300]}")
            return None
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"⏱️ {mode} mode timed out after {elapsed:.2f}s")
        return None
    except Exception as e:
        print(f"❌ Exception in {mode} mode: {e}")
        return None

def main():
    # Simple test feature
    feature = {
        'feature_id': 'test_comparison',
        'title': 'User Analytics',
        'description': 'Track user behavior patterns',
        'tags': ['analytics', 'tracking']
    }
    
    print("=" * 60)
    print("Testing RAG Toggle Functionality")
    print("=" * 60)
    
    # Test Direct mode first (should be faster)
    direct_time = test_mode(use_rag=False, feature=feature)
    
    print("\n" + "-" * 60 + "\n")
    
    # Test RAG mode (more comprehensive but slower)
    rag_time = test_mode(use_rag=True, feature=feature)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    if direct_time:
        print(f"Direct mode: {direct_time:.2f}s")
    else:
        print("Direct mode: Failed")
    
    if rag_time:
        print(f"RAG mode: {rag_time:.2f}s")
    else:
        print("RAG mode: Failed")
    
    if direct_time and rag_time:
        speedup = rag_time / direct_time
        print(f"\nSpeedup: Direct is {speedup:.1f}x {'faster' if speedup > 1 else 'slower'} than RAG")

if __name__ == "__main__":
    main()
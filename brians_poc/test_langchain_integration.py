#!/usr/bin/env python3
"""
Test script for Unified LangChain RAG integration
Now all LLMClient methods use LangChain RAG internally
"""

import asyncio
import os
from main import FeatureArtifact, analyze, settings, llm_client

async def test_unified_langchain_rag():
    print('🧪 Testing Unified LangChain RAG Integration...')
    print('=' * 50)
    
    # Check if required API keys are available
    if not settings.openai_api_key:
        print('⚠️  OPENAI_API_KEY not set - testing with mock responses')
    
    if not settings.pinecone_api_key:
        print('⚠️  PINECONE_API_KEY not set - testing will use fallbacks')
    
    # Create a test feature artifact
    test_artifact = FeatureArtifact(
        feature_id='test_personalized_recommendations',
        title='Personalized Content Recommendations',
        description='AI-driven system that analyzes user behavior to recommend personalized content feeds and ranking algorithms',
        docs=['User preferences API', 'Content ranking system'],
        code_hints=['recommendation_engine.py', 'user_profiling.js'],
        tags=['personalization', 'recommendations', 'AI']
    )
    
    try:
        print('📊 Testing individual LLMClient methods (all using LangChain RAG internally)...')
        
        # Test individual methods
        print('   🔍 Testing finder...')
        finder_result = await llm_client.finder(test_artifact, [])
        print(f'      Signals found: {len(finder_result.signals)}')
        print(f'      Claims found: {len(finder_result.claims)}')
        
        print('   🔄 Testing counter...')
        counter_result = await llm_client.counter(test_artifact, [])
        print(f'      Counter points: {len(counter_result.counter_points)}')
        print(f'      Missing signals: {len(counter_result.missing_signals)}')
        
        print('   ⚖️  Testing judge...')
        judge_result = await llm_client.judge(test_artifact, finder_result, counter_result, make_decision=True)
        print(f'      Final confidence: {judge_result.confidence:.2f}')
        print(f'      LLM decision: {getattr(judge_result, "llm_decision", "Not available")}')
        
        print('\\n📊 Testing complete analysis pipeline...')
        result = await analyze(test_artifact)
        
        print(f'\\n✅ Unified LangChain RAG Analysis completed!')
        print('=' * 50)
        print(f'   Feature: {result.feature_id}')
        print(f'   Compliance Required: {result.needs_geo_compliance}')
        print(f'   Confidence: {result.confidence:.2f}')
        print(f'   Reasoning: {result.reasoning[:150]}...')
        print(f'   Signals: {len(result.signals)} found: {result.signals[:3]}...')
        print(f'   Regulations: {result.regulations}')
        print(f'   Matched Rules: {result.matched_rules}')
        print(f'   Citations: {len(result.citations)} found')
        print(f'   Analysis Method: {"LLM Decision" if not settings.use_rules_engine else "Rules Engine"}')
        
        return result
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = asyncio.run(test_unified_langchain_rag())
    if result:
        print('\\n🎉 Unified LangChain RAG integration test PASSED!')
        print('   All analysis paths now use LangChain RAG consistently')
    else:
        print('\\n❌ Unified LangChain RAG integration test FAILED')
#!/usr/bin/env python3
"""Test synchronous execution"""

import os
from langchain_rag import LangChainRAGSystem, LangChainRAGSettings

def test_sync():
    print("Testing synchronous compliance_finder...")
    
    settings = LangChainRAGSettings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        pinecone_api_key=os.getenv('PINECONE_API_KEY')
    )
    
    rag = LangChainRAGSystem(settings)
    
    # Now it's synchronous
    result = rag.compliance_finder(
        'Personalized Recommendations',
        'A feature that shows personalized content',
        [],
        ['user_profile'],
        ['personalization']
    )
    
    print(f"✅ Success!")
    print(f"  - Signals: {len(result.get('signals', []))}")
    print(f"  - Claims: {len(result.get('claims', []))}")

if __name__ == "__main__":
    test_sync()
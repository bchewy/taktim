#!/usr/bin/env python3
"""Simple test for RAG system"""

import os
from langchain_rag import LangChainRAGSystem, LangChainRAGSettings

def test_sync():
    print("Testing synchronous RAG chain...")
    
    settings = LangChainRAGSettings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        pinecone_api_key=os.getenv('PINECONE_API_KEY')
    )
    
    rag = LangChainRAGSystem(settings)
    rag._initialize_existing_retriever()
    
    prompt = """Analyze this software feature:
    Title: Personalized Recommendations
    Description: Shows personalized content to users
    
    Provide your analysis with:
    1. SIGNALS: List compliance signals
    2. CLAIMS: List any regulations that apply
    3. CITATIONS: List sources
    """
    
    print("Calling RAG chain...")
    result = rag._safe_rag_invoke(prompt)
    
    print(f"✅ Success! Response length: {len(result)}")
    print(f"Response preview: {result[:300]}...")
    
    # Parse it
    parsed = rag._parse_compliance_response(result, "finder")
    print(f"\nParsed result:")
    print(f"  - Signals: {len(parsed.get('signals', []))}")
    print(f"  - Claims: {len(parsed.get('claims', []))}")
    print(f"  - Citations: {len(parsed.get('citations', []))}")

if __name__ == "__main__":
    test_sync()
#!/usr/bin/env python3
"""Minimal test to isolate the issue"""

import os
import asyncio
from langchain_rag import LangChainRAGSystem, LangChainRAGSettings

async def test_compliance_finder():
    print("Testing compliance_finder directly...")
    
    settings = LangChainRAGSettings(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        pinecone_api_key=os.getenv('PINECONE_API_KEY')
    )
    
    rag = LangChainRAGSystem(settings)
    
    # This is where it hangs
    result = await rag.compliance_finder(
        'Test Feature',
        'A test feature',
        [],
        [],
        []
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_compliance_finder())
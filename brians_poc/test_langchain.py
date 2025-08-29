#!/usr/bin/env python3
"""
Quick test of LangChain RAG system
"""
import asyncio
from langchain_rag import LangChainRAGSystem, ScrapedDocument
from datetime import datetime

async def test_langchain():
    """Test LangChain RAG with simple documents"""
    print("🧪 Testing LangChain RAG system...")
    
    # Create test documents
    test_docs = [
        ScrapedDocument(
            url="https://example.com/doc1",
            title="EU Digital Services Act - Article 1",
            content="The Digital Services Act establishes requirements for recommender systems used by online platforms. These systems must be transparent and allow user control.",
            source="test",
            regulation="EU Digital Services Act",
            jurisdiction="EU", 
            scraped_at=datetime.now().isoformat(),
            content_length=100
        ),
        ScrapedDocument(
            url="https://example.com/doc2", 
            title="EU DSA - Recommender Systems",
            content="Article 29 of the Digital Services Act requires online platforms to provide clear information about recommender system parameters. Users must have options to modify or influence these systems.",
            source="test",
            regulation="EU Digital Services Act",
            jurisdiction="EU",
            scraped_at=datetime.now().isoformat(),
            content_length=120
        )
    ]
    
    try:
        # Initialize system
        rag = LangChainRAGSystem()
        
        # Index documents
        indexed_count = await rag.index_scraped_documents(test_docs)
        print(f"✅ Indexed {indexed_count} chunks")
        
        # Test query
        result = rag.query("What are the requirements for recommender systems?")
        print(f"🔍 Query result:")
        print(f"   Answer: {result['answer']}")
        print(f"   Sources: {len(result['sources'])} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_langchain())
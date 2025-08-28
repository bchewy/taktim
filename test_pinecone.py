#!/usr/bin/env python3
"""
Quick test of Pinecone integration
"""
import asyncio
import os
from langchain_rag import LangChainRAGSystem, LangChainRAGSettings, ScrapedDocument
from datetime import datetime

async def test_pinecone():
    """Test Pinecone integration with simple documents"""
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
        
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not found in environment variables")
        print("   Set it with: export PINECONE_API_KEY='your-key-here'")
        return
    
    print("🧪 Testing Pinecone RAG system...")
    
    try:
        # Initialize RAG system with Pinecone
        settings = LangChainRAGSettings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_name="test-legal-docs"  # Use test index
        )
        
        rag = LangChainRAGSystem(settings=settings)
        
        # Create test legal documents
        test_docs = [
            ScrapedDocument(
                url="https://example.com/eu-dsa",
                title="EU Digital Services Act",
                content="The EU Digital Services Act requires platforms to provide transparency for recommender systems. Users must have options to modify algorithmic parameters and access non-profiling content options.",
                source="test",
                regulation="EU-DSA",
                jurisdiction="EU",
                scraped_at=datetime.now().isoformat(),
                content_length=200
            ),
            ScrapedDocument(
                url="https://example.com/ca-sb976",
                title="California SB976",
                content="California SB976 prohibits social media platforms from using personal information of minors for targeted advertising. Platforms must implement highest privacy settings by default for children under 18.",
                source="test",
                regulation="CA-SB976",
                jurisdiction="California",
                scraped_at=datetime.now().isoformat(),
                content_length=180
            )
        ]
        
        # Index documents
        print("📚 Indexing test documents into Pinecone...")
        indexed_count = await rag.index_scraped_documents(test_docs)
        print(f"✅ Indexed {indexed_count} chunks")
        
        # Test query
        print("🔍 Testing retrieval...")
        query_result = rag.query("What are the requirements for recommender systems?")
        
        print("📝 Query Result:")
        print(f"Answer: {query_result['answer'][:200]}...")
        print(f"Sources: {len(query_result['sources'])} documents")
        print(f"Source URLs: {query_result['sources']}")
        
        print("🎉 Pinecone integration test successful!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pinecone())
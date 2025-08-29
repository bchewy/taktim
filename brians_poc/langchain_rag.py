#!/usr/bin/env python3
"""
LangChain RAG System for Legal Document Analysis
Modern LangChain implementation following official tutorials
"""

import os
import asyncio
import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# LangChain imports (updated for current version)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Pinecone
from pinecone import Pinecone

# Web scraping
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from pydantic_settings import BaseSettings


class LangChainRAGSettings(BaseSettings):
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    chunk_size: int = 500  # Reduced chunk size for large documents
    chunk_overlap: int = 50  # Reduced overlap
    retrieval_k: int = 6
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "legal-compliance-docs"
    
    model_config = {"env_file": ".env", "extra": "ignore"}


@dataclass
class ScrapedDocument:
    """Scraped legal document with metadata"""
    url: str
    title: str
    content: str
    source: str  # "perplexity", "exa"
    regulation: str
    jurisdiction: str
    scraped_at: str
    content_length: int
    
    def to_langchain_doc(self) -> Document:
        """Convert to LangChain Document format"""
        return Document(
            page_content=self.content,
            metadata={
                "url": self.url,
                "title": self.title,
                "source": self.source,
                "regulation": self.regulation,
                "jurisdiction": self.jurisdiction,
                "scraped_at": self.scraped_at,
                "content_length": self.content_length
            }
        )


class LegalDocumentScraper:
    """Scrapes full content from legal document URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    async def scrape_url(self, url: str) -> str:
        """Scrape full text content from a URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try to find main content areas first
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return f"Error scraping content from {url}"
    
    async def scrape_urls(self, urls: List[str], regulation: str, jurisdiction: str, source: str) -> List[ScrapedDocument]:
        """Scrape multiple URLs concurrently"""
        from datetime import datetime
        
        docs = []
        for url in urls:
            print(f"   📄 Scraping: {url}")
            content = await self.scrape_url(url)
            
            if content and len(content) > 100:  # Only keep substantial content
                # Extract title from URL or content
                title = url.split('/')[-1] if '/' in url else url
                if len(content) > 200:
                    # Try to extract title from first meaningful line
                    lines = content.split('\n')[:10]
                    for line in lines:
                        if len(line.strip()) > 10 and len(line.strip()) < 200:
                            title = line.strip()
                            break
                
                docs.append(ScrapedDocument(
                    url=url,
                    title=title,
                    content=content,
                    source=source,
                    regulation=regulation,
                    jurisdiction=jurisdiction,
                    scraped_at=datetime.now().isoformat(),
                    content_length=len(content)
                ))
        
        return docs


class LangChainRAGSystem:
    """Modern LangChain-based RAG system for legal document analysis"""
    
    def __init__(self, settings: Optional[LangChainRAGSettings] = None):
        self.settings = settings or LangChainRAGSettings()
        
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LangChain RAG")
        
        if not self.settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is required for Pinecone vector store")
        
        # Set API keys
        os.environ["OPENAI_API_KEY"] = self.settings.openai_api_key
        os.environ["PINECONE_API_KEY"] = self.settings.pinecone_api_key
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        
        # Initialize components
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        self.scraper = LegalDocumentScraper()
        
        print("✅ LangChain RAG system initialized with Pinecone")
    
    def _initialize_existing_retriever(self):
        """Initialize retriever to connect to existing Pinecone index without adding documents"""
        index_name = self.settings.pinecone_index_name
        
        # Check if index exists
        if index_name not in [idx.name for idx in self.pc.list_indexes()]:
            raise ValueError(f"Pinecone index '{index_name}' does not exist")
        
        print(f"🔗 Connecting to existing Pinecone index: {index_name}")
        
        # Initialize vector store connection
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=self.settings.pinecone_api_key
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.settings.retrieval_k}
        )
        
        # Setup RAG chain
        self._setup_rag_chain()
        
        print(f"✅ Connected to existing Pinecone vector store")
    
    def _generate_doc_hash(self, doc: Document) -> str:
        """Generate a unique hash for a document based on its content and metadata"""
        content = f"{doc.page_content}|{doc.metadata.get('url', '')}|{doc.metadata.get('regulation', '')}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _check_document_exists(self, doc_hash: str) -> bool:
        """Check if a document with this hash already exists in Pinecone"""
        if not self.vectorstore:
            return False
        
        try:
            # Query Pinecone for documents with this hash in metadata
            results = self.vectorstore.similarity_search(
                query="test",  # Dummy query
                k=1,
                filter={"doc_hash": doc_hash}
            )
            return len(results) > 0
        except Exception:
            return False
    
    def _setup_retriever(self, docs: List[Document], force_refresh: bool = False, skip_indexing: bool = False):
        """Setup Pinecone vector store and retriever"""
        try:
            # Create or get Pinecone index
            index_name = self.settings.pinecone_index_name
            
            # Check if index exists, create if not
            if index_name not in [idx.name for idx in self.pc.list_indexes()]:
                print(f"📦 Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                print("✅ Index created successfully")
            else:
                print(f"📦 Using existing Pinecone index: {index_name}")
            
            # Initialize vector store
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=self.embeddings,
                pinecone_api_key=self.settings.pinecone_api_key
            )
            
            if skip_indexing:
                print("⏭️  Skipping indexing - using existing vector store content only")
                total_added = 0
            else:
                # Filter out existing documents if not forcing refresh
                docs_to_add = []
                if force_refresh:
                    print("🔄 Force refresh enabled - will re-index all documents")
                    # Add hashes to all docs for tracking
                    for doc in docs:
                        doc.metadata["doc_hash"] = self._generate_doc_hash(doc)
                    docs_to_add = docs
                else:
                    print("🔍 Checking for existing documents...")
                    existing_hashes = set()
                    new_docs = 0
                    
                    # First, get all existing hashes by querying the vector store
                    try:
                        # Query for some existing docs to see what hashes we have
                        existing_docs = self.vectorstore.similarity_search(
                            query="regulation law", 
                            k=1000,  # Get a large sample to check hashes
                            filter={"doc_hash": {"$exists": True}}
                        )
                        existing_hashes = {doc.metadata.get("doc_hash") for doc in existing_docs if doc.metadata.get("doc_hash")}
                        print(f"   📋 Found {len(existing_hashes)} existing document hashes in vector store")
                    except Exception as e:
                        print(f"   ⚠️  Could not query existing docs: {e} - will index all")
                        existing_hashes = set()
                    
                    # Check each document
                    for doc in docs:
                        doc_hash = self._generate_doc_hash(doc)
                        doc.metadata["doc_hash"] = doc_hash
                        
                        if doc_hash not in existing_hashes:
                            docs_to_add.append(doc)
                            new_docs += 1
                    
                    print(f"📝 {new_docs} new documents to index, {len(docs) - new_docs} already exist")
                
                # Add documents in batches to avoid token limits
                batch_size = 20
                total_added = 0
                
                for i in range(0, len(docs_to_add), batch_size):
                    batch = docs_to_add[i:i+batch_size]
                    try:
                        self.vectorstore.add_documents(batch)
                        total_added += len(batch)
                        print(f"   ✅ Added batch {i//batch_size + 1}/{(len(docs_to_add)-1)//batch_size + 1} ({len(batch)} documents)")
                    except Exception as e:
                        print(f"   ⚠️  Batch {i//batch_size + 1} failed: {e}")
                        continue
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": self.settings.retrieval_k}
            )
            
            # Setup RAG chain
            self._setup_rag_chain()
            
            print(f"🔧 Setup Pinecone retriever with {total_added} documents indexed")
            
        except Exception as e:
            print(f"❌ Failed to setup Pinecone retriever: {e}")
            raise
    
    def _setup_rag_chain(self):
        """Setup the RAG chain for question answering"""
        if not self.retriever:
            raise ValueError("Retriever not initialized")
        
        # Define the prompt template
        template = """You are a legal compliance expert. Use the following pieces of context to answer the question about legal regulations and compliance requirements.

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create the RAG chain with fallback model
        try:
            print(f"🔧 Trying GPT-5 model...")
            llm = ChatOpenAI(
                model="gpt-5-2025-08-07", 
                temperature=0, 
                request_timeout=60,  # Increased timeout for GPT-5
                max_retries=2
            )
            model_name = "gpt-5-2025-08-07"
        except Exception as e:
            print(f"⚠️  GPT-5 setup failed ({e}), falling back to GPT-4o")
            llm = ChatOpenAI(
                model="gpt-4o", 
                temperature=0, 
                request_timeout=45,
                max_retries=2
            )
            model_name = "gpt-4o"
        
        def format_docs(docs):
            print(f"📄 Formatting {len(docs)} retrieved documents")
            formatted_docs = []
            total_length = 0
            max_context_length = 8000  # Reasonable limit
            
            for i, doc in enumerate(docs):
                doc_content = doc.page_content[:1000]  # Limit each doc to 1000 chars
                if total_length + len(doc_content) > max_context_length:
                    print(f"   ⚠️  Truncating context at doc {i} to stay under {max_context_length} chars")
                    break
                formatted_docs.append(doc_content)
                total_length += len(doc_content)
            
            formatted = "\n\n".join(formatted_docs)
            print(f"📝 Final context length: {len(formatted)} chars from {len(formatted_docs)} docs")
            return formatted
        
        print(f"🔧 Setting up RAG chain with {model_name}")
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print(f"✅ RAG chain setup complete")
    
    def _safe_rag_invoke(self, prompt: str) -> str:
        """Safely invoke RAG chain with minimal logging"""
        import time
        
        start_time = time.time()
        print(f"🔄 Starting RAG chain invoke...")
        
        try:
            if not self.rag_chain:
                raise ValueError("RAG chain not initialized")
            
            print(f"📡 Calling LLM via RAG chain...")
            result = self.rag_chain.invoke(prompt)
            
            total_time = time.time() - start_time
            print(f"✅ RAG chain completed in {total_time:.2f}s, response length: {len(result)} chars")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ RAG chain failed after {total_time:.2f}s: {type(e).__name__}: {str(e)}")
            
            error_msg = str(e).lower()
            if "timeout" in error_msg or "request timed out" in error_msg:
                print(f"⏰ Timeout detected, attempting fallback...")
                try:
                    self._setup_rag_chain_with_fallback()
                    fallback_start = time.time()
                    result = self.rag_chain.invoke(prompt)
                    fallback_time = time.time() - fallback_start
                    print(f"✅ Fallback succeeded in {fallback_time:.2f}s")
                    return result
                except Exception as fallback_error:
                    print(f"❌ Fallback failed: {fallback_error}")
                    raise e
            else:
                raise
    
    def _setup_rag_chain_with_fallback(self):
        """Setup RAG chain with GPT-4o as fallback"""
        print(f"🔄 Setting up fallback RAG chain with GPT-4o...")
        
        template = """You are a legal compliance expert. Use the following pieces of context to answer the question about legal regulations and compliance requirements.

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Use GPT-4o as fallback
        llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0, 
            request_timeout=45,
            max_retries=1
        )
        
        def format_docs(docs):
            formatted_docs = []
            total_length = 0
            max_context_length = 6000  # Smaller for fallback
            
            for i, doc in enumerate(docs):
                doc_content = doc.page_content[:800]  # Smaller chunks for fallback
                if total_length + len(doc_content) > max_context_length:
                    break
                formatted_docs.append(doc_content)
                total_length += len(doc_content)
            
            formatted = "\n\n".join(formatted_docs)
            print(f"📝 Fallback context length: {len(formatted)} chars from {len(formatted_docs)} docs")
            return formatted
        
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print(f"✅ Fallback RAG chain ready")
    
    def _parse_compliance_response(self, response: str, response_type: str) -> Dict[str, Any]:
        """Parse natural language response into structured format"""
        try:
            # Try JSON first in case the model still returns JSON
            if response.strip().startswith('{'):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Parse natural language response
            lines = response.split('\n')
            result = {}
            
            if response_type == "finder":
                result = {"signals": [], "claims": [], "citations": []}
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if 'SIGNALS:' in line.upper():
                        current_section = 'signals'
                    elif 'CLAIMS:' in line.upper():
                        current_section = 'claims'
                    elif 'CITATIONS:' in line.upper():
                        current_section = 'citations'
                    elif current_section == 'signals' and line.startswith(('-', '*', '•')) or len(line) > 2:
                        signal = line.lstrip('-*•').strip()
                        if signal:
                            result['signals'].append(signal)
                    elif current_section == 'claims' and line:
                        # Simple parsing for claims
                        if ':' in line:
                            parts = line.split(':', 1)
                            result['claims'].append({
                                "regulation": parts[0].strip(),
                                "why": parts[1].strip() if len(parts) > 1 else "",
                                "citations": []
                            })
                    elif current_section == 'citations' and line:
                        citation = line.lstrip('-*•').strip()
                        if citation:
                            result['citations'].append(citation)
            
            elif response_type == "counter":
                result = {"counter_points": [], "missing_signals": [], "citations": []}
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if 'COUNTER' in line.upper() or 'POINTS' in line.upper():
                        current_section = 'counter_points'
                    elif 'MISSING' in line.upper():
                        current_section = 'missing_signals'
                    elif 'CITATIONS:' in line.upper():
                        current_section = 'citations'
                    elif current_section and line.startswith(('-', '*', '•', '1', '2', '3')) or len(line) > 2:
                        item = line.lstrip('-*•0123456789.').strip()
                        if item and current_section in result:
                            result[current_section].append(item)
            
            elif response_type == "judge":
                # Extract key information from judge response
                result = {
                    "signals": [],
                    "notes": response[:500],  # First 500 chars as notes
                    "confidence": 0.7  # Default confidence
                }
                
                # Try to extract confidence if mentioned
                import re
                confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', response.lower())
                if confidence_match:
                    try:
                        result['confidence'] = float(confidence_match.group(1))
                    except:
                        pass
                
                # Extract decision if mentioned
                if 'requires compliance' in response.lower() or 'needs compliance' in response.lower():
                    result['requires_compliance'] = True
                elif 'does not require' in response.lower() or 'no compliance' in response.lower():
                    result['requires_compliance'] = False
            
            return result
            
        except Exception as e:
            print(f"⚠️  Failed to parse response: {e}")
            # Return minimal structure with raw response
            if response_type == "finder":
                return {"signals": [], "claims": [], "citations": [], "raw_response": response}
            elif response_type == "counter":
                return {"counter_points": [], "missing_signals": [], "citations": [], "raw_response": response}
            else:
                return {"signals": [], "notes": response[:200], "confidence": 0.5, "raw_response": response}
    
    async def index_scraped_documents(self, scraped_docs: List[ScrapedDocument], force_refresh: bool = False, skip_indexing: bool = False) -> int:
        """Index scraped legal documents into the RAG system"""
        if not scraped_docs:
            return 0
        
        # Convert to LangChain documents
        langchain_docs = [doc.to_langchain_doc() for doc in scraped_docs]
        
        # Split documents into chunks
        chunks = []
        for doc in langchain_docs:
            doc_chunks = self.text_splitter.split_documents([doc])
            chunks.extend(doc_chunks)
        
        print(f"📚 Split {len(langchain_docs)} documents into {len(chunks)} chunks")
        
        # Setup retriever
        self._setup_retriever(chunks, force_refresh=force_refresh, skip_indexing=skip_indexing)
        
        # Modern Chroma auto-persists, no need for manual persist()
        
        return 0 if skip_indexing else len(chunks)
    
    async def index_regulation_from_search_apis(self, regulation_name: str, jurisdiction: str, 
                                                perplexity_client=None, exa_client=None, force_refresh: bool = False, skip_indexing: bool = False) -> int:
        """Index a regulation by first finding URLs, then scraping full content"""
        all_scraped_docs = []
        
        # Get URLs from Perplexity
        if perplexity_client:
            try:
                perplexity_result = await perplexity_client.search_regulation(regulation_name, jurisdiction)
                if perplexity_result.official_sites:
                    print(f"🔍 Perplexity found {len(perplexity_result.official_sites)} official sites")
                    scraped = await self.scraper.scrape_urls(
                        perplexity_result.official_sites[:5],  # Limit to top 5
                        regulation_name, jurisdiction, "perplexity"
                    )
                    all_scraped_docs.extend(scraped)
            except Exception as e:
                print(f"⚠️  Perplexity search failed: {e}")
        
        # Get URLs from Exa
        if exa_client:
            try:
                exa_result = await exa_client.search_regulation(regulation_name, jurisdiction)
                if exa_result.official_sites:
                    print(f"🔍 Exa found {len(exa_result.official_sites)} official sites")
                    scraped = await self.scraper.scrape_urls(
                        exa_result.official_sites[:10],  # Exa typically finds more
                        regulation_name, jurisdiction, "exa"
                    )
                    all_scraped_docs.extend(scraped)
            except Exception as e:
                print(f"⚠️  Exa search failed: {e}")
        
        # Index the scraped documents
        if all_scraped_docs:
            indexed_count = await self.index_scraped_documents(all_scraped_docs, force_refresh=force_refresh, skip_indexing=skip_indexing)
            if skip_indexing:
                print(f"⏭️  Skipped indexing {len(all_scraped_docs)} documents for {regulation_name}")
            else:
                print(f"📚 Indexed {indexed_count} chunks from {len(all_scraped_docs)} documents for {regulation_name}")
            return indexed_count
        
        return 0
    
    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """Retrieve relevant documents for a query"""
        if not self.retriever:
            # Try to initialize retriever for existing Pinecone index
            try:
                self._initialize_existing_retriever()
            except Exception as e:
                print(f"⚠️  Could not connect to existing vector store: {e}")
                return []
        
        if not self.retriever:
            print("⚠️  No documents indexed yet")
            return []
        
        k = k or self.settings.retrieval_k
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            return docs[:k]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
    
    def get_rag_chain(self):
        """Get the RAG chain for question answering"""
        if not self.rag_chain:
            raise ValueError("No documents indexed. Call index_* methods first.")
        
        return self.rag_chain
    
    def query(self, question: str) -> Dict[str, Any]:
        """Ask a question about the indexed legal documents"""
        try:
            if not self.rag_chain:
                raise ValueError("RAG chain not initialized. Index documents first.")
            
            # Get answer from RAG chain
            answer = self.rag_chain.invoke(question)
            
            # Get source documents separately for metadata
            source_docs = self.retrieve(question)
            
            return {
                "answer": answer,
                "source_documents": source_docs,
                "sources": [doc.metadata.get("url", "unknown") for doc in source_docs]
            }
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "source_documents": [],
                "sources": []
            }
    
    def compliance_finder(self, artifact_title: str, artifact_description: str, artifact_docs: List[str], 
                               artifact_code_hints: List[str], artifact_tags: List[str]) -> Dict[str, Any]:
        """Find compliance signals and regulations using LangChain RAG"""
        
        prompt = f"""Feature: {artifact_title}
Description: {artifact_description}
Tags: {', '.join(artifact_tags) if artifact_tags else 'none'}

Does this feature need geographical compliance? List:
- SIGNALS: Compliance indicators found
- CLAIMS: Relevant regulations
- CITATIONS: Sources"""

        try:
            print(f"🔍 compliance_finder: Starting analysis")
            
            # Initialize retriever if needed (do this synchronously before async operations)
            if not self.rag_chain:
                print(f"⚠️  RAG chain not initialized, initializing now...")
                self._initialize_existing_retriever()
                print(f"✅ RAG chain initialized")
            
            print(f"🤖 Invoking RAG chain with prompt length: {len(prompt)} chars")
            print(f"🔍 Query preview: {prompt[:200]}...")
            
            # Add timeout to prevent hanging
            import asyncio
            import time
            start_time = time.time()
            
            try:
                print(f"⏱️  Starting LLM call at {time.strftime('%H:%M:%S')}")
                
                # Call synchronously - we're already in an async context
                result = self._safe_rag_invoke(prompt)
                
                end_time = time.time()
                duration = end_time - start_time
                print(f"✅ RAG chain returned result in {duration:.2f}s, length: {len(result)} chars")
                print(f"🔍 Response preview: {result[:200]}...")
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"❌ RAG chain failed after {duration:.2f}s: {type(e).__name__}: {str(e)}")
                return {
                    "signals": [],
                    "claims": [],
                    "citations": [],
                    "error": "Analysis timed out - please try again"
                }
            
            # Parse the natural language response
            return self._parse_compliance_response(result, response_type="finder")
                
        except Exception as e:
            return {
                "signals": [],
                "claims": [],
                "citations": [],
                "error": f"LangChain RAG query failed: {str(e)}"
            }
    
    def compliance_counter(self, artifact_title: str, artifact_description: str, artifact_docs: List[str], 
                                artifact_code_hints: List[str], artifact_tags: List[str]) -> Dict[str, Any]:
        """Find counter-arguments and missing signals using LangChain RAG"""
        
        prompt = f"""Feature: {artifact_title}
Description: {artifact_description}

List reasons this might NOT need compliance:
- COUNTER POINTS: Arguments against
- MISSING SIGNALS: What's absent
- CITATIONS: Sources"""

        try:
            print(f"🔍 compliance_counter: Starting counter-analysis")
            
            if not self.rag_chain:
                print(f"⚠️  RAG chain not initialized for counter analysis, initializing...")
                self._initialize_existing_retriever()
                print(f"✅ RAG chain initialized")
            
            print(f"🤖 Invoking RAG chain for counter analysis")
            
            # Add timeout to prevent hanging
            import asyncio
            import time
            try:
                print(f"⏱️  Starting counter analysis LLM call at {time.strftime('%H:%M:%S')}")
                start_time = time.time()
                
                # Call synchronously
                result = self._safe_rag_invoke(prompt)
                
                end_time = time.time()
                duration = end_time - start_time
                print(f"✅ Counter analysis completed in {duration:.2f}s, result length: {len(result)} chars")
                print(f"🔍 Counter response preview: {result[:200]}...")
            except Exception as e:
                end_time = time.time() 
                duration = end_time - start_time
                print(f"❌ Counter analysis failed after {duration:.2f}s: {type(e).__name__}: {str(e)}")
                return {
                    "counter_points": [],
                    "missing_signals": [],
                    "citations": [],
                    "error": "Counter analysis timed out - please try again"
                }
            
            # Parse the natural language response
            return self._parse_compliance_response(result, response_type="counter")
                
        except Exception as e:
            return {
                "counter_points": [],
                "missing_signals": [],
                "citations": [],
                "error": f"LangChain RAG query failed: {str(e)}"
            }
    
    def compliance_judge(self, artifact_title: str, artifact_description: str, 
                              finder_signals: List[str], finder_claims: List[Dict], 
                              counter_points: List[str], missing_signals: List[str], 
                              make_decision: bool = False) -> Dict[str, Any]:
        """Make final compliance decision using LangChain RAG"""
        
        if make_decision:
            instructions = """**Instructions:**
1. Synthesize all evidence for and against
2. Make a final determination on compliance requirements  
3. Assign a confidence score (0.0-1.0)
4. Combine all relevant signals found
5. Provide clear reasoning

Provide:
- Your confidence level (0.0 to 1.0)
- Clear reasoning for your decision
- Whether this feature requires compliance (yes/no)
- Key signals identified"""
        else:
            instructions = """**Instructions:**
1. Synthesize all evidence for and against
2. Combine all relevant signals found
3. Assign a confidence score (0.0-1.0) for the analysis quality
4. Provide clear reasoning notes
5. DO NOT make the final compliance decision

Provide:
- Your confidence level (0.0 to 1.0)  
- Detailed reasoning and analysis
- Key signals identified

Do NOT make the final compliance decision."""
        
        prompt = f"""Feature: {artifact_title}

FOR compliance: {', '.join(finder_signals[:3]) if finder_signals else 'none'}
AGAINST compliance: {', '.join(counter_points[:3]) if counter_points else 'none'}

{instructions}"""

        try:
            print(f"🔍 compliance_judge: Starting final analysis (make_decision={make_decision})")
            
            if not self.rag_chain:
                print(f"⚠️  RAG chain not initialized for judge analysis, initializing...")
                self._initialize_existing_retriever()
                print(f"✅ RAG chain initialized")
            
            print(f"🤖 Invoking RAG chain for judge analysis")
            
            # Add timeout to prevent hanging
            import asyncio
            import time
            try:
                print(f"⏱️  Starting judge analysis LLM call at {time.strftime('%H:%M:%S')}")
                start_time = time.time()
                
                # Call synchronously
                result = self._safe_rag_invoke(prompt)
                
                end_time = time.time()
                duration = end_time - start_time
                print(f"✅ Judge analysis completed in {duration:.2f}s, result length: {len(result)} chars")
                print(f"🔍 Judge response preview: {result[:200]}...")
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"❌ Judge analysis failed after {duration:.2f}s: {type(e).__name__}: {str(e)}")
                return {
                    "signals": list(set(finder_signals + missing_signals)),
                    "notes": "Judge analysis timed out - please try again",
                    "confidence": 0.0,
                    "error": "Judge analysis timed out"
                }
            
            # Parse the natural language response
            parsed_result = self._parse_compliance_response(result, response_type="judge")
            
            # Ensure we have all required fields
            if "signals" not in parsed_result or not parsed_result["signals"]:
                parsed_result["signals"] = list(set(finder_signals + missing_signals))
            if "confidence" not in parsed_result:
                parsed_result["confidence"] = 0.5
            if "notes" not in parsed_result:
                parsed_result["notes"] = "Analysis completed"
            
            return parsed_result
                
        except Exception as e:
            return {
                "signals": list(set(finder_signals + missing_signals)),
                "notes": f"LangChain RAG analysis failed: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }


# Integration with existing system
async def create_enhanced_rag_system(regulations: List[Dict[str, str]], 
                                   perplexity_client=None, exa_client=None) -> LangChainRAGSystem:
    """Create and populate a LangChain RAG system with legal documents"""
    
    rag = LangChainRAGSystem()
    
    total_indexed = 0
    for regulation in regulations:
        name = regulation.get("name", "")
        jurisdiction = regulation.get("jurisdiction", "")
        
        if name:
            print(f"\n📋 Processing: {name} ({jurisdiction})")
            count = await rag.index_regulation_from_search_apis(
                name, jurisdiction, perplexity_client, exa_client
            )
            total_indexed += count
    
    print(f"\n✅ LangChain RAG setup complete: {total_indexed} total chunks indexed")
    return rag


# Example usage
async def main():
    """Example usage of the LangChain RAG system"""
    
    # Import your existing clients
    from perplexity import PerplexityClient
    from exa_sdk import ExaSDKClient
    
    # Test regulations
    regulations = [
        {"name": "EU Digital Services Act", "jurisdiction": "EU"},
        {"name": "California SB976", "jurisdiction": "California"}
    ]
    
    # Initialize clients
    perplexity_client = PerplexityClient()
    exa_client = ExaSDKClient()
    
    try:
        # Create enhanced RAG system
        rag = await create_enhanced_rag_system(
            regulations, perplexity_client, exa_client
        )
        
        # Test queries
        test_questions = [
            "What are the requirements for recommender systems in the EU?",
            "How does California regulate social media for minors?",
            "What penalties exist for violations of these regulations?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            result = rag.query(question)
            print(f"📝 Answer: {result['answer'][:300]}...")
            print(f"📚 Sources: {len(result['sources'])} documents")
            
    finally:
        await perplexity_client.close()


if __name__ == "__main__":
    asyncio.run(main())
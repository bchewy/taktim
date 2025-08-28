#!/usr/bin/env python3
"""
GeoGov Lite - Python Backend
Single-file FastAPI application for geo-compliance analysis
"""

import asyncio
import csv
import hashlib
import io
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
import uuid

import httpx
import numpy as np
import orjson
import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt, wait_exponential
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("Warning: Mem0 not available, falling back to TF-IDF")

# Import our scraping clients
try:
    from perplexity import PerplexityClient, PerplexityResult
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    print("Warning: Perplexity client not available")

try:
    from exa_sdk import ExaSDKClient, ExaSDKSearchResult
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    try:
        from exa import ExaClient, ExaSearchResult
        EXA_AVAILABLE = True
        print("Using custom Exa client (fallback)")
    except ImportError:
        print("Warning: Exa clients not available")

# Configuration
class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    firecrawl_api_key: str = ""
    exa_api_key: str = ""
    perplexity_api_key: str = ""
    mem0_key: str = ""
    rag_topk: int = 6
    policy_version: str = "v0.1.0"
    
    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

# Data Models
class FeatureArtifact(BaseModel):
    feature_id: str
    title: str
    description: str
    docs: List[str] = []
    code_hints: List[str] = []
    tags: List[str] = []

class Citation(BaseModel):
    source: str
    snippet: str

class Decision(BaseModel):
    feature_id: str
    needs_geo_compliance: bool
    reasoning: str
    regulations: List[str]
    signals: List[str]
    citations: List[Citation]
    confidence: float
    matched_rules: List[str]
    hash: str = ""
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    policy_version: str = settings.policy_version

class FinderOut(BaseModel):
    signals: List[str]
    claims: List[Dict[str, Any]]
    citations: List[str]

class CounterOut(BaseModel):
    counter_points: List[str]
    missing_signals: List[str]
    citations: List[str]

class JudgeOut(BaseModel):
    signals: List[str]
    notes: str
    confidence: float

class SignalSet(BaseModel):
    tags: Set[str] = set()
    text_signals: Set[str] = set()
    hints: List[str] = []
    
    def to_list(self) -> List[str]:
        return list(self.tags.union(self.text_signals))

class Verdict(BaseModel):
    ok: bool
    matched_ids: List[str]
    regulations: List[str]
    reason: str

class RawDoc(BaseModel):
    url: str
    content: str
    title: str = ""
    metadata: Dict[str, Any] = {}

class Chunk(BaseModel):
    id: str
    content: str
    source: str
    metadata: Dict[str, Any] = {}

# Global state
app = FastAPI(title="GeoGov Lite", version="1.0.0")

# Utility Functions
def get_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def compute_sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return ""
    if len(hashes) == 1:
        return hashes[0]
    
    next_level = []
    for i in range(0, len(hashes), 2):
        if i + 1 < len(hashes):
            combined = hashes[i] + hashes[i + 1]
        else:
            combined = hashes[i] + hashes[i]
        next_level.append(compute_sha256(combined))
    
    return merkle_root(next_level)

# Signal Extraction
class SignalExtractor:
    def __init__(self):
        self.patterns = {
            "personalization": r"personali[sz]ed?|ranking|feed|recommendation",
            "minors": r"minor|under\s*18|teen|age\s*gate|parental",
            "moderation": r"appeal|takedown|notice|moderat|remov",
            "geo_eu": r"\bEU\b|EEA|Europe|France|Germany|Italy|Spain",
            "geo_us": r"\bUS\b|United\s*States|America|California|Florida|Utah",
            "safety": r"NCMEC|CSAM|child\s*sexual\s*abuse|safety",
            "ads": r"advertis|targeting|ad\s*serv|marketing"
        }
    
    def extract_signals(self, artifact: FeatureArtifact) -> SignalSet:
        signals = SignalSet()
        
        # Extract from tags
        signals.tags.update(artifact.tags)
        
        # Extract from text
        text = f"{artifact.title} {artifact.description} {' '.join(artifact.code_hints)}"
        text_lower = text.lower()
        
        for signal_type, pattern in self.patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                signals.text_signals.add(signal_type)
        
        # Code hints
        signals.hints = artifact.code_hints
        
        return signals

signal_extractor = SignalExtractor()

# Rules Engine
class RulesEngine:
    def __init__(self, rules_file: str = "rules.yaml"):
        self.rules_file = rules_file
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        try:
            with open(self.rules_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('rules', [])
        except FileNotFoundError:
            return []
    
    def _text_contains(self, text: str, terms: List[str]) -> bool:
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in terms)
    
    def _check_tags(self, signals: SignalSet, required_tags: List[str]) -> bool:
        return any(tag in signals.tags for tag in required_tags)
    
    def _check_text_signals(self, signals: SignalSet, required_signals: List[str]) -> bool:
        return any(sig in signals.text_signals for sig in required_signals)
    
    def evaluate(self, signals: SignalSet, text: str) -> Verdict:
        matched_rules = []
        all_regulations = []
        
        for rule in self.rules:
            rule_id = rule.get('id', '')
            verdict = rule.get('verdict', False)
            
            # Check when_any conditions
            when_any_match = False
            if 'when_any' in rule:
                when_any = rule['when_any']
                if 'tags' in when_any and self._check_tags(signals, when_any['tags']):
                    when_any_match = True
                if 'text' in when_any and self._text_contains(text, when_any['text']):
                    when_any_match = True
            
            # Check when_any_text
            if 'when_any_text' in rule:
                if self._text_contains(text, rule['when_any_text']):
                    when_any_match = True
            
            # Check when_all_text
            when_all_match = True
            if 'when_all_text' in rule:
                when_all_match = all(self._text_contains(text, [term]) for term in rule['when_all_text'])
            
            # Check and_text
            and_text_match = True
            if 'and_text' in rule:
                and_text_match = all(self._text_contains(text, [term]) for term in rule['and_text'])
            
            # Evaluate rule
            if (when_any_match or 'when_any' not in rule and 'when_any_text' not in rule) and when_all_match and and_text_match:
                matched_rules.append(rule_id)
                if verdict:
                    all_regulations.extend(rule.get('regulations', []))
                    return Verdict(
                        ok=True,
                        matched_ids=[rule_id],
                        regulations=rule.get('regulations', []),
                        reason=rule.get('reason', f"Rule {rule_id} triggered")
                    )
        
        return Verdict(
            ok=False,
            matched_ids=matched_rules,
            regulations=[],
            reason="No compliance requirements detected"
        )

rules_engine = RulesEngine()

# Mock LLM Integration (for demo purposes - replace with actual API calls)
class LLMClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_openai(self, messages: List[Dict], model: str = "gpt-3.5-turbo") -> Dict:
        # Mock implementation - in production, use actual OpenAI API
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "signals": ["personalization", "EU"],
                        "claims": [{"regulation": "EU-DSA", "why": "Personalized content", "citations": ["chunk_1"]}],
                        "confidence": 0.8,
                        "notes": "Personalized recommender system in EU jurisdiction"
                    })
                }
            }]
        }
    
    async def finder(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> FinderOut:
        # Mock finder - replace with actual LLM call
        return FinderOut(
            signals=["personalization", "EU"],
            claims=[{"regulation": "EU-DSA", "why": "Personalized content", "citations": ["chunk_1"]}],
            citations=["chunk_1"]
        )
    
    async def counter(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> CounterOut:
        # Mock counter - replace with actual LLM call
        return CounterOut(
            counter_points=["May be business geofencing"],
            missing_signals=["explicit_geo_targeting"],
            citations=["chunk_2"]
        )
    
    async def judge(self, artifact: FeatureArtifact, finder_out: FinderOut, counter_out: CounterOut) -> JudgeOut:
        # Mock judge - replace with actual LLM call
        all_signals = list(set(finder_out.signals + counter_out.missing_signals))
        return JudgeOut(
            signals=all_signals,
            notes="Personalized recommender system likely requires EU compliance",
            confidence=0.81
        )

llm_client = LLMClient()

# Hybrid RAG System: Mem0 Primary + TF-IDF Fallback
class RAGSystem:
    def __init__(self):
        self.chunks = []
        self.use_mem0 = False
        self.memory = None
        
        # Try to initialize Mem0 first (primary)
        if MEM0_AVAILABLE:
            try:
                # Set OpenAI API key in environment for Mem0 to use
                if settings.openai_api_key and settings.openai_api_key.startswith('sk-'):
                    os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                    print(f"🔑 OpenAI API key loaded: {settings.openai_api_key[:20]}...")
                
                # Configure Mem0 to use cloud service with API key
                if settings.mem0_key and settings.mem0_key.startswith('m0-'):
                    # Use Mem0 cloud service
                    config = {
                        "mem0_api_key": settings.mem0_key
                    }
                    print("🚀 Using Mem0 cloud service with API key")
                else:
                    # Fallback to self-hosted with local ChromaDB
                    config = {
                        "vector_store": {
                            "provider": "chroma",
                            "config": {
                                "collection_name": "geogov_legal_docs",
                                "path": "data/mem0_chroma"
                            }
                        },
                        # Configure LLM to preserve content instead of summarizing
                        "llm": {
                            "provider": "openai",
                            "config": {
                                "api_key": settings.openai_api_key,
                                "model": "gpt-4o-mini",
                                "temperature": 0.1,
                                "max_tokens": 4000
                            }
                        }
                    }
                    
                    # Only add embedder if we have OpenAI key
                    if settings.openai_api_key and settings.openai_api_key.startswith('sk-'):
                        config["embedder"] = {
                            "provider": "openai", 
                            "config": {
                                "api_key": settings.openai_api_key,
                                "model": "text-embedding-3-small"
                            }
                        }
                    print("🚀 Using Mem0 self-hosted with local ChromaDB")
                
                self.memory = Memory.from_config(config)
                self.use_mem0 = True
                print("✅ Mem0 initialized successfully - will use semantic search for legal documents")
                
            except Exception as e:
                print(f"⚠️  Mem0 initialization failed: {e}")
                print("📋 Falling back to TF-IDF system")
                
        # Initialize TF-IDF fallback system (always initialize for potential fallback)
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.doc_vectors = None
        
        if not self.use_mem0:
            print("📊 Initialized TF-IDF fallback system")
    
    def index_documents(self, docs: List[RawDoc]) -> int:
        self.chunks = []
        indexed_count = 0
        
        # Create chunks for all systems
        for i, doc in enumerate(docs):
            chunk = Chunk(
                id=f"legal_doc_{i}",
                content=doc.content,
                source=doc.url,
                metadata=doc.metadata
            )
            self.chunks.append(chunk)
        
        if self.use_mem0 and self.memory:
            # Index into Mem0 as memories (legal documents)
            for chunk in self.chunks:
                try:
                    # Store legal document as memory with rich metadata
                    print(f"📝 Adding document {chunk.id} to Mem0...")
                    
                    # Fix: Mem0 expects messages in proper format
                    try:
                        # Store full legal document content in Mem0
                        messages = [
                            {
                                "role": "user", 
                                "content": f"Store this complete legal regulation document: {chunk.content}"
                            },
                            {
                                "role": "assistant",
                                "content": f"I will store the complete legal regulation from {chunk.source} covering {chunk.metadata.get('jurisdiction', 'general')} jurisdiction."
                            }
                        ]
                        result = self.memory.add(
                            user_id="legal_corpus",  # Common user_id for all legal docs
                            messages=messages,
                            infer=False,  # Disable automatic inference/summarization
                            metadata={
                                "document_id": chunk.id,
                                "source": chunk.source,
                                "jurisdiction": chunk.metadata.get("jurisdiction", "unknown"),
                                "topic": chunk.metadata.get("topic", "regulation"),
                                "document_type": "legal_regulation",
                                "full_content": chunk.content,  # Store full content in metadata too
                                **chunk.metadata
                            }
                        )
                        print(f"📝 Method 1 - Proper messages format - result: {result}")
                        
                        # Fix: Add 5-second delay for write transaction to complete (Issue #2386)
                        import time
                        time.sleep(5)  # Increased to 5 seconds as per GitHub fix
                        
                    except Exception as e1:
                        print(f"📝 Method 1 failed: {e1}")
                        
                        try:
                            # Method 2: Messages format (original approach)
                            result = self.memory.add(
                                user_id="legal_corpus",
                                messages=[{
                                    "role": "user", 
                                    "content": chunk.content
                                }],
                                metadata={
                                    "document_id": chunk.id,
                                    "source": chunk.source,
                                    "jurisdiction": chunk.metadata.get("jurisdiction", "unknown"),
                                    "topic": chunk.metadata.get("topic", "regulation"),
                                    "document_type": "legal_regulation",
                                }
                            )
                            print(f"📝 Method 2 - Messages format - result: {result}")
                        except Exception as e2:
                            print(f"📝 Method 2 also failed: {e2}")
                            result = {"error": str(e2)}
                    
                    indexed_count += 1
                    
                except Exception as e:
                    print(f"Warning: Could not index document {chunk.id} into Mem0: {e}")
                    continue
            
            print(f"📚 Indexed {indexed_count} legal documents into Mem0 memory")
            
            # Fix: Explicitly persist ChromaDB data
            try:
                if hasattr(self.memory, 'client') and hasattr(self.memory.client, 'persist'):
                    self.memory.client.persist()
                    print("💾 Explicitly persisted ChromaDB data")
                elif hasattr(self.memory, 'vector_store') and hasattr(self.memory.vector_store, 'persist'):
                    self.memory.vector_store.persist()
                    print("💾 Explicitly persisted vector store data")
            except Exception as e:
                print(f"⚠️  Could not explicitly persist data: {e}")
            
            # Add another delay after persistence
            import time
            time.sleep(2)
            print("⏳ Additional delay after persistence...")
            
            # Verification: Check if memories were actually stored
            try:
                all_memories = self.memory.get_all(user_id="legal_corpus")
                print(f"🔍 Verification: Found {len(all_memories.get('results', []))} memories stored in Mem0")
                if len(all_memories.get('results', [])) == 0:
                    print("⚠️  WARNING: No memories found after indexing! This is a known Mem0 issue.")
            except Exception as e:
                print(f"⚠️  Could not verify memory storage: {e}")
        
        # Always prepare TF-IDF fallback (even when using Mem0)
        if self.chunks:
            corpus = [chunk.content for chunk in self.chunks]
            self.doc_vectors = self.vectorizer.fit_transform(corpus)
            
            if not self.use_mem0:
                indexed_count = len(self.chunks)
                print(f"📊 Indexed {indexed_count} documents with TF-IDF fallback")
        
        return indexed_count
    
    def retrieve(self, query: str, k: int = 6) -> List[Chunk]:
        if self.use_mem0 and self.memory:
            return self._retrieve_with_mem0(query, k)
        else:
            return self._retrieve_with_tfidf(query, k)
    
    def _retrieve_with_mem0(self, query: str, k: int = 6) -> List[Chunk]:
        try:
            # Search legal document memories with semantic search
            memories = self.memory.search(
                user_id="legal_corpus",
                query=f"Legal regulations related to: {query}",
                limit=k
            )
            
            print(f"🔍 Mem0 returned memories: {memories}")
            
            # Extract relevant chunks from Mem0 search results
            relevant_chunks = []
            if memories.get('results'):
                # Process Mem0 memories into chunks with full content
                for memory in memories['results'][:k]:
                    chunk_id = memory.get('metadata', {}).get('document_id', f"mem0_{len(relevant_chunks)}")
                    
                    # Use full content from metadata if available, otherwise use memory content
                    full_content = memory.get('metadata', {}).get('full_content')
                    if full_content:
                        content = full_content  # Use the complete legal document
                        print(f"✅ Using full legal document content from Mem0 metadata ({len(content)} chars)")
                    else:
                        content = memory.get('memory', '')  # Fallback to memory content
                        print(f"⚠️  Using Mem0 memory content ({len(content)} chars) - may be summarized")
                    
                    source = memory.get('metadata', {}).get('source', 'unknown')
                    
                    chunk = Chunk(
                        id=chunk_id,
                        content=content,
                        source=source,
                        metadata=memory.get('metadata', {})
                    )
                    relevant_chunks.append(chunk)
                    
                print(f"🎯 Using {len(relevant_chunks)} documents from Mem0 semantic search")
            else:
                print("⚠️  No Mem0 memories found - this shouldn't happen if storage worked")
            
            print(f"🔍 Mem0 semantic search found {len(relevant_chunks)} relevant legal documents")
            return relevant_chunks
            
        except Exception as e:
            print(f"Warning: Mem0 retrieval failed: {e}, falling back to TF-IDF")
            return self._retrieve_with_tfidf(query, k)
    
    def _retrieve_with_tfidf(self, query: str, k: int = 6) -> List[Chunk]:
        if not self.chunks or self.doc_vectors is None:
            return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()
            top_indices = np.argsort(similarities)[::-1][:k]
            
            relevant_chunks = []
            for idx in top_indices:
                if similarities[idx] > 0.01:
                    relevant_chunks.append(self.chunks[idx])
            
            print(f"📊 TF-IDF search found {len(relevant_chunks)} relevant documents")
            return relevant_chunks
            
        except Exception as e:
            print(f"Warning: Could not perform TF-IDF retrieval: {e}")
            return []
    
    def hydrate_citations(self, chunk_ids: List[str]) -> List[Citation]:
        citations = []
        # If no specific chunk_ids provided, use all chunks (Mem0 case)
        if not chunk_ids and self.chunks:
            citations.append(Citation(
                source=self.chunks[0].source,
                snippet=self.chunks[0].content[:200] + "..." if len(self.chunks[0].content) > 200 else self.chunks[0].content
            ))
        else:
            for chunk_id in chunk_ids:
                for chunk in self.chunks:
                    if chunk.id == chunk_id:
                        citations.append(Citation(
                            source=chunk.source,
                            snippet=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                        ))
                        break
        return citations

# Integrated Scraping System
class ScrapingAggregator:
    """Aggregates content from multiple search APIs (Perplexity, Exa) for comprehensive legal research"""
    
    def __init__(self):
        self.perplexity_client = None
        self.exa_client = None
        
        # Initialize Perplexity client if available
        if PERPLEXITY_AVAILABLE and settings.perplexity_api_key:
            try:
                self.perplexity_client = PerplexityClient()
                print("✅ Perplexity client initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize Perplexity client: {e}")
        
        # Initialize Exa client if available
        if EXA_AVAILABLE and settings.exa_api_key:
            try:
                if 'ExaSDKClient' in globals():
                    self.exa_client = ExaSDKClient()
                else:
                    self.exa_client = ExaClient()
                print("✅ Exa client initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize Exa client: {e}")
    
    async def search_regulation(self, regulation_name: str, jurisdiction: str = "") -> List[RawDoc]:
        """Search for a specific regulation across all available APIs"""
        all_docs = []
        
        # Search with Perplexity
        if self.perplexity_client:
            try:
                perplexity_result = await self.perplexity_client.search_regulation(regulation_name, jurisdiction)
                for site in perplexity_result.official_sites[:5]:  # Limit to top 5
                    all_docs.append(RawDoc(
                        url=site,
                        content=perplexity_result.summary,
                        title=f"{regulation_name} - Perplexity Research",
                        metadata={
                            "source": "perplexity",
                            "jurisdiction": jurisdiction,
                            "regulation": regulation_name,
                            "confidence": perplexity_result.confidence
                        }
                    ))
                print(f"🔍 Perplexity found {len(perplexity_result.official_sites)} official sites for {regulation_name}")
            except Exception as e:
                print(f"⚠️  Perplexity search failed for {regulation_name}: {e}")
        
        # Search with Exa
        if self.exa_client:
            try:
                exa_result = await self.exa_client.search_regulation(regulation_name, jurisdiction)
                for site in exa_result.official_sites[:10]:  # Exa typically finds more
                    # Find the corresponding result for full text
                    site_result = next((r for r in exa_result.results if r.url == site), None)
                    content = site_result.text if site_result and site_result.text else f"Official source for {regulation_name}"
                    
                    all_docs.append(RawDoc(
                        url=site,
                        content=content,
                        title=site_result.title if site_result else f"{regulation_name} - Exa Research",
                        metadata={
                            "source": "exa",
                            "jurisdiction": jurisdiction,
                            "regulation": regulation_name,
                            "confidence": exa_result.confidence,
                            "score": site_result.score if site_result else 0.0
                        }
                    ))
                print(f"🔍 Exa found {len(exa_result.official_sites)} official sites for {regulation_name}")
            except Exception as e:
                print(f"⚠️  Exa search failed for {regulation_name}: {e}")
        
        return all_docs
    
    async def search_compliance_topic(self, topic: str, jurisdictions: List[str] = None) -> List[RawDoc]:
        """Search for compliance information on a topic across all available APIs"""
        all_docs = []
        
        # Search with Perplexity
        if self.perplexity_client:
            try:
                perplexity_result = await self.perplexity_client.search_compliance_topic(topic, jurisdictions)
                for site in perplexity_result.official_sites[:5]:
                    all_docs.append(RawDoc(
                        url=site,
                        content=perplexity_result.summary,
                        title=f"{topic} Compliance - Perplexity Research",
                        metadata={
                            "source": "perplexity",
                            "topic": topic,
                            "jurisdictions": jurisdictions or [],
                            "confidence": perplexity_result.confidence
                        }
                    ))
                print(f"🔍 Perplexity found {len(perplexity_result.official_sites)} sites for {topic}")
            except Exception as e:
                print(f"⚠️  Perplexity topic search failed for {topic}: {e}")
        
        # Search with Exa
        if self.exa_client:
            try:
                exa_result = await self.exa_client.search_compliance_topic(topic, jurisdictions)
                for site in exa_result.official_sites[:8]:
                    site_result = next((r for r in exa_result.results if r.url == site), None)
                    content = site_result.text if site_result and site_result.text else f"Compliance information for {topic}"
                    
                    all_docs.append(RawDoc(
                        url=site,
                        content=content,
                        title=site_result.title if site_result else f"{topic} Compliance - Exa Research",
                        metadata={
                            "source": "exa",
                            "topic": topic,
                            "jurisdictions": jurisdictions or [],
                            "confidence": exa_result.confidence
                        }
                    ))
                print(f"🔍 Exa found {len(exa_result.official_sites)} sites for {topic}")
            except Exception as e:
                print(f"⚠️  Exa topic search failed for {topic}: {e}")
        
        return all_docs
    
    async def refresh_corpus_for_regulations(self, regulations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Refresh the corpus with content for multiple regulations"""
        all_docs = []
        sources_count = {}
        
        for reg in regulations:
            name = reg.get("name", "")
            jurisdiction = reg.get("jurisdiction", "")
            
            if not name:
                continue
                
            print(f"\n📋 Researching: {name} ({jurisdiction})")
            regulation_docs = await self.search_regulation(name, jurisdiction)
            all_docs.extend(regulation_docs)
            
            sources_count[f"{name}_{jurisdiction}"] = len(regulation_docs)
        
        # Index all documents into the RAG system
        if all_docs:
            indexed_count = rag_system.index_documents(all_docs)
            print(f"\n📚 Successfully indexed {indexed_count} documents from {len(sources_count)} regulations")
        
        return {
            "ingested": len(all_docs),
            "regulations_processed": len(sources_count),
            "sources": sources_count
        }
    
    async def close(self):
        """Close all clients"""
        if self.perplexity_client:
            await self.perplexity_client.close()
        if self.exa_client and hasattr(self.exa_client, 'close'):
            await self.exa_client.close()

# Initialize systems
rag_system = RAGSystem()
scraping_aggregator = ScrapingAggregator()

# Evidence System
class EvidenceSystem:
    def __init__(self, receipts_file: str = "data/receipts.jsonl"):
        self.receipts_file = receipts_file
        Path("data").mkdir(exist_ok=True)
    
    def write_receipt(self, decision: Decision) -> str:
        # Create canonical JSON for hashing
        canonical_dict = decision.model_dump()
        canonical_dict.pop('hash', None)  # Remove hash field for canonical representation
        canonical_json = orjson.dumps(canonical_dict, option=orjson.OPT_SORT_KEYS).decode()
        
        # Compute hash
        hash_value = compute_sha256(canonical_json)
        decision.hash = f"sha256-{hash_value}"
        
        # Write to JSONL file
        with open(self.receipts_file, 'a') as f:
            f.write(orjson.dumps(decision.model_dump()).decode() + '\n')
        
        return decision.hash
    
    def export_csv(self, decisions: List[Decision], filename: str = "data/outputs.csv") -> str:
        if not decisions:
            return filename
        
        df_data = []
        for d in decisions:
            df_data.append({
                'feature_id': d.feature_id,
                'title': '',  # Not in decision model
                'needs_geo_compliance': d.needs_geo_compliance,
                'reasoning': d.reasoning,
                'regulations': ','.join(d.regulations),
                'confidence': d.confidence,
                'signals': ','.join(d.signals),
                'citations': len(d.citations),
                'matched_rules': ','.join(d.matched_rules),
                'policy_version': d.policy_version,
                'ts': d.ts
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)
        return filename
    
    def make_evidence_zip(self, feature_id: Optional[str] = None) -> bytes:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add receipts
            if os.path.exists(self.receipts_file):
                zf.write(self.receipts_file, "receipts.jsonl")
            
            # Add outputs CSV if exists
            if os.path.exists("data/outputs.csv"):
                zf.write("data/outputs.csv", "outputs.csv")
            
            # Add policy snapshot
            if os.path.exists("rules.yaml"):
                zf.write("rules.yaml", "policy_snapshot.yaml")
            
            # Add merkle root
            hashes = []
            if os.path.exists(self.receipts_file):
                with open(self.receipts_file, 'r') as f:
                    for line in f:
                        try:
                            decision_data = orjson.loads(line)
                            if 'hash' in decision_data:
                                hashes.append(decision_data['hash'])
                        except:
                            continue
            
            merkle = merkle_root(hashes)
            zf.writestr("merkle.txt", merkle)
        
        return zip_buffer.getvalue()

evidence_system = EvidenceSystem()

# Core Analysis Function
async def analyze(artifact: FeatureArtifact) -> Decision:
    # Extract signals
    sigs = signal_extractor.extract_signals(artifact)
    
    # RAG retrieval
    query = " ".join([artifact.title, artifact.description] + sigs.hints)
    chunks = rag_system.retrieve(query, k=settings.rag_topk)
    
    # LLM ensemble
    finder_out = await llm_client.finder(artifact, chunks)
    counter_out = await llm_client.counter(artifact, chunks)
    judge_out = await llm_client.judge(artifact, finder_out, counter_out)
    
    # Rules engine final decision
    text = f"{artifact.title} {artifact.description}"
    verdict = rules_engine.evaluate(sigs, text)
    
    # Create decision
    all_signals = list(set(sigs.to_list() + judge_out.signals))
    decision = Decision(
        feature_id=artifact.feature_id,
        needs_geo_compliance=verdict.ok,
        reasoning=verdict.reason,
        regulations=verdict.regulations,
        signals=all_signals,
        citations=rag_system.hydrate_citations(finder_out.citations[:3]),
        confidence=judge_out.confidence,
        matched_rules=verdict.matched_ids,
        ts=get_utc_timestamp(),
        policy_version=settings.policy_version
    )
    
    # Write receipt and set hash
    decision.hash = evidence_system.write_receipt(decision)
    
    return decision

# FastAPI Endpoints
@app.get("/api/health")
async def health():
    rules_content = ""
    if os.path.exists("rules.yaml"):
        with open("rules.yaml", 'r') as f:
            rules_content = f.read()
    
    rules_hash = compute_sha256(rules_content)
    
    return {
        "ok": True,
        "rules_hash": rules_hash,
        "mem0_docs": len(rag_system.chunks),
        "policy_version": settings.policy_version
    }

@app.post("/api/analyze")
async def analyze_endpoint(artifact: FeatureArtifact) -> Decision:
    try:
        return await analyze(artifact)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bulk_analyze")
async def bulk_analyze(request: Dict[str, List[FeatureArtifact]]):
    items = request.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="No items provided")
    
    decisions = []
    for item in items:
        try:
            decision = await analyze(item)
            decisions.append(decision)
        except Exception as e:
            # Continue with other items if one fails
            continue
    
    # Export to CSV
    csv_path = evidence_system.export_csv(decisions)
    
    return {
        "count": len(decisions),
        "csv_path": csv_path
    }

@app.get("/api/evidence")
async def get_evidence(feature_id: Optional[str] = None):
    try:
        zip_data = evidence_system.make_evidence_zip(feature_id)
        return Response(
            content=zip_data,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=evidence.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh_corpus")
async def refresh_corpus():
    """Refresh corpus using dynamic input configuration"""
    try:
        # Load regulations from inputs.yaml
        with open("inputs.yaml", 'r') as f:
            inputs_config = yaml.safe_load(f)
        
        regulations = inputs_config.get('regulations', [])
        if not regulations:
            # Fallback to mock data if no configuration
            return await refresh_corpus_fallback()
        
        # Use the scraping aggregator to research all regulations
        result = await scraping_aggregator.refresh_corpus_for_regulations(regulations)
        
        return result
        
    except Exception as e:
        print(f"⚠️  Failed to refresh corpus from inputs.yaml: {e}")
        # Fallback to mock data
        return await refresh_corpus_fallback()

async def refresh_corpus_fallback():
    """Fallback corpus refresh with mock data"""
    mock_docs = [
        RawDoc(
            url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065",
            content="""EU Digital Services Act (DSA) Article 38 - Recommender Systems Transparency:

1. Recipients of the service shall be able to easily understand when information is being prioritised based on profiling as defined in Article 4(4) of Regulation (EU) 2016/679.

2. For each of their recommender systems, providers of online platforms shall set out in their terms and conditions, in plain and intelligible language:
   (a) the main parameters used in their recommender systems, as well as any options for the recipients of the service to modify or influence those main parameters, including at least one option which is not based on profiling;
   (b) how to access and use the options referred to in point (a).

3. Providers of online platforms shall provide recipients of their service with at least one option for each of their recommender systems that is not based on profiling. That option shall be prominently displayed and easily accessible.

4. Very large online platforms shall provide recipients with easily accessible functionality that allows them to view content that is not recommended on the basis of profiling or categorisation of the recipient.

Article 39 - Risk Assessment:
Very large online platforms shall diligently identify, analyse and assess any systemic risks in the Union stemming from the design or functioning of their service and its related systems, including algorithmic systems, or from the use made of their service. Those assessments shall include the following systemic risks:
(a) the dissemination of illegal content;
(b) any actual or foreseeable negative effects for the exercise of fundamental rights;
(c) intentional manipulation of their service, including by means of inauthentic use or automated exploitation of the service.""",
            title="EU Digital Services Act - Recommender Systems & Risk Assessment",
            metadata={"jurisdiction": "EU", "topic": "recommender_systems", "compliance_areas": "profiling,transparency,risk_assessment"}
        ),
        RawDoc(
            url="https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240SB976",
            content="""California SB976 - Social Media Platforms: Children
SEC. 2. Chapter 22.1 (commencing with Section 22675) is added to Division 8 of the Business and Professions Code, to read:

22675. For purposes of this chapter:
(a) "Child" means a natural person under 18 years of age.
(b) "Social media platform" means an internet website or application that is primarily used for social networking and allows users to view and post content, communicate with other users, and join communities.

22676. (a) A social media platform shall not use the personal information of a child to provide advertising that is targeted to that child.
(b) A social media platform shall not use any system design feature that the platform knows, or should know, causes or is reasonably likely to cause addiction-like behavior by children on the platform.

22677. (a) A social media platform shall provide, by default, the highest privacy settings for child users and shall require affirmative consent before reducing those privacy protections.
(b) A social media platform shall not send notifications to a child between the hours of 12 a.m. and 6 a.m. or during school hours, unless there is an imminent threat to the child's physical safety.

22678. Enforcement and Civil Penalties:
(a) A violation of this chapter constitutes an unlawful business practice under Section 17200.
(b) The Attorney General may seek civil penalties up to $25,000 per affected child for each violation.
(c) A child or parent may bring a civil action for violations, seeking actual damages or $1,000, whichever is greater.""",
            title="California SB976 - Social Media Child Protection",
            metadata={"jurisdiction": "CA", "topic": "minors_protection", "compliance_areas": "targeted_advertising,privacy,parental_controls,penalties"}
        )
    ]
    
    indexed_count = rag_system.index_documents(mock_docs)
    
    return {
        "ingested": indexed_count,
        "sources": {
            "EU-DSA": 1,
            "CA-SB976": 1
        }
    }

@app.get("/api/memories")
async def get_memories():
    """Debug endpoint to check what memories are stored in Mem0"""
    if rag_system.use_mem0 and rag_system.memory:
        try:
            # Try different ways to get memories
            results = {}
            
            # Method 1: get_all with legal_corpus user_id
            try:
                memories1 = rag_system.memory.get_all(user_id="legal_corpus")
                results["legal_corpus"] = memories1
            except Exception as e:
                results["legal_corpus_error"] = str(e)
            
            # Method 2: Try individual document user_ids
            try:
                memories2 = rag_system.memory.get_all(user_id="legal_doc_0")
                results["legal_doc_0"] = memories2
            except Exception as e:
                results["legal_doc_0_error"] = str(e)
                
            try:
                memories3 = rag_system.memory.get_all(user_id="legal_doc_1")  
                results["legal_doc_1"] = memories3
            except Exception as e:
                results["legal_doc_1_error"] = str(e)
                
            # Method 3: Try to see all user_ids or general info
            try:
                # Some Mem0 versions might have different methods
                if hasattr(rag_system.memory, 'list_users'):
                    results["users"] = rag_system.memory.list_users()
                elif hasattr(rag_system.memory, 'get_users'):
                    results["users"] = rag_system.memory.get_users()
            except Exception as e:
                results["users_error"] = str(e)
            
            return {
                "system": "mem0",
                "results": results,
                "mem0_initialized": True,
                "chunks_available": len(rag_system.chunks)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "system": "mem0",
                "memory_count": 0
            }
    else:
        return {
            "message": "Using TF-IDF fallback, no Mem0 memories",
            "system": "tfidf",
            "chunks": len(rag_system.chunks)
        }

@app.post("/api/test_mem0")
async def test_mem0():
    """Simple test to verify Mem0 is working"""
    if rag_system.use_mem0 and rag_system.memory:
        try:
            # Try a very simple add/get cycle
            test_result = rag_system.memory.add(
                user_id="test_user",
                messages="This is a simple test memory for legal compliance."
            )
            
            # Try to retrieve it
            retrieved = rag_system.memory.get_all(user_id="test_user")
            
            return {
                "add_result": test_result,
                "get_result": retrieved,
                "test": "simple_mem0_test"
            }
        except Exception as e:
            return {"error": str(e), "test": "failed"}
    else:
        return {"error": "Mem0 not available"}

# Initialize with some sample data
@app.on_event("startup")
async def startup_event():
    # Initialize with mock corpus
    await refresh_corpus()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
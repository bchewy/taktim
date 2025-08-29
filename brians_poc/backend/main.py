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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt, wait_exponential

# OpenAI API for LLM integration
from openai import AsyncOpenAI

# Simplified RAG system
try:
    from langchain_rag import SimplifiedRAGSystem, create_enhanced_rag_system
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Error: RAG system not available. Please install: pip install langchain-openai langchain-chroma chromadb")

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
    print("Warning: Exa SDK not available")

# Configuration
class Settings(BaseSettings):
    openai_api_key: str = ""
    exa_api_key: str = ""
    perplexity_api_key: str = ""
    rag_topk: int = 6
    policy_version: str = "v0.1.0"
    use_rules_engine: bool = False  # Toggle: True = rules engine decides, False = LLM decides (default)
    skip_indexing: bool = False  # Toggle: True = skip vector store indexing, False = index documents (default)
    skip_scraping: bool = False  # Toggle: True = skip scraping documents, False = scrape documents (default)
    use_rag: bool = True  # Toggle: True = use RAG for analysis (slower), False = direct LLM calls (faster)
    llm_timeout: int = 10  # Timeout for LLM API calls in seconds
    chroma_persist_directory: str = "data/chroma_db"
    database_path: str = "data/analysis.db"
    
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
    llm_decision: Optional[bool] = None  # Only set when LLM makes final decision

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

# Add CORS middleware to handle browser requests from file:// or different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

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

# Lazy initialization for signal extractor  
_signal_extractor = None

def get_signal_extractor():
    global _signal_extractor
    if _signal_extractor is None:
        _signal_extractor = SignalExtractor()
    return _signal_extractor

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

# Lazy initialization for rules engine
_rules_engine = None

def get_rules_engine():
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = RulesEngine()
    return _rules_engine

# Real OpenAI LLM Integration
class LLMClient:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM integration")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-5-2025-08-07"  # Default model for RAG mode
        self.direct_model = "gpt-4o-mini"  # Faster model for Direct mode
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_openai(self, messages: List[Dict], model: str = None) -> Dict:
        """Call OpenAI API with retry logic"""
        import asyncio
        
        try:
            total_prompt_length = sum(len(str(msg)) for msg in messages)
            print(f"🤖 Calling OpenAI API with model: {model or self.model}")
            print(f"📝 Message count: {len(messages)}")
            print(f"📏 Total prompt length: {total_prompt_length} chars (~{total_prompt_length//4} tokens)")
            
            # Warning if prompt is too long
            if total_prompt_length > 20000:  # ~5k tokens
                print(f"⚠️  Large prompt detected! May hit token limits.")
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model or self.model,
                    messages=messages,
                    # temperature=1.0,  # GPT-5 only supports default temperature (1.0)
                    max_completion_tokens=8000  # Further increased token limit for GPT-5
                    # Removed response_format as it causes GPT-5 to hang
                ),
                timeout=settings.llm_timeout
            )
            
            print(f"✅ OpenAI API response received")
            print(f"📊 Response details: finish_reason={response.choices[0].finish_reason}")
            print(f"📊 Content length: {len(response.choices[0].message.content or '')} chars")
            
            content = response.choices[0].message.content or ""
            print(f"🔍 Raw content preview: '{content[:100]}...'")
            
            return {
                "choices": [{
                    "message": {
                        "content": content
                    }
                }]
            }
        except asyncio.TimeoutError:
            print(f"⏱️ OpenAI API timeout after {settings.llm_timeout}s")
            return {
                "choices": [{
                    "message": {
                        "content": "TIMEOUT: Analysis timed out"
                    }
                }]
            }
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            print(f"   Error type: {type(e).__name__}")
            raise
    
    def _parse_finder_response(self, response: str) -> FinderOut:
        """Parse natural language finder response"""
        signals = []
        claims = []
        citations = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'SIGNAL' in line.upper():
                current_section = 'signals'
            elif 'CLAIM' in line.upper():
                current_section = 'claims'
            elif 'CITATION' in line.upper():
                current_section = 'citations'
            elif line.startswith('-') or line.startswith('•'):
                content = line.lstrip('-•').strip()
                if content and current_section == 'signals':
                    signals.append(content)
                elif content and current_section == 'claims':
                    claims.append({"claim": content, "regulation": content})
                elif content and current_section == 'citations':
                    citations.append(content)
        
        return FinderOut(signals=signals, claims=claims, citations=citations)
    
    def _parse_counter_response(self, response: str) -> CounterOut:
        """Parse natural language counter response"""
        counter_points = []
        missing_signals = []
        citations = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'REASON' in line.upper() or 'COUNTER' in line.upper():
                current_section = 'counter'
            elif 'MISSING' in line.upper() or 'SIGNAL' in line.upper():
                current_section = 'missing'
            elif 'CITATION' in line.upper() or 'SOURCE' in line.upper():
                current_section = 'citations'
            elif line.startswith('-') or line.startswith('•'):
                content = line.lstrip('-•').strip()
                if content and current_section == 'counter':
                    counter_points.append(content)
                elif content and current_section == 'missing':
                    missing_signals.append(content)
                elif content and current_section == 'citations':
                    citations.append(content)
        
        return CounterOut(counter_points=counter_points, missing_signals=missing_signals, citations=citations)
    
    def _parse_judge_response(self, response: str, make_decision: bool) -> JudgeOut:
        """Parse natural language judge response"""
        confidence = 0.5
        decision = None
        notes = ""
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if 'CONFIDENCE' in line.upper():
                if 'HIGH' in line.upper():
                    confidence = 0.9
                elif 'MEDIUM' in line.upper():
                    confidence = 0.6
                elif 'LOW' in line.upper():
                    confidence = 0.3
            elif 'DECISION' in line.upper():
                if 'YES' in line.upper():
                    decision = True
                elif 'NO' in line.upper():
                    decision = False
            elif 'REASON' in line.upper():
                # Get everything after REASON:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    notes = parts[1].strip()
        
        return JudgeOut(
            confidence=confidence,
            notes=notes or response[:200],
            llm_decision=decision if make_decision else None
        )
    
    async def finder(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> FinderOut:
        """Find compliance signals and regulations"""
        
        if settings.use_rag:
            # Use simplified RAG for comprehensive analysis
            rag = get_rag_system()
            result = rag.simplified_rag.compliance_finder(
                artifact.title, artifact.description, artifact.docs,
                artifact.code_hints, artifact.tags
            )
            
            # Convert RAG result to FinderOut format
            return FinderOut(
                signals=result.get("signals", []),
                claims=result.get("claims", []),
                citations=result.get("citations", [])
            )
        else:
            # Direct LLM call without RAG (faster but less context-aware)
            prompt = f"""Feature: {artifact.title}
Description: {artifact.description}
Tags: {', '.join(artifact.tags) if artifact.tags else 'none'}

Does this feature need geographical compliance? List:
- SIGNALS: Compliance indicators found
- CLAIMS: Relevant regulations
- CITATIONS: Sources"""
            
            messages = [{"role": "user", "content": prompt}]
            # Use faster model for Direct mode
            response = await self.call_openai(messages, model=self.direct_model)
            
            try:
                content = response["choices"][0]["message"]["content"]
                return self._parse_finder_response(content)
            except (KeyError, Exception) as e:
                print(f"Error parsing finder response: {e}")
                return FinderOut(signals=[], claims=[], citations=[])
    
    async def counter(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> CounterOut:
        """Find counter-arguments and missing signals"""
        
        if settings.use_rag:
            # Use simplified RAG for comprehensive counter-analysis
            rag = get_rag_system()
            result = rag.simplified_rag.compliance_counter(
                artifact.title, artifact.description, artifact.docs,
                artifact.code_hints, artifact.tags
            )
            
            # Convert RAG result to CounterOut format
            return CounterOut(
                counter_points=result.get("counter_points", []),
                missing_signals=result.get("missing_signals", []),
                citations=result.get("citations", [])
            )
        else:
            # Direct LLM call without RAG
            prompt = f"""Feature: {artifact.title}
Description: {artifact.description}

Why might this NOT need compliance? List:
- COUNTER POINTS: Reasons compliance may not apply
- MISSING SIGNALS: What indicators are absent
- CITATIONS: Sources"""
            
            messages = [{"role": "user", "content": prompt}]
            # Use faster model for Direct mode
            response = await self.call_openai(messages, model=self.direct_model)
            
            try:
                content = response["choices"][0]["message"]["content"]
                return self._parse_counter_response(content)
            except (KeyError, Exception) as e:
                print(f"Error parsing counter response: {e}")
                return CounterOut(counter_points=[], missing_signals=[], citations=[])
    
    async def judge(self, artifact: FeatureArtifact, finder_out: FinderOut, counter_out: CounterOut, make_decision: bool = False) -> JudgeOut:
        """Make final compliance decision"""
        
        if settings.use_rag:
            # Use simplified RAG for comprehensive judge analysis
            rag = get_rag_system()
            result = rag.simplified_rag.compliance_judge(
                artifact.title, artifact.description,
                finder_out.signals, finder_out.claims,
                counter_out.counter_points, counter_out.missing_signals,
                make_decision=make_decision
            )
            
            # Combine signals from finder and counter analysis as fallback
            all_signals = list(set(finder_out.signals + counter_out.missing_signals))
            
            # Create JudgeOut object
            judge_out = JudgeOut(
                signals=result.get("signals", all_signals),
                notes=result.get("notes", "RAG analysis completed"),
                confidence=result.get("confidence", 0.5)
            )
            
            # If LLM is making decision, store it in the llm_decision field
            if make_decision and "requires_compliance" in result:
                judge_out.llm_decision = result.get("requires_compliance", False)
            
            return judge_out
        else:
            # Direct LLM call without RAG
            all_signals = list(set(finder_out.signals + counter_out.missing_signals))
            
            prompt = f"""Feature: {artifact.title}
FOR compliance: {', '.join(finder_out.signals[:3]) if finder_out.signals else 'none'}
AGAINST compliance: {', '.join(counter_out.counter_points[:3]) if counter_out.counter_points else 'none'}

Does this need compliance? Answer:
- CONFIDENCE: High/Medium/Low
- DECISION: Yes/No
- REASON: Brief explanation"""
            
            messages = [{"role": "user", "content": prompt}]
            # Use faster model for Direct mode
            response = await self.call_openai(messages, model=self.direct_model)
            
            try:
                content = response["choices"][0]["message"]["content"]
                parsed = self._parse_judge_response(content, make_decision)
                
                judge_out = JudgeOut(
                    signals=all_signals,
                    notes=parsed.notes,
                    confidence=parsed.confidence
                )
                
                if make_decision:
                    judge_out.llm_decision = parsed.llm_decision
                
                return judge_out
            except (KeyError, Exception) as e:
                print(f"Error parsing judge response: {e}")
                return JudgeOut(
                    signals=all_signals,
                    notes="Analysis completed",
                    confidence=0.5,
                    llm_decision=False if make_decision else None
                )

# Lazy initialization for LLM client
_llm_client = None

def get_llm_client():
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

# Simplified RAG System
class RAGSystem:
    def __init__(self):
        if not RAG_AVAILABLE:
            raise ImportError("RAG system is required. Please install: pip install langchain-openai langchain-chroma chromadb")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for RAG")
        
        # Initialize Simplified RAG with Chroma
        try:
            from langchain_rag import SimplifiedRAGSystem, SimplifiedRAGSettings
            rag_settings = SimplifiedRAGSettings(
                openai_api_key=settings.openai_api_key,
                chroma_persist_directory=settings.chroma_persist_directory,
                database_path=settings.database_path
            )
            self.simplified_rag = SimplifiedRAGSystem(settings=rag_settings)
            print("✅ Simplified RAG initialized successfully - using Chroma vector search")
        except Exception as e:
            print(f"❌ RAG initialization failed: {e}")
            raise
        
        self.chunks = []
    
    def index_documents(self, docs: List[RawDoc]) -> int:
        self.chunks = []
        
        # Create chunks for reference
        for i, doc in enumerate(docs):
            chunk = Chunk(
                id=f"legal_doc_{i}",
                content=doc.content,
                source=doc.url,
                metadata=doc.metadata
            )
            self.chunks.append(chunk)
        
        # Convert to ScrapedDocument format for simplified RAG
        try:
            from langchain_rag import ScrapedDocument
            from datetime import datetime
            
            scraped_docs = []
            for chunk in self.chunks:
                scraped_doc = ScrapedDocument(
                    url=chunk.source,
                    title=chunk.metadata.get('title', f"Legal Document {chunk.id}"),
                    content=chunk.content,
                    source=chunk.metadata.get('source', 'unknown'),
                    regulation=chunk.metadata.get('regulation', 'unknown'),
                    jurisdiction=chunk.metadata.get('jurisdiction', 'unknown'),
                    scraped_at=datetime.now().isoformat(),
                    content_length=len(chunk.content)
                )
                scraped_docs.append(scraped_doc)
            
            # Index into simplified RAG
            import asyncio
            indexed_count = asyncio.run(self.simplified_rag.index_scraped_documents(scraped_docs))
            print(f"📚 Indexed {indexed_count} chunks into simplified RAG system")
            return indexed_count
            
        except Exception as e:
            print(f"❌ Could not index documents into RAG: {e}")
            raise
    
    def retrieve(self, query: str, k: int = 6) -> List[Chunk]:
        try:
            # Use simplified RAG's vector retrieval
            docs = self.simplified_rag.retrieve(query, k)
            
            # Convert back to Chunk format for compatibility
            relevant_chunks = []
            for doc in docs:
                chunk = Chunk(
                    id=f"rag_{len(relevant_chunks)}",
                    content=doc.page_content,
                    source=doc.metadata.get('url', 'unknown'),
                    metadata=doc.metadata
                )
                relevant_chunks.append(chunk)
            
            print(f"🔍 Simplified RAG found {len(relevant_chunks)} relevant legal documents")
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ RAG retrieval failed: {e}")
            return []
    
    
    def hydrate_citations(self, chunk_ids: List[str]) -> List[Citation]:
        citations = []
        # If no specific chunk_ids provided, use all chunks
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
                self.exa_client = ExaSDKClient()
                print("✅ Exa SDK client initialized")
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
    
    async def refresh_corpus_for_regulations(self, regulations: List[Dict[str, str]], force_refresh: bool = False) -> Dict[str, Any]:
        """Refresh the corpus with content for multiple regulations using enhanced scraping"""
        
        # Use LangChain RAG system with full document scraping
        return await self._refresh_with_langchain_rag(regulations, force_refresh=force_refresh)
    
    async def _refresh_with_langchain_rag(self, regulations: List[Dict[str, str]], force_refresh: bool = False) -> Dict[str, Any]:
        """Enhanced refresh using LangChain RAG with full document scraping"""
        sources_count = {}
        total_indexed = 0
        
        for reg in regulations:
            name = reg.get("name", "")
            jurisdiction = reg.get("jurisdiction", "")
            
            if not name:
                continue
                
            refresh_mode = "force refresh" if force_refresh else "smart refresh"
            print(f"\n📋 Processing with LangChain RAG ({refresh_mode}): {name} ({jurisdiction})")
            
            try:
                # Use simplified RAG to find URLs, scrape, and index documents
                rag = get_rag_system()
                
                # Prepare search clients list
                search_clients = []
                if self.perplexity_client:
                    search_clients.append(self.perplexity_client)
                if self.exa_client:
                    search_clients.append(self.exa_client)
                
                indexed_count = await rag.simplified_rag.index_regulation_from_search_apis(
                    name, jurisdiction, search_clients, force_refresh=force_refresh, skip_indexing=settings.skip_indexing
                )
                sources_count[f"{name}_{jurisdiction}"] = indexed_count
                total_indexed += indexed_count
                
            except Exception as e:
                print(f"⚠️  RAG processing failed for {name}: {e}")
                sources_count[f"{name}_{jurisdiction}"] = 0
        
        return {
            "ingested": total_indexed,
            "regulations_processed": len(regulations),
            "sources": sources_count,
            "system": "simplified_rag",
            "force_refresh": force_refresh
        }
    
    async def _refresh_with_summaries(self, regulations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fallback refresh using summaries/snippets (original approach)"""
        all_docs = []
        sources_count = {}
        
        for reg in regulations:
            name = reg.get("name", "")
            jurisdiction = reg.get("jurisdiction", "")
            
            if not name:
                continue
                
            print(f"\n📋 Researching (summary mode): {name} ({jurisdiction})")
            regulation_docs = await self.search_regulation(name, jurisdiction)
            all_docs.extend(regulation_docs)
            
            sources_count[f"{name}_{jurisdiction}"] = len(regulation_docs)
        
        # Index all documents into the RAG system
        if all_docs:
            indexed_count = get_rag_system().index_documents(all_docs)
            print(f"\n📚 Successfully indexed {indexed_count} documents from {len(sources_count)} regulations")
        
        return {
            "ingested": len(all_docs),
            "regulations_processed": len(sources_count),
            "sources": sources_count,
            "system": "simplified_rag"
        }
    
    async def close(self):
        """Close all clients"""
        if self.perplexity_client:
            await self.perplexity_client.close()
        if self.exa_client and hasattr(self.exa_client, 'close'):
            await self.exa_client.close()

# Lazy initialization for systems
_rag_system = None
_scraping_aggregator = None

def get_rag_system():
    global _rag_system
    if _rag_system is None:
        print("🔄 Initializing RAG system (lazy load)...")
        _rag_system = RAGSystem()
        print("✅ RAG system initialized")
    return _rag_system

def get_scraping_aggregator():
    global _scraping_aggregator
    if _scraping_aggregator is None:
        print("🔄 Initializing scraping aggregator (lazy load)...")
        _scraping_aggregator = ScrapingAggregator()
        print("✅ Scraping aggregator initialized")
    return _scraping_aggregator

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

# Lazy initialization for evidence system
_evidence_system = None

def get_evidence_system():
    global _evidence_system
    if _evidence_system is None:
        _evidence_system = EvidenceSystem()
    return _evidence_system

# Core Analysis Function
async def analyze(artifact: FeatureArtifact) -> Decision:
    # Extract signals using pattern matching
    sigs = get_signal_extractor().extract_signals(artifact)
    
    # Log which mode we're using
    mode = "LangChain RAG" if settings.use_rag else "Direct LLM"
    print(f"🤖 Using {mode} for compliance analysis of {artifact.feature_id}")
    
    # For backward compatibility, pass empty chunks since LLMClient now uses RAG internally
    empty_chunks = []
    
    # Run LLM ensemble analysis
    llm_client = get_llm_client()
    finder_out = await llm_client.finder(artifact, empty_chunks)
    counter_out = await llm_client.counter(artifact, empty_chunks)
    
    # Toggle: LLM vs Rules Engine decision
    use_llm_decision = not settings.use_rules_engine
    judge_out = await llm_client.judge(artifact, finder_out, counter_out, make_decision=use_llm_decision)
    
    # Decision logic based on toggle
    if use_llm_decision:
        # LLM makes the final decision
        needs_compliance = judge_out.llm_decision if judge_out.llm_decision is not None else False
        reasoning = judge_out.notes
        matched_rules = ["SIMPLIFIED_RAG_DECISION"]
        
        # Extract regulations from finder claims
        regulations = []
        for claim in finder_out.claims:
            if isinstance(claim, dict) and "regulation" in claim:
                regulations.append(claim["regulation"])
        
    else:
        # Rules engine makes the final decision (original behavior)
        text = f"{artifact.title} {artifact.description}"
        verdict = get_rules_engine().evaluate(sigs, text)
        needs_compliance = verdict.ok
        reasoning = verdict.reason
        regulations = verdict.regulations
        matched_rules = verdict.matched_ids
    
    # Combine all signals from pattern matching and LangChain RAG
    all_signals = list(set(sigs.to_list() + judge_out.signals))
    
    # Create citations from finder results
    citations = []
    for citation_ref in finder_out.citations[:3]:
        citations.append(Citation(
            source=citation_ref,
            snippet="RAG retrieved document"
        ))
    
    # Create decision
    decision = Decision(
        feature_id=artifact.feature_id,
        needs_geo_compliance=needs_compliance,
        reasoning=reasoning,
        regulations=regulations,
        signals=all_signals,
        citations=citations,
        confidence=judge_out.confidence,
        matched_rules=matched_rules,
        ts=get_utc_timestamp(),
        policy_version=settings.policy_version
    )
    
    # Write receipt and set hash
    decision.hash = get_evidence_system().write_receipt(decision)
    
    # Store in database if using RAG
    if settings.use_rag:
        try:
            rag = get_rag_system()
            rag.simplified_rag.store_analysis(
                decision.feature_id, decision.needs_geo_compliance, decision.confidence,
                decision.reasoning, decision.regulations, decision.signals,
                [c.source for c in decision.citations], session_id="main_analysis"
            )
        except Exception as e:
            print(f"⚠️  Failed to store analysis in database: {e}")
    
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
        "mem0_docs": len(get_rag_system().chunks),
        "policy_version": settings.policy_version
    }

@app.get("/api/rag_status")
async def get_rag_status():
    """Get current RAG toggle status"""
    return {
        "use_rag": settings.use_rag,
        "description": "RAG (Retrieval-Augmented Generation) is currently " + ("enabled" if settings.use_rag else "disabled")
    }

@app.post("/api/test_llm")
async def test_llm():
    """Test direct LLM call with simple prompt"""
    from openai import AsyncOpenAI
    import asyncio
    
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    try:
        print("🧪 Testing direct LLM call...")
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-5-2025-08-07",
                messages=[{"role": "user", "content": "Say 'Hello'"}],
                max_completion_tokens=10
            ),
            timeout=5
        )
        
        content = response.choices[0].message.content
        print(f"✅ LLM responded: {content}")
        return {"success": True, "response": content}
    except asyncio.TimeoutError:
        print("⏱️ LLM timeout")
        return {"success": False, "error": "Timeout after 5 seconds"}
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/toggle_rag")
async def toggle_rag(enable: bool = None):
    """Toggle RAG on or off, or explicitly set it"""
    if enable is None:
        settings.use_rag = not settings.use_rag
    else:
        settings.use_rag = enable
    
    status = "enabled" if settings.use_rag else "disabled"
    print(f"🔄 RAG has been {status}")
    
    return {
        "use_rag": settings.use_rag,
        "message": f"RAG has been {status}. This will affect all subsequent analyze calls."
    }

@app.post("/api/analyze")
async def analyze_endpoint(artifact: FeatureArtifact) -> Decision:
    import time
    start_time = time.time()
    
    try:
        mode = "RAG" if settings.use_rag else "Direct"
        print(f"🔍 Starting {mode} analysis for feature: {artifact.feature_id}")
        result = await analyze(artifact)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ {mode} analysis completed for {artifact.feature_id} in {duration:.2f} seconds")
        
        return result
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Analysis failed for {artifact.feature_id} after {duration:.2f} seconds: {str(e)}")
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
    csv_path = get_evidence_system().export_csv(decisions)
    
    return {
        "count": len(decisions),
        "csv_path": csv_path
    }

@app.get("/api/evidence")
async def get_evidence(feature_id: Optional[str] = None):
    try:
        zip_data = get_evidence_system().make_evidence_zip(feature_id)
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
            return {"error": "No regulations configured in inputs.yaml", "ingested": 0}
        
        # Use the scraping aggregator to research all regulations
        scraping = get_scraping_aggregator()
        result = await scraping.refresh_corpus_for_regulations(regulations)
        
        return result
        
    except Exception as e:
        print(f"⚠️  Failed to refresh corpus from inputs.yaml: {e}")
        return {"error": str(e), "ingested": 0}


@app.get("/api/rag_status")
async def get_rag_status():
    """Debug endpoint to check RAG system status"""
    try:
        # Get simplified RAG status
        return {
            "system": "simplified_rag",
            "rag_initialized": True,
            "chunks_available": len(get_rag_system().chunks),
            "vectorstore_available": get_rag_system().simplified_rag.vectorstore is not None,
            "rag_chain_available": get_rag_system().simplified_rag.rag_chain is not None
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "system": "simplified_rag",
            "chunks_available": 0
        }

# Initialize with some sample data
@app.on_event("startup")
async def startup_event():
    # Just initialize the systems without auto-processing
    print("🚀 FastAPI server started - ready to process requests")
    print("📡 Available endpoints:")
    print("   • GET  /api/health - System health check")
    print("   • POST /api/analyze - Single feature analysis")
    print("   • POST /api/bulk_analyze - Bulk feature analysis")
    print("   • GET  /api/evidence - Download evidence ZIP")
    print("   • POST /api/refresh_corpus - Refresh knowledge base")
    print("💡 Use the HTML frontend or call APIs directly")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
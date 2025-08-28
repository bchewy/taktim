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

# LangChain RAG system
try:
    from langchain_rag import LangChainRAGSystem, create_enhanced_rag_system
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Error: LangChain not available. Please install: pip install langchain-openai langchain-pinecone")

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
    pinecone_api_key: str = ""
    rag_topk: int = 6
    policy_version: str = "v0.1.0"
    use_rules_engine: bool = False  # Toggle: True = rules engine decides, False = LLM decides (default)
    skip_indexing: bool = False  # Toggle: True = skip vector store indexing, False = index documents (default)
    skip_scraping: bool = False  # Toggle: True = skip scraping documents, False = scrape documents (default)
    
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

# Real OpenAI LLM Integration
class LLMClient:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM integration")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-5-2025-08-07"  # Using GPT-5 for best compliance reasoning
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_openai(self, messages: List[Dict], model: str = None) -> Dict:
        """Call OpenAI API with retry logic"""
        try:
            total_prompt_length = sum(len(str(msg)) for msg in messages)
            print(f"🤖 Calling OpenAI API with model: {model or self.model}")
            print(f"📝 Message count: {len(messages)}")
            print(f"📏 Total prompt length: {total_prompt_length} chars (~{total_prompt_length//4} tokens)")
            
            # Warning if prompt is too long
            if total_prompt_length > 20000:  # ~5k tokens
                print(f"⚠️  Large prompt detected! May hit token limits.")
            
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                # temperature=1.0,  # GPT-5 only supports default temperature (1.0)
                max_completion_tokens=8000,  # Further increased token limit for GPT-5
                response_format={"type": "json_object"}  # Required for structured output
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
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    async def finder(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> FinderOut:
        """Find compliance signals and regulations using GPT-4"""
        
        # Prepare context from retrieved chunks (reduced for token limits)
        context = "\n\n".join([
            f"Source: {chunk.metadata.get('source', 'unknown')}\n"
            f"Content: {chunk.content[:500]}...\n"  # Truncate each chunk to 500 chars
            f"Metadata: {chunk.metadata}"
            for chunk in chunks[:5]  # Limit to top 5 chunks to stay within token limits
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are a legal compliance expert analyzing software features for geographical regulatory compliance. Your job is to find compliance signals and identify relevant regulations based on legal documents provided as context."
            },
            {
                "role": "user", 
                "content": f"""Analyze this software feature for geographical compliance requirements:

**Feature:** {artifact.title}
**Description:** {artifact.description}
**Documentation:** {' '.join(artifact.docs)}
**Code Hints:** {' '.join(artifact.code_hints)}
**Tags:** {', '.join(artifact.tags)}

**Legal Context:**
{context}

Based on the legal context provided, identify:
1. Compliance signals (keywords/concepts that suggest regulatory requirements)
2. Specific regulations that may apply
3. Why each regulation applies
4. Citations to specific chunks that support your analysis

Return your analysis as JSON with this structure:
{{
  "signals": ["list of compliance signals found"],
  "claims": [
    {{
      "regulation": "regulation name", 
      "why": "explanation why this regulation applies",
      "citations": ["chunk reference"]
    }}
  ],
  "citations": ["list of all chunk references used"]
}}"""
            }
        ]
        
        try:
            response = await self.call_openai(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Debug: print the raw response
            print(f"🔍 Finder raw response: {content[:200]}...")
            
            if not content or content.strip() == "":
                print("⚠️  Empty response from LLM")
                return FinderOut(signals=[], claims=[], citations=[])
            
            result = json.loads(content)
            
            return FinderOut(
                signals=result.get("signals", []),
                claims=result.get("claims", []),
                citations=result.get("citations", [])
            )
        except json.JSONDecodeError as e:
            print(f"Finder JSON decode error: {e}")
            print(f"Raw response: {content}")
            return FinderOut(signals=[], claims=[], citations=[])
        except Exception as e:
            print(f"Finder LLM call failed: {e}")
            return FinderOut(signals=[], claims=[], citations=[])
    
    async def counter(self, artifact: FeatureArtifact, chunks: List[Chunk]) -> CounterOut:
        """Find counter-arguments and missing signals using GPT-4"""
        
        context = "\n\n".join([
            f"Source: {chunk.metadata.get('source', 'unknown')}\n"
            f"Content: {chunk.content[:500]}...\n"  # Truncate each chunk to 500 chars
            f"Metadata: {chunk.metadata}"
            for chunk in chunks[:5]  # Limit to top 5 chunks to stay within token limits
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are a legal compliance expert. Your job is to find counter-arguments and identify missing compliance signals that might suggest a feature does NOT require geographical regulatory compliance."
            },
            {
                "role": "user",
                "content": f"""Analyze this software feature for potential exemptions or counter-arguments to geographical compliance:

**Feature:** {artifact.title}
**Description:** {artifact.description}
**Documentation:** {' '.join(artifact.docs)}
**Code Hints:** {' '.join(artifact.code_hints)}
**Tags:** {', '.join(artifact.tags)}

**Legal Context:**
{context}

Find counter-arguments and missing signals that might suggest this feature does NOT require geographical compliance:
1. Counter-points (arguments against compliance requirements)
2. Missing signals (compliance indicators that are notably absent)
3. Citations supporting your counter-analysis

Return as JSON:
{{
  "counter_points": ["list of arguments against compliance requirements"],
  "missing_signals": ["list of compliance signals that are notably missing"],
  "citations": ["list of chunk references"]
}}"""
            }
        ]
        
        try:
            response = await self.call_openai(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Debug: print the raw response
            print(f"🔄 Counter raw response: {content[:200]}...")
            
            if not content or content.strip() == "":
                print("⚠️  Empty response from Counter LLM")
                return CounterOut(counter_points=[], missing_signals=[], citations=[])
            
            result = json.loads(content)
            
            return CounterOut(
                counter_points=result.get("counter_points", []),
                missing_signals=result.get("missing_signals", []),
                citations=result.get("citations", [])
            )
        except json.JSONDecodeError as e:
            print(f"Counter JSON decode error: {e}")
            print(f"Raw response: {content}")
            return CounterOut(counter_points=[], missing_signals=[], citations=[])
        except Exception as e:
            print(f"Counter LLM call failed: {e}")
            return CounterOut(counter_points=[], missing_signals=[], citations=[])
    
    async def judge(self, artifact: FeatureArtifact, finder_out: FinderOut, counter_out: CounterOut, make_decision: bool = False) -> JudgeOut:
        """Make final compliance decision using GPT-4"""
        
        if make_decision:
            # LLM makes the final decision
            system_msg = "You are a senior legal compliance expert making final decisions on whether software features require geographical regulatory compliance. You must weigh evidence for and against compliance requirements."
            instructions = """**Instructions:**
1. Synthesize all evidence for and against
2. Make a final determination on compliance requirements  
3. Assign a confidence score (0.0-1.0)
4. Combine all relevant signals found
5. Provide clear reasoning

Return as JSON:
{{
  "signals": ["combined list of all relevant signals"],
  "notes": "detailed reasoning for your decision", 
  "confidence": 0.85,
  "requires_compliance": true
}}"""
        else:
            # LLM only analyzes, doesn't decide (original PRD behavior)
            system_msg = "You are a legal compliance expert. Merge findings from compliance analysis. Normalize signals and provide confidence, but do NOT make the final YES/NO decision - that will be handled by a separate rules engine."
            instructions = """**Instructions:**
1. Synthesize all evidence for and against
2. Combine all relevant signals found
3. Assign a confidence score (0.0-1.0) for the analysis quality
4. Provide clear reasoning notes
5. DO NOT make the final compliance decision

Return as JSON:
{{
  "signals": ["combined list of all relevant signals"],
  "notes": "detailed reasoning and analysis",
  "confidence": 0.85
}}"""
        
        messages = [
            {
                "role": "system",
                "content": system_msg
            },
            {
                "role": "user",
                "content": f"""Analyze this software feature for geographical regulatory compliance:

**Feature:** {artifact.title}
**Description:** {artifact.description}

**Evidence FOR compliance (from finder analysis):**
- Signals found: {', '.join(finder_out.signals)}
- Regulatory claims: {json.dumps(finder_out.claims, indent=2)}

**Evidence AGAINST compliance (from counter analysis):**
- Counter-points: {', '.join(counter_out.counter_points)}
- Missing signals: {', '.join(counter_out.missing_signals)}

{instructions}"""
            }
        ]
        
        try:
            response = await self.call_openai(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Debug: print the raw response
            print(f"⚖️  Judge raw response: {content[:200]}...")
            
            if not content or content.strip() == "":
                print("⚠️  Empty response from Judge LLM")
                all_signals = list(set(finder_out.signals + counter_out.missing_signals))
                return JudgeOut(
                    signals=all_signals,
                    notes="Empty response from LLM",
                    confidence=0.0
                )
            
            result = json.loads(content)
            
            # Combine signals from finder and counter analysis
            all_signals = list(set(finder_out.signals + counter_out.missing_signals))
            
            judge_out = JudgeOut(
                signals=result.get("signals", all_signals),
                notes=result.get("notes", "Analysis completed"),
                confidence=result.get("confidence", 0.5)
            )
            
            # If LLM is making decision, store it in the notes for later use
            if make_decision and "requires_compliance" in result:
                judge_out.llm_decision = result.get("requires_compliance", False)
            
            return judge_out
            
        except json.JSONDecodeError as e:
            print(f"Judge JSON decode error: {e}")
            print(f"Raw response: {content}")
            all_signals = list(set(finder_out.signals + counter_out.missing_signals))
            return JudgeOut(
                signals=all_signals,
                notes=f"JSON decode failed: {str(e)}",
                confidence=0.0
            )
        except Exception as e:
            print(f"Judge LLM call failed: {e}")
            # Fallback logic
            all_signals = list(set(finder_out.signals + counter_out.missing_signals))
            return JudgeOut(
                signals=all_signals,
                notes=f"LLM analysis failed: {str(e)}",
                confidence=0.0
            )

# Initialize LLM client
llm_client = LLMClient()

# LangChain RAG System Only
class RAGSystem:
    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required. Please install: pip install langchain-openai langchain-pinecone")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LangChain RAG")
        
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is required for Pinecone vector store")
        
        # Initialize LangChain RAG with Pinecone
        try:
            from langchain_rag import LangChainRAGSystem, LangChainRAGSettings
            rag_settings = LangChainRAGSettings(
                openai_api_key=settings.openai_api_key,
                pinecone_api_key=settings.pinecone_api_key
            )
            self.langchain_rag = LangChainRAGSystem(settings=rag_settings)
            print("✅ LangChain RAG initialized successfully - will use Pinecone vector search")
        except Exception as e:
            print(f"❌ LangChain RAG initialization failed: {e}")
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
        
        # Convert to ScrapedDocument format for LangChain
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
            
            # Index into LangChain RAG
            import asyncio
            indexed_count = asyncio.run(self.langchain_rag.index_scraped_documents(scraped_docs))
            print(f"📚 Indexed {indexed_count} chunks into LangChain RAG system")
            return indexed_count
            
        except Exception as e:
            print(f"❌ Could not index documents into LangChain RAG: {e}")
            raise
    
    def retrieve(self, query: str, k: int = 6) -> List[Chunk]:
        try:
            # Use LangChain's vector retrieval
            docs = self.langchain_rag.retrieve(query, k)
            
            # Convert back to Chunk format for compatibility
            relevant_chunks = []
            for doc in docs:
                chunk = Chunk(
                    id=f"langchain_{len(relevant_chunks)}",
                    content=doc.page_content,
                    source=doc.metadata.get('url', 'unknown'),
                    metadata=doc.metadata
                )
                relevant_chunks.append(chunk)
            
            print(f"🔍 LangChain RAG found {len(relevant_chunks)} relevant legal documents")
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ LangChain retrieval failed: {e}")
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
                # Use LangChain RAG to find URLs, scrape, and index documents
                indexed_count = await rag_system.langchain_rag.index_regulation_from_search_apis(
                    name, jurisdiction, self.perplexity_client, self.exa_client, force_refresh=force_refresh, skip_indexing=settings.skip_indexing
                )
                sources_count[f"{name}_{jurisdiction}"] = indexed_count
                total_indexed += indexed_count
                
            except Exception as e:
                print(f"⚠️  LangChain RAG processing failed for {name}: {e}")
                sources_count[f"{name}_{jurisdiction}"] = 0
        
        return {
            "ingested": total_indexed,
            "regulations_processed": len(regulations),
            "sources": sources_count,
            "system": "langchain_rag",
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
            indexed_count = rag_system.index_documents(all_docs)
            print(f"\n📚 Successfully indexed {indexed_count} documents from {len(sources_count)} regulations")
        
        return {
            "ingested": len(all_docs),
            "regulations_processed": len(sources_count),
            "sources": sources_count,
            "system": "langchain_rag"
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
    
    # Toggle: LLM vs Rules Engine decision
    use_llm_decision = not settings.use_rules_engine
    judge_out = await llm_client.judge(artifact, finder_out, counter_out, make_decision=use_llm_decision)
    
    # Decision logic based on toggle
    if use_llm_decision:
        # LLM makes the final decision
        needs_compliance = judge_out.llm_decision if judge_out.llm_decision is not None else False
        reasoning = judge_out.notes
        regulations = []  # Extract from finder_out.claims if needed
        matched_rules = ["LLM_DECISION"]
        
        # Extract regulations from LLM claims
        for claim in finder_out.claims:
            if isinstance(claim, dict) and "regulation" in claim:
                regulations.append(claim["regulation"])
        
    else:
        # Rules engine makes the final decision (original behavior)
        text = f"{artifact.title} {artifact.description}"
        verdict = rules_engine.evaluate(sigs, text)
        needs_compliance = verdict.ok
        reasoning = verdict.reason
        regulations = verdict.regulations
        matched_rules = verdict.matched_ids
    
    # Create decision
    all_signals = list(set(sigs.to_list() + judge_out.signals))
    decision = Decision(
        feature_id=artifact.feature_id,
        needs_geo_compliance=needs_compliance,
        reasoning=reasoning,
        regulations=regulations,
        signals=all_signals,
        citations=rag_system.hydrate_citations(finder_out.citations[:3]),
        confidence=judge_out.confidence,
        matched_rules=matched_rules,
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

@app.get("/api/rag_status")
async def get_rag_status():
    """Debug endpoint to check RAG system status"""
    try:
        # Get LangChain RAG status
        return {
            "system": "langchain",
            "langchain_initialized": True,
            "chunks_available": len(rag_system.chunks),
            "vectorstore_available": rag_system.langchain_rag.vectorstore is not None,
            "rag_chain_available": rag_system.langchain_rag.rag_chain is not None
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "system": "langchain",
            "chunks_available": len(rag_system.chunks)
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
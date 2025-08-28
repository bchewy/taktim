#!/usr/bin/env python3
"""
Perplexity API Client for Legal Regulation Research
Fetches official government sites and legal sources for compliance analysis
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel

from pydantic_settings import BaseSettings


# Configuration
class PerplexitySettings(BaseSettings):
    perplexity_api_key: str = ""
    perplexity_model: str = "sonar"  # Online search model 
    perplexity_max_tokens: int = 2000
    perplexity_timeout: int = 15
    
    model_config = {"env_file": ".env", "extra": "ignore"}


@dataclass
class PerplexityCitation:
    """Citation from Perplexity search results"""
    title: str
    url: str
    snippet: str
    is_official: bool = False  # Whether this is from an official government/legal source


@dataclass
class PerplexityResult:
    """Result from Perplexity API query"""
    summary: str
    citations: List[PerplexityCitation]
    official_sites: List[str]  # Filtered list of official government/legal URLs
    query: str
    confidence: float = 0.0


class PerplexityClient:
    """Client for Perplexity API to fetch legal regulation information"""
    
    # Official domains for legal/regulatory sources
    OFFICIAL_DOMAINS = {
        # EU/European sources
        'eur-lex.europa.eu',
        'ec.europa.eu', 
        'europa.eu',
        'consilium.europa.eu',
        'europarl.europa.eu',
        'digital-strategy.ec.europa.eu',
        
        # US Federal
        'congress.gov',
        'govinfo.gov', 
        'federalregister.gov',
        'justice.gov',
        'ftc.gov',
        'fcc.gov',
        'sec.gov',
        'cftc.gov',
        'treasury.gov',
        'whitehouse.gov',
        'regulations.gov',
        
        # US States - California
        'leginfo.legislature.ca.gov',
        'oag.ca.gov',
        'gov.ca.gov',
        'cpuc.ca.gov',
        
        # US States - Florida  
        'flsenate.gov',
        'myfloridahouse.gov',
        'myfloridalegal.com',
        'flgov.com',
        
        # US States - Utah
        'le.utah.gov',
        'attorneygeneral.utah.gov',
        'utah.gov',
        
        # US States - New York
        'nysenate.gov',
        'assembly.state.ny.us',
        'ag.ny.gov',
        'ny.gov',
        
        # US States - Texas
        'capitol.texas.gov',
        'statutes.capitol.texas.gov',
        'texasattorneygeneral.gov',
        'texas.gov',
        
        # UK
        'legislation.gov.uk',
        'gov.uk',
        'parliament.uk',
        'ico.org.uk',
        
        # Canada
        'laws-lois.justice.gc.ca',
        'parl.ca',
        'priv.gc.ca',
        'canada.ca',
        
        # International organizations
        'oecd.org',
        'un.org',
        'wto.org',
        'coe.int'
    }
    
    # Keywords that indicate official legal content (must be strong indicators)
    OFFICIAL_INDICATORS = [
        'CFR', 'USC', 'public law', 'federal register',
        'regulation (EU)', 'directive (EU)', 'council regulation',
        'united states code', 'code of federal regulations',
        'official journal', 'federal statute', 'public act',
        'session laws', 'statutes at large'
    ]
    
    def __init__(self, settings: Optional[PerplexitySettings] = None):
        self.settings = settings or PerplexitySettings()
        
        if not self.settings.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY is required")
            
        self.client = httpx.AsyncClient(
            base_url="https://api.perplexity.ai",
            headers={
                "Authorization": f"Bearer {self.settings.perplexity_api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.settings.perplexity_timeout
        )
    
    def _is_official_domain(self, url: str) -> bool:
        """Check if URL is from an official government/legal domain"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.removeprefix('www.')
            
            # Exclude known non-official domains
            excluded_domains = {'wikipedia.org', 'en.wikipedia.org', 'ebu.ch', 'cdt.org', 'didomi.io'}
            if domain in excluded_domains:
                return False
            
            # Direct match
            if domain in self.OFFICIAL_DOMAINS:
                return True
                
            # Check for subdomains of official domains
            for official_domain in self.OFFICIAL_DOMAINS:
                if domain.endswith('.' + official_domain):
                    return True
                    
            return False
        except Exception:
            return False
    
    def _is_official_content(self, title: str, snippet: str) -> bool:
        """Check if content appears to be from official legal source based on keywords"""
        text = f"{title} {snippet}".lower()
        return any(indicator in text for indicator in self.OFFICIAL_INDICATORS)
    
    def _extract_citations_from_response(self, response_data: Dict) -> List[PerplexityCitation]:
        """Extract and classify citations from Perplexity response"""
        citations = []
        
        # Get search results from the response
        search_results = response_data.get('search_results', [])
        
        for result in search_results:
            url = result.get('url', '')
            title = result.get('title', '')
            snippet = title  # Use title as snippet since Perplexity doesn't provide separate snippet
            
            is_official = (
                self._is_official_domain(url) or 
                self._is_official_content(title, snippet)
            )
            
            citations.append(PerplexityCitation(
                title=title,
                url=url,
                snippet=snippet,
                is_official=is_official
            ))
        
        return citations
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    async def _make_request(self, query: str) -> Dict[str, Any]:
        """Make request to Perplexity API with retry logic"""
        
        # Craft a query optimized for finding official legal sources
        enhanced_query = f"""
        Find official government and legal sources for: {query}
        
        Focus on:
        - Official government websites and legal databases
        - Primary legal texts (statutes, regulations, codes)
        - Regulatory agency guidance and enforcement documents
        - Congressional or legislative records
        - Court decisions from official sources
        
        Please prioritize .gov, .eu, and other official domains in your search.
        """
        
        payload = {
            "model": self.settings.perplexity_model,
            "messages": [
                {
                    "role": "user", 
                    "content": enhanced_query
                }
            ],
            "max_tokens": self.settings.perplexity_max_tokens
        }
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    async def answer(self, query: str) -> PerplexityResult:
        """
        Search for official legal sources related to the query
        
        Args:
            query: Legal/regulatory topic to search for
            
        Returns:
            PerplexityResult with summary, citations, and filtered official sites
        """
        try:
            response_data = await self._make_request(query)
            
            # Extract the response content
            choices = response_data.get("choices", [])
            if not choices:
                raise ValueError("No response from Perplexity API")
            
            message = choices[0].get("message", {})
            summary = message.get("content", "")
            
            # Extract citations
            citations = self._extract_citations_from_response(response_data)
            
            # Filter for official sites only
            official_sites = [
                citation.url for citation in citations 
                if citation.is_official and citation.url
            ]
            
            # Remove duplicates while preserving order
            official_sites = list(dict.fromkeys(official_sites))
            
            # Calculate confidence based on number of official sources found
            confidence = min(len(official_sites) * 0.2, 1.0)
            
            return PerplexityResult(
                summary=summary,
                citations=citations,
                official_sites=official_sites,
                query=query,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error in Perplexity search for '{query}': {e}")
            return PerplexityResult(
                summary=f"Error searching for legal information: {str(e)}",
                citations=[],
                official_sites=[],
                query=query,
                confidence=0.0
            )
    
    async def search_regulation(self, regulation_name: str, jurisdiction: str = "") -> PerplexityResult:
        """
        Search for a specific regulation by name and jurisdiction
        
        Args:
            regulation_name: Name of the regulation (e.g., "Digital Services Act", "SB976")
            jurisdiction: Jurisdiction (e.g., "EU", "California", "United States")
            
        Returns:
            PerplexityResult with official sources for the regulation
        """
        if jurisdiction:
            query = f"{regulation_name} {jurisdiction} official text statute regulation"
        else:
            query = f"{regulation_name} official text statute regulation"
            
        return await self.answer(query)
    
    async def search_compliance_topic(self, topic: str, jurisdictions: List[str] = None) -> PerplexityResult:
        """
        Search for compliance requirements on a specific topic across jurisdictions
        
        Args:
            topic: Compliance topic (e.g., "recommender systems", "minors protection", "data privacy")
            jurisdictions: List of jurisdictions to focus on (e.g., ["EU", "California", "US"])
            
        Returns:
            PerplexityResult with relevant official sources
        """
        jurisdiction_text = ""
        if jurisdictions:
            jurisdiction_text = f" in {', '.join(jurisdictions)}"
            
        query = f"{topic} compliance requirements regulations laws{jurisdiction_text} official government sources"
        return await self.answer(query)
    
    async def batch_search(self, queries: List[str]) -> List[PerplexityResult]:
        """
        Perform multiple searches concurrently
        
        Args:
            queries: List of search queries
            
        Returns:
            List of PerplexityResult objects
        """
        tasks = [self.answer(query) for query in queries]
        return await asyncio.gather(*tasks)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Convenience functions for common use cases
async def get_official_regulation_sites(regulation_name: str, jurisdiction: str = "") -> List[str]:
    """
    Quick function to get official sites for a specific regulation
    
    Args:
        regulation_name: Name of the regulation
        jurisdiction: Optional jurisdiction filter
        
    Returns:
        List of official URLs
    """
    client = PerplexityClient()
    try:
        result = await client.search_regulation(regulation_name, jurisdiction)
        return result.official_sites
    finally:
        await client.close()


async def search_legal_topic(topic: str, jurisdictions: List[str] = None) -> PerplexityResult:
    """
    Quick function to search for legal information on a topic
    
    Args:
        topic: Legal/compliance topic
        jurisdictions: Optional list of jurisdictions
        
    Returns:
        PerplexityResult with search results
    """
    client = PerplexityClient()
    try:
        return await client.search_compliance_topic(topic, jurisdictions)
    finally:
        await client.close()


# Example usage and testing
async def main():
    """Example usage of the Perplexity client"""
    
    # Test queries for common regulations
    test_queries = [
        ("EU Digital Services Act", "EU"),
        ("California SB976", "California"), 
        ("COPPA", "United States"),
        ("GDPR", "EU"),
        ("Florida Online Privacy Minors", "Florida")
    ]
    
    client = PerplexityClient()
    
    try:
        for regulation, jurisdiction in test_queries:
            print(f"\n🔍 Searching for: {regulation} ({jurisdiction})")
            result = await client.search_regulation(regulation, jurisdiction)
            
            print(f"📄 Summary: {result.summary[:200]}...")
            print(f"🏛️  Official sites found: {len(result.official_sites)}")
            for site in result.official_sites[:3]:  # Show first 3
                print(f"   • {site}")
            print(f"🎯 Confidence: {result.confidence:.2f}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
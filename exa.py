#!/usr/bin/env python3
"""
Exa.ai API Client for Legal Regulation Research
Fast AI-powered search for official government sites and legal sources
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
class ExaSettings(BaseSettings):
    exa_api_key: str = ""
    exa_num_results: int = 10
    exa_timeout: int = 15
    exa_include_text: bool = True
    
    model_config = {"env_file": ".env", "extra": "ignore"}


@dataclass
class ExaResult:
    """Individual search result from Exa API"""
    title: str
    url: str
    text: str = ""
    summary: str = ""
    published_date: str = ""
    score: float = 0.0
    is_official: bool = False


@dataclass
class ExaSearchResult:
    """Complete search result from Exa API"""
    results: List[ExaResult]
    official_sites: List[str]  # Filtered list of official government/legal URLs
    query: str
    request_id: str = ""
    resolved_search_type: str = ""
    confidence: float = 0.0


class ExaClient:
    """Client for Exa.ai API to perform fast legal regulation searches"""
    
    # Official domains for legal/regulatory sources (same as perplexity.py)
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
    
    # Keywords that indicate official legal content (strict indicators)
    OFFICIAL_INDICATORS = [
        'CFR', 'USC', 'public law', 'federal register',
        'regulation (EU)', 'directive (EU)', 'council regulation',
        'united states code', 'code of federal regulations',
        'official journal', 'federal statute', 'public act',
        'session laws', 'statutes at large'
    ]
    
    def __init__(self, settings: Optional[ExaSettings] = None):
        self.settings = settings or ExaSettings()
        
        if not self.settings.exa_api_key:
            raise ValueError("EXA_API_KEY is required")
            
        self.client = httpx.AsyncClient(
            base_url="https://api.exa.ai",
            headers={
                "x-api-key": self.settings.exa_api_key,
                "Content-Type": "application/json"
            },
            timeout=self.settings.exa_timeout
        )
    
    def _is_official_domain(self, url: str) -> bool:
        """Check if URL is from an official government/legal domain"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.removeprefix('www.')
            
            # Exclude known non-official domains
            excluded_domains = {'wikipedia.org', 'en.wikipedia.org'}
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
    
    def _is_official_content(self, title: str, text: str) -> bool:
        """Check if content appears to be from official legal source based on keywords"""
        content = f"{title} {text}".lower()
        return any(indicator.lower() in content for indicator in self.OFFICIAL_INDICATORS)
    
    def _process_search_results(self, response_data: Dict, query: str) -> ExaSearchResult:
        """Process Exa API response into structured results"""
        results = []
        
        # Extract results from response
        raw_results = response_data.get('results', [])
        
        for raw_result in raw_results:
            url = raw_result.get('url', '')
            title = raw_result.get('title', '')
            text = raw_result.get('text', '')
            summary = raw_result.get('summary', '')
            published_date = raw_result.get('publishedDate', '')
            score = raw_result.get('score', 0.0)
            
            # Determine if this is an official source
            is_official = (
                self._is_official_domain(url) or 
                self._is_official_content(title, text)
            )
            
            results.append(ExaResult(
                title=title,
                url=url,
                text=text,
                summary=summary,
                published_date=published_date,
                score=score,
                is_official=is_official
            ))
        
        # Filter for official sites only
        official_sites = [
            result.url for result in results 
            if result.is_official and result.url
        ]
        
        # Remove duplicates while preserving order
        official_sites = list(dict.fromkeys(official_sites))
        
        # Calculate confidence based on number of official sources found
        confidence = min(len(official_sites) * 0.1, 1.0)
        
        return ExaSearchResult(
            results=results,
            official_sites=official_sites,
            query=query,
            request_id=response_data.get('requestId', ''),
            resolved_search_type=response_data.get('resolvedSearchType', ''),
            confidence=confidence
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Exa API with retry logic"""
        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    async def search(self, query: str, include_domains: List[str] = None, 
                    exclude_domains: List[str] = None, num_results: int = None) -> ExaSearchResult:
        """
        Perform a fast AI-powered search for legal content
        
        Args:
            query: Search query
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            num_results: Number of results to return (default from settings)
            
        Returns:
            ExaSearchResult with search results and filtered official sites
        """
        if num_results is None:
            num_results = self.settings.exa_num_results
        
        # Craft a query optimized for finding official legal sources
        enhanced_query = f"""
        Official government legal regulations and statutes for: {query}
        
        Find primary legal sources, government regulations, official statutes, and regulatory documents.
        Priority: .gov, .eu, official legal databases and government agency sites.
        """
        
        payload = {
            "query": enhanced_query.strip(),
            "num_results": num_results,
            "text": self.settings.exa_include_text,
            "highlights": {"num_sentences": 3, "highlights_per_url": 2} if self.settings.exa_include_text else None
        }
        
        # Add domain filters if provided
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        try:
            response_data = await self._make_request("/search", payload)
            return self._process_search_results(response_data, query)
            
        except Exception as e:
            print(f"Error in Exa search for '{query}': {e}")
            return ExaSearchResult(
                results=[],
                official_sites=[],
                query=query,
                confidence=0.0
            )
    
    async def search_regulation(self, regulation_name: str, jurisdiction: str = "") -> ExaSearchResult:
        """
        Search for a specific regulation by name and jurisdiction
        
        Args:
            regulation_name: Name of the regulation (e.g., "Digital Services Act", "SB976")
            jurisdiction: Jurisdiction (e.g., "EU", "California", "United States")
            
        Returns:
            ExaSearchResult with official sources for the regulation
        """
        if jurisdiction:
            query = f"{regulation_name} {jurisdiction} official statute regulation law"
        else:
            query = f"{regulation_name} official statute regulation law"
        
        # Include only official domains for regulation searches
        official_domain_list = list(self.OFFICIAL_DOMAINS)
        
        return await self.search(
            query=query, 
            include_domains=official_domain_list,
            num_results=15  # Get more results for regulation searches
        )
    
    async def search_compliance_topic(self, topic: str, jurisdictions: List[str] = None) -> ExaSearchResult:
        """
        Search for compliance requirements on a specific topic across jurisdictions
        
        Args:
            topic: Compliance topic (e.g., "recommender systems", "minors protection", "data privacy")
            jurisdictions: List of jurisdictions to focus on (e.g., ["EU", "California", "US"])
            
        Returns:
            ExaSearchResult with relevant official sources
        """
        jurisdiction_text = ""
        if jurisdictions:
            jurisdiction_text = f" {' '.join(jurisdictions)}"
            
        query = f"{topic} compliance requirements regulations laws{jurisdiction_text}"
        
        # Include only official domains for compliance searches
        official_domain_list = list(self.OFFICIAL_DOMAINS)
        
        return await self.search(
            query=query,
            include_domains=official_domain_list,
            num_results=12
        )
    
    async def find_similar_regulations(self, reference_url: str, num_results: int = 8) -> ExaSearchResult:
        """
        Find regulations similar to a reference regulation URL
        
        Args:
            reference_url: URL of a known regulation to find similar ones
            num_results: Number of similar results to return
            
        Returns:
            ExaSearchResult with similar regulation sources
        """
        payload = {
            "url": reference_url,
            "num_results": num_results,
            "text": self.settings.exa_include_text,
            "include_domains": list(self.OFFICIAL_DOMAINS)
        }
        
        try:
            response_data = await self._make_request("/find_similar", payload)
            return self._process_search_results(response_data, f"Similar to {reference_url}")
            
        except Exception as e:
            print(f"Error in Exa find_similar for '{reference_url}': {e}")
            return ExaSearchResult(
                results=[],
                official_sites=[],
                query=f"Similar to {reference_url}",
                confidence=0.0
            )
    
    async def answer(self, query: str) -> Dict[str, Any]:
        """
        Generate an AI answer with citations for a legal question
        
        Args:
            query: Legal question or topic
            
        Returns:
            Dictionary with answer text and citations
        """
        enhanced_query = f"Legal regulations and compliance requirements for: {query}"
        
        payload = {
            "query": enhanced_query,
            "text": True
        }
        
        try:
            response_data = await self._make_request("/answer", payload)
            return response_data
            
        except Exception as e:
            print(f"Error in Exa answer for '{query}': {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": []
            }
    
    async def batch_search(self, queries: List[str]) -> List[ExaSearchResult]:
        """
        Perform multiple searches concurrently
        
        Args:
            queries: List of search queries
            
        Returns:
            List of ExaSearchResult objects
        """
        tasks = [self.search(query) for query in queries]
        return await asyncio.gather(*tasks)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Convenience functions for common use cases
async def get_official_regulation_sites_exa(regulation_name: str, jurisdiction: str = "") -> List[str]:
    """
    Quick function to get official sites for a specific regulation using Exa
    
    Args:
        regulation_name: Name of the regulation
        jurisdiction: Optional jurisdiction filter
        
    Returns:
        List of official URLs
    """
    client = ExaClient()
    try:
        result = await client.search_regulation(regulation_name, jurisdiction)
        return result.official_sites
    finally:
        await client.close()


async def search_legal_topic_exa(topic: str, jurisdictions: List[str] = None) -> ExaSearchResult:
    """
    Quick function to search for legal information on a topic using Exa
    
    Args:
        topic: Legal/compliance topic
        jurisdictions: Optional list of jurisdictions
        
    Returns:
        ExaSearchResult with search results
    """
    client = ExaClient()
    try:
        return await client.search_compliance_topic(topic, jurisdictions)
    finally:
        await client.close()


# Example usage and testing
async def main():
    """Example usage of the Exa client"""
    
    # Test queries for common regulations
    test_queries = [
        ("EU Digital Services Act", "EU"),
        ("California SB976", "California"), 
        ("COPPA", "United States"),
        ("GDPR", "EU"),
        ("Florida Online Privacy Minors", "Florida")
    ]
    
    client = ExaClient()
    
    try:
        for regulation, jurisdiction in test_queries:
            print(f"\n🔍 Searching with Exa: {regulation} ({jurisdiction})")
            result = await client.search_regulation(regulation, jurisdiction)
            
            print(f"📄 Found {len(result.results)} total results")
            print(f"🏛️  Official sites found: {len(result.official_sites)}")
            for site in result.official_sites[:3]:  # Show first 3
                print(f"   • {site}")
            print(f"🎯 Confidence: {result.confidence:.2f}")
            print(f"🔬 Search type: {result.resolved_search_type}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
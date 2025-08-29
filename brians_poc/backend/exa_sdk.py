#!/usr/bin/env python3
"""
Exa.ai SDK Client for Legal Regulation Research
Enhanced version using the official Exa Python SDK for optimal performance
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse

from exa_py import Exa
from pydantic_settings import BaseSettings


# Configuration
class ExaSDKSettings(BaseSettings):
    exa_api_key: str = ""
    exa_num_results: int = 10
    exa_include_text: bool = True
    
    model_config = {"env_file": ".env", "extra": "ignore"}


@dataclass
class ExaSDKResult:
    """Individual search result from Exa SDK"""
    title: str
    url: str
    text: str = ""
    summary: str = ""
    published_date: str = ""
    score: float = 0.0
    is_official: bool = False


@dataclass
class ExaSDKSearchResult:
    """Complete search result from Exa SDK"""
    results: List[ExaSDKResult]
    official_sites: List[str]  # Filtered list of official government/legal URLs
    query: str
    autoprompt_string: str = ""
    confidence: float = 0.0


class ExaSDKClient:
    """Enhanced client using the official Exa SDK for fast legal regulation searches"""
    
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
    
    # Keywords that indicate official legal content (strict indicators)
    OFFICIAL_INDICATORS = [
        'CFR', 'USC', 'public law', 'federal register',
        'regulation (EU)', 'directive (EU)', 'council regulation',
        'united states code', 'code of federal regulations',
        'official journal', 'federal statute', 'public act',
        'session laws', 'statutes at large'
    ]
    
    def __init__(self, settings: Optional[ExaSDKSettings] = None):
        self.settings = settings or ExaSDKSettings()
        
        if not self.settings.exa_api_key:
            raise ValueError("EXA_API_KEY is required")
        
        # Initialize the official Exa client
        self.exa = Exa(api_key=self.settings.exa_api_key)
    
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
    
    def _process_search_results(self, exa_result, query: str) -> ExaSDKSearchResult:
        """Process Exa SDK response into structured results"""
        results = []
        
        # Extract results from Exa response
        for result in exa_result.results:
            url = result.url
            title = result.title
            text = getattr(result, 'text', '')
            summary = getattr(result, 'summary', '')
            published_date = getattr(result, 'published_date', '')
            score = getattr(result, 'score', 0.0)
            
            # Determine if this is an official source
            is_official = (
                self._is_official_domain(url) or 
                self._is_official_content(title, text)
            )
            
            results.append(ExaSDKResult(
                title=title,
                url=url,
                text=text,
                summary=summary,
                published_date=str(published_date) if published_date else "",
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
        
        return ExaSDKSearchResult(
            results=results,
            official_sites=official_sites,
            query=query,
            autoprompt_string=getattr(exa_result, 'autoprompt_string', ''),
            confidence=confidence
        )
    
    async def search(self, query: str, include_domains: List[str] = None, 
                    exclude_domains: List[str] = None, num_results: int = None) -> ExaSDKSearchResult:
        """
        Perform a fast AI-powered search for legal content using Exa SDK
        
        Args:
            query: Search query
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            num_results: Number of results to return (default from settings)
            
        Returns:
            ExaSDKSearchResult with search results and filtered official sites
        """
        if num_results is None:
            num_results = self.settings.exa_num_results
        
        # Craft a query optimized for finding official legal sources
        enhanced_query = f"Official government legal regulations and statutes for: {query}"
        
        try:
            # Use search_and_contents for better results with text content
            if self.settings.exa_include_text:
                exa_result = self.exa.search_and_contents(
                    query=enhanced_query,
                    num_results=num_results,
                    text=True,
                    highlights={"num_sentences": 3, "highlights_per_url": 2},
                    include_domains=include_domains or list(self.OFFICIAL_DOMAINS),
                    exclude_domains=exclude_domains,
                    use_autoprompt=True
                )
            else:
                exa_result = self.exa.search(
                    query=enhanced_query,
                    num_results=num_results,
                    include_domains=include_domains or list(self.OFFICIAL_DOMAINS),
                    exclude_domains=exclude_domains,
                    use_autoprompt=True
                )
            
            return self._process_search_results(exa_result, query)
            
        except Exception as e:
            print(f"Error in Exa SDK search for '{query}': {e}")
            return ExaSDKSearchResult(
                results=[],
                official_sites=[],
                query=query,
                confidence=0.0
            )
    
    async def search_regulation(self, regulation_name: str, jurisdiction: str = "") -> ExaSDKSearchResult:
        """
        Search for a specific regulation by name and jurisdiction using Exa SDK
        
        Args:
            regulation_name: Name of the regulation (e.g., "Digital Services Act", "SB976")
            jurisdiction: Jurisdiction (e.g., "EU", "California", "United States")
            
        Returns:
            ExaSDKSearchResult with official sources for the regulation
        """
        if jurisdiction:
            query = f"{regulation_name} {jurisdiction} official statute regulation law"
        else:
            query = f"{regulation_name} official statute regulation law"
        
        return await self.search(
            query=query, 
            num_results=15  # Get more results for regulation searches
        )
    
    async def search_compliance_topic(self, topic: str, jurisdictions: List[str] = None) -> ExaSDKSearchResult:
        """
        Search for compliance requirements on a specific topic across jurisdictions
        
        Args:
            topic: Compliance topic (e.g., "recommender systems", "minors protection", "data privacy")
            jurisdictions: List of jurisdictions to focus on (e.g., ["EU", "California", "US"])
            
        Returns:
            ExaSDKSearchResult with relevant official sources
        """
        jurisdiction_text = ""
        if jurisdictions:
            jurisdiction_text = f" {' '.join(jurisdictions)}"
            
        query = f"{topic} compliance requirements regulations laws{jurisdiction_text}"
        
        return await self.search(
            query=query,
            num_results=12
        )
    
    async def find_similar_regulations(self, reference_url: str, num_results: int = 8) -> ExaSDKSearchResult:
        """
        Find regulations similar to a reference regulation URL using Exa SDK
        
        Args:
            reference_url: URL of a known regulation to find similar ones
            num_results: Number of similar results to return
            
        Returns:
            ExaSDKSearchResult with similar regulation sources
        """
        try:
            if self.settings.exa_include_text:
                exa_result = self.exa.find_similar_and_contents(
                    url=reference_url,
                    num_results=num_results,
                    text=True,
                    include_domains=list(self.OFFICIAL_DOMAINS)
                )
            else:
                exa_result = self.exa.find_similar(
                    url=reference_url,
                    num_results=num_results,
                    include_domains=list(self.OFFICIAL_DOMAINS)
                )
            
            return self._process_search_results(exa_result, f"Similar to {reference_url}")
            
        except Exception as e:
            print(f"Error in Exa SDK find_similar for '{reference_url}': {e}")
            return ExaSDKSearchResult(
                results=[],
                official_sites=[],
                query=f"Similar to {reference_url}",
                confidence=0.0
            )
    
    async def answer(self, query: str) -> Dict[str, Any]:
        """
        Generate an AI answer with citations for a legal question using Exa SDK
        
        Args:
            query: Legal question or topic
            
        Returns:
            Dictionary with answer text and citations
        """
        enhanced_query = f"Legal regulations and compliance requirements for: {query}"
        
        try:
            # Use the answer method from Exa SDK
            answer_result = self.exa.answer(
                query=enhanced_query,
                text=True
            )
            
            return {
                "answer": answer_result.answer,
                "citations": [citation.url for citation in answer_result.citations if hasattr(citation, 'url')]
            }
            
        except Exception as e:
            print(f"Error in Exa SDK answer for '{query}': {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": []
            }
    
    async def batch_search(self, queries: List[str]) -> List[ExaSDKSearchResult]:
        """
        Perform multiple searches concurrently using Exa SDK
        
        Args:
            queries: List of search queries
            
        Returns:
            List of ExaSDKSearchResult objects
        """
        tasks = [self.search(query) for query in queries]
        return await asyncio.gather(*tasks)


# Convenience functions for common use cases
async def get_official_regulation_sites_exa_sdk(regulation_name: str, jurisdiction: str = "") -> List[str]:
    """
    Quick function to get official sites for a specific regulation using Exa SDK
    
    Args:
        regulation_name: Name of the regulation
        jurisdiction: Optional jurisdiction filter
        
    Returns:
        List of official URLs
    """
    client = ExaSDKClient()
    result = await client.search_regulation(regulation_name, jurisdiction)
    return result.official_sites


async def search_legal_topic_exa_sdk(topic: str, jurisdictions: List[str] = None) -> ExaSDKSearchResult:
    """
    Quick function to search for legal information on a topic using Exa SDK
    
    Args:
        topic: Legal/compliance topic
        jurisdictions: Optional list of jurisdictions
        
    Returns:
        ExaSDKSearchResult with search results
    """
    client = ExaSDKClient()
    return await client.search_compliance_topic(topic, jurisdictions)


# Example usage and testing
async def main():
    """Example usage of the Exa SDK client"""
    
    # Test queries for common regulations
    test_queries = [
        ("EU Digital Services Act", "EU"),
        ("California SB976", "California"), 
        ("COPPA", "United States"),
        ("GDPR", "EU"),
        ("Florida Online Privacy Minors", "Florida")
    ]
    
    client = ExaSDKClient()
    
    for regulation, jurisdiction in test_queries:
        print(f"\n🔍 Searching with Exa SDK: {regulation} ({jurisdiction})")
        result = await client.search_regulation(regulation, jurisdiction)
        
        print(f"📄 Found {len(result.results)} total results")
        print(f"🏛️  Official sites found: {len(result.official_sites)}")
        for site in result.official_sites[:3]:  # Show first 3
            print(f"   • {site}")
        print(f"🎯 Confidence: {result.confidence:.2f}")
        if result.autoprompt_string:
            print(f"🤖 Autoprompt: {result.autoprompt_string}")


if __name__ == "__main__":
    asyncio.run(main())
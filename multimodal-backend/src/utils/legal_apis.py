"""
Legal API integrations for accessing government legal databases
Provides real-time access to federal regulations and legislative information
"""

import httpx
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

class GovInfoAPI:
    """GovInfo API client for accessing federal regulations"""
    
    def __init__(self):
        self.base_url = "https://api.govinfo.gov"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_regulations(self, query: str, collection: str = "cfr") -> Dict[str, Any]:
        """Search Code of Federal Regulations (CFR)"""
        try:
            params = {
                "query": query,
                "pageSize": 10,
                "offsetMark": "*",
                "collection": collection
            }
            
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"GovInfo API error: {e}")
            return {"results": [], "error": str(e)}
    
    async def get_regulation_details(self, package_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific regulation"""
        try:
            response = await self.client.get(f"{self.base_url}/packages/{package_id}/summary")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"GovInfo regulation details error: {e}")
            return {"error": str(e)}
    
    async def search_privacy_regulations(self) -> List[Dict[str, Any]]:
        """Search for privacy-related federal regulations"""
        privacy_terms = [
            "children privacy protection",
            "data protection", 
            "online privacy",
            "social media regulation",
            "minor protection"
        ]
        
        results = []
        for term in privacy_terms:
            result = await self.search_regulations(term)
            if "results" in result:
                results.extend(result["results"][:3])  # Limit to top 3 per term
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class CongressAPI:
    """Congress.gov API client for legislative information"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.congress.gov/v3"
        self.api_key = api_key or os.getenv("CONGRESS_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            print("Warning: Congress API key not found. Some features may be limited.")
    
    async def search_bills(self, query: str, congress: int = 118) -> Dict[str, Any]:
        """Search for bills in Congress"""
        try:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            params = {
                "query": query,
                "limit": 10,
                "format": "json"
            }
            
            response = await self.client.get(
                f"{self.base_url}/bill/{congress}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"Congress API error: {e}")
            return {"bills": [], "error": str(e)}
    
    async def get_bill_details(self, bill_id: str, congress: int = 118) -> Dict[str, Any]:
        """Get detailed information about a specific bill"""
        try:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            response = await self.client.get(
                f"{self.base_url}/bill/{congress}/{bill_id}",
                headers=headers,
                params={"format": "json"}
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            print(f"Congress bill details error: {e}")
            return {"error": str(e)}
    
    async def search_social_media_bills(self) -> List[Dict[str, Any]]:
        """Search for social media related legislation"""
        social_media_terms = [
            "social media",
            "children online safety", 
            "data privacy",
            "algorithm transparency",
            "content moderation"
        ]
        
        results = []
        for term in social_media_terms:
            result = await self.search_bills(term)
            if "bills" in result:
                results.extend(result["bills"][:2])  # Limit to top 2 per term
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class StateRegulationAPI:
    """Access to state-level regulations (limited free sources)"""
    
    def __init__(self):
        self.state_sources = {
            "california": {
                "base_url": "https://leginfo.legislature.ca.gov",
                "bill_search": "/faces/billSearchClient.xhtml"
            },
            "florida": {
                "base_url": "http://www.leg.state.fl.us",
                "statutes": "/statutes/"
            },
            "utah": {
                "base_url": "https://legislature.utah.gov",
                "code": "/xcode/"
            }
        }
    
    def get_known_state_laws(self) -> Dict[str, Any]:
        """Return curated information about key state laws"""
        return {
            "california_sb976": {
                "name": "California SB976 - Social Media Child Protection",
                "effective_date": "2024-01-01",
                "key_provisions": [
                    "Prohibits targeted advertising to users under 18",
                    "Requires highest privacy settings by default for minors",
                    "Restricts notifications during school and sleep hours",
                    "Requires parental controls for users under 18"
                ],
                "penalties": "Up to $25,000 per affected child",
                "jurisdiction": "California",
                "applies_to": "Social media platforms"
            },
            "florida_opm": {
                "name": "Florida Online Protection for Minors Act",
                "key_provisions": [
                    "Age verification requirements",
                    "Parental consent for users under 16",
                    "Content restrictions for minors"
                ],
                "jurisdiction": "Florida",
                "applies_to": "Online platforms accessible to minors"
            },
            "utah_smra": {
                "name": "Utah Social Media Regulation Act",
                "key_provisions": [
                    "Parental consent requirements",
                    "Time restrictions for minor users",
                    "Access to child's social media accounts for parents"
                ],
                "jurisdiction": "Utah", 
                "applies_to": "Social media companies"
            }
        }


class LegalResearchAggregator:
    """Aggregates legal research from multiple government APIs"""
    
    def __init__(self, congress_api_key: Optional[str] = None):
        self.govinfo = GovInfoAPI()
        self.congress = CongressAPI(congress_api_key)
        self.state_regs = StateRegulationAPI()
    
    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """Comprehensive legal research on a topic"""
        print(f"🔍 Researching legal topic: {topic}")
        
        # Parallel API calls for efficiency
        tasks = [
            self.govinfo.search_regulations(topic),
            self.congress.search_bills(topic)
        ]
        
        try:
            govinfo_results, congress_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(govinfo_results, Exception):
                govinfo_results = {"results": [], "error": str(govinfo_results)}
            if isinstance(congress_results, Exception):
                congress_results = {"bills": [], "error": str(congress_results)}
            
            # Get state law information
            state_laws = self.state_regs.get_known_state_laws()
            
            return {
                "topic": topic,
                "federal_regulations": govinfo_results.get("results", []),
                "congressional_bills": congress_results.get("bills", []),
                "state_laws": state_laws,
                "research_timestamp": datetime.utcnow().isoformat(),
                "sources": ["govinfo.gov", "congress.gov", "state_curated"]
            }
            
        except Exception as e:
            print(f"Legal research error: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "research_timestamp": datetime.utcnow().isoformat()
            }
    
    async def research_social_media_compliance(self) -> Dict[str, Any]:
        """Specialized research for social media platform compliance"""
        topics = [
            "children online privacy",
            "social media minors",
            "content moderation",
            "algorithm transparency",
            "data protection social media"
        ]
        
        results = {}
        for topic in topics:
            results[topic.replace(" ", "_")] = await self.research_topic(topic)
            # Small delay to be respectful to APIs
            await asyncio.sleep(0.5)
        
        return {
            "comprehensive_research": results,
            "summary": f"Researched {len(topics)} key compliance areas",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close all API clients"""
        await self.govinfo.close()
        await self.congress.close()


# Test function
async def test_legal_apis():
    """Test the legal API integrations"""
    print("🧪 Testing Legal APIs...")
    
    aggregator = LegalResearchAggregator()
    
    try:
        # Test basic research
        result = await aggregator.research_topic("children privacy protection")
        print(f"✅ Research completed: {len(result.get('federal_regulations', []))} federal regulations found")
        
        # Test social media specific research
        social_media_result = await aggregator.research_social_media_compliance()
        print(f"✅ Social media research completed: {len(social_media_result.get('comprehensive_research', {}))} topics researched")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
        
    finally:
        await aggregator.close()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_legal_apis())
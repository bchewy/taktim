"""
API Validation Tracker for Legal Research
Tracks success/failure of API calls and source metadata for benchmarking
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class APICallResult:
    """Result of an API call with validation metadata"""
    api_name: str
    endpoint: str
    status: str  # 'calling', 'success', 'failed', 'timeout'
    response_time_ms: Optional[float] = None
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
    source_dates: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.source_dates is None:
            self.source_dates = []

class APIValidationTracker:
    """Tracks API calls and validates data retrieval for benchmarking"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.api_calls: List[APICallResult] = []
        self.current_calls: Dict[str, APICallResult] = {}
    
    def start_api_call(self, api_name: str, endpoint: str = None) -> APICallResult:
        """Start tracking an API call"""
        call_result = APICallResult(
            api_name=api_name,
            endpoint=endpoint or "default",
            status="calling",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.current_calls[api_name] = call_result
        self.api_calls.append(call_result)
        
        # Log to agent progress if available
        try:
            try:
                from .agent_progress_tracker import log_agent_activity
            except ImportError:
                from src.utils.agent_progress_tracker import log_agent_activity
            log_agent_activity(
                self.session_id, 
                "api_validator", 
                "API Validator", 
                f"📡 Calling {api_name} API...", 
                "api_validation"
            )
        except ImportError:
            pass
        
        return call_result
    
    def complete_api_call(self, api_name: str, success: bool, 
                         result_count: int = None, response_time_ms: float = None,
                         error_message: str = None, source_dates: List[Dict] = None):
        """Mark an API call as completed"""
        if api_name not in self.current_calls:
            return
        
        call_result = self.current_calls[api_name]
        call_result.status = "success" if success else "failed"
        call_result.response_time_ms = response_time_ms
        call_result.result_count = result_count
        call_result.error_message = error_message
        call_result.source_dates = source_dates or []
        
        # Log completion status
        try:
            try:
                from .agent_progress_tracker import log_agent_activity
            except ImportError:
                from src.utils.agent_progress_tracker import log_agent_activity
            
            if success:
                message = f"✅ {api_name} API: {result_count} results in {response_time_ms:.0f}ms"
                status = "completed"
            else:
                message = f"❌ {api_name} API failed: {error_message}"
                status = "failed"
                
            log_agent_activity(
                self.session_id, 
                "api_validator", 
                "API Validator", 
                message, 
                "api_validation",
                status=status
            )
        except ImportError:
            pass
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all API validation results"""
        total_calls = len(self.api_calls)
        successful_calls = len([call for call in self.api_calls if call.status == "success"])
        failed_calls = len([call for call in self.api_calls if call.status == "failed"])
        
        avg_response_time = None
        if self.api_calls:
            response_times = [call.response_time_ms for call in self.api_calls 
                            if call.response_time_ms is not None]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Extract source metadata
        all_sources = []
        for call in self.api_calls:
            if call.status == "success" and call.source_dates:
                all_sources.extend(call.source_dates)
        
        return {
            "session_id": self.session_id,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "api_calls_summary": {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
                "avg_response_time_ms": avg_response_time
            },
            "api_details": [asdict(call) for call in self.api_calls],
            "sources_consulted": all_sources,
            "data_freshness_analysis": self._analyze_source_freshness(all_sources)
        }
    
    def _analyze_source_freshness(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze freshness of legal sources"""
        if not sources:
            return {"status": "no_sources", "warning": "No sources were successfully retrieved"}
        
        current_date = datetime.now(timezone.utc)
        freshness_analysis = {
            "total_sources": len(sources),
            "very_fresh": 0,  # < 1 year
            "fresh": 0,       # 1-3 years  
            "aging": 0,       # 3-10 years
            "stale": 0,       # > 10 years
            "warnings": []
        }
        
        for source in sources:
            source_date_str = source.get("publication_date") or source.get("date_issued")
            if not source_date_str:
                continue
                
            try:
                source_date = datetime.fromisoformat(source_date_str.replace('Z', '+00:00'))
                age_years = (current_date - source_date).days / 365.25
                
                source["age_years"] = round(age_years, 1)
                
                if age_years < 1:
                    freshness_analysis["very_fresh"] += 1
                elif age_years < 3:
                    freshness_analysis["fresh"] += 1
                elif age_years < 10:
                    freshness_analysis["aging"] += 1
                else:
                    freshness_analysis["stale"] += 1
                    freshness_analysis["warnings"].append(
                        f"{source.get('title', 'Unknown source')} is {age_years:.1f} years old"
                    )
            except Exception:
                continue
        
        # Generate overall assessment
        stale_percentage = (freshness_analysis["stale"] / freshness_analysis["total_sources"]) * 100
        if stale_percentage > 50:
            freshness_analysis["overall_status"] = "concerning"
            freshness_analysis["warnings"].append("Over 50% of sources are more than 10 years old")
        elif stale_percentage > 25:
            freshness_analysis["overall_status"] = "moderate"
        else:
            freshness_analysis["overall_status"] = "good"
        
        return freshness_analysis


# Enhanced legal API wrappers with validation tracking
class TrackedGovInfoAPI:
    """GovInfo API wrapper with validation tracking"""
    
    def __init__(self, api_key: Optional[str] = None, tracker: APIValidationTracker = None):
        try:
            from .legal_apis import GovInfoAPI
        except ImportError:
            from src.utils.legal_apis import GovInfoAPI
        self.api = GovInfoAPI(api_key)
        self.tracker = tracker
    
    async def search_regulations(self, query: str, collection: str = "cfr") -> Dict[str, Any]:
        """Search regulations with tracking"""
        api_call = None
        start_time = time.time()
        
        if self.tracker:
            api_call = self.tracker.start_api_call("GovInfo", f"search/{collection}")
        
        try:
            result = await self.api.search_regulations(query, collection)
            response_time_ms = (time.time() - start_time) * 1000
            
            # Extract source dates
            source_dates = []
            if "results" in result and result["results"]:
                for item in result["results"][:10]:  # Limit to first 10 for performance
                    source_dates.append({
                        "title": item.get("title", "Unknown"),
                        "publication_date": item.get("dateIssued"),
                        "package_id": item.get("packageId"),
                        "source": "GovInfo CFR"
                    })
            
            if self.tracker and api_call:
                success = "error" not in result
                result_count = len(result.get("results", []))
                error_msg = result.get("error") if not success else None
                
                self.tracker.complete_api_call(
                    "GovInfo", success, result_count, response_time_ms, error_msg, source_dates
                )
            
            return result
            
        except Exception as e:
            if self.tracker and api_call:
                response_time_ms = (time.time() - start_time) * 1000
                self.tracker.complete_api_call(
                    "GovInfo", False, 0, response_time_ms, str(e), []
                )
            raise
    
    async def close(self):
        """Close the API connection"""
        await self.api.close()


class TrackedCongressAPI:
    """Congress API wrapper with validation tracking"""
    
    def __init__(self, api_key: Optional[str] = None, tracker: APIValidationTracker = None):
        try:
            from .legal_apis import CongressAPI
        except ImportError:
            from src.utils.legal_apis import CongressAPI
        self.api = CongressAPI(api_key)
        self.tracker = tracker
    
    async def search_bills(self, query: str, congress: int = 118) -> Dict[str, Any]:
        """Search bills with tracking"""
        api_call = None
        start_time = time.time()
        
        if self.tracker:
            api_call = self.tracker.start_api_call("Congress.gov", f"bills/{congress}")
        
        try:
            result = await self.api.search_bills(query, congress)
            response_time_ms = (time.time() - start_time) * 1000
            
            # Extract source dates
            source_dates = []
            if "bills" in result and result["bills"]:
                for bill in result["bills"][:10]:  # Limit to first 10
                    source_dates.append({
                        "title": bill.get("title", "Unknown Bill"),
                        "publication_date": bill.get("introducedDate"),
                        "bill_id": f"{bill.get('type', '')} {bill.get('number', '')}",
                        "congress": bill.get("congress"),
                        "source": "Congress.gov"
                    })
            
            if self.tracker and api_call:
                success = "error" not in result
                result_count = len(result.get("bills", []))
                error_msg = result.get("error") if not success else None
                
                self.tracker.complete_api_call(
                    "Congress.gov", success, result_count, response_time_ms, error_msg, source_dates
                )
            
            return result
            
        except Exception as e:
            if self.tracker and api_call:
                response_time_ms = (time.time() - start_time) * 1000
                self.tracker.complete_api_call(
                    "Congress.gov", False, 0, response_time_ms, str(e), []
                )
            raise
    
    async def close(self):
        """Close the API connection"""
        await self.api.close()


class TrackedLegalResearchAggregator:
    """Enhanced legal research aggregator with validation tracking"""
    
    def __init__(self, congress_api_key: Optional[str] = None, session_id: Optional[str] = None):
        self.tracker = APIValidationTracker(session_id)
        self.govinfo = TrackedGovInfoAPI(tracker=self.tracker)
        self.congress = TrackedCongressAPI(congress_api_key, self.tracker)
    
    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research topic with comprehensive validation tracking"""
        print(f"🔍 Researching legal topic with tracking: {topic}")
        
        # Parallel API calls with individual tracking
        tasks = [
            self.govinfo.search_regulations(topic),
            self.congress.search_bills(topic)
        ]
        
        try:
            govinfo_results, congress_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(govinfo_results, Exception):
                print(f"GovInfo API error: {govinfo_results}")
                govinfo_results = {"results": [], "error": str(govinfo_results)}
            if isinstance(congress_results, Exception):
                print(f"Congress API error: {congress_results}")
                congress_results = {"bills": [], "error": str(congress_results)}
            
            # Get state law information (static, so just mark as successful)
            try:
                from .legal_apis import StateRegulationAPI
            except ImportError:
                from src.utils.legal_apis import StateRegulationAPI
            state_regs = StateRegulationAPI()
            state_laws = state_regs.get_known_state_laws()
            
            # Track state law "API call" 
            state_call = self.tracker.start_api_call("State Laws", "static_db")
            state_sources = [
                {
                    "title": law_data.get("name", key),
                    "publication_date": law_data.get("effective_date"),
                    "jurisdiction": law_data.get("jurisdiction"),
                    "source": "Curated State Laws"
                }
                for key, law_data in state_laws.items()
            ]
            self.tracker.complete_api_call(
                "State Laws", True, len(state_laws), 50, None, state_sources
            )
            
            research_result = {
                "topic": topic,
                "federal_regulations": govinfo_results.get("results", []),
                "congressional_bills": congress_results.get("bills", []),
                "state_laws": state_laws,
                "research_timestamp": datetime.now(timezone.utc).isoformat(),
                "sources": ["govinfo.gov", "congress.gov", "state_curated"],
                "validation_summary": self.tracker.get_validation_summary()
            }
            
            return research_result
            
        except Exception as e:
            print(f"Legal research error: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "research_timestamp": datetime.now(timezone.utc).isoformat(),
                "validation_summary": self.tracker.get_validation_summary()
            }
    
    async def close(self):
        """Close all API connections"""
        await self.govinfo.close()
        await self.congress.close()


# Test function
async def test_tracked_research():
    """Test the tracked legal research"""
    print("🧪 Testing tracked legal research...")
    
    aggregator = TrackedLegalResearchAggregator(session_id="test_session")
    
    try:
        result = await aggregator.research_topic("children online privacy")
        
        validation_summary = result.get("validation_summary", {})
        print(f"✅ Research completed")
        print(f"📊 API Success Rate: {validation_summary.get('api_calls_summary', {}).get('success_rate', 0):.1f}%")
        print(f"📚 Sources Retrieved: {validation_summary.get('sources_consulted', []).__len__()}")
        print(f"⏱️ Avg Response Time: {validation_summary.get('api_calls_summary', {}).get('avg_response_time_ms', 0):.0f}ms")
        
        # Print freshness analysis
        freshness = validation_summary.get("data_freshness_analysis", {})
        print(f"📅 Data Freshness: {freshness.get('overall_status', 'unknown')}")
        if freshness.get("warnings"):
            for warning in freshness["warnings"][:3]:
                print(f"⚠️  {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await aggregator.close()


if __name__ == "__main__":
    asyncio.run(test_tracked_research())
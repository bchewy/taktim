"""
Enhanced Multimodal Crew with API Validation Tracking
Integrates the benchmarking and source citation system
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
try:
    from .multimodal_crew import MultimodalCrew
except ImportError:
    from multimodal_crew import MultimodalCrew
try:
    from ..utils.api_validation_tracker import TrackedLegalResearchAggregator
except ImportError:
    from src.utils.api_validation_tracker import TrackedLegalResearchAggregator

class EnhancedMultimodalCrew(MultimodalCrew):
    """Enhanced crew with API validation tracking and source citation"""
    
    def __init__(self, session_id: Optional[str] = None):
        super().__init__()
        self.session_id = session_id or f"session_{int(datetime.utcnow().timestamp())}"
        self.validation_aggregator = None
    
    async def analyze_comprehensive_compliance_with_validation(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced comprehensive compliance analysis with validation tracking"""
        
        try:
            # Initialize tracked legal research aggregator
            congress_api_key = os.getenv("CONGRESS_API_KEY")
            self.validation_aggregator = TrackedLegalResearchAggregator(
                congress_api_key=congress_api_key,
                session_id=self.session_id
            )
            
            # Import logging function if available
            try:
                from ..utils.agent_progress_tracker import log_agent_activity
                tracking_enabled = True
            except ImportError:
                tracking_enabled = False
            
            if tracking_enabled:
                log_agent_activity(
                    self.session_id, "multimodal_crew", "Multimodal Crew Lead", 
                    "🎯 Starting enhanced compliance analysis with validation...", "initializing"
                )
            
            # Step 1: Conduct legal research with validation tracking
            if tracking_enabled:
                log_agent_activity(
                    self.session_id, "legal_researcher", "Legal Research Agent", 
                    "🔍 Starting legal research with API validation...", "legal_analysis"
                )
            
            # Determine research topics based on feature
            research_topics = self._determine_research_topics(feature_data)
            
            # Conduct tracked legal research
            legal_research_results = {}
            for topic in research_topics:
                result = await self.validation_aggregator.research_topic(topic)
                legal_research_results[topic.replace(" ", "_")] = result
                
                if tracking_enabled:
                    validation_summary = result.get("validation_summary", {})
                    success_rate = validation_summary.get("api_calls_summary", {}).get("success_rate", 0)
                    sources_count = len(validation_summary.get("sources_consulted", []))
                    
                    log_agent_activity(
                        self.session_id, "legal_researcher", "Legal Research Agent", 
                        f"📊 {topic}: {success_rate:.1f}% API success, {sources_count} sources found", 
                        "legal_analysis"
                    )
            
            if tracking_enabled:
                log_agent_activity(
                    self.session_id, "legal_researcher", "Legal Research Agent", 
                    "✅ Legal research with validation completed!", "legal_analysis", status="completed"
                )
            
            # Step 2: Run original analysis (simplified)
            original_analysis = self.analyze_legal_compliance(feature_data)
            
            # Step 3: Combine validation data with analysis results
            combined_validation = self._combine_validation_results(legal_research_results)
            
            # Enhanced result with validation data
            enhanced_result = {
                "project_id": feature_data.get('project_name', 'Unknown'),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "session_id": self.session_id,
                
                # Original analysis data
                "legal_analysis": original_analysis.get('legal_analysis', 'Analysis completed'),
                "compliance_status": "NEEDS_REVIEW",
                "risk_level": self._determine_enhanced_risk_level(legal_research_results, combined_validation),
                
                # Enhanced with validation data
                "validation_summary": combined_validation,
                "legal_research_results": legal_research_results,
                "api_benchmarking": True,
                "source_citation": True,
                
                # Additional metadata
                "enhanced_analysis": True,
                "features_analyzed": feature_data.get('project_name', 'Unknown Feature')
            }
            
            if tracking_enabled:
                log_agent_activity(
                    self.session_id, "multimodal_crew", "Multimodal Crew Lead", 
                    "🎉 Enhanced analysis with validation completed!", "finalizing", status="completed"
                )
            
            return enhanced_result
            
        except Exception as e:
            print(f"❌ Enhanced analysis failed: {e}")
            # Fallback to original analysis
            return {
                "project_id": feature_data.get('project_name', 'Unknown'),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "error": f"Enhanced analysis failed: {str(e)}",
                "fallback_to_original": True,
                "compliance_status": "ERROR",
                "risk_level": "UNKNOWN",
                "session_id": self.session_id
            }
        
        finally:
            # Clean up
            if self.validation_aggregator:
                await self.validation_aggregator.close()
    
    def _determine_research_topics(self, feature_data: Dict[str, Any]) -> List[str]:
        """Determine what legal topics to research based on feature"""
        description = str(feature_data.get('project_description', '')).lower()
        title = str(feature_data.get('project_name', '')).lower()
        
        content = f"{description} {title}"
        
        topics = []
        
        # Basic topic mapping
        if any(keyword in content for keyword in ['minor', 'child', 'teen', 'kid', 'age']):
            topics.append("children online privacy")
        
        if any(keyword in content for keyword in ['upload', 'content', 'video', 'social']):
            topics.append("social media regulation")
        
        if any(keyword in content for keyword in ['data', 'privacy', 'personal', 'user']):
            topics.append("data protection")
        
        # Default topics if none detected
        if not topics:
            topics = ["social media regulation", "data protection"]
        
        return topics[:2]  # Limit to 2 topics for performance
    
    def _combine_validation_results(self, legal_research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine validation results from multiple legal research calls"""
        combined = {
            "session_id": self.session_id,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "api_calls_summary": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "success_rate": 0,
                "avg_response_time_ms": 0
            },
            "api_details": [],
            "sources_consulted": [],
            "data_freshness_analysis": {}
        }
        
        total_response_times = []
        
        for topic, research_result in legal_research_results.items():
            validation_summary = research_result.get("validation_summary", {})
            
            # Combine API call summaries
            api_summary = validation_summary.get("api_calls_summary", {})
            combined["api_calls_summary"]["total_calls"] += api_summary.get("total_calls", 0)
            combined["api_calls_summary"]["successful_calls"] += api_summary.get("successful_calls", 0)
            combined["api_calls_summary"]["failed_calls"] += api_summary.get("failed_calls", 0)
            
            # Combine API details
            api_details = validation_summary.get("api_details", [])
            combined["api_details"].extend(api_details)
            
            # Combine sources
            sources = validation_summary.get("sources_consulted", [])
            combined["sources_consulted"].extend(sources)
            
            # Collect response times
            for detail in api_details:
                if detail.get("response_time_ms") is not None:
                    total_response_times.append(detail["response_time_ms"])
        
        # Calculate overall metrics
        total_calls = combined["api_calls_summary"]["total_calls"]
        successful_calls = combined["api_calls_summary"]["successful_calls"]
        
        if total_calls > 0:
            combined["api_calls_summary"]["success_rate"] = (successful_calls / total_calls) * 100
        
        if total_response_times:
            combined["api_calls_summary"]["avg_response_time_ms"] = sum(total_response_times) / len(total_response_times)
        
        # Use freshness analysis from first result (they should be similar)
        if legal_research_results:
            first_result = next(iter(legal_research_results.values()))
            combined["data_freshness_analysis"] = first_result.get("validation_summary", {}).get("data_freshness_analysis", {})
        
        return combined
    
    def _determine_enhanced_risk_level(self, legal_research_results: Dict[str, Any], 
                                     validation_summary: Dict[str, Any]) -> str:
        """Determine risk level based on legal research and validation results"""
        
        # Check API success rate
        success_rate = validation_summary.get("api_calls_summary", {}).get("success_rate", 0)
        if success_rate < 70:
            return "HIGH"  # High risk if we couldn't get reliable legal data
        
        # Check source freshness
        freshness = validation_summary.get("data_freshness_analysis", {})
        if freshness.get("overall_status") == "concerning":
            return "HIGH"  # High risk if legal sources are very outdated
        
        # Check for compliance-triggering content
        total_sources = len(validation_summary.get("sources_consulted", []))
        if total_sources >= 10:
            return "HIGH"  # Many applicable regulations = high risk
        elif total_sources >= 5:
            return "MEDIUM"
        else:
            return "LOW"


# Example usage
async def test_enhanced_crew():
    """Test the enhanced multimodal crew"""
    print("🧪 Testing Enhanced Multimodal Crew...")
    
    crew = EnhancedMultimodalCrew()
    
    feature_data = {
        'project_name': 'Teen Video Upload Limits',
        'project_description': 'New feature to limit video uploads for users under 18, with parental consent requirements',
        'project_type': 'Social Media Feature'
    }
    
    try:
        result = await crew.analyze_comprehensive_compliance_with_validation(feature_data)
        
        print(f"✅ Enhanced analysis completed")
        print(f"📊 API Success Rate: {result.get('validation_summary', {}).get('api_calls_summary', {}).get('success_rate', 0):.1f}%")
        print(f"📚 Sources Found: {len(result.get('validation_summary', {}).get('sources_consulted', []))}")
        print(f"🎯 Risk Level: {result.get('risk_level', 'Unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(test_enhanced_crew())
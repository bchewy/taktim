"""
CrewAI tools for legal research using government APIs
Provides real-time access to legal databases for the Legal Knowledge Agent
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from crewai.tools import tool
from .legal_apis import LegalResearchAggregator

class LegalResearchInput(BaseModel):
    """Input schema for legal research tool"""
    topic: str = Field(..., description="Legal topic or regulation to research")
    include_federal: bool = Field(default=True, description="Include federal regulations")
    include_congressional: bool = Field(default=True, description="Include congressional bills")
    include_state: bool = Field(default=True, description="Include state laws")

@tool("legal_research")
def legal_research_tool(topic: str, include_federal: bool = True, 
                       include_congressional: bool = True, include_state: bool = True) -> str:
    """Research legal topics using official government APIs. 
    Searches federal regulations (GovInfo), congressional bills (Congress.gov), 
    and curated state laws. Use this to get current, authoritative legal information 
    for compliance analysis."""
    
    congress_api_key = os.getenv("CONGRESS_API_KEY")
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, 
                    _async_legal_research(topic, include_federal, include_congressional, include_state, congress_api_key)
                )
                return future.result(timeout=60)
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(_async_legal_research(topic, include_federal, include_congressional, include_state, congress_api_key))
    except Exception as e:
        return f"Legal research failed: {str(e)}"

async def _async_legal_research(topic: str, include_federal: bool, include_congressional: bool, include_state: bool, congress_api_key: str) -> str:
    """Execute legal research asynchronously"""
    aggregator = None
    try:
        # Initialize aggregator
        aggregator = LegalResearchAggregator(congress_api_key)
        
        # Perform research
        result = await aggregator.research_topic(topic)
        
        # Format results for the agent
        formatted_result = _format_research_results(result, include_federal, include_congressional, include_state)
        
        return formatted_result
        
    except Exception as e:
        return f"Legal research error: {str(e)}"
    finally:
        if aggregator:
            await aggregator.close()

def _format_research_results(result: Dict[str, Any], include_federal: bool,
                            include_congressional: bool, include_state: bool) -> str:
        """Format research results for agent consumption"""
        output = []
        
        output.append(f"# Legal Research: {result.get('topic', 'Unknown Topic')}")
        output.append(f"Research conducted on: {result.get('research_timestamp', 'Unknown')}")
        output.append("")
        
        # Federal Regulations
        if include_federal and "federal_regulations" in result:
            federal_regs = result["federal_regulations"]
            output.append("## Federal Regulations (GovInfo.gov)")
            
            if federal_regs:
                for i, reg in enumerate(federal_regs[:5], 1):  # Limit to top 5
                    title = reg.get("title", "Unknown Title")
                    package_id = reg.get("packageId", "Unknown ID")
                    date = reg.get("dateIssued", "Unknown Date")
                    output.append(f"{i}. **{title}**")
                    output.append(f"   - Package ID: {package_id}")
                    output.append(f"   - Date: {date}")
                    output.append("")
            else:
                output.append("No federal regulations found for this topic.")
                output.append("")
        
        # Congressional Bills
        if include_congressional and "congressional_bills" in result:
            bills = result["congressional_bills"]
            output.append("## Congressional Bills (Congress.gov)")
            
            if bills:
                for i, bill in enumerate(bills[:5], 1):  # Limit to top 5
                    title = bill.get("title", "Unknown Bill")
                    bill_type = bill.get("type", "Unknown")
                    number = bill.get("number", "Unknown")
                    congress = bill.get("congress", "Unknown")
                    output.append(f"{i}. **{title}**")
                    output.append(f"   - Bill: {bill_type} {number} (Congress {congress})")
                    output.append("")
            else:
                output.append("No congressional bills found for this topic.")
                output.append("")
        
        # State Laws
        if include_state and "state_laws" in result:
            state_laws = result["state_laws"]
            output.append("## State Laws (Curated)")
            
            if state_laws:
                for law_key, law_data in state_laws.items():
                    output.append(f"### {law_data.get('name', law_key)}")
                    output.append(f"**Jurisdiction:** {law_data.get('jurisdiction', 'Unknown')}")
                    
                    if "effective_date" in law_data:
                        output.append(f"**Effective Date:** {law_data['effective_date']}")
                    
                    if "key_provisions" in law_data:
                        output.append("**Key Provisions:**")
                        for provision in law_data["key_provisions"]:
                            output.append(f"- {provision}")
                    
                    if "penalties" in law_data:
                        output.append(f"**Penalties:** {law_data['penalties']}")
                    
                    output.append("")
            else:
                output.append("No relevant state laws found.")
                output.append("")
        
        # Sources
        sources = result.get("sources", [])
        if sources:
            output.append("## Sources")
            for source in sources:
                output.append(f"- {source}")
        
        return "\n".join(output)


@tool("social_media_compliance_research")
def social_media_compliance_research_tool() -> str:
    """Comprehensive legal research specifically for social media platform compliance. 
    Covers children's privacy, content moderation, algorithm transparency, and platform-specific 
    regulations across federal and state jurisdictions."""
    
    congress_api_key = os.getenv("CONGRESS_API_KEY")
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _async_social_media_research(congress_api_key))
                return future.result(timeout=120)  # Longer timeout for comprehensive research
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(_async_social_media_research(congress_api_key))
    except Exception as e:
        return f"Social media compliance research failed: {str(e)}"

async def _async_social_media_research(congress_api_key: str) -> str:
    """Execute comprehensive social media compliance research"""
    aggregator = None
    try:
        # Initialize aggregator
        aggregator = LegalResearchAggregator(congress_api_key)
        
        # Perform comprehensive research
        result = await aggregator.research_social_media_compliance()
        
        # Format results
        formatted_result = _format_compliance_results(result)
        
        return formatted_result
        
    except Exception as e:
        return f"Social media compliance research error: {str(e)}"
    finally:
        if aggregator:
            await aggregator.close()

def _format_compliance_results(result: Dict[str, Any]) -> str:
        """Format comprehensive compliance research results"""
        output = []
        
        output.append("# Comprehensive Social Media Platform Compliance Research")
        output.append(f"Research completed: {result.get('timestamp', 'Unknown')}")
        output.append(f"Summary: {result.get('summary', 'No summary available')}")
        output.append("")
        
        comprehensive_research = result.get("comprehensive_research", {})
        
        for topic_key, topic_data in comprehensive_research.items():
            topic_name = topic_key.replace("_", " ").title()
            output.append(f"## {topic_name}")
            
            # Federal regulations for this topic
            federal_regs = topic_data.get("federal_regulations", [])
            if federal_regs:
                output.append("### Federal Regulations")
                for i, reg in enumerate(federal_regs[:3], 1):
                    title = reg.get("title", "Unknown Title")
                    output.append(f"{i}. {title}")
                output.append("")
            
            # Congressional bills for this topic  
            bills = topic_data.get("congressional_bills", [])
            if bills:
                output.append("### Recent Congressional Bills")
                for i, bill in enumerate(bills[:3], 1):
                    title = bill.get("title", "Unknown Bill")
                    output.append(f"{i}. {title}")
                output.append("")
            
            # State laws
            state_laws = topic_data.get("state_laws", {})
            if state_laws:
                output.append("### Relevant State Laws")
                for law_key, law_data in list(state_laws.items())[:3]:
                    name = law_data.get("name", law_key)
                    jurisdiction = law_data.get("jurisdiction", "Unknown")
                    output.append(f"- **{name}** ({jurisdiction})")
                output.append("")
            
            output.append("---")
            output.append("")
        
        return "\n".join(output)


@tool("regulation_details")
def regulation_details_tool(topic: str) -> str:
    """Get detailed information about a specific regulation or law. 
    Provide the regulation name or package ID to get comprehensive details including 
    full text, effective dates, penalties, and compliance requirements."""
    # This would integrate with specific regulation detail APIs
    # For now, return curated information about key regulations
    
    known_regulations = {
            "coppa": {
                "full_name": "Children's Online Privacy Protection Act (COPPA)",
                "authority": "Federal Trade Commission (FTC)",
                "effective_date": "April 21, 2000 (updated 2013)",
                "scope": "Websites and online services directed to children under 13",
                "key_requirements": [
                    "Obtain verifiable parental consent before collecting personal information from children under 13",
                    "Provide clear and comprehensive privacy policy",
                    "Limit collection of personal information to what is reasonably necessary",
                    "Provide parents access to their child's personal information",
                    "Provide parents the option to refuse further collection or use of information",
                    "Establish procedures to protect confidentiality, security, and integrity of information"
                ],
                "penalties": "Up to $43,792 per violation (as of 2024)",
                "enforcement": "FTC enforcement with civil penalties",
                "recent_updates": "2013 Rule amendments expanded definition of personal information"
            },
            "california sb976": {
                "full_name": "California Social Media Child Protection Act (SB 976)",
                "authority": "California State Legislature",
                "effective_date": "January 1, 2024",
                "scope": "Social media platforms with users in California under 18",
                "key_requirements": [
                    "Prohibition on targeted advertising to users under 18",
                    "Default privacy settings must be highest level for minor users",
                    "No notifications between 12 AM - 6 AM or during school hours",
                    "Parental controls and oversight tools required",
                    "Age verification mechanisms must be implemented"
                ],
                "penalties": "Up to $25,000 per affected child for each violation",
                "enforcement": "California Attorney General enforcement",
                "compliance_deadline": "Platforms must comply within 12 months of effective date"
            }
        }
        
    topic_lower = topic.lower()
    for key, reg_data in known_regulations.items():
        if key in topic_lower or any(word in topic_lower for word in key.split()):
            return _format_regulation_details(reg_data)
    
    return f"Detailed information not available for: {topic}. Try using the legal_research tool for general information."

def _format_regulation_details(reg_data: Dict[str, Any]) -> str:
        """Format detailed regulation information"""
        output = []
        
        output.append(f"# {reg_data.get('full_name', 'Unknown Regulation')}")
        output.append("")
        
        if "authority" in reg_data:
            output.append(f"**Regulatory Authority:** {reg_data['authority']}")
        
        if "effective_date" in reg_data:
            output.append(f"**Effective Date:** {reg_data['effective_date']}")
        
        if "scope" in reg_data:
            output.append(f"**Scope:** {reg_data['scope']}")
        
        output.append("")
        
        if "key_requirements" in reg_data:
            output.append("## Key Requirements")
            for req in reg_data["key_requirements"]:
                output.append(f"- {req}")
            output.append("")
        
        if "penalties" in reg_data:
            output.append(f"**Penalties:** {reg_data['penalties']}")
        
        if "enforcement" in reg_data:
            output.append(f"**Enforcement:** {reg_data['enforcement']}")
        
        if "recent_updates" in reg_data:
            output.append(f"**Recent Updates:** {reg_data['recent_updates']}")
        
        if "compliance_deadline" in reg_data:
            output.append(f"**Compliance Deadline:** {reg_data['compliance_deadline']}")
        
        return "\n".join(output)


# Factory function to create all legal research tools
def create_legal_research_tools(congress_api_key: Optional[str] = None):
    """Create all legal research tools for the CrewAI agent"""
    import os
    # Set environment variable if provided
    if congress_api_key:
        os.environ["CONGRESS_API_KEY"] = congress_api_key
    
    return [
        legal_research_tool,
        social_media_compliance_research_tool,
        regulation_details_tool
    ]
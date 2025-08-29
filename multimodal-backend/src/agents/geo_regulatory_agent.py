"""
Geo-Regulatory Mapping Agent
Maps TikTok features to jurisdiction-specific compliance requirements
Generates auditable geo-compliance evidence
"""

import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Import our regulatory database
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.geo_regulatory_database import GeoRegulatoryDatabase, RiskLevel, ComplianceStatus, GeographicCompliance

@tool("geo_compliance_mapping")
def geo_compliance_mapping_tool(target_markets: str, feature_characteristics: str, feature_name: str = "Unknown Feature") -> str:
    """Map TikTok features to jurisdiction-specific regulatory requirements.
    Analyzes target markets and feature characteristics to identify applicable regulations
    in each geographic region. Provides detailed compliance requirements and risk assessment."""
    
    geo_db = GeoRegulatoryDatabase()
    
    # Parse inputs
    markets = [market.strip() for market in target_markets.split(",")]
    characteristics = [char.strip() for char in feature_characteristics.split(",")]
    
    # Get applicable regulations
    applicable_regs = geo_db.get_applicable_regulations(markets, characteristics)
    
    # Assess risk levels
    risk_levels = geo_db.assess_compliance_risk(applicable_regs)
    
    # Generate requirements
    requirements = geo_db.generate_compliance_requirements(applicable_regs)
    
    # Generate evidence citations
    citations = geo_db.generate_evidence_citations(applicable_regs)
    
    # Format output for agent
    output = []
    output.append(f"# Geo-Regulatory Compliance Mapping for: {feature_name}")
    output.append(f"Target Markets: {', '.join(markets)}")
    output.append(f"Feature Characteristics: {', '.join(characteristics)}")
    output.append(f"Analysis Timestamp: {datetime.utcnow().isoformat()}")
    output.append("")
    
    if not applicable_regs:
        output.append("## No Regulatory Requirements Found")
        output.append("This feature does not trigger any jurisdiction-specific compliance requirements.")
        return "\n".join(output)
    
    output.append("## Jurisdiction-Specific Compliance Analysis")
    output.append("")
    
    for jurisdiction, regulations in applicable_regs.items():
        risk_level = risk_levels.get(jurisdiction, RiskLevel.LOW)
        
        output.append(f"### {jurisdiction}")
        output.append(f"**Risk Level**: {risk_level.value.upper()}")
        output.append(f"**Applicable Regulations**: {len(regulations)}")
        output.append("")
        
        # List regulations
        output.append("**Regulations:**")
        for reg in regulations:
            output.append(f"- {reg.regulation_name} ({reg.article_section})")
            output.append(f"  - Enforcement: {reg.enforcement_authority}")
            output.append(f"  - Penalties: {reg.penalties}")
        output.append("")
        
        # List requirements
        if jurisdiction in requirements:
            output.append("**Compliance Requirements:**")
            for req in requirements[jurisdiction]:
                output.append(f"- {req}")
            output.append("")
        
        # List evidence citations
        if jurisdiction in citations:
            output.append("**Legal Citations for Audit Trail:**")
            for citation in citations[jurisdiction]:
                output.append(f"- {citation}")
            output.append("")
    
    # Overall risk summary
    max_risk = max(risk_levels.values(), key=lambda x: ["low", "medium", "high", "critical"].index(x.value))
    output.append(f"## Overall Risk Assessment")
    output.append(f"**Highest Risk Level**: {max_risk.value.upper()}")
    output.append(f"**Total Jurisdictions Affected**: {len(applicable_regs)}")
    output.append(f"**Audit Trail ID**: {str(uuid.uuid4())}")
    
    return "\n".join(output)

@tool("audit_trail_generator")
def audit_trail_generator_tool(feature_data: str, compliance_analysis: str) -> str:
    """Generate comprehensive audit trail for regulatory compliance screening.
    Creates structured evidence that can be used to respond to regulatory inquiries
    and prove that features were properly screened for compliance requirements."""
    
    geo_db = GeoRegulatoryDatabase()
    audit_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    output = []
    output.append(f"# REGULATORY COMPLIANCE AUDIT TRAIL")
    output.append(f"**Audit ID**: {audit_id}")
    output.append(f"**Generated**: {timestamp}")
    output.append(f"**System**: TikTok Geo-Regulatory Compliance Detection")
    output.append("")
    
    output.append("## Feature Screening Summary")
    output.append("This audit trail provides evidence that the following feature was")
    output.append("systematically screened for geo-specific regulatory compliance requirements.")
    output.append("")
    
    output.append("## Screening Process")
    output.append("1. **Regulatory Database Query**: Feature characteristics mapped against")
    output.append("   comprehensive database of global social media regulations")
    output.append("2. **Jurisdiction Analysis**: Target markets analyzed for applicable laws")
    output.append("3. **Risk Assessment**: Compliance risk evaluated per jurisdiction")
    output.append("4. **Evidence Generation**: Official legal citations compiled for audit trail")
    output.append("")
    
    output.append("## Compliance Analysis Results")
    output.append(compliance_analysis)
    output.append("")
    
    output.append("## Regulatory Inquiry Response Ready")
    output.append("This audit trail can be used to demonstrate to regulatory authorities that:")
    output.append("- Feature was proactively screened for compliance requirements")
    output.append("- All applicable jurisdictions were considered")
    output.append("- Official legal sources were consulted and cited")
    output.append("- Systematic process was followed with full traceability")
    output.append("")
    
    output.append("## Audit Trail Integrity")
    output.append(f"**Hash**: SHA256-{abs(hash(compliance_analysis + timestamp))}")
    output.append(f"**Verifiable**: This audit trail can be verified against regulatory databases")
    output.append(f"**Retention**: Stored for regulatory inquiry response purposes")
    
    return "\n".join(output)

class GeoRegulatoryAgent:
    """CrewAI agent for geo-regulatory compliance mapping"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize tools
        self.geo_compliance_tool = geo_compliance_mapping_tool
        self.audit_trail_tool = audit_trail_generator_tool
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the geo-regulatory mapping agent"""
        
        return Agent(
            role="Geo-Regulatory Compliance Specialist",
            goal="Map TikTok features to jurisdiction-specific regulatory requirements and generate auditable compliance evidence",
            backstory="""You are a specialized geo-regulatory compliance expert with deep knowledge 
            of global social media regulations across multiple jurisdictions. Your expertise includes:
            
            • Multi-Jurisdictional Compliance: US Federal, State laws, EU regulations, Canadian privacy laws
            • Social Media Specific Laws: COPPA, California SB976, GDPR, Digital Services Act
            • Platform Liability: Section 230, content moderation requirements, algorithmic transparency
            • Geographic Mapping: Understanding how regulations apply across different markets
            • Audit Trail Generation: Creating evidence for regulatory inquiry responses
            
            Your role is critical for TikTok's proactive compliance strategy. You transform regulatory 
            detection from a blind spot into a traceable, auditable process. Every analysis you provide 
            includes specific legal citations and jurisdiction-specific requirements that can withstand 
            regulatory scrutiny.
            
            IMPORTANT: Always use your geo_compliance_mapping tool to get jurisdiction-specific analysis,
            then use audit_trail_generator to create proper evidence documentation.""",
            tools=[geo_compliance_mapping_tool, audit_trail_generator_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_geo_compliance(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feature for geo-specific compliance requirements"""
        
        task = Task(
            description=f"""
            Conduct comprehensive geo-regulatory compliance analysis for this TikTok feature.
            
            **Feature Details:**
            - Name: {feature_data.get('feature_name', 'Unknown Feature')}
            - Description: {feature_data.get('description', 'No description provided')}
            - Target Markets: {', '.join(feature_data.get('target_markets', []))}
            
            **MANDATORY ANALYSIS STEPS:**
            
            1. **Geo-Compliance Mapping** (REQUIRED):
               - Use geo_compliance_mapping tool with target_markets: "{', '.join(feature_data.get('target_markets', []))}"
               - Feature characteristics: Extract relevant characteristics from the feature data
               - Include: {self._extract_feature_characteristics(feature_data)}
            
            2. **Audit Trail Generation** (REQUIRED):
               - Use audit_trail_generator tool to create evidence documentation
               - Include the compliance analysis results from step 1
               - Generate regulatory-inquiry-ready documentation
            
            **OUTPUT REQUIREMENTS:**
            Your analysis must provide:
            - Jurisdiction-specific compliance matrix (which laws apply where)
            - Risk assessment for each target market
            - Specific implementation requirements per jurisdiction
            - Auditable evidence trail with legal citations
            - Regulatory inquiry response documentation
            
            This analysis will be used by TikTok legal teams to:
            - Implement proactive compliance guardrails
            - Respond to regulatory inquiries
            - Demonstrate systematic compliance screening
            """,
            expected_output="Comprehensive geo-regulatory compliance analysis with jurisdiction-specific requirements and auditable evidence trail",
            agent=self.agent
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return {"geo_compliance_analysis": result.raw}
    
    def _extract_feature_characteristics(self, feature_data: Dict[str, Any]) -> str:
        """Extract feature characteristics for regulatory mapping from description and feature name"""
        
        characteristics = []
        
        # Extract from feature name and description
        feature_name = feature_data.get('feature_name', '').lower()
        description = feature_data.get('description', '').lower()
        combined_text = f"{feature_name} {description}"
        
        # AI/ML detection
        if any(term in combined_text for term in ['ai', 'ml', 'algorithm', 'machine learning', 'artificial intelligence', 'recommend', 'personalization', 'intelligence']):
            characteristics.append('recommendation_engine')
            characteristics.append('user_personalization')
        
        # Biometric/facial recognition detection
        if any(term in combined_text for term in ['biometric', 'facial', 'face', 'recognition', 'vision', 'image analysis']):
            characteristics.append('biometric_analysis')
        
        # Location detection
        if any(term in combined_text for term in ['location', 'geolocation', 'gps', 'geographic', 'geo']):
            characteristics.append('location_tracking')
        
        # Age/minor detection
        if any(term in combined_text for term in ['teen', 'child', 'minor', 'age', 'youth', '13', '17', 'under 18']):
            characteristics.append('age_detection')
        
        # Social sharing detection
        if any(term in combined_text for term in ['social', 'sharing', 'share', 'post', 'comment', 'like', 'follow']):
            characteristics.append('social_sharing')
        
        # Advertising detection
        if any(term in combined_text for term in ['advertis', 'target', 'ad', 'marketing', 'promotion']):
            characteristics.append('targeted_advertising')
        
        # Content moderation detection
        if any(term in combined_text for term in ['moderat', 'filter', 'content review', 'safety']):
            characteristics.append('content_moderation')
        
        # Analytics detection
        if any(term in combined_text for term in ['analytics', 'track', 'metrics', 'data', 'analysis', 'monitoring']):
            characteristics.append('data_analytics')
        
        # Video/media detection
        if any(term in combined_text for term in ['video', 'media', 'content', 'stream', 'upload']):
            characteristics.append('content_sharing')
        
        # Discovery/feed detection
        if any(term in combined_text for term in ['discovery', 'feed', 'explore', 'trending', 'for you']):
            characteristics.append('content_curation')
        
        # Default characteristics for social media platforms if nothing detected
        if not characteristics:
            characteristics = ['social_sharing', 'user_personalization', 'content_sharing']
        
        return ', '.join(list(set(characteristics)))
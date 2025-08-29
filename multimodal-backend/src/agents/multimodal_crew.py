"""
CrewAI Multimodal Agent System
Handles text, image, and document processing with specialized agents
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool
from langchain_openai import ChatOpenAI
import base64
from pathlib import Path

# Import legal research tools
try:
    from ..utils.legal_research_tools import create_legal_research_tools
    LEGAL_TOOLS_AVAILABLE = True
except ImportError:
    LEGAL_TOOLS_AVAILABLE = False
    print("Warning: Legal research tools not available")

# Import geo-regulatory agent
try:
    from .geo_regulatory_agent import GeoRegulatoryAgent
    GEO_REGULATORY_AVAILABLE = True
except ImportError:
    GEO_REGULATORY_AVAILABLE = False
    print("Warning: Geo-regulatory agent not available")


class MultimodalCrew:
    """CrewAI system for multimodal content analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize tools
        self.file_tool = FileReadTool()
        self.directory_tool = DirectoryReadTool()
        
        # Initialize geo-regulatory agent
        self.geo_regulatory_agent = None
        if GEO_REGULATORY_AVAILABLE:
            try:
                self.geo_regulatory_agent = GeoRegulatoryAgent()
                print("✅ Geo-Regulatory Agent initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Geo-Regulatory Agent: {e}")
        
        # Create specialized agents
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for different content types"""
        
        # Document Analyst Agent
        document_agent = Agent(
            role="Document Analyst",
            goal="Extract, analyze, and summarize content from text documents, PDFs, and spreadsheets",
            backstory="""You are an expert document analyst with deep expertise in processing 
            various document formats. You excel at extracting key information, identifying 
            patterns, and creating comprehensive summaries.""",
            tools=[self.file_tool, self.directory_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Image Analyst Agent
        image_agent = Agent(
            role="Image Analyst", 
            goal="Analyze images, extract text via OCR, identify objects, and describe visual content",
            backstory="""You are a computer vision specialist with expertise in image analysis, 
            OCR, object detection, and visual content understanding. You can interpret 
            charts, diagrams, screenshots, and photographs.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Content Synthesizer Agent
        synthesizer_agent = Agent(
            role="Content Synthesizer",
            goal="Combine insights from multiple sources and create comprehensive reports",
            backstory="""You are a master synthesizer who can take information from various 
            sources - documents, images, and data - and create coherent, insightful reports 
            that highlight key findings and relationships.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Legal Knowledge Agent with API-powered tools
        legal_tools = [self.file_tool, self.directory_tool]
        
        # Add legal research tools if available
        if LEGAL_TOOLS_AVAILABLE:
            try:
                congress_api_key = os.getenv("CONGRESS_API_KEY")  # Optional
                legal_research_tools = create_legal_research_tools(congress_api_key)
                legal_tools.extend(legal_research_tools)
                print("✅ Legal research tools (GovInfo, Congress.gov) loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load legal research tools: {e}")
        
        legal_agent = Agent(
            role="Legal Compliance Expert",
            goal="Analyze TikTok features for global regulatory compliance using real-time legal research",
            backstory="""You are a world-class legal compliance expert with access to real-time 
            government legal databases including GovInfo.gov (federal regulations) and Congress.gov 
            (legislative tracking). Your expertise covers:
            
            • Federal Regulations: Real-time access to CFR, Federal Register, and agency guidance
            • Congressional Activity: Current bills and laws affecting social media platforms
            • State Law Knowledge: California SB976, Florida OPM, Utah SMRA, and other state regulations
            • Global Data Privacy: GDPR, CCPA, PIPEDA, and international privacy frameworks
            • Children Protection: COPPA, state minor protection laws, age verification requirements
            • Social Media Specific: Content moderation, algorithm transparency, platform liability
            • AI Governance: Emerging AI regulations, explainability requirements, bias auditing
            
            IMPORTANT: Always use your legal research tools to get the most current and accurate 
            legal information before making compliance recommendations. Cross-reference multiple 
            sources and cite specific regulations in your analysis.
            
            You provide actionable compliance guidance with specific technical requirements, 
            timelines, and risk assessments for each jurisdiction.""",
            tools=legal_tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        return {
            "document": document_agent,
            "image": image_agent,
            "synthesizer": synthesizer_agent,
            "legal": legal_agent
        }
    
    def analyze_documents(self, file_paths: List[str], query: str) -> str:
        """Analyze text documents and PDFs"""
        
        task = Task(
            description=f"""
            Analyze the following documents and answer this query: {query}
            
            Documents to analyze: {file_paths}
            
            Your analysis should include:
            1. Key information extracted from each document
            2. Main themes and patterns identified
            3. Relevant data points and statistics
            4. Direct answers to the user's query
            5. Summary of findings
            """,
            expected_output="Comprehensive document analysis with key insights and direct answers to the query",
            agent=self.agents["document"]
        )
        
        crew = Crew(
            agents=[self.agents["document"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def analyze_images(self, image_data: List[Dict], query: str) -> str:
        """Analyze images with vision capabilities"""
        
        image_descriptions = []
        for img_info in image_data:
            image_descriptions.append(f"Image: {img_info['filename']} - {img_info.get('description', 'No description')}")
        
        task = Task(
            description=f"""
            Analyze the provided images and answer this query: {query}
            
            Images provided: {image_descriptions}
            
            Your analysis should include:
            1. Visual content description for each image
            2. Text extraction (OCR) if applicable
            3. Object and scene identification
            4. Relevant visual patterns or data
            5. Direct answers to the user's query based on visual content
            """,
            expected_output="Detailed image analysis with visual insights and query responses",
            agent=self.agents["image"]
        )
        
        crew = Crew(
            agents=[self.agents["image"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def synthesize_multimodal_analysis(self, 
                                     document_analysis: str, 
                                     image_analysis: str, 
                                     query: str) -> str:
        """Combine document and image analysis into comprehensive report"""
        
        task = Task(
            description=f"""
            Create a comprehensive analysis report by synthesizing information from both 
            document analysis and image analysis to answer: {query}
            
            Document Analysis Results:
            {document_analysis}
            
            Image Analysis Results:
            {image_analysis}
            
            Your synthesis should include:
            1. Executive summary of key findings
            2. Cross-referenced insights between documents and images
            3. Comprehensive answer to the user's query
            4. Identified patterns and correlations
            5. Actionable recommendations if applicable
            """,
            expected_output="Comprehensive multimodal analysis report with synthesized insights",
            agent=self.agents["synthesizer"]
        )
        
        crew = Crew(
            agents=[self.agents["synthesizer"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def full_multimodal_analysis(self, 
                                file_paths: List[str], 
                                image_data: List[Dict], 
                                query: str) -> Dict[str, Any]:
        """Complete multimodal analysis workflow"""
        
        results = {}
        
        # Analyze documents if provided
        if file_paths:
            results["document_analysis"] = self.analyze_documents(file_paths, query)
        else:
            results["document_analysis"] = "No documents provided for analysis."
        
        # Analyze images if provided
        if image_data:
            results["image_analysis"] = self.analyze_images(image_data, query)
        else:
            results["image_analysis"] = "No images provided for analysis."
        
        # Synthesize results if we have both types of content
        if file_paths and image_data:
            results["synthesis"] = self.synthesize_multimodal_analysis(
                results["document_analysis"],
                results["image_analysis"],
                query
            )
        elif file_paths:
            results["synthesis"] = results["document_analysis"]
        elif image_data:
            results["synthesis"] = results["image_analysis"]
        else:
            results["synthesis"] = "No content provided for analysis."
        
        return results
    
    def analyze_legal_compliance(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze TikTok feature for legal compliance using real-time legal research"""
        
        task = Task(
            description=f"""
            Conduct comprehensive legal compliance analysis for this TikTok feature using real-time legal research.
            
            **Feature Details:**
            - Name: {feature_data.get('feature_name', 'Unknown Feature')}
            - Description: {feature_data.get('description', 'No description provided')}
            - Target Markets: {', '.join(feature_data.get('target_markets', []))}
            
            **MANDATORY RESEARCH STEPS (You MUST use your legal research tools):**
            
            1. **PRIMARY RESEARCH (Required):**
               - FIRST: Use legal_research tool with topic "social media platform compliance"
               - SECOND: Use social_media_compliance_research tool for comprehensive analysis
               - THIRD: Use regulation_details tool for "COPPA" if minors are involved
               - FOURTH: Use legal_research tool for any AI/algorithm components mentioned
            
            2. **Cross-Reference Multiple Sources:**
               - Verify findings across federal (GovInfo), congressional (Congress.gov), and state sources
               - Look for recent legislative developments that might affect this feature
               - Check for enforcement patterns and recent penalties
            
            3. **Jurisdiction-Specific Analysis:**
               For each target market, determine:
               - Applicable federal laws and regulations
               - State/local requirements (especially CA, FL, UT for social media)
               - International requirements (GDPR if global, other privacy laws)
            
            4. **Risk and Compliance Assessment:**
               Based on your research, evaluate:
               - Compliance status: "compliant" | "needs_review" | "high_risk"
               - Risk level per jurisdiction: "low" | "medium" | "high"
               - Specific compliance gaps and requirements
               - Recommended implementation steps
            
            **CRITICAL:** Always cite specific regulations, CFR sections, or bills from your research.
            Reference the exact source (GovInfo package ID, bill number, etc.) in your analysis.
            
            **Output Requirements:**
            Provide detailed analysis including:
            - Research citations from your legal research tools
            - Specific regulation requirements with exact legal references
            - Technical implementation requirements
            - Jurisdiction-by-jurisdiction compliance status
            - Timeline recommendations for compliance implementation
            """,
            expected_output="Comprehensive legal compliance analysis with real-time research citations and specific regulatory requirements",
            agent=self.agents["legal"]
        )
        
        crew = Crew(
            agents=[self.agents["legal"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return {"legal_analysis": result.raw}
    
    def assess_regulatory_risks(self, feature_data: Dict[str, Any], specific_jurisdictions: List[str] = None) -> Dict[str, Any]:
        """Deep dive risk assessment for specific jurisdictions"""
        
        jurisdictions = specific_jurisdictions or feature_data.get('target_markets', ['US', 'EU'])
        
        task = Task(
            description=f"""
            Perform a detailed regulatory risk assessment for this TikTok feature:
            
            **Feature:** {feature_data.get('feature_name')}
            **Focus Jurisdictions:** {', '.join(jurisdictions)}
            
            **Feature Details:**
            {feature_data}
            
            **Risk Assessment Focus:**
            
            1. **High-Risk Scenarios:**
               - What could go wrong from a legal perspective?
               - What are the worst-case regulatory outcomes?
               - Which aspects of the feature are most problematic?
            
            2. **Jurisdiction-Specific Risks:**
               - Analyze each jurisdiction separately
               - Consider local cultural and legal sensitivities
               - Factor in enforcement patterns and penalties
            
            3. **Precedent Analysis:**
               - Reference similar features that have faced regulatory scrutiny
               - Learn from compliance issues at other social media platforms
            
            4. **Mitigation Strategies:**
               - How can identified risks be reduced or eliminated?
               - What controls or safeguards should be implemented?
            
            Provide specific, actionable risk assessment with clear mitigation paths.
            """,
            expected_output="Detailed regulatory risk assessment with jurisdiction-specific analysis and mitigation strategies",
            agent=self.agents["legal"]
        )
        
        crew = Crew(
            agents=[self.agents["legal"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return {"risk_assessment": result.raw}
    
    def analyze_comprehensive_compliance(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive compliance analysis combining legal research and geo-regulatory mapping"""
        
        if not self.geo_regulatory_agent:
            return {"error": "Geo-Regulatory Agent not available"}
        
        # Step 1: Legal research using government APIs
        legal_analysis = self.analyze_legal_compliance(feature_data)
        
        # Step 2: Geo-regulatory mapping for jurisdiction-specific requirements
        geo_analysis = self.geo_regulatory_agent.analyze_geo_compliance(feature_data)
        
        # Step 3: Combined analysis
        comprehensive_result = {
            "feature_id": feature_data.get('feature_name', 'Unknown'),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "legal_research": legal_analysis,
            "geo_regulatory_mapping": geo_analysis,
            "compliance_status": self._determine_overall_compliance_status(legal_analysis, geo_analysis),
            "audit_trail_ready": True
        }
        
        return comprehensive_result
    
    def _determine_overall_compliance_status(self, legal_analysis: Dict, geo_analysis: Dict) -> Dict[str, Any]:
        """Determine overall compliance status from combined analyses"""
        
        # Extract risk indicators from both analyses
        has_legal_concerns = "high" in str(legal_analysis).lower() or "critical" in str(legal_analysis).lower()
        has_geo_concerns = "HIGH" in str(geo_analysis) or "CRITICAL" in str(geo_analysis)
        
        if has_legal_concerns or has_geo_concerns:
            status = "REQUIRES_IMMEDIATE_REVIEW"
            risk_level = "HIGH"
        elif "medium" in str(legal_analysis).lower() or "MEDIUM" in str(geo_analysis):
            status = "NEEDS_COMPLIANCE_IMPLEMENTATION"  
            risk_level = "MEDIUM"
        else:
            status = "COMPLIANT_WITH_MONITORING"
            risk_level = "LOW"
        
        return {
            "overall_status": status,
            "risk_level": risk_level,
            "legal_analysis_complete": "legal_analysis" in str(legal_analysis),
            "geo_mapping_complete": "geo_compliance_analysis" in str(geo_analysis),
            "regulatory_inquiry_ready": True
        }


class ChatAgent:
    """Interactive chat agent with multimodal context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.chat_agent = Agent(
            role="Multimodal Assistant",
            goal="Provide helpful responses based on uploaded content and chat history",
            backstory="""You are an intelligent assistant with access to analyzed content 
            from documents and images. You can answer questions, provide insights, and 
            help users understand their multimodal data.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def chat_with_context(self, message: str, context: Dict[str, Any]) -> str:
        """Chat with context from previous analyses"""
        
        context_info = ""
        if context.get("document_analysis"):
            context_info += f"\nDocument Analysis: {context['document_analysis']}"
        if context.get("image_analysis"):
            context_info += f"\nImage Analysis: {context['image_analysis']}"
        if context.get("synthesis"):
            context_info += f"\nSynthesis: {context['synthesis']}"
        
        task = Task(
            description=f"""
            Respond to the user's message using the available context from previous analyses.
            
            User Message: {message}
            
            Available Context: {context_info}
            
            Provide a helpful, accurate response that leverages the context when relevant.
            """,
            expected_output="Helpful response incorporating relevant context",
            agent=self.chat_agent
        )
        
        crew = Crew(
            agents=[self.chat_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
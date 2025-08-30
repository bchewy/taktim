⏺ How the Application Works: Single Feature Analysis

  Based on my exploration of your codebase, here's a comprehensive overview of how the application works when analyzing a single feature:

  Architecture Overview

  The application consists of a React frontend communicating with a FastAPI backend that orchestrates multiple CrewAI agents for compliance analysis.

  Frontend Flow (SingleAnalysis.js)

  1. User Input Form:
    - User enters feature details: summary, project_name, project_description, project_type, priority, due_date
    - Has a "Demo" button that pre-populates with sample data (Video upload limits feature)
  2. Analysis Trigger:
    - When submitted, the form sends a POST request to /api/comprehensive-compliance-analysis
    - The UI shows an animated agent visualization during processing
    - Progresses through stages: initializing → legal_analysis → geo_mapping → audit_generation → finalizing
  3. Visual Feedback:
    - AgentVisualization component shows animated agents working
    - ResultsReady component appears when analysis completes
    - Results display with accordion sections for different analysis areas

  Backend Processing (main.py)

  The /api/comprehensive-compliance-analysis endpoint (multimodal-backend/main.py:448-478) orchestrates the entire analysis:

  1. Session Tracking: Creates a unique session ID for real-time progress tracking
  2. Calls multimodal_crew.analyze_comprehensive_compliance()

  CrewAI Agent System (multimodal_crew.py)

  The MultimodalCrew class manages specialized AI agents:

  Agent Types:

  1. Legal Compliance Expert (multimodal-backend/src/agents/multimodal_crew.py:114-141)
    - Has access to legal research tools (GovInfo.gov, Congress.gov APIs)
    - Analyzes features for regulatory compliance
    - Expertise in GDPR, COPPA, CCPA, state laws, AI governance
  2. Geo-Regulatory Agent (geo_regulatory_agent.py)
    - Maps features to jurisdiction-specific requirements
    - Uses a regulatory database to identify applicable laws
    - Generates audit trails and evidence citations
  3. Document/Image Analysts - For multimodal content processing
  4. Content Synthesizer - Combines insights from multiple sources

  Analysis Workflow (multimodal_crew.py:376-450):

  1. Legal Analysis Phase:
    - Legal agent researches applicable laws using government APIs
    - Performs risk assessment
    - Identifies compliance requirements
    - Uses real-time legal research tools to query federal regulations and congressional bills
  2. Geo-Regulatory Mapping:
    - Geo-regulatory agent maps feature to jurisdiction-specific requirements
    - Assesses risk levels per jurisdiction
    - Generates compliance requirements for each market
  3. Audit Trail Generation:
    - Creates evidence trail for regulatory inquiries
    - Documents all compliance checks
    - Generates citations and references

  Real-Time Progress Tracking

  The system includes sophisticated progress tracking:
  - agent_progress_tracker.py logs agent activities
  - Frontend can stream progress via SSE endpoint /api/progress-stream/{session_id}
  - Each agent reports its status: initializing → working → completed

  Legal Research Integration

  The system integrates with government APIs (legal_research_tools.py):
  - GovInfo.gov: Federal regulations, CFR, Federal Register
  - Congress.gov: Congressional bills and laws
  - State law database: Curated state-specific regulations

  Data Flow Summary

  User Input (Frontend)
      ↓
  FastAPI Endpoint
      ↓
  MultimodalCrew.analyze_comprehensive_compliance()
      ↓
  Parallel Agent Execution:
      - Legal Compliance Agent → Government API queries
      - Geo-Regulatory Agent → Jurisdiction mapping
      ↓
  Result Synthesis & Audit Trail
      ↓
  Response to Frontend
      ↓
  Visual Display with Accordion Sections

  Key Features

  1. Multi-Agent Orchestration: Different specialized agents handle specific aspects of compliance
  2. Real Government Data: Integrates with official legal databases for current regulations
  3. Jurisdiction-Specific Analysis: Maps features to requirements in different geographic regions
  4. Audit Trail: Generates regulatory-inquiry-ready documentation
  5. Real-Time Progress: Visual feedback during analysis with agent animations
  6. Risk Assessment: Provides risk levels (LOW/MEDIUM/HIGH/CRITICAL) per jurisdiction

  The system is designed to help TikTok (or similar platforms) ensure features comply with global regulations by combining AI analysis with real legal data sources.
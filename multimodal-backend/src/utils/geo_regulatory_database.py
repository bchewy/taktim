"""
Geo-Regulatory Database for jurisdiction-specific compliance mapping
Maps regulations to specific geographic regions and feature characteristics
"""

from typing import Dict, List, Any, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NEEDS_REVIEW = "needs_review"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_IMPLEMENTATION = "requires_implementation"

@dataclass
class RegulationMapping:
    regulation_name: str
    jurisdiction: str
    article_section: str
    applies_when: List[str]  # Feature characteristics that trigger this regulation
    requirements: List[str]
    penalties: str
    enforcement_authority: str
    effective_date: str
    last_updated: str
    government_source: str

@dataclass
class GeographicCompliance:
    jurisdiction: str
    regulations: List[RegulationMapping]
    risk_level: RiskLevel
    compliance_status: ComplianceStatus
    specific_requirements: List[str]
    implementation_deadline: str
    evidence_citations: List[str]
    audit_trail_id: str

class GeoRegulatoryDatabase:
    """Comprehensive database of geographic-specific regulations for social media platforms"""
    
    def __init__(self):
        self.regulations = self._build_regulation_database()
        self.jurisdiction_mappings = self._build_jurisdiction_mappings()
        self.feature_triggers = self._build_feature_triggers()
    
    def _build_regulation_database(self) -> Dict[str, List[RegulationMapping]]:
        """Build comprehensive regulation database by jurisdiction"""
        
        return {
            "US_FEDERAL": [
                RegulationMapping(
                    regulation_name="COPPA",
                    jurisdiction="United States (Federal)",
                    article_section="15 U.S.C. 6501-6506",
                    applies_when=["users_under_13", "personal_data_collection", "child_directed_content"],
                    requirements=[
                        "Obtain verifiable parental consent before collecting personal information from children under 13",
                        "Provide clear and comprehensive privacy notice",
                        "Limit collection to reasonably necessary information",
                        "Provide parents access to child's personal information",
                        "Provide option for parents to refuse further collection"
                    ],
                    penalties="Up to $43,792 per violation (2024)",
                    enforcement_authority="Federal Trade Commission (FTC)",
                    effective_date="2000-04-21",
                    last_updated="2024-01-16",
                    government_source="16 CFR Part 312"
                ),
                RegulationMapping(
                    regulation_name="Section 230",
                    jurisdiction="United States (Federal)", 
                    article_section="47 U.S.C. § 230",
                    applies_when=["user_generated_content", "content_moderation", "platform_liability"],
                    requirements=[
                        "Good faith content moderation efforts",
                        "Notice and takedown procedures",
                        "Platform immunity for third-party content with exceptions"
                    ],
                    penalties="Platform liability exceptions for certain content",
                    enforcement_authority="Various federal agencies and courts",
                    effective_date="1996-02-08",
                    last_updated="2018-04-11",
                    government_source="Communications Decency Act"
                )
            ],
            
            "US_CALIFORNIA": [
                RegulationMapping(
                    regulation_name="California SB976",
                    jurisdiction="California, United States",
                    article_section="SB976 Chapter 2024",
                    applies_when=["social_media_platform", "users_under_18", "california_residents"],
                    requirements=[
                        "Prohibition on targeted advertising to users under 18",
                        "Default privacy settings must be highest level for minor users",
                        "No notifications between 12 AM - 6 AM for minors",
                        "No notifications during school hours (8 AM - 3 PM on weekdays) for minors",
                        "Implement age verification mechanisms"
                    ],
                    penalties="Up to $25,000 per affected child per violation",
                    enforcement_authority="California Attorney General",
                    effective_date="2024-01-01",
                    last_updated="2024-01-01",
                    government_source="California Legislature SB976"
                ),
                RegulationMapping(
                    regulation_name="CCPA",
                    jurisdiction="California, United States",
                    article_section="Cal. Civ. Code § 1798.100 et seq.",
                    applies_when=["personal_information_processing", "california_residents", "commercial_purposes"],
                    requirements=[
                        "Right to know what personal information is collected",
                        "Right to delete personal information",
                        "Right to opt-out of sale of personal information",
                        "Right to non-discrimination for exercising privacy rights",
                        "Privacy policy disclosures"
                    ],
                    penalties="Up to $7,500 per intentional violation",
                    enforcement_authority="California Privacy Protection Agency",
                    effective_date="2020-01-01",
                    last_updated="2023-01-01",
                    government_source="California Civil Code 1798"
                )
            ],
            
            "EUROPEAN_UNION": [
                RegulationMapping(
                    regulation_name="GDPR",
                    jurisdiction="European Union",
                    article_section="Regulation (EU) 2016/679",
                    applies_when=["personal_data_processing", "eu_residents", "data_subject_rights"],
                    requirements=[
                        "Lawful basis for processing personal data",
                        "Data subject consent mechanisms",
                        "Right to erasure (right to be forgotten)",
                        "Data portability rights",
                        "Privacy by design and by default",
                        "Data Protection Impact Assessment for high-risk processing"
                    ],
                    penalties="Up to €20 million or 4% of global annual turnover",
                    enforcement_authority="Data Protection Authorities (DPAs)",
                    effective_date="2018-05-25",
                    last_updated="2018-05-25",
                    government_source="EUR-Lex 32016R0679"
                ),
                RegulationMapping(
                    regulation_name="Digital Services Act (DSA)",
                    jurisdiction="European Union",
                    article_section="Regulation (EU) 2022/2065",
                    applies_when=["recommender_systems", "online_platforms", "algorithmic_systems"],
                    requirements=[
                        "Provide at least one non-personalized recommender system option",
                        "Transparency in recommender system parameters",
                        "Allow users to modify/influence recommender parameters",
                        "Risk assessment for systemic risks",
                        "Content moderation transparency reporting"
                    ],
                    penalties="Up to 6% of global annual turnover",
                    enforcement_authority="European Commission and Digital Services Coordinators",
                    effective_date="2024-02-17",
                    last_updated="2024-02-17",
                    government_source="EUR-Lex 32022R2065"
                )
            ],
            
            "CANADA": [
                RegulationMapping(
                    regulation_name="PIPEDA",
                    jurisdiction="Canada (Federal)",
                    article_section="S.C. 2000, c. 5",
                    applies_when=["personal_information_collection", "commercial_activity", "canadian_residents"],
                    requirements=[
                        "Obtain meaningful consent for collection, use and disclosure",
                        "Limit collection to necessary purposes",
                        "Provide access to personal information upon request",
                        "Implement safeguards for personal information protection",
                        "Be accountable for personal information handling"
                    ],
                    penalties="Up to CAD $100,000 per violation",
                    enforcement_authority="Office of the Privacy Commissioner of Canada",
                    effective_date="2001-01-01",
                    last_updated="2015-06-18",
                    government_source="Privacy Act S.C. 2000"
                )
            ],
            
            "AUSTRALIA": [
                RegulationMapping(
                    regulation_name="Privacy Act 1988",
                    jurisdiction="Australia",
                    article_section="Privacy Act 1988 (Cth)",
                    applies_when=["personal_information_handling", "australian_residents", "social_media_services"],
                    requirements=[
                        "Comply with Australian Privacy Principles (APPs)",
                        "Notify eligible data breaches to OAIC and individuals",
                        "Provide privacy policy accessible and up-to-date",
                        "Implement reasonable security safeguards"
                    ],
                    penalties="Up to AUD $50 million or 30% of turnover",
                    enforcement_authority="Office of the Australian Information Commissioner (OAIC)",
                    effective_date="1988-12-01",
                    last_updated="2022-12-12",
                    government_source="Privacy Act 1988 Cth"
                )
            ]
        }
    
    def _build_jurisdiction_mappings(self) -> Dict[str, List[str]]:
        """Map market identifiers to jurisdiction codes"""
        return {
            "US": ["US_FEDERAL", "US_CALIFORNIA", "US_FLORIDA", "US_UTAH", "US_NEW_YORK"],
            "EU": ["EUROPEAN_UNION"],
            "Canada": ["CANADA"],
            "Australia": ["AUSTRALIA"],
            "UK": ["UNITED_KINGDOM"],
            "Global": ["US_FEDERAL", "EUROPEAN_UNION", "CANADA", "AUSTRALIA", "UNITED_KINGDOM"]
        }
    
    def _build_feature_triggers(self) -> Dict[str, List[str]]:
        """Map feature characteristics to regulation triggers"""
        return {
            "recommendation_engine": ["algorithmic_systems", "recommender_systems", "personalization"],
            "user_personalization": ["personal_data_processing", "algorithmic_systems", "data_subject_rights"],
            "age_detection": ["users_under_13", "users_under_18", "child_directed_content"],
            "location_tracking": ["personal_data_collection", "personal_information_collection", "geolocation_data"],
            "social_sharing": ["user_generated_content", "social_media_platform", "content_moderation"],
            "targeted_advertising": ["behavioral_targeting", "personal_data_processing", "commercial_purposes"],
            "data_analytics": ["personal_information_processing", "data_subject_rights", "analytics_processing"],
            "content_moderation": ["content_moderation", "platform_liability", "user_generated_content"],
            "biometric_analysis": ["sensitive_personal_data", "biometric_processing", "special_category_data"],
            "cross_border_transfer": ["international_transfer", "adequacy_decision", "data_localization"]
        }
    
    def get_applicable_regulations(self, 
                                 target_markets: List[str], 
                                 feature_characteristics: List[str]) -> Dict[str, List[RegulationMapping]]:
        """Get applicable regulations for given markets and feature characteristics"""
        
        applicable = {}
        
        for market in target_markets:
            if market in self.jurisdiction_mappings:
                jurisdictions = self.jurisdiction_mappings[market]
                
                for jurisdiction in jurisdictions:
                    if jurisdiction in self.regulations:
                        applicable_regs = []
                        
                        for regulation in self.regulations[jurisdiction]:
                            # Check if any feature characteristics trigger this regulation
                            if any(trigger in regulation.applies_when for trigger in feature_characteristics):
                                applicable_regs.append(regulation)
                        
                        if applicable_regs:
                            applicable[jurisdiction] = applicable_regs
        
        return applicable
    
    def assess_compliance_risk(self, 
                             applicable_regulations: Dict[str, List[RegulationMapping]]) -> Dict[str, RiskLevel]:
        """Assess compliance risk level for each jurisdiction"""
        
        risk_assessment = {}
        
        for jurisdiction, regulations in applicable_regulations.items():
            risk_factors = []
            
            for reg in regulations:
                # High risk factors
                if "children" in reg.regulation_name.lower() or "minor" in reg.regulation_name.lower():
                    risk_factors.append("children_protection")
                if "million" in reg.penalties or "turnover" in reg.penalties:
                    risk_factors.append("high_penalties")
                if any(req.lower().startswith("prohibit") for req in reg.requirements):
                    risk_factors.append("prohibition_requirements")
                if "consent" in " ".join(reg.requirements).lower():
                    risk_factors.append("consent_requirements")
                    
            # Calculate risk level
            if len(risk_factors) >= 3:
                risk_assessment[jurisdiction] = RiskLevel.CRITICAL
            elif len(risk_factors) >= 2:
                risk_assessment[jurisdiction] = RiskLevel.HIGH
            elif len(risk_factors) >= 1:
                risk_assessment[jurisdiction] = RiskLevel.MEDIUM
            else:
                risk_assessment[jurisdiction] = RiskLevel.LOW
        
        return risk_assessment
    
    def generate_compliance_requirements(self, 
                                       applicable_regulations: Dict[str, List[RegulationMapping]]) -> Dict[str, List[str]]:
        """Generate specific compliance requirements by jurisdiction"""
        
        requirements_by_jurisdiction = {}
        
        for jurisdiction, regulations in applicable_regulations.items():
            all_requirements = []
            
            for reg in regulations:
                for req in reg.requirements:
                    if req not in all_requirements:
                        all_requirements.append(req)
            
            requirements_by_jurisdiction[jurisdiction] = all_requirements
        
        return requirements_by_jurisdiction
    
    def generate_evidence_citations(self, 
                                  applicable_regulations: Dict[str, List[RegulationMapping]]) -> Dict[str, List[str]]:
        """Generate evidence citations for audit trail"""
        
        citations_by_jurisdiction = {}
        
        for jurisdiction, regulations in applicable_regulations.items():
            citations = []
            
            for reg in regulations:
                citation = f"{reg.regulation_name} ({reg.article_section}) - {reg.government_source}"
                citations.append(citation)
            
            citations_by_jurisdiction[jurisdiction] = citations
        
        return citations_by_jurisdiction
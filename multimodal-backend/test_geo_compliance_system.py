#!/usr/bin/env python3
"""
Comprehensive Test Suite for Geo-Compliance Detection System
Tests the complete pipeline for TikTok's regulatory blind spot solution
"""

import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, List, Any

# Test TikTok features that represent different compliance scenarios
TEST_SCENARIOS = [
    {
        "name": "High Risk - Teen Personalized Feed",
        "feature": {
            "feature_name": "AI Teen Discovery Feed",
            "description": "Personalized content recommendation system for teenage users with AI-driven engagement optimization",
            "target_markets": ["US", "EU", "Canada"]
        },
        "expected_risk": "HIGH",
        "expected_jurisdictions": ["US_FEDERAL", "US_CALIFORNIA", "EUROPEAN_UNION", "CANADA"],
        "expected_regulations": ["COPPA", "California SB976", "GDPR", "DSA"]
    },
    {
        "name": "Medium Risk - Adult Social Features",
        "feature": {
            "feature_name": "Social Circle Suggestions",
            "description": "Friend recommendation system using social graph analysis for adult users",
            "target_markets": ["US", "Australia"]
        },
        "expected_risk": "MEDIUM",
        "expected_jurisdictions": ["US_FEDERAL", "AUSTRALIA"],
        "expected_regulations": ["CCPA", "Privacy Act 1988"]
    },
    {
        "name": "Low Risk - Simple Content Filter",
        "feature": {
            "feature_name": "Basic Content Categories",
            "description": "Simple content categorization without personalization or data collection",
            "target_markets": ["US"]
        },
        "expected_risk": "LOW",
        "expected_jurisdictions": [],
        "expected_regulations": []
    },
    {
        "name": "Critical Risk - Biometric Minor Features",
        "feature": {
            "feature_name": "Dance Move Recognition for Kids",
            "description": "Biometric dance analysis for users under 13 with facial recognition and movement tracking",
            "target_markets": ["US", "EU", "Canada"]
        },
        "expected_risk": "CRITICAL",
        "expected_jurisdictions": ["US_FEDERAL", "US_CALIFORNIA", "EUROPEAN_UNION", "CANADA"],
        "expected_regulations": ["COPPA", "California SB976", "GDPR"]
    }
]

API_BASE_URL = "http://localhost:8001"

class GeoComplianceTestSuite:
    """Comprehensive test suite for the geo-compliance detection system"""
    
    def __init__(self):
        self.results = []
        self.api_endpoints = [
            "/api/comprehensive-compliance-analysis",
            "/api/geo-regulatory-mapping", 
            "/api/audit-trail-generation"
        ]
    
    def test_api_health(self) -> bool:
        """Test if the API is running"""
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("API Health: PASS")
                return True
            else:
                print(f"API Health: FAIL - Status {response.status_code}")
                return False
        except Exception as e:
            print(f"API Health: FAIL - {e}")
            return False
    
    def test_comprehensive_compliance_analysis(self, scenario: Dict) -> Dict[str, Any]:
        """Test the comprehensive compliance analysis endpoint"""
        
        print(f"\nTesting: {scenario['name']}")
        print(f"Feature: {scenario['feature']['feature_name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/comprehensive-compliance-analysis",
                json=scenario['feature'],
                timeout=120  # Longer timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze response for compliance detection
                test_result = self._analyze_compliance_response(result, scenario)
                test_result['api_status'] = 'SUCCESS'
                test_result['response_time'] = response.elapsed.total_seconds()
                
                print(f"  API Response: SUCCESS ({test_result['response_time']:.2f}s)")
                print(f"  Risk Assessment: {test_result.get('detected_risk', 'Unknown')}")
                print(f"  Jurisdictions Found: {test_result.get('jurisdictions_count', 0)}")
                print(f"  Audit Trail Ready: {test_result.get('audit_ready', False)}")
                
                return test_result
            else:
                print(f"  API Response: FAIL - Status {response.status_code}")
                return {
                    'scenario': scenario['name'],
                    'api_status': 'FAIL',
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'accuracy_score': 0
                }
                
        except Exception as e:
            print(f"  API Response: ERROR - {e}")
            return {
                'scenario': scenario['name'],
                'api_status': 'ERROR',
                'error': str(e),
                'accuracy_score': 0
            }
    
    def _analyze_compliance_response(self, api_response: Dict, scenario: Dict) -> Dict[str, Any]:
        """Analyze API response for accuracy against expected results"""
        
        analysis = {
            'scenario': scenario['name'],
            'feature_name': scenario['feature']['feature_name']
        }
        
        # Extract key information from API response
        result_data = api_response.get('result', {})
        compliance_status = result_data.get('compliance_status', {})
        
        # Check if comprehensive analysis was performed
        has_legal_analysis = 'legal_research' in result_data
        has_geo_mapping = 'geo_regulatory_mapping' in result_data
        audit_ready = result_data.get('audit_trail_ready', False)
        
        analysis['legal_analysis_performed'] = has_legal_analysis
        analysis['geo_mapping_performed'] = has_geo_mapping
        analysis['audit_ready'] = audit_ready
        
        # Extract detected risk level
        detected_risk = compliance_status.get('risk_level', 'UNKNOWN')
        analysis['detected_risk'] = detected_risk
        
        # Count jurisdictions analyzed
        geo_analysis = result_data.get('geo_regulatory_mapping', {})
        geo_content = str(geo_analysis)
        jurisdictions_count = sum(1 for jurisdiction in ['US_FEDERAL', 'US_CALIFORNIA', 'EUROPEAN_UNION', 'CANADA', 'AUSTRALIA'] 
                                if jurisdiction in geo_content)
        analysis['jurisdictions_count'] = jurisdictions_count
        
        # Calculate accuracy score
        accuracy_factors = []
        
        # Risk level accuracy
        expected_risk = scenario['expected_risk']
        if detected_risk == expected_risk:
            accuracy_factors.append(25)  # 25 points for correct risk level
        elif abs(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(detected_risk) - 
                ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(expected_risk)) <= 1:
            accuracy_factors.append(15)  # 15 points for close risk level
        
        # Jurisdiction detection accuracy
        expected_jurisdiction_count = len(scenario['expected_jurisdictions'])
        if jurisdictions_count >= expected_jurisdiction_count:
            accuracy_factors.append(25)  # 25 points for finding expected jurisdictions
        elif jurisdictions_count > 0:
            accuracy_factors.append(15)  # 15 points for finding some jurisdictions
        
        # System completeness
        if has_legal_analysis and has_geo_mapping:
            accuracy_factors.append(25)  # 25 points for complete analysis
        elif has_legal_analysis or has_geo_mapping:
            accuracy_factors.append(15)  # 15 points for partial analysis
        
        # Audit readiness
        if audit_ready:
            accuracy_factors.append(25)  # 25 points for audit trail
        
        analysis['accuracy_score'] = sum(accuracy_factors)
        analysis['max_possible_score'] = 100
        
        return analysis
    
    def test_audit_trail_generation(self, scenario: Dict) -> Dict[str, Any]:
        """Test audit trail generation for regulatory inquiries"""
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/audit-trail-generation",
                json=scenario['feature'],
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check audit trail completeness
                audit_trail = result.get('audit_trail', {})
                has_timestamps = 'screening_timestamp' in audit_trail
                has_compliance_analysis = 'compliance_analysis' in audit_trail
                has_jurisdictions = 'jurisdictions_analyzed' in audit_trail
                regulatory_ready = result.get('regulatory_response_ready', False)
                
                audit_score = sum([
                    25 if has_timestamps else 0,
                    25 if has_compliance_analysis else 0,
                    25 if has_jurisdictions else 0,
                    25 if regulatory_ready else 0
                ])
                
                return {
                    'audit_trail_complete': has_timestamps and has_compliance_analysis,
                    'regulatory_response_ready': regulatory_ready,
                    'audit_score': audit_score
                }
            else:
                return {'audit_score': 0, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'audit_score': 0, 'error': str(e)}
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all test scenarios and generate comprehensive report"""
        
        print("="*80)
        print("GEO-COMPLIANCE DETECTION SYSTEM - COMPREHENSIVE TEST SUITE")
        print("Testing TikTok's solution for regulatory blind spots")
        print("="*80)
        
        # Test API health first
        api_healthy = self.test_api_health()
        if not api_healthy:
            return {"status": "FAILED", "error": "API not accessible"}
        
        # Run all test scenarios
        test_results = []
        
        for scenario in TEST_SCENARIOS:
            # Test comprehensive compliance analysis
            compliance_result = self.test_comprehensive_compliance_analysis(scenario)
            
            # Test audit trail generation
            audit_result = self.test_audit_trail_generation(scenario)
            
            # Combine results
            combined_result = {**compliance_result, **audit_result}
            test_results.append(combined_result)
        
        # Generate final report
        return self._generate_final_report(test_results)
    
    def _generate_final_report(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive test report for grading/evaluation"""
        
        print("\n" + "="*80)
        print("FINAL TEST REPORT - GEO-COMPLIANCE DETECTION SYSTEM")
        print("="*80)
        
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results if result.get('api_status') == 'SUCCESS')
        
        # Calculate average accuracy
        accuracy_scores = [result.get('accuracy_score', 0) for result in test_results if 'accuracy_score' in result]
        average_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        
        # Calculate audit readiness
        audit_ready_count = sum(1 for result in test_results if result.get('audit_ready', False))
        audit_readiness_percentage = (audit_ready_count / total_tests) * 100
        
        # Response times
        response_times = [result.get('response_time', 0) for result in test_results if 'response_time' in result]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # System completeness
        complete_analyses = sum(1 for result in test_results 
                              if result.get('legal_analysis_performed', False) and 
                                 result.get('geo_mapping_performed', False))
        completeness_percentage = (complete_analyses / total_tests) * 100
        
        report = {
            "test_summary": {
                "total_scenarios_tested": total_tests,
                "successful_api_calls": successful_tests,
                "api_success_rate": (successful_tests / total_tests) * 100,
                "average_response_time_seconds": round(average_response_time, 2)
            },
            "compliance_detection_accuracy": {
                "average_accuracy_score": round(average_accuracy, 1),
                "max_possible_score": 100,
                "accuracy_percentage": round(average_accuracy, 1)
            },
            "regulatory_inquiry_readiness": {
                "audit_trails_generated": audit_ready_count,
                "audit_readiness_percentage": round(audit_readiness_percentage, 1),
                "regulatory_response_capable": audit_readiness_percentage >= 75
            },
            "system_completeness": {
                "complete_analyses_performed": complete_analyses,
                "completeness_percentage": round(completeness_percentage, 1),
                "legal_and_geo_mapping_integrated": completeness_percentage >= 75
            },
            "detailed_results": test_results,
            "test_timestamp": datetime.utcnow().isoformat(),
            "overall_grade": self._calculate_overall_grade(average_accuracy, audit_readiness_percentage, completeness_percentage)
        }
        
        # Print summary
        print(f"API Success Rate: {report['test_summary']['api_success_rate']:.1f}%")
        print(f"Compliance Detection Accuracy: {report['compliance_detection_accuracy']['accuracy_percentage']:.1f}%")
        print(f"Regulatory Inquiry Readiness: {report['regulatory_inquiry_readiness']['audit_readiness_percentage']:.1f}%")
        print(f"System Completeness: {report['system_completeness']['completeness_percentage']:.1f}%")
        print(f"Overall Grade: {report['overall_grade']['grade']} - {report['overall_grade']['status']}")
        
        # Save report
        with open("geo_compliance_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed test report saved to: geo_compliance_test_report.json")
        print("Use this report to demonstrate system effectiveness for TikTok's regulatory compliance!")
        
        return report
    
    def _calculate_overall_grade(self, accuracy: float, audit_readiness: float, completeness: float) -> Dict[str, str]:
        """Calculate overall system grade"""
        
        overall_score = (accuracy + audit_readiness + completeness) / 3
        
        if overall_score >= 90:
            return {"grade": "A", "score": overall_score, "status": "EXCELLENT - Production Ready"}
        elif overall_score >= 80:
            return {"grade": "B", "score": overall_score, "status": "GOOD - Minor Improvements Needed"}
        elif overall_score >= 70:
            return {"grade": "C", "score": overall_score, "status": "ACCEPTABLE - Significant Improvements Needed"}
        else:
            return {"grade": "D", "score": overall_score, "status": "NEEDS MAJOR WORK"}


def main():
    """Run the comprehensive test suite"""
    test_suite = GeoComplianceTestSuite()
    report = test_suite.run_comprehensive_tests()
    
    print(f"\nTesting complete! System grade: {report.get('overall_grade', {}).get('grade', 'Unknown')}")
    return report

if __name__ == "__main__":
    main()
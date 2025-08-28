#!/usr/bin/env python3
"""
GeoGov Analysis Runner
Processes dynamic inputs and runs comprehensive compliance analysis
"""

import asyncio
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import httpx
import pandas as pd

# Import from our integrated system
from main import (
    FeatureArtifact, Decision, Settings,
    scraping_aggregator, analyze, evidence_system
)


class AnalysisRunner:
    """Orchestrates the complete compliance analysis workflow"""
    
    def __init__(self):
        self.settings = Settings()
        self.results = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    async def load_inputs(self, inputs_file: str = "inputs.yaml") -> Dict[str, Any]:
        """Load dynamic inputs from YAML configuration"""
        try:
            with open(inputs_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Input file {inputs_file} not found")
            raise
        except yaml.YAMLError as e:
            print(f"❌ Error parsing {inputs_file}: {e}")
            raise
    
    async def refresh_knowledge_base(self, regulations: List[Dict]) -> Dict[str, Any]:
        """Refresh the knowledge base with regulation research"""
        print(f"\n🔄 Refreshing knowledge base with {len(regulations)} regulations...")
        
        try:
            result = await scraping_aggregator.refresh_corpus_for_regulations(regulations)
            print(f"✅ Knowledge base refreshed: {result['ingested']} documents indexed")
            return result
        except Exception as e:
            print(f"⚠️  Knowledge base refresh failed: {e}")
            return {"ingested": 0, "error": str(e)}
    
    async def analyze_feature(self, feature_config: Dict) -> Decision:
        """Analyze a single feature for compliance"""
        # Convert config to FeatureArtifact
        feature = FeatureArtifact(
            feature_id=feature_config["feature_id"],
            title=feature_config["title"],
            description=feature_config["description"],
            docs=feature_config.get("docs", []),
            code_hints=feature_config.get("code_hints", []),
            tags=feature_config.get("tags", [])
        )
        
        print(f"\n🔍 Analyzing: {feature.feature_id} - {feature.title}")
        
        try:
            decision = await analyze(feature)
            
            # Validate against expected results if provided
            expected_compliance = feature_config.get("expected_compliance")
            expected_regulations = feature_config.get("expected_regulations", [])
            
            validation_notes = []
            if expected_compliance is not None:
                compliance_match = decision.needs_geo_compliance == expected_compliance
                validation_notes.append(f"Compliance prediction: {'✅' if compliance_match else '❌'} (expected: {expected_compliance}, got: {decision.needs_geo_compliance})")
            
            if expected_regulations:
                regulation_match = bool(set(expected_regulations) & set(decision.regulations))
                validation_notes.append(f"Regulations match: {'✅' if regulation_match else '❌'} (expected: {expected_regulations}, got: {decision.regulations})")
            
            # Add validation to decision metadata
            if hasattr(decision, 'metadata'):
                decision.metadata.update({"validation_notes": validation_notes})
            
            print(f"   📊 Result: {'🚨 COMPLIANCE REQUIRED' if decision.needs_geo_compliance else '✅ NO COMPLIANCE NEEDED'}")
            print(f"   📏 Confidence: {decision.confidence:.2f}")
            print(f"   📋 Regulations: {', '.join(decision.regulations) if decision.regulations else 'None'}")
            
            if validation_notes:
                print(f"   🔍 Validation:")
                for note in validation_notes:
                    print(f"      {note}")
            
            return decision
            
        except Exception as e:
            print(f"❌ Analysis failed for {feature.feature_id}: {e}")
            # Create a failure decision
            return Decision(
                feature_id=feature.feature_id,
                needs_geo_compliance=False,
                reasoning=f"Analysis failed: {str(e)}",
                regulations=[],
                signals=[],
                citations=[],
                confidence=0.0,
                matched_rules=[]
            )
    
    async def run_batch_analysis(self, features: List[Dict]) -> List[Decision]:
        """Run analysis on multiple features"""
        print(f"\n🎯 Running batch analysis on {len(features)} features...")
        
        decisions = []
        
        for feature_config in features:
            decision = await self.analyze_feature(feature_config)
            decisions.append(decision)
            self.results.append({
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "feature_id": decision.feature_id,
                "needs_compliance": decision.needs_geo_compliance,
                "regulations": decision.regulations,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning
            })
        
        return decisions
    
    def generate_summary_report(self, decisions: List[Decision], features: List[Dict]) -> Dict[str, Any]:
        """Generate a summary report of the analysis"""
        total_features = len(decisions)
        compliance_required = sum(1 for d in decisions if d.needs_geo_compliance)
        
        # Regulation frequency analysis
        regulation_counts = {}
        for decision in decisions:
            for reg in decision.regulations:
                regulation_counts[reg] = regulation_counts.get(reg, 0) + 1
        
        # Confidence analysis
        avg_confidence = sum(d.confidence for d in decisions) / total_features if total_features > 0 else 0
        
        # Validation results if available
        validation_summary = {"correct_predictions": 0, "total_validatable": 0}
        for i, decision in enumerate(decisions):
            if i < len(features):
                feature_config = features[i]
                expected = feature_config.get("expected_compliance")
                if expected is not None:
                    validation_summary["total_validatable"] += 1
                    if decision.needs_geo_compliance == expected:
                        validation_summary["correct_predictions"] += 1
        
        accuracy = 0
        if validation_summary["total_validatable"] > 0:
            accuracy = validation_summary["correct_predictions"] / validation_summary["total_validatable"]
        
        return {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_features_analyzed": total_features,
                "features_requiring_compliance": compliance_required,
                "compliance_rate": compliance_required / total_features if total_features > 0 else 0,
                "average_confidence": avg_confidence,
                "prediction_accuracy": accuracy
            },
            "regulation_frequency": regulation_counts,
            "validation": validation_summary
        }
    
    async def export_results(self, decisions: List[Decision], summary: Dict[str, Any]):
        """Export results to various formats"""
        print(f"\n📊 Exporting results...")
        
        # Export to CSV using the evidence system
        csv_path = evidence_system.export_csv(decisions, f"data/analysis_results_{self.session_id}.csv")
        print(f"   📄 CSV exported: {csv_path}")
        
        # Export summary as JSON
        summary_path = f"data/analysis_summary_{self.session_id}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"   📄 Summary exported: {summary_path}")
        
        # Create evidence ZIP
        try:
            zip_path = f"analysis_evidence_{self.session_id}.zip"
            zip_data = evidence_system.make_evidence_zip()
            with open(zip_path, 'wb') as f:
                f.write(zip_data)
            print(f"   📦 Evidence ZIP created: {zip_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to create evidence ZIP: {e}")
        
        return {
            "csv_path": csv_path,
            "summary_path": summary_path,
            "zip_path": zip_path if 'zip_path' in locals() else None
        }
    
    async def run_complete_analysis(self, inputs_file: str = "inputs.yaml"):
        """Run the complete analysis workflow"""
        print(f"🚀 Starting GeoGov Analysis - Session: {self.session_id}")
        print("=" * 60)
        
        try:
            # Load inputs
            inputs = await self.load_inputs(inputs_file)
            regulations = inputs.get("regulations", [])
            test_features = inputs.get("test_features", [])
            
            if not test_features:
                print("❌ No test features found in inputs")
                return
            
            # Refresh knowledge base if regulations are provided
            kb_result = None
            if regulations:
                kb_result = await self.refresh_knowledge_base(regulations)
            
            # Run analysis
            decisions = await self.run_batch_analysis(test_features)
            
            # Generate summary
            summary = self.generate_summary_report(decisions, test_features)
            
            # Export results
            export_paths = await self.export_results(decisions, summary)
            
            # Print final summary
            print(f"\n🎉 Analysis Complete!")
            print("=" * 60)
            print(f"📊 Features Analyzed: {summary['summary']['total_features_analyzed']}")
            print(f"🚨 Compliance Required: {summary['summary']['features_requiring_compliance']} ({summary['summary']['compliance_rate']:.1%})")
            print(f"🎯 Average Confidence: {summary['summary']['average_confidence']:.2f}")
            if summary['summary']['prediction_accuracy'] > 0:
                print(f"✅ Prediction Accuracy: {summary['summary']['prediction_accuracy']:.1%}")
            
            if summary['regulation_frequency']:
                print(f"\n📋 Most Triggered Regulations:")
                sorted_regs = sorted(summary['regulation_frequency'].items(), key=lambda x: x[1], reverse=True)
                for reg, count in sorted_regs[:5]:
                    print(f"   • {reg}: {count} features")
            
            print(f"\n📁 Results exported to:")
            print(f"   • {export_paths['csv_path']}")
            print(f"   • {export_paths['summary_path']}")
            if export_paths['zip_path']:
                print(f"   • {export_paths['zip_path']}")
            
            return {
                "decisions": decisions,
                "summary": summary,
                "export_paths": export_paths
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            raise
        finally:
            # Cleanup
            await scraping_aggregator.close()


# CLI Interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run GeoGov compliance analysis")
    parser.add_argument("--inputs", "-i", default="inputs.yaml", help="Input configuration file")
    parser.add_argument("--feature", "-f", help="Analyze single feature by ID")
    parser.add_argument("--export-only", action="store_true", help="Only export existing results")
    
    args = parser.parse_args()
    
    runner = AnalysisRunner()
    
    if args.export_only:
        print("📊 Export mode - processing existing data...")
        # TODO: Implement export-only mode
        return
    
    if args.feature:
        # Single feature analysis
        inputs = await runner.load_inputs(args.inputs)
        features = inputs.get("test_features", [])
        
        target_feature = next((f for f in features if f.get("feature_id") == args.feature), None)
        if not target_feature:
            print(f"❌ Feature {args.feature} not found in inputs")
            return
        
        decision = await runner.analyze_feature(target_feature)
        print(f"\n✅ Analysis complete for {decision.feature_id}")
    else:
        # Full batch analysis
        await runner.run_complete_analysis(args.inputs)


if __name__ == "__main__":
    asyncio.run(main())
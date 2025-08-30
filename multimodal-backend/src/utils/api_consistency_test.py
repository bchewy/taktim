"""
Test script to check if government APIs return different results over time
This helps determine if daily consistency monitoring is needed
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from .legal_apis import LegalResearchAggregator
import sqlite3

class APIConsistencyTester:
    """Test consistency of government API responses over time"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Path(__file__).parent.parent.parent / "data" / "api_consistency.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database to store API responses over time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response_hash TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    result_count INTEGER,
                    INDEX(api_name, query),
                    INDEX(timestamp)
                )
            """)
    
    def _hash_response(self, response_data):
        """Create hash of response for comparison"""
        # Remove timestamps and volatile data for stable comparison
        stable_data = {}
        
        if isinstance(response_data, dict):
            for key, value in response_data.items():
                if key not in ['research_timestamp', 'timestamp', 'dateIssued']:
                    if isinstance(value, list):
                        # For lists, extract key identifying information
                        stable_items = []
                        for item in value:
                            if isinstance(item, dict):
                                stable_item = {k: v for k, v in item.items() 
                                             if k not in ['dateIssued', 'lastModified', 'timestamp']}
                                stable_items.append(stable_item.get('title', str(stable_item)))
                            else:
                                stable_items.append(str(item))
                        stable_data[key] = stable_items
                    elif isinstance(value, dict):
                        stable_value = {k: v for k, v in value.items() 
                                      if k not in ['research_timestamp', 'timestamp', 'dateIssued']}
                        stable_data[key] = stable_value
                    else:
                        stable_data[key] = value
        
        content = json.dumps(stable_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def test_api_consistency(self, queries: list = None):
        """Test consistency of API responses for given queries"""
        if queries is None:
            queries = [
                "children online privacy",
                "social media minors",
                "data protection"
            ]
        
        aggregator = LegalResearchAggregator()
        results = {}
        
        try:
            for query in queries:
                print(f"🔍 Testing query: '{query}'")
                
                # Get current API response
                response = await aggregator.research_topic(query)
                response_hash = self._hash_response(response)
                
                # Count results
                result_count = 0
                if 'federal_regulations' in response:
                    result_count += len(response['federal_regulations'])
                if 'congressional_bills' in response:
                    result_count += len(response['congressional_bills'])
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO api_responses 
                        (api_name, query, response_hash, response_data, timestamp, result_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        "legal_research_aggregator",
                        query,
                        response_hash,
                        json.dumps(response),
                        datetime.utcnow(),
                        result_count
                    ))
                
                # Check for previous responses
                consistency_info = self._check_consistency(query)
                
                results[query] = {
                    'current_hash': response_hash,
                    'result_count': result_count,
                    'consistency_info': consistency_info,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                print(f"✅ Query '{query}': {result_count} results, Hash: {response_hash[:8]}...")
                
                # Small delay to be respectful to APIs
                await asyncio.sleep(1)
        
        finally:
            await aggregator.close()
        
        return results
    
    def _check_consistency(self, query: str):
        """Check consistency of responses for a query over time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT response_hash, result_count, timestamp
                FROM api_responses 
                WHERE api_name = 'legal_research_aggregator' AND query = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (query,))
            
            responses = cursor.fetchall()
            
            if len(responses) <= 1:
                return {
                    'status': 'insufficient_data',
                    'total_responses': len(responses),
                    'unique_hashes': 0,
                    'consistency_percentage': 0
                }
            
            unique_hashes = set(row['response_hash'] for row in responses)
            result_counts = [row['result_count'] for row in responses]
            
            # Calculate consistency metrics
            most_common_hash = max(set(row['response_hash'] for row in responses), 
                                 key=lambda x: sum(1 for row in responses if row['response_hash'] == x))
            consistent_responses = sum(1 for row in responses if row['response_hash'] == most_common_hash)
            consistency_percentage = (consistent_responses / len(responses)) * 100
            
            return {
                'status': 'analyzed',
                'total_responses': len(responses),
                'unique_hashes': len(unique_hashes),
                'consistency_percentage': consistency_percentage,
                'result_count_variance': {
                    'min': min(result_counts),
                    'max': max(result_counts),
                    'latest': result_counts[0] if result_counts else 0
                },
                'time_span_days': (responses[0]['timestamp'] - responses[-1]['timestamp']).days if len(responses) > 1 else 0
            }
    
    def generate_consistency_report(self):
        """Generate a comprehensive consistency report"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get summary by query
            cursor = conn.execute("""
                SELECT 
                    query,
                    COUNT(*) as total_tests,
                    COUNT(DISTINCT response_hash) as unique_responses,
                    MIN(result_count) as min_results,
                    MAX(result_count) as max_results,
                    AVG(result_count) as avg_results,
                    MIN(timestamp) as first_test,
                    MAX(timestamp) as latest_test
                FROM api_responses 
                GROUP BY query
                ORDER BY total_tests DESC
            """)
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'summary': {},
                'recommendations': []
            }
            
            for row in cursor.fetchall():
                consistency_percentage = ((row['total_tests'] - row['unique_responses'] + 1) / row['total_tests']) * 100 if row['total_tests'] > 0 else 0
                
                query_summary = {
                    'total_tests': row['total_tests'],
                    'unique_responses': row['unique_responses'],
                    'consistency_percentage': consistency_percentage,
                    'result_count_variance': {
                        'min': row['min_results'],
                        'max': row['max_results'],
                        'avg': round(row['avg_results'], 1)
                    },
                    'test_period_days': (datetime.fromisoformat(row['latest_test']) - 
                                       datetime.fromisoformat(row['first_test'])).days
                }
                
                report['summary'][row['query']] = query_summary
                
                # Generate recommendations
                if query_summary['consistency_percentage'] < 80:
                    report['recommendations'].append(
                        f"Query '{row['query']}' shows {consistency_percentage:.1f}% consistency - consider implementing result caching"
                    )
                
                if query_summary['result_count_variance']['max'] - query_summary['result_count_variance']['min'] > 2:
                    report['recommendations'].append(
                        f"Query '{row['query']}' shows significant result count variance ({row['min_results']}-{row['max_results']}) - APIs are updating frequently"
                    )
        
        return report
    
    async def run_daily_test(self):
        """Run the consistency test (designed to be called daily)"""
        print("🕐 Running daily API consistency test...")
        
        results = await self.test_api_consistency()
        
        # Check if we should alert about inconsistencies
        alerts = []
        for query, result in results.items():
            consistency_info = result['consistency_info']
            
            if consistency_info['status'] == 'analyzed':
                if consistency_info['consistency_percentage'] < 80:
                    alerts.append(
                        f"⚠️  Query '{query}' consistency dropped to {consistency_info['consistency_percentage']:.1f}%"
                    )
                
                count_variance = consistency_info['result_count_variance']
                if count_variance['max'] - count_variance['min'] > 3:
                    alerts.append(
                        f"📊 Query '{query}' result count varies significantly: {count_variance['min']}-{count_variance['max']}"
                    )
        
        if alerts:
            print("\n🚨 CONSISTENCY ALERTS:")
            for alert in alerts:
                print(alert)
        else:
            print("✅ No consistency issues detected")
        
        return results, alerts


# CLI interface for easy testing
async def main():
    """Command line interface for API consistency testing"""
    import sys
    
    tester = APIConsistencyTester()
    
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        # Generate report
        report = tester.generate_consistency_report()
        print("📊 API Consistency Report:")
        print(json.dumps(report, indent=2))
    else:
        # Run consistency test
        results, alerts = await tester.run_daily_test()
        
        print(f"\n📋 Test Summary:")
        for query, result in results.items():
            print(f"  {query}: {result['result_count']} results, {result['consistency_info']['status']}")


if __name__ == "__main__":
    asyncio.run(main())
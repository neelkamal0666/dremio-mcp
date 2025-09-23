#!/usr/bin/env python3
"""
Test script for Flask API
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class FlaskAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        print("🔍 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_list_tables(self) -> bool:
        """Test tables endpoint"""
        print("\n🔍 Testing tables endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/tables")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tables endpoint passed: Found {data['data']['count']} tables")
                return True
            else:
                print(f"❌ Tables endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Tables endpoint error: {e}")
            return False
    
    def test_query(self, question: str, expected_type: str = None) -> bool:
        """Test query endpoint"""
        print(f"\n🔍 Testing query: '{question}'")
        try:
            payload = {"question": question}
            response = self.session.post(
                f"{self.base_url}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query successful: {data['query_type']}")
                print(f"   Success: {data['success']}")
                
                if 'data' in data:
                    if 'row_count' in data['data']:
                        print(f"   Rows: {data['data']['row_count']}")
                    if 'total_count' in data['data']:
                        print(f"   Total count: {data['data']['total_count']}")
                    if 'tables' in data['data']:
                        print(f"   Tables: {len(data['data']['tables'])}")
                    if 'message' in data['data']:
                        print(f"   Message: {data['data']['message']}")
                
                if expected_type and data.get('query_type') != expected_type:
                    print(f"⚠️  Expected type '{expected_type}', got '{data.get('query_type')}'")
                
                return True
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Query error: {e}")
            return False
    
    def test_table_metadata(self, table_name: str) -> bool:
        """Test table metadata endpoint"""
        print(f"\n🔍 Testing table metadata: '{table_name}'")
        try:
            response = self.session.get(f"{self.base_url}/table/{table_name}/metadata")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Table metadata successful")
                print(f"   Columns: {data['data']['column_count']}")
                if data['data']['wiki_description']:
                    print(f"   Wiki: {len(data['data']['wiki_description'])} chars")
                return True
            else:
                print(f"❌ Table metadata failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Table metadata error: {e}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive test suite"""
        print("🧪 Starting Flask API Comprehensive Test")
        print("=" * 50)
        
        all_passed = True
        
        # Test 1: Health check
        if not self.test_health():
            all_passed = False
        
        # Test 2: List tables
        if not self.test_list_tables():
            all_passed = False
        
        # Test 3: Table exploration queries
        table_queries = [
            "show me all tables",
            "what tables are available",
            "list all data"
        ]
        
        for query in table_queries:
            if not self.test_query(query, "table_exploration"):
                all_passed = False
        
        # Test 4: Count queries
        count_queries = [
            "how many accounts are there",
            "count the records in demographic details",
            "what is the total number of users"
        ]
        
        for query in count_queries:
            if not self.test_query(query, "count_query"):
                all_passed = False
        
        # Test 5: Aggregation queries
        aggregation_queries = [
            "what is the average age of users",
            "show me the total revenue",
            "what is the maximum score",
            "give me statistics for the accounts table",
            "what is the minimum value"
        ]
        
        for query in aggregation_queries:
            if not self.test_query(query, "aggregation_query"):
                all_passed = False
        
        # Test 6: Field selection queries
        field_selection_queries = [
            "show me only the names and emails",
            "just the IDs and ages",
            "what are the names in the accounts table",
            "get me only the email addresses"
        ]
        
        for query in field_selection_queries:
            if not self.test_query(query, "field_selection_query"):
                all_passed = False
        
        # Test 7: Data queries
        data_queries = [
            "show me top 10 accounts",
            "get demographic details",
            "show me customer information"
        ]
        
        for query in data_queries:
            if not self.test_query(query, "data_query"):
                all_passed = False
        
        # Test 8: Metadata queries
        metadata_queries = [
            "describe the accounts table",
            "what is the structure of demographic details",
            "tell me about the customer data"
        ]
        
        for query in metadata_queries:
            if not self.test_query(query, "metadata_request"):
                all_passed = False
        
        # Test 9: General queries
        general_queries = [
            "help me understand the data",
            "what can I do with this system",
            "show me something interesting"
        ]
        
        for query in general_queries:
            if not self.test_query(query, "general"):
                all_passed = False
        
        # Test 10: Table metadata (if we have tables)
        try:
            response = self.session.get(f"{self.base_url}/tables")
            if response.status_code == 200:
                data = response.json()
                tables = data['data']['tables']
                if tables:
                    # Test metadata for first few tables
                    for table in tables[:3]:
                        if not self.test_table_metadata(table):
                            all_passed = False
        except Exception as e:
            print(f"⚠️  Could not test table metadata: {e}")
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return all_passed


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Flask API')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--wait', type=int, default=5, help='Wait time for server startup')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Flask API tests against {args.url}")
    print(f"⏳ Waiting {args.wait} seconds for server startup...")
    time.sleep(args.wait)
    
    tester = FlaskAPITester(args.url)
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

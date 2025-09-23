#!/usr/bin/env python3
"""
Enhanced Query Examples for Flask API
Demonstrates various query types that don't return all columns
"""

import requests
import json
import time

class EnhancedQueryExamples:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_query(self, question: str, expected_type: str = None):
        """Test a single query"""
        print(f"\n🔍 Testing: '{question}'")
        try:
            payload = {"question": question}
            response = self.session.post(
                f"{self.base_url}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data['query_type']}")
                
                if 'data' in data:
                    if 'message' in data['data']:
                        print(f"   📝 Message: {data['data']['message']}")
                    
                    if 'row_count' in data['data']:
                        print(f"   📊 Rows: {data['data']['row_count']}")
                    
                    if 'columns' in data['data']:
                        print(f"   📋 Columns: {data['data']['columns']}")
                    
                    if 'aggregation_type' in data['data']:
                        print(f"   🧮 Aggregation: {data['data']['aggregation_type']}")
                    
                    if 'selected_columns' in data['data']:
                        print(f"   🎯 Selected: {data['data']['selected_columns']}")
                    
                    if 'count_value' in data['data']:
                        print(f"   🔢 Count: {data['data']['count_value']}")
                
                if expected_type and data.get('query_type') != expected_type:
                    print(f"⚠️  Expected '{expected_type}', got '{data.get('query_type')}'")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_examples(self):
        """Run comprehensive examples of enhanced queries"""
        print("🚀 Enhanced Query Examples for Flask API")
        print("=" * 60)
        
        # Wait for server
        print("⏳ Waiting for server to be ready...")
        time.sleep(2)
        
        # Test server health
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print("❌ Server not ready. Please start the Flask API first.")
                return False
            print("✅ Server is ready!")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("📊 TESTING ENHANCED QUERY TYPES")
        print("=" * 60)
        
        # 1. Count Queries
        print("\n🔢 COUNT QUERIES")
        print("-" * 30)
        count_examples = [
            "how many accounts are there",
            "count the records in demographic details",
            "what is the total number of users",
            "how many records are in the projects table"
        ]
        
        for example in count_examples:
            self.test_query(example, "count_query")
        
        # 2. Aggregation Queries
        print("\n🧮 AGGREGATION QUERIES")
        print("-" * 30)
        aggregation_examples = [
            "what is the average age of users",
            "show me the total revenue",
            "what is the maximum score",
            "give me statistics for the accounts table",
            "what is the minimum value",
            "what is the sum of all amounts",
            "show me the average rating"
        ]
        
        for example in aggregation_examples:
            self.test_query(example, "aggregation_query")
        
        # 3. Field Selection Queries
        print("\n🎯 FIELD SELECTION QUERIES")
        print("-" * 30)
        field_selection_examples = [
            "show me only the names and emails",
            "just the IDs and ages",
            "what are the names in the accounts table",
            "get me only the email addresses",
            "show me only the customer names",
            "just the user IDs and scores"
        ]
        
        for example in field_selection_examples:
            self.test_query(example, "field_selection_query")
        
        # 4. Table Exploration
        print("\n📋 TABLE EXPLORATION")
        print("-" * 30)
        table_exploration_examples = [
            "show me all tables",
            "what tables are available",
            "list all data sources",
            "what data do we have"
        ]
        
        for example in table_exploration_examples:
            self.test_query(example, "table_exploration")
        
        # 5. Metadata Requests
        print("\n📖 METADATA REQUESTS")
        print("-" * 30)
        metadata_examples = [
            "describe the accounts table",
            "what is the structure of demographic details",
            "tell me about the customer data",
            "explain the projects table"
        ]
        
        for example in metadata_examples:
            self.test_query(example, "metadata_request")
        
        # 6. Data Queries (Full Data)
        print("\n📊 DATA QUERIES")
        print("-" * 30)
        data_examples = [
            "show me top 10 accounts",
            "get demographic details",
            "show me customer information",
            "get me some sample data"
        ]
        
        for example in data_examples:
            self.test_query(example, "data_query")
        
        print("\n" + "=" * 60)
        print("🎉 Enhanced Query Examples Completed!")
        print("=" * 60)
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Query Examples')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    
    args = parser.parse_args()
    
    examples = EnhancedQueryExamples(args.url)
    success = examples.run_examples()
    
    if success:
        print("\n✅ All examples completed successfully!")
        print("\n📚 Query Type Summary:")
        print("   🔢 Count Queries: 'how many', 'count', 'total number'")
        print("   🧮 Aggregation: 'average', 'sum', 'maximum', 'statistics'")
        print("   🎯 Field Selection: 'only the', 'just the', 'specific fields'")
        print("   📋 Table Exploration: 'show tables', 'list data'")
        print("   📖 Metadata: 'describe', 'structure', 'explain'")
        print("   📊 Data Queries: 'show me', 'get data', 'sample'")
    else:
        print("\n❌ Some examples failed. Check server status.")

if __name__ == '__main__':
    main()

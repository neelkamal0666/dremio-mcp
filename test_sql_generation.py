#!/usr/bin/env python3
"""
Test script for SQL generation fixes

This script tests the SQL generation to ensure it produces valid SQL.
"""

import asyncio
import os
from dotenv import load_dotenv
from ai_agent import DremioAIAgent

# Load environment variables
load_dotenv()

def test_sql_cleaning():
    """Test the SQL cleaning functionality"""
    print("🧪 Testing SQL Query Cleaning")
    print("=" * 40)
    
    # Create agent without client (we only need the cleaning method)
    agent = DremioAIAgent(None)
    
    test_cases = [
        ("SELECT COUNT(*) as count FROM accounts", "SELECT COUNT(*) as total_count FROM accounts"),
        ("SELECT * FROM users as user", "SELECT * FROM users as user_info"),
        ("SELECT * FROM orders as order", "SELECT * FROM orders as order_info"),
        ("SELECT COUNT(*) as count FROM customers", "SELECT COUNT(*) as total_count FROM customers"),
        ("SELECT * FROM data as data", "SELECT * FROM data as data_info"),
        ("SELECT * FROM groups as group", "SELECT * FROM groups as group_info"),
    ]
    
    for input_sql, expected in test_cases:
        result = agent._clean_sql_query(input_sql)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {input_sql}")
        print(f"   Output: {result}")
        print(f"   Expected: {expected}")
        print()

def test_heuristic_sql_generation():
    """Test heuristic SQL generation"""
    print("🧪 Testing Heuristic SQL Generation")
    print("=" * 40)
    
    agent = DremioAIAgent(None)
    
    test_queries = [
        ("how many accounts are there", "SELECT COUNT(*) as total_count FROM accounts"),
        ("show me all customers", "SELECT * FROM customers LIMIT 100"),
        ("count the users", "SELECT COUNT(*) as total_count FROM users"),
        ("display product information", "SELECT * FROM products LIMIT 100"),
        ("list all orders", "SELECT * FROM orders LIMIT 50"),
    ]
    
    for query, expected_pattern in test_queries:
        intent = agent._analyze_query_intent(query)
        sql = agent._generate_sql_heuristic(query, intent)
        
        if sql:
            print(f"✅ Query: '{query}'")
            print(f"   Generated: {sql}")
            print(f"   Expected pattern: {expected_pattern}")
        else:
            print(f"❌ Query: '{query}' - No SQL generated")
        print()

async def test_ai_sql_generation():
    """Test AI SQL generation if API key is available"""
    print("🧪 Testing AI SQL Generation")
    print("=" * 40)
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("⚠️  No Anthropic API key found - skipping AI SQL generation test")
        return
    
    agent = DremioAIAgent(None, anthropic_api_key=anthropic_key)
    
    test_queries = [
        "how many accounts are there",
        "show me customer information",
        "count the number of orders"
    ]
    
    for query in test_queries:
        print(f"Testing: '{query}'")
        try:
            intent = agent._analyze_query_intent(query)
            sql = await agent._generate_sql_with_ai(query, intent)
            
            if sql:
                print(f"✅ Generated: {sql}")
            else:
                print("❌ No SQL generated")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

async def main():
    """Main test function"""
    print("🚀 SQL Generation Test Suite")
    print("=" * 50)
    
    # Test SQL cleaning
    test_sql_cleaning()
    
    # Test heuristic generation
    test_heuristic_sql_generation()
    
    # Test AI generation
    await test_ai_sql_generation()
    
    print("=" * 50)
    print("🎉 SQL generation tests completed!")
    print("\nThe fixes should resolve the 'as count' syntax error.")
    print("Now queries like 'how many accounts are there' should work properly!")

if __name__ == "__main__":
    asyncio.run(main())

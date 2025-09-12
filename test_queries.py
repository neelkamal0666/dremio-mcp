#!/usr/bin/env python3
"""
Test script for query processing

This script tests the query processing without requiring Dremio connection.
"""

import asyncio
import os
from dotenv import load_dotenv
from ai_agent import DremioAIAgent

# Load environment variables
load_dotenv()

async def test_query_processing():
    """Test query processing with various scenarios"""
    print("🧪 Testing Query Processing")
    print("=" * 50)
    
    # Create agent without client (we only need intent analysis and SQL generation)
    agent = DremioAIAgent(None)
    
    # Set Anthropic key if available
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        agent.set_anthropic_key(anthropic_key)
        print("✅ Using Anthropic API for enhanced SQL generation")
    else:
        print("⚠️  No Anthropic API key - using heuristic SQL generation only")
    
    test_queries = [
        "how many accounts are there",
        "show me demographic details",
        "show me all tables",
        "what columns are in the orders table",
        "count the number of customers",
        "display user information"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 30)
        
        try:
            result = await agent.process_query(query)
            
            if result.get('success'):
                print("✅ Query processed successfully")
                if 'query' in result:
                    print(f"Generated SQL: {result['query']}")
                if 'tables' in result:
                    print(f"Found {result.get('count', 0)} tables")
            else:
                print(f"❌ Query failed: {result.get('error')}")
                if 'suggestion' in result:
                    print(f"💡 Suggestion: {result['suggestion']}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Query processing test completed!")

if __name__ == "__main__":
    asyncio.run(test_query_processing())

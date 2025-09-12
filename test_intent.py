#!/usr/bin/env python3
"""
Test script for intent analysis

This script tests the intent analysis without requiring Dremio connection.
"""

import os
from dotenv import load_dotenv
from ai_agent import DremioAIAgent

# Load environment variables
load_dotenv()

def test_intent_analysis():
    """Test intent analysis for various queries"""
    print("🧪 Testing Intent Analysis")
    print("=" * 50)
    
    # Create agent without client (we only need intent analysis)
    agent = DremioAIAgent(None)
    
    test_queries = [
        "show me all tables",
        "list all tables",
        "what tables are available",
        "show me the schema of customer table",
        "what columns are in the orders table",
        "how many customers do we have",
        "show me the first 10 rows from products",
        "find tables with customer in the name",
        "tell me about the sales table",
        "what is the description of the orders table"
    ]
    
    for query in test_queries:
        intent = agent._analyze_query_intent(query)
        print(f"Query: '{query}'")
        print(f"Intent: {intent['type']}")
        if intent.get('filters'):
            print(f"Filters: {intent['filters']}")
        if intent.get('entities'):
            print(f"Entities: {intent['entities']}")
        print("-" * 30)
    
    print("✅ Intent analysis test completed!")

if __name__ == "__main__":
    test_intent_analysis()

#!/usr/bin/env python3
"""
Test script to verify Anthropic API connection
"""

import os
import asyncio
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

async def test_anthropic_connection():
    """Test Anthropic API connection"""
    print("🧪 Testing Anthropic API Connection")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize client
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
        
        # Test API call
        def _call_anthropic():
            return client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.1,
                messages=[{"role": "user", "content": "Say 'Hello, world!'"}]
            )
        
        response = await asyncio.to_thread(_call_anthropic)
        print(f"✅ API call successful: {response.content[0].text}")
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
        
        # Try to get more specific error information
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")

if __name__ == "__main__":
    asyncio.run(test_anthropic_connection())

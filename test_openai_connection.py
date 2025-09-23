#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("🧪 Testing OpenAI API Connection")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test API call
        def _call_openai():
            return client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=100,
                temperature=0.1,
                messages=[{"role": "user", "content": "Say 'Hello, world!'"}]
            )
        
        response = await asyncio.to_thread(_call_openai)
        print(f"✅ API call successful: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
        
        # Try to get more specific error information
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            print(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")

if __name__ == "__main__":
    asyncio.run(test_openai_connection())

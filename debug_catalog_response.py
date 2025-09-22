#!/usr/bin/env python3
"""
Debug script to check catalog response format
"""

import os
import json
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def debug_catalog_response():
    """Debug the catalog API response format"""
    print("🔍 Debugging Catalog Response Format")
    print("=" * 40)
    
    # Configuration
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true'
    }
    
    try:
        # Initialize client
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Failed to authenticate with Dremio")
            return
        
        print("✅ Successfully connected to Dremio!")
        
        # Test catalog API response
        print("\n📋 Testing catalog API response:")
        search_url = f"{client.api_v3}/catalog"
        response = client.session.get(search_url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                catalog_data = response.json()
                print(f"Response type: {type(catalog_data)}")
                
                if isinstance(catalog_data, dict):
                    print(f"Response keys: {list(catalog_data.keys())}")
                    
                    if 'data' in catalog_data:
                        items = catalog_data['data']
                        print(f"Data items count: {len(items)}")
                        
                        if items:
                            print(f"First item type: {type(items[0])}")
                            if isinstance(items[0], dict):
                                print(f"First item keys: {list(items[0].keys())}")
                                print(f"First item: {json.dumps(items[0], indent=2)}")
                            else:
                                print(f"First item: {items[0]}")
                    else:
                        print("No 'data' key found in response")
                        print(f"Full response: {json.dumps(catalog_data, indent=2)}")
                else:
                    print(f"Response is not a dict: {catalog_data}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}...")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Error response: {response.text}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    debug_catalog_response()

git #!/usr/bin/env python3
"""
Debug script for Dremio Wiki API issues

This script helps debug why wiki content is not being found.
"""

import os
import requests
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def debug_wiki_api():
    """Debug the wiki API calls"""
    print("🔍 Debugging Dremio Wiki API")
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
        
        # Get a sample table to test with
        tables = client.list_tables()
        if not tables:
            print("❌ No tables found")
            return
        
        # Test with first few tables
        test_tables = tables[:5]
        print(f"\n📋 Testing wiki API with {len(test_tables)} tables:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\n🔍 Testing: {table_path}")
            
            # Test the wiki URL construction
            wiki_url = f"{client.api_v3}/catalog/by-path/{table_path}/collaboration/wiki"
            print(f"   Wiki URL: {wiki_url}")
            
            try:
                # Make the request manually to see the response
                response = client.session.get(wiki_url)
                print(f"   Status Code: {response.status_code}")
                print(f"   Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    wiki_data = response.json()
                    print(f"   Response JSON keys: {list(wiki_data.keys())}")
                    
                    if 'text' in wiki_data:
                        wiki_text = wiki_data['text']
                        if wiki_text and wiki_text.strip():
                            print(f"   ✅ Wiki content found: {len(wiki_text)} characters")
                            print(f"   Preview: {wiki_text[:100]}...")
                        else:
                            print(f"   ❌ Wiki content is empty")
                    else:
                        print(f"   ❌ No 'text' field in response")
                        print(f"   Full response: {wiki_data}")
                else:
                    print(f"   ❌ Error response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        # Test alternative wiki endpoints
        print(f"\n🔍 Testing alternative wiki endpoints:")
        
        # Try the old wiki endpoint format
        for schema, table in test_tables[:2]:
            table_path = f"{schema}.{table}"
            
            # Try different URL formats
            alternative_urls = [
                f"{client.api_v3}/catalog/by-path/{table_path}/collaboration/wiki",
                f"{client.api_v3}/catalog/by-path/{table_path}/wiki",
                f"{client.api_v3}/catalog/by-path/{table_path}/collaboration",
                f"{client.api_v3}/catalog/{table_path}/collaboration/wiki",
            ]
            
            for alt_url in alternative_urls:
                try:
                    response = client.session.get(alt_url)
                    print(f"   {alt_url} -> {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        if 'text' in data and data['text']:
                            print(f"   ✅ Found wiki content at: {alt_url}")
                            break
                except Exception as e:
                    print(f"   ❌ {alt_url} -> Error: {e}")
        
        # Test catalog item details to see if wiki info is there
        print(f"\n🔍 Testing catalog item details:")
        
        for schema, table in test_tables[:2]:
            table_path = f"{schema}.{table}"
            catalog_url = f"{client.api_v3}/catalog/by-path/{table_path}"
            
            try:
                response = client.session.get(catalog_url)
                if response.status_code == 200:
                    catalog_data = response.json()
                    print(f"   {table_path} catalog keys: {list(catalog_data.keys())}")
                    
                    # Look for wiki-related fields
                    wiki_fields = [k for k in catalog_data.keys() if 'wiki' in k.lower() or 'collaboration' in k.lower()]
                    if wiki_fields:
                        print(f"   Wiki-related fields: {wiki_fields}")
                        for field in wiki_fields:
                            print(f"     {field}: {catalog_data[field]}")
                    else:
                        print(f"   No wiki-related fields found")
                        
            except Exception as e:
                print(f"   ❌ Error getting catalog details: {e}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_wiki_api()

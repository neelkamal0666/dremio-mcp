#!/usr/bin/env python3
"""
Enhanced debug script for Dremio Wiki API issues

This script tests different approaches to access wiki content.
"""

import os
import requests
import json
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def debug_wiki_api_v2():
    """Debug the wiki API calls with different approaches"""
    print("🔍 Enhanced Dremio Wiki API Debug")
    print("=" * 50)
    
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
        test_tables = tables[:3]
        print(f"\n📋 Testing wiki API with {len(test_tables)} tables:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\n🔍 Testing: {table_path}")
            
            # Method 1: Get catalog item details first to find the ID
            print("   Method 1: Getting catalog item details...")
            catalog_url = f"{client.api_v3}/catalog/by-path/{table_path}"
            
            try:
                response = client.session.get(catalog_url)
                if response.status_code == 200:
                    catalog_data = response.json()
                    print(f"   ✅ Catalog data retrieved")
                    print(f"   ID: {catalog_data.get('id', 'N/A')}")
                    print(f"   Type: {catalog_data.get('entityType', 'N/A')}")
                    print(f"   Path: {catalog_data.get('path', 'N/A')}")
                    
                    # Check if there are any collaboration-related fields
                    collaboration_fields = [k for k in catalog_data.keys() if 'collaboration' in k.lower() or 'wiki' in k.lower()]
                    if collaboration_fields:
                        print(f"   Collaboration fields: {collaboration_fields}")
                        for field in collaboration_fields:
                            print(f"     {field}: {catalog_data[field]}")
                    
                    # Method 2: Try wiki API with the ID
                    entity_id = catalog_data.get('id')
                    if entity_id:
                        print(f"   Method 2: Trying wiki API with ID...")
                        wiki_url_by_id = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                        print(f"   Wiki URL by ID: {wiki_url_by_id}")
                        
                        try:
                            wiki_response = client.session.get(wiki_url_by_id)
                            print(f"   Status Code: {wiki_response.status_code}")
                            
                            if wiki_response.status_code == 200:
                                wiki_data = wiki_response.json()
                                print(f"   ✅ Wiki content found!")
                                print(f"   Response keys: {list(wiki_data.keys())}")
                                
                                if 'text' in wiki_data:
                                    wiki_text = wiki_data['text']
                                    if wiki_text and wiki_text.strip():
                                        print(f"   Content length: {len(wiki_text)} characters")
                                        print(f"   Preview: {wiki_text[:200]}...")
                                    else:
                                        print(f"   ❌ Wiki content is empty")
                                else:
                                    print(f"   ❌ No 'text' field in response")
                                    print(f"   Full response: {json.dumps(wiki_data, indent=2)}")
                            else:
                                print(f"   ❌ Wiki API error: {wiki_response.text}")
                                
                        except Exception as e:
                            print(f"   ❌ Wiki API exception: {e}")
                    
                    # Method 3: Try different URL patterns
                    print(f"   Method 3: Trying alternative URL patterns...")
                    alternative_patterns = [
                        f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki",
                        f"{client.api_v3}/catalog/{entity_id}/wiki",
                        f"{client.api_v3}/catalog/{entity_id}/collaboration",
                        f"{client.api_v3}/catalog/by-path/{table_path}/collaboration/wiki",
                        f"{client.api_v3}/catalog/by-path/{table_path}/wiki",
                    ]
                    
                    for pattern in alternative_patterns:
                        try:
                            resp = client.session.get(pattern)
                            print(f"     {pattern} -> {resp.status_code}")
                            if resp.status_code == 200:
                                data = resp.json()
                                if 'text' in data and data['text']:
                                    print(f"     ✅ Found wiki content at: {pattern}")
                                    break
                        except Exception as e:
                            print(f"     ❌ {pattern} -> Error: {e}")
                    
                    # Method 4: Check if there's a different collaboration structure
                    print(f"   Method 4: Checking collaboration structure...")
                    collaboration_url = f"{client.api_v3}/catalog/{entity_id}/collaboration"
                    try:
                        collab_resp = client.session.get(collaboration_url)
                        print(f"   Collaboration endpoint: {collab_resp.status_code}")
                        if collab_resp.status_code == 200:
                            collab_data = collab_resp.json()
                            print(f"   Collaboration data: {json.dumps(collab_data, indent=2)}")
                    except Exception as e:
                        print(f"   ❌ Collaboration endpoint error: {e}")
                        
                else:
                    print(f"   ❌ Failed to get catalog data: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exception getting catalog data: {e}")
        
        # Method 5: Try to find any existing wiki content in the system
        print(f"\n🔍 Method 5: Searching for any existing wiki content...")
        
        # Try to get all catalog items and check for wiki content
        try:
            all_catalog_url = f"{client.api_v3}/catalog"
            response = client.session.get(all_catalog_url)
            if response.status_code == 200:
                catalog_items = response.json()
                print(f"   Found {len(catalog_items.get('data', []))} catalog items")
                
                # Check first few items for wiki content
                for item in catalog_items.get('data', [])[:5]:
                    item_id = item.get('id')
                    item_path = '.'.join(item.get('path', []))
                    print(f"   Checking: {item_path} (ID: {item_id})")
                    
                    if item_id:
                        wiki_url = f"{client.api_v3}/catalog/{item_id}/collaboration/wiki"
                        try:
                            wiki_resp = client.session.get(wiki_url)
                            if wiki_resp.status_code == 200:
                                wiki_data = wiki_resp.json()
                                if 'text' in wiki_data and wiki_data['text']:
                                    print(f"   ✅ Found wiki content for: {item_path}")
                                    print(f"   Content: {wiki_data['text'][:100]}...")
                                    break
                        except Exception as e:
                            pass
            else:
                print(f"   ❌ Failed to get catalog items: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception searching catalog: {e}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_wiki_api_v2()

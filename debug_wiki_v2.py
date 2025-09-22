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
        
        # Filter for DataMesh tables specifically
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        
        if not datamesh_tables:
            print("❌ No DataMesh tables found. Available schemas:")
            schemas = set([schema for schema, table in tables[:20]])
            for schema in sorted(schemas):
                print(f"   - {schema}")
            return
        
        # Test with DataMesh tables
        test_tables = datamesh_tables[:3]
        print(f"\n📋 Testing wiki API with {len(test_tables)} DataMesh tables:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\n🔍 Testing: {table_path}")
            
            # Method 1: Get catalog item details first to find the ID
            print("   Method 1: Getting catalog item details...")
            
            # Try different path formats
            path_formats = [
                table_path,  # Original format
                table_path.replace('.', '/'),  # Slash format
                table_path.replace('.', '%2E'),  # URL encoded dots
                f'"{table_path}"',  # Quoted format
            ]
            
            for i, path_format in enumerate(path_formats):
                catalog_url = f"{client.api_v3}/catalog/by-path/{path_format}"
                print(f"     Format {i+1}: {catalog_url}")
                
                try:
                    response = client.session.get(catalog_url)
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        catalog_data = response.json()
                        print(f"     ✅ Success with format {i+1}")
                        print(f"     ID: {catalog_data.get('id', 'N/A')}")
                        print(f"     Type: {catalog_data.get('entityType', 'N/A')}")
                        print(f"     Path: {catalog_data.get('path', 'N/A')}")
                        
                        # Test wiki with this ID
                        entity_id = catalog_data.get('id')
                        if entity_id:
                            print(f"     Testing wiki with ID: {entity_id}")
                            wiki_url = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                            wiki_response = client.session.get(wiki_url)
                            print(f"     Wiki status: {wiki_response.status_code}")
                            
                            if wiki_response.status_code == 200:
                                wiki_data = wiki_response.json()
                                if 'text' in wiki_data and wiki_data['text']:
                                    print(f"     ✅ Wiki content found!")
                                    print(f"     Content: {wiki_data['text'][:100]}...")
                                else:
                                    print(f"     ❌ Wiki content is empty")
                            else:
                                print(f"     ❌ Wiki not found: {wiki_response.text}")
                        break
                    else:
                        print(f"     ❌ Failed: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"     ❌ Exception: {e}")
            
            # If none of the path formats worked, try alternative approaches
            if i == len(path_formats) - 1:  # If we tried all formats and none worked
                print("   Method 2: Trying alternative catalog search...")
                
                # Try to search for the table in the catalog
                try:
                    search_url = f"{client.api_v3}/catalog"
                    response = client.session.get(search_url)
                    if response.status_code == 200:
                        catalog_items = response.json()
                        print(f"     Found {len(catalog_items.get('data', []))} catalog items")
                        
                        # Look for our table in the catalog
                        for item in catalog_items.get('data', []):
                            item_path = '.'.join(item.get('path', []))
                            if table.lower() in item_path.lower() and 'datamesh' in item_path.lower():
                                print(f"     Found matching item: {item_path}")
                                print(f"     ID: {item.get('id')}")
                                
                                # Test wiki with this ID
                                entity_id = item.get('id')
                                if entity_id:
                                    wiki_url = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                                    wiki_response = client.session.get(wiki_url)
                                    print(f"     Wiki status: {wiki_response.status_code}")
                                    
                                    if wiki_response.status_code == 200:
                                        wiki_data = wiki_response.json()
                                        if 'text' in wiki_data and wiki_data['text']:
                                            print(f"     ✅ Wiki content found!")
                                            print(f"     Content: {wiki_data['text'][:100]}...")
                                        else:
                                            print(f"     ❌ Wiki content is empty")
                                    else:
                                        print(f"     ❌ Wiki not found")
                                break
                except Exception as e:
                    print(f"     ❌ Search exception: {e}")
        
        # Method 3: Search for DataMesh tables with wiki content
        print(f"\n🔍 Method 3: Searching for DataMesh tables with wiki content...")
        
        try:
            all_catalog_url = f"{client.api_v3}/catalog"
            response = client.session.get(all_catalog_url)
            if response.status_code == 200:
                catalog_items = response.json()
                print(f"   Found {len(catalog_items.get('data', []))} catalog items")
                
                # Look specifically for DataMesh tables
                datamesh_items = []
                for item in catalog_items.get('data', []):
                    item_path = '.'.join(item.get('path', []))
                    if 'datamesh' in item_path.lower() or 'DataMesh' in item_path:
                        datamesh_items.append(item)
                
                print(f"   Found {len(datamesh_items)} DataMesh items")
                
                # Check DataMesh items for wiki content
                for item in datamesh_items[:5]:  # Check first 5 DataMesh items
                    item_id = item.get('id')
                    item_path = '.'.join(item.get('path', []))
                    print(f"   Checking DataMesh item: {item_path} (ID: {item_id})")
                    
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
                                else:
                                    print(f"   ❌ No wiki content for: {item_path}")
                            else:
                                print(f"   ❌ Wiki not found for: {item_path} (status: {wiki_resp.status_code})")
                        except Exception as e:
                            print(f"   ❌ Error checking wiki for {item_path}: {e}")
            else:
                print(f"   ❌ Failed to get catalog items: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception searching catalog: {e}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_wiki_api_v2()

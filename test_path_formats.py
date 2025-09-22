#!/usr/bin/env python3
"""
Test script to find the correct path format for DataMesh tables
"""

import os
import requests
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def test_path_formats():
    """Test different path formats to find the correct one"""
    print("🔍 Testing Path Formats for DataMesh Tables")
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
        
        # Get DataMesh tables
        tables = client.list_tables()
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        
        if not datamesh_tables:
            print("❌ No DataMesh tables found. Available schemas:")
            schemas = set([schema for schema, table in tables[:20]])
            for schema in sorted(schemas):
                print(f"   - {schema}")
            return
        
        print(f"📋 Found {len(datamesh_tables)} DataMesh tables")
        
        # Test with first DataMesh table
        schema, table = datamesh_tables[0]
        table_path = f"{schema}.{table}"
        print(f"\n🔍 Testing path formats for: {table_path}")
        
        # Test different path formats
        path_formats = [
            table_path,  # Original: DataMesh.application.Accounts
            table_path.replace('.', '/'),  # Slash: DataMesh/application/Accounts
            table_path.replace('.', '%2E'),  # URL encoded: DataMesh%2Eapplication%2EAccounts
            f'"{table_path}"',  # Quoted: "DataMesh.application.Accounts"
            f'[{table_path}]',  # Bracketed: [DataMesh.application.Accounts]
            table_path.replace('.', '.'),  # Same as original
        ]
        
        for i, path_format in enumerate(path_formats):
            print(f"\n   Format {i+1}: {path_format}")
            catalog_url = f"{client.api_v3}/catalog/by-path/{path_format}"
            print(f"   URL: {catalog_url}")
            
            try:
                response = client.session.get(catalog_url)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    catalog_data = response.json()
                    print(f"   ✅ SUCCESS!")
                    print(f"   ID: {catalog_data.get('id')}")
                    print(f"   Type: {catalog_data.get('entityType')}")
                    print(f"   Path: {catalog_data.get('path')}")
                    
                    # Test wiki with this ID
                    entity_id = catalog_data.get('id')
                    if entity_id:
                        print(f"   Testing wiki...")
                        wiki_url = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                        wiki_response = client.session.get(wiki_url)
                        print(f"   Wiki status: {wiki_response.status_code}")
                        
                        if wiki_response.status_code == 200:
                            wiki_data = wiki_response.json()
                            if 'text' in wiki_data and wiki_data['text']:
                                print(f"   ✅ Wiki content found!")
                                print(f"   Content: {wiki_data['text'][:100]}...")
                            else:
                                print(f"   ❌ Wiki content is empty")
                        else:
                            print(f"   ❌ Wiki not found")
                    
                    # This format works, so we can stop here
                    print(f"\n🎉 Found working path format: {path_format}")
                    return path_format
                    
                else:
                    print(f"   ❌ Failed: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        print(f"\n❌ None of the path formats worked for {table_path}")
        
        # Try to find the table in the catalog directly
        print(f"\n🔍 Searching catalog for DataMesh tables...")
        try:
            catalog_url = f"{client.api_v3}/catalog"
            response = client.session.get(catalog_url)
            if response.status_code == 200:
                catalog_items = response.json()
                print(f"   Found {len(catalog_items.get('data', []))} catalog items")
                
                # Look for DataMesh items
                for item in catalog_items.get('data', []):
                    item_path = '.'.join(item.get('path', []))
                    if 'datamesh' in item_path.lower() or 'DataMesh' in item_path:
                        print(f"   Found DataMesh item: {item_path}")
                        print(f"   ID: {item.get('id')}")
                        print(f"   Type: {item.get('type')}")
                        
                        # Test wiki
                        entity_id = item.get('id')
                        if entity_id:
                            wiki_url = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                            wiki_response = client.session.get(wiki_url)
                            print(f"   Wiki status: {wiki_response.status_code}")
                            
                            if wiki_response.status_code == 200:
                                wiki_data = wiki_response.json()
                                if 'text' in wiki_data and wiki_data['text']:
                                    print(f"   ✅ Wiki content found!")
                                    print(f"   Content: {wiki_data['text'][:100]}...")
                                else:
                                    print(f"   ❌ Wiki content is empty")
                            else:
                                print(f"   ❌ Wiki not found")
                        break
        except Exception as e:
            print(f"   ❌ Exception searching catalog: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_path_formats()

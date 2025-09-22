#!/usr/bin/env python3
"""
Debug script to see what's actually in the catalog
"""

import os
import json
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def debug_catalog_items():
    """Debug what's in the catalog vs what's in list_tables"""
    print("🔍 Debugging Catalog Items")
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
        
        # Get tables via SQL
        print("\n📋 Tables via SQL (list_tables):")
        tables = client.list_tables()
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        print(f"Total tables: {len(tables)}")
        print(f"DataMesh tables: {len(datamesh_tables)}")
        
        # Show first few DataMesh tables
        for schema, table in datamesh_tables[:5]:
            print(f"  - {schema}.{table}")
        
        # Get catalog items via REST API
        print("\n📋 Catalog items via REST API:")
        try:
            catalog_url = f"{client.api_v3}/catalog"
            response = client.session.get(catalog_url)
            if response.status_code == 200:
                catalog_items = response.json()
                items = catalog_items.get('data', [])
                print(f"Total catalog items: {len(items)}")
                
                # Show first few items
                for item in items[:10]:
                    item_path = '.'.join(item.get('path', []))
                    item_name = item.get('name', '')
                    item_type = item.get('type', '')
                    print(f"  - {item_path} (name: {item_name}, type: {item_type})")
                
                # Look for any DataMesh items
                datamesh_items = []
                for item in items:
                    item_path = '.'.join(item.get('path', []))
                    if 'datamesh' in item_path.lower() or 'DataMesh' in item_path:
                        datamesh_items.append(item)
                
                print(f"\nDataMesh items in catalog: {len(datamesh_items)}")
                for item in datamesh_items:
                    item_path = '.'.join(item.get('path', []))
                    item_name = item.get('name', '')
                    item_type = item.get('type', '')
                    print(f"  - {item_path} (name: {item_name}, type: {item_type})")
                
                # Check if any DataMesh tables from SQL are in catalog
                print(f"\n🔍 Checking if DataMesh tables from SQL are in catalog:")
                found_in_catalog = 0
                for schema, table in datamesh_tables[:10]:
                    table_path = f"{schema}.{table}"
                    found = False
                    for item in items:
                        item_path = '.'.join(item.get('path', []))
                        if item_path.lower() == table_path.lower():
                            found = True
                            found_in_catalog += 1
                            print(f"  ✅ {table_path} found in catalog")
                            break
                    if not found:
                        print(f"  ❌ {table_path} NOT found in catalog")
                
                print(f"\nSummary: {found_in_catalog}/{min(10, len(datamesh_tables))} DataMesh tables found in catalog")
                
            else:
                print(f"❌ Failed to get catalog: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting catalog: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    debug_catalog_items()

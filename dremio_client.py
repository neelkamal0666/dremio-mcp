#!/usr/bin/env python3
"""
Enhanced Dremio Client

This module provides comprehensive Dremio integration including:
- REST API access for metadata and wiki descriptions
- Flight SQL connection for data queries
- Authentication handling (basic auth and OAuth)
- Metadata caching and management
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class DremioClient:
    """Enhanced Dremio client with REST API and Flight SQL support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = f"{'https' if config.get('use_ssl', True) else 'http'}://{config['host']}:{config.get('port', 9047)}"
        # Use v3 for data APIs; v2 only for login endpoint
        self.api_v3 = f"{self.base_url}/api/v3"
        self.api_v2 = f"{self.base_url}/api/v2"
        # SSL verification preference and optional custom CA bundle
        self.verify_ssl = bool(config.get('verify_ssl', True))
        self.cert_path = config.get('cert_path')
        # Flight SQL configuration (separate port from REST)
        self.flight_port = int(config.get('flight_port', config.get('port', 32010)))
        # Default scoping
        self.default_source = config.get('default_source')
        self.default_schema = config.get('default_schema')
        self.session = self._create_session()
        self.token = None
        self.engine = None
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Apply SSL verification preference
        if not self.config.get('use_ssl', True):
            session.verify = True  # not used for http
        else:
            if not self.verify_ssl:
                session.verify = False
            elif self.cert_path and os.path.exists(self.cert_path):
                session.verify = self.cert_path
            else:
                session.verify = True
        
        # Default headers
        session.headers.update({'Content-Type': 'application/json'})
        
        return session
    
    def authenticate(self) -> bool:
        """Authenticate with Dremio and get access token"""
        try:
            # Dremio login is on /apiv2/login
            auth_url = f"{self.base_url}/apiv2/login"
            
            # Try OAuth first if credentials are provided
            if self.config.get('client_id') and self.config.get('client_secret'):
                return self._authenticate_oauth()
            
            # Fall back to basic authentication
            auth_data = {
                "userName": self.config['username'],
                "password": self.config['password']
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get('token')
            
            if self.token:
                # Dremio expects Authorization: _dremio{token}
                self.session.headers.update({
                    'Authorization': f"_dremio{self.token}",
                })
                logger.info("Successfully authenticated with Dremio")
                return True
            else:
                logger.error("Authentication failed: No token received")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
        except ValueError as e:
            # JSON decode error (non-JSON response)
            logger.error(f"Authentication response parse error: {str(e)}")
            return False

    # REST SQL helpers
    def _rest_submit_sql(self, sql: str) -> Optional[str]:
        try:
            url = f"{self.api_v3}/sql"
            resp = self.session.post(url, json={"sql": sql})
            resp.raise_for_status()
            data = resp.json()
            return data.get('id')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting SQL: {str(e)}")
            return None
        except ValueError:
            logger.error("Error parsing SQL submit response")
            return None

    def _rest_wait_job(self, job_id: str, timeout: int = 300, interval: int = 2) -> bool:
        try:
            url = f"{self.api_v3}/job/{job_id}"
            elapsed = 0
            last_state = None
            while elapsed < timeout:
                r = self.session.get(url)
                r.raise_for_status()
                info = r.json()
                state = info.get('jobState')
                if state != last_state:
                    logger.info(f"Job {job_id} state: {state}")
                    last_state = state
                if state == 'COMPLETED':
                    return True
                if state in ('FAILED', 'CANCELED'):
                    logger.error(f"Job {job_id} ended: {state} - {info.get('errorMessage')}")
                    return False
                import time as _t
                _t.sleep(interval)
                elapsed += interval
            logger.error(f"Timeout waiting for job {job_id}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling job {job_id}: {str(e)}")
            return False

    def _rest_fetch_results(self, job_id: str, limit: Optional[int] = None, page_limit: int = 500) -> pd.DataFrame:
        try:
            # First page to get counts
            url = f"{self.api_v3}/job/{job_id}/results"
            params = {"offset": 0, "limit": page_limit}
            r = self.session.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            rows = data.get('rows', [])
            total_rows = data.get('rowCount', len(rows))
            if limit is not None:
                total_rows = min(total_rows, limit)
            all_rows = list(rows)
            # Fetch remaining pages
            offset = len(rows)
            while offset < total_rows:
                fetch_size = min(page_limit, total_rows - offset)
                pr = self.session.get(url, params={"offset": offset, "limit": fetch_size})
                pr.raise_for_status()
                pdata = pr.json()
                all_rows.extend(pdata.get('rows', []))
                offset += fetch_size
            # Convert to DataFrame
            if not all_rows:
                return pd.DataFrame()
            # Normalize rows (list of dicts)
            import pandas as _pd
            return _pd.DataFrame(all_rows)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching results for job {job_id}: {str(e)}")
            return pd.DataFrame()
        except ValueError:
            logger.error("Error parsing results JSON")
            return pd.DataFrame()

    def get_connection_engine(self):
        """Get SQLAlchemy engine for Flight SQL queries"""
        if self.engine is None:
            # Build query parameters for SSL/verification using dialect-expected names
            params: Dict[str, Any] = {}
            params['UseEncryption'] = 'true' if self.config.get('use_ssl', True) else 'false'
            if self.config.get('use_ssl', True):
                if not self.verify_ssl:
                    params['DisableCertificateVerification'] = 'true'
                elif self.cert_path and os.path.exists(self.cert_path):
                    params['TrustedCertificates'] = self.cert_path
                else:
                    # Use system trust when verifying but no custom bundle
                    params['useSystemTrustStore'] = 'true'
            
            query_str = urlencode(params)
            protocol = "dremio+flight"
            connection_string = (
                f"{protocol}://{self.config['username']}:{self.config['password']}@"
                f"{self.config['host']}:{self.flight_port}/?{query_str}"
            )
            self.engine = create_engine(connection_string)
        return self.engine
    
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame via REST API"""
        try:
            job_id = self._rest_submit_sql(query if (not limit or 'LIMIT' in (query or '').upper()) else f"{query} LIMIT {limit}")
            if not job_id:
                raise RuntimeError("Failed to submit SQL job")
            if not self._rest_wait_job(job_id):
                raise RuntimeError("SQL job did not complete successfully")
            # If LIMIT was not in query and provided, fetch up to limit
            effective_limit = None if (limit is None or 'LIMIT' in (query or '').upper()) else limit
            df = self._rest_fetch_results(job_id, limit=effective_limit)
            return df
        except Exception as e:
            logger.error(f"SQL execution error (REST): {str(e)}")
            raise
    
    def get_catalog_items(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get catalog items (datasets, folders, etc.) from Dremio"""
        try:
            if path:
                url = f"{self.api_v3}/catalog/by-path/{path}"
            else:
                url = f"{self.api_v3}/catalog"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting catalog items: {str(e)}")
            return []
    
    def get_dataset_metadata(self, dataset_path: str) -> Dict[str, Any]:
        """Get comprehensive metadata for a dataset"""
        try:
            # Get dataset info
            dataset_url = f"{self.api_v3}/catalog/by-path/{dataset_path}"
            response = self.session.get(dataset_url)
            response.raise_for_status()
            dataset_info = response.json()
            
            # Get wiki description if available
            wiki_description = self.get_wiki_description(dataset_path)
            
            # Get sample data
            sample_data = None
            try:
                sample_query = f"SELECT * FROM {dataset_path} LIMIT 5"
                sample_data = self.execute_query(sample_query)
            except Exception as e:
                logger.warning(f"Could not get sample data: {str(e)}")
            
            return {
                "dataset_info": dataset_info,
                "wiki_description": wiki_description,
                "sample_data": sample_data.to_dict('records') if sample_data is not None else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting dataset metadata: {str(e)}")
            return {}
    
    def get_wiki_description(self, entity_path: str) -> Optional[str]:
        """Get wiki description for a dataset or folder"""
        try:
            # First get the entity ID from the path
            entity_id = self._get_entity_id_by_path(entity_path)
            if not entity_id:
                logger.warning(f"Could not find entity ID for path: {entity_path}")
                return None
            
            # Try to get wiki content using entity ID
            wiki_url = f"{self.api_v3}/catalog/{entity_id}/collaboration/wiki"
            response = self.session.get(wiki_url)
            
            if response.status_code == 200:
                wiki_data = response.json()
                return wiki_data.get('text', '')
            else:
                logger.debug(f"Wiki not found for {entity_path} (ID: {entity_id}): {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not get wiki description: {str(e)}")
            return None
    
    def get_wiki_metadata(self, entity_path: str) -> Dict[str, Any]:
        """Get comprehensive wiki metadata including tags, descriptions, and custom fields"""
        try:
            # First get the entity ID from the path
            entity_id = self._get_entity_id_by_path(entity_path)
            if not entity_id:
                logger.warning(f"Could not find entity ID for path: {entity_path}")
                return {}
            
            # Try to get wiki content using entity ID
            wiki_url = f"{self.api_v3}/catalog/{entity_id}/collaboration/wiki"
            response = self.session.get(wiki_url)
            
            if response.status_code == 200:
                wiki_data = response.json()
                
                # Parse wiki content for structured metadata
                wiki_text = wiki_data.get('text', '')
                parsed_metadata = self._parse_wiki_metadata(wiki_text)
                
                return {
                    'raw_text': wiki_text,
                    'parsed_metadata': parsed_metadata,
                    'last_modified': wiki_data.get('version', {}).get('createdAt'),
                    'author': wiki_data.get('version', {}).get('author')
                }
            else:
                logger.debug(f"Wiki not found for {entity_path} (ID: {entity_id}): {response.status_code}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not get wiki metadata: {str(e)}")
            return {}
    
    def _get_entity_id_by_path(self, entity_path: str) -> Optional[str]:
        """Get entity ID from entity path using catalog search"""
        try:
            # First try the direct by-path approach
            catalog_url = f"{self.api_v3}/catalog/by-path/{entity_path}"
            response = self.session.get(catalog_url)
            
            if response.status_code == 200:
                catalog_data = response.json()
                return catalog_data.get('id')
            else:
                logger.debug(f"Direct by-path failed for {entity_path}: {response.status_code}")
                
                # Fallback: Search through catalog items
                logger.debug(f"Searching catalog for entity: {entity_path}")
                search_url = f"{self.api_v3}/catalog"
                search_response = self.session.get(search_url)
                
                if search_response.status_code == 200:
                    catalog_items = search_response.json()
                    
                    # Extract table name from entity path for matching
                    path_parts = entity_path.split('.')
                    table_name = path_parts[-1] if path_parts else entity_path
                    schema_parts = path_parts[:-1] if len(path_parts) > 1 else []
                    
                    # Look for matching items
                    logger.debug(f"Searching through {len(catalog_items.get('data', []))} catalog items")
                    for item in catalog_items.get('data', []):
                        item_path = '.'.join(item.get('path', []))
                        item_name = item.get('name', '')
                        
                        # Check if this item matches our target
                        if (table_name.lower() in item_name.lower() and 
                            any(part.lower() in item_path.lower() for part in schema_parts)):
                            logger.debug(f"Found matching catalog item: {item_path} (ID: {item.get('id')})")
                            return item.get('id')
                        
                        # Also check for exact path match
                        if item_path.lower() == entity_path.lower():
                            logger.debug(f"Found exact path match: {item_path} (ID: {item.get('id')})")
                            return item.get('id')
                    
                    logger.debug(f"No matching catalog item found for {entity_path}")
                    return None
                else:
                    logger.warning(f"Failed to search catalog: {search_response.status_code}")
                    return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not get entity ID for path {entity_path}: {str(e)}")
            return None
    
    def _parse_wiki_metadata(self, wiki_text: str) -> Dict[str, Any]:
        """Parse wiki text to extract structured metadata"""
        metadata = {
            'description': '',
            'business_purpose': '',
            'data_source': '',
            'update_frequency': '',
            'owner': '',
            'tags': [],
            'column_descriptions': {},
            'usage_notes': '',
            'data_quality_notes': ''
        }
        
        if not wiki_text:
            return metadata
        
        lines = wiki_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Parse section headers
            if line.startswith('# '):
                current_section = 'description'
                metadata['description'] = line[2:].strip()
            elif line.startswith('## '):
                section_name = line[3:].strip().lower()
                if 'purpose' in section_name:
                    current_section = 'business_purpose'
                elif 'source' in section_name:
                    current_section = 'data_source'
                elif 'frequency' in section_name or 'update' in section_name:
                    current_section = 'update_frequency'
                elif 'owner' in section_name:
                    current_section = 'owner'
                elif 'usage' in section_name:
                    current_section = 'usage_notes'
                elif 'quality' in section_name:
                    current_section = 'data_quality_notes'
                elif 'columns' in section_name:
                    current_section = 'column_descriptions'
                else:
                    current_section = None
            elif line.startswith('**') and line.endswith('**'):
                # Bold text - could be field names
                field_name = line[2:-2].strip().lower()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.replace('**', '').strip().lower()
                    value = value.replace('**', '').strip()
                    
                    if 'description' in key:
                        metadata['description'] = value
                    elif 'purpose' in key:
                        metadata['business_purpose'] = value
                    elif 'source' in key:
                        metadata['data_source'] = value
                    elif 'frequency' in key or 'update' in key:
                        metadata['update_frequency'] = value
                    elif 'owner' in key:
                        metadata['owner'] = value
            elif line.startswith('- ') or line.startswith('* '):
                # List items - could be tags or column descriptions
                item = line[2:].strip()
                if current_section == 'column_descriptions':
                    # Parse column descriptions like "column_name: description"
                    if ':' in item:
                        col_name, col_desc = item.split(':', 1)
                        metadata['column_descriptions'][col_name.strip()] = col_desc.strip()
                elif 'tag' in item.lower() or item.startswith('#'):
                    # Extract tags
                    tag = item.replace('#', '').strip()
                    if tag:
                        metadata['tags'].append(tag)
            elif line and current_section and current_section != 'column_descriptions':
                # Regular text content
                if metadata[current_section]:
                    metadata[current_section] += ' ' + line
                else:
                    metadata[current_section] = line
        
        return metadata
    
    def search_wiki_content(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for entities with wiki content matching the search term"""
        try:
            # Get all catalog items
            catalog_items = self.get_catalog_items()
            matching_items = []
            
            for item in catalog_items:
                entity_path = item.get('path', [])
                if not entity_path:
                    continue
                
                full_path = '.'.join(entity_path)
                wiki_metadata = self.get_wiki_metadata(full_path)
                
                if wiki_metadata and wiki_metadata.get('raw_text'):
                    wiki_text = wiki_metadata['raw_text'].lower()
                    if search_term.lower() in wiki_text:
                        matching_items.append({
                            'path': full_path,
                            'name': item.get('name', ''),
                            'type': item.get('type', ''),
                            'wiki_snippet': self._extract_snippet(wiki_metadata['raw_text'], search_term),
                            'wiki_metadata': wiki_metadata
                        })
            
            return matching_items
            
        except Exception as e:
            logger.error(f"Error searching wiki content: {str(e)}")
            return []
    
    def _extract_snippet(self, text: str, search_term: str, context_length: int = 100) -> str:
        """Extract a snippet of text around the search term"""
        text_lower = text.lower()
        term_lower = search_term.lower()
        
        index = text_lower.find(term_lower)
        if index == -1:
            return text[:context_length] + "..." if len(text) > context_length else text
        
        start = max(0, index - context_length // 2)
        end = min(len(text), index + len(search_term) + context_length // 2)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def search_datasets(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for datasets by name or description"""
        try:
            search_url = f"{self.api_v3}/catalog/search"
            params = {
                "query": search_term,
                "type": "dataset"
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching datasets: {str(e)}")
            return []
    
    def get_table_schema(self, table_path: str) -> pd.DataFrame:
        """Get detailed schema information for a table"""
        try:
            # Use INFORMATION_SCHEMA to get column details
            schema_query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM INFORMATION_SCHEMA."COLUMNS"
            WHERE table_name = '{table_path.split('.')[-1]}'
            ORDER BY ordinal_position
            """
            
            return self.execute_query(schema_query)
            
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise
    
    def list_tables(self, source: Optional[str] = None, schema: Optional[str] = None) -> List[Tuple[str, str]]:
        """List all available tables with optional filtering"""
        try:
            # Apply defaults if not explicitly provided
            if source is None and self.default_source:
                source = self.default_source
            if schema is None and self.default_schema:
                schema = self.default_schema
            
            query = "SELECT table_schema, table_name FROM INFORMATION_SCHEMA.\"TABLES\" WHERE table_type IN ('TABLE','VIEW')"
            
            if source and schema:
                # Case-insensitive match on fully-qualified schema
                fq_schema = f"{source}.{schema}"
                query += f" AND LOWER(table_schema) = LOWER('{fq_schema}')"
            elif source:
                query += f" AND LOWER(table_schema) LIKE LOWER('{source}.%')"
            elif schema:
                query += f" AND LOWER(table_schema) LIKE LOWER('%.{schema}')"
            
            query += " ORDER BY table_schema, table_name"
            
            df = self.execute_query(query)
            return [(row['table_schema'], row['table_name']) for _, row in df.iterrows()]
            
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            return []
    
    def get_data_sample(self, table_path: str, limit: int = 10) -> pd.DataFrame:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_path} LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting sample data: {str(e)}")
            raise
    
    def get_reflection_info(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Get reflection information for a dataset"""
        try:
            reflections_url = f"{self.api_v3}/catalog/by-path/{dataset_path}/reflection"
            response = self.session.get(reflections_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not get reflection info: {str(e)}")
            return []
    
    def get_job_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent job history"""
        try:
            jobs_url = f"{self.api_v3}/jobs"
            params = {"limit": limit}
            
            response = self.session.get(jobs_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting job history: {str(e)}")
            return []

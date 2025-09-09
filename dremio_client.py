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
from urllib.parse import urljoin

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
        self.api_url = f"{self.base_url}/api/v3"
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
        
        return session
    
    def authenticate(self) -> bool:
        """Authenticate with Dremio and get access token"""
        try:
            auth_url = f"{self.api_url}/login"
            
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
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                logger.info("Successfully authenticated with Dremio")
                return True
            else:
                logger.error("Authentication failed: No token received")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _authenticate_oauth(self) -> bool:
        """Authenticate using OAuth2"""
        try:
            # This is a simplified OAuth flow - adjust based on your Dremio OAuth setup
            oauth_url = f"{self.api_url}/oauth/token"
            
            oauth_data = {
                "grant_type": "client_credentials",
                "client_id": self.config['client_id'],
                "client_secret": self.config['client_secret']
            }
            
            response = self.session.post(oauth_url, data=oauth_data)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get('access_token')
            
            if self.token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                logger.info("Successfully authenticated with OAuth")
                return True
            else:
                logger.error("OAuth authentication failed: No access token received")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OAuth authentication error: {str(e)}")
            return False
    
    def get_connection_engine(self):
        """Get SQLAlchemy engine for Flight SQL queries"""
        if self.engine is None:
            protocol = "dremio+flight" if self.config.get('use_ssl', True) else "dremio+flight"
            connection_string = f"{protocol}://{self.config['username']}:{self.config['password']}@{self.config['host']}:{self.config.get('port', 9047)}"
            self.engine = create_engine(connection_string)
        return self.engine
    
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            engine = self.get_connection_engine()
            
            # Add LIMIT if not present and limit is specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                
                return pd.DataFrame(rows, columns=columns)
                
        except SQLAlchemyError as e:
            logger.error(f"SQL execution error: {str(e)}")
            raise
    
    def get_catalog_items(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get catalog items (datasets, folders, etc.) from Dremio"""
        try:
            if path:
                url = f"{self.api_url}/catalog/by-path/{path}"
            else:
                url = f"{self.api_url}/catalog"
            
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
            dataset_url = f"{self.api_url}/catalog/by-path/{dataset_path}"
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
            # Try to get wiki content
            wiki_url = f"{self.api_url}/catalog/by-path/{entity_path}/collaboration/wiki"
            response = self.session.get(wiki_url)
            
            if response.status_code == 200:
                wiki_data = response.json()
                return wiki_data.get('text', '')
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not get wiki description: {str(e)}")
            return None
    
    def search_datasets(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for datasets by name or description"""
        try:
            search_url = f"{self.api_url}/catalog/search"
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
            FROM INFORMATION_SCHEMA.COLUMNS 
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
            query = "SELECT table_schema, table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_type = 'BASE TABLE'"
            params = []
            
            if source:
                query += " AND table_schema LIKE ?"
                params.append(f"{source}%")
            
            if schema:
                query += " AND table_schema = ?"
                params.append(schema)
            
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
            reflections_url = f"{self.api_url}/catalog/by-path/{dataset_path}/reflection"
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
            jobs_url = f"{self.api_url}/jobs"
            params = {"limit": limit}
            
            response = self.session.get(jobs_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting job history: {str(e)}")
            return []

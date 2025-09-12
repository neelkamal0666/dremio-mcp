#!/usr/bin/env python3
"""
AI Agent for Dremio Data Interaction

This module provides an AI agent that can:
- Process natural language queries about Dremio data
- Generate appropriate SQL queries
- Provide data insights and analysis
- Work with the MCP server to access Dremio
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from dremio_client import DremioClient

logger = logging.getLogger(__name__)

class DremioAIAgent:
    """AI Agent for natural language interaction with Dremio data"""
    
    def __init__(self, dremio_client: DremioClient, openai_api_key: Optional[str] = None):
        self.dremio_client = dremio_client
        self.openai_client: Optional[OpenAI] = None
        
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Cache for metadata to avoid repeated API calls
        self.metadata_cache = {}
        self.table_schemas = {}
        
    def set_openai_key(self, api_key: str):
        """Set OpenAI API key for enhanced natural language processing"""
        self.openai_client = OpenAI(api_key=api_key)
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a natural language query and return results"""
        try:
            # Analyze the query to understand intent
            intent = self._analyze_query_intent(user_query)
            
            if intent['type'] == 'data_query':
                return await self._handle_data_query(user_query, intent)
            elif intent['type'] == 'schema_inquiry':
                return await self._handle_schema_inquiry(user_query, intent)
            elif intent['type'] == 'table_exploration':
                return await self._handle_table_exploration(user_query, intent)
            elif intent['type'] == 'metadata_request':
                return await self._handle_metadata_request(user_query, intent)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported query type: {intent['type']}",
                    'suggestion': "Try asking about data, table schemas, or available tables"
                }
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'suggestion': "Please try rephrasing your question"
            }
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and extract entities"""
        query_lower = query.lower()
        
        # Data query patterns
        data_patterns = [
            r'show me|display|get|fetch|retrieve|find',
            r'how many|count|total|sum|average|max|min',
            r'what is|what are|list|show',
            r'where|when|who|which'
        ]
        
        # Schema inquiry patterns
        schema_patterns = [
            r'schema|structure|columns|fields',
            r'what columns|what fields|describe table',
            r'data types|column types'
        ]
        
        # Table exploration patterns
        table_patterns = [
            r'tables|datasets|sources',
            r'available|list all|show all',
            r'what tables|what datasets'
        ]
        
        # Metadata patterns
        metadata_patterns = [
            r'description|wiki|documentation|info about',
            r'metadata|details|information'
        ]
        
        intent = {
            'type': 'unknown',
            'entities': [],
            'filters': {},
            'aggregations': []
        }
        
        # Check for data query intent
        if any(re.search(pattern, query_lower) for pattern in data_patterns):
            intent['type'] = 'data_query'
            
            # Extract potential table names (simple heuristic)
            table_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b', query)
            intent['entities'] = [match for match in table_matches if '.' in match]
            
            # Extract aggregations
            agg_patterns = {
                'count': r'\bcount\b|\bhow many\b',
                'sum': r'\bsum\b|\btotal\b',
                'average': r'\baverage\b|\bavg\b',
                'max': r'\bmax\b|\bmaximum\b',
                'min': r'\bmin\b|\bminimum\b'
            }
            
            for agg_type, pattern in agg_patterns.items():
                if re.search(pattern, query_lower):
                    intent['aggregations'].append(agg_type)
        
        # Check for schema inquiry intent
        elif any(re.search(pattern, query_lower) for pattern in schema_patterns):
            intent['type'] = 'schema_inquiry'
            
            # Extract table names
            table_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b', query)
            intent['entities'] = [match for match in table_matches if '.' in match]
        
        # Check for table exploration intent
        elif any(re.search(pattern, query_lower) for pattern in table_patterns):
            intent['type'] = 'table_exploration'
            
            # Extract source/schema filters
            if 'source' in query_lower:
                source_match = re.search(r'source[:\s]+([a-zA-Z_][a-zA-Z0-9_]*)', query_lower)
                if source_match:
                    intent['filters']['source'] = source_match.group(1)
        
        # Check for metadata intent
        elif any(re.search(pattern, query_lower) for pattern in metadata_patterns):
            intent['type'] = 'metadata_request'
            
            # Extract table names
            table_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b', query)
            intent['entities'] = [match for match in table_matches if '.' in match]
        
        return intent
    
    async def _handle_data_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data-related queries"""
        try:
            # Generate SQL query using AI if available
            if self.openai_client:
                sql_query = await self._generate_sql_with_ai(query, intent)
            else:
                sql_query = self._generate_sql_heuristic(query, intent)
            
            if not sql_query:
                return {
                    'success': False,
                    'error': "Could not generate SQL query from your question",
                    'suggestion': "Try being more specific about the table and columns you want to query"
                }
            
            # Execute the query
            result_df = self.dremio_client.execute_query(sql_query)
            
            return {
                'success': True,
                'query': sql_query,
                'data': result_df.to_dict('records'),
                'row_count': len(result_df),
                'columns': list(result_df.columns)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error executing query: {str(e)}",
                'suggestion': "Please check your table names and try again"
            }
    
    async def _handle_schema_inquiry(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schema-related queries"""
        try:
            if not intent['entities']:
                return {
                    'success': False,
                    'error': "Please specify which table you want schema information for",
                    'suggestion': "Try: 'What is the schema of table_name' or 'Show me the columns in source.schema.table'"
                }
            
            table_path = intent['entities'][0]
            schema_df = self.dremio_client.get_table_schema(table_path)
            
            return {
                'success': True,
                'table': table_path,
                'schema': schema_df.to_dict('records'),
                'column_count': len(schema_df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting schema: {str(e)}",
                'suggestion': "Please check the table name and try again"
            }
    
    async def _handle_table_exploration(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle table exploration queries"""
        try:
            source = intent['filters'].get('source')
            tables = self.dremio_client.list_tables(source=source)
            
            if not tables:
                return {
                    'success': True,
                    'message': "No tables found",
                    'tables': []
                }
            
            # Format table list
            table_list = [f"{schema}.{table}" for schema, table in tables]
            
            return {
                'success': True,
                'tables': table_list,
                'count': len(table_list),
                'source_filter': source
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error listing tables: {str(e)}"
            }
    
    async def _handle_metadata_request(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle metadata requests including wiki descriptions"""
        try:
            if not intent['entities']:
                return {
                    'success': False,
                    'error': "Please specify which table you want metadata for",
                    'suggestion': "Try: 'Tell me about table_name' or 'What is the description of source.schema.table'"
                }
            
            table_path = intent['entities'][0]
            metadata = self.dremio_client.get_dataset_metadata(table_path)
            
            return {
                'success': True,
                'table': table_path,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting metadata: {str(e)}"
            }
    
    async def _generate_sql_with_ai(self, query: str, intent: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query using OpenAI API (>=1.0 client)"""
        try:
            if not self.openai_client:
                return None
            # Get available tables for context
            tables = self.dremio_client.list_tables()
            table_context = "\n".join([f"- {schema}.{table}" for schema, table in tables[:20]])  # Limit to first 20
            
            prompt = (
                "You are a SQL expert for Dremio. Based on the user's natural language query, "
                "generate an appropriate SQL query.\n\n"
                f"Available tables:\n{table_context}\n\n"
                f"User query: \"{query}\"\n\n"
                f"Intent analysis: {json.dumps(intent, indent=2)}\n\n"
                "Generate a SQL query that answers the user's question. If the query involves aggregations, "
                "include appropriate GROUP BY clauses. Return only the SQL query, no explanations."
            )
            
            def _call_openai():
                return self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1,
                )
            
            response = await asyncio.to_thread(_call_openai)
            sql_query = response.choices[0].message.content.strip()
            sql_query = re.sub(r'^```sql\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            return sql_query
        except Exception as e:
            logger.warning(f"AI SQL generation failed: {str(e)}")
            return None
    
    def _generate_sql_heuristic(self, query: str, intent: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query using heuristic rules"""
        query_lower = query.lower()
        
        # Simple heuristics for common queries
        if 'show me' in query_lower or 'display' in query_lower:
            if intent['entities']:
                table = intent['entities'][0]
                return f"SELECT * FROM {table} LIMIT 100"
        
        if 'count' in query_lower or 'how many' in query_lower:
            if intent['entities']:
                table = intent['entities'][0]
                return f"SELECT COUNT(*) as count FROM {table}"
        
        if 'list' in query_lower and intent['entities']:
            table = intent['entities'][0]
            return f"SELECT * FROM {table} LIMIT 50"
        
        return None
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        suggestions = []
        
        # Get available tables
        tables = self.dremio_client.list_tables()
        table_names = [f"{schema}.{table}" for schema, table in tables]
        
        # Simple autocomplete for table names
        if '.' in partial_query:
            # User is typing a table name
            matching_tables = [t for t in table_names if t.lower().startswith(partial_query.lower())]
            suggestions.extend(matching_tables[:5])
        
        # Common query patterns
        common_patterns = [
            "SELECT * FROM ",
            "SELECT COUNT(*) FROM ",
            "SELECT DISTINCT ",
            "SHOW TABLES",
            "DESCRIBE TABLE "
        ]
        
        matching_patterns = [p for p in common_patterns if p.lower().startswith(partial_query.lower())]
        suggestions.extend(matching_patterns)
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    async def explain_query(self, sql_query: str) -> str:
        """Explain what a SQL query does in natural language"""
        if not self.openai_client:
            return "AI explanation not available. Please set OpenAI API key."
        
        try:
            prompt = (
                "Explain this SQL query in simple, natural language:\n\n"
                f"{sql_query}\n\n"
                "Provide a clear explanation of what this query does, what data it retrieves, "
                "and any important details about the results."
            )
            
            def _call_openai():
                return self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.3,
                )
            
            response = await asyncio.to_thread(_call_openai)
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error explaining query: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def get_data_insights(self, data: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate insights from query results"""
        if not data:
            return {"insights": "No data to analyze"}
        
        # Basic statistical insights
        insights = {
            "row_count": len(data),
            "column_count": len(data[0]) if data else 0,
            "columns": list(data[0].keys()) if data else []
        }
        
        # Try to identify numeric columns for basic stats
        numeric_columns = []
        for col in insights["columns"]:
            try:
                # Check if column contains numeric data
                sample_values = [row[col] for row in data[:10] if row[col] is not None]
                if sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                    numeric_columns.append(col)
            except:
                continue
        
        if numeric_columns:
            insights["numeric_columns"] = numeric_columns
            insights["suggestion"] = f"Consider using aggregations like SUM, AVG, MIN, MAX on columns: {', '.join(numeric_columns)}"
        
        return insights

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
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
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
            
            # Debug logging
            logger.info(f"Query: '{user_query}' -> Intent: {intent}")
            
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
                    'suggestion': "Try asking about data, table schemas, or available tables",
                    'debug_info': f"Intent analysis: {intent}"
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
            r'available|list all|show all|show me all',
            r'what tables|what datasets',
            r'show me.*tables|list.*tables|display.*tables'
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
        
        # Check for table exploration intent FIRST (most specific)
        if any(re.search(pattern, query_lower) for pattern in table_patterns):
            intent['type'] = 'table_exploration'
            
            # Extract source/schema filters
            if 'source' in query_lower:
                source_match = re.search(r'source[:\s]+([a-zA-Z_][a-zA-Z0-9_]*)', query_lower)
                if source_match:
                    intent['filters']['source'] = source_match.group(1)
        
        # Check for schema inquiry intent
        elif any(re.search(pattern, query_lower) for pattern in schema_patterns):
            intent['type'] = 'schema_inquiry'
            
            # Extract table names
            table_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b', query)
            intent['entities'] = [match for match in table_matches if '.' in match]
        
        # Check for metadata intent
        elif any(re.search(pattern, query_lower) for pattern in metadata_patterns):
            intent['type'] = 'metadata_request'
            
            # Extract table names
            table_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b', query)
            intent['entities'] = [match for match in table_matches if '.' in match]
        
        # Check for data query intent LAST (least specific)
        elif any(re.search(pattern, query_lower) for pattern in data_patterns):
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
                # Try heuristic as fallback even if AI is available
                sql_query = self._generate_sql_heuristic(query, intent)
                
                if not sql_query:
                    return {
                        'success': False,
                        'error': "Could not generate SQL query from your question",
                        'suggestion': "Try being more specific about the table and columns you want to query. For example: 'How many records are in the accounts table?'"
                    }
            
            # Log the generated SQL for debugging
            logger.info(f"Generated SQL query: {sql_query}")
            
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
                'suggestion': "Please check your table names and try again. You can also try: 'show me all tables' to see available tables"
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
                # Try to search wiki content for relevant tables
                query_lower = query.lower()
                
                # Search wiki content for matching terms
                wiki_results = self.dremio_client.search_wiki_content(query)
                
                if wiki_results:
                    # Format wiki search results
                    result_text = f"Found {len(wiki_results)} tables with relevant wiki documentation:\n\n"
                    for result in wiki_results[:5]:  # Show top 5 results
                        result_text += f"**{result['path']}**\n"
                        result_text += f"Type: {result['type']}\n"
                        result_text += f"Wiki snippet: {result['wiki_snippet']}\n\n"
                    
                    return {
                        'success': True,
                        'message': result_text,
                        'wiki_results': wiki_results,
                        'suggestion': f"Try: 'Tell me about {wiki_results[0]['path']}' for detailed information"
                    }
                
                # Fallback to common table name matching
                potential_tables = []
                common_table_names = ['accounts', 'customers', 'users', 'orders', 'products', 'sales', 'demographics', 'profile', 'data']
                
                for table_name in common_table_names:
                    if table_name in query_lower:
                        potential_tables.append(table_name)
                
                if potential_tables:
                    return {
                        'success': False,
                        'error': f"Please specify which table you want metadata for. I found these potential matches: {', '.join(potential_tables)}",
                        'suggestion': f"Try: 'Tell me about {potential_tables[0]}' or 'What is the description of {potential_tables[0]} table'"
                    }
                else:
                    return {
                        'success': False,
                        'error': "Please specify which table you want metadata for",
                        'suggestion': "Try: 'Tell me about table_name' or 'What is the description of source.schema.table'"
                    }
            
            table_path = intent['entities'][0]
            
            # Get comprehensive metadata including wiki
            basic_metadata = self.dremio_client.get_dataset_metadata(table_path)
            wiki_metadata = self.dremio_client.get_wiki_metadata(table_path)
            
            # Combine metadata
            combined_metadata = {
                'table': table_path,
                'basic_metadata': basic_metadata,
                'wiki_metadata': wiki_metadata
            }
            
            # Format response with wiki information
            response_text = f"**Metadata for {table_path}**\n\n"
            
            if wiki_metadata and wiki_metadata.get('parsed_metadata'):
                parsed = wiki_metadata['parsed_metadata']
                
                if parsed.get('description'):
                    response_text += f"**Description:** {parsed['description']}\n\n"
                
                if parsed.get('business_purpose'):
                    response_text += f"**Business Purpose:** {parsed['business_purpose']}\n\n"
                
                if parsed.get('data_source'):
                    response_text += f"**Data Source:** {parsed['data_source']}\n\n"
                
                if parsed.get('owner'):
                    response_text += f"**Owner:** {parsed['owner']}\n\n"
                
                if parsed.get('update_frequency'):
                    response_text += f"**Update Frequency:** {parsed['update_frequency']}\n\n"
                
                if parsed.get('tags'):
                    response_text += f"**Tags:** {', '.join(parsed['tags'])}\n\n"
                
                if parsed.get('column_descriptions'):
                    response_text += "**Column Descriptions:**\n"
                    for col, desc in parsed['column_descriptions'].items():
                        response_text += f"- {col}: {desc}\n"
                    response_text += "\n"
                
                if parsed.get('usage_notes'):
                    response_text += f"**Usage Notes:** {parsed['usage_notes']}\n\n"
                
                if parsed.get('data_quality_notes'):
                    response_text += f"**Data Quality Notes:** {parsed['data_quality_notes']}\n\n"
            
            elif basic_metadata.get('wiki_description'):
                response_text += f"**Description:** {basic_metadata['wiki_description']}\n\n"
            
            if basic_metadata.get('sample_data'):
                response_text += f"**Sample Data:** {len(basic_metadata['sample_data'])} rows available\n\n"
            
            return {
                'success': True,
                'formatted_response': response_text,
                'metadata': combined_metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error getting metadata: {str(e)}"
            }
    
    async def _generate_sql_with_ai(self, query: str, intent: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query using Anthropic Claude API"""
        try:
            if not self.openai_client:
                return None
            
            # Try to get available tables and wiki context, but don't fail if it doesn't work
            table_context = ""
            wiki_context = ""
            
            try:
                if self.dremio_client:
                    tables = self.dremio_client.list_tables()
                    table_context = "\n".join([f"- {schema}.{table}" for schema, table in tables[:20]])  # Limit to first 20
                    table_context = f"Available tables:\n{table_context}\n\n"
                    
                    # Try to get wiki context for relevant tables
                    query_lower = query.lower()
                    relevant_tables = []
                    for schema, table in tables[:10]:  # Check first 10 tables
                        if any(term in table.lower() or term in schema.lower() for term in query_lower.split()):
                            relevant_tables.append(f"{schema}.{table}")
                    
                    if relevant_tables:
                        wiki_context = "Relevant table documentation:\n"
                        for table_path in relevant_tables[:3]:  # Limit to 3 tables
                            wiki_metadata = self.dremio_client.get_wiki_metadata(table_path)
                            if wiki_metadata and wiki_metadata.get('parsed_metadata'):
                                parsed = wiki_metadata['parsed_metadata']
                                wiki_context += f"\n{table_path}:\n"
                                if parsed.get('description'):
                                    wiki_context += f"  Description: {parsed['description']}\n"
                                if parsed.get('business_purpose'):
                                    wiki_context += f"  Purpose: {parsed['business_purpose']}\n"
                                if parsed.get('column_descriptions'):
                                    wiki_context += "  Key columns:\n"
                                    for col, desc in list(parsed['column_descriptions'].items())[:3]:
                                        wiki_context += f"    - {col}: {desc}\n"
                        wiki_context += "\n"
                else:
                    table_context = "Note: No table context available. Use common table names like 'accounts', 'customers', 'orders', etc.\n\n"
            except Exception as e:
                logger.warning(f"Could not get table context: {str(e)}")
                table_context = "Note: Could not retrieve table list. Use common table names like 'accounts', 'customers', 'orders', etc.\n\n"
            
            prompt = (
                "You are a SQL expert for Dremio. Based on the user's natural language query, "
                "generate an appropriate SQL query.\n\n"
                f"{table_context}"
                f"{wiki_context}"
                f"User query: \"{query}\"\n\n"
                f"Intent analysis: {json.dumps(intent, indent=2)}\n\n"
                "Generate a SQL query that answers the user's question. Use the table documentation above "
                "to understand column names and business context. If the query involves aggregations, "
                "include appropriate GROUP BY clauses.\n\n"
                "TABLE NAME MATCHING: When the user asks about 'accounts', 'customers', etc., look for tables "
                "in the available tables list that contain those words (case-insensitive). Use the full "
                "qualified name (schema.table) from the available tables list.\n\n"
                "IMPORTANT: Avoid using reserved SQL words as column aliases. Use descriptive aliases like "
                "'total_count', 'record_count', 'customer_count', etc. instead of 'count'.\n\n"
                "Return only the SQL query, no explanations."
            )
            
            def _call_openai():
                return self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=500,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
            
            response = await asyncio.to_thread(_call_openai)
            sql_query = response.choices[0].message.content.strip()
            sql_query = re.sub(r'^```sql\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            
            # Clean up common SQL issues
            sql_query = self._clean_sql_query(sql_query)
            return sql_query
        except Exception as e:
            error_msg = str(e)
            if "Connection error" in error_msg:
                logger.warning(f"AI SQL generation failed due to network connectivity issue: {error_msg}")
                logger.info("Falling back to heuristic SQL generation")
            else:
                logger.warning(f"AI SQL generation failed: {error_msg}")
            return None
    
    def _generate_sql_heuristic(self, query: str, intent: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query using heuristic rules"""
        query_lower = query.lower()
        
        # Extract potential table names from common patterns
        potential_table = None
        
        # First, try to find matching tables from the actual table list
        try:
            if self.dremio_client:
                available_tables = self.dremio_client.list_tables()
                logger.info(f"Available tables for matching: {available_tables[:10]}")  # Log first 10 tables
                
                # Look for tables that match query terms (case-insensitive)
                for schema, table in available_tables:
                    table_lower = table.lower()
                    schema_lower = schema.lower()
                    
                    # Check if any word from the query matches the table name
                    query_words = query_lower.split()
                    for word in query_words:
                        if word in table_lower or word in schema_lower:
                            potential_table = f"{schema}.{table}"
                            logger.info(f"Found matching table: {potential_table} (matched word: {word})")
                            break
                    if potential_table:
                        break
        except Exception as e:
            logger.warning(f"Could not get available tables for heuristic: {str(e)}")
        
        # Fallback to common table names if no match found
        if not potential_table:
            logger.info(f"No matching table found in available tables, trying common table names")
            common_tables = ['accounts', 'customers', 'users', 'orders', 'products', 'sales', 'demographics', 'profile', 'data', 'tags', 'projects']
            for table in common_tables:
                if table in query_lower:
                    potential_table = table
                    logger.info(f"Using common table name: {potential_table}")
                    break
        
        # If still no table found, try to use the first available table as a fallback
        if not potential_table:
            try:
                if self.dremio_client:
                    available_tables = self.dremio_client.list_tables()
                    if available_tables:
                        # Use the first DataMesh table if available, otherwise first table
                        for schema, table in available_tables:
                            if 'datamesh' in schema.lower():
                                potential_table = f"{schema}.{table}"
                                logger.info(f"Using first DataMesh table as fallback: {potential_table}")
                                break
                        if not potential_table:
                            schema, table = available_tables[0]
                            potential_table = f"{schema}.{table}"
                            logger.info(f"Using first available table as fallback: {potential_table}")
            except Exception as e:
                logger.warning(f"Could not get fallback table: {str(e)}")
        
        # If we have entities from intent analysis, use those
        if intent['entities'] and not potential_table:
            potential_table = intent['entities'][0]
        
        # Simple heuristics for common queries
        if 'show me' in query_lower or 'display' in query_lower:
            if potential_table:
                sql = f"SELECT * FROM {potential_table} LIMIT 100"
            else:
                sql = "SELECT * FROM accounts LIMIT 100"  # Default fallback
            return self._clean_sql_query(sql)
        
        if 'count' in query_lower or 'how many' in query_lower:
            if potential_table:
                sql = f"SELECT COUNT(*) as total_count FROM {potential_table}"
            else:
                sql = "SELECT COUNT(*) as total_count FROM accounts"  # Default fallback
            return self._clean_sql_query(sql)
        
        if 'list' in query_lower:
            if potential_table:
                sql = f"SELECT * FROM {potential_table} LIMIT 50"
            else:
                sql = "SELECT * FROM accounts LIMIT 50"  # Default fallback
            return self._clean_sql_query(sql)
        
        # Handle "top" queries - try to find a reasonable column to order by
        if 'top' in query_lower:
            if potential_table:
                # For top queries, we'll need to make some assumptions about ordering
                # Try to find a reasonable column to order by or use a simple limit
                sql = f"SELECT * FROM {potential_table} LIMIT 10"
            else:
                sql = "SELECT * FROM accounts LIMIT 10"  # Default fallback
            return self._clean_sql_query(sql)
        
        # If we have a potential table but no specific pattern, do a basic select
        if potential_table:
            sql = f"SELECT * FROM {potential_table} LIMIT 10"
            return self._clean_sql_query(sql)
        
        return None
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean up common SQL issues and reserved word conflicts"""
        if not sql_query:
            return sql_query
        
        # Replace common reserved word aliases
        sql_query = re.sub(r'\bas\s+count\b', ' as total_count', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bas\s+order\b', ' as order_info', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bas\s+group\b', ' as group_info', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bas\s+user\b', ' as user_info', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bas\s+data\b', ' as data_info', sql_query, flags=re.IGNORECASE)
        
        # Ensure proper spacing around keywords
        sql_query = re.sub(r'\bSELECT\b', 'SELECT', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bFROM\b', ' FROM', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bWHERE\b', ' WHERE', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bGROUP\s+BY\b', ' GROUP BY', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bORDER\s+BY\b', ' ORDER BY', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bLIMIT\b', ' LIMIT', sql_query, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        sql_query = re.sub(r'\s+', ' ', sql_query).strip()
        
        return sql_query
    
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
            return "AI explanation not available. Please set Anthropic API key."
        
        try:
            prompt = (
                "Explain this SQL query in simple, natural language:\n\n"
                f"{sql_query}\n\n"
                "Provide a clear explanation of what this query does, what data it retrieves, "
                "and any important details about the results."
            )
            
            def _call_openai():
                return self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=300,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
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

#!/usr/bin/env python3
"""
Flask REST API for Dremio MCP Server
Handles natural language queries and returns structured JSON responses
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from dremio_client import DremioClient
from ai_agent import DremioAIAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DremioFlaskAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        # Initialize Dremio client
        self.dremio_client = None
        self.ai_agent = None
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'Dremio MCP Flask API',
                'version': '1.0.0'
            })
        
        @self.app.route('/query', methods=['POST'])
        def process_query():
            """Main endpoint for processing natural language queries"""
            try:
                data = request.get_json()
                if not data or 'question' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing required field: question',
                        'error_code': 'MISSING_QUESTION'
                    }), 400
                
                question = data['question'].strip()
                if not question:
                    return jsonify({
                        'success': False,
                        'error': 'Question cannot be empty',
                        'error_code': 'EMPTY_QUESTION'
                    }), 400
                
                # Process the query
                result = self._process_natural_language_query(question)
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}',
                    'error_code': 'INTERNAL_ERROR'
                }), 500
        
        @self.app.route('/tables', methods=['GET'])
        def list_tables():
            """List available tables"""
            try:
                if not self.dremio_client:
                    return jsonify({
                        'success': False,
                        'error': 'Dremio client not initialized',
                        'error_code': 'CLIENT_NOT_INITIALIZED'
                    }), 500
                
                tables = self.dremio_client.list_tables()
                return jsonify({
                    'success': True,
                    'data': {
                        'tables': tables,
                        'count': len(tables)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error listing tables: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Error listing tables: {str(e)}',
                    'error_code': 'LIST_TABLES_ERROR'
                }), 500
        
        @self.app.route('/table/<path:table_name>/metadata', methods=['GET'])
        def get_table_metadata(table_name):
            """Get metadata for a specific table"""
            try:
                if not self.dremio_client:
                    return jsonify({
                        'success': False,
                        'error': 'Dremio client not initialized',
                        'error_code': 'CLIENT_NOT_INITIALIZED'
                    }), 500
                
                # Get table schema
                schema = self.dremio_client.get_table_schema(table_name)
                
                # Get wiki description if available
                wiki_description = None
                try:
                    wiki_description = self.dremio_client.get_wiki_description(table_name)
                except Exception as e:
                    logger.warning(f"Could not get wiki description for {table_name}: {e}")
                
                return jsonify({
                    'success': True,
                    'data': {
                        'table_name': table_name,
                        'schema': schema,
                        'wiki_description': wiki_description,
                        'column_count': len(schema) if schema else 0
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting table metadata: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Error getting table metadata: {str(e)}',
                    'error_code': 'TABLE_METADATA_ERROR'
                }), 500
    
    def initialize_dremio_connection(self, config: Dict[str, Any]):
        """Initialize Dremio connection"""
        try:
            self.dremio_client = DremioClient(config)
            self.dremio_client.authenticate()
            logger.info("Dremio client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Dremio client: {e}")
            return False
    
    def initialize_ai_agent(self, openai_key: str):
        """Initialize AI agent"""
        try:
            self.ai_agent = DremioAIAgent(self.dremio_client)
            self.ai_agent.set_openai_key(openai_key)
            logger.info("AI agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            return False
    
    def _process_natural_language_query(self, question: str) -> Dict[str, Any]:
        """Process natural language query and return structured response"""
        try:
            # Analyze query intent
            intent = self._analyze_query_intent(question)
            logger.info(f"Query intent: {intent}")
            
            if intent == 'table_exploration':
                return self._handle_table_exploration(question)
            elif intent == 'metadata_request':
                return self._handle_metadata_request(question)
            elif intent == 'aggregation_query':
                return self._handle_aggregation_query(question)
            elif intent == 'count_query':
                return self._handle_count_query(question)
            elif intent == 'field_selection_query':
                return self._handle_field_selection_query(question)
            elif intent == 'data_query':
                return self._handle_data_query(question)
            else:
                return self._handle_general_query(question)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'error': f'Error processing query: {str(e)}',
                'error_code': 'QUERY_PROCESSING_ERROR'
            }
    
    def _analyze_query_intent(self, question: str) -> str:
        """Analyze query intent using enhanced pattern matching"""
        question_lower = question.lower()
        
        # Table exploration patterns
        table_patterns = [
            r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?(tables?|data)\b',
            r'\bwhat\s+(tables?|data)\s+(are\s+)?(available|there)\b',
            r'\b(available|existing)\s+(tables?|data)\b'
        ]
        
        # Metadata request patterns
        metadata_patterns = [
            r'\b(describe|explain|tell\s+me\s+about|what\s+is)\s+(the\s+)?(table|data|schema)\b',
            r'\b(metadata|information|details)\s+(about|for)\b',
            r'\b(columns?|fields?|structure)\s+(of|in)\b'
        ]
        
        # Aggregation query patterns
        aggregation_patterns = [
            r'\b(sum|total|add\s+up)\b',
            r'\b(average|mean|avg)\b',
            r'\b(minimum|min|lowest|smallest)\b',
            r'\b(maximum|max|highest|largest)\b',
            r'\b(statistics|stats|summary)\b',
            r'\b(group\s+by|grouped|grouping)\b'
        ]
        
        # Count query patterns
        count_patterns = [
            r'\b(how\s+many|count|number\s+of)\b',
            r'\b(total\s+count|record\s+count)\b'
        ]
        
        # Field selection patterns
        field_selection_patterns = [
            r'\b(show\s+me\s+only|just\s+the|only\s+the)\b',
            r'\b(select|get|fetch|retrieve)\s+(specific|particular|certain)\b',
            r'\b(columns?|fields?)\s+(only|just|specifically)\b',
            r'\b(what\s+are\s+the)\s+(names?|emails?|ids?)\b'
        ]
        
        # Data query patterns
        data_patterns = [
            r'\b(select|get|fetch|retrieve|show)\s+(data|records?|rows?)\b',
            r'\b(top|first|last)\s+\d+\b',
            r'\b(where|filter|find)\b',
            r'\b(sample|examples?)\b'
        ]
        
        import re
        
        # Check for table exploration
        for pattern in table_patterns:
            if re.search(pattern, question_lower):
                return 'table_exploration'
        
        # Check for metadata requests
        for pattern in metadata_patterns:
            if re.search(pattern, question_lower):
                return 'metadata_request'
        
        # Check for aggregation queries
        for pattern in aggregation_patterns:
            if re.search(pattern, question_lower):
                return 'aggregation_query'
        
        # Check for count queries
        for pattern in count_patterns:
            if re.search(pattern, question_lower):
                return 'count_query'
        
        # Check for field selection queries
        for pattern in field_selection_patterns:
            if re.search(pattern, question_lower):
                return 'field_selection_query'
        
        # Check for data queries
        for pattern in data_patterns:
            if re.search(pattern, question_lower):
                return 'data_query'
        
        # Default to general query
        return 'general'
    
    def _handle_table_exploration(self, question: str) -> Dict[str, Any]:
        """Handle table exploration queries"""
        try:
            tables = self.dremio_client.list_tables()
            
            # Filter tables based on question keywords
            filtered_tables = self._filter_tables_by_keywords(tables, question)
            
            return {
                'success': True,
                'query_type': 'table_exploration',
                'data': {
                    'tables': filtered_tables,
                    'total_count': len(filtered_tables),
                    'all_tables_count': len(tables)
                },
                'message': f'Found {len(filtered_tables)} tables matching your query'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error exploring tables: {str(e)}',
                'error_code': 'TABLE_EXPLORATION_ERROR'
            }
    
    def _handle_metadata_request(self, question: str) -> Dict[str, Any]:
        """Handle metadata requests"""
        try:
            # Extract table name from question
            table_name = self._extract_table_name_from_question(question)
            
            if not table_name:
                # Search for relevant tables
                tables = self.dremio_client.list_tables()
                relevant_tables = self._filter_tables_by_keywords(tables, question)
                
                return {
                    'success': True,
                    'query_type': 'metadata_request',
                    'data': {
                        'suggested_tables': relevant_tables[:5],  # Top 5 suggestions
                        'message': 'Please specify which table you want metadata for'
                    }
                }
            
            # Get table metadata
            schema = self.dremio_client.get_table_schema(table_name)
            wiki_description = None
            
            try:
                wiki_description = self.dremio_client.get_wiki_description(table_name)
            except Exception as e:
                logger.warning(f"Could not get wiki description: {e}")
            
            return {
                'success': True,
                'query_type': 'metadata_request',
                'data': {
                    'table_name': table_name,
                    'schema': schema,
                    'wiki_description': wiki_description,
                    'column_count': len(schema) if schema else 0
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting metadata: {str(e)}',
                'error_code': 'METADATA_ERROR'
            }
    
    def _handle_aggregation_query(self, question: str) -> Dict[str, Any]:
        """Handle aggregation queries (SUM, AVG, MIN, MAX, etc.)"""
        try:
            # Extract aggregation type and field
            aggregation_info = self._extract_aggregation_info(question)
            table_name = self._find_best_table_for_query(question)
            
            if not table_name:
                return {
                    'success': False,
                    'error': 'Could not determine which table to query',
                    'error_code': 'TABLE_NOT_FOUND'
                }
            
            # Generate aggregation SQL
            sql_query = self._generate_aggregation_sql(question, table_name, aggregation_info)
            
            if not sql_query:
                return {
                    'success': False,
                    'error': 'Could not generate aggregation query',
                    'error_code': 'AGGREGATION_SQL_FAILED'
                }
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            # Format aggregation results
            return self._format_aggregation_results(results, question, aggregation_info)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing aggregation query: {str(e)}',
                'error_code': 'AGGREGATION_ERROR'
            }
    
    def _handle_count_query(self, question: str) -> Dict[str, Any]:
        """Handle count queries specifically"""
        try:
            table_name = self._find_best_table_for_query(question)
            
            if not table_name:
                return {
                    'success': False,
                    'error': 'Could not determine which table to query',
                    'error_code': 'TABLE_NOT_FOUND'
                }
            
            # Generate count SQL
            sql_query = f"SELECT COUNT(*) as total_count FROM {table_name}"
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            # Format count results
            return self._format_count_results(results, question)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing count query: {str(e)}',
                'error_code': 'COUNT_ERROR'
            }
    
    def _handle_field_selection_query(self, question: str) -> Dict[str, Any]:
        """Handle field selection queries (specific columns only)"""
        try:
            # Extract requested fields
            requested_fields = self._extract_requested_fields(question)
            table_name = self._find_best_table_for_query(question)
            
            if not table_name:
                return {
                    'success': False,
                    'error': 'Could not determine which table to query',
                    'error_code': 'TABLE_NOT_FOUND'
                }
            
            # Get table schema to validate fields
            schema = self.dremio_client.get_table_schema(table_name)
            available_columns = [col['column_name'] for col in schema] if schema else []
            
            # Match requested fields to available columns
            selected_columns = self._match_columns_to_schema(requested_fields, available_columns)
            
            if not selected_columns:
                return {
                    'success': False,
                    'error': f'No matching columns found. Available columns: {available_columns}',
                    'error_code': 'COLUMNS_NOT_FOUND'
                }
            
            # Generate field selection SQL
            columns_str = ', '.join(selected_columns)
            sql_query = f"SELECT {columns_str} FROM {table_name} LIMIT 100"
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            # Format field selection results
            return self._format_field_selection_results(results, question, selected_columns)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing field selection query: {str(e)}',
                'error_code': 'FIELD_SELECTION_ERROR'
            }
    
    def _handle_data_query(self, question: str) -> Dict[str, Any]:
        """Handle data queries"""
        try:
            # Try AI-generated SQL first
            sql_query = None
            if self.ai_agent:
                try:
                    sql_query = self.ai_agent.generate_sql(question)
                    logger.info(f"AI generated SQL: {sql_query}")
                except Exception as e:
                    logger.warning(f"AI SQL generation failed: {e}")
            
            # Fallback to heuristic SQL generation
            if not sql_query:
                sql_query = self._generate_heuristic_sql(question)
                logger.info(f"Heuristic SQL: {sql_query}")
            
            if not sql_query:
                return {
                    'success': False,
                    'error': 'Could not generate SQL query from your question',
                    'error_code': 'SQL_GENERATION_FAILED'
                }
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            # Process results
            return self._format_query_results(results, question)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error executing data query: {str(e)}',
                'error_code': 'DATA_QUERY_ERROR'
            }
    
    def _handle_general_query(self, question: str) -> Dict[str, Any]:
        """Handle general queries"""
        try:
            # Try to find relevant tables
            tables = self.dremio_client.list_tables()
            relevant_tables = self._filter_tables_by_keywords(tables, question)
            
            return {
                'success': True,
                'query_type': 'general',
                'data': {
                    'suggested_tables': relevant_tables[:5],
                    'message': 'I found some relevant tables. Please be more specific about what you want to do with the data.'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing general query: {str(e)}',
                'error_code': 'GENERAL_QUERY_ERROR'
            }
    
    def _filter_tables_by_keywords(self, tables: List[str], question: str) -> List[str]:
        """Filter tables based on keywords in the question"""
        question_lower = question.lower()
        keywords = question_lower.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'show', 'me', 'all', 'get', 'find', 'what', 'how', 'many', 'count', 'list', 'display'}
        keywords = [word for word in keywords if word not in stop_words and len(word) > 2]
        
        if not keywords:
            return tables
        
        filtered_tables = []
        for table in tables:
            table_lower = table.lower()
            if any(keyword in table_lower for keyword in keywords):
                filtered_tables.append(table)
        
        return filtered_tables if filtered_tables else tables[:10]  # Return top 10 if no matches
    
    def _extract_table_name_from_question(self, question: str) -> Optional[str]:
        """Extract table name from question"""
        # Look for common table name patterns
        import re
        
        # Pattern for fully qualified table names (schema.table)
        pattern = r'\b\w+\.\w+\.\w+\b'
        matches = re.findall(pattern, question)
        if matches:
            return matches[0]
        
        # Pattern for simple table names
        pattern = r'\b(?:table|data|dataset)\s+(\w+)\b'
        match = re.search(pattern, question.lower())
        if match:
            table_name = match.group(1)
            # Try to find the full qualified name
            tables = self.dremio_client.list_tables()
            for table in tables:
                if table.endswith(f'.{table_name}') or table_name in table:
                    return table
        
        return None
    
    def _generate_heuristic_sql(self, question: str) -> Optional[str]:
        """Generate SQL using heuristic approach"""
        question_lower = question.lower()
        
        # Count queries
        if any(word in question_lower for word in ['how many', 'count', 'number of']):
            table_name = self._find_best_table_for_query(question)
            if table_name:
                return f"SELECT COUNT(*) as total_count FROM {table_name}"
        
        # Top N queries
        top_match = re.search(r'top\s+(\d+)', question_lower)
        if top_match:
            limit = int(top_match.group(1))
            table_name = self._find_best_table_for_query(question)
            if table_name:
                return f"SELECT * FROM {table_name} LIMIT {limit}"
        
        # General data queries
        table_name = self._find_best_table_for_query(question)
        if table_name:
            return f"SELECT * FROM {table_name} LIMIT 100"
        
        return None
    
    def _find_best_table_for_query(self, question: str) -> Optional[str]:
        """Find the best table for a query"""
        tables = self.dremio_client.list_tables()
        question_lower = question.lower()
        
        # Look for exact matches first
        for table in tables:
            table_lower = table.lower()
            if any(word in table_lower for word in question_lower.split()):
                return table
        
        # Fallback to common table names
        common_tables = ['accounts', 'users', 'customers', 'demographic', 'projects', 'tags']
        for common in common_tables:
            if common in question_lower:
                for table in tables:
                    if common in table.lower():
                        return table
        
        # Return first available table as last resort
        return tables[0] if tables else None
    
    def _extract_aggregation_info(self, question: str) -> Dict[str, Any]:
        """Extract aggregation type and field from question"""
        question_lower = question.lower()
        
        # Determine aggregation type
        aggregation_type = None
        if any(word in question_lower for word in ['sum', 'total', 'add up']):
            aggregation_type = 'SUM'
        elif any(word in question_lower for word in ['average', 'mean', 'avg']):
            aggregation_type = 'AVG'
        elif any(word in question_lower for word in ['minimum', 'min', 'lowest', 'smallest']):
            aggregation_type = 'MIN'
        elif any(word in question_lower for word in ['maximum', 'max', 'highest', 'largest']):
            aggregation_type = 'MAX'
        elif any(word in question_lower for word in ['statistics', 'stats', 'summary']):
            aggregation_type = 'STATS'
        
        # Extract field name
        field_name = None
        import re
        
        # Look for common field patterns
        field_patterns = [
            r'\b(amount|value|price|cost|revenue|sales|income)\b',
            r'\b(age|score|rating|count|number)\b',
            r'\b(id|user_id|customer_id|account_id)\b'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, question_lower)
            if match:
                field_name = match.group(1)
                break
        
        return {
            'type': aggregation_type,
            'field': field_name,
            'group_by': 'group by' in question_lower
        }
    
    def _generate_aggregation_sql(self, question: str, table_name: str, aggregation_info: Dict[str, Any]) -> Optional[str]:
        """Generate SQL for aggregation queries"""
        agg_type = aggregation_info['type']
        field = aggregation_info['field']
        
        if not agg_type:
            return None
        
        if agg_type == 'STATS':
            # Generate comprehensive statistics
            if field:
                return f"""
                SELECT 
                    COUNT(*) as record_count,
                    AVG({field}) as average_{field},
                    MIN({field}) as min_{field},
                    MAX({field}) as max_{field},
                    SUM({field}) as total_{field}
                FROM {table_name}
                """
            else:
                return f"SELECT COUNT(*) as record_count FROM {table_name}"
        
        elif field:
            return f"SELECT {agg_type}({field}) as {agg_type.lower()}_{field} FROM {table_name}"
        else:
            # Fallback to count if no field specified
            return f"SELECT COUNT(*) as total_count FROM {table_name}"
    
    def _extract_requested_fields(self, question: str) -> List[str]:
        """Extract requested field names from question"""
        question_lower = question.lower()
        requested_fields = []
        
        # Common field patterns
        field_patterns = [
            r'\b(names?|name)\b',
            r'\b(emails?|email)\b',
            r'\b(ids?|id)\b',
            r'\b(ages?|age)\b',
            r'\b(addresses?|address)\b',
            r'\b(phones?|phone|mobile)\b',
            r'\b(dates?|date|created|updated)\b',
            r'\b(amounts?|amount|value|price)\b'
        ]
        
        import re
        for pattern in field_patterns:
            matches = re.findall(pattern, question_lower)
            requested_fields.extend(matches)
        
        return list(set(requested_fields))  # Remove duplicates
    
    def _match_columns_to_schema(self, requested_fields: List[str], available_columns: List[str]) -> List[str]:
        """Match requested fields to available columns"""
        matched_columns = []
        
        for requested in requested_fields:
            # Direct match
            if requested in available_columns:
                matched_columns.append(requested)
                continue
            
            # Partial match
            for column in available_columns:
                if requested in column.lower() or column.lower() in requested:
                    matched_columns.append(column)
                    break
        
        return matched_columns
    
    def _format_aggregation_results(self, results: pd.DataFrame, question: str, aggregation_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format aggregation query results"""
        try:
            if results is None or results.empty:
                return {
                    'success': True,
                    'query_type': 'aggregation_query',
                    'data': {
                        'rows': [],
                        'row_count': 0,
                        'columns': [],
                        'message': 'No data found for aggregation'
                    }
                }
            
            rows = results.to_dict('records')
            columns = list(results.columns)
            column_types = {col: str(results[col].dtype) for col in columns}
            
            return {
                'success': True,
                'query_type': 'aggregation_query',
                'data': {
                    'rows': rows,
                    'row_count': len(rows),
                    'columns': columns,
                    'column_types': column_types,
                    'aggregation_type': aggregation_info['type'],
                    'message': f"Aggregation results for {aggregation_info['type']}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error formatting aggregation results: {str(e)}',
                'error_code': 'AGGREGATION_FORMATTING_ERROR'
            }
    
    def _format_count_results(self, results: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Format count query results"""
        try:
            if results is None or results.empty:
                return {
                    'success': True,
                    'query_type': 'count_query',
                    'data': {
                        'rows': [],
                        'row_count': 0,
                        'columns': [],
                        'message': 'No data found'
                    }
                }
            
            rows = results.to_dict('records')
            columns = list(results.columns)
            column_types = {col: str(results[col].dtype) for col in columns}
            
            # Extract count value
            count_value = None
            if rows and 'total_count' in columns:
                count_value = rows[0]['total_count']
            elif rows and len(columns) == 1:
                count_value = rows[0][columns[0]]
            
            return {
                'success': True,
                'query_type': 'count_query',
                'data': {
                    'rows': rows,
                    'row_count': len(rows),
                    'columns': columns,
                    'column_types': column_types,
                    'is_count_query': True,
                    'count_value': count_value,
                    'message': f"Total count: {count_value}" if count_value else "Count query executed"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error formatting count results: {str(e)}',
                'error_code': 'COUNT_FORMATTING_ERROR'
            }
    
    def _format_field_selection_results(self, results: pd.DataFrame, question: str, selected_columns: List[str]) -> Dict[str, Any]:
        """Format field selection query results"""
        try:
            if results is None or results.empty:
                return {
                    'success': True,
                    'query_type': 'field_selection_query',
                    'data': {
                        'rows': [],
                        'row_count': 0,
                        'columns': [],
                        'message': 'No data found for selected fields'
                    }
                }
            
            rows = results.to_dict('records')
            columns = list(results.columns)
            column_types = {col: str(results[col].dtype) for col in columns}
            
            return {
                'success': True,
                'query_type': 'field_selection_query',
                'data': {
                    'rows': rows,
                    'row_count': len(rows),
                    'columns': columns,
                    'column_types': column_types,
                    'selected_columns': selected_columns,
                    'message': f"Selected fields: {', '.join(selected_columns)}"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error formatting field selection results: {str(e)}',
                'error_code': 'FIELD_SELECTION_FORMATTING_ERROR'
            }
    
    def _format_query_results(self, results: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Format query results into structured JSON"""
        try:
            if results is None or results.empty:
                return {
                    'success': True,
                    'query_type': 'data_query',
                    'data': {
                        'rows': [],
                        'row_count': 0,
                        'columns': [],
                        'message': 'No data found'
                    }
                }
            
            # Convert DataFrame to list of dictionaries
            rows = results.to_dict('records')
            
            # Get column information
            columns = list(results.columns)
            column_types = {col: str(results[col].dtype) for col in columns}
            
            # Check if this is a count query
            is_count_query = any(word in question.lower() for word in ['how many', 'count', 'number of'])
            
            response = {
                'success': True,
                'query_type': 'data_query',
                'data': {
                    'rows': rows,
                    'row_count': len(rows),
                    'columns': columns,
                    'column_types': column_types,
                    'is_count_query': is_count_query
                }
            }
            
            # Add specific message for count queries
            if is_count_query and len(rows) == 1 and 'total_count' in columns:
                response['data']['message'] = f"Total count: {rows[0]['total_count']}"
            elif is_count_query and len(rows) == 1 and len(columns) == 1:
                response['data']['message'] = f"Total count: {rows[0][columns[0]]}"
            else:
                response['data']['message'] = f"Found {len(rows)} rows"
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error formatting results: {str(e)}',
                'error_code': 'RESULT_FORMATTING_ERROR'
            }
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting Flask API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main function to run the Flask API"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dremio MCP Flask API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--dremio-host', required=True, help='Dremio host')
    parser.add_argument('--dremio-username', required=True, help='Dremio username')
    parser.add_argument('--dremio-password', required=True, help='Dremio password')
    parser.add_argument('--openai-key', help='OpenAI API key (optional)')
    parser.add_argument('--verify-ssl', action='store_true', help='Verify SSL certificates')
    parser.add_argument('--cert-path', help='Path to SSL certificate')
    parser.add_argument('--flight-port', type=int, default=32010, help='Dremio Flight port')
    parser.add_argument('--default-source', help='Default Dremio source')
    parser.add_argument('--default-schema', help='Default Dremio schema')
    
    args = parser.parse_args()
    
    # Create Dremio config
    config = {
        'host': args.dremio_host,
        'username': args.dremio_username,
        'password': args.dremio_password,
        'verify_ssl': args.verify_ssl,
        'cert_path': args.cert_path,
        'flight_port': args.flight_port,
        'default_source': args.default_source,
        'default_schema': args.default_schema
    }
    
    # Create Flask API
    api = DremioFlaskAPI()
    
    # Initialize Dremio connection
    if not api.initialize_dremio_connection(config):
        logger.error("Failed to initialize Dremio connection")
        return 1
    
    # Initialize AI agent if OpenAI key is provided
    if args.openai_key:
        if not api.initialize_ai_agent(args.openai_key):
            logger.warning("Failed to initialize AI agent, continuing without AI features")
    
    # Run the server
    api.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python3
"""
Enhanced AI Agent with AWS Bedrock Support
Supports both OpenAI and AWS Bedrock for SQL generation
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Any
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DremioAIAgentBedrock:
    """Enhanced AI agent with AWS Bedrock support for natural language to SQL conversion"""
    
    def __init__(self, dremio_client, provider: str = "openai", bedrock_model_id: str = None):
        self.dremio_client = dremio_client
        self.provider = provider.lower()
        self.bedrock_model_id = bedrock_model_id or os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        # Initialize providers
        self.openai_client = None
        self.bedrock_client = None
        
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "bedrock":
            self._init_bedrock()
        else:
            logger.warning(f"Unknown provider: {provider}. Using heuristic SQL generation.")

    def _normalize_table_names(self, tables: List[Any]) -> List[str]:
        """Convert table entries to fully qualified string names.

        Accepts items like:
        - "DataMesh.application.accounts"
        - (schema, table)
        - (source, schema, table)
        Returns a list of dotted strings.
        """
        normalized: List[str] = []
        for item in tables or []:
            if isinstance(item, str):
                normalized.append(item)
            elif isinstance(item, tuple) or isinstance(item, list):
                parts = [str(p) for p in item if p is not None]
                if parts:
                    normalized.append(".".join(parts))
            else:
                try:
                    normalized.append(str(item))
                except Exception:
                    continue
        return normalized
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("No OpenAI API key found")
        except ImportError:
            logger.error("OpenAI package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _init_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            import boto3
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"Bedrock client initialized with model: {self.bedrock_model_id}")
        except ImportError:
            logger.error("boto3 package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock: {e}")
    
    def set_openai_key(self, api_key: str):
        """Set OpenAI API key"""
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.provider = "openai"
            logger.info("OpenAI client configured")
        except Exception as e:
            logger.error(f"Failed to set OpenAI key: {e}")
    
    def set_bedrock_config(self, model_id: str, region: str = None):
        """Set Bedrock configuration"""
        self.bedrock_model_id = model_id
        if region:
            os.environ['AWS_REGION'] = region
        self.provider = "bedrock"
        self._init_bedrock()
    
    def process_query(self, question: str) -> str:
        """Process natural language query and return response"""
        try:
            # Analyze query intent
            intent = self._analyze_query_intent(question)
            logger.info(f"Query intent: {intent}")
            
            if intent == 'table_exploration':
                return self._handle_table_exploration(question)
            elif intent == 'metadata_request':
                return self._handle_metadata_request(question)
            elif intent == 'data_query':
                return self._handle_data_query(question)
            else:
                return self._handle_general_query(question)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing query: {str(e)}"
    
    def process_query_structured(self, question: str) -> Dict[str, Any]:
        """Process natural language query and return structured response"""
        try:
            # Analyze query intent
            intent = self._analyze_query_intent(question)
            logger.info(f"Query intent: {intent}")
            
            if intent == 'table_exploration':
                return self._handle_table_exploration_structured(question)
            elif intent == 'metadata_request':
                return self._handle_metadata_request_structured(question)
            elif intent == 'data_query':
                return self._handle_data_query_structured(question)
            else:
                return self._handle_general_query_structured(question)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "message": f"Error processing query: {str(e)}",
                "error": str(e),
                "success": False
            }
    
    def _analyze_query_intent(self, question: str) -> str:
        """Analyze query intent using pattern matching"""
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
        
        # Data query patterns
        data_patterns = [
            r'\b(how\s+many|count|number\s+of)\b',
            r'\b(select|get|fetch|retrieve|show)\s+(data|records?|rows?)\b',
            r'\b(top|first|last)\s+\d+\b',
            r'\b(where|filter|find)\b'
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
        
        # Check for data queries
        for pattern in data_patterns:
            if re.search(pattern, question_lower):
                return 'data_query'
        
        # Default to general query
        return 'general'
    
    def _handle_table_exploration(self, question: str) -> str:
        """Handle table exploration queries"""
        try:
            tables_raw = self.dremio_client.list_tables()
            tables = self._normalize_table_names(tables_raw)
            
            # Filter tables based on question keywords
            filtered_tables = self._filter_tables_by_keywords(tables, question)
            
            if filtered_tables:
                return f"Found {len(filtered_tables)} tables matching your query:\n" + "\n".join(f"- {table}" for table in filtered_tables[:10])
            else:
                return f"Found {len(tables)} total tables:\n" + "\n".join(f"- {table}" for table in tables[:10])
                
        except Exception as e:
            return f"Error exploring tables: {str(e)}"
    
    def _handle_metadata_request(self, question: str) -> str:
        """Handle metadata requests"""
        try:
            # Extract table name from question
            table_name = self._extract_table_name_from_question(question)
            
            if not table_name:
                # Search for relevant tables
                tables = self._normalize_table_names(self.dremio_client.list_tables())
                relevant_tables = self._filter_tables_by_keywords(tables, question)
                
                if relevant_tables:
                    return f"Please specify which table you want metadata for. Found these relevant tables:\n" + "\n".join(f"- {table}" for table in relevant_tables[:5])
                else:
                    return "Please specify which table you want metadata for."
            
            # Get table metadata
            schema = self.dremio_client.get_table_schema(table_name)
            wiki_description = None
            
            try:
                wiki_description = self.dremio_client.get_wiki_description(table_name)
            except Exception as e:
                logger.warning(f"Could not get wiki description: {e}")
            
            result = f"Metadata for table '{table_name}':\n"
            result += f"Columns ({len(schema) if schema else 0}):\n"
            
            if schema:
                for col in schema:
                    result += f"- {col['column_name']}: {col['data_type']}\n"
            
            if wiki_description:
                result += f"\nDescription:\n{wiki_description[:200]}..."
            
            return result
            
        except Exception as e:
            return f"Error getting metadata: {str(e)}"
    
    def _handle_data_query(self, question: str) -> str:
        """Handle data queries"""
        try:
            # Try AI-generated SQL first
            sql_query = None
            if self.provider == "openai" and self.openai_client:
                try:
                    sql_query = self._generate_sql_with_openai(question)
                    logger.info(f"OpenAI generated SQL: {sql_query}")
                except Exception as e:
                    logger.warning(f"OpenAI SQL generation failed: {e}")
            elif self.provider == "bedrock" and self.bedrock_client:
                try:
                    sql_query = self._generate_sql_with_bedrock(question)
                    logger.info(f"Bedrock generated SQL: {sql_query}")
                except Exception as e:
                    logger.warning(f"Bedrock SQL generation failed: {e}")
            
            # Fallback to heuristic SQL generation
            if not sql_query:
                sql_query = self._generate_sql_heuristic(question)
                logger.info(f"Heuristic SQL: {sql_query}")
            
            if not sql_query:
                return "Could not generate SQL query from your question. Please try being more specific about the table and columns you want to query."
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            if results is None or results.empty:
                return "No data found for your query."
            
            # Format results
            return self._format_query_results(results, question)
            
        except Exception as e:
            return f"Error executing data query: {str(e)}"
    
    def _handle_data_query_structured(self, question: str) -> Dict[str, Any]:
        """Handle data queries and return structured response"""
        try:
            # Try AI-generated SQL first
            sql_query = None
            if self.provider == "openai" and self.openai_client:
                try:
                    sql_query = self._generate_sql_with_openai(question)
                    logger.info(f"OpenAI generated SQL: {sql_query}")
                except Exception as e:
                    logger.warning(f"OpenAI SQL generation failed: {e}")
            elif self.provider == "bedrock" and self.bedrock_client:
                try:
                    sql_query = self._generate_sql_with_bedrock(question)
                    logger.info(f"Bedrock generated SQL: {sql_query}")
                except Exception as e:
                    logger.warning(f"Bedrock SQL generation failed: {e}")
            
            # Fallback to heuristic SQL generation
            if not sql_query:
                sql_query = self._generate_sql_heuristic(question)
                logger.info(f"Heuristic SQL: {sql_query}")
            
            if not sql_query:
                return {
                    "message": "Could not generate SQL query from your question. Please try being more specific about the table and columns you want to query.",
                    "success": False,
                    "error": "SQL generation failed"
                }
            
            # Execute query
            results = self.dremio_client.execute_query(sql_query)
            
            if results is None or results.empty:
                return {
                    "message": "No data found for your query.",
                    "row_count": 0,
                    "rows": [],
                    "columns": [],
                    "success": True
                }
            
            # Format results as structured data
            structured_results = self._format_query_results_structured(results, question)
            structured_results["sql_query"] = sql_query
            structured_results["success"] = True
            return structured_results
            
        except Exception as e:
            return {
                "message": f"Error executing data query: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _handle_general_query(self, question: str) -> str:
        """Handle general queries"""
        try:
            # Try to find relevant tables
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            relevant_tables = self._filter_tables_by_keywords(tables, question)
            
            if relevant_tables:
                return f"I found some relevant tables. Please be more specific about what you want to do with the data.\nRelevant tables:\n" + "\n".join(f"- {table}" for table in relevant_tables[:5])
            else:
                return "I found some tables. Please be more specific about what you want to do with the data."
                
        except Exception as e:
            return f"Error processing general query: {str(e)}"
    
    def _handle_table_exploration_structured(self, question: str) -> Dict[str, Any]:
        """Handle table exploration queries and return structured response"""
        try:
            tables_raw = self.dremio_client.list_tables()
            tables = self._normalize_table_names(tables_raw)
            
            # Filter tables based on question keywords
            filtered_tables = self._filter_tables_by_keywords(tables, question)
            
            return {
                "message": f"Found {len(filtered_tables)} tables matching your query" if filtered_tables else f"Found {len(tables)} total tables",
                "tables": filtered_tables[:10] if filtered_tables else tables[:10],
                "total_count": len(filtered_tables) if filtered_tables else len(tables),
                "success": True
            }
                
        except Exception as e:
            return {
                "message": f"Error exploring tables: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _handle_metadata_request_structured(self, question: str) -> Dict[str, Any]:
        """Handle metadata requests and return structured response"""
        try:
            # Extract table name from question
            table_name = self._extract_table_name_from_question(question)
            
            if not table_name:
                # Search for relevant tables
                tables = self._normalize_table_names(self.dremio_client.list_tables())
                relevant_tables = self._filter_tables_by_keywords(tables, question)
                
                return {
                    "message": "Please specify which table you want metadata for.",
                    "relevant_tables": relevant_tables[:5] if relevant_tables else [],
                    "success": False,
                    "error": "No table specified"
                }
            
            # Get table metadata
            schema = self.dremio_client.get_table_schema(table_name)
            wiki_description = None
            
            try:
                wiki_description = self.dremio_client.get_wiki_description(table_name)
            except Exception as e:
                logger.warning(f"Could not get wiki description: {e}")
            
            schema_data = []
            if schema is not None and not schema.empty:
                schema_data = [{"column_name": row['column_name'], "data_type": row['data_type']} 
                              for _, row in schema.iterrows()]
            
            return {
                "message": f"Metadata for table '{table_name}'",
                "table_name": table_name,
                "columns": schema_data,
                "column_count": len(schema_data),
                "wiki_description": wiki_description[:200] + "..." if wiki_description else None,
                "success": True
            }
            
        except Exception as e:
            return {
                "message": f"Error getting metadata: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _handle_general_query_structured(self, question: str) -> Dict[str, Any]:
        """Handle general queries and return structured response"""
        try:
            # Try to find relevant tables
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            relevant_tables = self._filter_tables_by_keywords(tables, question)
            
            return {
                "message": "I found some relevant tables. Please be more specific about what you want to do with the data." if relevant_tables else "I found some tables. Please be more specific about what you want to do with the data.",
                "relevant_tables": relevant_tables[:5] if relevant_tables else [],
                "success": True
            }
                
        except Exception as e:
            return {
                "message": f"Error processing general query: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _generate_sql_with_openai(self, question: str) -> Optional[str]:
        """Generate SQL using OpenAI"""
        try:
            # Get available tables and their schemas
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            table_info = []
            
            for table in tables[:10]:  # Limit to first 10 tables
                try:
                    schema = self.dremio_client.get_table_schema(table)
                    if schema is not None and not schema.empty:
                        columns = [row['column_name'] for _, row in schema.iterrows()]
                        table_info.append(f"{table}: {', '.join(columns)}")
                except Exception as e:
                    logger.warning(f"Could not get schema for {table}: {e}")
            
            # Get wiki context
            wiki_context = self._get_wiki_context(question)
            
            prompt = f"""You are a SQL expert for Dremio. Generate a SQL query based on the user's question.

Available tables and columns:
{chr(10).join(table_info)}

Wiki context:
{wiki_context}

User question: {question}

Rules:
1. Use fully qualified table names (e.g., DataMesh.application.accounts)
2. Always use LIMIT for queries that might return many rows
3. Avoid reserved words as column aliases (use total_count instead of count)
4. Be specific about table and column names
5. Return only the SQL query, no explanations

SQL Query:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            logger.error(f"OpenAI SQL generation failed: {e}")
            return None
    
    def _generate_sql_with_bedrock(self, question: str) -> Optional[str]:
        """Generate SQL using AWS Bedrock"""
        try:
            # Get available tables and their schemas
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            table_info = []
            
            for table in tables[:10]:  # Limit to first 10 tables
                try:
                    schema = self.dremio_client.get_table_schema(table)
                    if schema is not None and not schema.empty:
                        columns = [row['column_name'] for _, row in schema.iterrows()]
                        table_info.append(f"{table}: {', '.join(columns)}")
                except Exception as e:
                    logger.warning(f"Could not get schema for {table}: {e}")
            
            # Get wiki context
            wiki_context = self._get_wiki_context(question)
            
            system_prompt = """You are a SQL expert for Dremio. Generate a SQL query based on the user's question.

Rules:
1. Use fully qualified table names (e.g., DataMesh.application.accounts)
2. Always use LIMIT for queries that might return many rows
3. Avoid reserved words as column aliases (use total_count instead of count)
4. Be specific about table and column names
5. Return only the SQL query, no explanations"""

            user_prompt = f"""Available tables and columns:
{chr(10).join(table_info)}

Wiki context:
{wiki_context}

User question: {question}

Generate SQL Query:"""

            # Prepare Bedrock request
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.1,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_prompt}]
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model_id,
                accept="application/json",
                contentType="application/json",
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            
            # Extract text from response
            sql_query = ""
            for content in result.get('content', []):
                if content.get('type') == 'text':
                    sql_query += content.get('text', '')
            
            sql_query = sql_query.strip()
            
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Bedrock SQL generation failed: {e}")
            return None
    
    def _generate_sql_heuristic(self, question: str) -> Optional[str]:
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
    
    def _get_wiki_context(self, question: str) -> str:
        """Get relevant wiki context for the question"""
        try:
            # Search for relevant tables
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            relevant_tables = self._filter_tables_by_keywords(tables, question)
            
            wiki_context = ""
            for table in relevant_tables[:3]:  # Limit to first 3 tables
                try:
                    wiki_description = self.dremio_client.get_wiki_description(table)
                    if wiki_description:
                        wiki_context += f"\n{table}:\n{wiki_description[:200]}...\n"
                except Exception as e:
                    logger.warning(f"Could not get wiki for {table}: {e}")
            
            return wiki_context
            
        except Exception as e:
            logger.warning(f"Could not get wiki context: {e}")
            return ""
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean up SQL query to avoid reserved word issues"""
        # Replace common reserved words used as aliases
        replacements = {
            'as count': 'as total_count',
            'as sum': 'as total_sum',
            'as avg': 'as average_value',
            'as min': 'as minimum_value',
            'as max': 'as maximum_value'
        }
        
        for old, new in replacements.items():
            sql_query = sql_query.replace(old, new)
        
        return sql_query
    
    def _filter_tables_by_keywords(self, tables: List[Any], question: str) -> List[str]:
        """Filter tables based on keywords in the question"""
        # Ensure tables are strings
        tables = self._normalize_table_names(tables)
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
        
        return filtered_tables if filtered_tables else tables[:10]
    
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
            tables = self._normalize_table_names(self.dremio_client.list_tables())
            for table in tables:
                if table.endswith(f'.{table_name}') or table_name in table:
                    return table
        
        return None
    
    def _find_best_table_for_query(self, question: str) -> Optional[str]:
        """Find the best table for a query"""
        tables = self._normalize_table_names(self.dremio_client.list_tables())
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
    
    def _format_query_results(self, results: pd.DataFrame, question: str) -> str:
        """Format query results for display"""
        try:
            if results is None or results.empty:
                return "No data found for your query."
            
            # Check if this is a count query
            is_count_query = any(word in question.lower() for word in ['how many', 'count', 'number of'])
            
            if is_count_query and len(results) == 1:
                # Extract count value
                if 'total_count' in results.columns:
                    count_value = results.iloc[0]['total_count']
                    return f"Total count: {count_value}"
                elif len(results.columns) == 1:
                    count_value = results.iloc[0, 0]
                    return f"Total count: {count_value}"
            
            # Format regular results
            result_text = f"Query successful! Found {len(results)} rows.\n\n"
            result_text += "Results:\n"
            result_text += results.to_string(index=False, max_rows=20)
            
            if len(results) >= 20:
                result_text += f"\n\n... (showing first 20 rows of {len(results)} total)"
            
            return result_text
            
        except Exception as e:
            return f"Error formatting results: {str(e)}"
    
    def _format_query_results_structured(self, results: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Format query results as structured data for JSON response"""
        try:
            if results is None or results.empty:
                return {
                    "message": "No data found for your query.",
                    "row_count": 0,
                    "rows": [],
                    "columns": []
                }
            
            # Check if this is a count query
            is_count_query = any(word in question.lower() for word in ['how many', 'count', 'number of'])
            
            if is_count_query and len(results) == 1:
                # Extract count value
                if 'total_count' in results.columns:
                    count_value = results.iloc[0]['total_count']
                    return {
                        "message": f"Total count: {count_value}",
                        "row_count": 1,
                        "count_value": count_value,
                        "is_count_query": True
                    }
                elif len(results.columns) == 1:
                    count_value = results.iloc[0, 0]
                    return {
                        "message": f"Total count: {count_value}",
                        "row_count": 1,
                        "count_value": count_value,
                        "is_count_query": True
                    }
            
            # Convert DataFrame to structured format
            rows = results.to_dict('records')
            columns = list(results.columns)
            
            return {
                "message": f"Query successful! Found {len(results)} rows.",
                "row_count": len(results),
                "rows": rows,
                "columns": columns,
                "is_count_query": False
            }
            
        except Exception as e:
            return {
                "message": f"Error formatting results: {str(e)}",
                "row_count": 0,
                "rows": [],
                "columns": [],
                "error": str(e)
            }
    
    def explain_query(self, sql_query: str) -> str:
        """Explain what a SQL query does"""
        try:
            if self.provider == "openai" and self.openai_client:
                return self._explain_query_openai(sql_query)
            elif self.provider == "bedrock" and self.bedrock_client:
                return self._explain_query_bedrock(sql_query)
            else:
                return f"SQL Query: {sql_query}\n\nThis query will execute against your Dremio data source."
                
        except Exception as e:
            return f"Error explaining query: {str(e)}"
    
    def _explain_query_openai(self, sql_query: str) -> str:
        """Explain query using OpenAI"""
        try:
            prompt = f"""Explain what this SQL query does in simple terms:

{sql_query}

Provide a clear, concise explanation of what this query will return."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI query explanation failed: {e}")
            return f"SQL Query: {sql_query}\n\nThis query will execute against your Dremio data source."
    
    def _explain_query_bedrock(self, sql_query: str) -> str:
        """Explain query using Bedrock"""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": f"Explain what this SQL query does in simple terms:\n\n{sql_query}\n\nProvide a clear, concise explanation of what this query will return."
                        }]
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model_id,
                accept="application/json",
                contentType="application/json",
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            
            # Extract text from response
            explanation = ""
            for content in result.get('content', []):
                if content.get('type') == 'text':
                    explanation += content.get('text', '')
            
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Bedrock query explanation failed: {e}")
            return f"SQL Query: {sql_query}\n\nThis query will execute against your Dremio data source."

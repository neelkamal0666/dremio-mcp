# 🚀 Enhanced Query Types - Complete Guide

## 🎯 **Overview**

The Flask API now supports **6 different query types** that intelligently handle various data exploration scenarios, including queries that don't need to return all columns. This provides efficient, targeted data access for different use cases.

## 📊 **Query Types**

### 1. **🔢 Count Queries**
**Purpose**: Get record counts without returning actual data
**Keywords**: "how many", "count", "total number"

**Examples**:
```json
{
  "question": "how many accounts are there"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "count_query",
  "data": {
    "rows": [{"total_count": 150}],
    "is_count_query": true,
    "count_value": 150,
    "message": "Total count: 150"
  }
}
```

### 2. **🧮 Aggregation Queries**
**Purpose**: Calculate statistics and aggregations
**Keywords**: "sum", "average", "maximum", "minimum", "statistics"

**Examples**:
```json
{
  "question": "what is the average age of users"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [{"avg_age": 32.5}],
    "aggregation_type": "AVG",
    "message": "Aggregation results for AVG"
  }
}
```

**Supported Aggregations**:
- **SUM**: "total revenue", "sum of amounts"
- **AVG**: "average age", "mean score"
- **MIN**: "minimum value", "lowest price"
- **MAX**: "maximum score", "highest amount"
- **STATS**: "statistics", "summary" (comprehensive stats)

### 3. **🎯 Field Selection Queries**
**Purpose**: Return only specific columns, not all data
**Keywords**: "only the", "just the", "specific fields"

**Examples**:
```json
{
  "question": "show me only the names and emails"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "field_selection_query",
  "data": {
    "rows": [
      {"name": "John Doe", "email": "john@example.com"},
      {"name": "Jane Smith", "email": "jane@example.com"}
    ],
    "selected_columns": ["name", "email"],
    "message": "Selected fields: name, email"
  }
}
```

**Supported Field Types**:
- **Names**: "names", "customer names"
- **Emails**: "emails", "email addresses"
- **IDs**: "IDs", "user IDs", "customer IDs"
- **Ages**: "ages", "age values"
- **Addresses**: "addresses", "locations"
- **Phones**: "phones", "mobile numbers"
- **Dates**: "dates", "created dates"
- **Amounts**: "amounts", "values", "prices"

### 4. **📋 Table Exploration**
**Purpose**: Discover available tables and data sources
**Keywords**: "show tables", "list data", "what tables"

**Examples**:
```json
{
  "question": "show me all tables"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": ["DataMesh.application.accounts", "DataMesh.application.users"],
    "total_count": 2,
    "message": "Found 2 tables matching your query"
  }
}
```

### 5. **📖 Metadata Requests**
**Purpose**: Get table structure and descriptions
**Keywords**: "describe", "structure", "explain", "metadata"

**Examples**:
```json
{
  "question": "describe the accounts table"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "metadata_request",
  "data": {
    "table_name": "DataMesh.application.accounts",
    "schema": [
      {"column_name": "id", "data_type": "INTEGER"},
      {"column_name": "name", "data_type": "VARCHAR"}
    ],
    "wiki_description": "# Accounts Table\nThis table contains...",
    "column_count": 5
  }
}
```

### 6. **📊 Data Queries**
**Purpose**: Return full data records (all columns)
**Keywords**: "show me", "get data", "sample", "examples"

**Examples**:
```json
{
  "question": "show me top 10 accounts"
}
```

**Response**:
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {"id": 1, "name": "John", "email": "john@example.com", "age": 30},
      {"id": 2, "name": "Jane", "email": "jane@example.com", "age": 25}
    ],
    "row_count": 2,
    "columns": ["id", "name", "email", "age"],
    "column_types": {"id": "int64", "name": "object", "email": "object", "age": "int64"}
  }
}
```

## 🎯 **Smart Query Detection**

The API automatically detects query intent using advanced pattern matching:

### **Pattern Recognition**:
- **Count**: "how many", "count", "total number"
- **Aggregation**: "sum", "average", "maximum", "statistics"
- **Field Selection**: "only the", "just the", "specific fields"
- **Table Exploration**: "show tables", "list data"
- **Metadata**: "describe", "structure", "explain"
- **Data**: "show me", "get data", "sample"

### **Intelligent Fallbacks**:
- If AI fails → Heuristic SQL generation
- If table not found → Suggest similar tables
- If columns not found → Show available columns
- If aggregation fails → Fallback to count

## 🚀 **Performance Benefits**

### **Efficient Data Transfer**:
- **Count Queries**: Only return numbers, not full records
- **Field Selection**: Only requested columns, not all data
- **Aggregations**: Single calculated values, not raw data
- **Metadata**: Structure info only, no data rows

### **Network Optimization**:
- **Reduced Payload**: Smaller JSON responses
- **Faster Queries**: Targeted SQL generation
- **Bandwidth Savings**: Only necessary data transferred
- **Mobile Friendly**: Lightweight responses

## 🧪 **Testing Enhanced Queries**

### **Run Examples**:
```bash
# Test all enhanced query types
python example_enhanced_queries.py

# Or using Make
make test-enhanced-queries
```

### **Manual Testing**:
```bash
# Count query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "how many accounts are there"}'

# Aggregation query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the average age"}'

# Field selection query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me only the names and emails"}'
```

## 📈 **Use Cases**

### **Business Intelligence**:
- **Dashboards**: Count queries for KPIs
- **Reports**: Aggregations for summaries
- **Analytics**: Field selection for specific metrics

### **Data Exploration**:
- **Discovery**: Table exploration for data catalog
- **Understanding**: Metadata requests for schema
- **Sampling**: Data queries for examples

### **Application Development**:
- **APIs**: Efficient data endpoints
- **Mobile Apps**: Lightweight responses
- **Web Apps**: Targeted data loading

## 🔧 **Configuration**

### **Environment Variables**:
```bash
# Enable enhanced query processing
ENHANCED_QUERIES=true

# Set default limits
DEFAULT_ROW_LIMIT=100
AGGREGATION_TIMEOUT=30
```

### **Custom Patterns**:
```python
# Add custom field patterns
CUSTOM_FIELD_PATTERNS = [
    r'\b(custom_field|special_field)\b'
]

# Add custom aggregation patterns
CUSTOM_AGGREGATION_PATTERNS = [
    r'\b(median|percentile)\b'
]
```

## 🎉 **Benefits**

### **For Users**:
- **Natural Language**: Ask questions naturally
- **Efficient Results**: Get only what you need
- **Fast Responses**: Optimized queries
- **Smart Suggestions**: Helpful error messages

### **For Developers**:
- **Flexible API**: Multiple query types
- **Easy Integration**: Simple HTTP endpoints
- **Rich Responses**: Structured JSON
- **Error Handling**: Comprehensive error codes

### **For Business**:
- **Cost Effective**: Reduced data transfer
- **Scalable**: Efficient resource usage
- **User Friendly**: Natural language interface
- **Powerful**: Advanced query capabilities

## 🚀 **Next Steps**

1. **Deploy**: Use the enhanced API in production
2. **Monitor**: Track query performance and usage
3. **Extend**: Add custom query patterns
4. **Optimize**: Fine-tune for your specific use cases

The enhanced Flask API now provides **intelligent, efficient data access** that adapts to your specific needs! 🎉

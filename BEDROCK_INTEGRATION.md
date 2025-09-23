# 🚀 AWS Bedrock Integration for MCP Server

## 🎯 **Enhanced MCP Server with AWS Bedrock Support**

The MCP server now supports **AWS Bedrock** as an alternative to OpenAI for SQL generation, providing enterprise-grade AI capabilities with better compliance and cost control.

## 🔧 **Key Features**

### **✅ AWS Bedrock Integration**
- **Enterprise AI**: Use AWS Bedrock for SQL generation
- **Model Flexibility**: Support for Claude, Llama, and other Bedrock models
- **Cost Control**: Pay-per-use pricing with AWS billing
- **Compliance**: Enterprise security and compliance features

### **✅ Provider Selection**
- **Automatic Detection**: Chooses Bedrock if configured, falls back to OpenAI
- **Environment-Based**: Configure via environment variables
- **Fallback Support**: Graceful degradation to heuristic SQL generation

### **✅ Supported Models**
- **Anthropic Claude**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Meta Llama**: `meta.llama-3-1-405b-instruct-v1:0`
- **Cohere Command**: `cohere.command-text-v14:0`

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Dremio Configuration (required)
DREMIO_HOST=your-dremio-host.com
DREMIO_USERNAME=your-username
DREMIO_PASSWORD=your-password

# Optional: OpenAI fallback
OPENAI_API_KEY=your-openai-api-key
```

### **AWS IAM Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
```

## 🚀 **Usage Examples**

### **Start MCP Server with Bedrock**
```bash
# Set environment variables
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# Start MCP server
python dremio_mcp_server_json.py

# Or using Make
make start-mcp-bedrock
```

### **Test Bedrock Integration**
```bash
# Test Bedrock integration
python test_bedrock_integration.py

# Or using Make
make test-bedrock
```

### **Direct Python Usage**
```python
#!/usr/bin/env python3
"""Direct Bedrock AI agent usage"""

import asyncio
from ai_agent_bedrock import DremioAIAgentBedrock
from dremio_client import DremioClient

async def main():
    # Initialize Dremio client
    client = DremioClient({
        'host': 'your-dremio-host.com',
        'username': 'your-username',
        'password': 'your-password',
        'verify_ssl': False
    })
    client.authenticate()
    
    # Initialize Bedrock AI agent
    ai_agent = DremioAIAgentBedrock(
        client,
        provider="bedrock",
        bedrock_model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    
    # Process natural language queries
    questions = [
        "show me all tables",
        "how many accounts are there",
        "what is the average age of users"
    ]
    
    for question in questions:
        print(f"🔍 Question: {question}")
        response = ai_agent.process_query(question)
        print(f"✅ Response: {response}")

asyncio.run(main())
```

## 📊 **JSON Response Examples**

### **Natural Language Query with Bedrock**
```json
{
  "success": true,
  "query_type": "natural_language_query",
  "data": {
    "question": "show me all tables",
    "response": "Found 5 tables:\n- DataMesh.application.accounts\n- DataMesh.application.users\n- DataMesh.application.projects",
    "message": "Natural language query processed with Bedrock"
  }
}
```

### **SQL Generation with Bedrock**
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [{"total": 150}],
    "row_count": 1,
    "columns": ["total"],
    "column_types": {"total": "int64"},
    "is_count_query": true,
    "message": "Found 1 rows"
  }
}
```

## 🔄 **Provider Selection Logic**

### **Priority Order:**
1. **AWS Bedrock** (if configured)
2. **OpenAI** (if Bedrock not available)
3. **Heuristic SQL** (if no AI available)

### **Configuration Detection:**
```python
# Bedrock configuration
if BEDROCK_MODEL_ID and AWS_REGION and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    # Use Bedrock
    ai_agent = DremioAIAgentBedrock(client, provider="bedrock")
elif OPENAI_API_KEY:
    # Use OpenAI
    ai_agent = DremioAIAgentBedrock(client, provider="openai")
else:
    # Use heuristic SQL generation
    ai_agent = None
```

## 🧪 **Testing**

### **Test Bedrock Integration**
```bash
# Test complete Bedrock integration
python test_bedrock_integration.py

# Test specific components
python -c "
from ai_agent_bedrock import DremioAIAgentBedrock
agent = DremioAIAgentBedrock(None, provider='bedrock')
print('✅ Bedrock AI agent created')
"
```

### **Test MCP Server with Bedrock**
```bash
# Start MCP server with Bedrock
python dremio_mcp_server_json.py

# Test natural language queries
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me all tables"}'
```

## 🎯 **Supported Bedrock Models**

### **Anthropic Claude Models**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Recommended)
- `anthropic.claude-3-5-haiku-20241022-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`

### **Meta Llama Models**
- `meta.llama-3-1-405b-instruct-v1:0`
- `meta.llama-3-1-70b-instruct-v1:0`

### **Cohere Models**
- `cohere.command-text-v14:0`
- `cohere.command-light-text-v14:0`

## 🔒 **Security & Compliance**

### **AWS Security Features**
- **IAM Integration**: Fine-grained access control
- **VPC Support**: Private network access
- **Encryption**: Data encryption in transit and at rest
- **Audit Logging**: CloudTrail integration

### **Enterprise Benefits**
- **Cost Control**: Pay-per-use pricing
- **Compliance**: SOC 2, HIPAA, GDPR support
- **Governance**: Centralized AI model management
- **Monitoring**: CloudWatch integration

## 🚀 **Benefits of Bedrock Integration**

### **1. Enterprise Features**
- **Compliance**: Built-in enterprise security
- **Cost Control**: Transparent AWS billing
- **Governance**: Centralized model management
- **Monitoring**: AWS CloudWatch integration

### **2. Model Flexibility**
- **Multiple Providers**: Claude, Llama, Cohere
- **Model Selection**: Choose best model for your use case
- **Version Control**: Pin to specific model versions
- **Performance**: Optimized for enterprise workloads

### **3. Integration Benefits**
- **AWS Ecosystem**: Native AWS integration
- **VPC Support**: Private network access
- **IAM Integration**: Existing AWS permissions
- **Cost Optimization**: Pay only for what you use

## 🎉 **Summary**

The enhanced MCP server now provides:

1. **✅ AWS Bedrock Integration** - Enterprise-grade AI capabilities
2. **✅ Model Flexibility** - Support for multiple AI models
3. **✅ Automatic Fallback** - Graceful degradation to OpenAI or heuristic
4. **✅ Enterprise Security** - IAM, VPC, and compliance features
5. **✅ Cost Control** - Transparent AWS billing

**Your MCP server now supports AWS Bedrock for enterprise-grade AI-powered SQL generation!** 🚀

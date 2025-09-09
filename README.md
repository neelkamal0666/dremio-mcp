# Dremio MCP Server and AI Agent

A comprehensive Model Context Protocol (MCP) server and AI agent for interacting with Dremio data using natural language queries. This project enables AI assistants like Claude or GPT to seamlessly access and analyze data stored in Dremio.

## Features

- **MCP Server**: Full MCP protocol implementation for Dremio integration
- **Natural Language Queries**: Ask questions about your data in plain English
- **Metadata Access**: Retrieve table schemas, descriptions, and wiki documentation
- **AI-Powered SQL Generation**: Convert natural language to SQL queries
- **Interactive CLI**: Command-line interface for testing and exploration
- **Comprehensive Data Access**: Query data, explore schemas, and get insights

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server     │    │     Dremio      │
│  (Claude/GPT)   │◄──►│  (dremio_mcp)    │◄──►│   Data Lake     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   AI Agent       │
                       │  (ai_agent.py)   │
                       └──────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Access to a Dremio instance
- (Optional) OpenAI API key for enhanced AI features

### Setup

1. **Clone or download this repository**
   ```bash
   cd /Users/neel/WebstormProjects/DremioMCP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your Dremio connection details:
   ```env
   DREMIO_HOST=your-dremio-host.com
   DREMIO_PORT=9047
   DREMIO_USERNAME=your-username
   DREMIO_PASSWORD=your-password
   DREMIO_USE_SSL=true
   
   # Optional: For enhanced AI features
   OPENAI_API_KEY=your-openai-api-key
   ```

## Usage

### 1. Test Connection

First, verify your Dremio connection:

```bash
python cli.py test-connection
```

### 2. Interactive AI Agent

Start an interactive session with the AI agent:

```bash
python cli.py interactive
```

Example interactions:
```
Dremio AI> Show me all tables in the sales schema
Dremio AI> What is the schema of customer_data table?
Dremio AI> How many records are in the orders table?
Dremio AI> Show me the first 10 rows from products table
```

### 3. Direct SQL Queries

Execute SQL queries directly:

```bash
python cli.py query --query "SELECT * FROM sales.customers LIMIT 10"
```

### 4. Start MCP Server

Run the MCP server for integration with AI assistants:

```bash
python cli.py start-server
```

## MCP Server Tools

The MCP server provides the following tools:

### `query_dremio`
Execute SQL queries against Dremio data sources.

**Parameters:**
- `query` (required): SQL query to execute
- `limit` (optional): Maximum number of rows to return (default: 1000)

**Example:**
```json
{
  "query": "SELECT customer_id, name, email FROM sales.customers WHERE region = 'North America'",
  "limit": 100
}
```

### `get_table_schema`
Get schema information for a specific table.

**Parameters:**
- `table_path` (required): Full path to the table (e.g., 'source.schema.table')

**Example:**
```json
{
  "table_path": "sales.customers"
}
```

### `list_tables`
List all available tables in Dremio.

**Parameters:**
- `source` (optional): Source name to filter tables
- `schema` (optional): Schema name to filter tables

**Example:**
```json
{
  "source": "sales"
}
```

### `get_table_metadata`
Get comprehensive metadata for a table including wiki descriptions.

**Parameters:**
- `table_path` (required): Full path to the table

**Example:**
```json
{
  "table_path": "sales.customers"
}
```

### `search_tables`
Search for tables by name or description.

**Parameters:**
- `search_term` (required): Search term to find tables

**Example:**
```json
{
  "search_term": "customer"
}
```

### `get_data_sample`
Get a sample of data from a table for exploration.

**Parameters:**
- `table_path` (required): Full path to the table
- `limit` (optional): Number of rows to return (default: 10)

**Example:**
```json
{
  "table_path": "sales.customers",
  "limit": 5
}
```

## Integration with AI Assistants

### Claude Desktop Integration

1. **Configure Claude Desktop** to use the MCP server by adding to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "dremio": {
      "command": "python",
      "args": ["/Users/neel/WebstormProjects/DremioMCP/dremio_mcp_server.py"],
      "env": {
        "DREMIO_HOST": "your-dremio-host.com",
        "DREMIO_USERNAME": "your-username",
        "DREMIO_PASSWORD": "your-password"
      }
    }
  }
}
```

2. **Restart Claude Desktop** and you'll have access to Dremio tools.

### GPT Integration

For GPT integration, you can use the MCP server through the OpenAI API or run the interactive CLI.

## Natural Language Query Examples

The AI agent can understand various types of queries:

### Data Exploration
- "Show me all tables in the sales schema"
- "What tables contain customer information?"
- "List all available data sources"

### Schema Information
- "What is the schema of the customers table?"
- "What columns are in the orders table?"
- "Show me the data types for the products table"

### Data Queries
- "How many customers do we have?"
- "Show me the top 10 products by sales"
- "What is the average order value?"
- "Find all customers from North America"

### Metadata and Documentation
- "Tell me about the customer_data table"
- "What is the description of the sales schema?"
- "Show me the wiki documentation for the orders table"

## Advanced Features

### AI-Powered SQL Generation

When OpenAI API key is configured, the agent can:
- Convert complex natural language queries to SQL
- Suggest query optimizations
- Explain SQL queries in natural language
- Provide data insights and analysis

### Metadata Caching

The system caches metadata to improve performance:
- Table schemas are cached after first access
- Wiki descriptions are retrieved and stored
- Connection pooling for better performance

### Error Handling

Comprehensive error handling includes:
- Connection retry logic
- SQL error explanations
- Graceful fallbacks for missing features
- Helpful suggestions for common issues

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DREMIO_HOST` | Dremio server hostname | localhost |
| `DREMIO_PORT` | Dremio server port | 9047 |
| `DREMIO_USERNAME` | Dremio username | - |
| `DREMIO_PASSWORD` | Dremio password | - |
| `DREMIO_USE_SSL` | Use SSL connection | true |
| `DREMIO_CLIENT_ID` | OAuth client ID (optional) | - |
| `DREMIO_CLIENT_SECRET` | OAuth client secret (optional) | - |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

### Authentication Methods

1. **Basic Authentication**: Username and password
2. **OAuth2**: Client credentials flow (if configured)

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify Dremio host and port
   - Check network connectivity
   - Ensure credentials are correct

2. **Authentication Error**
   - Verify username and password
   - Check if account has necessary permissions
   - Try OAuth if basic auth fails

3. **Query Errors**
   - Check table names and paths
   - Verify SQL syntax
   - Ensure user has query permissions

4. **MCP Server Issues**
   - Check Python dependencies
   - Verify environment variables
   - Review server logs

### Debug Mode

Enable debug logging by setting:
```bash
export PYTHONPATH=/Users/neel/WebstormProjects/DremioMCP
export LOG_LEVEL=DEBUG
```

## Development

### Project Structure

```
DremioMCP/
├── dremio_mcp_server.py    # Main MCP server implementation
├── dremio_client.py        # Dremio client with REST API and Flight SQL
├── ai_agent.py            # AI agent for natural language processing
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── env.example           # Environment configuration template
└── README.md             # This file
```

### Adding New Tools

To add new MCP tools:

1. Add tool definition in `handle_list_tools()`
2. Implement handler in `handle_call_tool()`
3. Add corresponding method in `DremioClient`
4. Update documentation

### Testing

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub
4. Contact the development team

## Roadmap

- [ ] Enhanced wiki integration
- [ ] Query optimization suggestions
- [ ] Data visualization support
- [ ] Multi-tenant support
- [ ] Advanced caching strategies
- [ ] Query history and favorites
- [ ] Export functionality
- [ ] Real-time data streaming

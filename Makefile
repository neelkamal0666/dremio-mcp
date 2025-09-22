# Dremio MCP Server Makefile

.PHONY: help install setup test clean run-server run-interactive run-example

help: ## Show this help message
	@echo "Dremio MCP Server and AI Agent"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

setup: ## Run initial setup
	python setup.py

test: ## Run test suite
	python test_setup.py

test-anthropic: ## Test Anthropic Claude integration
	python test_anthropic.py

test-intent: ## Test intent analysis
	python test_intent.py

test-queries: ## Test query processing
	python test_queries.py

test-wiki: ## Test wiki metadata functionality
	python test_wiki.py

test-sql: ## Test SQL generation fixes
	python test_sql_generation.py

test-table-matching: ## Test table name matching fixes
	python test_table_matching.py

test-mcp-wiki: ## Test MCP server wiki functionality
	python test_mcp_wiki.py

test-entity-id: ## Test entity ID resolution for DataMesh tables
	python test_entity_id.py

test-connection: ## Test Dremio connection
	python cli.py test-connection

run-server: ## Start MCP server
	python cli.py start-server

run-interactive: ## Start interactive AI agent
	python cli.py interactive

run-example: ## Run example usage script
	python example_usage.py

query: ## Run a SQL query (usage: make query QUERY="SELECT * FROM table LIMIT 10")
	python cli.py query --query "$(QUERY)"

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete

format: ## Format code with black
	black *.py

lint: ## Run linting
	flake8 *.py

check-deps: ## Check for outdated dependencies
	pip list --outdated

update-deps: ## Update dependencies
	pip install --upgrade -r requirements.txt

# Development commands
dev-install: ## Install development dependencies
	pip install -r requirements.txt
	pip install black flake8 pytest

dev-test: ## Run development tests
	pytest tests/ -v

# Docker commands (if needed)
docker-build: ## Build Docker image
	docker build -t dremio-mcp-server .

docker-run: ## Run in Docker container
	docker run -it --env-file .env dremio-mcp-server

# Documentation
docs: ## Generate documentation
	@echo "Documentation is available in README.md"
	@echo "For API documentation, run: python -c 'import dremio_client; help(dremio_client.DremioClient)'"

# Quick start
quick-start: install setup test ## Quick start: install, setup, and test
	@echo "Quick start completed!"
	@echo "Next: make run-interactive"

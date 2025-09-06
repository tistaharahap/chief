# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
source .venv/bin/activate
```

### Required Environment Variables
```bash
# OpenRouter API key (required) - Get from https://openrouter.ai/keys
export OPENROUTER_API_KEY="your-openrouter-api-key-here"

# Tavily API key (required for web search) - Get from https://tavily.com
export TAVILY_API_KEY="your-tavily-api-key-here"
```

Or set them in the `.env` file:
```env
OPENROUTER_API_KEY=your-openrouter-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

### Code Quality
```bash
# Lint and fix issues
ruff check . --fix

# Format code
ruff format .

# Check for remaining issues
ruff check .
```

### Testing
```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=src
```

### Running Applications
```bash
python src/appclis/chief.py --help
python src/appclis/chen.py --help
```

### Running Commands

Always run commands with `rye run` if you want to access the virtual environment and dependencies.

## Architecture Overview

This project implements AI agents using the Pydantic AI framework with two main CLI applications: `chief` and `chen`.

### Core Structure
- **src/appclis/**: CLI entry points using Typer framework
- **src/libagentic/**: Core agent library with tools, providers, and MongoDB integration
- **src/libshared/**: Shared utilities, particularly MongoDB base classes

### Agent Architecture
The project uses a factory pattern for agent creation:
- `get_chief_agent()` and `get_chen_agent()` functions in `libagentic/agents.py`
- Agents are configured with system prompts from `libagentic/prompts.py`
- **Model Provider**: Uses OpenRouter for access to multiple LLM providers (Anthropic, OpenAI, etc.)
- Provider configuration in `libagentic/providers.py` with OpenAI-compatible OpenRouter integration
- Tools system provides web search (Tavily API) and datetime utilities
- MongoDB persistence through Beanie ODM with async support

### Model Configuration
- **Default Model**: `anthropic/claude-3.5-sonnet` via OpenRouter
- **Provider**: OpenRouter (https://openrouter.ai) for multi-provider access
- **API Key**: Set `OPENROUTER_API_KEY` in `.env` file
- **Available Models**: All OpenRouter-supported models (Anthropic, OpenAI, Google, etc.)

### Known Issues

**Critical Circular Import**: 
```
libagentic.agents → libagentic.tools.search → libagentic.agents (TavilyDeps)
```
This prevents the CLI applications from starting. The `TavilyDeps` class should be moved to a separate module (e.g., `libagentic.types` or `libagentic.deps`).

## Configuration Details

### Code Style (Ruff)
- Line length: 120 characters
- Double quotes for strings
- Absolute imports only (relative imports banned)
- Python 3.13 target, 3.8+ compatibility

### Dependencies
- **Pydantic AI**: Core agent framework with Logfire integration
- **Typer**: CLI framework
- **Beanie**: Async MongoDB ODM  
- **Tavily**: Web search API client
- **Asyncer**: Async utilities

### Project Scripts
Defined in `pyproject.toml`:
- `chief = "appclis.chief:app"`
- `chen = "appclis.chen:app"`

## Development Notes

### Async Patterns
The entire codebase uses async/await patterns. CLI applications wrap async functions with `asyncio.run()`.

### Import Organization
First-party packages are: `["apppublicapi", "libagentic", "libshared"]`

### MongoDB Integration
Uses Beanie ODM with base classes in `libshared/mongo.py` providing common document patterns and slug mixins.
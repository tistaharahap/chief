# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
source .venv/bin/activate
```

### Chen Configuration

Chen uses JSON-based configuration stored in `~/.chen/settings.json`. On first run, Chen will automatically launch an interactive onboarding process to collect your API keys and preferences.

#### Interactive Setup (Recommended)
```bash
# First time running Chen triggers automatic onboarding
rye run chen
# OR manually trigger onboarding
rye run chen onboard
```

#### Manual Configuration
```bash
# Set individual configuration values
rye run chen config set anthropic_api_key "sk-ant-..."
rye run chen config set openai_api_key "sk-..."
rye run chen config set openrouter_api_key "sk-or-..."
rye run chen config set tavily_api_key "tvly-..."
rye run chen config set context_window 150000

# View all settings
rye run chen config

# Get specific setting
rye run chen config get anthropic_api_key

# Reset all settings (triggers onboarding on next run)
rye run chen reset
```

#### Configuration File Structure
Settings are stored in `~/.chen/settings.json`:
```json
{
  "anthropic_api_key": "sk-ant-...",
  "openai_api_key": "sk-...",
  "openrouter_api_key": "sk-or-...",
  "tavily_api_key": "tvly-...",
  "context_window": 200000
}
```

#### Environment Variables (Optional)
Environment variables can be used as defaults during onboarding:
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key" 
export OPENROUTER_API_KEY="your-openrouter-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

Or set them in the `.env` file:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
TAVILY_API_KEY=your-tavily-api-key
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
rye run chief --help
rye run chen --help
```

#### Chen CLI Commands
```bash
# Start Chen chat interface
rye run chen

# Configuration management
rye run chen config              # Show all settings
rye run chen config list         # Same as above
rye run chen config get <key>    # Get specific setting
rye run chen config set <key> <value>  # Set specific setting

# Setup and maintenance
rye run chen onboard            # Run interactive setup
rye run chen reset              # Reset all settings
```

### Running Commands

Always run commands with `rye run` if you want to access the virtual environment and dependencies.

## Architecture Overview

This project implements AI agents using the Pydantic AI framework with two main CLI applications: `chief` and `chen`.

### Core Structure
- **src/appclis/**: CLI entry points using Typer framework
  - **settings/**: Chen configuration management system with Pydantic models
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
- **API Key Configuration**: Interactive onboarding or `chen config set` commands
- **Available Models**: All OpenRouter-supported models (Anthropic, OpenAI, Google, etc.)
- **Supported Providers**: Anthropic (primary), OpenAI, OpenRouter, Tavily (web search)

## Configuration Details

### Code Style (Ruff)
- Line length: 120 characters
- Double quotes for strings
- Absolute imports only (relative imports banned)
- Python 3.13 target, 3.8+ compatibility

### Dependencies
- **Pydantic AI**: Core agent framework with Logfire integration
- **Pydantic Settings**: Configuration management with validation
- **Typer**: CLI framework with command groups
- **Rich**: Terminal formatting and interactive prompts
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

### Chen Settings Architecture
Chen implements a sophisticated configuration system:

#### Settings Module (`src/appclis/settings/`)
- **`chen_settings.py`**: Pydantic BaseSettings model with validation
  - Supports 4 API providers with field validation
  - Configurable context window (default: 200,000 tokens)
  - Requires at least one API key for operation
- **`settings_manager.py`**: Core settings management class
  - JSON file operations with `~/.chen/settings.json`
  - Interactive onboarding with environment variable defaults
  - Individual setting get/set operations with type conversion
  - API key masking for security
- **`__init__.py`**: Module exports for clean imports

#### Key Features
- **Automatic Onboarding**: Triggered on first run or when settings are missing
- **Environment Variable Integration**: Uses existing env vars as onboarding defaults
- **Type Safety**: Pydantic validation with proper error handling
- **Security**: API key masking in CLI display and error messages
- **Backwards Compatibility**: Still loads `.env` files as fallback defaults
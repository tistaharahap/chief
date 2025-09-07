# Chief & Chen AI Agents

A sophisticated AI agent framework built with Pydantic AI, featuring two main applications: **Chief** and **Chen**. Both agents provide conversational AI interfaces with web search capabilities and configurable model providers.

**Chen** has been written as an AI psychologist with an extensive software engineering background. You can think of her like [Wendy Rhoades](https://www.charactour.com/hub/characters/view/Wendy-Rhoades.Billions) that is always on your side.

On the other hand, **Chief** is a barebone agent with a barebone system prompt. Chief provides an entry point if you want to write your own agents using the same patterns that Chen uses.

## Features

- **Dual Agent System**: Chief and Chen applications with distinct personalities and capabilities
- **Multi-Provider Support**: Anthropic, OpenAI, and OpenRouter integration
- **Web Search Integration**: Powered by Tavily API for real-time information
- **Smart Configuration**: Interactive onboarding with JSON-based settings management
- **MongoDB Persistence**: ~~Async document storage with Beanie ODM~~ Not implemented yet
- **Rich CLI Interface**: Beautiful terminal UI with Typer and Rich
- **MCP Support**: Coming soon

## Quick Start

### Installation

```bash
# Clone and setup
git clone git@github.com:tistaharahap/chief-ai.git
cd chief
source .venv/bin/activate

# Install dependencies
rye sync
```

### First Run (Chen)

```bash
# Launch Chen with automatic onboarding
rye run chen
```

Chen will guide you through interactive setup to configure your API keys and preferences.

### First Run (Chief)

```bash
# Launch Chief
rye run chief
```

## LLM Providers & Models Priority

In [src/libagentic/providers.py](src/libagentic/providers.py), it is clear that the first choice is Anthropic's Claude 4 Sonnet.

If the `anthropic_api_key` in `~/.chen/settings.json` is set, Claude 4 Sonnet will be the first choice. When all providers are set, the fallback becomes:

1. `claude-sonnet-4-20250514` via Anthropic
2. `gpt-5` via OpenAI
3. `deepseek/deepseek-chat-v3.1:free` via OpenRouter

To use free models, simply set the OpenRouter API key and leave the others unset.

## Configuration

### Chen Configuration System

Chen uses a sophisticated JSON-based configuration system with interactive onboarding:

```bash
# View current settings
rye run chen config

# Set individual values
rye run chen config set anthropic_api_key "sk-ant-..."
rye run chen config set context_window 150000

# Manual onboarding
rye run chen onboard

# Reset all settings
rye run chen reset
```

Settings are stored in `~/.chen/settings.json` with support for:
- Anthropic, OpenAI, OpenRouter, and Tavily API keys
- Configurable context window size
- Automatic validation and type conversion

### Environment Variables (Optional)

Environment variables serve as defaults during onboarding:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"
export TAVILY_API_KEY="your-key-here"
```

## Architecture

### Core Structure

```
src/
├── appclis/              # CLI applications
│   ├── chen.py          # Chen agent with config system
│   ├── chief.py         # Chief agent
│   └── settings/        # Configuration management
├── libagentic/          # Core agent framework
│   ├── agents.py        # Agent factory functions
│   ├── providers.py     # Model provider configs
│   ├── prompts.py       # System prompts
│   └── tools/           # Agent tools and capabilities
└── libshared/           # Shared utilities
    └── mongo.py         # MongoDB base classes
```

### Technology Stack

- **Pydantic AI**: Core agent framework with Logfire integration
- **Typer + Rich**: Beautiful CLI interfaces with command groups
- **Pydantic Settings**: Type-safe configuration management
- **Beanie**: Async MongoDB ODM for persistence
- **Tavily**: Web search API integration
- **OpenRouter**: Multi-provider LLM access

## Development

### Code Quality

```bash
# Lint and format
ruff check . --fix
ruff format .

# Type checking and final lint
ruff check .
```

### Testing

```bash
# Run tests (when implemented)
pytest

# With coverage
pytest --cov=src
```

## Model Providers

- **Default**: `deepseek/deepseek-chat-v3.1:free` via OpenRouter, `gpt-5` via OpenAI and `claude-sonnet-4-20250514` via Anthropic
- **Supported**: All Anthropic, OpenAI, and OpenRouter models
- **Configuration**: Interactive setup or individual config commands
- **Fallbacks**: Automatic provider selection based on availability

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please open issues or pull requests for enhancements and bug fixes.

# Chief & Chen AI Agents

A sophisticated AI agent framework built with Pydantic AI, featuring two main applications: **Chief** and **Chen**. Both agents provide conversational AI interfaces with web search capabilities and configurable model providers.

**Chen** has been written as an AI psychologist with an extensive software engineering background. You can think of her like [Wendy Rhoades](https://www.charactour.com/hub/characters/view/Wendy-Rhoades.Billions) that is always on your side.

On the other hand, **Chief** is a barebone agent with a barebone system prompt. Chief provides an entry point if you want to write your own agents using the same patterns that Chen uses.

Fork the repository and customize **Chief** however you want!

## Features

- **Dual Agent System**: Chief and Chen applications with distinct personalities and capabilities
- **Multi-Provider Support**: Anthropic, OpenAI, and OpenRouter integration
- **Web Search Integration**: Powered by Tavily API for real-time information
- **Smart Configuration**: Interactive onboarding with JSON-based settings management
- **MongoDB Persistence**: ~~Async document storage with Beanie ODM~~ Not implemented yet
- **Rich CLI Interface**: Beautiful terminal UI with Typer and Rich
- **MCP Support**: Coming soon

## Quick Start

### Easy Installation (Recommended)

Install with a convenience script that creates convenient `chen` and `chief` commands:

```bash
curl -sSL https://raw.githubusercontent.com/tistaharahap/chief-ai/main/install.sh | bash
```

After installation, you can run:

```bash
chen --help    # Chen AI psychologist
chief --help   # Basic AI agent
chen           # Start Chen (triggers onboarding on first run)
```

### Manual Installation

Alternatively, run directly with uvx:

```bash
# Run Chen directly
uvx --python 3.13 --from chief-ai chen --help

# Go straight to onboarding
uvx --python 3.13 --from chief-ai chen
```

### Installation (for development)

```bash
# Clone and setup
git clone git@github.com:tistaharahap/chief-ai.git
cd chief-ai
source .venv/bin/activate

# Install dependencies
rye sync
```

## LLM Providers & Models Priority

In [src/libagentic/providers.py](src/libagentic/providers.py), it is clear that the first choice is Anthropic's Claude 4 Sonnet.

If the `anthropic_api_key` in `~/.chen/settings.json` is set, Claude 4 Sonnet will be the first choice. When all providers are set, the fallback becomes:

1. `claude-sonnet-4-20250514` via Anthropic
2. `gpt-5` via OpenAI
3. `deepseek/deepseek-chat-v3.1:free` via OpenRouter

To use free models, simply set the OpenRouter API key and leave the others unset.

## Chen

Chen has its settings defined in `~/.chen/settings.json` that looks like this:

```json
{
  "anthropic_api_key": "sk-ant-...",
  "openai_api_key": "sk-...",
  "openrouter_api_key": "sk-or-...",
  "tavily_api_key": "tvly_...",
  "context_window": 200000
}
```

### Settings Explained

Each of these settings items are going to be prompted during onboarding if not set. Here are some commands with regards to settings:

```bash
chen config                             # View all settings
chen config get anthropic_api_key       # Get specific setting, follows the JSON keys
chen config set context_window 150000   # Set specific setting
```

### Sessions

You can also find your chat history in `~/.chen/sessions/` with each session as a subdirectory there. A typical session directory might look like this:

```bash
ls -la ~/.chen/sessions/
total 0
drwxr-xr-x@ 14 tista  staff  448 Sep  7 23:07 .
drwxr-xr-x@  5 tista  staff  160 Sep  7 22:05 ..
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:01 068bdba6-1b51-7fd5-8000-b37d1f0832ea
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:02 068bdbab-2071-7c75-8000-2cb9c8158015
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:04 068bdbb2-163e-7553-8000-e3ce5a060b30
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:04 068bdbb3-bbca-76b9-8000-498755d91316
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:05 068bdbb5-702c-7e57-8000-317c40048963
drwxr-xr-x@  4 tista  staff  128 Sep  7 21:09 068bdbc3-cff6-7ea4-8000-62576dfa2d1f
```

Session subdirectories are named with UUID v7 which are chronologically sorted. Within each session, you will find these files:

```bash
ls -la ~/.chen/sessions/068bdba6-1b51-7fd5-8000-b37d1f0832ea 
total 160
drwxr-xr-x@  4 tista  staff    128 Sep  7 21:01 .
drwxr-xr-x@ 14 tista  staff    448 Sep  7 23:07 ..
-rw-r--r--@  1 tista  staff  74545 Sep  7 21:01 history.jsonl
-rw-r--r--@  1 tista  staff    327 Sep  7 21:01 metadata.json
```

The `history.jsonl` file contains the full conversation history in JSON Lines format, while `metadata.json` holds session metadata.

### In-chat Commands

While in a chat session with Chen, you can use the following commands:

```
/quit       # Exit the chat session
/exit       # Exit the chat session
Ctrl+D      # Exit the chat session
Ctrl+C      # Exit the chat session supposedly but you have to press it twice, got some exception bubbling not right yet
/resume     # Resume a previous session, you will be shown a list of sessions to choose from
```

## Development

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

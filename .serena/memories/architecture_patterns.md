# Architecture and Design Patterns

## Project Structure
```
chief/
├── src/
│   ├── appclis/          # CLI entry points
│   │   ├── chief.py      # Main agent CLI
│   │   └── chen.py       # Secondary agent CLI
│   ├── libagentic/       # Core agent library
│   │   ├── agents.py     # Agent definitions and factory functions
│   │   ├── prompts.py    # System prompts (CHIEF_SYSTEM_PROMPT, CHEN_SYSTEM_PROMPT)
│   │   ├── mongo.py      # MongoDB models with Beanie
│   │   └── tools/        # Agent tools
│   │       ├── search.py # Web search via Tavily API
│   │       └── time.py   # Current datetime utilities
│   └── libshared/        # Shared utilities
│       └── mongo.py      # Base MongoDB document classes
├── .venv/                # Virtual environment
├── pyproject.toml        # Project configuration
├── ruff.toml            # Code quality configuration
└── requirements*.lock    # Locked dependencies
```

## Design Patterns

### Agent Pattern
- **Factory Functions**: `get_chief_agent()`, `get_chen_agent()`
- **Dependency Injection**: `TavilyDeps` dataclass for external services
- **Tool Integration**: Modular tools system with `web_search`, `current_datetime`

### CLI Pattern  
- **Typer Framework**: Modern CLI with automatic help generation
- **Async CLI**: `asyncio.run()` wrapper for async agent operations
- **Exception Handling**: `contextlib.suppress()` for clean exits

### Data Persistence
- **MongoDB + Beanie**: Async ODM for document storage
- **Base Classes**: `BaseMongoDocument`, `SlugMixin` for common patterns
- **Type Safety**: Pydantic models with field validation

### Configuration Management
- **Pydantic Settings**: Environment-based configuration
- **Dependency Management**: Locked requirements for reproducibility
- **Build System**: Modern Hatchling with package specifications

## Current Issues

### Circular Import Problem
```
libagentic.agents → libagentic.tools.search → libagentic.agents (TavilyDeps)
```

**Recommended Fix**: Move `TavilyDeps` to a separate module (e.g., `libagentic.types` or `libagentic.deps`)

## Best Practices Observed
- **Async/Await**: Consistent async patterns throughout
- **Type Hints**: Modern Python typing with `typing_extensions`
- **Error Handling**: Graceful exception handling in CLI
- **Separation of Concerns**: Clear module boundaries
- **Documentation**: Type annotations and docstrings (in prompts.py)

## Integration Points
- **Pydantic AI**: Core agent framework
- **Tavily API**: Web search capabilities  
- **MongoDB**: Data persistence layer
- **Logfire**: Observability and monitoring
- **Typer**: CLI interface framework
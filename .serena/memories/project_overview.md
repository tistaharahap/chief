# Chief Project Overview

## Purpose
Chief is a Python project implementing AI agents using Pydantic AI framework. The project contains two main CLI applications:
- **chief**: Main agent CLI interface
- **chen**: Secondary agent CLI interface

Both agents are built on top of the Pydantic AI framework with integrated tools for web search and time operations.

## Key Features
- AI agent system using Pydantic AI
- Web search capabilities via Tavily API
- MongoDB integration with Beanie ODM
- CLI interfaces built with Typer
- Observability with Logfire
- Async/await support throughout

## Current Status
- Project is in early development (v0.1.0)
- Contains circular import issue between `libagentic.agents` and `libagentic.tools.search`
- No test suite implemented yet
- Basic structure established with modular architecture

## Author
Batista Harahap (batista@bango29.com)
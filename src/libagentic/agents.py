from typing import Annotated

from pydantic_ai import Agent, ModelSettings, Tool
from pydantic_ai.mcp import MCPServer
from typing_extensions import Doc

from libagentic.models import TavilyDeps
from libagentic.prompts import CHEN_SYSTEM_PROMPT, CHIEF_SYSTEM_PROMPT, TITLE_GENERATION_SYSTEM_PROMPT
from libagentic.providers import get_default_model
from libagentic.tools.search import web_search
from libagentic.tools.time import current_datetime


def get_chief_agent(
    mcps: Annotated[list[MCPServer], Doc("""List of MCP servers to connect the agent to""")] = None,
    temperature: Annotated[
        float, Doc("""The temperature to use for the model, the lower it is, the less adventurous the model will be""")
    ] = 0.2,
) -> Agent:
    """
    Returns the chief agent using OpenRouter for model access.

    Args:
        mcps (list[MCPServer] | None, optional): List of MCP servers to connect the agent to. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.2.

    Returns:
        Agent: The chief agent
    """
    settings = ModelSettings(temperature=temperature)
    fallback_model = get_default_model()

    return Agent(
        fallback_model,
        name="Chief",
        system_prompt=CHIEF_SYSTEM_PROMPT,
        mcp_servers=mcps,
        model_settings=settings,
    )


def get_chen_agent(
    mcps: Annotated[list[MCPServer], Doc("""List of MCP servers to connect the agent to""")] = None,
    temperature: Annotated[
        float, Doc("""The temperature to use for the model, the lower it is, the less adventurous the model will be""")
    ] = 0.2,
) -> Agent:
    """
    Returns the Chen agent using OpenRouter for model access. Web search is enabled by default using the Tavily tool.

    Args:
        mcps (list[MCPServer] | None, optional): List of MCP servers to connect the agent to. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.2.

    Returns:
        Agent: The Chen agent
    """
    settings = ModelSettings(temperature=temperature)
    fallback_model = get_default_model()

    return Agent(
        fallback_model,
        name="Chen",
        system_prompt=CHEN_SYSTEM_PROMPT,
        mcp_servers=mcps,
        model_settings=settings,
        deps_type=TavilyDeps,
        tools=[
            Tool(web_search, takes_ctx=True),
            current_datetime,
        ],
    )


def get_title_agent(
    anthropic_model_name: str = "claude-3-5-haiku-latest",
    openai_model_name: str = "gpt-4o",
    temperature: float = 0.1,
) -> Agent:
    """
    Returns a lightweight agent specifically for generating chat session titles.

    Uses a low temperature for consistent, focused title generation and a fast model
    (Haiku) for quick response times.

    Args:
        anthropic_model_name: The Anthropic model identifier for title generation
        openai_model_name: The OpenAI model identifier for title generation
        temperature: Low temperature for consistent titles. Defaults to 0.1.

    Returns:
        Agent: The title generation agent
    """
    settings = ModelSettings(temperature=temperature)
    # Use a lightweight model configuration optimized for title generation
    title_model = get_default_model(
        anthropic_model_name=anthropic_model_name,
        openai_model_name=openai_model_name,
        openrouter_model_name="deepseek/deepseek-chat-v3.1:free",  # Keep fallback
    )

    return Agent(
        title_model,
        name="TitleGenerator",
        system_prompt=TITLE_GENERATION_SYSTEM_PROMPT,
        model_settings=settings,
    )


def get_compression_agent() -> Agent:
    """
    Returns a lightweight agent specifically for compressing conversation history.

    Uses the fallback model configuration with low temperature for consistent compression
    that preserves meaning and nuances while reducing token count.

    Returns:
        Agent: The context compression agent
    """
    compression_prompt = """You are a context compression specialist. Your task is to compress conversation history while:

PRIORITY 1: Preserve meaning over token reduction - never sacrifice understanding for brevity
PRIORITY 2: Capture nuances and subtleties - small details often matter most for continuity
PRIORITY 3: Maintain key points and decisions - but subordinate to priorities 1 & 2

Compress the following conversation history into a coherent summary that preserves:
- Technical decisions and their reasoning
- User preferences and established patterns
- Unresolved issues or pending tasks
- Context needed for future messages
- Subtle implications and nuanced understanding

Output a flowing narrative that reads as natural context, not bullet points."""

    settings = ModelSettings(temperature=0.1)  # Consistent compression
    fallback_model = get_default_model()

    return Agent(
        fallback_model,
        name="ContextCompressor",
        system_prompt=compression_prompt,
        model_settings=settings,
    )

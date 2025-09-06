from typing import Annotated

from pydantic_ai import Agent, ModelSettings, Tool
from pydantic_ai.mcp import MCPServer
from typing_extensions import Doc

from libagentic.models import TavilyDeps
from libagentic.prompts import CHEN_SYSTEM_PROMPT, CHIEF_SYSTEM_PROMPT
from libagentic.providers import get_default_model
from libagentic.tools.search import web_search
from libagentic.tools.time import current_datetime


def get_chief_agent(
    model: Annotated[
        str | None, Doc("""The OpenRouter model to use (e.g. 'anthropic/claude-3.5-sonnet', 'openai/gpt-4o')""")
    ] = None,
    mcps: Annotated[list[MCPServer], Doc("""List of MCP servers to connect the agent to""")] = None,
    temperature: Annotated[
        float, Doc("""The temperature to use for the model, the lower it is, the less adventurous the model will be""")
    ] = 0.2,
) -> Agent:
    """
    Returns the chief agent using OpenRouter for model access.

    Args:
        model (str, optional): The OpenRouter model to use. Defaults to "anthropic/claude-3.5-sonnet".
        mcps (list[MCPServer] | None, optional): List of MCP servers to connect the agent to. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.2.

    Returns:
        Agent: The chief agent
    """
    settings = ModelSettings(temperature=temperature)
    openrouter_model = get_default_model(model)

    return Agent(
        openrouter_model,
        name="Chief",
        system_prompt=CHIEF_SYSTEM_PROMPT,
        mcp_servers=mcps,
        model_settings=settings,
    )


def get_chen_agent(
    model: Annotated[
        str | None, Doc("""The OpenRouter model to use (e.g. 'anthropic/claude-3.5-sonnet', 'openai/gpt-4o')""")
    ] = None,
    mcps: Annotated[list[MCPServer], Doc("""List of MCP servers to connect the agent to""")] = None,
    temperature: Annotated[
        float, Doc("""The temperature to use for the model, the lower it is, the less adventurous the model will be""")
    ] = 0.2,
) -> Agent:
    """
    Returns the Chen agent using OpenRouter for model access. Web search is enabled by default using the Tavily tool.

    Args:
        model (str, optional): The OpenRouter model to use. Defaults to "anthropic/claude-3.5-sonnet".
        mcps (list[MCPServer] | None, optional): List of MCP servers to connect the agent to. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.2.

    Returns:
        Agent: The Chen agent
    """
    settings = ModelSettings(temperature=temperature)
    openrouter_model = get_default_model(model)

    return Agent(
        openrouter_model,
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

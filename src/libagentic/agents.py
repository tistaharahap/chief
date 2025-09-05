from typing import Annotated

from pydantic_ai import Agent, ModelSettings
from pydantic_ai.mcp import MCPServer
from typing_extensions import Doc

from libagentic.prompts import CHIEF_SYSTEM_PROMPT


def get_chief_agent(
    model: Annotated[str | None, Doc(
        """The model to use, must be known to Pydantic AI"""
    )] = "anthropic:claude-4-sonnet-20250514",
    mcps: Annotated[list[MCPServer], Doc(
        """List of MCP servers to connect the agent to"""
    )] = None,
    temperature: Annotated[float, Doc(
        """The temperature to use for the model, the lower it is, the less adventurous the model will be"""
    )] = 0.2,
) -> Agent:
    """
    Returns the chief agent, the entry point

    Args:
        model (str, optional): The model to use. Defaults to "anthropic:claude-4-sonnet-20250514".
        mcps (list[MCPServer] | None, optional): List of MCP servers to connect the agent to. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.2.

    Returns:
        Agent: The chief agent
    """
    settings = ModelSettings(temperature=temperature)
    return Agent(
        model,
        name="Chief",
        system_prompt=CHIEF_SYSTEM_PROMPT,
        mcp_servers=mcps,
        model_settings=settings,
    )

"""
Provider configurations for different AI model providers.
"""

from os import environ

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_openrouter_model(
    model_name: str = "anthropic/claude-3.5-sonnet", api_key: str | None = None
) -> OpenAIChatModel:
    """
    Create an OpenAI-compatible model configured for OpenRouter.

    Args:
        model_name: The model identifier from OpenRouter's model list
        api_key: OpenRouter API key, defaults to OPENROUTER_API_KEY env var

    Returns:
        OpenAIChatModel configured for OpenRouter
    """
    if api_key is None:
        api_key = environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
        )

    provider = OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    return OpenAIChatModel(model_name, provider=provider)


def get_default_model(
    model_name: str | None = "deepseek/deepseek-chat-v3.1:free", api_key: str | None = None
) -> OpenAIChatModel:
    """
    Get the default model configuration for the application.

    Uses OpenRouter by default with deepseek/deepseek-chat-v3.1:free model.

    Args:
        model_name: The model to use, defaults to anthropic/claude-3.5-sonnet
        api_key: API key, defaults to OPENROUTER_API_KEY env var

    Returns:
        OpenAIChatModel configured for the specified provider
    """
    return get_openrouter_model(model_name, api_key)

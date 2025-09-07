"""
Provider configurations for different AI model providers.
"""

from os import environ

from dotenv import load_dotenv
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelName
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_openrouter_model(model_name: str = "deepseek/deepseek-chat-v3.1:free") -> OpenAIChatModel:
    """
    Create an OpenAI-compatible model configured for OpenRouter.

    Args:
        model_name: The model identifier from OpenRouter's model list

    Returns:
        OpenAIChatModel configured for OpenRouter
    """
    api_key = environ.get("OPENROUTER_API_KEY")
    provider = OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    return OpenAIChatModel(model_name, provider=provider)


def get_openai_model(model_name: str = "gpt-5-2025-08-07") -> OpenAIChatModel:
    """
    Create an OpenAI model directly using OpenAI's API.

    Args:
        model_name: The OpenAI model identifier (e.g., gpt-4, gpt-3.5-turbo)
        api_key: OpenAI API key, defaults to OPENAI_API_KEY env var

    Returns:
        OpenAIChatModel configured for OpenAI
    """
    return OpenAIChatModel(model_name)


def get_anthropic_model(model_name: AnthropicModelName = "claude-sonnet-4-20250514") -> AnthropicModel:
    """
    Create an Anthropic model using OpenRouter (since pydantic-ai doesn't have native Anthropic support).

    Args:
        model_name: The Anthropic model identifier (e.g., claude-3-5-sonnet-20241022)

    Returns:
        OpenAIChatModel configured for Anthropic via OpenRouter
    """
    # Use OpenRouter for Anthropic models since pydantic-ai doesn't have native Anthropic provider
    return AnthropicModel(model_name=model_name)


def get_default_model(
    anthropic_model_name: AnthropicModelName | str | None = "claude-sonnet-4-20250514",
    openai_model_name: str | None = "gpt-5-2025-08-07",
    openrouter_model_name: str | None = "deepseek/deepseek-chat-v3.1:free",
) -> FallbackModel:
    """
    Get the default model configuration for the application.

    Uses OpenRouter by default with deepseek/deepseek-chat-v3.1:free model.

    Args:
        anthropic_model_name: The Anthropic model identifier
        openai_model_name: The OpenAI model identifier
        openrouter_model_name: The OpenRouter model identifier, if None OpenRouter is skipped

    Returns:
        FallbackModel configured for the specified providers
    """
    # Ensure environment variables are loaded
    load_dotenv()

    anthropic_api_key = environ.get("ANTHROPIC_API_KEY")
    openai_api_key = environ.get("OPENAI_API_KEY")
    openrouter_api_key = environ.get("OPENROUTER_API_KEY")

    match [anthropic_api_key is not None, openai_api_key is not None, openrouter_api_key is not None]:
        case [False, False, False]:
            raise ValueError(
                "No API keys found. Please set at least one of ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY environment variables."
            )
        case [True, True, True]:
            return FallbackModel(
                get_anthropic_model(anthropic_model_name),
                get_openai_model(openai_model_name),
                get_openrouter_model(openrouter_model_name),
            )
        case [True, True, False]:
            return FallbackModel(
                get_anthropic_model(anthropic_model_name),
                get_openai_model(openai_model_name),
            )
        case [True, False, True]:
            return FallbackModel(
                get_anthropic_model(anthropic_model_name),
                get_openrouter_model(openrouter_model_name),
            )
        case [False, True, True]:
            return FallbackModel(
                get_openai_model(openai_model_name),
                get_openrouter_model(openrouter_model_name),
            )
        case [True, False, False]:
            return FallbackModel(
                get_anthropic_model(anthropic_model_name),
            )
        case [False, True, False]:
            return FallbackModel(
                get_openai_model(openai_model_name),
            )
        case [False, False, True]:
            return FallbackModel(
                get_openrouter_model(openrouter_model_name),
            )
        case _:
            raise ValueError("Unexpected error in API key configuration.")

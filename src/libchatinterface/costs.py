"""Cost tracking and calculation utilities for chat sessions."""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pydantic_ai.usage import RunUsage


@dataclass
class ModelCosts:
    """Represents costs for a specific model."""

    input_cost_per_1k: float  # USD per 1K input tokens
    output_cost_per_1k: float  # USD per 1K output tokens
    cached_cost_per_1k: Optional[float] = None  # USD per 1K cached tokens (if supported)


# Model pricing configuration (as of January 2025)
# Prices are per 1K tokens in USD
MODEL_PRICING: Dict[str, ModelCosts] = {
    # Anthropic models (direct API pricing)
    "claude-3-5-sonnet-20241022": ModelCosts(3.00, 15.00),
    "claude-3-5-sonnet-latest": ModelCosts(3.00, 15.00),
    "claude-sonnet-4-20250514": ModelCosts(15.00, 75.00),  # Estimated pricing
    "claude-3-5-haiku-20241022": ModelCosts(0.25, 1.25),
    "claude-3-5-haiku-latest": ModelCosts(0.25, 1.25),
    "claude-3-haiku-20240307": ModelCosts(0.25, 1.25),
    # OpenAI models (direct API pricing)
    "gpt-4o": ModelCosts(2.50, 10.00),
    "gpt-4o-2024-11-20": ModelCosts(2.50, 10.00),
    "gpt-5-2025-08-07": ModelCosts(5.00, 20.00),  # Estimated pricing
    "gpt-4o-mini": ModelCosts(0.15, 0.60),
    "gpt-4-turbo": ModelCosts(10.00, 30.00),
    # OpenRouter models (approximate pricing, varies)
    "deepseek/deepseek-chat-v3.1:free": ModelCosts(0.00, 0.00),  # Free tier
    "deepseek/deepseek-chat-v3.1": ModelCosts(0.14, 0.28),
    "anthropic/claude-3.5-sonnet": ModelCosts(3.00, 15.00),
    "anthropic/claude-3.5-haiku": ModelCosts(0.25, 1.25),
    "openai/gpt-4o": ModelCosts(2.50, 10.00),
    "openai/gpt-4o-mini": ModelCosts(0.15, 0.60),
}


@dataclass
class UsageCosts:
    """Represents token usage and associated costs."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    requests: int = 0
    cost_usd: Optional[float] = None
    model_name: Optional[str] = None


@dataclass
class SessionCosts:
    """Aggregated costs for an entire session."""

    total_usage: UsageCosts
    model_breakdown: Dict[str, UsageCosts]

    def __init__(self):
        self.total_usage = UsageCosts()
        self.model_breakdown = {}


def normalize_model_name(model_name: str) -> str:
    """Normalize model name for pricing lookup.

    Handles provider prefixes and variations in model names.
    """
    if not model_name:
        return model_name

    # Remove common provider prefixes
    model_name = re.sub(r"^(anthropic|openai|google|deepseek)/", "", model_name, flags=re.IGNORECASE)

    # Handle OpenRouter prefixes
    model_name = re.sub(r"^(anthropic:|openai:|google-gla:|deepseek/)", "", model_name, flags=re.IGNORECASE)

    return model_name.lower()


def calculate_usage_cost(usage: RunUsage, model_name: Optional[str] = None) -> UsageCosts:
    """Calculate costs for a RunUsage object.

    Args:
        usage: Pydantic AI RunUsage object
        model_name: Name of the model used

    Returns:
        UsageCosts object with token counts and calculated costs
    """
    costs = UsageCosts(
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cached_tokens=getattr(usage, "cached_tokens", 0),
        total_tokens=usage.total_tokens,
        requests=usage.requests,
        model_name=model_name,
    )

    # Calculate cost if model pricing is available
    if model_name:
        normalized_name = normalize_model_name(model_name)

        # Try exact match first
        model_costs = MODEL_PRICING.get(normalized_name)

        # Try partial matches for similar models
        if not model_costs:
            for pricing_key, pricing in MODEL_PRICING.items():
                if (
                    normalized_name in pricing_key
                    or pricing_key in normalized_name
                    or any(part in pricing_key for part in normalized_name.split("-")[:2])
                ):
                    model_costs = pricing
                    break

        if model_costs:
            input_cost = (costs.input_tokens / 1000.0) * model_costs.input_cost_per_1k
            output_cost = (costs.output_tokens / 1000.0) * model_costs.output_cost_per_1k
            cached_cost = 0.0

            if costs.cached_tokens and model_costs.cached_cost_per_1k:
                cached_cost = (costs.cached_tokens / 1000.0) * model_costs.cached_cost_per_1k

            costs.cost_usd = input_cost + output_cost + cached_cost

    return costs


def add_usage_to_session(session_costs: SessionCosts, usage_costs: UsageCosts) -> None:
    """Add usage costs to session totals.

    Args:
        session_costs: SessionCosts object to update
        usage_costs: UsageCosts to add
    """
    # Update totals
    session_costs.total_usage.input_tokens += usage_costs.input_tokens
    session_costs.total_usage.output_tokens += usage_costs.output_tokens
    session_costs.total_usage.cached_tokens += usage_costs.cached_tokens
    session_costs.total_usage.total_tokens += usage_costs.total_tokens
    session_costs.total_usage.requests += usage_costs.requests

    if usage_costs.cost_usd is not None:
        if session_costs.total_usage.cost_usd is None:
            session_costs.total_usage.cost_usd = 0.0
        session_costs.total_usage.cost_usd += usage_costs.cost_usd

    # Update model breakdown
    if usage_costs.model_name:
        model_key = usage_costs.model_name
        if model_key not in session_costs.model_breakdown:
            session_costs.model_breakdown[model_key] = UsageCosts(model_name=model_key)

        model_costs = session_costs.model_breakdown[model_key]
        model_costs.input_tokens += usage_costs.input_tokens
        model_costs.output_tokens += usage_costs.output_tokens
        model_costs.cached_tokens += usage_costs.cached_tokens
        model_costs.total_tokens += usage_costs.total_tokens
        model_costs.requests += usage_costs.requests

        if usage_costs.cost_usd is not None:
            if model_costs.cost_usd is None:
                model_costs.cost_usd = 0.0
            model_costs.cost_usd += usage_costs.cost_usd


def format_token_count(count: int) -> str:
    """Format token count with k/M notation for readability.

    Examples:
        1234 -> "1.2k"
        31233 -> "31.2k"
        1234567 -> "1.2M"
        5 -> "5"
    """
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count / 1000:.1f}k"
    else:
        return f"{count / 1000000:.1f}M"


def format_session_costs_for_metadata(session_costs: SessionCosts) -> Dict:
    """Format SessionCosts for inclusion in metadata.json.

    Args:
        session_costs: SessionCosts object

    Returns:
        Dictionary suitable for JSON serialization
    """

    def format_usage_costs(costs: UsageCosts) -> Dict:
        result = {
            "input_tokens": costs.input_tokens,
            "output_tokens": costs.output_tokens,
            "total_tokens": costs.total_tokens,
            "requests": costs.requests,
        }

        if costs.cached_tokens > 0:
            result["cached_tokens"] = costs.cached_tokens

        if costs.cost_usd is not None:
            result["cost_usd"] = round(costs.cost_usd, 6)  # Round to 6 decimal places

        return result

    result = {"total": format_usage_costs(session_costs.total_usage)}

    if session_costs.model_breakdown:
        result["models"] = {
            model_name: format_usage_costs(costs) for model_name, costs in session_costs.model_breakdown.items()
        }

    return result

from typing import Literal

from asyncer import asyncify
from pydantic_ai import RunContext

from libagentic.models import TavilyDeps


async def web_search(
    ctx: RunContext[TavilyDeps],
    query: str,
    search_depth: Literal["basic", "advanced"] = None,
    topic: Literal["general", "news", "finance"] = None,
    time_range: Literal["day", "week", "month", "year"] = None,
    start_date: str = None,
    end_date: str = None,
    days: int = None,
    max_results: int = None,
    timeout: int = 60,
    country: str = None,
) -> dict:
    """
    Perform a web search using the Tavily client.

    :param ctx: RunContext[TavilyDeps] - The run context containing dependencies.
    :param query: str - The search query.
    :param search_depth: Literal["basic", "advanced"] - The depth of the search.
    :param topic:  Literal["general", "news", "finance"] - The topic of the search.
    :param time_range: Literal["day", "week", "month", "year"] - The time range for the search.
    :param start_date: str - The start date for the search.
    :param end_date: str - The end date for the search.
    :param days: int - The number of days to look back for the search.
    :param max_results: int - The maximum number of results to return.
    :param timeout: int - The timeout for the search in seconds.
    :param country: str - The country code for the search.
    :return: dict - The search results.
    """
    return await asyncify(ctx.deps.tavily_client.search)(
        query=query,
        search_depth=search_depth,
        topic=topic,
        time_range=time_range,
        start_date=start_date,
        end_date=end_date,
        days=days,
        max_results=max_results,
        timeout=timeout,
        country=country,
    )

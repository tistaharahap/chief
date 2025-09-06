from dataclasses import dataclass

from tavily import TavilyClient


@dataclass
class TavilyDeps:
    tavily_client: TavilyClient

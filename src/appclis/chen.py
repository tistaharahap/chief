import asyncio
import contextlib
from os import environ

import typer
from tavily import TavilyClient

from libagentic.agents import get_chen_agent
from libagentic.models import TavilyDeps

app = typer.Typer(pretty_exceptions_enable=False)
TAVILY_API_KEY = environ.get("TAVILY_API_KEY")


async def run():
    agent = get_chen_agent()
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    deps = TavilyDeps(tavily_client=tavily_client)
    await agent.to_cli(prog_name="Chen", deps=deps)


@app.command()
def main():
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(run())


if __name__ == "__main__":
    app()

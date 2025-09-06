import asyncio
from os import environ

import typer
from dotenv import load_dotenv
from rich.console import Console
from tavily import TavilyClient

from libagentic.agents import get_chen_agent
from libagentic.models import TavilyDeps
from libchatinterface import ChatInterface

load_dotenv()
app = typer.Typer(pretty_exceptions_enable=False)
TAVILY_API_KEY = environ.get("TAVILY_API_KEY")


async def run():
    """Initialize and run the Chen chat interface."""
    agent = get_chen_agent()
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    deps = TavilyDeps(tavily_client=tavily_client)
    chat_interface = ChatInterface(agent=agent, deps=deps, app_name="chen", assistant_name="Chen")
    await chat_interface.run_chat()


@app.command()
def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C without ugly traceback
        console = Console()
        console.print("\n\n[yellow]Goodbye! 👋[/yellow]")


if __name__ == "__main__":
    app()

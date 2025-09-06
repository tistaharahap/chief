import asyncio

import typer
from rich.console import Console

from libagentic.agents import get_chief_agent

app = typer.Typer(pretty_exceptions_enable=False)


async def run():
    agent = get_chief_agent()
    await agent.to_cli(prog_name="Chief")


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

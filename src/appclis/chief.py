import asyncio
import contextlib

import typer

from libagentic.agents import get_chief_agent

app = typer.Typer(pretty_exceptions_enable=False)


async def run():
    agent = get_chief_agent()
    await agent.to_cli(prog_name="Chief")


@app.command()
def main():
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(run())


if __name__ == "__main__":
    app()

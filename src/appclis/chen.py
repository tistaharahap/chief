import asyncio
from os import environ

import typer
from dotenv import load_dotenv
from rich.console import Console
from tavily import TavilyClient

from appclis.settings.settings_manager import SettingsManager
from libagentic.agents import get_chen_agent
from libagentic.models import TavilyDeps
from libchatinterface import ChatInterface

load_dotenv()
app = typer.Typer(pretty_exceptions_enable=False)
console = Console()

# Global settings manager
settings_manager = SettingsManager()


async def run():
    """Initialize and run the Chen chat interface."""
    try:
        # Load settings (triggers onboarding if needed)
        settings = settings_manager.load_settings()

        # Get Tavily API key from environment as fallback
        tavily_api_key = environ.get("TAVILY_API_KEY")
        if not tavily_api_key:
            console.print("[yellow]Warning: TAVILY_API_KEY not found in environment variables.[/yellow]")
            console.print("[yellow]Web search functionality will be disabled.[/yellow]")
            tavily_client = None
            deps = None
        else:
            tavily_client = TavilyClient(api_key=tavily_api_key)
            deps = TavilyDeps(tavily_client=tavily_client)

        agent = get_chen_agent()
        chat_interface = ChatInterface(
            agent=agent,
            deps=deps,
            app_name="chen",
            assistant_name="Chen",
            context_window=settings.context_window or 200000,
        )
        await chat_interface.run_chat()

    except Exception as e:
        console.print(f"[red]Error starting Chen: {e}[/red]")
        raise


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Start Chen chat interface."""
    if ctx.invoked_subcommand is None:
        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            # Clean exit on Ctrl+C without ugly traceback
            console.print("\n\n[yellow]Goodbye! 👋[/yellow]")


@app.command()
def config():
    """Show current configuration settings."""
    settings_manager.show_current_settings()


@app.command()
def reset():
    """Reset all configuration settings."""
    settings_manager.reset_settings()


@app.command()
def onboard():
    """Run the onboarding process to configure settings."""
    try:
        settings_manager._run_onboarding()
    except KeyboardInterrupt:
        console.print("\n[yellow]Onboarding cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Onboarding failed: {e}[/red]")


if __name__ == "__main__":
    app()

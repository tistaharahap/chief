"""Rich-based chat interface components with history support."""

import json
import os
import re
import sys
import termios
import tty
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic_ai.messages import ModelRequest
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text


class HistoryManager:
    """Manages command history storage using Pydantic ModelRequest format."""

    def __init__(self, app_name: str = "chatinterface"):
        self.history_dir = Path.home() / f".{app_name}"
        self.history_file = self.history_dir / "history.jsonl"
        self.history: list[str] = []
        self._ensure_directory()
        self._load_history()

    def _ensure_directory(self):
        """Create ~/.{app_name} directory if it doesn't exist."""
        self.history_dir.mkdir(exist_ok=True)

    def _load_history(self):
        """Load command history from file."""
        if not self.history_file.exists():
            return

        try:
            with self.history_file.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Parse the JSON line to extract the user message
                        data = json.loads(line)
                        if data.get("type") == "user_prompt" and "content" in data:
                            # Support both old and new formats
                            content = data["content"]

                            # Check if we have valid model_request data (new format)
                            model_request = data.get("model_request")
                            if isinstance(model_request, dict):
                                # New format with proper JSON serialization
                                self.history.append(content)
                            elif isinstance(model_request, str) and model_request.startswith("ModelRequest("):
                                # Old format with string representation - still load the content
                                self.history.append(content)
                            else:
                                # Fallback: just use content
                                self.history.append(content)
        except Exception:
            # If there's any error loading history, start fresh
            self.history = []

    def add_message(self, message: str):
        """Add a user message to history."""
        if message.strip() and message not in ["/quit", "/exit", "/help", "quit", "exit", "help"]:
            # Create ModelRequest for storage
            model_request = ModelRequest.user_text_prompt(message)

            # Manually serialize ModelRequest to JSON by extracting data
            try:
                model_request_data = {"kind": getattr(model_request, "kind", "user"), "parts": []}

                # Serialize each part
                for part in model_request.parts:
                    part_data = {
                        "part_kind": getattr(part, "part_kind", "user_prompt"),
                        "content": part.content,
                        "timestamp": part.timestamp.isoformat() if part.timestamp else None,
                    }
                    model_request_data["parts"].append(part_data)

            except Exception:
                # Fallback if serialization fails
                model_request_data = {
                    "kind": "user",
                    "parts": [
                        {
                            "part_kind": "user_prompt",
                            "content": message,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    ],
                    "serialization_fallback": True,
                }

            # Convert to a serializable format
            history_entry = {
                "timestamp": datetime.now(UTC).isoformat(),
                "type": "user_prompt",
                "content": message,
                "model_request": model_request_data,
            }

            # Add to memory
            self.history.append(message)

            # Save to file
            try:
                with self.history_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(history_entry, ensure_ascii=False) + "\n")
            except Exception:
                pass  # Silently fail if can't write to file  # Silently fail if can't write to file  # Silently fail if can't write to file

    def get_history(self) -> list[str]:
        """Get the command history list."""
        return self.history.copy()


class RichHistoryPrompt:
    """Rich-native prompt with command history navigation using up/down arrows."""

    def __init__(self, console: Console, history_manager: HistoryManager):
        self.console = console
        self.history_manager = history_manager
        self.history_index = -1
        self.current_input = ""
        self.original_input = ""

    def _get_char(self) -> str:
        """Get a single character from stdin."""
        if os.name == "nt":  # Windows
            import msvcrt

            return msvcrt.getch().decode("utf-8", errors="ignore")
        else:  # Unix/Linux/macOS
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.cbreak(fd)
                ch = sys.stdin.read(1)
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _handle_arrow_keys(self, char: str) -> str | None:
        """Handle arrow key sequences and return the resulting input."""
        if char == "\x1b":  # ESC sequence
            # Read the next two characters to get the full arrow key sequence
            try:
                next_chars = sys.stdin.read(2)
                if next_chars == "[A":  # Up arrow
                    return self._navigate_history(-1)
                elif next_chars == "[B":  # Down arrow
                    return self._navigate_history(1)
            except Exception:
                pass
        return None

    def _navigate_history(self, direction: int) -> str:
        """Navigate through command history."""
        history = self.history_manager.get_history()
        if not history:
            return self.current_input

        if self.history_index == -1:
            # First time accessing history, store current input
            self.original_input = self.current_input

        # Calculate new index
        new_index = self.history_index + direction

        if direction == 1 and new_index >= 0:
            # Going forward (down arrow) beyond history
            self.history_index = -1
            return self.original_input
        elif direction == -1 and abs(new_index) <= len(history):
            # Going backward (up arrow) through history
            self.history_index = new_index
            return history[new_index]

        return self.current_input

    def ask(self, prompt: str) -> str:
        """Rich-styled prompt with history navigation."""
        # Reset history navigation state
        self.history_index = -1
        self.current_input = ""
        self.original_input = ""

        # For simplicity, fall back to regular Rich prompt with a note about history
        # This is a compromise to keep it native to Rich while adding history functionality
        self.console.print(f"{prompt} [dim](↑/↓ for history)[/dim]")

        # Use Rich's input but with history context
        try:
            # Attempt to use readline for history if available
            import readline

            # Set up readline with our history
            readline.clear_history()
            for item in self.history_manager.get_history():
                readline.add_history(item)

            result = input().strip()

        except ImportError:
            # Fallback to Rich prompt if readline not available
            result = Prompt.ask("", console=self.console).strip()

        return result


class MarkdownRenderer:
    """Handles markdown rendering with support for nested markdown code blocks."""

    def __init__(self, console: Console):
        self.console = console

    def render(self, content: str) -> None:
        """Render markdown content, handling nested markdown blocks."""
        # Pattern to detect nested markdown code blocks
        nested_pattern = r"```markdown\s*\n(.*?)```"

        # Find all nested markdown blocks
        matches = list(re.finditer(nested_pattern, content, re.DOTALL))

        if not matches:
            # No nested blocks, render normally
            md = Markdown(content)
            self.console.print(md)
            return

        # Process content with nested blocks
        current_pos = 0

        for match in matches:
            # Render content before the nested block
            if current_pos < match.start():
                pre_content = content[current_pos : match.start()]
                if pre_content.strip():
                    md = Markdown(pre_content)
                    self.console.print(md)

            # Render the nested markdown content
            nested_content = match.group(1)
            if nested_content.strip():
                # Create a panel to distinguish nested markdown
                nested_md = Markdown(nested_content)
                panel = Panel(nested_md, title="Markdown Content", border_style="blue")
                self.console.print(panel)

            current_pos = match.end()

        # Render any remaining content
        if current_pos < len(content):
            remaining_content = content[current_pos:]
            if remaining_content.strip():
                md = Markdown(remaining_content)
                self.console.print(md)


class ChatInterface:
    """Generic chat interface using Rich for rendering with history support."""

    def __init__(
        self,
        agent: Any,  # Accept any Pydantic AI agent type
        deps: Any = None,
        app_name: str = "chatinterface",
        assistant_name: str = "Assistant",
    ):
        self.agent = agent
        self.deps = deps
        self.app_name = app_name
        self.assistant_name = assistant_name
        self.console = Console()
        self.renderer = MarkdownRenderer(self.console)
        self.history_manager = HistoryManager(app_name)
        self.history_prompt = RichHistoryPrompt(self.console, self.history_manager)
        self.running = True

    def show_welcome(self):
        """Display welcome message."""
        welcome_text = Text(f"{self.assistant_name} AI Assistant", style="bold blue")
        welcome_panel = Panel(
            welcome_text,
            subtitle="Type your message, '/quit' to exit, or use ↑/↓ arrows for history",
            border_style="blue",
        )
        self.console.print(welcome_panel)
        self.console.print()

    def get_user_input(self) -> str:
        """Get input from user with rich prompt and history navigation."""
        try:
            user_input = self.history_prompt.ask("[bold green]You[/bold green]")
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return "/quit"

    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns False if should exit."""
        if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
            self.console.print("[yellow]Goodbye![/yellow]")
            return False
        elif user_input.lower() in ["/help", "help"]:
            help_text = f"""
Available commands:
- /quit, /exit: Exit the chat
- /help: Show this help message
- Any other text: Send message to {self.assistant_name} AI
"""
            self.console.print(Panel(help_text.strip(), title="Help", border_style="yellow"))
            return True
        return True

    async def send_message(self, message: str) -> str:
        """Send message to agent and get response."""
        try:
            # Use the agent's run method with dependencies
            response = await self.agent.run(message, deps=self.deps)

            # Extract the actual message content from the agent response
            if hasattr(response, "data"):
                return str(response.data)
            elif hasattr(response, "output"):
                return str(response.output)
            else:
                return str(response)
        except Exception as e:
            return f"Error: {str(e)}"

    async def run_chat(self):
        """Main chat loop."""
        self.show_welcome()

        while self.running:
            # Get user input
            user_input = self.get_user_input()

            if not user_input:
                continue

            # Handle special commands
            if user_input.startswith("/") or user_input.lower() in ["quit", "exit", "help"]:
                self.running = self.handle_command(user_input)
                continue

            # Add to history only when actually sending to agent
            self.history_manager.add_message(user_input)

            # Show thinking indicator
            with self.console.status(f"[bold green]{self.assistant_name} is thinking...", spinner="dots"):
                try:
                    response = await self.send_message(user_input)
                except Exception as e:
                    response = f"Error communicating with agent: {str(e)}"

            # Display response
            self.console.print()
            self.console.print(f"[bold blue]{self.assistant_name}:[/bold blue]")
            self.renderer.render(response)
            self.console.print()

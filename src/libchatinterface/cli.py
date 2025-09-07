"""Rich-based chat interface components with history support."""

import asyncio
import contextlib
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

from libchatinterface.costs import format_token_count


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
        context_window: int = 200_000,
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

        # Import here to avoid circular imports
        from libchatinterface.session import SessionManager

        self.session_manager = SessionManager(app_name, context_window=context_window)

        # Log system prompt if available
        system_prompt = getattr(agent, "system_prompt", None)
        if system_prompt:
            self.session_manager.log_system_prompt(system_prompt)

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
        except EOFError:
            return "/quit"
        except KeyboardInterrupt:
            # Let KeyboardInterrupt propagate for immediate exit
            raise

    async def _background_title_generation(self) -> None:
        """Generate AI title in background without blocking the main conversation."""
        with contextlib.suppress(Exception):
            await self.session_manager.update_title_with_ai()

    def _prepare_agent_with_context(self) -> Any:
        """Prepare agent with compressed context if available."""
        if not self.session_manager.compressed_context:
            return self.agent

        # Create agent with extended system prompt including compressed context
        from pydantic_ai import Agent

        # Get the original system prompt and extend it with compressed context
        original_prompt = getattr(self.agent, "system_prompt", "")
        extended_prompt = f"{original_prompt}\n\nPrevious Session Context: {self.session_manager.compressed_context}"

        # Create new agent instance with extended system prompt
        # Copy all settings from the original agent
        return Agent(
            model=self.agent.model,
            name=self.agent.name,
            system_prompt=extended_prompt,
            deps_type=getattr(self.agent, "deps_type", None),
            tools=getattr(self.agent, "tools", []),
            model_settings=getattr(self.agent, "model_settings", None),
            mcp_servers=getattr(self.agent, "mcp_servers", None),
        )

    def show_usage_metadata(self) -> None:
        """Display session usage metadata at bottom of interface."""
        # Only show if we have messages
        if self.session_manager.message_count == 0:
            return

        # Get session costs
        session_costs = self.session_manager.session_costs
        total = session_costs.total_usage

        # Don't show if no usage data yet
        if total.total_tokens == 0:
            return

        # Create subtle horizontal divider
        self.console.rule(style="dim")

        # Format usage information
        usage_parts = []

        # Tokens
        if total.input_tokens > 0 or total.output_tokens > 0:
            tokens_text = (
                f"Tokens: {format_token_count(total.input_tokens)} in, {format_token_count(total.output_tokens)} out"
            )
            if total.cached_tokens > 0:
                tokens_text += f", {format_token_count(total.cached_tokens)} cached"
            tokens_text += f" ({format_token_count(total.total_tokens)} total)"
            usage_parts.append(tokens_text)

        # Requests
        if total.requests > 0:
            usage_parts.append(f"Requests: {total.requests}")

        # Cost
        if total.cost_usd is not None and total.cost_usd > 0:
            cost_text = "Cost: <$0.01" if total.cost_usd < 0.01 else f"Cost: ${total.cost_usd:.4f}"
            usage_parts.append(cost_text)

        # Display usage info
        if usage_parts:
            usage_text = " • ".join(usage_parts)
            self.console.print(f"[dim]{usage_text}[/dim]")

    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns False if should exit."""
        if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
            self.console.print("[yellow]Goodbye![/yellow]")
            return False
        elif user_input.lower() in ["/help", "help"]:
            help_text = f"""
Available commands:
- /quit, /exit: Exit the chat
- /resume: Resume a previous chat session
- /help: Show this help message
- Any other text: Send message to {self.assistant_name} AI
"""
            self.console.print(Panel(help_text.strip(), title="Help", border_style="yellow"))
            return True
        elif user_input.lower() == "/resume":
            return self._handle_resume_command()
        return True

    def _handle_resume_command(self) -> bool:
        """Handle the /resume command to load a previous session."""
        from libchatinterface.session import ResumableSessionManager, SessionLister

        try:
            # Create session lister and show selection interface
            lister = SessionLister(self.app_name)
            selected_session_dir = lister.show_session_selection(self.console)

            if selected_session_dir is None:
                self.console.print("[yellow]Resume cancelled.[/yellow]")
                return True

            # Load the selected session
            resumed_manager = ResumableSessionManager.from_existing_session(
                selected_session_dir, self.app_name, context_window=self.session_manager.context_window
            )

            # Display session info
            session_info = resumed_manager.get_session_info()
            self.console.print(f"[green]✓ Resumed session: {session_info['title']}[/green]")
            self.console.print(
                f"[dim]Messages: {session_info['message_count']}, Last activity: {session_info['last_message_timestamp'] or 'Unknown'}[/dim]"
            )

            # Replace current session manager with resumed one
            self.session_manager = resumed_manager

            # Display conversation history
            self._display_conversation_history()

            return True

        except Exception as e:
            self.console.print(f"[red]Error resuming session: {str(e)}[/red]")
            return True

    def _display_conversation_history(self) -> None:
        """Display the conversation history from the resumed session."""
        messages = self.session_manager.get_conversation_context()

        if not messages:
            self.console.print("[dim]No previous messages to display.[/dim]")
            return

        self.console.print()
        self.console.print("[bold blue]Conversation History:[/bold blue]")
        self.console.print()

        for message in messages:
            msg_type = message.get("type", "unknown")
            content = message.get("content", "")

            # Skip system prompts as requested
            if msg_type == "system_prompt":
                continue

            if msg_type == "user_message":
                self.console.print(f"[bold green]You:[/bold green] {content}")
                self.console.print()  # Add line break after each message
            elif msg_type == "assistant_response":
                self.console.print(f"[bold blue]{self.assistant_name}:[/bold blue] {content}")
                self.console.print()  # Add line break after each message
            elif msg_type == "context_compression":
                self.console.print(f"[yellow]ℹ {content}[/yellow]")
                self.console.print()  # Add line break after each message

        self.console.print("[dim]--- End of history ---[/dim]")
        self.console.print()

    async def send_message(self, message: str) -> str:
        """Send message to agent and get response using streaming."""
        try:
            # Add 2 line breaks as requested for positioning
            self.console.print("\n")

            # Show live status updates during the wait period
            with self.console.status("[bold blue]Processing message...") as status:
                # Log user message to session
                self.session_manager.log_user_message(message)

                # Check for compression after adding the new message (reactive compression)
                await self.session_manager.compress_context_if_needed()

                # Generate AI title for first user message (run in background)
                if not hasattr(self, "_title_generated"):
                    self._title_generated = True
                    # Start title generation as background task - don't await
                    asyncio.create_task(self._background_title_generation())

                # Update status for the next phase (this is where the long delay happens)
                status.update("[bold blue]Initializing agent...")

                # Prepare agent with compressed context if available
                current_agent = self._prepare_agent_with_context()

                # Start the streaming context but don't stream yet
                status.update("[bold blue]Awaiting response...")

                # Check if this is a resumed session and get message history
                message_history = None
                if hasattr(self.session_manager, "get_pydantic_message_history"):
                    message_history = self.session_manager.get_pydantic_message_history()

                # Use message history for resumed sessions
                if message_history:
                    stream_context = current_agent.run_stream(message, deps=self.deps, message_history=message_history)
                else:
                    stream_context = current_agent.run_stream(message, deps=self.deps)

                result = await stream_context.__aenter__()

            # Status is automatically cleared when exiting the status context
            # Now we can stream without the spinner interfering
            try:
                # Display assistant name with proper line breaks
                self.console.print()
                self.console.print(f"[bold blue]{self.assistant_name}:[/bold blue]")

                # Stream text output character by character, appending each delta
                full_response = ""
                try:
                    async for text_delta in result.stream_text(delta=True, debounce_by=0.01):
                        # Print each character as it arrives - Rich Console doesn't need flush
                        self.console.print(text_delta, end="", markup=True, highlight=False)
                        full_response += text_delta
                except GeneratorExit:
                    # Handle clean generator exit on Ctrl+C
                    pass
                except Exception as stream_error:
                    self.console.print(f"\n[red]Streaming error: {str(stream_error)}[/red]")

                self.console.print()  # New line after response

                # Log usage and costs from this run
                try:
                    run_usage = result.usage()
                    model_name = getattr(result, "model_name", None)
                    if run_usage:
                        self.session_manager.log_run_usage(run_usage, model_name)
                except Exception:
                    # If we can't get usage data, continue without cost tracking
                    pass

                # Log all Pydantic AI messages for complete context (includes user/assistant messages)
                try:
                    all_messages = result.all_messages()
                    # Only log new messages (avoid duplicating across sessions)
                    new_messages = [
                        msg
                        for msg in all_messages
                        if not hasattr(self, "_last_message_count")
                        or len(all_messages) > getattr(self, "_last_message_count", 0)
                    ]

                    # Log new messages if we have them
                    if new_messages:
                        self.session_manager.log_pydantic_messages(new_messages)
                    else:
                        # Even if no "new" messages, we need to ensure current assistant response tokens are counted
                        # Find the latest assistant response and log it for token counting
                        from pydantic_ai.messages import ModelResponse

                        assistant_responses = [msg for msg in all_messages if isinstance(msg, ModelResponse)]
                        if assistant_responses:
                            latest_response = assistant_responses[-1]
                            self.session_manager.log_pydantic_messages([latest_response])

                    # ALWAYS check compression after assistant responses
                    await self.session_manager.compress_context_if_needed()

                    self._last_message_count = len(all_messages)
                except Exception:
                    # If we can't get Pydantic messages, continue with basic logging
                    # Fallback to basic logging if Pydantic message logging fails
                    if full_response:
                        self.session_manager.log_assistant_response(full_response)
                        # Check for compression after assistant response
                        await self.session_manager.compress_context_if_needed()
                    else:
                        pass
            finally:
                # Properly close the stream context
                await stream_context.__aexit__(None, None, None)

                # Safety net: Always check compression after any response processing
                await self.session_manager.compress_context_if_needed()

            return full_response

        except KeyboardInterrupt:
            # Let KeyboardInterrupt propagate for immediate exit
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
            raise
        except Exception as e:
            # Display error immediately instead of returning it
            self.console.print()
            self.console.print(f"[bold blue]{self.assistant_name}:[/bold blue]")
            self.console.print(f"[red]Error: {str(e)}[/red]")

            # Log error to session
            error_msg = f"Error: {str(e)}"
            self.session_manager.log_assistant_response(error_msg)
            # Check for compression after error response
            await self.session_manager.compress_context_if_needed()

            return error_msg

    async def run_chat(self):
        """Main chat loop with streaming support."""
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

            # Send message and stream response - errors are handled in send_message
            try:
                await self.send_message(user_input)
            except KeyboardInterrupt:
                # Let KeyboardInterrupt propagate for immediate exit
                raise

            # Show usage metadata after each interaction
            self.show_usage_metadata()

            self.console.print()

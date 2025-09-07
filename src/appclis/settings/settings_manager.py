"""Settings management for Chen with JSON file storage and onboarding flow."""

import json
import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from appclis.settings.chen_settings import ChenSettings

console = Console()


class SettingsManager:
    """Manages Chen settings with JSON file storage and interactive onboarding."""

    def __init__(self, settings_dir: Path | None = None):
        """Initialize the settings manager.

        Args:
            settings_dir: Custom directory for settings. Defaults to ~/.chen/
        """
        self.settings_dir = settings_dir or Path.home() / ".chen"
        self.settings_file = self.settings_dir / "settings.json"

    def ensure_settings_dir(self) -> None:
        """Create the settings directory if it doesn't exist."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)

    def settings_exist(self) -> bool:
        """Check if settings file exists."""
        return self.settings_file.exists()

    def load_settings(self) -> ChenSettings:
        """Load settings from JSON file, trigger onboarding if file doesn't exist.

        Returns:
            ChenSettings: The loaded or newly created settings
        """
        if not self.settings_exist():
            return self._run_onboarding()

        try:
            with self.settings_file.open(encoding="utf-8") as f:
                data = json.load(f)
            return ChenSettings.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            console.print(f"[red]Error loading settings: {e}[/red]")
            console.print("[yellow]Running onboarding to recreate settings...[/yellow]")
            return self._run_onboarding()

    def save_settings(self, settings: ChenSettings) -> None:
        """Save settings to JSON file.

        Args:
            settings: The settings to save
        """
        self.ensure_settings_dir()

        with self.settings_file.open("w", encoding="utf-8") as f:
            json.dump(settings.model_dump(), f, indent=2, ensure_ascii=False)

        console.print(f"[green]Settings saved to {self.settings_file}[/green]")

    def _run_onboarding(self) -> ChenSettings:
        """Run the interactive onboarding process to collect settings.

        Returns:
            ChenSettings: The configured settings
        """
        console.print("\n[bold blue]Welcome to Chen! 🤖[/bold blue]")
        console.print("Let's configure your settings. Press Enter to skip optional fields.\n")

        # Get environment variable defaults
        env_defaults = self._get_env_defaults()

        # Display defaults if any are found
        if env_defaults:
            console.print("[dim]Found these values in your environment:[/dim]")
            table = Table(show_header=False, box=None)
            for key, value in env_defaults.items():
                if value:
                    display_value = value if not key.endswith("_key") else f"{value[:8]}..."
                    table.add_row(f"  {key}:", f"[dim]{display_value}[/dim]")
            console.print(table)
            console.print()

        settings_data = {}

        # Anthropic API Key
        anthropic_key = self._prompt_for_setting(
            "anthropic_api_key",
            "Anthropic API key",
            "https://console.anthropic.com/settings/keys",
            env_defaults.get("anthropic_api_key"),
            mask_input=True,
        )
        if anthropic_key:
            settings_data["anthropic_api_key"] = anthropic_key

        # OpenAI API Key
        openai_key = self._prompt_for_setting(
            "openai_api_key",
            "OpenAI API key",
            "https://platform.openai.com/api-keys",
            env_defaults.get("openai_api_key"),
            mask_input=True,
        )
        if openai_key:
            settings_data["openai_api_key"] = openai_key

        # OpenRouter API Key
        openrouter_key = self._prompt_for_setting(
            "openrouter_api_key",
            "OpenRouter API key",
            "https://openrouter.ai/settings/keys",
            env_defaults.get("openrouter_api_key"),
            mask_input=True,
        )
        if openrouter_key:
            settings_data["openrouter_api_key"] = openrouter_key

        # Tavily API Key
        tavily_key = self._prompt_for_setting(
            "tavily_api_key",
            "Tavily API key (for web search)",
            "https://app.tavily.com/home",
            env_defaults.get("tavily_api_key"),
            mask_input=True,
        )
        if tavily_key:
            settings_data["tavily_api_key"] = tavily_key

        # Context Window
        context_window = self._prompt_for_setting(
            "context_window",
            "Context window size (tokens)",
            None,
            env_defaults.get("context_window", 200000),
            field_type=int,
        )
        if context_window:
            settings_data["context_window"] = context_window

        try:
            settings = ChenSettings.model_validate(settings_data)
            self.save_settings(settings)

            console.print("\n[green]✅ Configuration complete![/green]")
            console.print(f"Settings saved to: [dim]{self.settings_file}[/dim]\n")

            return settings

        except Exception as e:
            console.print(f"\n[red]❌ Configuration failed: {e}[/red]")
            console.print("Please check your API keys and try again.")
            raise

    def _get_env_defaults(self) -> dict[str, Any]:
        """Get default values from environment variables.

        Returns:
            Dict with environment variable values
        """
        return {
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
            "openai_api_key": os.environ.get("OPENAI_API_KEY"),
            "openrouter_api_key": os.environ.get("OPENROUTER_API_KEY"),
            "tavily_api_key": os.environ.get("TAVILY_API_KEY"),
            "context_window": os.environ.get("CONTEXT_WINDOW", 200000),
        }

    def _prompt_for_setting(
        self,
        field_name: str,
        display_name: str,
        url_hint: str | None = None,
        default: Any | None = None,
        mask_input: bool = False,
        field_type: type = str,
    ) -> Any | None:
        """Prompt user for a setting value.

        Args:
            field_name: The field name in settings
            display_name: Human readable name for the field
            url_hint: URL where user can get the value
            default: Default value to use
            mask_input: Whether to mask the input (for API keys)
            field_type: Type to convert the input to

        Returns:
            The entered value or None if skipped
        """
        # Build prompt text
        prompt_text = f"[bold]{display_name}[/bold]"
        if url_hint:
            prompt_text += f" [dim]({url_hint})[/dim]"

        if default:
            if mask_input:
                display_default = f"{str(default)[:8]}..." if len(str(default)) > 8 else str(default)
            else:
                display_default = str(default)
            prompt_text += f" [dim](default: {display_default})[/dim]"

        prompt_text += ": "

        try:
            if mask_input:
                value = Prompt.ask(prompt_text, password=True, default=str(default) if default else "")
            else:
                value = Prompt.ask(prompt_text, default=str(default) if default else "")

            if not value.strip():
                return None

            if field_type is int:
                return int(value)
            return value

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Onboarding cancelled[/yellow]")
            raise
        except ValueError as e:
            console.print(f"[red]Invalid value: {e}[/red]")
            return self._prompt_for_setting(field_name, display_name, url_hint, default, mask_input, field_type)

    def show_current_settings(self) -> None:
        """Display current settings in a formatted table."""
        if not self.settings_exist():
            console.print("[yellow]No settings file found. Run chen to trigger onboarding.[/yellow]")
            return

        try:
            settings = self.load_settings()

            console.print(f"\n[bold]Chen Settings[/bold] [dim]({self.settings_file})[/dim]\n")

            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", justify="center")

            # Add each setting to table
            for field_name, field_info in settings.model_fields.items():
                value = getattr(settings, field_name)

                if value is None:
                    display_value = "[dim]Not set[/dim]"
                    status = "❌"
                elif field_name.endswith("_api_key"):
                    display_value = f"{str(value)[:8]}..." if len(str(value)) > 8 else str(value)
                    status = "✅"
                else:
                    display_value = str(value)
                    status = "✅"

                description = field_info.description or field_name
                table.add_row(description, display_value, status)

            console.print(table)
            console.print()

        except Exception as e:
            console.print(f"[red]Error reading settings: {e}[/red]")

    def get_setting(self, key: str) -> Any:
        """Get a single setting value.

        Args:
            key: The setting key to retrieve

        Returns:
            The setting value

        Raises:
            ValueError: If key doesn't exist
        """
        if not self.settings_exist():
            console.print("[yellow]No settings file found. Run chen to trigger onboarding.[/yellow]")
            return None

        # Validate key exists in model
        valid_keys = self._get_valid_keys()
        if key not in valid_keys:
            valid_keys_str = ", ".join(valid_keys)
            raise ValueError(f"Invalid setting key '{key}'. Valid keys: {valid_keys_str}")

        settings = self.load_settings()
        return getattr(settings, key)

    def set_setting(self, key: str, value: str) -> None:
        """Set a single setting value.

        Args:
            key: The setting key to set
            value: The string value to set (will be converted to correct type)

        Raises:
            ValueError: If key doesn't exist or value is invalid
        """
        if not self.settings_exist():
            console.print("[yellow]No settings file found. Run onboarding first.[/yellow]")
            return

        # Validate key exists in model
        valid_keys = self._get_valid_keys()
        if key not in valid_keys:
            valid_keys_str = ", ".join(valid_keys)
            raise ValueError(f"Invalid setting key '{key}'. Valid keys: {valid_keys_str}")

        # Load current settings
        settings = self.load_settings()
        settings_dict = settings.model_dump()

        # Convert value to correct type based on field type
        converted_value = self._convert_setting_value(key, value)
        settings_dict[key] = converted_value

        try:
            # Validate the entire model
            updated_settings = ChenSettings.model_validate(settings_dict)
            self.save_settings(updated_settings)
            console.print(f"[green]✅ Setting '{key}' updated successfully[/green]")
        except Exception as e:
            raise ValueError(f"Failed to update setting: {e}") from e

    def _get_valid_keys(self) -> list[str]:
        """Get list of valid setting keys from the model."""
        return list(ChenSettings.model_fields.keys())

    def _convert_setting_value(self, key: str, value: str) -> Any:
        """Convert string value to the correct type for the given setting key.

        Args:
            key: The setting key
            value: The string value to convert

        Returns:
            The converted value

        Raises:
            ValueError: If conversion fails
        """
        field_info = ChenSettings.model_fields[key]

        # Handle None/empty values
        if not value or value.lower() in ("none", "null", ""):
            return None

        # Get the field type (handle Union types like str | None)
        field_type = field_info.annotation

        # Handle Union types (like str | None)
        if hasattr(field_type, "__args__"):
            # Extract the non-None type from the Union
            args = field_type.__args__
            field_type = next((arg for arg in args if arg is not type(None)), str)

        if field_type is int:
            try:
                converted = int(value)
                # Apply field constraints (like gt=1 for context_window)
                if hasattr(field_info, "gt") and field_info.gt is not None and converted <= field_info.gt:
                    raise ValueError(f"Value must be greater than {field_info.gt}")
                return converted
            except ValueError as e:
                raise ValueError(f"Invalid integer value '{value}' for {key}: {e}") from e
        elif field_type is str:
            return value
        else:
            # Default to string for unknown types
            return value

    def reset_settings(self) -> bool:
        """Reset settings by deleting the settings file.

        Returns:
            True if settings were reset, False if cancelled
        """
        if not self.settings_exist():
            console.print("[yellow]No settings file exists to reset.[/yellow]")
            return False

        if not Confirm.ask(f"Are you sure you want to reset all settings?\nThis will delete {self.settings_file}"):
            console.print("[yellow]Reset cancelled.[/yellow]")
            return False

        try:
            self.settings_file.unlink()
            console.print("[green]Settings reset successfully.[/green]")
            console.print("Run chen again to trigger onboarding.")
            return True
        except Exception as e:
            console.print(f"[red]Error resetting settings: {e}[/red]")
            return False

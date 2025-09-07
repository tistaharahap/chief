import sys
from pydantic import Field, model_validator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChenSettings(BaseSettings):
    anthropic_api_key: str | None = Field(
        None, description="Anthropic API key, https://console.anthropic.com/settings/keys"
    )
    openai_api_key: str | None = Field(None, description="OpenAI API key, https://platform.openai.com/api-keys")
    openrouter_api_key: str | None = Field(None, description="OpenRouter API key, https://openrouter.ai/settings/keys")
    tavily_api_key: str | None = Field(None, description="Tavily API key, https://app.tavily.com/home")
    context_window: int | None = Field(200_000, gt=1, description="Context window size to trigger compression")

    model_config = SettingsConfigDict(case_sensitive=False)

    @model_validator(mode="after")
    def validate_api_keys(self) -> Self:
        if not any([self.anthropic_api_key, self.openai_api_key, self.openrouter_api_key]):
            raise ValueError("At least one API key must be set: Anthropic, OpenAI, or OpenRouter.")
        return self

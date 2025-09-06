from pydantic import Field

from libshared.mongo import BaseMongoDocument, SlugMixin


class Prompt(BaseMongoDocument, SlugMixin):
    system_prompt: str | None = Field(None, description="The system prompt")
    user_prompt: str | None = Field(None, description="The user prompt")

    user_id: str | None = Field(None, description="The user id who owns the prompt")

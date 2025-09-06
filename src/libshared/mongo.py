import time
from datetime import UTC, datetime
from typing import Self

from beanie import Document, Insert, Replace, Save, before_event
from coolname import generate_slug
from pydantic import Field


class SlugMixin:
    """Mixin class that provides automatic unique slug generation."""

    slug: str | None = Field(None, description="The slug of the document")

    @before_event(Insert)
    async def generate_unique_slug(self: Self):
        """Generate a unique slug before inserting the document."""
        # Ensure this is used with a Beanie Document class
        cls = type(self)
        if not issubclass(cls, Document):
            raise TypeError(f"SlugMixin can only be used with Beanie Document classes, not {cls.__name__}")

        if self.slug is None:
            max_attempts = 10
            for _ in range(max_attempts):
                potential_slug = generate_slug(3)
                # Check if this slug already exists - safe now because we verified it's a Document
                existing = await cls.find_one({"slug": potential_slug})
                if existing is None:
                    object.__setattr__(self, "slug", potential_slug)
                    break
            else:
                # If we couldn't find a unique slug after max_attempts, use a timestamp suffix
                timestamp = int(time.time())
                object.__setattr__(self, "slug", f"{generate_slug(3)}-{timestamp}")


class BaseMongoDocument(Document):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="The date and time the document was created",
    )
    updated_at: datetime | None = Field(None, description="The date and time the document was last updated")
    deleted_at: datetime | None = Field(None, description="The date and time the document was deleted")

    @before_event(Replace, Save)
    def update_timestamp(self):
        """Update the updated_at field before replacing or saving the document."""
        self.updated_at = datetime.now(tz=UTC)

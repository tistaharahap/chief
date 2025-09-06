from datetime import UTC, datetime


def current_datetime() -> str:
    """
    Get the current date and time in UTC in ISO 8601 format.

    Returns:
        str: The current date and time in ISO 8601 format.
    """
    return datetime.now(tz=UTC).isoformat()

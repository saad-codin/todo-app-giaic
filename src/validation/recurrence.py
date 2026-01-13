"""Recurrence validation for todo tasks."""

VALID_RECURRENCE = {"none", "daily", "weekly", "monthly"}


def validate_recurrence(recurrence: str) -> str | None:
    """Validate recurrence type.

    Args:
        recurrence: Recurrence value to validate

    Returns:
        None if valid, error message string if invalid
    """
    if recurrence not in VALID_RECURRENCE:
        return f"Error: Invalid recurrence '{recurrence}'. Valid values: none, daily, weekly, monthly"
    return None

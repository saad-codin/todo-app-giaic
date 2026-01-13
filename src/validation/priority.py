"""Priority validation for todo tasks."""

VALID_PRIORITIES = {"high", "medium", "low"}


def validate_priority(priority: str) -> str | None:
    """Validate priority value.

    Args:
        priority: Priority value to validate

    Returns:
        None if valid, error message string if invalid
    """
    if priority not in VALID_PRIORITIES:
        return f"Error: Invalid priority '{priority}'. Valid values: high, medium, low"
    return None

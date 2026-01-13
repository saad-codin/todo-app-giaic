"""Date and datetime validation for todo tasks."""

from datetime import date, datetime


def validate_date(date_string: str) -> date | str:
    """Validate and parse ISO 8601 date string (YYYY-MM-DD).

    Args:
        date_string: Date string in ISO 8601 format

    Returns:
        date object if valid, error message string if invalid
    """
    try:
        return date.fromisoformat(date_string)
    except ValueError:
        return "Error: Invalid date format. Expected YYYY-MM-DD"


def validate_datetime(datetime_string: str) -> datetime | str:
    """Validate and parse ISO 8601 datetime string (YYYY-MM-DD HH:MM).

    Args:
        datetime_string: Datetime string in ISO 8601 format

    Returns:
        datetime object if valid, error message string if invalid
    """
    try:
        return datetime.fromisoformat(datetime_string)
    except ValueError:
        return "Error: Invalid datetime format. Expected YYYY-MM-DD HH:MM"

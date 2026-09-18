"""Timestamp utilities."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Get current UTC timestamp with timezone awareness."""
    return datetime.now(timezone.utc)


def to_iso8601(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string."""
    return dt.isoformat()


def from_iso8601(iso_string: str) -> datetime:
    """Parse ISO 8601 string to datetime."""
    return datetime.fromisoformat(iso_string)


def timestamp_to_datetime(timestamp: float) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_to_timestamp(dt: datetime) -> float:
    """Convert datetime to Unix timestamp."""
    return dt.timestamp()

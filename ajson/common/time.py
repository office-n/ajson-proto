"""
Time utility for SQLite compatibility.
"""
from datetime import datetime, timezone

def utcnow_sqlite_compatible() -> datetime:
    """
    Get current UTC time as naive datetime for SQLite compatibility.
    
    Returns:
        datetime: Naive datetime in UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

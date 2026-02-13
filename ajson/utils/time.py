import datetime
from datetime import timezone, timedelta

# JST Timezone (UTC+9)
JST = timezone(timedelta(hours=9))

def get_utc_now() -> datetime.datetime:
    """Get current time in UTC."""
    return datetime.datetime.now(timezone.utc)

def get_utc_iso() -> str:
    """Get current time in UTC ISO8601 format."""
    return get_utc_now().isoformat()

def get_jst_now() -> datetime.datetime:
    """Get current time in JST."""
    return datetime.datetime.now(JST)

def get_jst_iso() -> str:
    """Get current time in JST ISO8601 format."""
    return get_jst_now().isoformat()

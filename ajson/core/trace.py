# ajson/core/trace.py
import json
from datetime import datetime
from typing import Any, Dict

class Trace:
    """
    Records execution traces.
    """
    def __init__(self):
        self.records = []

    def log(self, event_type: str, details: Dict[str, Any]):
        timestamp = datetime.now().isoformat()
        record = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        self.records.append(record)
        # In a real impl, this might stream to a file or service

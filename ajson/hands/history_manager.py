
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistoryManager:
    """Manages session history with automatic path masking."""
    
    def __init__(self, history_dir: str = "logs/history"):
        self.history_dir = history_dir
        self.current_session_id = self._generate_session_id()
        self.entries: List[Dict[str, Any]] = []
        self.log_path = os.path.join(self.history_dir, f"session_{self.current_session_id}.json")
        
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir, exist_ok=True)

    def _generate_session_id(self) -> str:
        # Format: YYYYMMDD_HHMMSS (No absolute paths allowed in IDs)
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _mask_path(self, text: str) -> str:
        """Replace absolute user paths with [USER_HOME]."""
        home_dir = os.path.expanduser("~")
        if home_dir in text:
            return text.replace(home_dir, "[USER_HOME]")
        return text

    def add_entry(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": self._mask_path(content),
            "metadata": metadata if metadata else {}
        }
        self.entries.append(entry)

    def get_entries(self, last_n: int = 10) -> List[Dict[str, Any]]:
        return self.entries[-last_n:]

    def flush(self):
        """Save history entries to JSON file."""
        if not self.entries:
            return
            
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": self.current_session_id,
                    "updated_at": datetime.now().isoformat(),
                    "entries": self.entries
                }, f, indent=2, ensure_ascii=False)
            # Update a symlink for the latest session
            latest_path = os.path.join(self.history_dir, "latest.json")
            if os.path.exists(latest_path):
                os.remove(latest_path)
            # Use relative path for symlink to keep it portable
            os.symlink(os.path.basename(self.log_path), latest_path)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_latest(self) -> List[Dict[str, Any]]:
        latest_path = os.path.join(self.history_dir, "latest.json")
        if not os.path.exists(latest_path):
            return []
            
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("entries", [])
        except Exception:
            return []

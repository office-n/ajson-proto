
import sys
import os
from typing import List, Optional
from ajson.hands.history_manager import HistoryManager

class Cockpit:
    """AJSON Cockpit MVP: CLI for Agent-driven JSON Orchestration."""
    
    def __init__(self, history_mgr: Optional[HistoryManager] = None):
        self.history_mgr = history_mgr or HistoryManager()
        self.running = True
        self.multi_line_mode = False
        self.buffer: List[str] = []
        self.session_id = self.history_mgr.current_session_id

    def print_welcome(self):
        print(f"--- AJSON Cockpit M1 (Session: {self.session_id}) ---")
        print("Type 'exit' to quit. Use '\"\"\"' for multi-line input toggle.")
        print("Commands: history, attach <path>, exit")

    def run(self):
        self.print_welcome()
        try:
            while self.running:
                prompt = ">>> " if not self.multi_line_mode else "... "
                try:
                    line = input(prompt)
                except EOFError:
                    print("\n[EOF detected. Cleaning up...]")
                    if self.multi_line_mode:
                        print("Discarding incomplete multi-line input.")
                    break

                self.process_line(line)
        finally:
            self.history_mgr.flush()
            print("Cockpit session closed.")

    def process_line(self, line: str):
        stripped = line.strip()

        # Multi-line toggle
        if stripped == '"""':
            if not self.multi_line_mode:
                self.multi_line_mode = True
                print("[Multi-line mode: ON. Type '\"\"\"' to finish.]")
                self.buffer = []
            else:
                self.multi_line_mode = False
                message = "\n".join(self.buffer)
                print(f"[Multi-line message captured: {len(message)} chars]")
                if message:
                    self.execute_instruction(message)
                self.buffer = []
            return

        if self.multi_line_mode:
            self.buffer.append(line)
            return

        # Single-line commands
        if not stripped:
            return

        if stripped == "exit":
            self.running = False
        elif stripped == "history":
            self.show_history()
        elif stripped.startswith("attach "):
            path = stripped[7:].strip()
            self.attach_file(path)
        else:
            self.execute_instruction(stripped)

    def execute_instruction(self, text: str):
        # M1: Just record the instruction to history
        print(f"Recorded: {text[:50]}...")
        self.history_mgr.add_entry("user", text)

    def show_history(self, n: int = 10):
        entries = self.history_mgr.get_entries(n)
        if not entries:
            print("No history in this session.")
            return
        print(f"\n--- History (Last {n}) ---")
        for i, entry in enumerate(entries):
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            summary = (content[:60] + '...') if len(content) > 60 else content
            print(f"[{i}] {role.upper()}: {summary}")
        print("-" * 25)

    def attach_file(self, path: str):
        if not os.path.exists(path):
            print(f"Error: Path '{path}' not found.")
            return
        
        # M1: Record metadata to history
        info = {
            "path": os.path.basename(path),
            "abs_path": "[USER_HOME]/" + os.path.relpath(path, start=os.path.expanduser("~")) if path.startswith(os.path.expanduser("~")) else path,
            "size": os.path.getsize(path)
        }
        print(f"Attached: {info['path']} ({info['size']} bytes)")
        self.history_mgr.add_entry("system", f"Attached file: {info['path']}", metadata=info)

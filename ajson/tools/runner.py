"""
Safe tool runner with allowlist/denylist enforcement
"""
import subprocess
import os
from typing import Tuple, Optional


# Denylist: 禁止コマンド・キーワード
DENYLIST = [
    # 破壊コマンド
    "rm", "rd", "del", "delete",
    "format", "mkfs",
    # 権限変更
    "chmod", "chown", "sudo", "su",
    # プロセス管理
    "kill", "pkill", "killall",
    # ネットワーク
    "curl", "wget", "nc", "netcat",
    # システム操作
    "reboot", "shutdown", "halt",
    "mount", "umount",
]

# Allowlist: 許可コマンド
ALLOWLIST = [
    "python", "python3",
    "pytest",
    "git status", "git log", "git diff", "git show",
    "ls", "cat", "echo", "pwd",
    "grep", "find",
]

# 作業ディレクトリ（環境変数から取得、デフォルトは./workspace）
WORK_DIR = os.getenv("WORK_DIR", "./workspace")


def check_denylist(command: str) -> Tuple[bool, Optional[str]]:
    """
    Check if command contains denied keywords
    
    Returns:
        (is_denied, reason)
    """
    command_lower = command.lower()
    for denied in DENYLIST:
        if denied in command_lower:
            return True, f"Denied keyword detected: '{denied}'"
    return False, None


def check_allowlist(command: str) -> bool:
    """
    Check if command starts with an allowed command
    
    Returns:
        True if allowed, False otherwise
    """
    command_lower = command.lower().strip()
    for allowed in ALLOWLIST:
        if command_lower.startswith(allowed):
            return True
    return False


def run_tool(command: str, work_dir: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Safely execute a command with denylist/allowlist checks
    
    Args:
        command: Command to execute
        work_dir: Working directory (defaults to WORK_DIR)
    
    Returns:
        (success, result, error_reason)
        - success: True if command was executed, False if blocked/failed
        - result: Command output or error message
        - error_reason: Reason for blocking (if blocked)
    """
    # Denylist check (最優先)
    is_denied, deny_reason = check_denylist(command)
    if is_denied:
        return False, f"BLOCKED: {deny_reason}", deny_reason
    
    # Allowlist check
    if not check_allowlist(command):
        reason = "Command not in allowlist"
        return False, f"BLOCKED: {reason}", reason
    
    # 作業ディレクトリの確保
    if work_dir is None:
        work_dir = WORK_DIR
    
    # 作業ディレクトリが存在しない場合は作成
    os.makedirs(work_dir, exist_ok=True)
    
    # コマンド実行
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        
        if result.returncode != 0:
            return False, output, f"Command failed with exit code {result.returncode}"
        
        return True, output, None
        
    except subprocess.TimeoutExpired:
        return False, "Command timed out (30s limit)", "Timeout"
    except Exception as e:
        return False, f"Execution error: {str(e)}", str(e)


def detect_approval_gates(text: str) -> list:
    """
    Detect approval gate keywords in text
    
    Returns:
        List of detected gate types
    """
    gates = []
    text_lower = text.lower()
    
    gate_keywords = {
        "deploy": ["deploy", "deployment", "publish", "release"],
        "delete": ["delete", "remove", "drop table", "truncate"],
        "database": ["create table", "alter table", "database", "db migration"],
        "permission": ["grant", "revoke", "permission", "access control"],
        "billing": ["charge", "payment", "billing", "invoice"],
        "external": ["public", "external", "expose", "外部公開"],
    }
    
    for gate_type, keywords in gate_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                gates.append(gate_type)
                break
    
    return gates

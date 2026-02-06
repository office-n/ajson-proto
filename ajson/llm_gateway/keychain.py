"""
Keychain-based secure API key retrieval (macOS only)

このモジュールは macOS Keychain からAPIキーを安全に取得します。
キーの値は絶対に stdout/stderr に出力されません。
"""
import subprocess
import os
from typing import Optional


def get_keychain_password(
    service_name: str,
    account_name: Optional[str] = None
) -> Optional[str]:
    """
    Retrieve password from macOS Keychain.
    
    Args:
        service_name: Keychain item name (e.g. 'AJSON_OPENAI_API_KEY')
        account_name: Account name (default: current user from $USER)
    
    Returns:
        Password string if found, None otherwise
    
    Security:
        - Password is NEVER printed to stdout/stderr
        - Returns None silently on error (safe fallback)
        - No exception is raised (prevents accidental key leakage in stack traces)
    
    Example:
        >>> key = get_keychain_password('AJSON_OPENAI_API_KEY')
        >>> if key:
        >>>     # Use key (never print it!)
        >>>     pass
    """
    if account_name is None:
        account_name = os.getenv('USER', 'default')
    
    try:
        # -w: return password only (no other output)
        result = subprocess.run(
            [
                'security',
                'find-generic-password',
                '-s', service_name,
                '-a', account_name,
                '-w'  # password only
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False  # Don't raise on non-zero exit
        )
        
        if result.returncode == 0:
            # Success: return password (stripped of whitespace)
            return result.stdout.strip()
        else:
            # Not found or access denied: return None silently
            return None
            
    except Exception:
        # Fail silently (e.g. not macOS, timeout, permission error)
        # No traceback = no accidental key leakage
        return None


def check_keychain_status(service_name: str) -> str:
    """
    Check if a keychain item exists (without retrieving the password).
    
    Args:
        service_name: Keychain item name
    
    Returns:
        - \"設定済み\" if found
        - \"未設定\" if not found
    
    Security:
        - Does NOT return the actual password
        - Only checks existence
    """
    password = get_keychain_password(service_name)
    if password:
        return \"✅ 設定済み\"
    else:
        return \"❌ 未設定\"


def inject_from_keychain_if_needed():
    \"\"\"
    Inject API keys from Keychain into environment variables if not already set.
    
    This function is designed to be called at the start of scripts that need API keys.
    It will:
    1. Check if OPENAI_API_KEY and GEMINI_API_KEY are already in env
    2. If not, try to retrieve from Keychain
    3. If found, inject into os.environ (current process only)
    
    Security:
        - Keys are injected into current process only (not exported to shell)
        - No output to stdout/stderr
        - Safe to call multiple times (idempotent)
    
    Returns:
        None (side effect: may set os.environ)
    \"\"\"
    # OpenAI
    if not os.getenv('OPENAI_API_KEY'):
        key = get_keychain_password('AJSON_OPENAI_API_KEY')
        if key:
            os.environ['OPENAI_API_KEY'] = key
    
    # Gemini
    if not os.getenv('GEMINI_API_KEY'):
        key = get_keychain_password('AJSON_GEMINI_API_KEY')
        if key:
            os.environ['GEMINI_API_KEY'] = key


# Example usage (for testing only, not in production):
if __name__ == \"__main__\":
    print(\"Keychain status check:\")
    print(f\"OPENAI_API_KEY: {check_keychain_status('AJSON_OPENAI_API_KEY')}\")
    print(f\"GEMINI_API_KEY: {check_keychain_status('AJSON_GEMINI_API_KEY')}\")

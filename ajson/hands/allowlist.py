import os
from typing import List, Optional

class NetworkDeniedError(Exception):
    """Raised when a network connection is denied by the Allowlist."""
    pass

class Allowlist:
    """
    Layer 1: Static Allowlist for Network Connections.
    """
    DEFAULT_ALLOWED_HOSTS = [
        "api.openai.com",
        "cdn.openai.com",
        "pypi.org",
        "files.pythonhosted.org"
    ]
    DEFAULT_ALLOWED_PORTS = [443, 80]

    def __init__(self, allowed_hosts: Optional[List[str]] = None, allowed_ports: Optional[List[int]] = None):
        self.allowed_hosts = allowed_hosts or self._load_hosts_from_env() or self.DEFAULT_ALLOWED_HOSTS
        self.allowed_ports = allowed_ports or self.DEFAULT_ALLOWED_PORTS

    def _load_hosts_from_env(self) -> List[str]:
        env_val = os.getenv("AJSON_ALLOWED_HOSTS")
        if env_val:
            return [h.strip() for h in env_val.split(",") if h.strip()]
        return []

    def check(self, host: str, port: int) -> None:
        """
        Check if the host and port are allowed.
        Raises NetworkDeniedError if not allowed.
        """
        if port not in self.allowed_ports:
             raise NetworkDeniedError(f"Port {port} is not in the allowlist.")

        # Simple exact match for now. Could support wildcards later if needed.
        if host not in self.allowed_hosts:
             raise NetworkDeniedError(f"Host {host} is not in the allowlist.")
        
        return

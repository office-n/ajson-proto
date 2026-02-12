import datetime
from typing import Any, Dict, Optional

from ajson.hands.allowlist import Allowlist, NetworkDeniedError
from ajson.hands.approval_sqlite import SQLiteApprovalStore
from ajson.hands.audit_logger import AuditLogger

# STRICT SECURITY POLICY: Default to DENY for all network connections
allow_network = False

class NetworkAdapter(ABC):
    """Abstract base class for network connections."""
    
    @abstractmethod
    def connect(self, host: str, port: int, reason: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attempt to establish a connection.
        Returns True if successful (or mocked success), False otherwise.
        Raises specific security errors if denied.
        """
        pass

class ApprovalRequiredError(Exception):
    """Raised when an approval grant is required but missing or expired."""
    pass

class SecureNetworkConnector(NetworkAdapter):
    """
    Concrete implementation of NetworkAdapter with 3-layer defense:
    1. Allowlist
    2. Approval
    3. Audit Logging
    """
    def __init__(self, 
                 allowlist: Optional[Allowlist] = None, 
                 approval_store: Optional[SQLiteApprovalStore] = None,
                 audit_logger: Optional[AuditLogger] = None):
        self.allowlist = allowlist or Allowlist()
        self.approval_store = approval_store or SQLiteApprovalStore()
        self.audit_logger = audit_logger or AuditLogger()

    def connect(self, host: str, port: int, reason: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        meta = metadata or {}
        event_data = {
            "host": host,
            "port": port,
            "reason": reason,
            **meta
        }

        # 1. Audit: Attempt
        self.audit_logger.log_event("network.connect.attempt", event_data)

        try:
            # 2. Layer 1: Allowlist
            self.allowlist.check(host, port)

            # 3. Layer 2: Approval
            # We need to find a valid grant for this operation type="network_connect" 
            # and scope matching host/port (simplification: check if ANY active grant exists for now, 
            # or strictly we should query grants for specific scope. 
            # For Phase 9.8.1, we assume specific 'network_connect' category).
            
            # Using SQLiteApprovalStore's verify_grant if we knew the grant_id, 
            # but usually we want to "find" a valid grant. 
            # SQLiteApprovalStore has get_active_grants(). 
            # Let's filter in memory for now or assume strict check is needed.
            
            active_grants = self.approval_store.get_active_grants()
            # Simplistic check: is there a grant that covers this host?
            # In a real system, scope parsing is complex. 
            # Here we assume scope == host for simplicity or "all"
            
            has_valid_grant = False
            for grant in active_grants:
                # Mock logic for scope matching
                if grant.scope == "*" or grant.scope == host or host in grant.scope:
                     has_valid_grant = True
                     break
            
            if not has_valid_grant:
                 raise ApprovalRequiredError(f"No active approval grant found for host {host}")

            # If passed check
            self.audit_logger.log_event("network.connect.allowed", event_data)
            
            # 4. Actual Connection (Mocked for now as we don't do real IO yet)
            # In real impl, we would use socket or requests here.
            return True

        except (NetworkDeniedError, ApprovalRequiredError) as e:
            # Audit: Denied
            self.audit_logger.log_event("network.connect.denied", {**event_data, "error": str(e)})
            raise e
        except Exception as e:
            # Audit: Failed
            self.audit_logger.log_event("network.connect.failed", {**event_data, "error": str(e)})
            raise e

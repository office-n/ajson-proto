"""
Optional bearer token authentication for approval endpoints

Opt-in via AJSON_APPROVAL_TOKEN environment variable.
If not set, endpoints work without authentication (backward compatible).
"""
import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional


security = HTTPBearer(auto_error=False)


def get_approval_token() -> Optional[str]:
    """Get configured approval token from environment"""
    return os.environ.get("AJSON_APPROVAL_TOKEN")


def verify_approval_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> bool:
    """
    Verify approval endpoint authentication
    
    Returns:
        True if auth is valid or not required
        
    Raises:
        HTTPException: If auth is required but missing/invalid
    """
    configured_token = get_approval_token()
    
    # If no token configured, authentication not required (backward compatible)
    if not configured_token:
        return True
    
    # Token configured, authentication required
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required (AJSON_APPROVAL_TOKEN is set)",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    if credentials.credentials != configured_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid authentication token"
        )
    
    return True


def auth_required() -> bool:
    """Check if authentication is currently required"""
    return get_approval_token() is not None

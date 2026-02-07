"""
API endpoint for limited execution with approval grants
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ajson.hands.runner import ToolRunner
from ajson.hands.policy import PolicyDeniedError

router = APIRouter(prefix="/api/hands", tags=["hands"])


class ExecuteLimitedRequest(BaseModel):
    """Request to execute with approval grant"""
    grant_id: str
    tool_name: str
    args: Dict[str, Any]


@router.post("/execute_limited")
async def execute_limited(req: ExecuteLimitedRequest):
    """
    Execute tool with approval grant (LIMITED mode)
    
    Security:
    - Requires valid, non-expired approval grant
    - ALLOWLIST operations only
    - NETWORK always DENY
    - shell=False, timeout, cwd restrictions
    """
    runner = ToolRunner(dry_run=False)
    
    try:
        result = runner.execute_tool_limited(
            grant_id=req.grant_id,
            tool_name=req.tool_name,
            args=req.args
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PolicyDeniedError as e:
        raise HTTPException(status_code=403, detail=f"Operation denied: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

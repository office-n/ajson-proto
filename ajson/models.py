"""
Pydantic models for AJSON MVP
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MissionStatus:
    """Mission status constants"""
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    PRE_AUDIT = "PRE_AUDIT"
    EXECUTE = "EXECUTE"
    POST_AUDIT = "POST_AUDIT"
    FINALIZE = "FINALIZE"
    DONE = "DONE"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ERROR = "ERROR"


class StepStatus:
    """Step status constants"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApprovalStatus:
    """Approval status constants"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Mission models
class MissionCreate(BaseModel):
    """Create mission request"""
    title: str
    description: str
    attachments: Optional[List[str]] = Field(default_factory=list)


class Mission(BaseModel):
    """Mission model"""
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Step models
class StepCreate(BaseModel):
    """Create step request"""
    mission_id: int
    role: str
    input_data: str
    output_data: Optional[str] = None
    status: str = StepStatus.PENDING


class Step(BaseModel):
    """Step model"""
    id: int
    mission_id: int
    role: str
    input_data: str
    output_data: Optional[str]
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ToolRun models
class ToolRunCreate(BaseModel):
    """Create tool run request"""
    step_id: int
    command: str
    result: Optional[str] = None
    blocked: bool = False
    block_reason: Optional[str] = None


class ToolRun(BaseModel):
    """Tool run model"""
    id: int
    step_id: int
    command: str
    result: Optional[str]
    blocked: bool
    block_reason: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Approval models
class ApprovalCreate(BaseModel):
    """Create approval request"""
    mission_id: int
    gate_type: str
    reason: str
    status: str = ApprovalStatus.PENDING


class Approval(BaseModel):
    """Approval model"""
    id: int
    mission_id: int
    gate_type: str
    reason: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Artifact models
class ArtifactCreate(BaseModel):
    """Create artifact request"""
    mission_id: int
    artifact_type: str
    path: str
    content: str


class Artifact(BaseModel):
    """Artifact model"""
    id: int
    mission_id: int
    artifact_type: str
    path: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Memory models
class MemoryCreate(BaseModel):
    """Create memory request"""
    mission_id: int
    key: str
    value: str


class Memory(BaseModel):
    """Memory model"""
    id: int
    mission_id: int
    key: str
    value: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

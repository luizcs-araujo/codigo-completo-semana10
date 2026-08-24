from __future__ import annotations
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    read_only = 'read_only'
    write_safe = 'write_safe'
    write_sensitive = 'write_sensitive'
    destructive = 'destructive'

class ActionResult(BaseModel):
    status: Literal['dry_run', 'executed', 'duplicate', 'blocked', 'failed']
    message: str
    changed: bool = False
    request_id: str | None = None
    audit_id: int | None = None
    data: dict[str, Any] = Field(default_factory=dict)

class ToolSpec(BaseModel):
    name: str
    description: str
    risk: RiskLevel
    requires_approval: bool
    idempotency_required: bool
    writes_state: bool
    tags: list[str] = Field(default_factory=list)

class EventEnvelope(BaseModel):
    event_id: str
    event_type: str
    source: str
    payload: dict[str, Any]

class AgentRunSummary(BaseModel):
    status: Literal['completed', 'needs_human', 'blocked', 'failed', 'dry_run_only']
    use_case_id: str
    summary: str
    evidence: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    actions_executed: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    requires_human: bool = False

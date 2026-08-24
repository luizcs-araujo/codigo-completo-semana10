from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    claim: str = Field(description="Fato sustentado pela fonte")
    source: str = Field(description="Citação source_path#heading")
    version: str = Field(description="Versão da fonte")
    excerpt: str = Field(description="Trecho curto que sustenta o fato", max_length=400)


class TicketDiagnosis(BaseModel):
    ticket_id: str
    status: Literal["completed", "needs_human", "insufficient_evidence", "blocked"]
    probable_cause: str
    confidence: Literal["low", "medium", "high"]
    evidence: list[EvidenceReference] = Field(min_length=1, max_length=5)
    retrieval_queries: list[str] = Field(default_factory=list, max_length=3)
    next_steps: list[str] = Field(min_length=1, max_length=4)
    requires_human: bool
    stop_reason: Literal["sufficient_evidence", "needs_write_action", "insufficient_evidence", "tool_failure", "step_limit", "kill_switch"]

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TicketDiagnosis(BaseModel):
    """Diagnóstico final validado do agente."""

    ticket_id: str = Field(description="Identificador do ticket analisado")
    status: Literal["completed", "needs_human", "blocked"]
    probable_cause: str = Field(description="Causa mais provável, sem inventar fatos")
    confidence: Literal["low", "medium", "high"]
    evidence: list[str] = Field(
        min_length=1,
        max_length=5,
        description="Evidências concretas obtidas pelas tools",
    )
    next_steps: list[str] = Field(
        min_length=1,
        max_length=4,
        description="Próximos passos seguros e executáveis",
    )
    requires_human: bool
    stop_reason: Literal[
        "sufficient_evidence",
        "needs_write_action",
        "insufficient_evidence",
        "tool_failure",
        "step_limit",
    ]

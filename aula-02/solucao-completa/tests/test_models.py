from supportops.models import TicketDiagnosis


def test_diagnosis_schema():
    diagnosis = TicketDiagnosis(
        ticket_id="TCK-4821",
        status="needs_human",
        probable_cause="Cache de permissões desatualizado",
        confidence="high",
        evidence=["Fonte de verdade e cache divergem"],
        next_steps=["Solicitar invalidação manual do cache"],
        requires_human=True,
        stop_reason="needs_write_action",
    )
    assert diagnosis.requires_human is True

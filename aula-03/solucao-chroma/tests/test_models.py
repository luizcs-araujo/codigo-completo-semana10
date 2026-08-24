from supportops.models import TicketDiagnosis


def test_diagnosis_contract():
    diagnosis = TicketDiagnosis.model_validate({
        "ticket_id":"TCK-4821",
        "status":"needs_human",
        "probable_cause":"cache divergente",
        "confidence":"high",
        "evidence":[{"claim":"runbook exige aprovação","source":"doc.md#Mitigação","version":"2.1","relevance":0.9,"excerpt":"invalidação exige aprovação"}],
        "retrieval_queries":["403 role cache"],
        "next_steps":["solicitar aprovação"],
        "requires_human":True,
        "stop_reason":"needs_write_action",
    })
    assert diagnosis.requires_human

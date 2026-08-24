from supportops.models import TicketDiagnosis


def test_diagnosis_schema():
    item = TicketDiagnosis.model_validate({
        "ticket_id":"TCK-4821","status":"needs_human","probable_cause":"cache divergente","confidence":"high",
        "evidence":[{"claim":"roles divergem","source":"doc.md#Diagnóstico","version":"2.1","excerpt":"fonte e cache divergem"}],
        "retrieval_queries":["403 role cache"],"next_steps":["solicitar invalidação direcionada"],
        "requires_human":True,"stop_reason":"needs_write_action"
    })
    assert item.requires_human

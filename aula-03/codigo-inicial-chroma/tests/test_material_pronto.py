from supportops import repository
from supportops.rag.ingestion import load_catalog


def test_backend_expandido():
    assert repository.get_ticket("TCK-4826")["service_id"] == "reports-worker"
    assert repository.get_metric_snapshot("reports-worker", "prod")["queue_depth"] == 1840


def test_catalogo_profundo_disponivel():
    catalog = load_catalog()
    assert len(catalog) >= 25
    assert any(not row["is_current"] for row in catalog.values())
    assert any(row["trust_level"] == "unverified" for row in catalog.values())

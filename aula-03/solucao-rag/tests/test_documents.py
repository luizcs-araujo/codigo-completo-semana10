from supportops.config import settings
from supportops.rag.documents import load_documents


def test_all_documents_have_governance_metadata():
    docs = load_documents(settings.docs_dir)
    assert len(docs) >= 7
    for doc in docs:
        for key in ("doc_id","service_id","environment","version","updated_at","is_current","source_type","source_path"):
            assert key in doc.metadata

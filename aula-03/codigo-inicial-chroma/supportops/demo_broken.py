from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from supportops.config import settings


def main() -> None:
    catalog = json.loads(settings.catalog_path.read_text(encoding="utf-8"))
    loader = DirectoryLoader(
        str(settings.docs_dir), glob="**/*.md", loader_cls=TextLoader,
        loader_kwargs={"encoding":"utf-8"}, show_progress=False,
    )
    documents = []
    for raw in loader.load():
        source = Path(raw.metadata["source"]).resolve()
        relative = source.relative_to(settings.docs_dir.resolve()).as_posix()
        documents.append(Document(raw.page_content, metadata={**catalog[relative], "source_path":relative}))

    with TemporaryDirectory() as directory:
        store = Chroma(
            collection_name="naive_chroma_demo",
            embedding_function=DeterministicFakeEmbedding(size=64),
            persist_directory=directory,
        )
        store.add_documents(documents, ids=[doc.metadata["doc_id"] for doc in documents])
        rows = store.get(
            where={"service_id":"analytics-api"},
            where_document={"$contains":"403"},
            include=["documents","metadatas"],
        )
        matches = [
            {"document":doc,"metadata":metadata}
            for doc, metadata in zip(rows["documents"], rows["metadatas"])
        ]
        # Erro intencional: aceita o primeiro/mais antigo sem filtrar vigência ou confiança.
        matches.sort(key=lambda row: row["metadata"]["updated_at"])
        selected = matches[0]["metadata"]
        print(f"Fonte escolhida: {selected['source_path']} v{selected['version']} current={selected['is_current']}")
        print("Falha: Chroma foi usado sem filtros de vigência, ambiente e confiança.")
        for step in range(1,4):
            print(f"step {step}: mesma consulta → mesmo documento → nenhuma evidência nova")


if __name__ == "__main__":
    main()

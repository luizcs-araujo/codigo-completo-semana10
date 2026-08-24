from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from supportops.config import settings

HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def load_catalog() -> dict[str, dict]:
    return json.loads(settings.catalog_path.read_text(encoding="utf-8"))


def load_source_documents() -> list[Document]:
    loader = DirectoryLoader(
        str(settings.docs_dir),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
        use_multithreading=False,
    )
    catalog = load_catalog()
    documents = []
    for document in loader.load():
        source = Path(document.metadata["source"]).resolve()
        relative = source.relative_to(settings.docs_dir.resolve()).as_posix()
        if relative not in catalog:
            raise ValueError(f"Documento sem entrada no catálogo: {relative}")
        metadata = {**catalog[relative], "source_path": relative}
        documents.append(Document(page_content=document.page_content, metadata=metadata))
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=False)
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    output = []
    for document in documents:
        sections = header_splitter.split_text(document.page_content)
        enriched = []
        for section in sections:
            heading = section.metadata.get("h3") or section.metadata.get("h2") or section.metadata.get("h1") or "Documento"
            enriched.append(Document(
                page_content=section.page_content,
                metadata={**document.metadata, **section.metadata, "heading": heading},
            ))
        for index, chunk in enumerate(size_splitter.split_documents(enriched)):
            digest = hashlib.sha256(
                f"{document.metadata['source_path']}:{index}:{chunk.page_content}".encode()
            ).hexdigest()[:20]
            chunk.metadata["chunk_index"] = index
            chunk.metadata["chunk_id"] = digest
            output.append(chunk)
    return output

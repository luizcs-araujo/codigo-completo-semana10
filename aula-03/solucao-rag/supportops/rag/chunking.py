from __future__ import annotations

import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def naive_whole_document_chunks(documents: list[Document]) -> list[Document]:
    """Versão propositalmente ruim: um documento inteiro por chunk."""
    return [
        Document(
            page_content=d.page_content,
            metadata={**d.metadata, "heading": "documento inteiro", "chunk_index": 0},
            id=f"{d.id}:0",
        )
        for d in documents
    ]


def _sections(text: str) -> list[tuple[str, str]]:
    current_heading = "Introdução"
    current: list[str] = []
    sections: list[tuple[str, str]] = []
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s+", line):
            if current:
                sections.append((current_heading, "\n".join(current).strip()))
            current_heading = re.sub(r"^#{1,3}\s+", "", line).strip()
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append((current_heading, "\n".join(current).strip()))
    return [(heading, content) for heading, content in sections if content]


def heading_aware_chunks(
    documents: list[Document],
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    output: list[Document] = []
    for doc in documents:
        chunk_index = 0
        for heading, section in _sections(doc.page_content):
            for part in splitter.split_text(section):
                metadata = {
                    **doc.metadata,
                    "heading": heading,
                    "chunk_index": chunk_index,
                }
                chunk_id = f"{doc.metadata['doc_id']}:{chunk_index}"
                output.append(
                    Document(page_content=part, metadata=metadata, id=chunk_id)
                )
                chunk_index += 1
    return output

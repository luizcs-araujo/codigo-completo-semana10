from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document


def _parse_scalar(value: str) -> Any:
    clean = value.strip().strip('"').strip("'")
    if clean.lower() in {"true", "false"}:
        return clean.lower() == "true"
    return clean


def load_markdown_document(path: Path, root: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    metadata: dict[str, Any] = {
        "source_path": str(path.relative_to(root)).replace("\\", "/")
    }
    body = raw
    marker = "---\n"
    if raw.startswith(marker):
        _, frontmatter, body = raw.split(marker, 2)
        for line in frontmatter.splitlines():
            if not line.strip() or ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = _parse_scalar(value)
    required = {
        "doc_id", "title", "service_id", "environment", "version",
        "updated_at", "is_current", "source_type", "access_scope",
    }
    missing = required - metadata.keys()
    if missing:
        raise ValueError(f"Metadata ausente em {path}: {sorted(missing)}")
    return Document(
        page_content=body.strip(),
        metadata=metadata,
        id=str(metadata["doc_id"]),
    )


def load_documents(root: Path) -> list[Document]:
    return [
        load_markdown_document(path, root)
        for path in sorted(root.rglob("*.md"))
    ]

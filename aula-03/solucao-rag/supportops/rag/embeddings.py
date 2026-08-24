from __future__ import annotations

import hashlib
import math
import re
from langchain_core.embeddings import Embeddings


class HashEmbeddings(Embeddings):
    """Fallback determinístico para testes; não substitui embeddings semânticos em produção."""

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-zA-Z0-9_:-]+", text.lower()):
            index = int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

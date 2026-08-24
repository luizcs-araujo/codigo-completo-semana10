from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
    max_graph_steps: int = int(os.getenv("AGENT_MAX_GRAPH_STEPS", "14"))
    runs_dir: Path = Path(os.getenv("RUNS_DIR", "runs"))


settings = Settings()

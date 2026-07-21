from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    db_path: Path
    ollama_model: str
    langsmith_project: str
    langsmith_tracing: bool


def get_settings() -> Settings:
    db_path = Path(os.getenv('OPSPILOT_DB_PATH', '.opspilot/opspilot.sqlite3'))
    return Settings(
        db_path=db_path,
        ollama_model=os.getenv('OLLAMA_MODEL', 'qwen3:4b'),
        langsmith_project=os.getenv('LANGSMITH_PROJECT', 'opspilot-semana2-aula2'),
        langsmith_tracing=os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true',
    )

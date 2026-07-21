from __future__ import annotations
import importlib, os, sys
from .config import get_settings
from .database import init_db

REQUIRED = ['fastapi', 'pydantic', 'langchain_core', 'langsmith']

def main() -> None:
    print('OpsPilot doctor')
    print(f'Python: {sys.version.split()[0]}')
    settings = get_settings()
    print(f'DB path: {settings.db_path}')
    init_db(settings.db_path)
    print('SQLite: ok')
    for name in REQUIRED:
        importlib.import_module(name)
        print(f'{name}: ok')
    if settings.langsmith_tracing:
        if os.getenv('LANGSMITH_API_KEY'):
            print(f'LangSmith: tracing ligado · projeto={settings.langsmith_project}')
        else:
            print('LangSmith: LANGSMITH_TRACING=true, mas LANGSMITH_API_KEY vazio')
    else:
        print('LangSmith: tracing desligado (ok para testes locais)')
    print('ok')

if __name__ == '__main__':
    main()

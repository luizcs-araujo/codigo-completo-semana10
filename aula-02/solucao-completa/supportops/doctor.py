from __future__ import annotations

import json
import sys
from urllib.error import URLError
from urllib.request import urlopen

from supportops.config import settings


def main() -> int:
    url = settings.base_url.rstrip("/") + "/api/tags"
    try:
        with urlopen(url, timeout=3) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError) as exc:
        print(f"[ERRO] Ollama não respondeu em {settings.base_url}: {exc}")
        print("Inicie o Ollama e tente novamente.")
        return 1

    names = {item.get("name") for item in payload.get("models", [])}
    available = settings.model in names or settings.model.split(":")[0] in names
    print(f"[OK] Ollama respondeu em {settings.base_url}")
    print(f"[INFO] Modelo configurado: {settings.model}")

    if not available:
        print(f"[ERRO] Modelo não encontrado. Execute: ollama pull {settings.model}")
        print("Modelos instalados:", ", ".join(sorted(n for n in names if n)) or "nenhum")
        return 2

    print("[OK] Modelo disponível.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

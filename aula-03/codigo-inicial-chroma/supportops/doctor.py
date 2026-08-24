from __future__ import annotations

import json
from urllib.request import urlopen
from urllib.error import URLError
from supportops.config import settings


def main() -> None:
    try:
        with urlopen(f"{settings.base_url}/api/tags", timeout=3) as response:
            payload = json.loads(response.read().decode())
    except URLError as exc:
        raise SystemExit(f"Ollama indisponível em {settings.base_url}: {exc}")
    names = {item["name"] for item in payload.get("models", [])}
    required = [settings.model, settings.embedding_model]
    roots = {name.split(":")[0] for name in names}
    missing = [model for model in required if model not in names and model.split(":")[0] not in roots]
    if missing:
        command = " && ".join(f"ollama pull {model}" for model in missing)
        raise SystemExit(f"Modelos ausentes: {', '.join(missing)}. Rode: {command}")
    print("OK — Ollama e modelos necessários estão disponíveis")


if __name__ == "__main__":
    main()

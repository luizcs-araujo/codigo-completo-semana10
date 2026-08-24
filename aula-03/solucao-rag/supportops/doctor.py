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
    required = [settings.model]
    if settings.embedding_backend == "ollama":
        required.append(settings.embedding_model)
    missing = [model for model in required if model not in names and model.split(":")[0] not in {n.split(":")[0] for n in names}]
    if missing:
        raise SystemExit("Modelos ausentes: " + ", ".join(missing) + ". Rode: " + " && ".join(f"ollama pull {m}" for m in missing))
    print("OK — Ollama e modelos necessários estão disponíveis")

if __name__ == "__main__":
    main()

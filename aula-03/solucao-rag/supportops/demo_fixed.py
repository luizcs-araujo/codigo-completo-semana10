from __future__ import annotations

import argparse
from rich.console import Console
from supportops.rag.embeddings import HashEmbeddings
from supportops.rag.service import RagService, SearchFilters

console = Console()

def main() -> None:
    parser = argparse.ArgumentParser(description="Demonstração determinística do RAG corrigido")
    parser.add_argument("--query", default="erro 403 após mudança de role e cache")
    args = parser.parse_args()
    service = RagService(embeddings=HashEmbeddings())
    result = service.search(args.query, SearchFilters(service_id="analytics-api", environment="prod"), top_k=4)
    console.print(f"sufficient={result['sufficient']} — {result['sufficiency_reason']}")
    for index, item in enumerate(result["evidence"], 1):
        console.print(f"{index}. {item['citation']} v{item['version']} current={item['is_current']}")
    assert all(item["is_current"] for item in result["evidence"])
    assert all(item["environment"] in {"prod", "all"} for item in result["evidence"])
    console.print("[bold green]Correção validada:[/bold green] documento obsoleto e staging foram excluídos.")

if __name__ == "__main__": main()

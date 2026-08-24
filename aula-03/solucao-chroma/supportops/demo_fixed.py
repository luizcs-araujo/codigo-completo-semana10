from pathlib import Path
from tempfile import TemporaryDirectory
from langchain_core.embeddings import DeterministicFakeEmbedding
from rich.console import Console
from supportops.rag.index import rebuild_index
from supportops.rag.service import ChromaRagService, SearchRequest

console = Console()

if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        path = Path(directory)
        embedding = DeterministicFakeEmbedding(size=128)
        rebuild_index(embedding, path, "fixed_demo")
        service = ChromaRagService(embedding, path, "fixed_demo")
        result = service.search(SearchRequest(
            query="erro 403 após mudança de role e cache de permissões",
            service_id="analytics-api",
            environment="prod",
            top_k=8,
        ))
        console.print(f"sufficient={result['sufficient']} — {result['sufficiency_reason']}")
        for item in result["evidence"]:
            console.print(f"{item['citation']} v{item['version']} current={item['current']} trust={item['trust_level']}")
        assert all(item["current"] for item in result["evidence"])
        assert all(item["environment"] in {"prod", "all"} for item in result["evidence"])
        assert not any("obsoleto" in item["source"].lower() for item in result["evidence"])
        console.print("[bold green]Correção validada:[/bold green] fontes obsoletas, staging e chat não validado foram excluídos.")

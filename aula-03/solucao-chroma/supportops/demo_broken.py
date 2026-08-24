from pathlib import Path
from tempfile import TemporaryDirectory
from langchain_core.embeddings import DeterministicFakeEmbedding
from rich.console import Console
from supportops.rag.broken import broken_first_match
from supportops.rag.index import rebuild_index

console = Console()

if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        path = Path(directory)
        embedding = DeterministicFakeEmbedding(size=128)
        rebuild_index(embedding, path, "broken_demo")
        result = broken_first_match(embedding, path, "broken_demo")
        md = result["metadata"]
        console.print(f"[bold red]Fonte escolhida:[/bold red] {md['source_path']} v{md['version']} current={md['is_current']}")
        console.print("Motivo da falha: busca sem filtro de vigência, ambiente e confiança; a baseline ainda prioriza a fonte mais antiga.")
        console.print("\nLoop sem progresso:")
        for step in range(1, 4):
            console.print(f"step {step}: mesma consulta → {md['source_path']}")

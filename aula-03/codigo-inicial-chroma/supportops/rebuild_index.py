from rich.console import Console
from supportops.rag.index import rebuild_index

console = Console()

if __name__ == "__main__":
    manifest = rebuild_index()
    console.print("[bold green]Índice reconstruído[/bold green]")
    console.print_json(data=manifest)

# Aula 3 — Agentic RAG com LangChain, Chroma e Ollama

Evolução direta da solução da Aula 2. O agente continua em LangChain e o RAG passa a usar componentes estabelecidos:

- `DirectoryLoader` + `TextLoader`;
- `MarkdownHeaderTextSplitter`;
- `RecursiveCharacterTextSplitter`;
- `OllamaEmbeddings`;
- Chroma persistente;
- similarity search com relevance scores;
- metadata filters do Chroma;
- retriever exposto como tool.

## Preparação

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m supportops.doctor
python -m supportops.rebuild_index
```

## Demonstrar o problema e a correção

```bash
python -m supportops.demo_broken
python -m supportops.demo_fixed
```

## Executar o agente

```bash
python -m supportops.main TCK-4821
python -m supportops.main TCK-4823
```

## Testes

```bash
pytest -q
```

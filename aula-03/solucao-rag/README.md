# SupportOps Agent — Aula 3

Evolução direta da solução da Aula 2. O agente continua usando `qwen3:4b` no Ollama e ganha:

- base documental em Markdown;
- chunking por seção;
- embeddings locais com `qwen3-embedding:0.6b`;
- busca híbrida e filtros de metadata;
- RAG como tool do agente;
- citações e critério de suficiência;
- limites de model/tool calls, retry, circuit breaker, recursion limit e kill switch;
- demonstrações reproduzíveis de falha e correção.

## Preparação

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m supportops.doctor
pytest -q
```

## Demonstração sem depender do LLM

```bash
python -m supportops.demo_broken
python -m supportops.demo_fixed
```

## Agente completo

```bash
python -m supportops.main TCK-4821
python -m supportops.main TCK-4823
```

Para testar o RAG sem baixar embeddings, use `RAG_EMBEDDING_BACKEND=hash`. O agente Qwen continua exigindo Ollama.

# Código inicial — Aula 3 com Chroma

Este starter é executável como a solução da Aula 2: o agente usa as tools operacionais, mas ainda não possui RAG técnico. O backend mockado e os 32 documentos já estão disponíveis.

## Antes do exercício

```bash
python -m supportops.main TCK-4821
python -m supportops.demo_broken
pytest -q
```

A primeira execução mostra o agente operacional com uma linha do tempo legível:
raciocínio disponibilizado pelo modelo, chamadas e retornos de tools, diagnóstico
estruturado e uso agregado de tokens. A segunda usa Chroma de forma
propositalmente ruim e seleciona uma fonte obsoleta.

As chamadas ao modelo e às tools possuem limites independentes. O limite do
grafo permanece como proteção final contra loops. A tool
`invalidate_permission_cache` é uma operação protegida: quando o modelo a
solicita, a execução pausa e só continua após aprovação explícita no terminal.

Use `--json` quando precisar somente do payload estruturado, sem o render da
linha do tempo:

```bash
python -m supportops.main TCK-4821 --json
```

Os pontos de live coding estão marcados em:

- `supportops/rag/ingestion.py`;
- `supportops/rag/index.py`;
- `supportops/rag/service.py`;
- `supportops/rag_tools.py`;
- `supportops/tools.py`;
- `supportops/agent.py`.
# example_support_agent

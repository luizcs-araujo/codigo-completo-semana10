# Validação

Executado em ambiente local do container:

```bash
cd /mnt/data/opspilot_sandbox_base
PYTHONPATH=src python -m compileall -q src
pytest -q
PYTHONPATH=src python -m opspilot.doctor
PYTHONPATH=src python -m opspilot.cli list-tools
```

Resultado:

```text
10 passed
compileall: ok
doctor: ok
list-tools: ok
```

Observação: o projeto base não executa inferência com LLM. Os trios deverão plugar seus agentes com Ollama/LangChain quando implementarem os use cases.

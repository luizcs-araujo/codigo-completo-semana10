# Observabilidade esperada

O sistema base não força uma ferramenta única de observabilidade para os trabalhos dos trios, mas já está preparado para LangSmith.

## Ambiente

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="..."
export LANGSMITH_PROJECT="opspilot-semana2-aula2"
```

## O que os trios devem rastrear

- evento de entrada;
- seleção de tools;
- dry-run de ação perigosa;
- aprovação ou bloqueio;
- resultado da ação;
- saída estruturada;
- casos sem evidência suficiente;
- erros e retries.

## Metadata recomendada

```python
config = {
  "run_name": "uc04-feature-flag-regression",
  "tags": ["semana2-aula2", "team-03", "feature-flag"],
  "metadata": {
    "use_case_id": "UC04",
    "risk": "write_sensitive",
    "dry_run_first": True
  }
}
```

## Perguntas para apresentação

- Onde o trace mostra a decisão principal?
- Qual tool perigosa apareceu?
- A primeira chamada foi dry-run?
- O que ficou no audit log?
- Como o grupo provaria que o agente não agiu sem aprovação?
